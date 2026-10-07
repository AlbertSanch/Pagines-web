"""Descarga los ficheros de nombres del INE que usa la web.

Guarda las hojas de cálculo originales en cuantossellaman/datos-ine/ (no se suben a GitHub:
se descargan de nuevo en cada actualización). Falla con un error visible si falta algún
fichero imprescindible, para que el workflow no publique una web vacía.

Uso: python cuantossellaman/scripts/descargar_ine.py
"""
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://www.ine.es/daco/daco42/nombyapel/"
IMPRESCINDIBLES = [
    "nombres_por_edad_media.xlsx",   # todos los nombres con 20 o más personas, con edad media
    "nombres_mas_frecuentes.xlsx",   # top 100 de España y top 50 por provincia de residencia
    "nombres_por_fecha.xlsx",        # top 50 por década de nacimiento (España y por provincia de nacimiento)
    "apellidos_frecuencia.xls",      # todos los apellidos con 20 o más personas como primer apellido
    "apellidos_mas_frecuentes.xls",  # top 100 de España y top 50 por provincia
]
OPCIONALES = []
PRIMER_ANIO_BEBES = 2002
SALIDA = Path(__file__).resolve().parent.parent / "datos-ine"
CABECERAS = {"User-Agent": "Mozilla/5.0 (cuantossellaman.es; datos abiertos del INE)"}


def descargar(nombre, obligatorio):
    url = BASE + nombre
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers=CABECERAS)
            with urllib.request.urlopen(req, timeout=120) as r:
                datos = r.read()
            if len(datos) < 5000 or datos[:5].lower().startswith(b"<!doc") or datos[:5].lower().startswith(b"<html"):
                raise ValueError("el INE ha devuelto una página web en lugar de una hoja de cálculo")
            (SALIDA / nombre).write_bytes(datos)
            print(f"OK {nombre} ({len(datos) // 1024} KB)")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                if obligatorio:
                    sys.exit(f"ERROR: no existe {url} (¿ha cambiado el INE el nombre del fichero?)")
                return False
            print(f"{nombre}: {e} (intento {intento + 1})", file=sys.stderr)
        except Exception as e:
            print(f"{nombre}: {e} (intento {intento + 1})", file=sys.stderr)
        time.sleep(10 * (intento + 1))
    if obligatorio:
        sys.exit(f"ERROR: no se ha podido descargar {url}")
    return False


def main():
    SALIDA.mkdir(exist_ok=True)
    for f in IMPRESCINDIBLES:
        descargar(f, True)
    for f in OPCIONALES:
        descargar(f, False)
    anios = [a for a in range(PRIMER_ANIO_BEBES, date.today().year + 1) if descargar(f"nomnac{a % 100:02d}.xlsx", False)]
    if not anios:
        sys.exit("ERROR: no se ha descargado ningún fichero de nombres de recién nacidos (nomnacAA.xlsx)")
    print(f"Bebés: {anios[0]}–{anios[-1]} ({len(anios)} años)")


if __name__ == "__main__":
    main()
