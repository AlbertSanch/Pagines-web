"""Descarga del INE los contornos de los municipios y de las secciones censales de las ciudades grandes.

Usa el servicio de mapas del Atlas de Distribución de Renta de los Hogares (ArcGIS del INE), que ya trae las
geometrías simplificadas por el servidor (maxAllowableOffset). Coordenadas en metros (ETRS89 / UTM 30N),
redondeadas a enteros. Escribe:
  - data/geo_municipios.json: {código de municipio: [anillos]} (cada anillo, una lista plana x1, y1, x2, y2…)
  - data/geo_secciones.json: {código de municipio: {código de sección: [anillos]}} de los municipios con al menos
    MIN_HAB_SECCIONES habitantes.

Uso: python rentamedia/scripts/descargar_mapas.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
SERVICIO = "https://www.ine.es/servergis/rest/services/Hosted/ADRH_{anio}_Renta_media_por_persona/FeatureServer"
UA = {"User-Agent": "Mozilla/5.0 (rentamedia.es; datos abiertos del INE)"}
MIN_HAB_SECCIONES = 100000
TOLERANCIA_MUNICIPIOS = 150   # metros
TOLERANCIA_SECCIONES = 12


def bajar(url):
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"{url[:150]}: {e} (intento {intento + 1})", file=sys.stderr)
            time.sleep(10 * (intento + 1))
    sys.exit(f"ERROR: no se ha podido descargar {url[:200]}")


def servicio():
    """El año más reciente que tenga servicio de mapas."""
    for anio in range(2030, 2014, -1):
        try:
            with urllib.request.urlopen(urllib.request.Request(SERVICIO.format(anio=anio) + "?f=json", headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            if "layers" in d:
                return SERVICIO.format(anio=anio)
        except Exception:
            pass
    sys.exit("ERROR: no encuentro el servicio de mapas del INE")


def consultar(base, capa, where, campos, tolerancia):
    resultado, desde = [], 0
    while True:
        q = urllib.parse.urlencode({"where": where, "outFields": campos, "returnGeometry": "true", "outSR": "25830",
                                    "maxAllowableOffset": tolerancia, "geometryPrecision": 0, "resultOffset": desde,
                                    "resultRecordCount": 1000, "orderByFields": "objectid_1", "f": "json"})
        d = bajar(f"{base}/{capa}/query?{q}")
        if "error" in d:
            sys.exit(f"ERROR del servicio: {d['error']}")
        feats = d.get("features", [])
        resultado += feats
        if not feats or not d.get("exceededTransferLimit"):
            return resultado
        desde += len(feats)


def anillos(geom):
    return [[int(round(v)) for punto in anillo for v in punto[:2]] for anillo in (geom or {}).get("rings", []) if len(anillo) >= 4]


def main():
    base = servicio()
    print("Servicio:", base)
    municipios = {}
    for f in consultar(base, 1, "1=1", "cumun", TOLERANCIA_MUNICIPIOS):
        cod = (f["attributes"].get("cumun") or "").strip()
        if len(cod) == 5 and f.get("geometry"):
            municipios.setdefault(cod, []).extend(anillos(f["geometry"]))
    if len(municipios) < 8000:
        sys.exit(f"ERROR: solo {len(municipios)} municipios con contorno")
    (DATOS / "geo_municipios.json").write_text(json.dumps(municipios, separators=(",", ":")), encoding="utf-8")
    print(f"Municipios: {len(municipios)}")

    # Ciudades grandes: población del último año del INE
    demo = json.loads((DATOS / "mun_demografia.json").read_text(encoding="utf-8"))
    i = demo["indicadores"].index("Población")
    grandes = sorted(c for c, fila in demo["datos"].items() if (fila[i][-1] or 0) >= MIN_HAB_SECCIONES)
    secciones = {}
    for k in range(0, len(grandes), 20):
        lote = ",".join(f"'{c}'" for c in grandes[k:k + 20])
        for f in consultar(base, 3, f"cumun IN ({lote})", "cumun,cusec", TOLERANCIA_SECCIONES):
            a = f["attributes"]
            if f.get("geometry"):
                secciones.setdefault(a["cumun"], {}).setdefault(a["cusec"], []).extend(anillos(f["geometry"]))
    (DATOS / "geo_secciones.json").write_text(json.dumps(secciones, separators=(",", ":")), encoding="utf-8")
    print(f"Secciones: {sum(len(v) for v in secciones.values())} de {len(secciones)} ciudades")


if __name__ == "__main__":
    main()
