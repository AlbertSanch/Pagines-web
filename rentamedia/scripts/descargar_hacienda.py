"""Descarga de la Agencia Tributaria la renta por municipio y por código postal y la guarda en rentamedia/data/.

Hacienda no publica ficheros: publica páginas web con tablas («jrubik»), cuyas direcciones cambian cada año.
Este script entra por la portada de cada publicación y sigue los enlaces por su título:
  - Estadística de los declarantes del IRPF por municipios → Detalle municipios con más de 1.000 hab.
    → Posicionamiento → «Posicionamiento de los municipios mayores de 1.000 habitantes por Renta bruta media»
    (una tabla con todos los municipios: habitantes, declaraciones, renta bruta y disponible, media y mediana).
  - Estadística de los declarantes del IRPF de los mayores municipios por código postal
    → «Renta bruta y Renta disponible inframunicipal» (los códigos postales de las ciudades grandes, con su nombre).
Usa el último año publicado y el anterior (para la variación). Escribe data/hacienda.json.
Si no encuentra las tablas o salen muy pocos municipios, falla sin tocar los datos que ya había.

Uso: python rentamedia/scripts/descargar_hacienda.py
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "data" / "hacienda.json"
RAIZ = "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites"
UA = {"User-Agent": "Mozilla/5.0 (rentamedia.es; datos abiertos de la Agencia Tributaria)"}
MIN_MUNICIPIOS = 2500
MIN_CODIGOS = 500


def bajar(url):
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            print(f"{url}: {e} (intento {intento + 1})", file=sys.stderr)
        except Exception as e:
            print(f"{url}: {e} (intento {intento + 1})", file=sys.stderr)
        time.sleep(10 * (intento + 1))
    sys.exit(f"ERROR: no se ha podido descargar {url}")


def enlace(url_pagina, pagina, texto):
    """URL absoluta del enlace cuyo texto empieza por `texto` (sin distinguir mayúsculas)."""
    for href, t in re.findall(r'<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', pagina, re.S):
        if re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip().lower().startswith(texto.lower()):
            return urllib.parse.urljoin(url_pagina, href)
    return None


def portada(publicacion, anio):
    """Devuelve (url, html) de la portada real de la publicación de ese año, o None si no existe."""
    url = f"{RAIZ}/{publicacion}/{anio}/home.html"
    try:
        pagina = bajar(url)
    except urllib.error.HTTPError:
        return None
    # home.html a veces solo enlaza a la portada con nombre aleatorio (home<hash>.html)
    real = re.search(r'href="(home[0-9a-f]{20,}\.html)"', pagina)
    if real:
        url = urllib.parse.urljoin(url, real.group(1))
        pagina = bajar(url)
    return url, pagina


def seguir(publicacion, anio, pasos):
    p = portada(publicacion, anio)
    if not p:
        return None
    url, pagina = p
    for texto in pasos:
        siguiente = enlace(url, pagina, texto)
        if not siguiente:
            sys.exit(f"ERROR: {publicacion} {anio}: no encuentro el enlace «{texto}» en {url}")
        url, pagina = siguiente, bajar(siguiente)
    return pagina


def filas(pagina):
    tabla = re.search(r"<table\b.*?</table>", pagina, re.S)
    if not tabla:
        sys.exit("ERROR: la página no tiene tabla")
    for f in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tabla.group(0), re.S):
        yield [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
               for c in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", f, re.S)]


def numero(t):
    t = (t or "").strip()
    if not t or not re.search(r"\d", t):
        return None
    try:
        return int(t.replace(".", "").replace(",", ""))
    except ValueError:
        return None


def municipios(anio):
    pagina = seguir("irpfmunicipios", anio, ["Detalle municipios con más de 1.000",
                                             "Posicionamiento municipios con más de 1.000",
                                             "Posicionamiento de los municipios mayores de 1.000 habitantes por Renta bruta media"])
    if pagina is None:
        return None
    cab, datos = None, {}
    for c in filas(pagina):
        if cab is None:
            cab = [x.upper() for x in c]
            continue
        m = re.match(r"^(.*)-(\d{5})$", c[0])
        if not m or len(c) != len(cab):
            continue
        fila = dict(zip(cab, c))

        def v(nombre):
            return numero(next((fila[k] for k in fila if k.startswith(nombre)), None))
        datos[m.group(2)] = {"nombre": m.group(1).strip(), "habitantes": v("NUMERO HABITANTES"), "declaraciones": v("NUMERO DECLARACIONES"),
                             "bruta_media": v("RENTA BRUTA MEDIA"), "bruta_mediana": v("RENTA BRUTA MEDIANA"),
                             "disponible_media": v("RENTA DISPONIBLE MEDIA"), "disponible_mediana": v("RENTA DISPONIBLE MEDIANA"),
                             "puesto": v("POSICIONAMIENTO RENTA BRUTA MEDIA NIVEL NACIONAL")}
    return datos


def codigos_postales(anio):
    pagina = seguir("irpfCodPostal", anio, ["Renta bruta y Renta disponible inframunicipal"])
    if pagina is None:
        return None
    ciudades, actual = {}, None
    for c in filas(pagina):
        if len(c) < 4:
            continue
        m = re.match(r"^(.*)-(\d{5})$", c[0])
        if m:
            actual = m.group(2)
            ciudades[actual] = {"nombre": m.group(1).strip(), "declaraciones": numero(c[1]), "bruta_media": numero(c[2]),
                                "disponible_media": numero(c[3]), "codigos": {}}
            continue
        m = re.match(r"^(\d{5})\s*-\s*(.*)$", c[0])
        if m and actual:
            nombre = ", ".join(p.strip() for p in re.split(r"\s*-\s+|\s+-\s*", m.group(2)) if p.strip())
            ciudades[actual]["codigos"][m.group(1)] = {"nombre": nombre, "declaraciones": numero(c[1]),
                                                       "bruta_media": numero(c[2]), "disponible_media": numero(c[3])}
    return ciudades


def ultimo_anio(publicacion):
    for anio in range(date.today().year, date.today().year - 4, -1):
        if portada(publicacion, anio):
            return anio
    sys.exit(f"ERROR: no encuentro ningún año publicado de {publicacion}")


def main():
    am = ultimo_anio("irpfmunicipios")
    mun, mun_ant = municipios(am), municipios(am - 1) or {}
    if not mun or len(mun) < MIN_MUNICIPIOS:
        sys.exit(f"ERROR: solo {len(mun or {})} municipios de Hacienda en {am}")
    acp = ultimo_anio("irpfCodPostal")
    cp, cp_ant = codigos_postales(acp), codigos_postales(acp - 1) or {}
    n_cp = sum(len(x["codigos"]) for x in (cp or {}).values())
    if n_cp < MIN_CODIGOS:
        sys.exit(f"ERROR: solo {n_cp} códigos postales de Hacienda en {acp}")
    for cod, d in mun.items():
        d["bruta_media_ant"] = (mun_ant.get(cod) or {}).get("bruta_media")
    for cod, ciudad in cp.items():
        ant = cp_ant.get(cod, {}).get("codigos", {})
        for c, d in ciudad["codigos"].items():
            d["bruta_media_ant"] = (ant.get(c) or {}).get("bruta_media")
    SALIDA.write_text(json.dumps({"anio_municipios": am, "anio_codigos": acp, "municipios": mun, "ciudades": cp},
                                 ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    print(f"Hacienda: {len(mun)} municipios ({am}), {len(cp)} ciudades y {n_cp} códigos postales ({acp}).")


if __name__ == "__main__":
    main()
