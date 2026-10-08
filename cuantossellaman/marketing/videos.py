"""Genera vídeos verticales (1080x1920, MP4) para TikTok, Reels y Shorts con los colores de la web.

Cada vídeo es una lista de escenas; cada escena, una lista de elementos que aparecen uno detrás de otro
(con un pequeño deslizamiento hacia arriba). Sin voz ni música: el sonido se elige en TikTok.
El texto se mantiene en la zona central, lejos de los botones de TikTok (derecha y abajo).

Uso: python cuantossellaman/marketing/videos.py CARPETA_DE_SALIDA [nombre_del_video ...]
Necesita Pillow, numpy, ffmpeg y la fuente Inter (/usr/share/fonts/opentype/inter/).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FUENTES = "/usr/share/fonts/opentype/inter/"
AZUL, AZUL_OSCURO, BLANCO, CLARO, NARANJA = (63, 81, 196), (38, 50, 140), (255, 255, 255), (214, 220, 250), (232, 163, 61)
MARGEN = 90            # margen izquierdo
ANCHO = W - 2 * MARGEN - 60   # un poco menos por la derecha (botones de TikTok)
ENTRADA = 0.45         # segundos que tarda en aparecer cada elemento
DESLIZ = 60            # píxeles que sube al aparecer


def fuente(peso, tam):
    return ImageFont.truetype(f"{FUENTES}Inter-{peso}.otf", tam)


def partir(texto, f, ancho):
    """Parte el texto en líneas que caben en el ancho."""
    lineas = []
    for parrafo in texto.split("\n"):
        actual = ""
        for palabra in parrafo.split():
            prueba = (actual + " " + palabra).strip()
            if f.getlength(prueba) <= ancho:
                actual = prueba
            else:
                if actual:
                    lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return lineas


def bloque(texto, peso, tam, color, interlinea=1.18, fondo=None):
    """Imagen RGBA con el texto (y una píldora de fondo si se pide)."""
    f = fuente(peso, tam)
    lineas = partir(texto, f, ANCHO - (60 if fondo else 0))
    alto_linea = int(tam * interlinea)
    ancho = int(max(f.getlength(l) for l in lineas)) + (60 if fondo else 0)
    alto = alto_linea * len(lineas) + (36 if fondo else 0) + int(tam * 0.25)
    img = Image.new("RGBA", (ancho + 4, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if fondo:
        d.rounded_rectangle((0, 0, ancho, alto - int(tam * 0.25)), radius=alto // 2, fill=fondo)
    for i, l in enumerate(lineas):
        d.text((30 if fondo else 0, (18 if fondo else 0) + i * alto_linea), l, font=f, fill=color)
    return img


def fila(izq, der, tam=58):
    """Fila de lista: texto a la izquierda y cifra a la derecha, sobre una tarjeta translúcida."""
    fi, fd = fuente("Bold", tam), fuente("ExtraBold", tam)
    alto = int(tam * 1.9)
    img = Image.new("RGBA", (ANCHO, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, ANCHO, alto), radius=24, fill=(255, 255, 255, 34))
    d.text((32, alto // 2), izq, font=fi, fill=BLANCO, anchor="lm")
    if der:
        d.text((ANCHO - 32, alto // 2), der, font=fd, fill=NARANJA, anchor="rm")
    return img


def elemento(tipo, *args):
    if tipo == "gancho":
        return bloque(args[0], "ExtraBold", 104, BLANCO, 1.12)
    if tipo == "titulo":
        return bloque(args[0], "ExtraBold", 82, BLANCO, 1.15)
    if tipo == "texto":
        return bloque(args[0], "SemiBold", 56, CLARO, 1.3)
    if tipo == "cifra":
        return bloque(args[0], "ExtraBold", 190, NARANJA, 1.0)
    if tipo == "fila":
        return fila(*args)
    if tipo == "web":
        return bloque("cuantossellaman.es", "ExtraBold", 64, AZUL_OSCURO, 1.0, fondo=NARANJA)
    raise ValueError(tipo)


def fondo():
    """Degradado vertical azul con la marca arriba."""
    y = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(AZUL) * (1 - y) + np.array(AZUL_OSCURO) * y).astype(np.uint8)
    img = Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy())
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((MARGEN, 150, MARGEN + 76, 226), radius=18, fill=BLANCO)
    d.text((MARGEN + 38, 189), "?", font=fuente("ExtraBold", 54), fill=AZUL, anchor="mm")
    d.text((MARGEN + 100, 188), "¿Cuántos se llaman?", font=fuente("Bold", 44), fill=BLANCO, anchor="lm")
    return img


def suave(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def render(nombre, escenas, salida):
    """escenas: [(duración, separación entre elementos, [elementos])]"""
    base = fondo()
    ruta = Path(salida) / f"{nombre}.mp4"
    total = sum(d for d, _, _ in escenas)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
           "-movflags", "+faststart", str(ruta)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for duracion, sep, elems in escenas:
        imgs = [elemento(*e) for e in elems]
        # colocar los elementos centrados en vertical en la zona útil (entre la marca y los botones de abajo)
        huecos = 34
        alto_total = sum(i.height for i in imgs) + huecos * (len(imgs) - 1)
        y = 300 + max(0, (1350 - alto_total) // 2)
        posiciones = []
        for i in imgs:
            posiciones.append(y)
            y += i.height + huecos
        for k in range(int(duracion * FPS)):
            t = k / FPS
            frame = base.copy()
            salida_esc = suave((t - (duracion - 0.3)) / 0.3)  # se desvanece al final de la escena
            for n_el, (img, py) in enumerate(zip(imgs, posiciones)):
                p = suave((t - n_el * sep) / ENTRADA)
                if p <= 0:
                    continue
                alfa = p * (1 - salida_esc)
                capa = img.copy()
                capa.putalpha(capa.getchannel("A").point(lambda a: int(a * alfa)))
                frame.paste(capa, (MARGEN, int(py + (1 - p) * DESLIZ)), capa)
            ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    print(ruta, f"{total:.0f} s")


CIERRE = lambda pregunta: (4.0, 0.5, [("titulo", pregunta), ("texto", "Busca el tuyo:"), ("web",)])  # noqa: E731

VIDEOS = {
    "1-lucia-destronada": [
        (3.0, 0.0, [("gancho", "Lucía ha perdido el trono")]),
        (4.5, 0.6, [("texto", "Fue el nombre más puesto a las niñas en España"), ("cifra", "21 años"), ("texto", "seguidos… hasta 2024")]),
        (5.5, 0.55, [("titulo", "Bebés de 2024"), ("fila", "1. Sofía", "3.325"), ("fila", "2. Lucía", "2.830"), ("fila", "3. Martina", "2.364"),
                     ("fila", "4. María", "2.189"), ("fila", "5. Vega", "2.129")]),
        CIERRE("¿Conoces a alguna Sofía de menos de 5 años?"),
    ],
    "2-nombres-en-extincion": [
        (3.0, 0.0, [("gancho", "Estos nombres van a desaparecer")]),
        (3.5, 0.5, [("texto", "Los llevan miles de personas en España…"), ("titulo", "pero casi todas mayores")]),
        (7.0, 0.7, [("fila", "Josefa", "71,6 años"), ("fila", "Dolores", "70,1 años"), ("fila", "Consuelo", "70,1 años"),
                    ("fila", "Vicenta", "73,9 años"), ("fila", "Saturnino", "70,1 años"), ("texto", "Edad media de quienes se llaman así")]),
        (4.0, 0.6, [("cifra", "225.853"), ("texto", "mujeres se llaman Josefa. Desde 2002 nunca ha estado entre los 100 nombres más puestos a las niñas")]),
        CIERRE("¿Tu abuela se llama así?"),
    ],
    "3-daenerys": [
        (3.0, 0.0, [("gancho", "En España hay 305 niñas que se llaman Daenerys")]),
        (5.5, 0.6, [("titulo", "Juego de Tronos en el registro"), ("fila", "Daenerys", "305"), ("fila", "Khaleesi", "49"), ("fila", "Arya", "2.022")]),
        (4.0, 0.6, [("texto", "Edad media de las Aryas:"), ("cifra", "5 años")]),
        CIERRE("¿Le pondrías el nombre de un personaje?"),
    ],
    "4-provincias": [
        (3.0, 0.0, [("gancho", "En estas provincias el nombre nº1 no es Antonio")]),
        (8.0, 0.75, [("fila", "Girona y Lleida", "Jordi"), ("fila", "Gipuzkoa", "Mikel"), ("fila", "Bizkaia", "Jon"),
                     ("fila", "Zaragoza y Toledo", "Jesús"), ("fila", "Asturias", "José Manuel"), ("fila", "Ceuta y Melilla", "Mohamed")]),
        (3.5, 0.5, [("texto", "En casi todas las demás gana"), ("titulo", "Antonio o Manuel")]),
        CIERRE("¿Cuál es el de tu provincia?"),
    ],
    "5-garcia-garcia": [
        (3.0, 0.0, [("gancho", "Hay 74.765 personas que se llaman García García")]),
        (6.5, 0.6, [("titulo", "Apellidos más comunes"), ("fila", "1. García", "1.446.937"), ("fila", "2. Rodríguez", "939.214"),
                    ("fila", "3. González", "930.137"), ("fila", "4. Fernández", "896.725"), ("fila", "5. López", "871.380")]),
        (3.0, 0.0, [("texto", "Personas con ese primer apellido en España")]),
        CIERRE("¿Tu apellido está en el top?"),
    ],
    "6-hugo-mujeres": [
        (3.0, 0.0, [("gancho", "En España hay 54 mujeres que se llaman Hugo")]),
        (5.0, 0.7, [("texto", "Y no son las únicas:"), ("fila", "Mujeres llamadas Hugo", "54"), ("fila", "Mujeres llamadas Leo", "96")]),
        (3.5, 0.5, [("texto", "Y Hugo es el 2.º nombre más puesto a los niños: en 2024 se lo pusieron a"), ("cifra", "2.734"), ("texto", "niños")]),
        CIERRE("¿Conoces algún nombre así?"),
    ],
    "7-anos-80-vs-ahora": [
        (3.0, 0.0, [("gancho", "Nombres de los 80 vs nombres de ahora")]),
        (5.5, 0.55, [("titulo", "Nacidos en los 80"), ("texto", "Chicos y chicas más comunes"), ("fila", "David", "Laura"), ("fila", "Javier", "Cristina"), ("fila", "Daniel", "María")]),
        (5.5, 0.55, [("titulo", "Bebés de 2024"), ("texto", "Los más puestos"), ("fila", "Mateo", "Sofía"), ("fila", "Hugo", "Lucía"), ("fila", "Martín", "Martina")]),
        CIERRE("¿Cuántos se llamaban como tú en tu clase?"),
    ],
    "10-nombres-que-suben": [
        (3.0, 0.0, [("gancho", "Los nombres de niña que están arrasando")]),
        (6.5, 0.55, [("texto", "Nuevos en el top 100 de bebés:"), ("fila", "Alaia", ""), ("fila", "Catalina", ""), ("fila", "Violeta", ""),
                     ("fila", "Aurora", ""), ("fila", "Cataleya", "")]),
        (4.5, 0.6, [("titulo", "Y el que más sube: Gala"), ("fila", "Puesto en 2019", "53.º"), ("fila", "Puesto en 2024", "16.º")]),
        CIERRE("¿Cuál le pondrías a tu hija?"),
    ],
}


if __name__ == "__main__":
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    carpeta.mkdir(parents=True, exist_ok=True)
    elegidos = sys.argv[2:] or list(VIDEOS)
    for nombre in elegidos:
        render(nombre, VIDEOS[nombre], carpeta)
