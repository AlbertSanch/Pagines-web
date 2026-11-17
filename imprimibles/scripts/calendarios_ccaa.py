"""Prepara los calendarios por comunidad autónoma de imprimibles.es.

Lee los festivos nacionales y autonómicos de festivosde.es (festivos/data/festivos_AÑO.json, que salen de la
resolución anual de fiestas laborales del BOE) y escribe:
  - imprimibles/content/datos/festivos-AÑO.json: festivos de cada comunidad, con nombres cortos para el calendario;
  - imprimibles/src/pdf/calendario-AÑO*.xlsx: el calendario en Excel (nacional y uno por comunidad).

Uso: python imprimibles/scripts/calendarios_ccaa.py [AÑO]   (necesita openpyxl)
"""
import calendar
import datetime as dt
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "festivos" / "scripts"))
from comun import COMUNIDADES  # noqa: E402

ANIO = int(sys.argv[1]) if len(sys.argv) > 1 else 2027

# Nombres más cortos para que quepan en el calendario
CORTOS = {
    "Epifanía del Señor": "Reyes",
    "Natividad del Señor": "Navidad",
    "Día de la Constitución Española": "Día de la Constitución",
    "Lunes siguiente a asunción de la Virgen": "Lunes tras la Asunción",
    "Aniversario 1er Gobierno Euskadi": "Aniversario 1.er Gobierno vasco",
    "Sustitución 15 de agosto": "Traslado del 15 de agosto",
    "Eidul Adha-Fiesta Sacrificio": "Fiesta del Sacrificio",
    "Fiesta Sacrificio-Aid Al Adha": "Fiesta del Sacrificio",
    "Fiesta del Eid Fitr": "Fiesta del Eid al-Fitr",
    "San Jorge/Día de Aragón": "San Jorge, Día de Aragón",
}

# Nombre con artículo para las frases («el calendario de la Comunidad de Madrid»)
CON_ARTICULO = {
    "madrid": "la Comunidad de Madrid", "murcia": "la Región de Murcia", "valenciana": "la Comunitat Valenciana",
    "baleares": "las Illes Balears", "la-rioja": "La Rioja", "pais-vasco": "el País Vasco",
}

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
         "Diciembre"]
DIAS = ["L", "M", "X", "J", "V", "S", "D"]


def leer():
    datos = json.loads((RAIZ / "festivos" / "data" / f"festivos_{ANIO}.json").read_text(encoding="utf-8"))
    na = datos["nacionales_autonomicos"]
    comunes = None  # festivos que son fiesta en todas las comunidades
    for lista in na.values():
        fechas = {x["f"] for x in lista}
        comunes = fechas if comunes is None else comunes & fechas
    nacional = [x for x in na["madrid"] if x["f"] in comunes]
    salida = {
        "anio": ANIO, "boe": datos["boe"],
        "nacional": [[x["f"][5:], CORTOS.get(x["n"], x["n"])] for x in sorted(nacional, key=lambda x: x["f"])],
        "comunidades": {},
    }
    for clave, (nombre, _) in COMUNIDADES.items():
        lista = sorted(na[clave], key=lambda x: x["f"])
        salida["comunidades"][clave] = {
            "nombre": nombre,
            "con_articulo": CON_ARTICULO.get(clave, nombre),
            "festivos": [[x["f"][5:], CORTOS.get(x["n"], x["n"]), "comun" if x["f"] in comunes else "propio"]
                         for x in lista],
            "notas": datos.get("notas", {}).get(clave, []),
        }
    return salida


