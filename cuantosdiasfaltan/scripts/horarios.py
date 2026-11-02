"""Horarios de F1 y MotoGP para /horario-f1/ y /horario-motogp/.

Descarga el calendario con la hora de cada sesión y lo guarda en cuantosdiasfaltan/horarios.json,
con las horas en UTC (el generador las pasa a hora peninsular y de Canarias):
  - F1: Jolpica (api.jolpi.ca), la continuación de la base de datos Ergast, con los horarios oficiales de la F1.
  - MotoGP: la API pública de motogp.com (la que usa su propio calendario).
Si una fuente falla, se conserva lo último que se descargó bien: la web nunca se queda sin horarios.
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "horarios.json"
UA = {"User-Agent": "cuantosdiasfaltan.es (horarios; contacto en la web)", "Accept": "application/json"}

PAISES = {  # nombre en español del GP según el país (o la ciudad, si en el país hay más de uno)
    "Australia": "Australia", "China": "China", "Japan": "Japón", "Bahrain": "Baréin", "Saudi Arabia": "Arabia Saudí",
    "Miami": "Miami", "Canada": "Canadá", "Monaco": "Mónaco", "Barcelona": "Barcelona-Cataluña", "Madrid": "España",
    "Austria": "Austria", "UK": "Gran Bretaña", "Belgium": "Bélgica", "Hungary": "Hungría", "Netherlands": "Países Bajos",
    "Italy": "Italia", "Azerbaijan": "Azerbaiyán", "Singapore": "Singapur", "Austin": "Estados Unidos", "Mexico": "México",
    "Brazil": "Brasil", "Las Vegas": "Las Vegas", "Qatar": "Qatar", "UAE": "Abu Dabi", "Malaysia": "Malasia",
    "Portugal": "Portugal", "Turkey": "Turquía", "Türkiye": "Turquía", "Spain": "España",
}
MOTOGP = {  # código de país de motogp.com -> nombre del GP
    "TH": "Tailandia", "BR": "Brasil", "US": "las Américas", "ES": "España", "FR": "Francia", "IT": "Italia", "HU": "Hungría",
    "CZ": "Chequia", "NL": "Países Bajos", "DE": "Alemania", "GB": "Gran Bretaña", "AT": "Austria", "SM": "San Marino",
    "JP": "Japón", "ID": "Indonesia", "AU": "Australia", "MY": "Malasia", "QA": "Qatar", "PT": "Portugal", "AR": "Argentina",
    "KZ": "Kazajistán", "IN": "India",
}
NOMBRES_ES_MOTOGP = {"ARAGON": "Aragón", "CATALONIA": "Cataluña", "CATALUNYA": "Cataluña", "VALENCIA": "Valencia", "SPAIN": "España"}
SESIONES_F1 = [("FirstPractice", "Libres 1"), ("SecondPractice", "Libres 2"), ("ThirdPractice", "Libres 3"),
               ("SprintQualifying", "Clasificación al sprint"), ("SprintShootout", "Clasificación al sprint"),
               ("Sprint", "Sprint"), ("Qualifying", "Clasificación")]
SESIONES_MOTOGP = {"FP1": "Libres 1", "PR": "Práctica", "FP2": "Libres 2", "Q1": "Clasificación 1", "Q2": "Clasificación 2",
                   "SPR": "Sprint", "WUP": "Warm up", "RAC": "Carrera"}


def bajar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def utc(fecha, hora):
    return dt.datetime.fromisoformat(f"{fecha}T{hora.rstrip('Z')}").replace(tzinfo=dt.timezone.utc).isoformat()


def f1(anio):
    carreras = []
    for r in bajar(f"https://api.jolpi.ca/ergast/f1/{anio}.json?limit=100")["MRData"]["RaceTable"]["Races"]:
        if "time" not in r:
            continue  # aún sin hora: no se puede dar el horario
        lugar = r["Circuit"]["Location"]
        clave = next((k for k in (lugar["locality"], lugar["country"]) if k in PAISES), None)
        if not clave:
            print(f"AVISO F1 {anio}: país sin nombre en español: {r['raceName']} ({lugar['locality']}, {lugar['country']})")
        sesiones = [{"n": nombre, "utc": utc(r[k]["date"], r[k]["time"])} for k, nombre in SESIONES_F1 if r.get(k, {}).get("time")]
        sesiones.append({"n": "Carrera", "utc": utc(r["date"], r["time"])})
        carreras.append({"gp": f"GP de {PAISES.get(clave, r['raceName'])}", "ronda": int(r["round"]), "circuito": r["Circuit"]["circuitName"],
                         "ciudad": lugar["locality"], "sesiones": sorted(sesiones, key=lambda s: s["utc"])})
    return carreras


def motogp(anio):
    carreras = []
    for e in bajar(f"https://api.pulselive.motogp.com/motogp/v1/events?seasonYear={anio}"):
        if e.get("kind") != "GP" or e.get("status") == "CANCELLED":
            continue
        sesiones = []
        for b in e.get("broadcasts") or []:
            cat = (b.get("category") or {}).get("acronym") if isinstance(b.get("category"), dict) else None
            corto = b.get("shortname")
            if cat == "MGP" and corto in SESIONES_MOTOGP:
                sesiones.append({"n": SESIONES_MOTOGP[corto], "utc": dt.datetime.fromisoformat(b["date_start"]).astimezone(dt.timezone.utc).isoformat()})
            elif cat in ("MT2", "MT3") and corto == "RAC":
                sesiones.append({"n": f"Carrera de {'Moto2' if cat == 'MT2' else 'Moto3'}",
                                 "utc": dt.datetime.fromisoformat(b["date_start"]).astimezone(dt.timezone.utc).isoformat()})
        if not any(s["n"] == "Carrera" for s in sesiones):
            continue  # aún sin horario publicado
        nombre = re.search(r"GRAND PRIX OF (?:THE )?([A-Z ]+?)(?: AND THE|$)", e["name"].strip())
        pais = NOMBRES_ES_MOTOGP.get(nombre.group(1).strip()) if nombre else None
        pais = pais or MOTOGP.get(e.get("country"))
        if not pais:
            print(f"AVISO MotoGP {anio}: país sin nombre en español: {e['name']} ({e.get('country')})")
        carreras.append({"gp": f"GP de {pais or e['name'].title()}", "circuito": e["circuit"]["name"], "ciudad": e["circuit"].get("place") or "",
                         "sesiones": sorted(sesiones, key=lambda s: s["utc"])})
    carreras.sort(key=lambda c: c["sesiones"][-1]["utc"])
    for i, c in enumerate(carreras, 1):
        c["ronda"] = i
    return carreras


def main():
    datos = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {}
    anio = dt.date.today().year
    for serie, lector in (("f1", f1), ("motogp", motogp)):
        for a in (anio, anio + 1):
            try:
                carreras = lector(a)
            except Exception as e:  # se queda lo que había
                print(f"ERROR {serie} {a}: {e}")
                continue
            if carreras or str(a) not in datos.get(serie, {}):
                datos.setdefault(serie, {})[str(a)] = carreras
            print(f"{serie} {a}: {len(carreras)} carreras con horario")
    datos["descargado"] = dt.date.today().isoformat()
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    if not datos.get("f1") and not datos.get("motogp"):
        sys.exit("No hay horarios")


if __name__ == "__main__":
    main()
