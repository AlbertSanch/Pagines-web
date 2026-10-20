"""Gasolineras baratas cerca de mí y gasolineras low cost.

La llama actualizar_carburantes.py con todas las gasolineras ya descargadas del Ministerio. Genera:
  - ahorrometro/datos/gasolineras.json: todas las gasolineras (marca, dirección, precios, horario
    y coordenadas) para el buscador por ubicación, que funciona en el navegador.
  - ahorrometro/gasolineras-baratas-cerca-de-mi.html: el buscador y, escritas en el HTML para que
    Google las lea, las gasolineras más baratas de España y de cada provincia.
  - ahorrometro/gasolineras-low-cost.html: qué marcas son más baratas, medido con los datos del día.

«Low cost» no es una etiqueta que pongamos a ojo: comparamos cada gasolinera con la media de su
provincia y llamamos low cost a las marcas que, de media, están al menos LOW_COST céntimos por
debajo, con un mínimo de MIN_MARCA gasolineras. Así no influye que una marca esté en provincias
más baratas o más caras.
"""

import json
import re
import unicodedata
from html import escape
from pathlib import Path

from paginas_provincia import CANARIAS_CEUTA_MELILLA, DOMINIO, euros, fecha, litro, mapa

MIN_MARCA = 10          # gasolineras mínimas para entrar en la comparación de marcas
LOW_COST = 0.05         # €/L por debajo de la media de su provincia (gasolina 95 y diésel juntos)
MAS_BARATAS_ESPANA = 15
GENERICOS = {"", "SIN ROTULO", "SIN ROTULO.", "NO TIENE", "NINGUNO", "INDEPENDIENTE", "GASOLINERA",
             "ESTACION DE SERVICIO", "E.S.", "ES", "SIN MARCA", "BLANCA", "N/A", "OTROS"}
CAMPOS = ["marca", "direccion", "municipio", "cp", "provincia", "lat", "lon", "gasolina95", "gasolina98",
          "diesel", "glp", "horario", "lowcost"]


def clave_marca(rotulo):
    s = unicodedata.normalize("NFD", rotulo.upper())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]+", " ", s)).strip()


def marcas(gasolineras, resumen):
    """Ranking de marcas por diferencia media con su provincia (península y Baleares)."""
    grupos = {}
    for codigo, lista in gasolineras.items():
        if codigo in CANARIAS_CEUTA_MELILLA:  # otros impuestos: no se comparan con la península
            continue
        prov = resumen["provincias"][codigo]
        for g in lista:
            clave = clave_marca(g["rotulo"])
            if clave in GENERICOS:
                continue
            m = grupos.setdefault(clave, {"nombres": {}, "n": 0, "dif": [], "gasolina95": [], "diesel": []})
            m["n"] += 1
            m["nombres"][g["rotulo"]] = m["nombres"].get(g["rotulo"], 0) + 1
            for comb in ("gasolina95", "diesel"):
                if comb in g["precios"] and comb in prov:
                    m["dif"].append(g["precios"][comb] - prov[comb]["media"])
                    m[comb].append(g["precios"][comb])
    lista = []
    for clave, m in grupos.items():
        if m["n"] < MIN_MARCA or not m["dif"]:
            continue
        dif = sum(m["dif"]) / len(m["dif"])
        lista.append({
            "clave": clave,
            "nombre": max(m["nombres"], key=m["nombres"].get),
            "n": m["n"],
            "dif": round(dif, 3),
            "gasolina95": round(sum(m["gasolina95"]) / len(m["gasolina95"]), 3) if m["gasolina95"] else None,
            "diesel": round(sum(m["diesel"]) / len(m["diesel"]), 3) if m["diesel"] else None,
            "lowcost": dif <= -LOW_COST,
        })
    lista.sort(key=lambda m: m["dif"])
    return lista


def datos_json(gasolineras, lowcost):
    filas = []
    for codigo, lista in gasolineras.items():
        for g in lista:
            if g.get("lat") is None or g.get("lon") is None:
                continue
            p = g["precios"]
            filas.append([g["rotulo"], g["direccion"], g["municipio"], g.get("cp", ""), codigo,
                          round(g["lat"], 4), round(g["lon"], 4),
                          p.get("gasolina95"), p.get("gasolina98"), p.get("diesel"), p.get("glp"),
                          g.get("horario", ""), 1 if clave_marca(g["rotulo"]) in lowcost else 0])
    return filas