def excel(festivos, titulo, destino):
    """Libro con una hoja del año completo y una hoja por mes, con los festivos en rojo."""
    fest = {f: n for f, n, *_ in festivos}
    rojo = Font(color="C0392B", bold=True)
    gris = PatternFill("solid", fgColor="F3F1EA")
    cabecera = PatternFill("solid", fgColor="2B2B33")
    fino = Side(style="thin", color="999999")
    borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    libro = Workbook()

    # Hoja anual: tres meses por fila
    h = libro.active
    h.title = str(ANIO)
    h["A1"] = titulo
    h["A1"].font = Font(size=16, bold=True)
    for m in range(12):
        c0 = 1 + (m % 3) * 8
        f0 = 3 + (m // 3) * 9
        h.cell(f0, c0, MESES[m]).font = Font(bold=True, size=12)
        for j, d in enumerate(DIAS):
            celda = h.cell(f0 + 1, c0 + j, d)
            celda.font = Font(bold=True, color="C0392B" if j == 6 else "666666")
            celda.alignment = Alignment(horizontal="center")
        p0 = calendar.monthrange(ANIO, m + 1)[0]
        for d in range(1, calendar.monthrange(ANIO, m + 1)[1] + 1):
            pos = p0 + d - 1
            celda = h.cell(f0 + 2 + pos // 7, c0 + pos % 7, d)
            celda.alignment = Alignment(horizontal="center")
            if pos % 7 == 6 or f"{m + 1:02d}-{d:02d}" in fest:
                celda.font = rojo
            if f"{m + 1:02d}-{d:02d}" in fest:
                celda.fill = PatternFill("solid", fgColor="FBE3DF")
    for c in range(1, 25):
        h.column_dimensions[get_column_letter(c)].width = 4.2
    fila = 3 + 4 * 9
    h.cell(fila, 1, f"Festivos {ANIO}").font = Font(bold=True, size=12)
    for i, (f, n, *_) in enumerate(festivos):
        fecha = dt.date(ANIO, int(f[:2]), int(f[3:]))
        h.cell(fila + 1 + i, 1, fecha).number_format = "DD/MM/YYYY"
        h.cell(fila + 1 + i, 4, n)
    h.column_dimensions["A"].width = 11

    # Una hoja por mes con casillas para apuntar
    for m in range(12):
        hm = libro.create_sheet(MESES[m])
        hm["A1"] = f"{MESES[m]} {ANIO}"
        hm["A1"].font = Font(size=16, bold=True)
        for j, nombre in enumerate(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]):
            celda = hm.cell(3, 1 + j, nombre)
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="C0392B") if j == 6 else cabecera
            celda.alignment = Alignment(horizontal="center")
            hm.column_dimensions[get_column_letter(1 + j)].width = 18
        p0, nd = calendar.monthrange(ANIO, m + 1)
        filas = (p0 + nd + 6) // 7
        for i in range(filas * 7):
            d = i - p0 + 1
            celda = hm.cell(4 + i // 7, 1 + i % 7)
            celda.border = borde
            celda.alignment = Alignment(vertical="top", wrap_text=True)
            if 1 <= d <= nd:
                clave = f"{m + 1:02d}-{d:02d}"
                celda.value = f"{d}\n{fest[clave]}" if clave in fest else d
                if i % 7 == 6 or clave in fest:
                    celda.font = rojo
            else:
                celda.fill = gris
        for r in range(4, 4 + filas):
            hm.row_dimensions[r].height = 62
        hm.page_setup.orientation = "landscape"
        hm.page_setup.fitToWidth = 1
        hm.sheet_properties.pageSetUpPr.fitToPage = True
    h.page_setup.fitToWidth = 1
    h.sheet_properties.pageSetUpPr.fitToPage = True
    libro.save(destino)


def main():
    datos = leer()
    (RAIZ / "imprimibles" / "content" / "datos").mkdir(exist_ok=True)
    (RAIZ / "imprimibles" / "content" / "datos" / f"festivos-{ANIO}.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    pdf = RAIZ / "imprimibles" / "src" / "pdf"
    excel(datos["nacional"], f"Calendario {ANIO} · festivos nacionales · imprimibles.es", pdf / f"calendario-{ANIO}.xlsx")
    for clave, c in datos["comunidades"].items():
        excel(c["festivos"], f"Calendario {ANIO} · {c['nombre']} · imprimibles.es", pdf / f"calendario-{ANIO}-{clave}.xlsx")
    print(f"{len(datos['comunidades'])} comunidades; festivos comunes: {len(datos['nacional'])}")


if __name__ == "__main__":
    main()
