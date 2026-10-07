"""Genera una página estática por provincia con el precio de los carburantes.

La llama actualizar_carburantes.py después de descargar los datos. Las páginas llevan
los precios escritos en el HTML (sin depender de JavaScript) para que Google los lea.
Además actualiza la lista de provincias de precio-gasolina-hoy.html y el sitemap.xml
entre los comentarios <!-- PROVINCIAS:INICIO --> y <!-- PROVINCIAS:FIN -->.
"""

import re
import unicodedata
from html import escape
from pathlib import Path
from urllib.parse import quote

DOMINIO = "https://ahorrometro.es"
CARPETA = "gasolina"
DEPOSITO = 50  # litros
MAS_BARATAS = {"gasolina95": 10, "diesel": 10, "gasolina98": 5, "glp": 5}
MIN_GASOLINERAS_MUNICIPIO = 2

COMBUSTIBLES = [
    ("gasolina95", "Gasolina 95", "la gasolina 95"),
    ("diesel", "Diésel", "el diésel"),
    ("gasolina98", "Gasolina 98", "la gasolina 98"),
    ("glp", "GLP (autogás)", "el GLP"),
]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
# Canarias, Ceuta y Melilla tienen una fiscalidad distinta a la de la península
CANARIAS_CEUTA_MELILLA = {"35", "38", "51", "52"}


def slug(nombre):
    """'Santa Cruz de Tenerife' -> 'santa-cruz-de-tenerife', 'A Coruña' -> 'a-coruna'."""
    s = unicodedata.normalize("NFD", nombre.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def litro(p):
    return f"{p:.3f}".replace(".", ",")


def euros(x):
    entero, dec = f"{x:.2f}".split(".")
    return f"{int(entero):,}".replace(",", ".") + "," + dec + " €"


def centimos(diff):
    c = round(abs(diff) * 100, 1)
    texto = f"{c:.1f}".replace(".", ",").replace(",0", "")
    return f"{texto} céntimo{'s' if c != 1 else ''}"


def fecha(fecha_ministerio):
    """'07/10/2026 16:13:57' -> ('2026-10-07', 'miércoles, 7 de octubre de 2026', '16:13', 'octubre de 2026')."""
    import datetime
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})", fecha_ministerio or "")
    if not m:
        hoy = datetime.date.today()
        return hoy.isoformat(), f"{DIAS[hoy.weekday()]}, {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}", "", f"{MESES[hoy.month - 1]} de {hoy.year}"
    d = datetime.date(int(m[3]), int(m[2]), int(m[1]))
    return (d.isoformat(), f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}",
            f"{int(m[4])}:{m[5]}", f"{MESES[d.month - 1]} de {d.year}")


def mapa(g):
    if g.get("lat") is None or g.get("lon") is None:
        return ""
    return (f'<a href="https://www.google.com/maps/search/?api=1&amp;query={g["lat"]},{g["lon"]}" '
            f'target="_blank" rel="noopener">Cómo llegar</a>')


def ranking(resumen, clave):
    """Códigos de provincia ordenados de más barata a más cara para un combustible."""
    p = resumen["provincias"]
    return sorted((c for c in p if clave in p[c]), key=lambda c: p[c][clave]["media"])


def municipios(gasolineras):
    """Media de gasolina 95 y diésel por municipio (solo municipios con varias gasolineras)."""
    grupos = {}
    for g in gasolineras:
        grupos.setdefault(g["municipio"], []).append(g)
    filas = []
    for nombre, lista in grupos.items():
        g95 = [g["precios"]["gasolina95"] for g in lista if "gasolina95" in g["precios"]]
        die = [g["precios"]["diesel"] for g in lista if "diesel" in g["precios"]]
        if len(g95) >= MIN_GASOLINERAS_MUNICIPIO:
            filas.append((nombre, len(lista), sum(g95) / len(g95), sum(die) / len(die) if die else None))
    filas.sort(key=lambda f: f[2])
    return filas


