"""Descarga del INE las tablas del Atlas de Distribución de Renta de los Hogares (ADRH).

El ADRH (operación 353) publica, para cada provincia, una tabla por tema con todos sus
municipios, distritos y secciones censales y todos los años desde 2015. Descargamos estos temas:
  - renta: «Indicadores de renta media y mediana»
  - fuentes: «Distribución por fuente de ingresos»
  - gini: «Índice de Gini y Distribución de la renta P80/P20»
  - demografia: «Indicadores demográficos»
Los CSV originales se guardan en rentamedia/datos-ine/ (no se suben a GitHub).
Falla con un error visible si falta alguna tabla, para que el workflow no publique datos a medias.

Uso: python rentamedia/scripts/descargar_ine.py
"""
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OPERACION = 353
TEMAS = {
    "renta": "Indicadores de renta media y mediana",
    "fuentes": "Distribución por fuente de ingresos",
    "gini": "Índice de Gini y Distribución de la renta P80/P20",
    "demografia": "Indicadores demográficos",
}
MINIMO_TABLAS = 52  # una por provincia (más Ceuta y Melilla) y la nacional
EN_PARALELO = 6  # descargas a la vez: cada tabla tarda bastante en generarse en el INE
SALIDA = Path(__file__).resolve().parent.parent / "datos-ine"
CABECERAS = {"User-Agent": "Mozilla/5.0 (rentamedia.es; datos abiertos del INE)"}


def es_csv(datos):
    return not datos[:200].lower().lstrip().startswith((b"<!doc", b"<html")) and b";" in datos[:500]


def bajar(url, comprobar=None, intentos=4):
    """Descarga con reintentos. Con «comprobar», también reintenta si el INE devuelve otra cosa
    (a veces responde con una página de error en lugar del CSV cuando la tabla tarda en generarse)."""
    for intento in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=CABECERAS), timeout=180) as r:
                datos = r.read()
            if comprobar is None or comprobar(datos):
                return datos
            print(f"{url}: no es un CSV, empieza por {datos[:120]!r} (intento {intento + 1})", file=sys.stderr)
        except Exception as e:
            print(f"{url}: {e} (intento {intento + 1})", file=sys.stderr)
        time.sleep(30 * (intento + 1))
    sys.exit(f"ERROR: no se ha podido descargar {url} como CSV")


def main():
    SALIDA.mkdir(exist_ok=True)
    tablas = json.loads(bajar(f"https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{OPERACION}"))
    indice, trabajos = {}, []
    for tema, nombre in TEMAS.items():
        ids = sorted(t["Id"] for t in tablas if t["Nombre"].strip() == nombre)
        if len(ids) < MINIMO_TABLAS:
            sys.exit(f"ERROR: solo hay {len(ids)} tablas de «{nombre}» (¿ha cambiado el INE la publicación?)")
        indice[tema] = ids
        trabajos += [(tema, i) for i in ids]

    def una(trabajo):
        tema, i = trabajo
        destino = SALIDA / f"{tema}_{i}.csv"
        inicio = time.time()
        datos = bajar(f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{i}.csv", es_csv, intentos=5)
        destino.write_bytes(datos)
        print(f"OK {destino.name} ({len(datos) // 1024} KB, {time.time() - inicio:.0f} s)", flush=True)

    with ThreadPoolExecutor(EN_PARALELO) as ejecutor:
        list(ejecutor.map(una, trabajos))
    (SALIDA / "tablas.json").write_text(json.dumps(indice), encoding="utf-8")


if __name__ == "__main__":
    main()