def dif_texto(d):
    c = round(abs(d) * 100, 1)
    t = f"{c:.1f}".replace(".", ",").replace(",0", "")
    return f"{t} cént. {'menos' if d < 0 else 'más'}"


def tabla_gasolineras(lista, clave, resumen, con_provincia=True):
    filas = "".join(
        f'<tr><td class="gp-rank">{i}</td><td><strong>{escape(g["rotulo"] or "Gasolinera")}</strong>'
        f'<span class="sub">{escape(g["direccion"])} · {escape(g["municipio"])}'
        f'{" (" + escape(resumen["provincias"][g["_prov"]]["nombre"]) + ")" if con_provincia else ""}</span></td>'
        f'<td class="num gp-cheap">{litro(g["precios"][clave])} €</td><td>{mapa(g)}</td></tr>'
        for i, g in enumerate(lista, 1))
    return (f'<div class="table-wrap"><table class="data"><thead><tr><th class="gp-rank">#</th><th>Gasolinera</th>'
            f'<th class="num">Precio</th><th>Mapa</th></tr></thead><tbody>{filas}</tbody></table></div>')


def pagina_cerca(resumen, gasolineras, ranking, iso, dia, hora):
    todas = [dict(g, _prov=c) for c, lista in gasolineras.items() if c not in CANARIAS_CEUTA_MELILLA for g in lista]
    total = sum(len(lista) for lista in gasolineras.values())
    secciones = []
    for clave, nombre in (("gasolina95", "gasolina 95"), ("diesel", "diésel")):
        lista = sorted((g for g in todas if clave in g["precios"]), key=lambda g: g["precios"][clave])[:MAS_BARATAS_ESPANA]
        secciones.append(f"<section><h2>Las {MAS_BARATAS_ESPANA} gasolineras más baratas de España hoy: {nombre}</h2>"
                         f"<p>En la península y Baleares (Canarias, Ceuta y Melilla tienen otros impuestos).</p>"
                         f"{tabla_gasolineras(lista, clave, resumen)}</section>")
    provs = sorted(resumen["provincias"].items(), key=lambda x: x[1]["slug"])
    filas = "".join(
        f'<tr><td><a href="gasolina/{p["slug"]}">{escape(p["nombre"])}</a></td>'
        f'<td class="num">{litro(p["gasolina95"]["min"]) + " €" if "gasolina95" in p else "—"}</td>'
        f'<td class="num">{litro(p["diesel"]["min"]) + " €" if "diesel" in p else "—"}</td></tr>'
        for _, p in provs)
    low = [m for m in ranking if m["lowcost"]]
    preguntas = [
        ("¿Cómo encuentro la gasolinera más barata cerca de mí?",
         "Pulsa «Buscar cerca de mí» y permite que el navegador use tu ubicación, o escribe tu código postal o tu municipio. "
         "Verás las gasolineras de alrededor ordenadas por precio, con la distancia y un enlace para llegar."),
        ("¿Se guarda mi ubicación?",
         "No. La búsqueda se hace en tu propio navegador con la lista de gasolineras: tu ubicación no se envía a ningún servidor."),
        ("¿Cada cuánto se actualizan los precios?",
         "Dos veces al día, con los precios que las gasolineras comunican al Ministerio para la Transición Ecológica. "
         "Pueden haber cambiado desde entonces: confírmalos en el surtidor."),
        ("¿Qué gasolineras son low cost?",
         ("Hoy, según los datos del Ministerio, las marcas más baratas respecto a la media de su provincia son "
          + ", ".join(m["nombre"] for m in low[:6]) + ". Mira la comparación completa en la página de gasolineras low cost.")
         if low else "Mira la comparación de marcas en la página de gasolineras low cost."),
    ]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in preguntas]}
    cuerpo = f"""<nav class="breadcrumbs"><a href="./">Inicio</a> › <a href="precio-gasolina-hoy">Precio de la gasolina</a> › Gasolineras baratas cerca de mí</nav>
  <h1>Gasolineras baratas cerca de mí</h1>
  <p class="lead">Encuentra la gasolinera más barata cerca de ti, ordenada por precio y con la distancia. Precios oficiales del Ministerio del {escape(dia)}{hora}, de las {f'{total:,}'.replace(',', '.')} gasolineras de España.</p>

  <section class="gc-buscador" id="buscador">
    <div class="gc-fila">
      <button type="button" class="btn" id="gc-ubicacion">📍 Buscar cerca de mí</button>
      <span class="gc-o">o</span>
      <form id="gc-form" class="gc-form" role="search"><label class="sr-only" for="gc-lugar">Código postal o municipio</label>
        <input id="gc-lugar" type="search" placeholder="Código postal o municipio" autocomplete="postal-code">
        <button type="submit" class="btn btn-ghost">Buscar</button></form>
    </div>
    <div class="gp-controls">
      <div class="gp-switch" role="group" aria-label="Combustible">
        <button type="button" data-comb="gasolina95" aria-pressed="true">Gasolina 95</button>
        <button type="button" data-comb="diesel" aria-pressed="false">Diésel</button>
        <button type="button" data-comb="gasolina98" aria-pressed="false">Gasolina 98</button>
        <button type="button" data-comb="glp" aria-pressed="false">GLP</button>
      </div>
      <label>Distancia <select id="gc-radio"><option value="5">5 km</option><option value="10" selected>10 km</option><option value="25">25 km</option><option value="50">50 km</option></select></label>
      <label><input type="checkbox" id="gc-low"> Solo low cost</label>
      <label><input type="checkbox" id="gc-24"> Abiertas 24 h</label>
    </div>
    <div id="gc-resultado" aria-live="polite"><p class="gp-status">Pulsa «Buscar cerca de mí» o escribe tu código postal para ver las gasolineras más baratas de tu zona.</p></div>
  </section>

  {''.join(secciones)}

  <section><h2>La gasolinera más barata de cada provincia</h2>
  <p>Precio más bajo de hoy en cada provincia. Pulsa en la tuya para ver la lista completa de gasolineras baratas.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th><th class="num">Gasolina 95 desde</th><th class="num">Diésel desde</th></tr></thead><tbody>{filas}</tbody></table></div></section>

  <div class="content">
    <h2>Cómo funciona</h2>
    <p>Todas las gasolineras de España tienen que comunicar sus precios al Ministerio para la Transición Ecológica y el Reto Demográfico. Dos veces al día descargamos esa lista y el buscador calcula, en tu propio navegador, qué gasolineras tienes alrededor y cuál es la más barata. Tu ubicación no sale de tu móvil u ordenador.</p>
    <p>Las gasolineras marcadas como <strong>low cost</strong> son las de las marcas que hoy están de media al menos {round(LOW_COST * 100)} céntimos por debajo de la media de su provincia. Mira <a href="gasolineras-low-cost">qué marcas son low cost y cuánto ahorran</a>.</p>
    <h2>Preguntas frecuentes</h2>
    {''.join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in preguntas)}
    <p class="note">Fuente: Ministerio para la Transición Ecológica y el Reto Demográfico, Geoportal de gasolineras. Solo gasolineras de venta al público general.</p>
  </div>"""
    return pagina("gasolineras-baratas-cerca-de-mi", "Gasolineras baratas cerca de mí: la más barata hoy",
                  "Encuentra la gasolinera más barata cerca de ti con los precios oficiales de hoy: ordenadas por precio y distancia, con gasolina 95, diésel y low cost.",
                  cuerpo, iso, "Gasolineras baratas cerca de mí", [faq_ld], '<script src="assets/gasolineras.js?v=1" defer></script>')


