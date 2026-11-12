#!/usr/bin/env python3
"""Reparte los hechos comprobados en días: data/dias.json = {"AAAA-MM-DD": [ancla, h1, h2, h3, h4, h5]}.

- 6 hechos por día, todos de años distintos; el primero (el «ancla») sale ya colocado en la línea del tiempo.
- Al menos 2 de España y 2 del mundo, y como mucho 2 de la misma categoría.
- Mezcla de épocas: al menos uno anterior a 1900 y al menos tres posteriores.
- Un hecho no se repite hasta pasados DESCANSO días.
- Los días ya programados no se tocan (así nadie ve cambiar un día pasado); solo se añaden los que faltan.

Uso: python cronologia/scripts/programar.py [días hacia delante, por defecto 60]
"""
import datetime as dt
import json
import random
import sys
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_web import LANZAMIENTO, HOY  # noqa: E402

POR_DIA = 6
DESCANSO = 14


def valido(grupo):
    anios = [h["anio"] for h in grupo]
    if len(set(anios)) != len(anios):
        return False
    if sum(h["ambito"] == "espana" for h in grupo) < 2 or sum(h["ambito"] == "mundo" for h in grupo) < 2:
        return False
    cats = [h["categoria"] for h in grupo]
    if max(cats.count(c) for c in cats) > 2:
        return False
    return sum(a < 1900 for a in anios) >= 1 and sum(a >= 1900 for a in anios) >= 3


def main():
    adelante = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    hechos = json.loads((DATOS / "hechos.json").read_text(encoding="utf-8"))
    ver = json.loads((DATOS / "verificacion.json").read_text(encoding="utf-8"))
    buenos = [h for h in hechos if ver.get(h["slug"], {}).get("ok")]
    ruta = DATOS / "dias.json"
    dias = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    ultimo_uso = {}
    for f, lista in sorted(dias.items()):
        for s in lista:
            ultimo_uso[s] = dt.date.fromisoformat(f)
    inicio = max(LANZAMIENTO, min(HOY, LANZAMIENTO))
    nuevos = 0
    for i in range((HOY - inicio).days + adelante + 1):
        f = inicio + dt.timedelta(days=i)
        if f.isoformat() in dias:
            continue
        rnd = random.Random(f"qfa-{f.isoformat()}")
        libres = [h for h in buenos if (f - ultimo_uso.get(h["slug"], dt.date.min + dt.timedelta(days=DESCANSO))).days >= DESCANSO]
        # los que llevan más tiempo sin salir, primero (con algo de azar)
        libres.sort(key=lambda h: (ultimo_uso.get(h["slug"], dt.date.min), rnd.random()))
        candidatos = libres[: max(30, len(libres) // 2)]
        for _ in range(5000):
            grupo = rnd.sample(candidatos, POR_DIA)
            if valido(grupo):
                break
        else:
            sys.exit(f"No hay hechos suficientes para el {f}: añade más a data/hechos.json")
        # ancla: uno de los años del medio, para que haya huecos a los dos lados
        por_anio = sorted(grupo, key=lambda h: h["anio"])
        ancla = rnd.choice(por_anio[1:-1])
        resto = [h for h in grupo if h is not ancla]
        rnd.shuffle(resto)
        dias[f.isoformat()] = [ancla["slug"]] + [h["slug"] for h in resto]
        for h in grupo:
            ultimo_uso[h["slug"]] = f
        nuevos += 1
    ruta.write_text(json.dumps(dict(sorted(dias.items())), ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"{nuevos} días nuevos; programado hasta el {max(dias)} ({len(buenos)} hechos comprobados).")


if __name__ == "__main__":
    main()