def pagina(codigo, resumen, gasolineras):
    prov = resumen["provincias"][codigo]
    nombre = prov["nombre"]
    espana = resumen["espana"]
    iso, dia, hora, mes = fecha(resumen.get("fechaMinisterio"))
    url = f"{DOMINIO}/{CARPETA}/{prov['slug']}"
    n_prov = len(resumen["provincias"])
    e = escape

    # Tarjetas
    tarjetas = []
    for i, (clave, titulo, _) in enumerate(COMBUSTIBLES):
        s = prov.get(clave)
        if not s:
            tarjetas.append(f'<div class="gp-card"><p class="gp-name">{titulo}</p>'
                            f'<p class="gp-sub">No hay gasolineras con {titulo} en {e(nombre)}.</p></div>')
            continue
        calc = (f"../calculadoras/coste-viaje-coche?combustible={clave}&amp;precio={s['media']:.3f}"
                f"&amp;zona={quote(nombre)}")
        tarjetas.append(
            f'<div class="gp-card{" main" if i == 0 else ""}"><p class="gp-name">{titulo}</p>'
            f'<p class="gp-price">{litro(s["media"])}<small>€/L</small></p>'
            f'<p class="gp-sub">Desde {litro(s["min"])} €/L</p>'
            f'<p class="gp-sub">{s["n"]} gasolinera{"s" if s["n"] != 1 else ""}</p>'
            f'<a href="{calc}">Calcular un viaje →</a></div>')

    # Resumen en texto
    parrafos = []
    for clave, titulo, articulo in COMBUSTIBLES[:2]:
        s = prov.get(clave)
        if not s or clave not in espana:
            continue
        diff = s["media"] - espana[clave]["media"]
        puesto = ranking(resumen, clave).index(codigo) + 1
        comparacion = ("lo mismo que" if abs(diff) < 0.0005 else
                       f"{centimos(diff)} {'menos' if diff < 0 else 'más'} que")
        parrafos.append(
            f"Hoy {articulo} cuesta de media <strong>{litro(s['media'])} €/L</strong> en {e(nombre)}, "
            f"{comparacion} la media de España ({litro(espana[clave]['media'])} €/L). "
            f"Es la provincia número {puesto} de {n_prov} por precio de {titulo.lower()}, "
            f"siendo la 1 la más barata.")
    g95 = prov.get("gasolina95")
    if g95:
        ahorro = (g95["media"] - g95["min"]) * DEPOSITO
        parrafos.append(
            f"Llenando un depósito de {DEPOSITO} litros de gasolina 95 en la gasolinera más barata de la provincia "
            f"ahorras <strong class=\"gp-cheap\">{euros(ahorro)}</strong> frente al precio medio.")
    if codigo in CANARIAS_CEUTA_MELILLA:
        parrafos.append("Los carburantes aquí son más baratos que en la península porque no se aplican "
                        "el IVA ni el impuesto especial sobre hidrocarburos peninsulares.")

    # Tablas de gasolineras más baratas
    tablas = []
    for clave, titulo, _ in COMBUSTIBLES:
        lista = sorted((g for g in gasolineras if clave in g["precios"]), key=lambda g: g["precios"][clave])
        if not lista:
            continue
        filas = "".join(
            f'<tr><td class="gp-rank">{i}</td><td><strong>{e(g["rotulo"] or "Gasolinera")}</strong><br>'
            f'<span class="sub">{e(g["direccion"])} · {e(g["municipio"])}</span></td>'
            f'<td class="num gp-cheap">{litro(g["precios"][clave])} €</td><td>{mapa(g)}</td></tr>'
            for i, g in enumerate(lista[:MAS_BARATAS[clave]], 1))
        tablas.append(
            f"<section><h2>Gasolineras más baratas de {e(nombre)}: {titulo.lower() if clave != 'glp' else 'GLP'}</h2>"
            f'<div class="table-wrap"><table class="data"><thead><tr><th class="gp-rank">#</th><th>Gasolinera</th>'
            f'<th class="num">Precio</th><th>Mapa</th></tr></thead><tbody>{filas}</tbody></table></div></section>')

    # Municipios
    muni = municipios(gasolineras)
    seccion_muni = ""
    if len(muni) >= 3:
        filas = "".join(
            f'<tr><td>{e(n)}</td><td class="num">{cnt}</td><td class="num">{litro(m95)} €</td>'
            f'<td class="num">{litro(md) + " €" if md is not None else "—"}</td></tr>'
            for n, cnt, m95, md in muni[:10])
        seccion_muni = (
            f"<section><h2>Municipios de {e(nombre)} con la gasolina más barata</h2>"
            f"<p>Precio medio en los municipios con al menos {MIN_GASOLINERAS_MUNICIPIO} gasolineras, "
            f"ordenados por el precio de la gasolina 95.</p>"
            f'<div class="table-wrap"><table class="data"><thead><tr><th>Municipio</th><th class="num">Gasolineras</th>'
            f'<th class="num">Gasolina 95</th><th class="num">Diésel</th></tr></thead><tbody>{filas}</tbody></table></div></section>')

    # Otras provincias
    orden = sorted(resumen["provincias"], key=lambda c: slug(resumen["provincias"][c]["nombre"]))
    otras = "".join(
        f'<li><a href="{resumen["provincias"][c]["slug"]}">{e(resumen["provincias"][c]["nombre"])}</a></li>'
        for c in orden if c != codigo)

    media95 = litro(g95["media"]) if g95 else "—"
    diesel = prov.get("diesel")
    media_die = litro(diesel["media"]) if diesel else "—"
    descripcion = (f"Precio de la gasolina y el diésel hoy en {nombre}: gasolina 95 a {media95} €/L y diésel a "
                   f"{media_die} €/L de media. Las gasolineras más baratas de la provincia, con datos oficiales del Ministerio.")
    titulo_pagina = f"Precio de la gasolina hoy en {nombre}: gasolineras más baratas | Ahorrómetro"

    return PLANTILLA.format(
        titulo=e(titulo_pagina), descripcion=e(descripcion), url=url, nombre=e(nombre), iso=iso,
        dia=e(dia), hora=f", a las {hora}" if hora else "", mes=e(mes),
        breadcrumb=e(nombre), tarjetas="".join(tarjetas),
        parrafos="".join(f"<p>{p}</p>" for p in parrafos),
        tablas="".join(tablas), municipios=seccion_muni, otras=otras,
        og_titulo=e(f"Precio de la gasolina hoy en {nombre}"),
    )


