"""Genera la web estática de rentamedia.es a partir de rentamedia/data/ (lo crea procesar_ine.py).

Páginas:
  /                                    portada con buscador y los rankings principales
  /municipio/<slug>/                   una por municipio con datos: renta, evolución, ingresos, desigualdad…
  /municipios-mas-ricos-de-espana/     ranking de España (municipios de más de 2.000 habitantes, como el INE)
  /municipios-mas-pobres-de-espana/
  /provincia/<slug>/ y /comunidad/<slug>/   ranking de sus municipios
  /barrios-mas-ricos-de-madrid/ y /barrios-mas-ricos-de-barcelona/   renta por distrito
  /comparar-renta/                     calculadora «¿Estás por encima de la media de tu municipio?»
  /sobre-los-datos/, /aviso-legal/, /privacidad/

Todos los datos son del Atlas de Distribución de Renta de los Hogares del INE. Lo que el INE no publica
(secreto estadístico) se dice tal cual: nunca se estima ni se inventa.

Uso: python rentamedia/scripts/generar_web.py
"""
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
WEB = RAIZ / "web"
PLANTILLA = RAIZ / "plantilla"
DOMINIO = "https://rentamedia.es"
SITIO = "Renta Media"
VERSION = "3"
ADSENSE = "ca-pub-8810566450749484"  # la misma cuenta que Ahorrómetro y ¿Cuántos se llaman?
REGIONES_CONSENTIMIENTO = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT",
                           "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "GB", "CH"]
CABECERA_ANUNCIOS = (
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
    'gtag("consent","default",{ad_storage:"denied",ad_user_data:"denied",ad_personalization:"denied",analytics_storage:"denied",'
    f'wait_for_update:500,region:{json.dumps(REGIONES_CONSENTIMIENTO, separators=(",", ":"))}}});'
    'gtag("consent","default",{ad_storage:"granted",ad_user_data:"granted",ad_personalization:"granted",analytics_storage:"granted"});</script>\n'
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>')
CONFIGURAR_COOKIES = ('<a href="#" onclick="window.googlefc=window.googlefc||{};googlefc.callbackQueue=googlefc.callbackQueue||[];'
                      'googlefc.callbackQueue.push(function(){googlefc.showRevocationMessage()});return false">Configurar cookies</a>')
TITULAR = {"nombre": "Albert Sanchez Guiu", "nif": "48167483D", "domicilio": "La Roca del Vallès (Barcelona), España",
           "email": "contacto.ahorrometro@gmail.com"}
MIN_HAB_RANKING = 2000   # como el INE en sus notas de prensa: los pueblos muy pequeños bailan mucho de un año a otro
MIN_HAB_CIUDAD = 50000   # «ciudades más ricas de España»
MIN_PAGINAS = 7000       # si salen menos páginas de municipio, algo ha ido mal y no se publica

# Indicadores del INE (nombres exactos de sus tablas)
PERSONA = "Renta neta media por persona"
HOGAR = "Renta neta media por hogar"
BRUTA_PERSONA = "Renta bruta media por persona"
MEDIANA_UC = "Mediana de la renta por unidad de consumo"
MEDIA_UC = "Media de la renta por unidad de consumo"
POBLACION = "Población"
FUENTES = [("Fuente de ingreso: salario", "Salarios"), ("Fuente de ingreso: pensiones", "Pensiones"),
           ("Fuente de ingreso: prestaciones por desempleo", "Prestaciones por desempleo"),
           ("Fuente de ingreso: otras prestaciones", "Otras prestaciones"), ("Fuente de ingreso: otros ingresos", "Otros ingresos")]

# código INE de provincia: (nombre en las tablas del INE, nombre para mostrar, comunidad en las tablas del INE)
PROVINCIAS = {
    "01": ("Araba/Álava", "Álava", "País Vasco"), "02": ("Albacete", "Albacete", "Castilla - La Mancha"),
    "03": ("Alicante/Alacant", "Alicante", "Comunitat Valenciana"), "04": ("Almería", "Almería", "Andalucía"),
    "05": ("Ávila", "Ávila", "Castilla y León"), "06": ("Badajoz", "Badajoz", "Extremadura"),
    "07": ("Balears, Illes", "Illes Balears", "Balears, Illes"), "08": ("Barcelona", "Barcelona", "Cataluña"),
    "09": ("Burgos", "Burgos", "Castilla y León"), "10": ("Cáceres", "Cáceres", "Extremadura"),
    "11": ("Cádiz", "Cádiz", "Andalucía"), "12": ("Castellón/Castelló", "Castellón", "Comunitat Valenciana"),
    "13": ("Ciudad Real", "Ciudad Real", "Castilla - La Mancha"), "14": ("Córdoba", "Córdoba", "Andalucía"),
    "15": ("Coruña, A", "A Coruña", "Galicia"), "16": ("Cuenca", "Cuenca", "Castilla - La Mancha"),
    "17": ("Girona", "Girona", "Cataluña"), "18": ("Granada", "Granada", "Andalucía"),
    "19": ("Guadalajara", "Guadalajara", "Castilla - La Mancha"), "20": ("Gipuzkoa", "Gipuzkoa", "País Vasco"),
    "21": ("Huelva", "Huelva", "Andalucía"), "22": ("Huesca", "Huesca", "Aragón"),
    "23": ("Jaén", "Jaén", "Andalucía"), "24": ("León", "León", "Castilla y León"),
    "25": ("Lleida", "Lleida", "Cataluña"), "26": ("Rioja, La", "La Rioja", "Rioja, La"),
    "27": ("Lugo", "Lugo", "Galicia"), "28": ("Madrid", "Madrid", "Madrid, Comunidad de"),
    "29": ("Málaga", "Málaga", "Andalucía"), "30": ("Murcia", "Murcia", "Murcia, Región de"),
    "31": ("Navarra", "Navarra", "Navarra, Comunidad Foral de"), "32": ("Ourense", "Ourense", "Galicia"),
    "33": ("Asturias", "Asturias", "Asturias, Principado de"), "34": ("Palencia", "Palencia", "Castilla y León"),
    "35": ("Palmas, Las", "Las Palmas", "Canarias"), "36": ("Pontevedra", "Pontevedra", "Galicia"),
    "37": ("Salamanca", "Salamanca", "Castilla y León"), "38": ("Santa Cruz de Tenerife", "Santa Cruz de Tenerife", "Canarias"),
    "39": ("Cantabria", "Cantabria", "Cantabria"), "40": ("Segovia", "Segovia", "Castilla y León"),
    "41": ("Sevilla", "Sevilla", "Andalucía"), "42": ("Soria", "Soria", "Castilla y León"),
    "43": ("Tarragona", "Tarragona", "Cataluña"), "44": ("Teruel", "Teruel", "Aragón"),
    "45": ("Toledo", "Toledo", "Castilla - La Mancha"), "46": ("Valencia/València", "Valencia", "Comunitat Valenciana"),
    "47": ("Valladolid", "Valladolid", "Castilla y León"), "48": ("Bizkaia", "Bizkaia", "País Vasco"),
    "49": ("Zamora", "Zamora", "Castilla y León"), "50": ("Zaragoza", "Zaragoza", "Aragón"),
    "51": ("Ceuta", "Ceuta", "Ceuta"), "52": ("Melilla", "Melilla", "Melilla"),
}
COMUNIDADES = {
    "Andalucía": "Andalucía", "Aragón": "Aragón", "Asturias, Principado de": "Asturias", "Balears, Illes": "Illes Balears",
    "Canarias": "Canarias", "Cantabria": "Cantabria", "Castilla - La Mancha": "Castilla-La Mancha",
    "Castilla y León": "Castilla y León", "Cataluña": "Cataluña", "Ceuta": "Ceuta", "Comunitat Valenciana": "Comunitat Valenciana",
    "Extremadura": "Extremadura", "Galicia": "Galicia", "Madrid, Comunidad de": "Comunidad de Madrid", "Melilla": "Melilla",
    "Murcia, Región de": "Región de Murcia", "Navarra, Comunidad Foral de": "Navarra", "País Vasco": "País Vasco",
    "Rioja, La": "La Rioja",
}
# Los distritos censales del INE de Madrid y Barcelona coinciden con los distritos municipales
NOMBRES_DISTRITOS = {
    "28079": ["Centro", "Arganzuela", "Retiro", "Salamanca", "Chamartín", "Tetuán", "Chamberí", "Fuencarral-El Pardo",
              "Moncloa-Aravaca", "Latina", "Carabanchel", "Usera", "Puente de Vallecas", "Moratalaz", "Ciudad Lineal",
              "Hortaleza", "Villaverde", "Villa de Vallecas", "Vicálvaro", "San Blas-Canillejas", "Barajas"],
    "08019": ["Ciutat Vella", "Eixample", "Sants-Montjuïc", "Les Corts", "Sarrià-Sant Gervasi", "Gràcia",
              "Horta-Guinardó", "Nou Barris", "Sant Andreu", "Sant Martí"],
}


# ---------------------------------------------------------------- utilidades

def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes(t).lower().replace("'", " ")).strip("-")


def clave(t):
    """Texto normalizado para el buscador: minúsculas, sin tildes ni signos."""
    return re.sub(r"[^a-z0-9ñ ]+", " ", sin_tildes(t.lower().replace("ñ", "\0")).replace("\0", "ñ")).strip()


ARTICULO = re.compile(r"^(.*), (el|la|los|las|l'|lo|les|els|o|a|os|as|es|sa|ses|s')$", re.I)


def bonito(nombre_ine):
    """«Rozas de Madrid, Las» → «Las Rozas de Madrid»; «Orxa, l'/Lorcha» → «L'Orxa / Lorcha»."""
    partes = []
    for p in nombre_ine.split("/"):
        p = p.strip()
        m = ARTICULO.match(p)
        if m:
            art = m.group(2)
            p = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
        partes.append(p[:1].upper() + p[1:])
    return " / ".join(partes)


def n(x):
    return f"{round(x):,}".replace(",", ".")


def euros(x):
    return f"{n(x)} €"