def pagina_low_cost(resumen, gasolineras, ranking, iso, dia, hora):
    low = [m for m in ranking if m["lowcost"]]
    filas = "".join(
        f'<tr{" class=sel" if m["lowcost"] else ""}><td>{escape(m["nombre"])}{" <span class=gc-badge>low cost</span>" if m["lowcost"] else ""}</td>'
        f'<td class="num">{m["n"]}</td><td class="num {"gp-cheap" if m["dif"] < 0 else "gp-dear"}">{dif_texto(m["dif"])}</td>'
        f'<td class="num">{litro(m["gasolina95"]) + " €" if m["gasolina95"] else "—"}</td>'
        f'<td class="num">{litro(m["diesel"]) + " €" if m["diesel"] else "—"}</td></tr>'
        for m in ranking)
    claves_low = {m["clave"] for m in low}
    filas_prov = []
    for codigo, p in sorted(resumen["provincias"].items(), key=lambda x: x[1]["slug"]):
        cands = [g for g in gasolineras.get(codigo, []) if clave_marca(g["rotulo"]) in claves_low and "gasolina95" in g["precios"]]
        if not cands:
            continue
        g = min(cands, key=lambda g: g["precios"]["gasolina95"])
        ahorro = (p["gasolina95"]["media"] - g["precios"]["gasolina95"]) * 50 if "gasolina95" in p else None
        filas_prov.append(
            f'<tr><td><a href="gasolina/{p["slug"]}">{escape(p["nombre"])}</a></td><td><strong>{escape(g["rotulo"])}</strong>'
            f'<span class="sub">{escape(g["direccion"])} · {escape(g["municipio"])}</span></td>'
            f'<td class="num gp-cheap">{litro(g["precios"]["gasolina95"])} €</td>'
            f'<td class="num">{euros(ahorro) if ahorro and ahorro > 0 else "—"}</td></tr>')
    ejemplo = low[0] if low else None
    intro = (f"Hoy la marca más barata es <strong>{escape(ejemplo['nombre'])}</strong>: sus gasolineras están de media "
             f"{dif_texto(ejemplo['dif'])} por litro que la media de su provincia." if ejemplo else "")
    cuerpo = f"""<nav class="breadcrumbs"><a href="./">Inicio</a> › <a href="precio-gasolina-hoy">Precio de la gasolina</a> › Gasolineras low cost</nav>
  <h1>Gasolineras low cost: las marcas más baratas hoy</h1>
  <p class="lead">Qué marcas de gasolineras son de verdad más baratas, medido con los precios oficiales del Ministerio del {escape(dia)}{hora}. {intro}</p>
  <p><a class="btn" href="gasolineras-baratas-cerca-de-mi?lowcost=1#buscador">📍 Ver gasolineras low cost cerca de mí</a></p>

  <section><h2>Ranking de marcas de gasolineras por precio</h2>
  <p>Para cada marca con al menos {MIN_MARCA} gasolineras en la península y Baleares, comparamos el precio de cada gasolinera (gasolina 95 y diésel) con la media de su provincia y hacemos la media. Así no cuenta que una marca esté en zonas más caras o más baratas. Marcamos como <strong>low cost</strong> las que están al menos {round(LOW_COST * 100)} céntimos por litro por debajo.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Marca</th><th class="num">Gasolineras</th><th class="num">Frente a su provincia</th><th class="num">Gasolina 95 (media)</th><th class="num">Diésel (media)</th></tr></thead><tbody>{filas}</tbody></table></div></section>

  {f'''<section><h2>La gasolinera low cost más barata de cada provincia</h2>
  <p>Gasolina 95. El ahorro es lo que te ahorras al llenar un depósito de 50 litros frente al precio medio de la provincia.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th><th>Gasolinera</th><th class="num">Precio</th><th class="num">Ahorro (50 L)</th></tr></thead><tbody>{"".join(filas_prov)}</tbody></table></div></section>''' if filas_prov else ''}

  <div class="content">
    <h2>¿Qué es una gasolinera low cost?</h2>
    <p>Son gasolineras que venden más barato porque reducen costes: casi siempre son de autoservicio, sin tienda ni personal en la pista, y pagas en el propio surtidor con tarjeta. El combustible cumple las mismas especificaciones oficiales que el de cualquier otra gasolinera.</p>
    <p>No ponemos la etiqueta a ojo: la calculamos cada día con los precios reales, así que si una marca deja de ser barata, deja de salir como low cost.</p>
    <h2>Consejos para pagar menos</h2>
    <ul>
      <li>Compara antes de salir con el <a href="gasolineras-baratas-cerca-de-mi">buscador de gasolineras baratas cerca de ti</a>: entre la más cara y la más barata de una misma ciudad suele haber más de 20 céntimos por litro.</li>
      <li>Mira el <a href="precio-gasolina-hoy">precio medio de hoy en tu provincia</a> para saber si un precio es bueno.</li>
      <li>Calcula cuánto te cuesta un trayecto con la <a href="calculadoras/coste-viaje-coche">calculadora del coste de un viaje en coche</a>.</li>
    </ul>
    <p class="note">Fuente: Ministerio para la Transición Ecológica y el Reto Demográfico, Geoportal de gasolineras. Canarias, Ceuta y Melilla no entran en la comparación porque tienen otros impuestos. Los nombres de las marcas son los que cada gasolinera comunica al Ministerio.</p>
  </div>"""
    return pagina("gasolineras-low-cost", "Gasolineras low cost: las marcas más baratas hoy",
                  "Qué marcas de gasolineras son de verdad más baratas hoy, medido con los precios oficiales: ranking de marcas y la gasolinera low cost más barata de cada provincia.",
                  cuerpo, iso, "Gasolineras low cost")


