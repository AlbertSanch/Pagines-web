"""Descarga las normas oficiales del calendario escolar de cada comunidad y guarda su texto en
festivos/fuentes/escolar/ (una por territorio, según festivos/escolar.json).

Como descargar_fuentes.py, no interpreta nada: guarda el texto (pdftotext -layout o el HTML
pasado a texto) y un registro con la URL oficial, la fecha de descarga y la huella del documento.
Las fechas se leen de esos textos y se pasan a festivos/data/escolar.json citando la fuente.

Uso: python festivos/scripts/descargar_escolar.py
"""
import datetime as dt
import hashlib
import html
import json
import re
import ssl
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from descargar_fuentes import BASE, UA

DESTINO = BASE / "fuentes" / "escolar"
CONFIG = BASE / "escolar.json"


# Algunos servidores oficiales (p. ej. el DOGC) solo aceptan cifrados antiguos que Python rechaza por defecto
SSL_ANTIGUO = ssl.create_default_context()
SSL_ANTIGUO.set_ciphers("DEFAULT:@SECLEVEL=1")


def bajar(url, intentos=2):
    for i in range(intentos):
        for contexto in (None, SSL_ANTIGUO):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120, context=contexto) as r:
                    return r.read()
            except Exception as e:
                ultimo = e
                if "SSL" not in str(e):
                    break
    raise ultimo


def a_texto(datos):
    bruto = datos.decode("utf-8", "replace")
    if bruto.count("�") > 5:
        bruto = datos.decode("latin-1")
    texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", bruto, flags=re.S | re.I)
    texto = re.sub(r"<br\s*/?>|</(p|tr|li|h\d|div)>", "\n", texto, flags=re.I)
    texto = re.sub(r"<td[^>]*>", "\t", texto, flags=re.I)
    texto = html.unescape(re.sub(r"<[^>]+>", " ", texto))
    return re.sub(r"[ \xa0]+", " ", texto)


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    DESTINO.mkdir(parents=True, exist_ok=True)
    registro_ruta = DESTINO / "registro.json"
    registro = json.loads(registro_ruta.read_text(encoding="utf-8")) if registro_ruta.exists() else {}
    errores = []

    def una(f):
        ultimo = None
        for url in [f["descarga"]] + f.get("respaldo", []):
            try:
                return f, bajar(url), url, None
            except Exception as e:
                ultimo = f"{url}: {e}"
        return f, None, None, ultimo

    with ThreadPoolExecutor(max_workers=6) as pool:
        for f, datos, usada, error in pool.map(una, cfg["fuentes"]):
            clave = f["id"]
            if datos is None:
                errores.append(f"{clave}: {error}")
                print(f"{clave}: ERROR {error}", flush=True)
                continue
            if datos[:4] == b"%PDF":
                pdf = DESTINO / f"{clave}.pdf"
                pdf.write_bytes(datos)
                subprocess.run(["pdftotext", "-layout", str(pdf), str(DESTINO / f"{clave}.txt")], check=True)
                pdf.unlink()
            else:
                (DESTINO / f"{clave}.txt").write_text(a_texto(datos), encoding="utf-8")
            sha = hashlib.sha1(datos).hexdigest()
            cambio = registro.get(clave, {}).get("sha1") not in (None, sha)
            registro[clave] = {"url": f.get("oficial") or f["descarga"], "descargado_de": usada, "sha1": sha,
                               "descargado": dt.date.today().isoformat()}
            print(f"{clave}: {len(datos)} bytes desde {usada}{' (HA CAMBIADO)' if cambio else ''}", flush=True)

    registro_ruta.write_text(json.dumps(registro, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    if errores:
        print("\nErrores:\n  " + "\n  ".join(errores))


if __name__ == "__main__":
    main()