def dec(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def pct(x, d=1):
    return f"{dec(x, d)} %"


def indicador(valor, referencia, texto_ref="la media de España"):
    """Etiqueta de color: ▲ por encima / ▼ por debajo de la referencia."""
    if not valor or not referencia:
        return ""
    d = (valor - referencia) / referencia * 100
    if abs(d) < 1:
        return f'<span class="indicador igual">≈ En {texto_ref}</span>'
    if d > 0:
        return f'<span class="indicador arriba">▲ {dec(d)} % sobre {texto_ref}</span>'
    return f'<span class="indicador abajo">▼ {dec(-d)} % bajo {texto_ref}</span>'


def variacion(a, b):
    """Texto con la variación en % de a hasta b, con color."""
    if not a or b is None:
        return ""
    v = (b - a) / a * 100
    clase = "sube" if v >= 0 else "baja"
    return f'<span class="{clase}">{"+" if v >= 0 else "−"}{dec(abs(v))} %</span>'


class Tabla:
    def __init__(self, ruta):
        d = json.loads(ruta.read_text(encoding="utf-8"))
        self.anios = d["anios"]
        self.ind = {nombre: i for i, nombre in enumerate(d["indicadores"])}
        self.datos = d["datos"]

    def serie(self, cod, indicador):
        fila = self.datos.get(cod)
        if not fila or indicador not in self.ind:
            return [None] * len(self.anios)
        return fila[self.ind[indicador]]

    def ultimo(self, cod, indicador):
        return self.serie(cod, indicador)[-1]


# ---------------------------------------------------------------- plantilla de página

def pagina(ruta, titulo, descripcion, cuerpo, migas=None, extra_ld=None, indexable=True, scripts=""):
    url = DOMINIO + ruta
    migas = migas or []
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "item": DOMINIO + (r or ruta)}
        for i, (t, r) in enumerate([("Inicio", "/")] + migas)]}] if migas else []
    ld += extra_ld or []
    migas_html = ""
    if migas:
        partes = ['<a href="/">Inicio</a>'] + [f'<a href="{r}">{escape(t)}</a>' if r else escape(t) for t, r in migas]
        migas_html = f'<nav class="breadcrumbs" aria-label="Ruta">{" › ".join(partes)}</nav>'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{url}">
{'' if indexable else '<meta name="robots" content="noindex">'}
<meta name="theme-color" content="#0e4d3a">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITIO}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMINIO}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''}
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{CABECERA_ANUNCIOS}
</head>
<body>
<header class="site-header">
  <div class="container">
    <a href="/" class="logo"><span class="logo-mark">€</span><span>Renta <span class="hl">Media</span></span></a>
    <nav class="nav">
      <a href="/municipios-mas-ricos-de-espana/">Más ricos</a>
      <a href="/municipios-mas-pobres-de-espana/">Más pobres</a>
      <a href="/provincias/">Provincias</a>
      <a href="/barrios/">Barrios</a>
      <a href="/comparar-renta/">¿Estás por encima?</a>
    </nav>
  </div>
</header>
<main class="container">
{migas_html}
{cuerpo}
</main>
<footer class="site-footer">
  <div class="container">
    <p><strong>{SITIO}</strong> muestra la renta media de cada municipio, provincia y barrio de España con los datos oficiales del Instituto Nacional de Estadística (INE).</p>
    <div class="links"><a href="/">Buscar un municipio</a><a href="/municipios-mas-ricos-de-espana/">Municipios más ricos</a><a href="/municipios-mas-pobres-de-espana/">Municipios más pobres</a><a href="/ciudades-mas-ricas-de-espana/">Ciudades más ricas</a><a href="/provincias/">Provincias y comunidades</a><a href="/barrios/">Barrios de cada ciudad</a><a href="/barrios-mas-ricos-de-espana/">Barrios más ricos de España</a><a href="/comparar-renta/">¿Estás por encima de la media?</a><a href="/sobre-los-datos/">Sobre los datos</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad y cookies</a>{CONFIGURAR_COOKIES}</div>
    <p>Fuente: INE, Atlas de Distribución de Renta de los Hogares. Datos reutilizados conforme a sus condiciones de uso; esta web no está vinculada al INE.</p>
  </div>
</footer>
{scripts}
</body>
</html>
"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


def bloque_compartir(texto, ruta):
    url = DOMINIO + ruta
    wa = quote(f"{texto} {url}")
    x = f"text={quote(texto)}&amp;url={quote(url)}"
    return (f'<div class="compartir"><span>Compártelo:</span>'
            f'<a class="btn-c wa" href="https://wa.me/?text={wa}" target="_blank" rel="noopener">WhatsApp</a>'
            f'<a class="btn-c" href="https://twitter.com/intent/tweet?{x}" target="_blank" rel="noopener">X</a>'
            f'<button type="button" class="btn-c" data-compartir hidden data-texto="{escape(texto)}" data-url="{url}">Más…</button>'
            f'<button type="button" class="btn-c" data-copiar="{url}" hidden>Copiar enlace</button></div>'
            f'<script src="/assets/compartir.js?v={VERSION}" defer></script>')


def faq_ld(preguntas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": p, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}}
        for p, r in preguntas]}


def faq_html(preguntas):
    return "".join(f"<details><summary>{escape(p)}</summary><p>{r}</p></details>" for p, r in preguntas)


# ---------------------------------------------------------------- gráficos SVG

def grafico_evolucion(anios, valores, etiqueta, referencia=None, nombre_ref="España"):
    """Barras de la renta por año, con la cifra encima y, si se pasa, la línea de la referencia (España).
    Ligero: SVG en línea, sin JavaScript."""
    puntos = [(a, v, r) for a, v, r in zip(anios, valores, referencia or [None] * len(anios)) if v is not None]
    if len(puntos) < 2:
        return ""
    ancho, alto, margen_inf, margen_sup = 640, 230, 26, 24
    maximo = max([v for _, v, _ in puntos] + [r for *_, r in puntos if r])
    paso = ancho / len(puntos)
    barra = paso * 0.62
    escala = (alto - margen_inf - margen_sup) / maximo
    partes, linea = [], []
    for i, (a, v, r) in enumerate(puntos):
        h = v * escala
        x = i * paso + (paso - barra) / 2
        y = alto - margen_inf - h
        ultimo = i == len(puntos) - 1
        color = "#0e4d3a" if ultimo else "#c9dcd1"
        partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{barra:.1f}" height="{h:.1f}" rx="4" fill="{color}"><title>{a}: {euros(v)}</title></rect>'
                      f'<text x="{x + barra / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="13" font-weight="{700 if ultimo else 500}" fill="#10231d">{dec(v / 1000)}k</text>'
                      f'<text x="{x + barra / 2:.1f}" y="{alto - 8}" text-anchor="middle" font-size="13" fill="#5b6660">{a}</text>')
        if r:
            linea.append((x + barra / 2, alto - margen_inf - r * escala, a, r))
    if len(linea) >= 2:
        partes.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y, *_ in linea)}" fill="none" stroke="#b7862b" stroke-width="2.5" stroke-dasharray="6 4"/>')
        partes += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#b7862b"><title>{nombre_ref} {a}: {euros(r)}</title></circle>' for x, y, a, r in linea]
    leyenda = f' La línea dorada es {nombre_ref}.' if len(linea) >= 2 else ""
    return (f'<figure class="grafico"><svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{escape(etiqueta)}">{"".join(partes)}</svg>'
            f'<figcaption>{escape(etiqueta)}, en miles de euros al año.{leyenda}</figcaption></figure>')


def tabla_anual(anios, valores):
    filas, anterior = [], None
    for a, v in zip(anios, valores):
        filas.append(f'<tr><td>{a}</td><td class="num">{euros(v) if v else "No publicado"}</td>'
                     f'<td class="num">{variacion(anterior, v) if anterior and v else "—"}</td></tr>')
        anterior = v or anterior
    return (f'<details class="anual"><summary>Ver la renta año a año</summary><div class="table-wrap"><table class="data">'
            f'<thead><tr><th>Año</th><th class="num">Renta por persona</th><th class="num">Variación anual</th></tr></thead>'
            f'<tbody>{"".join(reversed(filas))}</tbody></table></div></details>')


def barras_fuentes(valores, referencia, nombre_ref):
    filas = []
    for (ind, texto), v, r in zip(FUENTES, valores, referencia):
        if v is None:
            continue
        ref = f" <small>({nombre_ref}: {pct(r)})</small>" if r is not None else ""
        filas.append(f'<li><span>{texto}</span><span class="barra"><span style="width:{min(v, 100):.1f}%"></span></span>'
                     f'<span class="v">{pct(v)}{ref}</span></li>')
    return f'<ul class="barras fuentes">{"".join(filas)}</ul>' if filas else ""


# ---------------------------------------------------------------- mapas

COLORES_MAPA = ["#f3e7c9", "#dcd39b", "#9cc3a4", "#4f9677", "#0e4d3a"]
SIN_DATO = "#e6e1d6"
GEO = {}  # contornos del INE (data/geo_*.json); vacío si no hay


def simplificar(puntos, tol):
    """Douglas-Peucker sobre una lista de (x, y), sin recursión (los contornos de costa son muy largos)."""
    n_p = len(puntos)
    if n_p < 3:
        return puntos
    conservar = [False] * n_p
    conservar[0] = conservar[-1] = True
    pila = [(0, n_p - 1)]
    while pila:
        a, b = pila.pop()
        (x1, y1), (x2, y2) = puntos[a], puntos[b]
        dx, dy = x2 - x1, y2 - y1
        largo = (dx * dx + dy * dy) ** 0.5
        peor, indice = -1.0, a
        for i in range(a + 1, b):
            x, y = puntos[i]
            d = (abs(dy * x - dx * y + x2 * y1 - y2 * x1) / largo) if largo else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            if d > peor:
                peor, indice = d, i
        if peor > tol:
            conservar[indice] = True
            pila += [(a, indice), (indice, b)]
    return [p for p, k in zip(puntos, conservar) if k]


def clases(valores):
    """Cortes por quintiles para colorear el mapa."""
    v = sorted(x for x in valores if x)
    if not v:
        return []
    return [v[min(len(v) - 1, int(len(v) * k / 5))] for k in range(1, 5)]


def color(valor, cortes):
    if not valor:
        return SIN_DATO
    return COLORES_MAPA[sum(valor >= c for c in cortes)]


