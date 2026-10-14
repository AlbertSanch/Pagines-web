"""Descarga las fuentes oficiales de los festivos y guarda su texto en festivos/fuentes/.

- BOE: resolución anual de la Dirección General de Trabajo con las fiestas
  nacionales y autonómicas de cada año (la busca en el sumario de la API de
  datos abiertos del BOE si no está en fuentes.json).
- Boletines autonómicos: las fiestas locales de cada municipio, según la lista
  de festivos/fuentes.json. Guarda el texto (pdftotext -layout) y un registro
  con la URL oficial, la fecha de descarga y la huella del documento.

No interpreta nada: los lectores están en procesar.py.
"""
import datetime as dt
import hashlib
import html
import re
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
CONFIG = BASE / "fuentes.json"
UA = {"User-Agent": "Mozilla/5.0 (descarga de datos abiertos de festivos)"}


def bajar(url, accept=None, intentos=3):
    cab = dict(UA)
    if accept:
        cab["Accept"] = accept
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=90) as r:
                return r.read()
        except Exception as e:
            if i == intentos - 1:
                raise
            print(f"   reintento {i + 1} ({e})")
            time.sleep(5 * (i + 1))


def items(nodo):
    if isinstance(nodo, dict):
        if "titulo" in nodo and ("url_xml" in nodo or "url_pdf" in nodo):
            yield nodo
        for v in nodo.values():
            yield from items(v)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from items(v)


def buscar_boe(anio):
    """Recorre los sumarios del BOE de septiembre a diciembre del año anterior."""
    d, fin = dt.date(anio - 1, 9, 1), min(dt.date(anio - 1, 12, 31), dt.date.today())
    while d <= fin:
        if d.weekday() != 6:
            try:
                js = json.loads(bajar(f"https://www.boe.es/datosabiertos/api/boe/sumario/{d:%Y%m%d}", "application/json", 1))
                for it in items(js):
                    t = it["titulo"].lower()
                    if "fiestas laborales" in t and str(anio) in t:
                        return it["identificador"] if "identificador" in it else it["url_xml"].split("id=")[-1]
            except Exception:
                pass
            time.sleep(0.2)
        d += dt.timedelta(days=1)
    return None


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    FUENTES.mkdir(exist_ok=True)
    registro_ruta = FUENTES / "registro.json"
    registro = json.loads(registro_ruta.read_text(encoding="utf-8")) if registro_ruta.exists() else {}
    errores = []

    # BOE: fiestas nacionales y autonómicas
    for anio in cfg["anios"]:
        clave = f"boe_{anio}"
        ident = cfg.get("boe", {}).get(str(anio)) or buscar_boe(anio)
        if not ident:
            print(f"{clave}: aún no publicada")
            continue
        url = f"https://www.boe.es/diario_boe/xml.php?id={ident}"
        try:
            datos = bajar(url)
        except Exception as e:
            errores.append(f"{clave}: {e}")
            continue
        (FUENTES / f"{clave}.xml").write_bytes(datos)
        registro[clave] = {"url": f"https://www.boe.es/buscar/doc.php?id={ident}", "id": ident,
                           "sha1": hashlib.sha1(datos).hexdigest(), "descargado": dt.date.today().isoformat()}
        print(f"{clave}: {ident} ({len(datos)} bytes)")

    # Boletines autonómicos: fiestas locales
    for f in cfg["locales"]:
        clave = f["id"]
        datos, usada = None, None
        for url in [f["descarga"]] + ([f["respaldo"]] if f.get("respaldo") else []):
            try:
                datos, usada = bajar(url), url
                break
            except Exception as e:
                errores.append(f"{clave}: {url}: {e}")
                print(f"{clave}: ERROR {url}: {e}")
        if datos is None:
            continue
        sha = hashlib.sha1(datos).hexdigest()
        if datos[:4] == b"%PDF":
            pdf = FUENTES / f"{clave}.pdf"
            pdf.write_bytes(datos)
            subprocess.run(["pdftotext", "-layout", str(pdf), str(FUENTES / f"{clave}.txt")], check=True)
            pdf.unlink()
        else:  # HTML: se guarda también como texto plano para los lectores
            (FUENTES / f"{clave}.html").write_bytes(datos)
            texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", datos.decode("utf-8", "replace"), flags=re.S | re.I)
            texto = re.sub(r"<br\s*/?>|</(p|tr|li|h\d|div)>", "\n", texto, flags=re.I)
            texto = re.sub(r"<td[^>]*>", "\t", texto, flags=re.I)
            texto = html.unescape(re.sub(r"<[^>]+>", " ", texto))
            (FUENTES / f"{clave}.txt").write_text(re.sub(r"[ \xa0]+", " ", texto), encoding="utf-8")
        cambio = registro.get(clave, {}).get("sha1") not in (None, sha)
        registro[clave] = {"url": f.get("oficial") or f["descarga"], "descargado_de": usada, "sha1": sha,
                           "descargado": dt.date.today().isoformat()}
        print(f"{clave}: {len(datos)} bytes{' (HA CAMBIADO)' if cambio else ''}")

    registro_ruta.write_text(json.dumps(registro, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    if errores:
        print("\nErrores:\n  " + "\n  ".join(errores))
    # Solo falla si no se ha podido bajar nada
    if not any((FUENTES / f"boe_{a}.xml").exists() for a in cfg["anios"]):
        sys.exit("No hay ninguna resolución del BOE")


if __name__ == "__main__":
    main()