def reemplazar_bloque(ruta, contenido):
    texto = ruta.read_text(encoding="utf-8")
    nuevo, n = re.subn(r"(<!-- PROVINCIAS:INICIO -->).*?(<!-- PROVINCIAS:FIN -->)",
                       lambda m: m[1] + contenido + m[2], texto, flags=re.S)
    if n != 1:
        raise SystemExit(f"No encuentro los marcadores PROVINCIAS en {ruta}")
    if nuevo != texto:
        ruta.write_text(nuevo, encoding="utf-8")


def generar(resumen, gasolineras, web):
    web = Path(web)
    carpeta = web / CARPETA
    carpeta.mkdir(parents=True, exist_ok=True)
    iso = fecha(resumen.get("fechaMinisterio"))[0]

    validas = set()
    for codigo, prov in resumen["provincias"].items():
        archivo = carpeta / f"{prov['slug']}.html"
        archivo.write_text(pagina(codigo, resumen, gasolineras.get(codigo, [])), encoding="utf-8")
        validas.add(archivo.name)
    for viejo in carpeta.glob("*.html"):  # páginas de provincias que ya no existen
        if viejo.name not in validas:
            viejo.unlink()

    orden = sorted(resumen["provincias"].values(), key=lambda p: slug(p["nombre"]))
    reemplazar_bloque(web / "precio-gasolina-hoy.html", "\n" + "\n".join(
        f'        <li><a href="{CARPETA}/{p["slug"]}">{escape(p["nombre"])}</a></li>' for p in orden) + "\n        ")
    reemplazar_bloque(web / "sitemap.xml", "\n" + "\n".join(
        f"  <url><loc>{DOMINIO}/{CARPETA}/{p['slug']}</loc><lastmod>{iso}</lastmod><priority>0.8</priority></url>"
        for p in orden) + "\n  ")


PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titulo}</title>
  <meta name="description" content="{descripcion}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#1f7a55">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ahorrómetro">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{og_titulo}">
  <meta property="og:description" content="{descripcion}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://ahorrometro.es/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  [{{"@context":"https://schema.org","@type":"WebPage","name":"{og_titulo}","url":"{url}","inLanguage":"es-ES","dateModified":"{iso}","author":{{"@type":"Person","name":"Albert Sanchez Guiu"}}}},
   {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Inicio","item":"https://ahorrometro.es/"}},{{"@type":"ListItem","position":2,"name":"Precio de la gasolina hoy","item":"https://ahorrometro.es/precio-gasolina-hoy"}},{{"@type":"ListItem","position":3,"name":"{breadcrumb}","item":"{url}"}}]}}]
  </script>
  <link rel="stylesheet" href="../assets/style.css?v=2">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <!-- ADSENSE: pega aquí el script de AdSense -->
</head>
<body>
<!-- Página generada automáticamente por scripts/paginas_provincia.py: no la edites a mano. -->
<header class="site-header">
  <div class="container">
    <a href="../" class="logo"><span class="logo-mark">€</span><span>Ahorró<span class="hl">metro</span></span></a>
    <button class="nav-toggle" aria-label="Abrir menú" aria-expanded="false">☰</button>
    <nav class="nav">
      <a href="../">Inicio</a>
      <a href="../#calculadoras">Calculadoras</a>
      <a href="../precio-luz-hoy">Precio de la luz</a>
      <a href="../precio-gasolina-hoy">Precio de la gasolina</a>
      <a href="../sobre-nosotros">Sobre nosotros</a>
      <a href="../contacto">Contacto</a>
    </nav>
  </div>
</header>

<main class="container">
  <nav class="breadcrumbs"><a href="../">Inicio</a> › <a href="../precio-gasolina-hoy">Precio de la gasolina</a> › {breadcrumb}</nav>
  <h1>Precio de la gasolina hoy en {nombre}</h1>
  <p class="lead">Precio medio por litro y gasolineras más baratas de {nombre}. Datos oficiales del Ministerio del {dia}{hora}, con impuestos incluidos.</p>
  <p class="updated">Se actualiza automáticamente dos veces al día.</p>

  <section class="gp-cards">{tarjetas}</section>

  <div class="content gp-resumen">{parrafos}</div>

  <div class="ad-slot"><!-- ADSENSE: anuncio bajo los precios -->Publicidad</div>

  {tablas}
  {municipios}

  <section class="affiliate">
    <h2>Gasta menos en cada depósito</h2>
    <div class="aff-grid">
      <a class="aff-item" href="https://www.amazon.es/s?k=compresor%20portatil%20neumaticos%20coche&amp;tag=albert671-21" rel="sponsored nofollow noopener" target="_blank"><span class="aff-icon">🛞</span><b>Compresor portátil para neumáticos</b><span class="aff-desc">Con las ruedas a la presión correcta el coche gasta menos.</span><span class="aff-cta">Ver precio en Amazon →</span></a>
      <a class="aff-item" href="https://www.amazon.es/s?k=obd2%20bluetooth%20diagnosis%20coche&amp;tag=albert671-21" rel="sponsored nofollow noopener" target="_blank"><span class="aff-icon">📟</span><b>Lector OBD2 Bluetooth</b><span class="aff-desc">Mide el consumo real de tu coche desde el móvil.</span><span class="aff-cta">Ver precio en Amazon →</span></a>
      <a class="aff-item" href="https://www.amazon.es/s?k=soporte%20movil%20coche&amp;tag=albert671-21" rel="sponsored nofollow noopener" target="_blank"><span class="aff-icon">📱</span><b>Soporte de móvil para el coche</b><span class="aff-desc">Lleva el navegador a la vista para llegar a la gasolinera barata.</span><span class="aff-cta">Ver precio en Amazon →</span></a>
    </div>
    <p class="aff-note">Enlaces de afiliado: si compras a través de ellos, recibimos una pequeña comisión sin coste extra para ti.</p>
  </section>

  <div class="content">
    <h2>Cómo calculamos estos precios</h2>
    <p>Todas las gasolineras de España deben comunicar sus precios al Ministerio para la Transición Ecológica y el Reto Demográfico. Dos veces al día descargamos esos datos y calculamos la media de {nombre}, contando solo las gasolineras abiertas al público general. Cada gasolinera cuenta lo mismo en la media, venda mucho o poco.</p>
    <p>Para saber cuánto te costará un viaje con estos precios, usa el enlace «Calcular un viaje» de cada combustible: abre la <a href="../calculadoras/coste-viaje-coche">calculadora del coste de un viaje en coche</a> con el precio medio de {nombre} ya puesto.</p>
    <h2>Precio de la gasolina en otras provincias</h2>
    <ul class="gp-provincias">{otras}</ul>
    <p class="note">Fuente: Ministerio para la Transición Ecológica y el Reto Demográfico, Geoportal de gasolineras. Los precios pueden haber cambiado desde la última actualización; confírmalos en el surtidor.</p>
  </div>
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div><h4>Ahorrómetro</h4><p>Calculadoras gratuitas para tomar mejores decisiones en casa y ahorrar dinero cada mes.</p></div>
      <div><h4>Calculadoras</h4><ul>
        <li><a href="../calculadoras/consumo-electrico">Consumo eléctrico</a></li>
        <li><a href="../calculadoras/placas-solares">Placas solares</a></li>
        <li><a href="../calculadoras/coste-viaje-coche">Viaje en coche</a></li>
        <li><a href="../calculadoras/pintura">Pintura</a></li>
      </ul></div>
      <div><h4>Información</h4><ul>
        <li><a href="../sobre-nosotros">Sobre nosotros</a></li>
        <li><a href="../contacto">Contacto</a></li>
        <li><a href="../aviso-legal">Aviso legal</a></li>
        <li><a href="../politica-privacidad">Política de privacidad</a></li>
        <li><a href="../politica-cookies">Política de cookies</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">© 2026 Ahorrómetro. Los resultados son orientativos y no constituyen asesoramiento profesional. Como Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.</div>
  </div>
</footer>

<div class="cookie-banner" id="cookie-banner" role="dialog" aria-label="Aviso de cookies">
  <p>Usamos cookies propias y de terceros (como Google) para analizar el uso de la web y mostrar publicidad. Puedes aceptarlas o rechazarlas. Más información en nuestra <a href="../politica-cookies">política de cookies</a>.</p>
  <div class="actions">
    <button class="btn btn-sm" data-consent="accepted">Aceptar</button>
    <button class="btn btn-sm btn-ghost" data-consent="rejected">Rechazar</button>
  </div>
</div>
<script src="../assets/main.js?v=2"></script>
</body>
</html>
"""
