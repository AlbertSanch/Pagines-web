"""Descarga los precios de las gasolineras del Ministerio y genera un resumen ligero.

Fuente: Ministerio para la Transición Ecológica y el Reto Demográfico (Geoportal de
gasolineras). El servicio devuelve todas las estaciones de España (unos 10 MB); este
script guarda solo lo que usa la web: medias por provincia y las gasolineras más
baratas de cada provincia.

Además genera una página estática por provincia (ahorrometro/gasolina/<provincia>.html)
con paginas_provincia.py.

Uso:
    python scripts/actualizar_carburantes.py                    # descarga del Ministerio
    python scripts/actualizar_carburantes.py --entrada datos.json  # usa un archivo local
"""

import argparse
import json
import os
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import paginas_provincia

URL = ("https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/"
       "PreciosCarburantes/EstacionesTerrestres/")
# El Ministerio corta las conexiones desde GitHub Actions; si se define esta variable,
# se descarga a través del Worker de Cloudflare (cloudflare/proxy-carburantes.js).
PROXY = os.environ.get("CARBURANTES_PROXY", "").strip()
WEB = Path(__file__).resolve().parent.parent / "ahorrometro"
MAS_BARATAS = 5  # gasolineras más baratas que se guardan por provincia y combustible

# Clave en la web -> campo del Ministerio
COMBUSTIBLES = {
    "gasolina95": "Precio Gasolina 95 E5",
    "gasolina98": "Precio Gasolina 98 E5",
    "diesel": "Precio Gasoleo A",
    "glp": "Precio Gases licuados del petróleo",
}

# Códigos INE de provincia (campo IDProvincia) -> nombre para mostrar
PROVINCIAS = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila",
    "06": "Badajoz", "07": "Baleares", "08": "Barcelona", "09": "Burgos", "10": "Cáceres",
    "11": "Cádiz", "12": "Castellón", "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña",
    "16": "Cuenca", "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Gipuzkoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lleida",
    "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
    "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
    "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria",
    "40": "Segovia", "41": "Sevilla", "42": "Soria", "43": "Tarragona", "44": "Teruel",
    "45": "Toledo", "46": "Valencia", "47": "Valladolid", "48": "Bizkaia", "49": "Zamora",
    "50": "Zaragoza", "51": "Ceuta", "52": "Melilla",
}


def descargar():
    errores = []
    for url in filter(None, [PROXY, URL]):
        peticion = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "ahorrometro.es (actualizacion de precios de carburantes)",
        })
        for intento in range(3):
            try:
                with urllib.request.urlopen(peticion, timeout=120) as r:
                    return json.loads(r.read().decode("utf-8-sig"))
            except Exception as e:  # el servidor del Ministerio falla a ratos
                errores.append(f"{url} (intento {intento + 1}): {e}")
                print(errores[-1], file=sys.stderr)
                time.sleep(10 * (intento + 1))
    raise SystemExit("No se han podido descargar los datos del Ministerio.")


def precio(texto):
    try:
        valor = float(str(texto).replace(",", "."))
    except ValueError:
        return None
    return valor if 0.3 < valor < 5 else None  # descarta valores vacíos o absurdos


def coord(texto):
    try:
        return round(float(str(texto).replace(",", ".")), 5)
    except ValueError:
        return None


MINUSCULAS = {"de", "del", "la", "las", "el", "los", "y", "a", "en"}


def titulo(texto):
    """'AVENIDA DE LA PAZ, 12' -> 'Avenida de la Paz, 12' (el Ministerio lo da en mayúsculas)."""
    palabras = []
    for i, p in enumerate(str(texto).strip().split()):
        if p.isupper():
            p = p.lower() if i and p.lower() in MINUSCULAS else p.capitalize()
        palabras.append(p)
    return " ".join(palabras)


def media(valores):
    return round(statistics.fmean(valores), 3)


def resumir(datos):
    if datos.get("ResultadoConsulta") not in (None, "OK"):
        raise SystemExit(f"El Ministerio ha respondido con un error: {datos.get('ResultadoConsulta')}")
    estaciones = datos.get("ListaEESSPrecio") or []
    if len(estaciones) < 1000:
        raise SystemExit(f"Respuesta sospechosa: solo {len(estaciones)} gasolineras")

    por_provincia = {}  # código -> combustible -> lista de (precio, estación)
    gasolineras = {}  # código -> lista de gasolineras normalizadas (para las páginas por provincia)
    for e in estaciones:
        if e.get("Tipo Venta", "P") != "P":  # solo venta al público general
            continue
        codigo = str(e.get("IDProvincia", "")).zfill(2)
        if codigo not in PROVINCIAS:
            continue
        g = {
            "rotulo": titulo(e.get("Rótulo", "")),
            "direccion": titulo(e.get("Dirección", "")),
            "municipio": titulo(e.get("Municipio", "")),
            "lat": coord(e.get("Latitud")),
            "lon": coord(e.get("Longitud (WGS84)")),
            "precios": {},
        }
        for clave, campo in COMBUSTIBLES.items():
            p = precio(e.get(campo, ""))
            if p is not None:
                g["precios"][clave] = p
                por_provincia.setdefault(codigo, {}).setdefault(clave, []).append((p, g))
        if g["precios"]:
            gasolineras.setdefault(codigo, []).append(g)

    provincias = {}
    todos = {clave: [] for clave in COMBUSTIBLES}
    for codigo, combustibles in sorted(por_provincia.items()):
        resumen = {"nombre": PROVINCIAS[codigo], "slug": paginas_provincia.slug(PROVINCIAS[codigo])}
        for clave, lista in combustibles.items():
            precios = [p for p, _ in lista]
            todos[clave].extend(precios)
            lista.sort(key=lambda x: x[0])
            resumen[clave] = {
                "media": media(precios),
                "min": min(precios),
                "max": max(precios),
                "n": len(precios),
                "baratas": [dict({k: g[k] for k in ("rotulo", "direccion", "municipio", "lat", "lon")}, precio=p)
                            for p, g in lista[:MAS_BARATAS]],
            }
        provincias[codigo] = resumen

    espana = {}
    for clave, precios in todos.items():
        if precios:
            espana[clave] = {"media": media(precios), "min": min(precios), "max": max(precios), "n": len(precios)}
    if "gasolina95" not in espana or "diesel" not in espana:
        raise SystemExit("Faltan los precios de gasolina 95 o diésel en la respuesta")

    return gasolineras, {
        "fuente": "Ministerio para la Transición Ecológica y el Reto Demográfico",
        "fechaMinisterio": datos.get("Fecha", ""),
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "espana": espana,
        "provincias": provincias,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--entrada", help="JSON del Ministerio ya descargado (para pruebas)")
    parser.add_argument("--web", default=str(WEB), help="Carpeta de la web (por defecto, ahorrometro/)")
    args = parser.parse_args()

    if args.entrada:
        datos = json.loads(Path(args.entrada).read_text(encoding="utf-8-sig"))
    else:
        datos = descargar()
    gasolineras, resumen = resumir(datos)

    web = Path(args.web)
    salida = web / "datos" / "carburantes.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resumen, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    e = resumen["espana"]
    print(f"{len(resumen['provincias'])} provincias · gasolina 95 {e['gasolina95']['media']} €/L · "
          f"diésel {e['diesel']['media']} €/L · {salida.stat().st_size // 1024} KB", file=sys.stderr)
    paginas_provincia.generar(resumen, gasolineras, web)


if __name__ == "__main__":
    main()
