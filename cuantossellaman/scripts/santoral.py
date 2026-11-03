"""Santoral de cuantossellaman.es a partir de data/santoral.json (lo mantiene Albert a mano).

Cada entrada: nombre, fecha («MM-DD», vacía si es variable), fecha_texto, santo, otras_fechas («MM-DD texto; MM-DD texto»),
confianza («alta» o «revisar») y nota. Solo se publican las de confianza «alta»: las de «revisar» quedan ocultas hasta que
Albert las verifique y les cambie la confianza en el JSON.
"""
import datetime as dt
import json
import re
from pathlib import Path

from tildes import normalizar

FICHERO = Path(__file__).resolve().parent.parent / "data" / "santoral.json"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
# Fiestas que dependen de la Pascua: días que se suman al Domingo de Resurrección
VARIABLES = {"lunes de pentecostes": (50, "el lunes de Pentecostés"), "domingo siguiente a pentecostes": (56, "el domingo de la Santísima Trinidad, el siguiente a Pentecostés")}


def pascua(anio):
    """Domingo de Resurrección (algoritmo de Meeus/Jones/Butcher, calendario gregoriano)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mes = (h + l_ - 7 * m + 114) // 31
    dia = (h + l_ - 7 * m + 114) % 31 + 1
    return dt.date(anio, mes, dia)


def texto_dia(mmdd):
    m, d = int(mmdd[:2]), int(mmdd[3:])
    return f"{d} de {MESES[m - 1]}"


def ruta_dia(mmdd):
    m, d = int(mmdd[:2]), int(mmdd[3:])
    return f"/santoral/{d}-de-{MESES[m - 1]}/"


def otras(texto):
    """«03-05 San Adrián de Cesarea; 12-10 Santa Eulalia de Mérida» -> [("03-05", "San Adrián de Cesarea"), …]"""
    salida = []
    for parte in (texto or "").split(";"):
        m = re.match(r"\s*(\d{2}-\d{2})\s+(.+?)\s*$", parte)
        if m:
            salida.append((m.group(1), m.group(2)))
    return salida


def variable(e):
    """(días tras la Pascua, descripción) si la fecha es variable."""
    clave = normalizar(e.get("nota") or "")
    return next((v for k, v in VARIABLES.items() if k in clave), None)


def fecha_variable(e, anio):
    v = variable(e)
    return pascua(anio) + dt.timedelta(days=v[0]) if v else None


def cargar():
    """{nombre normalizado: entrada} solo con confianza «alta». Si dos formas coinciden sin tildes (Nuria y Núria),
    se queda la primera. Falla si una entrada «alta» tiene la fecha mal escrita."""
    if not FICHERO.exists():
        return {}
    por_nombre = {}
    for e in json.loads(FICHERO.read_text(encoding="utf-8")):
        if (e.get("confianza") or "").strip().lower() != "alta":
            continue
        if e.get("fecha"):
            dt.date(2024, int(e["fecha"][:2]), int(e["fecha"][3:]))  # valida (2024 es bisiesto: admite el 29 de febrero)
        elif not variable(e):
            raise SystemExit(f"santoral.json: {e['nombre']} no tiene fecha ni una fecha variable conocida")
        e["otras"] = otras(e.get("otras_fechas"))
        por_nombre.setdefault(normalizar(e["nombre"]), e)
    return por_nombre


def por_dia(santos):
    """{«MM-DD»: [(entrada, santo, es_principal)]} con las fechas principales y las «otras fechas»."""
    dias = {}
    for e in santos.values():
        if e.get("fecha"):
            dias.setdefault(e["fecha"], []).append((e, e["santo"], True))
        for mmdd, santo in e["otras"]:
            dias.setdefault(mmdd, []).append((e, santo, False))
    return dict(sorted(dias.items()))
