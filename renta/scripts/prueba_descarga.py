"""Prueba de descarga de los datos de renta (INE y Agencia Tributaria).

No genera ninguna web: solo comprueba qué se puede descargar y guarda muestras pequeñas
en renta/prueba/ para revisar columnas, niveles territoriales y años.

Uso: python renta/scripts/prueba_descarga.py
"""

import csv
import io
import json
import re
import urllib.request
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "prueba"
UA = {"User-Agent": "Mozilla/5.0 (prueba de datos abiertos)"}
ADRH = 353  # operación del INE: Atlas de Distribución de Renta de los Hogares


def bajar(url, limite=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read(limite) if limite else r.read()


def guardar(nombre, texto):
    (SALIDA / nombre).write_text(texto, encoding="utf-8")
    print(f"  guardado {nombre} ({len(texto)} caracteres)")


def intento(titulo, funcion):
    print(f"\n=== {titulo}")
    try:
        funcion()
    except Exception as e:  # la prueba sigue aunque una fuente falle
        print(f"  ERROR: {type(e).__name__}: {e}")
        guardar(re.sub(r"\W+", "_", titulo.lower())[:40] + "_error.txt", f"{type(e).__name__}: {e}\n")


def tablas_ine():
    tablas = json.loads(bajar(f"https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{ADRH}"))
    lineas = [f"{t['Id']}\t{t['Nombre']}" for t in tablas]
    guardar("ine_tablas.tsv", "\n".join(lineas) + "\n")
    print(f"  {len(tablas)} tablas")
    return tablas


def muestra_tabla(id_tabla, prefijo):
    texto = bajar(f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{id_tabla}.csv").decode("utf-8-sig", "replace")
    filas = list(csv.reader(io.StringIO(texto), delimiter=";"))
    cab, datos = filas[0], filas[1:]
    resumen = [f"Tabla {id_tabla}: {len(datos)} filas", "Columnas: " + " | ".join(cab)]
    for i, col in enumerate(cab):
        valores = sorted({f[i] for f in datos if len(f) > i})
        if len(valores) <= 40:
            resumen.append(f"\n[{col}] {len(valores)} valores: " + " | ".join(valores))
        else:
            resumen.append(f"\n[{col}] {len(valores)} valores, ejemplos: " + " | ".join(valores[:15]))
    # niveles territoriales: los códigos de municipio tienen 5 cifras, distrito 7 y sección 10
    for i, col in enumerate(cab):
        codigos = [re.match(r"\d+", f[i] or "") for f in datos if len(f) > i]
        largos = {}
        for m in codigos:
            if m:
                largos[len(m.group())] = largos.get(len(m.group()), 0) + 1
        if largos:
            resumen.append(f"\nLongitud de los códigos en [{col}]: {largos}")
    guardar(f"{prefijo}_resumen.txt", "\n".join(resumen) + "\n")
    guardar(f"{prefijo}_primeras.csv", "\n".join(texto.splitlines()[:60]) + "\n")
    # unas filas de Getafe (28065) y de Madrid (28079) para ver cómo vienen
    getafe = [l for l in texto.splitlines() if l.startswith(("28065", "28079")) or ";28065" in l or "Getafe" in l]
    guardar(f"{prefijo}_getafe_madrid.csv", "\n".join(getafe[:80]) + "\n")


def ine():
    tablas = tablas_ine()
    hechas = set()
    # una tabla de cada tipo para la provincia de Madrid
    for t in tablas:
        nombre = t["Nombre"].lower()
        if "madrid" not in nombre:
            continue
        tipo = re.sub(r"\W+", "_", nombre.split(":")[0].split(".")[0])[:30]
        if tipo in hechas:
            continue
        hechas.add(tipo)
        intento(f"Tabla INE {t['Id']} {t['Nombre']}", lambda t=t, tipo=tipo: muestra_tabla(t["Id"], f"ine_{t['Id']}_{tipo}"))


def arcgis():
    base = "https://www.ine.es/servergis/rest/services/Hosted/ADRH_2023_Renta_media_por_persona/FeatureServer"
    guardar("arcgis_servicio.json", bajar(f"{base}?f=json").decode("utf-8", "replace")[:20000])
    q = f"{base}/3/query?where=1%3D1&outFields=*&returnGeometry=false&resultRecordCount=3&f=json"
    guardar("arcgis_secciones_muestra.json", bajar(q).decode("utf-8", "replace")[:20000])


def aeat():
    paginas = {
        "aeat_municipios_2023": "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2023/jrubik3442cca89c83f10254b1df84b6723ef2856884.html",
        "aeat_cp_2023": "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfCodPostal/2023/jrubik44358fe15d06f0315790c5013da035b787a00310.html",
        "aeat_datosabiertos_cp": "https://sede.agenciatributaria.gob.es/Sede/datosabiertos/catalogo/hacienda/Estadistica_del_IRPF_por_codigo_postal.shtml",
        "aeat_datosabiertos": "https://sede.agenciatributaria.gob.es/Sede/datosabiertos/catalogo.shtml",
    }
    for nombre, url in paginas.items():
        def una(nombre=nombre, url=url):
            html = bajar(url).decode("utf-8", "replace")
            enlaces = sorted(set(re.findall(r'href="([^"]+)"', html)))
            utiles = [e for e in enlaces if re.search(r"\.(csv|xlsx?|zip|json|px)\b|irpf|municip|postal|descarg", e, re.I)]
            texto = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S))
            texto = re.sub(r"\s+", " ", texto)
            guardar(f"{nombre}.txt", f"URL: {url}\n\nENLACES ÚTILES:\n" + "\n".join(utiles[:200])
                    + f"\n\nTEXTO (inicio):\n{texto[:6000]}\n")
        intento(nombre, una)


