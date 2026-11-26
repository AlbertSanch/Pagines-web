"""Prepara los calendarios escolares para imprimir de imprimibles.es.

Lee el calendario escolar oficial de festivosde.es (festivos/data/escolar.json, sacado de la orden o resolución de cada
comunidad o provincia) y los festivos nacionales y autonómicos (festivos/data/festivos_AÑO.json), y escribe
imprimibles/content/datos/escolar-CURSO.json con, para cada territorio: inicio y fin de clases (Infantil y Primaria),
vacaciones, días no lectivos y festivos de septiembre a junio.

Uso: python imprimibles/scripts/calendarios_escolares.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "festivos" / "scripts"))
from comun import COMUNIDADES, slug  # noqa: E402

CORTOS = {"Epifanía del Señor": "Reyes", "Natividad del Señor": "Navidad", "Día de la Constitución Española": "Constitución",
          "Lunes siguiente a asunción de la Virgen": "Lunes tras la Asunción", "Fiesta Nacional de España": "Fiesta Nacional",
          "Inmaculada Concepción": "Inmaculada", "Todos los Santos": "Todos los Santos"}


def principal(lista):
    return next((x for x in lista if "Primaria" in x["etapas"]), lista[0]) if lista else None


def main():
    esc = json.loads((RAIZ / "festivos" / "data" / "escolar.json").read_text(encoding="utf-8"))
    curso = esc["curso"]
    a0, a1 = (int(x) for x in curso.split("-"))
    fest = {a: json.loads((RAIZ / "festivos" / "data" / f"festivos_{a}.json").read_text(encoding="utf-8"))["nacionales_autonomicos"]
            for a in (a0, a1) if (RAIZ / "festivos" / "data" / f"festivos_{a}.json").exists()}
    salida = {"curso": curso, "territorios": []}
    for t in esc["territorios"]:
        ini, fin = principal(t["inicio"]), principal(t["fin"])
        if not ini or not fin:
            continue
        d0, d1 = dt.date.fromisoformat(ini["fecha"]), dt.date.fromisoformat(fin["fecha"])
        nombre_cc = COMUNIDADES[t["ccaa"]][0]
        nombre = t["provincia"] or nombre_cc
        marcas = {}  # fecha ISO -> [tipo, texto]  (tipo: vac, nl, fest)
        for v in t["vacaciones"]:
            d, h = dt.date.fromisoformat(v["desde"]), dt.date.fromisoformat(v["hasta"])
            while d <= h:
                marcas[d.isoformat()] = ["vac", v["nombre"]]
                d += dt.timedelta(days=1)
        for x in t["no_lectivos"]:
            marcas.setdefault(x["fecha"], ["nl", x["motivo"]])
        festivos = []
        for a, cc in fest.items():
            for x in cc.get(t["ccaa"], []):
                f = dt.date.fromisoformat(x["f"])
                if dt.date(a0, 9, 1) <= f <= dt.date(a1, 6, 30):
                    n = CORTOS.get(x["n"], x["n"])
                    festivos.append([x["f"], n])
                    if f.weekday() < 5:
                        marcas.setdefault(x["f"], ["fest", n])
        salida["territorios"].append({
            "id": t["id"], "slug": slug(t["id"].replace("_", "-")), "ccaa": t["ccaa"], "comunidad": nombre_cc, "nombre": nombre,
            "es_provincia": bool(t["provincia"]), "inicio": ini["fecha"], "fin": fin["fecha"], "etapas": ini["etapas"],
            "otras_etapas": [[x["etapas"], x["fecha"]] for x in t["inicio"] if x is not ini],
            "vacaciones": sorted(([v["nombre"], v["desde"], v["hasta"]] for v in t["vacaciones"]), key=lambda v: v[1]),
            "no_lectivos": sorted([x["fecha"], x["motivo"]] for x in t["no_lectivos"]),
            "festivos": sorted(festivos), "marcas": dict(sorted(marcas.items())), "norma": t["norma"], "url": next(iter((t.get("urls") or {}).values()), None), "locales": t.get("locales"),
        })
    salida["nacionales"] = sorted({(x["f"], CORTOS.get(x["n"], x["n"])) for a, cc in fest.items() for x in cc.get("madrid", [])
                                   if dt.date(a0, 9, 1) <= dt.date.fromisoformat(x["f"]) <= dt.date(a1, 6, 30)
                                   and all(any(y["f"] == x["f"] for y in cc[k]) for k in cc)})
    salida["pendientes"] = [p["provincia"] or COMUNIDADES[p["ccaa"]][0] for p in esc.get("pendientes", [])]
    salida["territorios"].sort(key=lambda x: (slug(x["comunidad"]), slug(x["nombre"])))
    destino = RAIZ / "imprimibles" / "content" / "datos" / f"escolar-{curso}.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(salida['territorios'])} territorios → {destino}")


if __name__ == "__main__":
    main()