def pagina(ruta, titulo, descripcion, cuerpo, iso, miga, extra_ld=None, scripts=""):
    url = f"{DOMINIO}/{ruta}"
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": titulo, "url": url, "inLanguage": "es-ES", "dateModified": iso},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMINIO}/"},
              {"@type": "ListItem", "position": 2, "name": "Precio de la gasolina hoy", "item": f"{DOMINIO}/precio-gasolina-hoy"},
              {"@type": "ListItem", "position": 3, "name": miga, "item": url}]}] + (extra_ld or [])
    plantilla = (Path(__file__).resolve().parent.parent / "ahorrometro" / "sobre-nosotros.html").read_text(encoding="utf-8")
    cabeza, resto = plantilla.split("<main", 1)
    pie = resto.split("</main>", 1)[1]
    cabeza = re.sub(r"<title>.*?</title>", f"<title>{escape(titulo)}</title>", cabeza)
    cabeza = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m[1] + escape(descripcion), cabeza)
    cabeza = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m[1] + escape(descripcion), cabeza)
    cabeza = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m[1] + escape(titulo), cabeza)
    cabeza = cabeza.replace("https://ahorrometro.es/sobre-nosotros", url)
    cabeza = cabeza.replace("</head>", f'  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>')
    pie = pie.replace("</body>", f"{scripts}\n</body>")
    aviso = "<!-- Página generada automáticamente por scripts/paginas_gasolineras.py: no la edites a mano. -->\n"
    return cabeza.replace("<body>", "<body>\n" + aviso, 1) + f'<main class="container">\n  {cuerpo}\n</main>' + pie


