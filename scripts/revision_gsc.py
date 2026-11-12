"""Lectura de Search Console de todas las webs, a través del Worker revisor-gsc (cloudflare/revisor-gsc.js).

La contraseña del Worker la añade el proxy de la sesión de Claude (no está en el código ni en variables).
Uso:
  python scripts/revision_gsc.py                      resumen de clics e impresiones por semana de cada web
  python scripts/revision_gsc.py inspeccionar URL     estado de indexación de una página
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

WORKER = "https://revisor-gsc.albertsanchezguiu.workers.dev"
WEBS = ["festivosde.es", "rentamedia.es", "cuantossellaman.es", "cuantosdiasfaltan.es", "ahorrometro.es", "famosodeldia.es", "imprimibles.es"]
CABECERAS = {"Content-Type": "application/json", "User-Agent": "revisor-webs/1.0"}  # el agente de Python por defecto lo bloquea Cloudflare


def llamar(ruta, cuerpo, intentos=4):
    req = urllib.request.Request(WORKER + ruta, data=json.dumps(cuerpo).encode(), headers=CABECERAS, method="POST")
    for i in range(intentos):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code < 500 or i == intentos - 1:
                raise
            time.sleep(2 * (i + 1))


def consulta(web, cuerpo):
    sitio = urllib.parse.quote(f"sc-domain:{web}", safe="")
    return llamar(f"/webmasters/v3/sites/{sitio}/searchAnalytics/query", cuerpo).get("rows", [])


def inspeccionar(url):
    web = urllib.parse.urlparse(url).netloc.removeprefix("www.")
    r = llamar("/v1/urlInspection/index:inspect", {"inspectionUrl": url, "siteUrl": f"sc-domain:{web}", "languageCode": "es"})
    return r.get("inspectionResult", {}).get("indexStatusResult", r)


def resumen():
    fin = date.today() - timedelta(days=2)  # Search Console va unos dos días por detrás
    semanas = [(fin - timedelta(days=7 * i + 6), fin - timedelta(days=7 * i)) for i in range(3, -1, -1)]
    print("web".ljust(22) + "".join(f"{a.strftime('%d/%m')}-{b.strftime('%d/%m')}".rjust(22) for a, b in semanas))
    for web in WEBS:
        filas = consulta(web, {"startDate": semanas[0][0].isoformat(), "endDate": fin.isoformat(), "dimensions": ["date"], "rowLimit": 100})
        celdas = []
        for a, b in semanas:
            sel = [f for f in filas if a.isoformat() <= f["keys"][0] <= b.isoformat()]
            celdas.append(f"{sum(f['clicks'] for f in sel):.0f} cl / {sum(f['impressions'] for f in sel):.0f} imp".rjust(22))
        print(web.ljust(22) + "".join(celdas))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "inspeccionar":
        print(json.dumps(inspeccionar(sys.argv[2]), ensure_ascii=False, indent=1))
    else:
        resumen()
