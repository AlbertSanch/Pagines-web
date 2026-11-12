#!/usr/bin/env python3
"""Comprueba cada hecho de data/hechos.json contra su artículo de Wikipedia en español: el artículo tiene que existir y
mencionar el año del hecho. Guarda el resultado en data/verificacion.json (lo usa generar_web.py para publicar solo
los hechos comprobados) y lista los que hay que revisar a mano.

Uso: python cronologia/scripts/verificar.py [--solo-nuevos]
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "data"
UA = {"User-Agent": "revisor-webs/1.0 (proyecto personal; comprobación puntual de años)"}


def wikitexto(titulo, saltos=3):
    url = "https://es.wikipedia.org/w/index.php?action=raw&title=" + urllib.parse.quote(titulo.replace(" ", "_"))
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                texto = r.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, titulo
            time.sleep(5 * (intento + 1))
    else:
        return None, titulo
    m = re.match(r"\s*#(?:REDIRECCIÓN|REDIRECCION|REDIRECT)\s*\[\[([^\]|#]+)", texto, re.I)
    if m and saltos:
        return wikitexto(m.group(1), saltos - 1)
    return texto, titulo


def patrones(h):
    a = h["anio"]
    if a <= -1000000:
        return [rf"{abs(a) // 1000000}\s*millones"]
    if a <= -10000:
        miles, resto = divmod(abs(a), 1000)
        return [rf"{miles}(?:[\s.\u00a0]|&nbsp;)?{resto:03d}", rf"{miles}\s*mil"]
    if a < 0:
        return [rf"\b{abs(a)}\s*a\.?\s*(?:&nbsp;)?\s*C", rf"\b{abs(a)}\b"]
    return [rf"\b{a}\b"]


def main():
    hechos = json.loads((DATOS / "hechos.json").read_text(encoding="utf-8"))
    ruta = DATOS / "verificacion.json"
    previo = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    solo_nuevos = "--solo-nuevos" in sys.argv
    malos = []
    for h in hechos:
        clave = f'{h["slug"]}|{h["anio"]}|{h["wiki"]}'
        if solo_nuevos and previo.get(h["slug"], {}).get("clave") == clave and previo[h["slug"]]["ok"]:
            continue
        texto, titulo = wikitexto(h["wiki"])
        if texto is None:
            res = {"ok": False, "motivo": "no existe el artículo"}
        else:
            veces = sum(len(re.findall(p, texto)) for p in patrones(h))
            res = {"ok": veces > 0, "veces": veces, "articulo": titulo,
                   "motivo": "" if veces else "el artículo no menciona el año"}
        if h.get("revisado_a_mano"):  # comprobado con otra fuente, anotado en el propio hecho
            res["ok"] = True
        res["clave"] = clave
        previo[h["slug"]] = res
        if not res["ok"]:
            malos.append(f'{h["slug"]} ({h["anio"]}, «{h["wiki"]}»): {res["motivo"]}')
        time.sleep(0.4)
    ruta.write_text(json.dumps(previo, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    ok = sum(1 for h in hechos if previo.get(h["slug"], {}).get("ok"))
    print(f"{ok} de {len(hechos)} hechos comprobados.")
    if malos:
        print("Revisar:\n  " + "\n  ".join(malos))


if __name__ == "__main__":
    main()