def ronda2():
    # Tablas de renta media: la primera (¿nacional?) y una de provincia
    for t in (30656, 30833, 53689):
        intento(f"Tabla INE {t}", lambda t=t: muestra_tabla(t, f"ine_{t}"))
    # Capa de municipios del servicio de mapas y años disponibles
    def capas():
        base = "https://www.ine.es/servergis/rest/services/Hosted/ADRH_2023_Renta_media_por_persona/FeatureServer/1/query"
        n = bajar(f"{base}?where=1%3D1&returnCountOnly=true&f=json").decode()
        m = bajar(f"{base}?where=cumun%3D%2728065%27&outFields=*&returnGeometry=false&f=json").decode("utf-8", "replace")
        guardar("arcgis_municipios.txt", f"Total municipios: {n}\n\nGetafe:\n{m[:6000]}\n")
        anios = []
        for a in range(2015, 2026):
            try:
                bajar(f"https://www.ine.es/servergis/rest/services/Hosted/ADRH_{a}_Renta_media_por_persona/FeatureServer?f=json", 2000)
                anios.append(f"{a}: sí")
            except Exception as e:
                anios.append(f"{a}: no ({e})")
        guardar("arcgis_anios.txt", "\n".join(anios) + "\n")
    intento("ArcGIS municipios y años", capas)
    # Portadas de Hacienda de 2024 y 2025: qué tablas y descargas ofrecen
    raiz = "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites"
    for nombre, url in {
        "aeat_mun_2024_home": f"{raiz}/irpfmunicipios/2024/home.html",
        "aeat_mun_2023_home": f"{raiz}/irpfmunicipios/2023/home.html",
        "aeat_cp_2024_home": f"{raiz}/irpfCodPostal/2024/home.html",
        "aeat_mun_portada": "https://sede.agenciatributaria.gob.es/Sede/datosabiertos/catalogo/hacienda/Estadistica_de_los_declarantes_del_IRPF_por_municipios.shtml",
    }.items():
        def una(nombre=nombre, url=url):
            html = bajar(url).decode("utf-8", "replace")
            enlaces = sorted(set(re.findall(r'(?:href|src|action)="([^"]+)"', html)))
            texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)))
            guardar(f"{nombre}.txt", f"URL: {url}\n\nENLACES:\n" + "\n".join(enlaces[:300]) + f"\n\nTEXTO:\n{texto[:5000]}\n")
        intento(nombre, una)


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    ronda2()