def generar(resumen, gasolineras, web):
    web = Path(web)
    iso, dia, hora, _ = fecha(resumen.get("fechaMinisterio"))
    hora = f", a las {hora}" if hora else ""
    ranking = marcas(gasolineras, resumen)
    lowcost = {m["clave"] for m in ranking if m["lowcost"]}
    (web / "datos" / "gasolineras.json").write_text(json.dumps(
        {"fecha": resumen.get("fechaMinisterio", ""), "campos": CAMPOS, "gasolineras": datos_json(gasolineras, lowcost)},
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (web / "gasolineras-baratas-cerca-de-mi.html").write_text(pagina_cerca(resumen, gasolineras, ranking, iso, dia, hora), encoding="utf-8")
    (web / "gasolineras-low-cost.html").write_text(pagina_low_cost(resumen, gasolineras, ranking, iso, dia, hora), encoding="utf-8")
    sitemap = web / "sitemap.xml"
    if "<!-- GASOLINERAS:INICIO -->" in sitemap.read_text(encoding="utf-8"):
        texto = sitemap.read_text(encoding="utf-8")
        nuevo = re.sub(r"(<!-- GASOLINERAS:INICIO -->).*?(<!-- GASOLINERAS:FIN -->)", lambda m: m[1] + "\n" + "\n".join(
            f"  <url><loc>{DOMINIO}/{r}</loc><lastmod>{iso}</lastmod><priority>0.9</priority></url>"
            for r in ("gasolineras-baratas-cerca-de-mi", "gasolineras-low-cost")) + "\n  " + m[2], texto, flags=re.S)
        sitemap.write_text(nuevo, encoding="utf-8")
    print(f"gasolineras.json: {sum(len(v) for v in gasolineras.values())} gasolineras · "
          f"marcas low cost: {', '.join(m['nombre'] for m in ranking if m['lowcost']) or 'ninguna'}")
