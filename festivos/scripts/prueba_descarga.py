"""Prueba de descarga de los festivos oficiales (no genera la web).

1. Busca en el sumario del BOE (API de datos abiertos) la resolución con la
   relación de fiestas laborales de 2026 (y la de 2027, si ya ha salido).
2. Descarga varios boletines autonómicos con las fiestas locales de cada
   municipio y muestra un extracto del texto para ver si se pueden procesar.
Deja todo en festivos/prueba/ para subirlo como artefacto.
"""
import datetime as dt
import json
import pathlib
import re
import subprocess
import time
import urllib.request

SALIDA = pathlib.Path(__file__).resolve().parent.parent / "prueba"
SALIDA.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (prueba de datos abiertos; contacto: albertsanchezguiu@gmail.com)"}

PDFS = {
    "murcia_2027": "https://www.borm.es/services/anuncio/844400/pdf",
    "rioja_2027": "https://www.laboral-social.com/sites/laboral-social.com/files/Fiestas-locales-Rioja-2027.pdf",
    "baleares_2027": "https://www.laboral-social.com/sites/laboral-social.com/files/calendario-laboral-general-local-baleares-2027.pdf",
    "madrid_2026": "https://originjofjn-boc.comunidad.madrid/boletin/CM_Orden_BOCM/2026/01/08/BOCM-20260108-18.PDF",
    "andalucia_2026_mod": "https://www.juntadeandalucia.es/eboja/2026/79/BOJA26-079-00002-5437-01_00336674.pdf",
    "canarias_2026": "https://iac.edu.es/system/files/documents/2026-01/CAC_fiestas%20locales%20propias%20de%20cada%20municipio%20_boc-a-2025-165-3029.pdf",
    "asturias_2026": "https://miprincipado.asturias.es/documents/d/guest/2025-04744",
}


def bajar(url, accept=None):
    cab = dict(UA)
    if accept:
        cab["Accept"] = accept
    with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=60) as r:
        return r.read()


def items(nodo):
    """Recorre el JSON del sumario y devuelve los diccionarios que tienen título."""
    if isinstance(nodo, dict):
        if "titulo" in nodo and ("url_xml" in nodo or "url_pdf" in nodo):
            yield nodo
        for v in nodo.values():
            yield from items(v)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from items(v)


def buscar_boe(desde, hasta, anio):
    d = desde
    while d <= hasta:
        if d.weekday() != 6:
            try:
                js = json.loads(bajar(f"https://www.boe.es/datosabiertos/api/boe/sumario/{d:%Y%m%d}", "application/json"))
                for it in items(js):
                    t = it["titulo"].lower()
                    if "fiestas laborales" in t and str(anio) in t:
                        return d, it
            except Exception as e:  # día sin boletín u otro error
                if "404" not in str(e):
                    print(f"  {d}: {e}")
            time.sleep(0.3)
        d += dt.timedelta(days=1)
    return None, None


def texto_pdf(nombre, datos):
    ruta = SALIDA / f"{nombre}.pdf"
    ruta.write_bytes(datos)
    subprocess.run(["pdftotext", "-layout", str(ruta), str(ruta.with_suffix(".txt"))], check=False)
    return ruta.with_suffix(".txt").read_text(encoding="utf-8", errors="replace") if ruta.with_suffix(".txt").exists() else ""


def main():
    print("== BOE: resolución de fiestas laborales")
    for anio, desde, hasta in [(2026, dt.date(2025, 10, 1), dt.date(2025, 11, 15)),
                               (2027, dt.date(2026, 9, 15), dt.date.today())]:
        dia, it = buscar_boe(desde, hasta, anio)
        if not it:
            print(f"{anio}: no encontrada entre {desde} y {hasta}")
            continue
        print(f"{anio}: {dia} · {it['titulo']}")
        url = it.get("url_xml")
        url = url["texto"] if isinstance(url, dict) else url
        print("  XML:", url)
        xml = bajar(url).decode("utf-8", "replace")
        (SALIDA / f"boe_{anio}.xml").write_text(xml, encoding="utf-8")
        texto = re.sub(r"<[^>]+>", " ", xml)
        texto = re.sub(r"\s+", " ", texto)
        print(f"  {len(xml)} caracteres. Tablas: {xml.count('<table')}. Extracto:")
        i = texto.lower().find("enero")
        print("  ", texto[max(0, i - 300):i + 1500])

    print("\n== Boletines autonómicos (fiestas locales)")
    for nombre, url in PDFS.items():
        try:
            datos = bajar(url)
        except Exception as e:
            print(f"\n-- {nombre}: ERROR {e}")
            continue
        txt = texto_pdf(nombre, datos)
        lineas = [l for l in txt.splitlines() if l.strip()]
        fechas = re.findall(r"\b\d{1,2} de [a-záéíóú]+\b", txt.lower())
        print(f"\n-- {nombre}: {len(datos)} bytes, {len(lineas)} líneas con texto, {len(fechas)} fechas tipo «15 de mayo»")
        print("\n".join(lineas[:12]))
        print("   [...]")
        mitad = len(lineas) // 2
        print("\n".join(lineas[mitad:mitad + 25]))


if __name__ == "__main__":
    main()