def mapa_svg(formas, etiqueta, ancho=640):
    """formas: [(anillos, valor, título, enlace o None)], anillos como listas planas x, y en metros (UTM).
    Dibuja un mapa coloreado por quintiles con su leyenda. Las formas se simplifican a la resolución de la pantalla."""
    xs = [r[i] for a, *_ in formas for r in a for i in range(0, len(r), 2)]
    ys = [r[i] for a, *_ in formas for r in a for i in range(1, len(r), 2)]
    if not xs:
        return ""
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    escala = ancho / max(x1 - x0, 1)
    alto = max(1, round((y1 - y0) * escala))
    if alto > ancho * 1.4:  # territorios muy alargados: limitar la altura
        escala = ancho * 1.4 / max(y1 - y0, 1)
        alto = round((y1 - y0) * escala)
    cortes = clases([v for _, v, *_ in formas])
    partes = []
    for anillos, valor, titulo, enlace in formas:
        d = []
        for r in anillos:
            pts = [((r[i] - x0) * escala, (y1 - r[i + 1]) * escala) for i in range(0, len(r) - 1, 2)]
            pts = simplificar(pts, 0.6)
            if len(pts) < 3:
                continue
            d.append("M" + " ".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z")
        if not d:
            continue
        forma = f'<path d="{"".join(d)}" fill="{color(valor, cortes)}"><title>{escape(titulo)}</title></path>'
        partes.append(f'<a href="{enlace}">{forma}</a>' if enlace else forma)
    limites = [0] + cortes
    leyenda = "".join(f'<li><i style="background:{c}"></i>{"menos de " + euros(cortes[0]) if k == 0 else ("más de " + euros(limites[k]) if k == 4 else euros(limites[k]) + " – " + euros(cortes[k]))}</li>'
                      for k, c in enumerate(COLORES_MAPA[:len(cortes) + 1]))
    if any(not v for _, v, *_ in formas):
        leyenda += f'<li><i style="background:{SIN_DATO}"></i>sin dato publicado</li>'
    return (f'<figure class="mapa"><svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{escape(etiqueta)}" stroke="#faf8f3" stroke-width="0.6">{"".join(partes)}</svg>'
            f'<figcaption><ul class="leyenda">{leyenda}</ul>{escape(etiqueta)}.</figcaption></figure>')


# ---------------------------------------------------------------- datos

HACIENDA = {}  # datos de Hacienda (data/hacienda.json); vacío si no hay


def cargar():
    for nombre in ("geo_municipios", "geo_secciones"):
        ruta = DATOS / f"{nombre}.json"
        if ruta.exists():
            GEO[nombre] = json.loads(ruta.read_text(encoding="utf-8"))
    ruta_h = DATOS / "hacienda.json"
    if ruta_h.exists():
        HACIENDA.update(json.loads(ruta_h.read_text(encoding="utf-8")))
    t = json.loads((DATOS / "territorios.json").read_text(encoding="utf-8"))
    tablas = {nombre: Tabla(DATOS / f"{nombre}.json") for nombre in (
        "mun_renta", "mun_fuentes", "mun_gini", "mun_demografia", "dis_renta", "dis_demografia",
        "sec_renta", "agr_renta", "agr_fuentes", "agr_gini", "agr_demografia")}
    return t, tablas


def construir(t, T):
    R = T["mun_renta"]
    anios = R.anios
    municipios = {}
    for cod, nombre_ine in t["mun"].items():
        if len(cod) != 5 or cod[:2] not in PROVINCIAS:
            continue
        serie = R.serie(cod, PERSONA)
        if all(v is None for v in serie):
            continue  # municipio desaparecido o sin ningún dato publicado
        poblacion = T["mun_demografia"].serie(cod, POBLACION)
        municipios[cod] = {
            "cod": cod, "ine": nombre_ine, "nombre": bonito(nombre_ine), "prov": cod[:2],
            "serie": serie, "renta": serie[-1], "hogar": R.ultimo(cod, HOGAR), "bruta": R.ultimo(cod, BRUTA_PERSONA),
            "mediana_uc": R.ultimo(cod, MEDIANA_UC), "media_uc": R.ultimo(cod, MEDIA_UC),
            "poblacion": next((p for p in reversed(poblacion) if p), None),
            "hac": HACIENDA.get("municipios", {}).get(cod),
        }
    # slugs únicos: si dos municipios se llaman igual, se añade la provincia
    por_slug = {}
    for m in municipios.values():
        por_slug.setdefault(slug(m["nombre"]), []).append(m)
    for s, lista in por_slug.items():
        for m in lista:
            m["slug"] = s if len(lista) == 1 else f"{s}-{slug(PROVINCIAS[m['prov']][1])}"
    # puestos con el último año (de mayor a menor renta por persona)
    con_dato = sorted((m for m in municipios.values() if m["renta"]), key=lambda m: -m["renta"])
    for i, m in enumerate(con_dato):
        m["puesto_es"] = i + 1
    por_prov = {}
    for m in con_dato:
        por_prov.setdefault(m["prov"], []).append(m)
    for lista in por_prov.values():
        for i, m in enumerate(lista):
            m["puesto_prov"] = i + 1
    return municipios, con_dato, por_prov, anios


def agregado(T, clave_agr, indicador=PERSONA, tabla="agr_renta"):
    return T[tabla].serie(clave_agr, indicador)


def clave_prov(p):
    return "prov:" + PROVINCIAS[p][0]


def clave_ccaa(p):
    return "ccaa:" + PROVINCIAS[p][2]


def ruta_mun(m):
    return f"/municipio/{m['slug']}/"


def ruta_prov(p):
    return f"/provincia/{slug(PROVINCIAS[p][1])}/"


def ruta_ccaa(nombre_ine):
    return f"/comunidad/{slug(COMUNIDADES[nombre_ine])}/"


def ruta_barrios(m):
    return f"/barrios-mas-ricos-de-{m['slug']}/"


def nombre_distrito(cod_dis):
    nombres = NOMBRES_DISTRITOS.get(cod_dis[:5])
    i = int(cod_dis[5:]) - 1
    return nombres[i] if nombres and 0 <= i < len(nombres) else f"Distrito {int(cod_dis[5:])}"


# ---------------------------------------------------------------- página de municipio

def tabla_ranking(lista, actual=None, puesto="puesto_es", con_prov=True, desde=1):
    maximo = max((m["renta"] for m in lista if m["renta"]), default=1)
    filas = []
    for i, m in enumerate(lista):
        p = m.get(puesto) or (desde + i)
        prov = f" <small>{escape(PROVINCIAS[m['prov']][1])}</small>" if con_prov else ""
        hab = f'<td class="num">{n(m["poblacion"])}</td>' if m.get("poblacion") else '<td class="num">—</td>'
        clase = ' class="actual"' if actual is m else ""
        filas.append(f'<tr{clase}><td>{p}</td>'
                     f'<td><a href="{ruta_mun(m)}">{escape(m["nombre"])}</a>{prov}</td>'
                     f'<td class="num">{euros(m["renta"])}<span class="mini"><i style="width:{m["renta"] / maximo * 100:.0f}%"></i></span></td>{hab}</tr>')
    return ('<div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Municipio</th>'
            '<th class="num">Renta por persona</th><th class="num">Habitantes</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>')


def pagina_municipio(m, T, por_prov, total_es, anios, t):
    p = m["prov"]
    nombre, prov_nombre = m["nombre"], PROVINCIAS[p][1]
    ruta = ruta_mun(m)
    ultimo = anios[-1]
    es = agregado(T, "es")[-1]
    provincia = agregado(T, clave_prov(p))[-1]
    ccaa_nombre = COMUNIDADES[PROVINCIAS[p][2]]
    cuerpo = [f"<h1>Renta media en {escape(nombre)}</h1>"]
    descripcion = ""
    preguntas = []
    if m["renta"]:
        dif_es = (m["renta"] - es) / es * 100
        comp = (f"un {dec(abs(dif_es))} % {'más' if dif_es >= 0 else 'menos'} que la media de España ({euros(es)})")
        cuerpo.append(f"""<div class="respuesta">
<p class="etiqueta">Renta neta media por persona (per cápita) · {ultimo}</p>
<p class="cifra">{euros(m['renta'])} <small>al año</small></p>
{indicador(m['renta'], es)}
<p class="sub">Es lo que ingresa de media cada vecino de {escape(nombre)} ({escape(prov_nombre)}), después de impuestos. Media de España: {euros(es)}.</p>
</div>""")
        stats = [f'<div class="stat"><b class="grande">{euros(m["hogar"])}</b><span>renta neta media por hogar</span></div>' if m["hogar"] else "",
                 f'<div class="stat"><b class="grande">{n(m["puesto_es"])}.º</b><span>de {n(total_es)} municipios de España</span></div>',
                 f'<div class="stat"><b class="grande">{n(m["puesto_prov"])}.º</b><span>de {len(por_prov[p])} en la provincia de {escape(prov_nombre)}</span></div>',
                 f'<div class="stat"><b class="grande">{n(m["poblacion"])}</b><span>habitantes</span></div>' if m["poblacion"] else ""]
        cuerpo.append(f'<div class="stats">{"".join(stats)}</div>')
        cuerpo.append(bloque_compartir(f"La renta media en {nombre} es de {euros(m['renta'])} por persona al año (puesto {m['puesto_es']} de España).", ruta))
    h = m.get("hac")
    if h and h.get("bruta_media"):
        ah, hes = HACIENDA["anio_municipios"], HACIENDA["espana"]
        cambio = f'<span class="sub-v">{variacion(h["bruta_media_ant"], h["bruta_media"])} desde {ah - 1}</span>' if h.get("bruta_media_ant") else ""
        cuerpo.append(f"""<h2>Lo más reciente: datos de Hacienda de {ah}</h2>
<p>La Agencia Tributaria ya ha publicado las declaraciones de la renta de {ah}, un año más recientes que las del INE. Mide otra cosa: la renta media <strong>por declaración</strong>, no por persona, así que las cifras son más altas.</p>
<div class="stats">
<div class="stat"><b class="grande">{euros(h['bruta_media'])}</b><span>renta bruta media por declaración {cambio}</span></div>
{f'<div class="stat"><b class="grande">{euros(h["disponible_media"])}</b><span>renta disponible media (después de impuestos)</span></div>' if h.get("disponible_media") else ''}
{f'<div class="stat"><b class="grande">{euros(h["bruta_mediana"])}</b><span>renta bruta mediana: la mitad declara menos</span></div>' if h.get("bruta_mediana") else ''}
{f'<div class="stat"><b class="grande">{n(h["puesto"])}.º</b><span>de {n(len(HACIENDA["municipios"]))} municipios según Hacienda</span></div>' if h.get("puesto") else ''}
</div>
<p class="updated">Media de España en {ah}: {euros(hes['bruta_media'])} brutos y {euros(hes['disponible_media'])} disponibles por declaración. Hacienda solo publica los municipios de más de 1.000 habitantes y no incluye el País Vasco ni Navarra, que tienen haciendas propias.</p>""")
        preguntas.append((f"¿Cuál es la renta media de {nombre} en {ah}?",
                          f"Según la Agencia Tributaria, en {ah} la renta bruta media por declaración en {escape(nombre)} fue de {euros(h['bruta_media'])}"
                          + (f" y la disponible, después de impuestos, de {euros(h['disponible_media'])}" if h.get("disponible_media") else "")
                          + (f", frente a {euros(h['bruta_media_ant'])} brutos en {ah - 1}" if h.get("bruta_media_ant") else "")
                          + f". La media de España fue de {euros(hes['bruta_media'])} brutos."))
        descripcion = (f"Renta media y per cápita de {nombre} ({prov_nombre}): {euros(m['renta'])} por persona y "
                       f"{euros(m['hogar']) + ' por hogar' if m['hogar'] else ''} al año ({ultimo}). Puesto {m['puesto_es']} de España "
                       f"y {m['puesto_prov']} de su provincia. Evolución desde 2015.")
        preguntas.append((f"¿Cuál es la renta media en {nombre}?",
                          f"Según el INE, en {ultimo} la renta neta media por persona en {escape(nombre)} fue de {euros(m['renta'])} al año"
                          + (f" y la renta neta media por hogar, de {euros(m['hogar'])}." if m["hogar"] else ".")))
        preguntas.append((f"¿Cuál es la renta per cápita de {nombre}?",
                          f"La renta per cápita, es decir, la renta neta media por persona, fue de {euros(m['renta'])} en {ultimo} según el INE. "
                          f"Se calcula sumando los ingresos de todos los hogares de {escape(nombre)}, después de impuestos, y dividiéndolos entre todos sus habitantes, niños incluidos."))
        if m["mediana_uc"]:
            med_es = agregado(T, "es", MEDIANA_UC)[-1]
            h_med = (m.get("hac") or {}).get("bruta_mediana")
            preguntas.append((f"¿Cuál es la renta mediana en {nombre}?",
                              f"La mediana de la renta por unidad de consumo en {escape(nombre)} fue de {euros(m['mediana_uc'])} en {ultimo} según el INE"
                              + (f" ({variacion(med_es, m['mediana_uc'])} frente a los {euros(med_es)} de España)" if med_es else "")
                              + ". La mitad de la población está por encima y la otra mitad por debajo, así que la afectan menos unos pocos hogares con ingresos muy altos que a la media."
                              + (f" Según Hacienda, la renta bruta mediana por declaración fue de {euros(h_med)} en {HACIENDA['anio_municipios']}." if h_med else "")))
        preguntas.append((f"¿{nombre} es un municipio rico?",
                          f"Con {euros(m['renta'])} por persona, {escape(nombre)} está en el puesto {m['puesto_es']} de {n(total_es)} municipios "
                          f"de España con datos, {comp}. En su provincia ocupa el puesto {m['puesto_prov']} de {len(por_prov[p])}."))
    else:
        cuerpo.append(f'<div class="card"><p>El INE no publica la renta media de {ultimo} de {escape(nombre)}, '
                      'normalmente porque tiene muy pocos habitantes y la cifra permitiría identificar a los hogares (secreto estadístico). '
                      'Abajo tienes los años que sí están publicados.</p></div>')
        descripcion = f"Renta media de {nombre} ({prov_nombre}) según el INE: evolución desde 2015 y comparación con su provincia y con España."

    # Evolución
    serie = m["serie"]
    primero = next(((a, v) for a, v in zip(anios, serie) if v), None)
    if primero and m["renta"] and primero[0] != ultimo:
        cuerpo.append(f"<h2>Evolución de la renta en {escape(nombre)}</h2>")
        cuerpo.append(f"<p>Desde {primero[0]}, la renta neta media por persona ha pasado de {euros(primero[1])} a {euros(m['renta'])}: "
                      f"{variacion(primero[1], m['renta'])}. En el mismo tiempo, la de su provincia ha cambiado "
                      f"{variacion(agregado(T, clave_prov(p))[anios.index(primero[0])], provincia)}.</p>")
        cuerpo.append(grafico_evolucion(anios, serie, f"Renta neta media por persona en {nombre}, {primero[0]}-{ultimo}", agregado(T, "es")))
        cuerpo.append(tabla_anual(anios, serie))
        preguntas.append((f"¿Cuánto ha subido la renta en {nombre}?",
                          f"Entre {primero[0]} y {ultimo} la renta neta media por persona pasó de {euros(primero[1])} a {euros(m['renta'])}, "
                          f"un {dec(abs((m['renta'] - primero[1]) / primero[1] * 100))} % {'más' if m['renta'] >= primero[1] else 'menos'}. "
                          "Son euros corrientes: no descuentan la inflación."))
    elif any(serie):
        filas = "".join(f"<tr><td>{a}</td><td class=\"num\">{euros(v) if v else 'No publicado'}</td></tr>" for a, v in zip(anios, serie))
        cuerpo.append(f'<h2>Años publicados</h2><div class="table-wrap"><table class="data"><thead><tr><th>Año</th><th class="num">Renta por persona</th></tr></thead><tbody>{filas}</tbody></table></div>')

    # Comparación
    if m["renta"]:
        filas = []
        for ind, texto, clave_m in ((PERSONA, "Renta neta por persona", "renta"), (HOGAR, "Renta neta por hogar", "hogar"),
                                    (BRUTA_PERSONA, "Renta bruta por persona", "bruta"), (MEDIANA_UC, "Mediana por unidad de consumo", "mediana_uc")):
            vp = agregado(T, clave_prov(p), ind)[-1]
            ve = agregado(T, "es", ind)[-1]
            filas.append(f"<tr><td>{texto}</td><td class=\"num\"><b>{euros(m[clave_m]) if m[clave_m] else '—'}</b></td>"
                         f"<td class=\"num\">{euros(vp) if vp else '—'}</td><td class=\"num\">{euros(ve) if ve else '—'}</td></tr>")
        cuerpo.append(f"<h2>Comparada con su provincia y con España</h2>"
                      f'<div class="table-wrap"><table class="data"><thead><tr><th>{ultimo}</th><th class="num">{escape(nombre)}</th>'
                      f'<th class="num">Prov. {escape(prov_nombre)}</th><th class="num">España</th></tr></thead><tbody>{"".join(filas)}</tbody></table></div>'
                      '<p class="updated">La renta neta es la bruta menos impuestos y cotizaciones. La «unidad de consumo» ajusta la renta del hogar '
                      'según cuántas personas viven en él, para poder comparar hogares de distinto tamaño.</p>')

    # Fuentes de ingreso
    F = T["mun_fuentes"]
    fuentes = [F.ultimo(m["cod"], ind) for ind, _ in FUENTES]
    fuentes_es = [T["agr_fuentes"].ultimo("es", ind) for ind, _ in FUENTES]
    if any(v is not None for v in fuentes):
        cuerpo.append(f"<h2>¿De dónde vienen los ingresos en {escape(nombre)}?</h2>"
                      f"<p>Qué parte de la renta de los vecinos procede de cada fuente ({ultimo}), comparada con el conjunto de España:</p>"
                      + barras_fuentes(fuentes, fuentes_es, "España"))
        sal, pen = fuentes[0], fuentes[1]
        if sal is not None and m["renta"]:
            preguntas.append((f"¿Cuál es el salario medio en {nombre}?",
                              f"El INE no publica el salario medio de cada municipio, así que no lo damos. Lo que sí publica es la renta: en {escape(nombre)} "
                              f"la renta neta media es de {euros(m['renta'])} por persona"
                              + (f" y {euros(m['hogar'])} por hogar" if m["hogar"] else "")
                              + f" al año ({ultimo}), y el {pct(sal)} de esos ingresos procede de salarios."))
        if sal is not None and pen is not None:
            preguntas.append((f"¿De qué viven los vecinos de {nombre}?",
                              f"El {pct(sal)} de sus ingresos son salarios y el {pct(pen)}, pensiones (en España, {pct(fuentes_es[0])} y {pct(fuentes_es[1])})."))

    # Distritos y secciones
    D = T["dis_renta"]
    distritos = [(c, D.ultimo(c, PERSONA)) for c in sorted(t["dis"]) if c.startswith(m["cod"])]
    distritos = [(c, v) for c, v in distritos if v]
    if len(distritos) > 1 and m["cod"] not in NOMBRES_DISTRITOS:
        distritos.sort(key=lambda x: -x[1])
        cuerpo.append(f"<h2>Renta por distritos de {escape(nombre)}</h2>"
                      f"<p>El INE divide {escape(nombre)} en {len(distritos)} distritos censales: el de más renta llega a <b>{euros(distritos[0][1])}</b> "
                      f"por persona y el de menos se queda en <b>{euros(distritos[-1][1])}</b>.</p>")
    elif len(distritos) > 1:
        distritos.sort(key=lambda x: -x[1])
        filas = "".join(f"<tr><td>{i + 1}</td><td>{escape(nombre_distrito(c))}</td><td class=\"num\">{euros(v)}</td></tr>"
                        for i, (c, v) in enumerate(distritos))
        extra = (f' Mira también <a href="{ruta_barrios(m)}">los barrios más ricos de {escape(nombre)}</a>.'
                 if m["cod"] in HACIENDA.get("ciudades", {}) else "")
        cuerpo.append(f"<h2>Renta por distritos de {escape(nombre)}</h2>"
                      f"<p>El INE divide {escape(nombre)} en {len(distritos)} distritos censales.{extra}</p>"
                      '<div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Distrito</th><th class="num">Renta por persona</th></tr></thead>'
                      f"<tbody>{filas}</tbody></table></div>")
    ciudad = HACIENDA.get("ciudades", {}).get(m["cod"])
    if ciudad:
        cps = sorted(((c, d) for c, d in ciudad["codigos"].items() if d.get("bruta_media")), key=lambda x: -x[1]["bruta_media"])
        if len(cps) >= 2:
            lis = lambda lista: "".join(f'<li>{escape(d["nombre"])} <small>{c} · {euros(d["bruta_media"])}</small></li>' for c, d in lista)
            cuerpo.append(f"<h2>Los barrios más ricos de {escape(nombre)}</h2>"
                          f"<p>Hacienda publica la renta de cada código postal de {escape(nombre)}. Renta bruta media por declaración en {HACIENDA['anio_codigos']}:</p>"
                          f'<div class="dos-col"><div><h3>Los que más</h3><ol class="top3">{lis(cps[:3])}</ol></div>'
                          f'<div><h3>Los que menos</h3><ol class="top3">{lis(list(reversed(cps))[:3])}</ol></div></div>'
                          f'<p><a href="{ruta_barrios(m)}">Ver los {len(cps)} barrios de {escape(nombre)} →</a></p>')
    S = T["sec_renta"]
    secciones = [v for c, fila in S.datos.items() if c.startswith(m["cod"]) and (v := fila[S.ind[PERSONA]][-1])]
    geo_sec = GEO.get("geo_secciones", {}).get(m["cod"])
    if geo_sec and len(secciones) >= 4:
        formas = []
        for cs, anillos in geo_sec.items():
            fila = S.datos.get(cs)
            v = fila[S.ind[PERSONA]][-1] if fila else None
            formas.append((anillos, v, f"Sección {cs[5:7]}-{cs[7:]}: " + (euros(v) if v else "sin dato"), None))
        cuerpo.append(f"<h2>Mapa de la renta en {escape(nombre)}</h2>"
                      "<p>Cada zona es una sección censal del INE, coloreada según su renta neta media por persona. "
                      "Pasa el dedo o el ratón por encima para ver la cifra.</p>"
                      + mapa_svg(formas, f"Renta neta media por persona en las secciones censales de {nombre}, {ultimo}"))
    if len(secciones) >= 4:
        cuerpo.append(f"<h2>Diferencias dentro de {escape(nombre)}</h2>"
                      f"<p>El INE también publica la renta de cada sección censal, zonas de unos 1.000 a 2.500 habitantes. "
                      f"En {escape(nombre)} hay {len(secciones)} con datos: la de más renta llega a <b>{euros(max(secciones))}</b> por persona "
                      f"y la de menos se queda en <b>{euros(min(secciones))}</b>, {dec(max(secciones) / min(secciones))} veces menos.</p>")

    # Desigualdad y población
    G, Dm = T["mun_gini"], T["mun_demografia"]
    gini, p8020 = G.ultimo(m["cod"], "Índice de Gini"), G.ultimo(m["cod"], "Distribución de la renta P80/P20")
    edad, mayores, hogar_tam = (Dm.ultimo(m["cod"], "Edad media de la población"), Dm.ultimo(m["cod"], "Porcentaje de población de 65 y más años"),
                                Dm.ultimo(m["cod"], "Tamaño medio del hogar"))
    datos_extra = []
    if gini is not None:
        datos_extra.append(f'<div class="stat"><b>{dec(gini)}</b><span>índice de Gini (España: {dec(T["agr_gini"].ultimo("es", "Índice de Gini"))})</span></div>')
    if p8020 is not None:
        datos_extra.append(f'<div class="stat"><b>{dec(p8020)} veces</b><span>más renta tiene el 20 % más rico que el 20 % más pobre</span></div>')
    if edad is not None:
        datos_extra.append(f'<div class="stat"><b>{dec(edad)} años</b><span>edad media</span></div>')
    if mayores is not None:
        datos_extra.append(f'<div class="stat"><b>{pct(mayores)}</b><span>tiene 65 años o más</span></div>')
    if hogar_tam is not None:
        datos_extra.append(f'<div class="stat"><b>{dec(hogar_tam)}</b><span>personas por hogar</span></div>')
    if datos_extra:
        cuerpo.append(f"<h2>Desigualdad y población</h2><div class=\"stats\">{''.join(datos_extra)}</div>"
                      '<p class="updated">El índice de Gini va de 0 (todos ganan lo mismo) a 100 (uno lo gana todo): cuanto más alto, más desigualdad.</p>')

    # Comparador
    if m["mediana_uc"]:
        cuerpo.append(f"""<h2>¿Tu hogar está por encima de la media de {escape(nombre)}?</h2>
<form class="calc-form" id="calc" data-mediana="{m['mediana_uc']}" data-media="{m['media_uc'] or ''}" data-lugar="{escape(nombre)}" data-anio="{ultimo}">
<label>Ingresos netos del hogar al año (€)<input type="number" name="ingresos" min="0" step="100" inputmode="numeric" required placeholder="Ej.: 32000"></label>
<label>Adultos<input type="number" name="adultos" min="1" max="15" value="1" inputmode="numeric"></label>
<label>Menores de 14<input type="number" name="ninos" min="0" max="15" value="0" inputmode="numeric"></label>
<button class="btn" type="submit">Comparar</button>
</form>
<div id="calc-resultado"></div>
<p class="updated">Se calcula en tu navegador: no se envía ni se guarda nada. Compara tus ingresos ajustados por el tamaño del hogar con la mediana de {escape(nombre)} de {ultimo}.</p>""")

    # Municipios cercanos en el ranking de la provincia
    if m["renta"]:
        lista = por_prov[p]
        i = m["puesto_prov"] - 1
        cerca = lista[max(0, i - 3): i + 4]
        cuerpo.append(f"<h2>Municipios con renta parecida en {escape(prov_nombre)}</h2>"
                      + tabla_ranking(cerca, m, "puesto_prov", con_prov=False)
                      + f'<p><a href="{ruta_prov(p)}">Ver el ranking completo de la provincia de {escape(prov_nombre)} →</a></p>')

    if preguntas:
        cuerpo.append(f'<div class="content"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</div>')
    cuerpo.append(f'<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares (datos de {anios[0]} a {ultimo}). '
                  f'Las cifras son la renta del año indicado, que el INE publica unos dos años después. <a href="/sobre-los-datos/">Sobre los datos</a>.</p>')
    # Título y descripción para Google: qué hay en la página, sin dar la cifra (si la da, nadie entra)
    if m["renta"]:
        anio_titulo = HACIENDA["anio_municipios"] if h and h.get("bruta_media") else ultimo
        titulo = f"Renta media y per cápita en {nombre} (datos {anio_titulo})"
        if len(titulo) > 65:
            titulo = f"Renta media en {nombre} (datos {anio_titulo})"
        texto = "\n".join(cuerpo)
        extras = ["la renta por persona y por hogar del INE" if m["hogar"] else "la renta por persona del INE"]
        if h and h.get("bruta_media"):
            extras.append(f"los datos de Hacienda de {HACIENDA['anio_municipios']}")
        if "<h2>Los barrios más ricos de" in texto:
            extras.append("los barrios más ricos")
        if "<h2>Mapa de la renta en" in texto:
            extras.append("el mapa por zonas")
        extras.append("su puesto en España y en su provincia")
        extras.append(f"la evolución desde {primero[0]}" if primero and primero[0] != ultimo else "cómo ha cambiado")
        descripcion = f"¿Cuánto se gana en {nombre}? Mira " + ", ".join(extras[:-1]) + " y " + extras[-1] + "."
    else:
        titulo = f"Renta media en {nombre}"
    migas = [(COMUNIDADES[PROVINCIAS[p][2]], ruta_ccaa(PROVINCIAS[p][2])), (prov_nombre, ruta_prov(p)), (nombre, None)]
    if ccaa_nombre == prov_nombre:
        migas = migas[1:]
    return pagina(ruta, titulo, descripcion, "\n".join(cuerpo), migas, [faq_ld(preguntas)] if preguntas else None,
                  scripts=f'<script src="/assets/comparar.js?v={VERSION}" defer></script>' if m["mediana_uc"] else "")


# ---------------------------------------------------------------- rankings

def mapa_provincia(p, por_prov, municipios_prov):
    geo = GEO.get("geo_municipios", {})
    formas = [(geo[m["cod"]], m["renta"], f'{m["nombre"]}: ' + (euros(m["renta"]) if m["renta"] else "sin dato"), ruta_mun(m))
              for m in municipios_prov.get(p, []) if m["cod"] in geo]
    if len(formas) < 3:
        return ""
    nombre = PROVINCIAS[p][1]
    return (f"<h2>Mapa de la renta en la provincia de {escape(nombre)}</h2>"
            "<p>Cada pueblo, coloreado según su renta neta media por persona. Toca uno para ver sus datos.</p>"
            + mapa_svg(formas, f"Renta neta media por persona en los municipios de {nombre}"))


def paginas_ranking(con_dato, por_prov, T, anios, todos_municipios=()):
    ultimo = anios[-1]
    grandes = [m for m in con_dato if (m["poblacion"] or 0) >= MIN_HAB_RANKING]
    for i, m in enumerate(grandes):
        m["puesto_grandes"] = i + 1
    pequenos = [m for m in con_dato if (m["poblacion"] or 0) < MIN_HAB_RANKING]
    es = agregado(T, "es")[-1]
    rutas = []

    ricos = grandes[:100]
    top = ricos[0]
    cuerpo = f"""<h1>Los pueblos y ciudades más ricos de España</h1>
<p class="lead">Ranking de los {len(ricos)} municipios de más de {n(MIN_HAB_RANKING)} habitantes con la renta neta media por persona más alta en {ultimo}, según el INE. La media de España es de {euros(es)}.</p>
<div class="respuesta"><p class="etiqueta">El municipio más rico de España · {ultimo}</p><p class="nombre">{escape(top['nombre'])}</p>
<p class="sub">{escape(PROVINCIAS[top['prov']][1])}: {euros(top['renta'])} por persona al año, {dec(top['renta'] / es)} veces la media de España.</p></div>
{bloque_compartir(f"Los municipios más ricos de España: {top['nombre']} encabeza el ranking con {euros(top['renta'])} por persona.", "/municipios-mas-ricos-de-espana/")}
{tabla_ranking(ricos, puesto="puesto_grandes")}
<h2>Los pueblos pequeños más ricos</h2>
<p>Entre los municipios de menos de {n(MIN_HAB_RANKING)} habitantes la renta varía mucho de un año a otro, porque pocos hogares con ingresos altos mueven la media. Por eso van aparte:</p>
{tabla_ranking(pequenos[:20])}
<p>¿Y tu pueblo? Búscalo en la <a href="/">portada</a> o mira el ranking de <a href="/provincias/">tu provincia</a>. Solo ciudades grandes: <a href="/ciudades-mas-ricas-de-espana/">las ciudades más ricas de España</a>.</p>
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}. Municipios con al menos {n(MIN_HAB_RANKING)} habitantes, como en las notas de prensa del INE.</p>"""
    preguntas = [("¿Cuál es el pueblo más rico de España?",
                  f"Según el INE, en {ultimo} el municipio de más de {n(MIN_HAB_RANKING)} habitantes con más renta neta media por persona fue "
                  f"{escape(top['nombre'])} ({escape(PROVINCIAS[top['prov']][1])}), con {euros(top['renta'])} al año. "
                  f"Le siguen {escape(ricos[1]['nombre'])} ({euros(ricos[1]['renta'])}) y {escape(ricos[2]['nombre'])} ({euros(ricos[2]['renta'])}).")]
    cuerpo += f'<div class="content"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</div>'
    guardar("/municipios-mas-ricos-de-espana/", pagina(
        "/municipios-mas-ricos-de-espana/", f"Los pueblos y ciudades más ricos de España (renta {ultimo})",
        f"Los 100 pueblos y ciudades más ricos de España por renta media por persona ({ultimo}, INE): cuál es el más rico, cuánto se gana y en qué provincias están.",
        cuerpo, [("Municipios más ricos", None)], [faq_ld(preguntas)]))
    rutas.append("/municipios-mas-ricos-de-espana/")

    pobres = list(reversed(grandes[-100:]))
    for i, m in enumerate(pobres):
        m["puesto_pobres"] = i + 1
    ult = pobres[0]
    cuerpo = f"""<h1>Los pueblos y ciudades más pobres de España</h1>
<p class="lead">Los {len(pobres)} municipios de más de {n(MIN_HAB_RANKING)} habitantes con la renta neta media por persona más baja en {ultimo}, según el INE. La media de España es de {euros(es)}.</p>
<div class="respuesta"><p class="etiqueta">El municipio con menos renta de España · {ultimo}</p><p class="nombre">{escape(ult['nombre'])}</p>
<p class="sub">{escape(PROVINCIAS[ult['prov']][1])}: {euros(ult['renta'])} por persona al año.</p></div>
{tabla_ranking(pobres, puesto="puesto_pobres")}
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}. Municipios con al menos {n(MIN_HAB_RANKING)} habitantes.</p>"""
    guardar("/municipios-mas-pobres-de-espana/", pagina(
        "/municipios-mas-pobres-de-espana/", f"Los pueblos más pobres de España (renta {ultimo})",
        f"Los 100 pueblos y ciudades de España con menos renta media por persona ({ultimo}, INE): cuál tiene la renta más baja y en qué provincias están.",
        cuerpo, [("Municipios más pobres", None)]))
    rutas.append("/municipios-mas-pobres-de-espana/")

    # Ciudades grandes
    ciudades = [m for m in con_dato if (m["poblacion"] or 0) >= MIN_HAB_CIUDAD]
    for i, m in enumerate(ciudades):
        m["puesto_ciudad"] = i + 1
    primera, ultima = ciudades[0], ciudades[-1]
    capitales = [m for m in ciudades if m["cod"] in ("28079", "08019", "46250", "41091", "50297", "29067")]
    cuerpo = f"""<h1>Las ciudades más ricas de España</h1>
<p class="lead">Las {len(ciudades)} ciudades de más de {n(MIN_HAB_CIUDAD)} habitantes ordenadas por renta neta media por persona en {ultimo}, según el INE. La media de España es de {euros(es)}.</p>
<div class="respuesta"><p class="etiqueta">La ciudad más rica de España · {ultimo}</p><p class="nombre">{escape(primera['nombre'])}</p>
<p class="sub">{escape(PROVINCIAS[primera['prov']][1])}: {euros(primera['renta'])} por persona al año. La que menos, {escape(ultima['nombre'])}, se queda en {euros(ultima['renta'])}.</p></div>
{bloque_compartir(f"Las ciudades más ricas de España: {primera['nombre']} encabeza el ranking con {euros(primera['renta'])} por persona.", "/ciudades-mas-ricas-de-espana/")}
<p>Las grandes capitales: {", ".join(f'<a href="{ruta_mun(m)}">{escape(m["nombre"])}</a> ({m["puesto_ciudad"]}.ª, {euros(m["renta"])})' for m in capitales)}.</p>
{tabla_ranking(ciudades, puesto="puesto_ciudad")}
<p>¿Buscas un pueblo? Mira <a href="/municipios-mas-ricos-de-espana/">los pueblos y ciudades más ricos de España</a> o el ranking de <a href="/provincias/">tu provincia</a>.</p>
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}. Ciudades con al menos {n(MIN_HAB_CIUDAD)} habitantes.</p>"""
    preguntas = [("¿Cuál es la ciudad más rica de España?",
                  f"Entre las ciudades de más de {n(MIN_HAB_CIUDAD)} habitantes, la de mayor renta neta media por persona en {ultimo} fue "
                  f"{escape(primera['nombre'])} ({euros(primera['renta'])}), seguida de {escape(ciudades[1]['nombre'])} y {escape(ciudades[2]['nombre'])}. "
                  f"De las grandes capitales, " + ", ".join(f"{escape(m['nombre'])} ocupa el puesto {m['puesto_ciudad']}" for m in capitales) + ".")]
    cuerpo += f'<div class="content"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</div>'
    guardar("/ciudades-mas-ricas-de-espana/", pagina(
        "/ciudades-mas-ricas-de-espana/", f"Las ciudades más ricas de España: ranking de renta {ultimo}",
        f"Ranking de las {len(ciudades)} ciudades de más de {n(MIN_HAB_CIUDAD)} habitantes por renta media por persona ({ultimo}, INE): cuál es la más rica y en qué puesto está la tuya.",
        cuerpo, [("Ciudades más ricas", None)], [faq_ld(preguntas)]))
    rutas.append("/ciudades-mas-ricas-de-espana/")

    # Provincias
    filas_prov = []
    municipios_prov = {}
    for m in todos_municipios:
        municipios_prov.setdefault(m["prov"], []).append(m)
    for p, (ine, nombre, ccaa) in sorted(PROVINCIAS.items(), key=lambda x: -(agregado(T, clave_prov(x[0]))[-1] or 0)):
        v = agregado(T, clave_prov(p))[-1]
        lista = por_prov.get(p, [])
        if not lista:
            continue
        filas_prov.append((p, nombre, v))
        cuerpo = f"""<h1>Renta media en la provincia de {escape(nombre)}</h1>
<div class="respuesta"><p class="etiqueta">Renta neta media por persona · provincia de {escape(nombre)} · {ultimo}</p><p class="cifra">{euros(v)} <small>al año</small></p>
{indicador(v, es)}<p class="sub">Media de España: {euros(es)}.</p></div>
{grafico_evolucion(anios, agregado(T, clave_prov(p)), f"Renta neta media por persona en la provincia de {nombre}", agregado(T, "es"))}
{mapa_provincia(p, por_prov, municipios_prov)}
<h2>Todos los pueblos de {escape(nombre)}, de más a menos renta</h2>
{tabla_ranking(lista, puesto="puesto_prov", con_prov=False)}
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}. Los municipios sin cifra publicada (secreto estadístico) no aparecen.</p>"""
        ruta = ruta_prov(p)
        guardar(ruta, pagina(ruta, f"Pueblos más ricos de {nombre}: renta media {ultimo}",
                             f"Ranking de los {len(lista)} pueblos y ciudades de la provincia de {nombre} por renta media por persona ({ultimo}, INE): cuál es el más rico, el más pobre y dónde está el tuyo.",
                             cuerpo, [(COMUNIDADES[ccaa], ruta_ccaa(ccaa)), (nombre, None)]))
        rutas.append(ruta)
    # Comunidades
    filas_ccaa = []
    for ine, nombre in sorted(COMUNIDADES.items(), key=lambda x: -(agregado(T, "ccaa:" + x[0])[-1] or 0)):
        v = agregado(T, "ccaa:" + ine)[-1]
        provs = [p for p, x in PROVINCIAS.items() if x[2] == ine]
        lista = sorted((m for p in provs for m in por_prov.get(p, []) if (m["poblacion"] or 0) >= MIN_HAB_RANKING), key=lambda m: -m["renta"])
        filas_ccaa.append((ine, nombre, v))
        for i, m in enumerate(lista):
            m["_p"] = i + 1
        enlaces = "".join(f'<li><a href="{ruta_prov(p)}">{escape(PROVINCIAS[p][1])}</a> <small>{euros(agregado(T, clave_prov(p))[-1])}</small></li>' for p in provs)
        cuerpo = f"""<h1>Renta media en {escape(nombre)}</h1>
<div class="respuesta"><p class="etiqueta">Renta neta media por persona · {escape(nombre)} · {ultimo}</p><p class="cifra">{euros(v)} <small>al año</small></p>
{indicador(v, es)}<p class="sub">Media de España: {euros(es)}.</p></div>
{grafico_evolucion(anios, agregado(T, "ccaa:" + ine), f"Renta neta media por persona en {nombre}", agregado(T, "es"))}
{f'<h2>Provincias</h2><ul class="chips">{enlaces}</ul>' if len(provs) > 1 else ''}
<h2>Los pueblos y ciudades más ricos de {escape(nombre)}</h2>
<p>Municipios de más de {n(MIN_HAB_RANKING)} habitantes, de más a menos renta por persona.</p>
{tabla_ranking(lista[:100], puesto="_p", con_prov=len(provs) > 1) if lista else '<p>No hay municipios de ese tamaño con datos.</p>'}
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}.</p>"""
        ruta = ruta_ccaa(ine)
        guardar(ruta, pagina(ruta, f"Pueblos más ricos de {nombre}: renta media {ultimo}",
                             f"Renta media en {nombre} ({ultimo}) y ranking de sus pueblos y ciudades más ricos según el INE: cuál es el primero y dónde está el tuyo.",
                             cuerpo, [(nombre, None)]))
        rutas.append(ruta)
    filas_html = "".join(f'<tr><td>{i + 1}</td><td><a href="{ruta_ccaa(ine)}">{escape(nombre)}</a></td><td class="num">{euros(v)}</td></tr>'
                         for i, (ine, nombre, v) in enumerate(filas_ccaa))
    filas_p = "".join(f'<tr><td>{i + 1}</td><td><a href="{ruta_prov(p)}">{escape(nombre)}</a></td><td class="num">{euros(v)}</td></tr>'
                      for i, (p, nombre, v) in enumerate(filas_prov))
    cuerpo = f"""<h1>Renta media por provincias y comunidades</h1>
<p class="lead">Renta neta media por persona en {ultimo} según el INE. Pulsa en cada una para ver el ranking de sus municipios.</p>
<div class="dos-col"><div><h2>Comunidades autónomas</h2><div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Comunidad</th><th class="num">Por persona</th></tr></thead><tbody>{filas_html}</tbody></table></div></div>
<div><h2>Provincias</h2><div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Provincia</th><th class="num">Por persona</th></tr></thead><tbody>{filas_p}</tbody></table></div></div></div>
<p class="fuente">Fuente: INE, Atlas de Distribución de Renta de los Hogares, {ultimo}.</p>"""
    guardar("/provincias/", pagina("/provincias/", f"Renta media por provincias y comunidades autónomas ({ultimo})",
                                   f"Ranking de provincias y comunidades autónomas de España por renta media por persona ({ultimo}, INE).",
                                   cuerpo, [("Provincias", None)]))
    rutas.append("/provincias/")
    return rutas, grandes


def tabla_distritos_ine(m, t, T, anios):
    D = T["dis_renta"]
    filas = sorted(((c, D.ultimo(c, PERSONA), D.ultimo(c, HOGAR), D.serie(c, PERSONA)[0]) for c in sorted(t["dis"])
                    if c.startswith(m["cod"]) and D.ultimo(c, PERSONA)), key=lambda x: -x[1])
    cuerpo = "".join(f"<tr><td>{i + 1}</td><td>{escape(nombre_distrito(c))}</td><td class=\"num\">{euros(v)}</td>"
                     f"<td class=\"num\">{euros(h) if h else '—'}</td><td class=\"num\">{variacion(v0, v) if v0 else '—'}</td></tr>"
                     for i, (c, v, h, v0) in enumerate(filas))
    return (f'<div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Distrito</th><th class="num">Por persona</th>'
            f'<th class="num">Por hogar</th><th class="num">Desde {anios[0]}</th></tr></thead><tbody>{cuerpo}</tbody></table></div>')


def tabla_codigos(cps, con_ciudad=False, municipios=None, desde=1):
    maximo = max(d["bruta_media"] for _, d, *_ in cps)
    filas = []
    for i, (c, d, *resto) in enumerate(cps):
        ciudad = ""
        if con_ciudad:
            m = municipios.get(resto[0])
            ciudad = f' <small>{escape(m["nombre"]) if m else ""}</small>'
        var = variacion(d.get("bruta_media_ant"), d["bruta_media"]) if d.get("bruta_media_ant") else "—"
        filas.append(f'<tr><td>{desde + i}</td><td>{escape(d["nombre"])} <small>{c}</small>{ciudad}</td>'
                     f'<td class="num">{euros(d["bruta_media"])}<span class="mini"><i style="width:{d["bruta_media"] / maximo * 100:.0f}%"></i></span></td>'
                     f'<td class="num">{euros(d["disponible_media"]) if d.get("disponible_media") else "—"}</td><td class="num">{var}</td></tr>')
    return ('<div class="table-wrap"><table class="data ranking codigos"><thead><tr><th>#</th><th>Barrio (código postal)</th>'
            '<th class="num">Renta bruta media</th><th class="num">Disponible</th><th class="num">Último año</th></tr></thead>'
            f'<tbody>{"".join(filas)}</tbody></table></div>')


def paginas_barrios(municipios, t, T, anios):
    rutas = []
    ciudades = HACIENDA.get("ciudades", {})
    if not ciudades:
        return rutas
    ac, hes = HACIENDA["anio_codigos"], HACIENDA["espana"]
    resumen = []
    todos = []
    for cod, ciudad in ciudades.items():
        m = municipios.get(cod)
        if not m:
            continue
        cps = sorted(((c, d) for c, d in ciudad["codigos"].items() if d.get("bruta_media")), key=lambda x: -x[1]["bruta_media"])
        if len(cps) < 2:
            continue
        todos += [(c, d, cod) for c, d in cps]
        (ct, top), (cu, ult) = cps[0], cps[-1]
        resumen.append((m, ciudad, top, ct, ult, cu))
        nombre = m["nombre"]
        ruta = ruta_barrios(m)
        distritos = ""
        if cod in NOMBRES_DISTRITOS:
            distritos = (f"<h2>Renta por distritos (INE, {anios[-1]})</h2><p>El INE publica la renta neta por persona de cada distrito municipal, "
                         f"con datos desde {anios[0]}:</p>" + tabla_distritos_ine(m, t, T, anios))
        preguntas = [(f"¿Cuál es el barrio más rico de {nombre}?",
                      f"Según la Agencia Tributaria, en {ac} el código postal con más renta de {escape(nombre)} fue el {ct} ({escape(top['nombre'])}), "
                      f"con una renta bruta media de {euros(top['bruta_media'])} por declaración, {dec(top['bruta_media'] / hes['bruta_media'])} veces la media de España."),
                     (f"¿Cuál es el barrio más pobre de {nombre}?",
                      f"El código postal con menos renta fue el {cu} ({escape(ult['nombre'])}), con {euros(ult['bruta_media'])} brutos por declaración: "
                      f"{dec(top['bruta_media'] / ult['bruta_media'])} veces menos que {escape(top['nombre'])}.")]
        cuerpo = f"""<h1>Los barrios más ricos de {escape(nombre)}</h1>
<p class="lead">Renta media de cada barrio de {escape(nombre)} en {ac}, por código postal, según las declaraciones de la renta publicadas por Hacienda. Media de la ciudad: {euros(ciudad['bruta_media'])} brutos por declaración.</p>
<div class="respuesta"><p class="etiqueta">El barrio más rico de {escape(nombre)} · {ac}</p><p class="nombre">{escape(top['nombre'])}</p>
{indicador(top['bruta_media'], ciudad['bruta_media'], f"la media de {nombre}")}
<p class="sub">Código postal {ct}: {euros(top['bruta_media'])} de renta bruta media por declaración, {dec(top['bruta_media'] / ult['bruta_media'])} veces más que {escape(ult['nombre'])} ({cu}, {euros(ult['bruta_media'])}).</p></div>
{bloque_compartir(f"El barrio más rico de {nombre} es {top['nombre']} ({ct}): {euros(top['bruta_media'])} de renta media por declaración.", ruta)}
<h2>Todos los barrios de {escape(nombre)}, de más a menos renta</h2>
{tabla_codigos(cps)}
<p class="updated">Renta bruta: antes de impuestos. Disponible: después de impuestos y cotizaciones. «Último año»: cambio respecto a {ac - 1}. Hacienda solo publica los códigos postales con más de 900 declaraciones.</p>
{distritos}
<p>Más datos de la ciudad en la página de <a href="{ruta_mun(m)}">renta media de {escape(nombre)}</a>. Otras ciudades: <a href="/barrios/">barrios más ricos de cada ciudad</a>.</p>
<div class="content"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</div>
<p class="fuente">Fuente: Agencia Tributaria, Estadística de los declarantes del IRPF de los mayores municipios por código postal, {ac}{f"; INE, Atlas de Distribución de Renta de los Hogares, {anios[-1]}" if distritos else ""}.</p>"""
        guardar(ruta, pagina(ruta, f"Los barrios más ricos de {nombre}: renta por código postal {ac}",
                             f"Ranking de los {len(cps)} barrios (códigos postales) de {nombre} por renta media en {ac} según Hacienda: cuáles son los más ricos, los más pobres y en qué puesto está el tuyo.",
                             cuerpo, [(nombre, ruta_mun(m)), ("Barrios", "/barrios/"), (f"Barrios de {nombre}", None)], [faq_ld(preguntas)]))
        rutas.append(ruta)

    # Índice de ciudades
    resumen.sort(key=lambda x: -x[1]["bruta_media"])
    filas = "".join(f'<tr><td>{i + 1}</td><td><a href="{ruta_barrios(m)}">{escape(m["nombre"])}</a></td>'
                    f'<td class="num">{euros(ciudad["bruta_media"])}</td><td>{escape(top["nombre"])} <small>{euros(top["bruta_media"])}</small></td></tr>'
                    for i, (m, ciudad, top, ct, ult, cu) in enumerate(resumen))
    cuerpo = f"""<h1>Los barrios más ricos de cada ciudad</h1>
<p class="lead">Hacienda publica la renta de cada código postal de las {len(resumen)} ciudades más grandes de España. Elige tu ciudad para ver todos sus barrios, del más rico al menos.</p>
<p>¿Y en toda España? Mira <a href="/barrios-mas-ricos-de-espana/">los barrios más ricos de España</a>.</p>
<div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Ciudad</th><th class="num">Media de la ciudad</th><th>Su barrio más rico</th></tr></thead><tbody>{filas}</tbody></table></div>
<p class="fuente">Fuente: Agencia Tributaria, renta bruta media por declaración, {ac}.</p>"""
    guardar("/barrios/", pagina("/barrios/", f"Los barrios más ricos de cada ciudad de España ({ac})",
                                f"Renta media por barrio (código postal) de las {len(resumen)} ciudades más grandes de España según Hacienda ({ac}).",
                                cuerpo, [("Barrios", None)]))
    rutas.append("/barrios/")

    # Ranking de España
    todos.sort(key=lambda x: -x[1]["bruta_media"])
    (c0, d0, m0), pobres = todos[0], list(reversed(todos))[:50]
    preguntas = [("¿Cuál es el barrio más rico de España?",
                  f"Entre los códigos postales que publica Hacienda, el de más renta en {ac} fue el {c0} ({escape(d0['nombre'])}, {escape(municipios[m0]['nombre'])}), "
                  f"con {euros(d0['bruta_media'])} de renta bruta media por declaración: {dec(d0['bruta_media'] / hes['bruta_media'])} veces la media de España ({euros(hes['bruta_media'])}).")]
    cuerpo = f"""<h1>Los barrios más ricos de España</h1>
<p class="lead">Los 100 códigos postales con más renta de las {len(resumen)} ciudades más grandes de España en {ac}, según las declaraciones de la renta publicadas por Hacienda. Media de España: {euros(hes['bruta_media'])} brutos por declaración.</p>
<div class="respuesta"><p class="etiqueta">El barrio más rico de España · {ac}</p><p class="nombre">{escape(d0['nombre'])}</p>
<p class="sub">{escape(municipios[m0]['nombre'])}, código postal {c0}: {euros(d0['bruta_media'])} de renta bruta media por declaración, {dec(d0['bruta_media'] / hes['bruta_media'])} veces la media de España.</p></div>
{bloque_compartir(f"El barrio más rico de España es {d0['nombre']} ({municipios[m0]['nombre']}): {euros(d0['bruta_media'])} de renta media por declaración.", "/barrios-mas-ricos-de-espana/")}
{tabla_codigos(todos[:100], True, municipios)}
<h2>Los barrios con menos renta</h2>
{tabla_codigos(pobres, True, municipios)}
<p>Elige tu ciudad en <a href="/barrios/">los barrios más ricos de cada ciudad</a>.</p>
<div class="content"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</div>
<p class="fuente">Fuente: Agencia Tributaria, Estadística de los declarantes del IRPF de los mayores municipios por código postal, {ac}. Solo incluye las {len(resumen)} ciudades que publica Hacienda (no incluye el País Vasco ni Navarra).</p>"""
    guardar("/barrios-mas-ricos-de-espana/", pagina(
        "/barrios-mas-ricos-de-espana/", f"Los barrios más ricos de España: ranking por código postal {ac}",
        f"Los 100 barrios (códigos postales) más ricos de España según Hacienda ({ac}). El primero: {d0['nombre']}, en {municipios[m0]['nombre']}, con {euros(d0['bruta_media'])}.",
        cuerpo, [("Barrios", "/barrios/"), ("Barrios más ricos de España", None)], [faq_ld(preguntas)]))
    rutas.append("/barrios-mas-ricos-de-espana/")
    return rutas


# ---------------------------------------------------------------- portada, comparador y buscador

def portada(con_dato, grandes, T, anios, n_paginas):
    ultimo = anios[-1]
    mayores = sorted((m for m in con_dato if m["poblacion"]), key=lambda m: -m["poblacion"])[:24]
    ciudades_html = "".join(f'<li><a href="{ruta_mun(m)}">{escape(m["nombre"])}</a> <small>{euros(m["renta"])}</small></li>' for m in mayores)
    ccaa_html = "".join(f'<li><a href="{ruta_ccaa(ine)}">{escape(nombre)}</a></li>' for ine, nombre in sorted(COMUNIDADES.items(), key=lambda x: sin_tildes(x[1])))
    es = agregado(T, "es")[-1]
    top = "".join(f'<li><a href="{ruta_mun(m)}">{escape(m["nombre"])}</a> <small>{euros(m["renta"])}</small></li>' for m in grandes[:10])
    bottom = "".join(f'<li><a href="{ruta_mun(m)}">{escape(m["nombre"])}</a> <small>{euros(m["renta"])}</small></li>' for m in list(reversed(grandes))[:10])
    cuerpo = f"""<section class="hero">
<h1>¿Cuál es la renta media de tu pueblo o ciudad?</h1>
<p>Busca cualquiera de los {n(n_paginas)} municipios de España y mira cuánto ingresan de media sus vecinos, cómo ha cambiado y en qué puesto está.</p>
<form class="buscador" id="buscador" action="/" role="search">
<input type="search" id="q" name="q" placeholder="Escribe tu municipio…" autocomplete="off" aria-label="Municipio">
<button class="btn" type="submit">Buscar</button>
</form>
<ul class="lista-sug" id="sugerencias"></ul>
<ul class="sugerencias"><li><a href="/municipio/madrid/">Madrid</a></li><li><a href="/municipio/barcelona/">Barcelona</a></li><li><a href="/municipio/valencia/">Valencia</a></li><li><a href="/municipio/sevilla/">Sevilla</a></li><li><a href="/municipio/getafe/">Getafe</a></li></ul>
</section>
<div class="stats"><div class="stat"><b class="grande">{euros(es)}</b><span>renta neta media por persona en España ({ultimo})</span></div>
<div class="stat"><b class="grande">{euros(agregado(T, "es", HOGAR)[-1])}</b><span>renta neta media por hogar</span></div></div>
<div class="dos-col">
<div class="card"><h2 style="margin-top:0">Los más ricos</h2><ol class="top3">{top}</ol><p><a href="/municipios-mas-ricos-de-espana/">Ver los 100 más ricos →</a></p></div>
<div class="card"><h2 style="margin-top:0">Los que menos</h2><ol class="top3">{bottom}</ol><p><a href="/municipios-mas-pobres-de-espana/">Ver los 100 más pobres →</a></p></div>
</div>
<div class="grid">
<a class="card" href="/ciudades-mas-ricas-de-espana/"><h3>Ciudades más ricas</h3><p>Las ciudades de más de 50.000 habitantes, de la primera a la última.</p></a>
<a class="card" href="/barrios/"><h3>Barrios de cada ciudad</h3><p>Renta de cada código postal de las ciudades más grandes, con los datos más recientes de Hacienda.</p></a>
<a class="card" href="/barrios-mas-ricos-de-espana/"><h3>Barrios más ricos de España</h3><p>Los 100 códigos postales con más renta del país.</p></a>
<a class="card" href="/comparar-renta/"><h3>¿Estás por encima de la media?</h3><p>Compara los ingresos de tu hogar con los de tu municipio.</p></a>
</div>
<h2>Las ciudades más pobladas</h2>
<ul class="chips">{ciudades_html}</ul>
<h2>Por comunidades</h2>
<ul class="chips">{ccaa_html}</ul>
<p><a href="/provincias/">Ver todas las provincias →</a></p>
<p class="fuente">Datos del INE (Atlas de Distribución de Renta de los Hogares) de {anios[0]} a {ultimo}. <a href="/sobre-los-datos/">Sobre los datos</a>.</p>"""
    return pagina("/", "Renta media de tu pueblo o ciudad: municipios más ricos de España",
                  f"Renta media por persona y por hogar de los {n(n_paginas)} municipios de España, con su evolución y ranking. Datos oficiales del INE ({ultimo}).",
                  cuerpo, scripts=f'<script src="/assets/buscar.js?v={VERSION}" defer></script>')


def pagina_comparador(anios):
    ultimo = anios[-1]
    cuerpo = f"""<h1>¿Tu hogar está por encima de la media?</h1>
<p class="lead">Busca tu municipio y, en su página, escribe los ingresos netos de tu hogar: te diremos si estás por encima o por debajo de la mitad de tus vecinos.</p>
<form class="buscador" id="buscador" action="/" role="search">
<input type="search" id="q" name="q" placeholder="Escribe tu municipio…" autocomplete="off" aria-label="Municipio">
<button class="btn" type="submit">Buscar</button>
</form>
<ul class="lista-sug" id="sugerencias"></ul>
<div class="content"><h2>Cómo se compara</h2>
<p>No es lo mismo ganar 30.000 € al año viviendo solo que con dos hijos. Por eso el INE ajusta la renta de cada hogar según cuántas personas viven en él, con la llamada <strong>escala de la OCDE modificada</strong>: el primer adulto cuenta 1, cada adulto más cuenta 0,5 y cada menor de 14 años, 0,3. El resultado es la renta por «unidad de consumo».</p>
<p>Comparamos la tuya con la <strong>mediana</strong> de tu municipio: la cifra que deja a la mitad de los vecinos por encima y a la otra mitad por debajo. Los datos del INE son de {ultimo}; si tus ingresos son de un año posterior, ten en cuenta que los sueldos han subido desde entonces.</p></div>"""
    return pagina("/comparar-renta/", "¿Tu hogar está por encima de la media de tu municipio?",
                  "Compara los ingresos de tu hogar con la renta mediana de tu municipio, ajustada por el número de personas, con datos del INE.",
                  cuerpo, [("¿Estás por encima?", None)], scripts=f'<script src="/assets/buscar.js?v={VERSION}" defer></script>')


def indices_busqueda(municipios):
    grupos = {}
    for m in municipios.values():
        claves = {clave(m["nombre"]), clave(m["ine"])} | {clave(p) for p in m["ine"].split("/")}
        claves |= {clave(ARTICULO.sub(r"\1", p.strip())) for p in m["ine"].split("/")}
        entrada = [sorted(claves), m["nombre"], m["slug"], PROVINCIAS[m["prov"]][1], m["renta"], m["poblacion"] or 0]
        for k in claves:
            for palabra in {k[:1]} | {w[:1] for w in k.split()}:
                if palabra:
                    g = palabra if palabra.isalpha() and palabra.isascii() else "otros"
                    grupos.setdefault(g, {})[m["slug"]] = entrada
    destino = WEB / "indice"
    destino.mkdir(parents=True, exist_ok=True)
    for g, entradas in grupos.items():
        (destino / f"{g}.json").write_text(json.dumps(list(entradas.values()), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return grupos


def paginas_legales(anios):
    t = TITULAR
    ultimo = anios[-1]
    sobre = f"""<h1>Sobre los datos</h1><div class="content">
<h2>De dónde salen</h2>
<p>Todos los datos proceden del <strong>Atlas de Distribución de Renta de los Hogares</strong> del Instituto Nacional de Estadística (INE). El INE lo elabora cruzando los datos fiscales de la Agencia Tributaria y de las haciendas forales del País Vasco y Navarra con el padrón, y lo publica para todos los municipios, distritos y secciones censales de España. Los datos actuales van de {anios[0]} a {ultimo}.</p>
<h2>Qué significa cada cifra</h2>
<ul>
<li><strong>Renta neta media por persona:</strong> la suma de los ingresos de los hogares, después de impuestos y cotizaciones, dividida entre todas las personas que viven en ellos, incluidos los niños. Es la cifra principal de esta web.</li>
<li><strong>Renta neta media por hogar:</strong> lo mismo, pero dividido entre el número de hogares.</li>
<li><strong>Renta bruta:</strong> antes de restar impuestos y cotizaciones sociales.</li>
<li><strong>Renta por unidad de consumo:</strong> la renta del hogar ajustada por cuántas personas viven en él (escala de la OCDE modificada), para poder comparar hogares de distinto tamaño. La mediana es la cifra que deja a la mitad de las personas por encima y a la mitad por debajo.</li>
<li><strong>Fuentes de ingreso:</strong> qué parte de la renta bruta procede de salarios, pensiones, prestaciones por desempleo, otras prestaciones y otros ingresos (como las rentas del capital o de actividades económicas).</li>
<li><strong>Índice de Gini:</strong> mide la desigualdad, de 0 (todos tienen la misma renta) a 100 (una persona lo tiene todo).</li>
</ul>
<h2>Por qué los datos son de {ultimo}</h2>
<p>El INE necesita las declaraciones de la renta de cada año, que se presentan al año siguiente, así que publica el atlas con unos dos años de retraso, normalmente en otoño. Esta web se actualiza automáticamente cuando salen datos nuevos.</p>
<h2>Datos que no se publican</h2>
<p>En los municipios y secciones con muy pocos habitantes, el INE oculta algunas cifras para que no se pueda identificar a ningún hogar (secreto estadístico). En esos casos verás «no publicado»: aquí nunca estimamos ni inventamos una cifra.</p>
<h2>Rankings</h2>
<p>Los rankings de España y de las comunidades incluyen solo los municipios con al menos {n(MIN_HAB_RANKING)} habitantes, igual que las notas de prensa del INE, porque en los pueblos muy pequeños unos pocos hogares cambian mucho la media. Los rankings de cada provincia incluyen todos los municipios con datos.</p>
<h2>Condiciones de uso</h2>
<p>Los datos del INE se reutilizan conforme a su aviso legal, citando la fuente. {SITIO} no está vinculada ni avalada por el INE.</p></div>"""
    aviso = f"""<h1>Aviso legal</h1><div class="content">
<h2>Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE), se informa de los datos del titular de este sitio web:</p>
<p>Titular: {t['nombre']}<br>NIF: {t['nif']}<br>Domicilio: {t['domicilio']}<br>Correo electrónico: {t['email']}<br>Sitio web: {DOMINIO}</p>
<h2>Objeto y condiciones de uso</h2>
<p>{SITIO} ofrece de forma gratuita información estadística sobre la renta de los municipios de España a partir de datos públicos del INE. El acceso es libre y no requiere registro.</p>
<h2>Responsabilidad</h2>
<p>Los datos se muestran tal y como los publica el INE, con fines informativos. El titular no se hace responsable de posibles errores en los datos de origen ni del contenido de sitios externos enlazados.</p>
<h2>Propiedad intelectual</h2>
<p>El diseño, los textos y el código de este sitio son del titular. Los datos estadísticos son del INE y se reutilizan citando la fuente.</p>
<h2>Legislación aplicable</h2><p>Estas condiciones se rigen por la legislación española.</p></div>"""
    privacidad = f"""<h1>Política de privacidad</h1><div class="content">
<h2>Responsable</h2><p>{t['nombre']} ({t['email']}).</p>
<h2>Qué datos tratamos</h2>
<p>Esta web no tiene formularios de registro. Lo que escribes en el buscador y en el comparador de ingresos se procesa en tu propio navegador y no se envía ni se guarda en ningún servidor.</p>
<p>El proveedor de alojamiento (Cloudflare) puede registrar datos técnicos de la conexión, como la dirección IP, por motivos de seguridad y funcionamiento del servicio, y ofrece estadísticas de visitas sin cookies.</p>
<h2>Publicidad y cookies</h2>
<p>Esta web se financia con publicidad de Google AdSense, un servicio de Google Ireland Limited. Google, como proveedor externo, utiliza cookies para mostrar anuncios, medir su rendimiento y, si lo aceptas, personalizarlos según tus visitas a esta y otras webs.</p>
<p>La primera vez que entras se muestra el mensaje de consentimiento de Google, donde puedes aceptar, rechazar o elegir qué finalidades permites. Base legal: tu consentimiento. Mientras no lo des, no se usan cookies de publicidad. Puedes cambiar tu elección con el enlace «Configurar cookies» del pie de página.</p>
<p>Más información: <a href="https://policies.google.com/technologies/ads?hl=es" rel="noopener">cómo usa Google las cookies en la publicidad</a>.</p>
<h2>Destinatarios</h2>
<p>No cedemos datos a terceros salvo obligación legal. Google y Cloudflare pueden tratar datos como proveedores del servicio; algunos pueden estar fuera del Espacio Económico Europeo, con las garantías previstas en el RGPD.</p>
<h2>Tus derechos</h2>
<p>Puedes ejercer tus derechos de acceso, rectificación, supresión y demás escribiendo a {t['email']}. También puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p></div>"""
    guardar("/sobre-los-datos/", pagina("/sobre-los-datos/", "Sobre los datos: el Atlas de Distribución de Renta del INE",
                                        "De dónde salen los datos de renta por municipio (INE), qué significa cada cifra y por qué son de hace dos años.",
                                        sobre, [("Sobre los datos", None)]))
    guardar("/aviso-legal/", pagina("/aviso-legal/", f"Aviso legal | {SITIO}", "Aviso legal y datos del titular de rentamedia.es.", aviso, [("Aviso legal", None)]))
    guardar("/privacidad/", pagina("/privacidad/", f"Política de privacidad | {SITIO}", "Política de privacidad y cookies de rentamedia.es.", privacidad, [("Privacidad", None)]))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Busca tu municipio desde la <a href="/">portada</a>.</p>', indexable=False))
    return ["/sobre-los-datos/", "/aviso-legal/", "/privacidad/"]


# ---------------------------------------------------------------- main

def main():
    t, T = cargar()
    municipios, con_dato, por_prov, anios = construir(t, T)
    if len(municipios) < MIN_PAGINAS:
        sys.exit(f"ERROR: solo {len(municipios)} municipios con datos (mínimo {MIN_PAGINAS}). No se publica.")
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    for f in ("style.css", "compartir.js", "buscar.js", "comparar.js"):
        shutil.copy(PLANTILLA / f, WEB / "assets" / f)
    for f in ("og.png", "favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        if (PLANTILLA / f).exists():
            shutil.copy(PLANTILLA / f, WEB / f)

    rutas, grandes = paginas_ranking(con_dato, por_prov, T, anios, list(municipios.values()))
    for m in municipios.values():
        guardar(ruta_mun(m), pagina_municipio(m, T, por_prov, len(con_dato), anios, t))
    rutas += paginas_barrios(municipios, t, T, anios)
    guardar("/comparar-renta/", pagina_comparador(anios))
    rutas.append("/comparar-renta/")
    rutas += paginas_legales(anios)
    guardar("/", portada(con_dato, grandes, T, anios, len(municipios)))
    grupos = indices_busqueda(municipios)

    hoy = date.today().isoformat()
    urls = ["/"] + rutas + [ruta_mun(m) for m in sorted(municipios.values(), key=lambda x: x["slug"])]
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"  <url><loc>{DOMINIO}{u}</loc><lastmod>{hoy}</lastmod></url>\n" for u in urls) + "</urlset>\n",
                                     encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /indice/\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    print(f"Web generada: {len(municipios)} municipios ({len(con_dato)} con renta de {anios[-1]}), {len(rutas)} páginas más, "
          f"{len(grupos)} ficheros de índice.")


if __name__ == "__main__":
    main()
