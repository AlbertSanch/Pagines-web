"""Exploración temporal de las publicaciones de Hacienda (IRPF por municipios y por código postal), 2.ª ronda.

Para cada página guarda un resumen de su tabla: número de filas, clases de fila (niveles) y las primeras filas.
No forma parte de la web.

Uso: python rentamedia/scripts/explorar_hacienda.py
"""
import html
import re
import urllib.parse
import urllib.request
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "prueba-hacienda"
UA = {"User-Agent": "Mozilla/5.0 (rentamedia.es; datos abiertos de la AEAT)"}
RAIZ = "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites"


def bajar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def celdas(fila):
    return [html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c))).strip()
            for c in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", fila, re.S)]


def tabla(nombre, url):
    s = bajar(url)
    titulo = re.search(r'<h1 class="titulo">\s*(.*?)</h1>', s, re.S)
    lineas = [f"URL: {url}", f"Título: {titulo.group(1).strip() if titulo else ''}", f"Tamaño: {len(s)}"]
    hijos = re.findall(r'<a href="((?:home_parcial|jrubik)[^"]+)">([^<]+)</a>', s)
    lineas.append(f"Enlaces a tablas/carpetas: {hijos[:20]}")
    for t in re.findall(r"<table\b.*?</table>", s, re.S)[:2]:
        filas = re.findall(r"<tr\b([^>]*)>(.*?)</tr>", t, re.S)
        clases = {}
        for a, _ in filas:
            m = re.search(r'class="([^"]+)"', a)
            clases[m.group(1) if m else ""] = clases.get(m.group(1) if m else "", 0) + 1
        lineas.append(f"\nTABLA: {len(filas)} filas, clases {clases}")
        for _, f in filas[:14]:
            lineas.append("  " + " | ".join(celdas(f))[:400])
        lineas.append("  ...")
        for _, f in filas[-4:]:
            lineas.append("  " + " | ".join(celdas(f))[:400])
    (SALIDA / f"r2_{nombre}.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return s, hijos


def main():
    SALIDA.mkdir(exist_ok=True)
    base = f"{RAIZ}/irpfmunicipios/2024/"
    for nombre, pagina in [("mun_alfabetico", "jrubikf33b43cbb020952b18117bae61c3cf587ba2d823d.html"),
                           ("mun_ambito", "jrubik28b31410534a65101f6d0deb7e75a87859f3915f.html"),
                           ("mun_posicionamiento", "home_parcial22122dc22b05995f268ba8575ff446255e939aa2.html")]:
        try:
            _, hijos = tabla(nombre, base + pagina)
            for i, (h, _) in enumerate(hijos[:4]):
                if h != pagina:
                    tabla(f"{nombre}_hijo{i}", base + h)
        except Exception as e:
            (SALIDA / f"r2_{nombre}_error.txt").write_text(f"{e}\n")
    # Código postal: la tabla «Renta bruta y Renta disponible inframunicipal» de cada año
    for anio in range(2018, 2025):
        try:
            home = bajar(f"{RAIZ}/irpfCodPostal/{anio}/home.html")
            enlace = re.search(r'href="([^"]+)"[^>]*>\s*Renta bruta y Renta disponible inframunicipal', home)
            if not enlace:
                inicio = re.search(r'href="(home[0-9a-f]+\.html)"', home)
                if inicio:
                    home = bajar(urllib.parse.urljoin(f"{RAIZ}/irpfCodPostal/{anio}/home.html", inicio.group(1)))
                    enlace = re.search(r'href="([^"]+)"[^>]*>\s*Renta bruta y Renta disponible inframunicipal', home)
            (SALIDA / f"r2_cp_{anio}.txt").write_text(f"{anio}: {enlace.group(1) if enlace else 'NO ENCONTRADO'}\n")
        except Exception as e:
            (SALIDA / f"r2_cp_{anio}.txt").write_text(f"{anio}: ERROR {e}\n")


if __name__ == "__main__":
    main()
