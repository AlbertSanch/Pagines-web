"""Calcula el precio medio de la luz (PVPC) de las últimas semanas para las calculadoras.

Descarga de Red Eléctrica (REData) el precio horario del PVPC de los últimos DIAS días en la
península y guarda en ahorrometro/datos/luz.json la media de todas las horas y la de las
horas valle (de 0 a 8 h entre semana y todo el día los fines de semana), sin y con impuestos.
Las calculadoras usan estos valores como precio por defecto del kWh.

Uso:
    python scripts/actualizar_luz.py
    python scripts/actualizar_luz.py --entrada respuesta_ree.json   # para pruebas
"""

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DIAS = 28
TROZO = 7  # días por petición, para no pasar el límite de REE con datos horarios
IMPUESTOS = 1.0511 * 1.21  # impuesto eléctrico + IVA (aproximado, como en precio-luz-hoy)
URL = ("https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
       "?start_date={desde}T00:00&end_date={hasta}T23:59&time_trunc=hour"
       "&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741")
SALIDA = Path(__file__).resolve().parent.parent / "ahorrometro" / "datos" / "luz.json"


def descargar(desde, hasta):
    peticion = urllib.request.Request(URL.format(desde=desde, hasta=hasta), headers={
        "Accept": "application/json",
        "User-Agent": "ahorrometro.es (precio medio de la luz)",
    })
    for intento in range(3):
        try:
            with urllib.request.urlopen(peticion, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"REE {desde}–{hasta} (intento {intento + 1}): {e}", file=sys.stderr)
            time.sleep(10 * (intento + 1))
    raise SystemExit("No se han podido descargar los precios de Red Eléctrica.")


def valores_pvpc(respuesta):
    """Lista de (datetime con zona, €/MWh) del PVPC. Misma lógica que precio-luz-hoy.html."""
    for item in respuesta.get("included") or []:
        texto = f"{(item.get('attributes') or {}).get('title', '')} {item.get('type', '')}"
        if item.get("id") == "1001" or "pvpc" in texto.lower():
            return [(datetime.fromisoformat(v["datetime"]), v["value"])
                    for v in item["attributes"].get("values", []) if v.get("value") is not None]
    return []


def resumir(valores):
    # Agrupa por hora (REE puede dar datos cuartohorarios) y descarta horas repetidas entre trozos
    horas = {}
    for dt, v in valores:
        horas.setdefault(dt.replace(minute=0, second=0, microsecond=0), []).append(v)
    if len(horas) < 24 * 7:
        raise SystemExit(f"Respuesta sospechosa de REE: solo {len(horas)} horas")
    todas, valle = [], []
    for dt, lista in horas.items():
        p = sum(lista) / len(lista) / 1000  # €/MWh -> €/kWh
        todas.append(p)
        if dt.weekday() >= 5 or dt.hour < 8:
            valle.append(p)
    media = sum(todas) / len(todas)
    media_valle = sum(valle) / len(valle)
    for nombre, p in (("media", media), ("valle", media_valle)):
        if not 0.01 < p < 0.6:
            raise SystemExit(f"Precio {nombre} fuera de rango: {p}")
    fechas = sorted(d.date() for d in horas)
    return {
        "fuente": "Red Eléctrica (REData), PVPC 2.0TD península",
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "desde": fechas[0].isoformat(),
        "hasta": fechas[-1].isoformat(),
        "horas": len(horas),
        "sinImpuestos": {"media": round(media, 4), "valle": round(media_valle, 4)},
        "conImpuestos": {"media": round(media * IMPUESTOS, 3), "valle": round(media_valle * IMPUESTOS, 3)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--entrada", help="Respuesta de REE ya descargada (para pruebas)")
    parser.add_argument("--salida", default=str(SALIDA))
    args = parser.parse_args()

    hoy = datetime.now(ZoneInfo("Europe/Madrid")).date()
    if args.entrada:
        valores = valores_pvpc(json.loads(Path(args.entrada).read_text(encoding="utf-8")))
    else:
        valores = []
        fin = hoy  # el día de hoy ya está publicado completo desde la tarde anterior
        inicio = fin - timedelta(days=DIAS - 1)
        d = inicio
        while d <= fin:
            h = min(d + timedelta(days=TROZO - 1), fin)
            valores += valores_pvpc(descargar(d.isoformat(), h.isoformat()))
            d = h + timedelta(days=1)
    resumen = resumir(valores)

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resumen, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    c = resumen["conImpuestos"]
    print(f"Luz {resumen['desde']}–{resumen['hasta']}: media {c['media']} €/kWh, valle {c['valle']} €/kWh "
          "(con impuestos)", file=sys.stderr)


if __name__ == "__main__":
    main()
