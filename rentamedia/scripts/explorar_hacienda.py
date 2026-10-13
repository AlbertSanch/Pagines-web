"""Exploración temporal de las publicaciones de Hacienda (IRPF por municipios y por código postal).

Guarda en rentamedia/prueba-hacienda/ el HTML de las portadas y de las primeras tablas, y un resumen de los
desplegables (select/option) y enlaces, para decidir cómo extraer los datos. No forma parte de la web.

Uso: python rentamedia/scripts/explorar_hacienda.py
"""
import re
import urllib.parse
import urllib.request
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "prueba-hacienda"
UA = {"User-Agent": "Mozilla/5.0 (rentamedia.es; datos abiertos de la AEAT)"}
RAIZ = "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites"


def bajar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def resumen(nombre, url, html):
    (SALIDA / f"{nombre}.html").write_text(html, encoding="utf-8")
    lineas = [f"URL: {url}", f"Tamaño: {len(html)}"]
    enlaces = re.findall(r'href="([^"#]+)"', html)
    lineas.append(f"\nENLACES ({len(enlaces)}):")
    lineas += [f"  {e}" for e in enlaces[:150]]
    for m in re.finditer(r"<select\b([^>]*)>(.*?)</select>", html, re.S):
        opciones = re.findall(r'<option\b([^>]*)>(.*?)</option>', m.group(2), re.S)
        lineas.append(f"\nSELECT {m.group(1).strip()[:200]} → {len(opciones)} opciones")
        lineas += [f"  {a.strip()[:160]} | {re.sub(r'<[^>]+>', '', t).strip()[:80]}" for a, t in opciones[:12]]
    for m in re.finditer(r"<form\b([^>]*)>", html):
        lineas.append(f"\nFORM {m.group(1)[:300]}")
    scripts = re.findall(r"<script\b[^>]*src=\"([^\"]+)\"", html)
    lineas.append(f"\nSCRIPTS: {scripts}")
    inline = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S)
    lineas.append("\nSCRIPTS EN LÍNEA (inicio):")
    lineas += [f"  ---\n{s.strip()[:1500]}" for s in inline if s.strip()][:6]
    tablas = re.findall(r"<table\b.*?</table>", html, re.S)
    lineas.append(f"\nTABLAS: {len(tablas)}")
    if tablas:
        texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", tablas[0]))
        lineas.append(texto[:3000])
    (SALIDA / f"{nombre}.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return enlaces


def main():
    SALIDA.mkdir(exist_ok=True)
    for pub in ("irpfmunicipios", "irpfCodPostal"):
        home = f"{RAIZ}/{pub}/2024/home.html"
        try:
            enlaces = resumen(f"{pub}_home", home, bajar(home))
        except Exception as e:
            (SALIDA / f"{pub}_error.txt").write_text(str(e))
            continue
        # Seguir los enlaces de la publicación (índice, tablas) y guardar los 8 primeros distintos
        vistos = 0
        for e in enlaces:
            url = urllib.parse.urljoin(home, e)
            if f"/{pub}/2024/" not in url or url == home or not url.endswith(".html"):
                continue
            nombre = f"{pub}_{vistos:02d}_" + re.sub(r"\W+", "_", url.rsplit("/", 1)[-1])[:40]
            try:
                resumen(nombre, url, bajar(url))
            except Exception as ex:
                (SALIDA / f"{nombre}_error.txt").write_text(f"{url}\n{ex}")
            vistos += 1
            if vistos >= 10:
                break


if __name__ == "__main__":
    main()
