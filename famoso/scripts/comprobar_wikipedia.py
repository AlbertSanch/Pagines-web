#!/usr/bin/env python3
"""Comprueba con Wikipedia los datos clave de cada famoso.

Cada famoso de data/mundial.json y data/espana.json puede tener "comprobar": textos (años, lugares…) que tienen que
aparecer en el artículo de su "fuente" (es.wikipedia.org). Uso:

  python famoso/scripts/comprobar_wikipedia.py [--desde AAAA-MM-DD]

Sin --desde comprueba todos; con él, solo los programados a partir de esa fecha.
"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "data"
CABECERAS = {"User-Agent": "famosodeldia-comprobador/1.0"}


def normal(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"(\d)[.\s ]+(?=\d{3}\b)", r"\1", t.replace("&nbsp;", " "))


def articulo(url):
    titulo = urllib.parse.unquote(url.rsplit("/wiki/", 1)[1])
    for _ in range(3):
        try:
            q = urllib.parse.urlencode({"title": titulo, "action": "raw"})
            req = urllib.request.Request(f"https://es.wikipedia.org/w/index.php?{q}", headers=CABECERAS)
            texto = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
            m = re.match(r"#(?:REDIRECCIÓN|REDIRECT)\s*\[\[([^\]|#]+)", texto, re.I)
            if m:
                titulo = m.group(1)
                continue
            return texto
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def main():
    desde = sys.argv[sys.argv.index("--desde") + 1] if "--desde" in sys.argv else ""
    mal = 0
    for archivo in ("mundial.json", "espana.json"):
        for f in json.loads((DATOS / archivo).read_text(encoding="utf-8")):
            if f.get("fecha", "") < desde or not f.get("comprobar"):
                continue
            texto = articulo(f["fuente"])
            if texto is None:
                print(f"✗ {f['nombre']}: no se encuentra el artículo {f['fuente']}")
                mal += 1
                continue
            n = normal(texto)
            faltan = [c for c in f["comprobar"] if normal(c) not in n]
            if faltan:
                print(f"✗ {f['nombre']}: el artículo no menciona {', '.join(faltan)}")
                mal += 1
            time.sleep(.3)
    print("Todo comprobado" if not mal else f"{mal} famoso(s) por revisar")
    sys.exit(1 if mal else 0)


if __name__ == "__main__":
    main()
