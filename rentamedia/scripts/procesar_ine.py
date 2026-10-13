"""Convierte los CSV del Atlas de Distribución de Renta de los Hogares en JSON compactos.

Lee rentamedia/datos-ine/ (lo descarga descargar_ine.py) y escribe en rentamedia/data/:
  - territorios.json: nombres de municipios, distritos, provincias y comunidades;
  - <nivel>_<tema>.json con nivel = mun (municipios), dis (distritos de municipios con más de uno),
    sec (secciones censales, solo la renta neta por persona) y agr (España, comunidades, provincias e islas).
Cada fichero tiene la forma {"anios": [...], "indicadores": [...], "datos": {código: [[valor por año] por indicador]}}.
Los datos que el INE no publica (secreto estadístico) se guardan como null: nunca se estiman.

Uso: python rentamedia/scripts/procesar_ine.py
"""
import csv
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "datos-ine"
SALIDA = RAIZ / "data"
TEMAS = ["renta", "fuentes", "gini", "demografia"]
SOLO_SECCIONES = {"renta": ["Renta neta media por persona"]}  # para no guardar 36.000 secciones × todo
COLS_TERRITORIO = {"Municipios", "Distritos", "Secciones", "Total Nacional",
                   "Comunidades y Ciudades Autónomas", "Provincias", "Islas"}


def valor(texto):
    t = (texto or "").strip()
    if t in ("", ".", "..", "-"):
        return None
    try:
        v = float(t.replace(".", "").replace(",", "."))
    except ValueError:
        return None
    return int(v) if v.is_integer() else round(v, 2)


def codigo_nombre(texto):
    m = re.match(r"\s*(\d+)\s+(.*)", texto or "")
    return (m.group(1), m.group(2).strip()) if m else (None, (texto or "").strip())


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        filas = csv.reader(f, delimiter=";")
        cab = next(filas)
        for fila in filas:
            if len(fila) == len(cab):
                yield dict(zip(cab, fila))


def main():
    if not ENTRADA.exists():
        sys.exit("ERROR: falta rentamedia/datos-ine/ (ejecuta antes descargar_ine.py)")
    territorios = {"mun": {}, "dis": {}, "agr": {}}
    # niveles[nivel][tema] = {código: {indicador: {año: valor}}}
    niveles = {n: {t: {} for t in TEMAS} for n in ("mun", "dis", "sec", "agr")}
    anios = set()
    for tema in TEMAS:
        ficheros = sorted(ENTRADA.glob(f"{tema}_*.csv"))
        if not ficheros:
            sys.exit(f"ERROR: no hay CSV de {tema}")
        for ruta in ficheros:
            for fila in leer(ruta):
                otras = [c for c in fila if c not in COLS_TERRITORIO and c not in ("Periodo", "Total")]
                indicador = " | ".join(fila[c].strip() for c in otras if fila[c].strip())
                anio = int(fila["Periodo"])
                anios.add(anio)
                v = valor(fila["Total"])
                if "Municipios" in fila:
                    cm, nm = codigo_nombre(fila["Municipios"])
                    cd, nd = codigo_nombre(fila.get("Distritos"))
                    cs, _ = codigo_nombre(fila.get("Secciones"))
                    if cs:
                        if tema not in SOLO_SECCIONES or indicador not in SOLO_SECCIONES[tema]:
                            continue
                        nivel, cod = "sec", cs
                    elif cd:
                        nivel, cod = "dis", cd
                        territorios["dis"][cd] = nd
                    else:
                        nivel, cod = "mun", cm
                        territorios["mun"][cm] = nm
                else:
                    partes = [fila.get(c, "").strip() for c in
                              ("Comunidades y Ciudades Autónomas", "Provincias", "Islas")]
                    if partes[2]:
                        cod = "isla:" + partes[2]
                    elif partes[1]:
                        cod = "prov:" + partes[1]
                    elif partes[0]:
                        cod = "ccaa:" + partes[0]
                    else:
                        cod = "es"
                    nivel = "agr"
                    territorios["agr"][cod] = next((p for p in reversed(partes) if p), "España")
                niveles[nivel][tema].setdefault(cod, {}).setdefault(indicador, {})[anio] = v
    anios = sorted(anios)
    # Distritos: solo los de municipios con más de un distrito (en los demás, distrito = municipio)
    por_mun = {}
    for cd in territorios["dis"]:
        por_mun.setdefault(cd[:5], []).append(cd)
    sobran = {cd for lista in por_mun.values() if len(lista) == 1 for cd in lista}
    for tema in TEMAS:
        for cd in sobran:
            niveles["dis"][tema].pop(cd, None)
    for cd in sobran:
        territorios["dis"].pop(cd)

    SALIDA.mkdir(exist_ok=True)
    resumen = []
    for nivel, temas in niveles.items():
        for tema, datos in temas.items():
            if not datos:
                continue
            indicadores = sorted({i for d in datos.values() for i in d})
            matriz = {cod: [[d.get(i, {}).get(a) for a in anios] for i in indicadores]
                      for cod, d in sorted(datos.items())}
            ruta = SALIDA / f"{nivel}_{tema}.json"
            ruta.write_text(json.dumps({"anios": anios, "indicadores": indicadores, "datos": matriz},
                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            resumen.append(f"{ruta.name}: {len(matriz)} territorios, {len(indicadores)} indicadores, "
                           f"{ruta.stat().st_size // 1024} KB")
            resumen.extend(f"    - {i}" for i in indicadores)
    (SALIDA / "territorios.json").write_text(json.dumps(territorios, ensure_ascii=False, indent=0,
                                                        sort_keys=True), encoding="utf-8")
    resumen.append(f"Municipios: {len(territorios['mun'])}, distritos (de municipios con varios): "
                   f"{len(territorios['dis'])}, agregados: {len(territorios['agr'])}, años: {anios}")
    (SALIDA / "resumen.txt").write_text("\n".join(resumen) + "\n", encoding="utf-8")
    print("\n".join(resumen))
    if len(territorios["mun"]) < 8000:
        sys.exit(f"ERROR: solo hay {len(territorios['mun'])} municipios")


if __name__ == "__main__":
    main()
