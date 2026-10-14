"""Genera la web estática de festivosde.es a partir de festivos/data/ (lo crea procesar.py).

Páginas:
  /                              portada: buscador, próximos festivos nacionales y comunidades
  /<municipio>/                  festivos de cada municipio (nacionales, autonómicos y locales) de cada año
  /comunidad/<slug>/             calendario laboral de la comunidad y sus provincias
  /provincia/<slug>/             festivos locales de todos sus municipios
  /calendario-laboral-<año>/     calendario de toda España: qué fiesta tiene cada comunidad
  /sobre-los-datos/, /aviso-legal/, /privacidad/

Todo sale del BOE y de los boletines oficiales de cada comunidad. Si un municipio todavía no tiene
sus fiestas locales publicadas, se dice así: nunca se inventa ni se supone una fecha.

Uso: python festivos/scripts/generar_web.py
"""
import datetime as dt
import json
import re
import shutil
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import COMUNIDADES, DATA, PROVINCIAS, MESES, DIAS, municipios, slug  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
PLANTILLA = RAIZ / "plantilla"
DOMINIO = "https://festivosde.es"
SITIO = "Festivos de"
VERSION = "1"
HOY = dt.date.today()
ADSENSE = "ca-pub-8810566450749484"  # la misma cuenta que las otras webs
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
RESERVADOS = {"comunidad", "provincia", "assets", "sobre-los-datos", "aviso-legal", "privacidad", "indice"}
TIPOS = {"nacional": "Nacional", "autonomico": "Autonómica", "local": "Local"}
# Val d'Aran: el BOE recoge una sustitución solo para este territorio
ARAN = {"Arres", "Bausen", "Bossòst", "Canejan", "Bòrdes, Es", "Les", "Naut Aran", "Vielha e Mijaran", "Vilamòs"}

ARTICULO = re.compile(r"^(.*), (el|la|los|las|l'|lo|les|els|o|a|os|as|es|sa|ses|s')$", re.I)


def bonito(nombre_ine):
    """«Rozas de Madrid, Las» → «Las Rozas de Madrid»; «Elx/Elche» → «Elx / Elche»."""
    partes = []
    for p in nombre_ine.split("/"):
        p = p.strip()
        m = ARTICULO.match(p)
        if m:
            art = m.group(2)
            p = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
        partes.append(p[:1].upper() + p[1:])
    return " / ".join(partes)


def corto(nombre_ine):
    """Nombre para títulos: la parte en castellano de los bilingües si la hay («Elx/Elche» → «Elche»)."""
    partes = [p.strip() for p in bonito(nombre_ine).split("/")]
    return partes[-1] if len(partes) > 1 else partes[0]


def fecha_larga(f, con_dia=True):
    d = dt.date.fromisoformat(f) if isinstance(f, str) else f
    texto = f"{d.day} de {MESES[d.month - 1]}"
    return f"{DIAS[d.weekday()]} {texto}" if con_dia else texto


def cargar():
    datos = {}
    for ruta in sorted(DATA.glob("festivos_*.json")):
        d = json.loads(ruta.read_text(encoding="utf-8"))
        datos[d["anio"]] = d
    if not datos:
        sys.exit("No hay datos: ejecuta antes procesar.py")
    return datos


def festivos_de(datos, anio, cod):
    """Lista ordenada de festivos de un municipio en un año: [{f, n, t}]."""
    d = datos[anio]
    ccaa = PROVINCIAS[cod[:2]][1]
    lista = [dict(x) for x in d["nacionales_autonomicos"].get(ccaa, [])]
    for x in d.get("comunes", {}).get(cod[:2], []):  # p. ej. San Prudencio en Álava, Día de Navarra
        lista.append({"f": x["f"], "n": x["n"] or "Fiesta local", "t": "local"})
    for x in d["locales"].get(cod, []):
        lista.append({"f": x["f"], "n": x["n"] or "Fiesta local", "t": "local"})
    return sorted(lista, key=lambda x: x["f"])


def tiene_locales(datos, anio, cod):
    return cod in datos[anio]["locales"]


def puentes(lista):
    """Festivos que caen en martes o jueves (puente) y en lunes o viernes (fin de semana largo)."""
    res = []
    for x in lista:
        d = dt.date.fromisoformat(x["f"])
        if d.weekday() == 1:
            res.append((x, "puente", "si coges libre el lunes anterior"))
        elif d.weekday() == 3:
            res.append((x, "puente", "si coges libre el viernes siguiente"))
        elif d.weekday() in (0, 4):
            res.append((x, "largo", "fin de semana de tres días"))
    return res


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
        migas_html = f'<nav class="migas" aria-label="Ruta">{" › ".join(partes)}</nav>'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{url}">
{'' if indexable else '<meta name="robots" content="noindex">'}
<meta name="theme-color" content="#c2410c">
<meta property="og:type" content="website">
<meta property="og:site_name" content="festivosde.es">
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
<header class="cabecera">
  <div class="contenedor">
    <a href="/" class="logo"><span class="logo-hoja"><b>{HOY.day}</b><i>{MESES[HOY.month - 1][:3]}</i></span><span>festivos<span class="de">de</span>.es</span></a>
    <nav class="menu">
      <a href="/calendario-laboral-{max(ANIOS)}/">Calendario {max(ANIOS)}</a>
      <a href="/calendario-laboral-{min(ANIOS)}/">Calendario {min(ANIOS)}</a>
      <a href="/#comunidades">Comunidades</a>
    </nav>
  </div>
</header>
<main class="contenedor">
{migas_html}
{cuerpo}
</main>
<footer class="pie">
  <div class="contenedor">
    <p><strong>festivosde.es</strong> reúne los días festivos de cada municipio de España a partir del Boletín Oficial del Estado y de los boletines oficiales de cada comunidad autónoma.</p>
    <div class="enlaces"><a href="/">Buscar un municipio</a>{''.join(f'<a href="/calendario-laboral-{a}/">Calendario laboral {a}</a>' for a in ANIOS)}<a href="/#comunidades">Comunidades autónomas</a><a href="/sobre-los-datos/">De dónde salen los datos</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad y cookies</a>{CONFIGURAR_COOKIES}</div>
    <p>Las fechas se toman de las publicaciones oficiales. Si ves un error, escríbenos a {TITULAR['email']}.</p>
  </div>
</footer>
<script src="/assets/app.js?v={VERSION}" defer></script>
{scripts}
</body>
</html>
"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


def faq_ld(preguntas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", r)}} for q, r in preguntas]}


def faq_html(preguntas):
    return "".join(f"<details><summary>{escape(q)}</summary><p>{r}</p></details>" for q, r in preguntas)


def tabla_festivos(lista):
    filas = "".join(
        f'<tr class="t-{x["t"]}"><td><time datetime="{x["f"]}">{fecha_larga(x["f"], False)}</time></td>'
        f'<td>{DIAS[dt.date.fromisoformat(x["f"]).weekday()]}</td><td>{escape(x["n"])}</td>'
        f'<td><span class="marca {x["t"]}">{TIPOS[x["t"]]}</span></td></tr>' for x in lista)
    return ('<div class="tabla-envoltorio"><table class="festivos"><thead><tr><th>Fecha</th><th>Día</th><th>Fiesta</th>'
            f'<th>Ámbito</th></tr></thead><tbody>{filas}</tbody></table></div>')


def bloque_puentes(lista, anio):
    p = puentes(lista)
    if not p:
        return ""
    items = "".join(f'<li><b>{fecha_larga(x["f"])}</b> · {escape(x["n"])}: <span class="{tipo}">{texto}</span></li>'
                    for x, tipo, texto in p)
    return f'<h3>Puentes y fines de semana largos de {anio}</h3><ul class="puentes">{items}</ul>'


def fuentes_html(datos, anio, ccaa, con_locales):
    d = datos[anio]
    partes = [f'<a href="{d["boe"]["url"]}" rel="nofollow noopener">{escape(d["boe"]["titulo"])}</a> (BOE de {fecha_larga(d["boe"]["publicado"], False)} de {d["boe"]["publicado"][:4]})']
    f = d["fuentes"].get(ccaa)
    if con_locales and f:
        partes.append(f'<a href="{escape(f["url"])}" rel="nofollow noopener">fiestas locales de {escape(COMUNIDADES[ccaa][0])} para {anio}</a>'
                      + (f' ({escape(f["titulo"])})' if f.get("titulo") else ""))
    return '<p class="fuente">Fuente: ' + "; ".join(partes) + ".</p>"


def notas_html(datos, anio, cod):
    ccaa = PROVINCIAS[cod[:2]][1]
    notas = []
    for t in datos[anio]["notas"].get(ccaa, []):
        if ccaa == "cataluna" and "Arán" in t and municipios()[cod] not in ARAN:
            continue
        notas.append(t)
    return "".join(f'<p class="nota">{escape(t)}</p>' for t in notas)


# ---------------------------------------------------------------- páginas de municipio

def pagina_municipio(datos, cod, m, vecinos):
    ccaa = PROVINCIAS[cod[:2]][1]
    prov_nombre = PROVINCIAS[cod[:2]][0]
    ccaa_nombre = COMUNIDADES[ccaa][0]
    N = m["nombre"]
    secciones, preguntas, embebido = [], [], {}
    for anio in ANIOS:
        lista = festivos_de(datos, anio, cod)
        embebido[anio] = [[x["f"], x["n"], x["t"][0]] for x in lista]
        locales = [x for x in lista if x["t"] == "local"]
        aviso_varias = ""
        if len(datos[anio]["locales"].get(cod, [])) > 2:
            aviso_varias = (f'<p class="nota">En {escape(N)} algunas fiestas locales solo se celebran en determinadas parroquias, '
                            'pedanías o núcleos. Comprueba en el boletín oficial enlazado abajo cuáles se aplican en tu localidad.</p>')
        if tiene_locales(datos, anio, cod):
            loc_txt = " y ".join(f"el {fecha_larga(x['f'])}" + (f" ({escape(x['n'])})" if x["n"] != "Fiesta local" else "") for x in locales)
            resumen = f"<p>Las <strong>fiestas locales de {escape(N)} en {anio}</strong> son {loc_txt}. En total, {len(lista)} días festivos en el año.</p>"
            preguntas.append((f"¿Cuáles son las fiestas locales de {N} en {anio}?",
                              f"Las fiestas locales de {escape(N)} en {anio} son " + " y ".join(fecha_larga(x["f"]) for x in locales)
                              + f". Además, hay {len(lista) - len(locales)} festivos nacionales y de {escape(ccaa_nombre)}."))
        else:
            resto = datos[anio]["fuentes"].get(ccaa, {}).get("resto")
            if resto:
                pendiente = (f"El boletín oficial de {escape(ccaa_nombre)} no indica fechas concretas para {escape(N)}: dice «{escape(resto)}». "
                             "Consulta las fechas exactas en tu ayuntamiento.")
            else:
                pendiente = (f"Las dos fiestas locales de {escape(N)} para {anio} todavía no están publicadas en nuestros datos. "
                             f"Las aprueba cada año el boletín oficial de {escape(ccaa_nombre)} y las añadiremos en cuanto salgan.")
            resumen = f'<p class="pendiente">{pendiente}</p><p>De momento, estos son los {len(lista)} festivos nacionales y de {escape(ccaa_nombre)} que también se celebran en {escape(N)}:</p>'
        secciones.append(f"""<section class="anio" id="festivos-{anio}">
<h2>Festivos de {escape(N)} en {anio}</h2>
{resumen}
{aviso_varias}
{tabla_festivos(lista)}
<div class="calendario" data-anio="{anio}"></div>
{bloque_puentes(lista, anio)}
{notas_html(datos, anio, cod)}
{fuentes_html(datos, anio, ccaa, tiene_locales(datos, anio, cod))}
</section>""")
        preguntas.append((f"¿Cuántos festivos hay en {N} en {anio}?",
                          f"En {escape(N)} hay {len(lista)} días festivos en {anio}: "
                          f"{sum(1 for x in lista if x['t'] == 'nacional')} nacionales, {sum(1 for x in lista if x['t'] == 'autonomico')} de {escape(ccaa_nombre)}"
                          + (f" y {len(locales)} locales." if locales else ". Las fiestas locales aún no están publicadas.")))
    lista_vecinos = "".join(f'<li><a href="{v["url"]}">{escape(v["nombre"])}</a></li>' for v in vecinos)
    cuerpo = f"""<h1>Festivos en {escape(N)}</h1>
<p class="lead">Calendario laboral de {escape(N)} ({escape(prov_nombre)}): fiestas locales, de {escape(ccaa_nombre)} y nacionales de {' y '.join(map(str, ANIOS))}.</p>
<div class="hoy" id="hoy" data-municipio="{escape(N)}"></div>
<nav class="saltos">{''.join(f'<a href="#festivos-{a}">{a}</a>' for a in ANIOS)}<button class="boton-ics" type="button">📅 Añadir a mi calendario</button></nav>
{''.join(secciones)}
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>
<section><h2>Otros municipios de {escape(prov_nombre)}</h2><ul class="lista-municipios">{lista_vecinos}</ul>
<p><a href="{RUTAS_PROV[cod[:2]]}">Todos los festivos locales de la provincia de {escape(prov_nombre)} →</a> · <a href="/comunidad/{ccaa}/">Calendario laboral de {escape(ccaa_nombre)} →</a></p></section>
<script type="application/json" id="datos-festivos">{json.dumps({"municipio": N, "festivos": embebido, "locales": [a for a in ANIOS if tiene_locales(datos, a, cod)]}, ensure_ascii=False, separators=(",", ":"))}</script>"""
    anio_tit = max(a for a in ANIOS)
    titulo = f"Festivos en {corto(m['nombre_ine'])} {min(ANIOS)} y {anio_tit}: calendario laboral"
    if len(titulo) > 65:
        titulo = f"Festivos en {corto(m['nombre_ine'])} {min(ANIOS)} y {anio_tit}"
    con_locales = [a for a in ANIOS if tiene_locales(datos, a, cod)]
    # Descripción para Google: qué hay en la página, sin dar las fechas (si las da, nadie entra)
    desc = (f"Cuáles son las fiestas locales de {N} en {' y '.join(map(str, ANIOS))}, el próximo festivo, "
            f"los puentes y todos los festivos de {ccaa_nombre}, con el boletín oficial. Añádelos a tu calendario.")
    migas = [(ccaa_nombre, f"/comunidad/{ccaa}/"), (prov_nombre, RUTAS_PROV[cod[:2]]), (N, None)]
    if ccaa_nombre == prov_nombre:
        migas = migas[1:]
    return pagina(m["url"], titulo, desc, cuerpo, migas, [faq_ld(preguntas)], indexable=bool(con_locales))


# ---------------------------------------------------------------- provincias, comunidades y España

def pagina_provincia(datos, codp, muni_prov):
    nombre, ccaa = PROVINCIAS[codp]
    secciones = []
    for anio in ANIOS:
        filas = []
        for cod, m in muni_prov:
            loc = [x for x in festivos_de(datos, anio, cod) if x["t"] == "local"]
            celda = ", ".join(fecha_larga(x["f"], False) for x in loc) if loc else '<span class="gris">Pendiente de publicar</span>'
            filas.append(f'<tr><td><a href="{m["url"]}">{escape(m["nombre"])}</a></td><td>{celda}</td></tr>')
        con = sum(1 for cod, _ in muni_prov if tiene_locales(datos, anio, cod))
        secciones.append(f"""<section id="festivos-{anio}"><h2>Fiestas locales de la provincia de {escape(nombre)} en {anio}</h2>
<p>{'Con fechas publicadas: ' + str(con) + ' de ' + str(len(muni_prov)) + ' municipios.' if con else 'Las fiestas locales de ' + str(anio) + ' todavía no están publicadas.'}</p>
<div class="tabla-envoltorio"><table class="festivos"><thead><tr><th>Municipio</th><th>Fiestas locales</th></tr></thead><tbody>{''.join(filas)}</tbody></table></div></section>""")
    cuerpo = f"""<h1>Festivos en la provincia de {escape(nombre)}</h1>
<p class="lead">Las dos fiestas locales de cada municipio de {escape(nombre)} y el <a href="/comunidad/{ccaa}/">calendario laboral de {escape(COMUNIDADES[ccaa][0])}</a>.</p>
{''.join(secciones)}"""
    alguno = any(tiene_locales(datos, a, c) for a in ANIOS for c, _ in muni_prov)
    return pagina(RUTAS_PROV[codp], f"Festivos locales de la provincia de {nombre} {min(ANIOS)} y {max(ANIOS)}",
                  f"Fiestas locales de todos los municipios de la provincia de {nombre} en {' y '.join(map(str, ANIOS))}, según el boletín oficial.",
                  cuerpo, [(COMUNIDADES[ccaa][0], f"/comunidad/{ccaa}/"), (nombre, None)], indexable=alguno)


def pagina_comunidad(datos, ccaa, provs):
    nombre = COMUNIDADES[ccaa][0]
    secciones = []
    for anio in ANIOS:
        lista = datos[anio]["nacionales_autonomicos"][ccaa]
        notas = "".join(f'<p class="nota">{escape(t)}</p>' for t in datos[anio]["notas"].get(ccaa, []))
        secciones.append(f"""<section id="festivos-{anio}"><h2>Calendario laboral de {escape(nombre)} {anio}</h2>
<p>{len(lista)} festivos comunes a toda la comunidad, más las dos fiestas locales de cada municipio.</p>
{tabla_festivos(lista)}{bloque_puentes(lista, anio)}{notas}
<p class="fuente">Fuente: <a href="{datos[anio]['boe']['url']}" rel="nofollow noopener">{escape(datos[anio]['boe']['titulo'])}</a>.</p></section>""")
    enlaces = "".join(f'<li><a href="{RUTAS_PROV[p]}">{escape(PROVINCIAS[p][0])}</a></li>' for p in provs)
    cuerpo = f"""<h1>Festivos en {escape(nombre)}</h1>
<p class="lead">Calendario laboral de {escape(nombre)} en {' y '.join(map(str, ANIOS))}: festivos nacionales y autonómicos. Busca tu municipio para ver también sus fiestas locales.</p>
{''.join(secciones)}
<section><h2>Fiestas locales por provincia</h2><ul class="lista-municipios">{enlaces}</ul></section>"""
    return pagina(f"/comunidad/{ccaa}/", f"Calendario laboral {nombre} {min(ANIOS)} y {max(ANIOS)}: festivos",
                  f"Festivos de {nombre} en {' y '.join(map(str, ANIOS))} según el BOE: fiestas nacionales y autonómicas, puentes y fiestas locales por provincia.",
                  cuerpo, [(nombre, None)])


def pagina_espana(datos, anio):
    d = datos[anio]["nacionales_autonomicos"]
    fechas = {}
    for ccaa, lista in d.items():
        for x in lista:
            fechas.setdefault((x["f"], x["n"]), []).append((ccaa, x["t"]))
    filas = []
    todas = len(COMUNIDADES)
    for (f, n), cc in sorted(fechas.items()):
        if len(cc) == todas:
            donde = "<strong>Toda España</strong>"
        else:
            donde = ", ".join(f'<a href="/comunidad/{c}/">{escape(COMUNIDADES[c][0])}</a>' for c, _ in sorted(cc))
        tipo = "nacional" if all(t == "nacional" for _, t in cc) else "autonomico"
        filas.append(f'<tr class="t-{tipo}"><td><time datetime="{f}">{fecha_larga(f, False)}</time></td><td>{DIAS[dt.date.fromisoformat(f).weekday()]}</td>'
                     f'<td>{escape(n)}</td><td>{donde}</td></tr>')
    comunes = [f for (f, n), cc in fechas.items() if len(cc) == todas]
    cuerpo = f"""<h1>Calendario laboral {anio}</h1>
<p class="lead">Todos los festivos de {anio} en España según el BOE: {len(comunes)} fiestas comunes a todo el país y las de cada comunidad autónoma. Busca tu municipio para ver también sus dos fiestas locales.</p>
<div class="tabla-envoltorio"><table class="festivos"><thead><tr><th>Fecha</th><th>Día</th><th>Fiesta</th><th>Dónde es festivo</th></tr></thead><tbody>{''.join(filas)}</tbody></table></div>
<p class="fuente">Fuente: <a href="{datos[anio]['boe']['url']}" rel="nofollow noopener">{escape(datos[anio]['boe']['titulo'])}</a>, publicada en el BOE el {fecha_larga(datos[anio]['boe']['publicado'], False)} de {datos[anio]['boe']['publicado'][:4]}.</p>
<section id="comunidades"><h2>Calendario laboral {anio} por comunidad</h2>{lista_comunidades()}</section>"""
    return pagina(f"/calendario-laboral-{anio}/", f"Calendario laboral {anio}: todos los festivos de España",
                  f"Festivos de {anio} en España según el BOE: fiestas nacionales, de cada comunidad autónoma y locales de cada municipio.",
                  cuerpo, [(f"Calendario laboral {anio}", None)])


def lista_comunidades():
    return '<ul class="lista-municipios">' + "".join(f'<li><a href="/comunidad/{c}/">{escape(n)}</a></li>' for c, (n, _) in
                                                       sorted(COMUNIDADES.items(), key=lambda x: x[1][0])) + "</ul>"


def portada(datos):
    anio = HOY.year if HOY.year in datos else min(ANIOS)
    proximos = [x for x in datos[anio]["nacionales_autonomicos"]["madrid"] if x["t"] == "nacional" and x["f"] >= HOY.isoformat()][:3]
    if anio + 1 in datos and len(proximos) < 3:
        proximos += [x for x in datos[anio + 1]["nacionales_autonomicos"]["madrid"] if x["t"] == "nacional"][:3 - len(proximos)]
    prox = "".join(f'<li><b>{fecha_larga(x["f"])}</b> {x["f"][:4]} · {escape(x["n"])}</li>' for x in proximos)
    cuerpo = f"""<section class="portada">
<h1>Festivos de tu municipio</h1>
<p class="lead">Las fiestas locales, autonómicas y nacionales de los más de 8.000 municipios de España, sacadas del BOE y de los boletines oficiales de cada comunidad.</p>
<form class="buscador" role="search" action="/" onsubmit="return false"><label for="q" class="oculto">Municipio</label>
<input id="q" type="search" placeholder="Escribe tu municipio: Getafe, Elche, Reus…" autocomplete="off"><ul id="sugerencias" class="sugerencias"></ul></form>
</section>
<section><h2>Próximos festivos nacionales</h2><ul class="puentes">{prox}</ul>
<p>{' · '.join(f'<a href="/calendario-laboral-{a}/">Calendario laboral {a} completo →</a>' for a in ANIOS)}</p></section>
<section id="comunidades"><h2>Festivos por comunidad autónoma</h2>{lista_comunidades()}</section>
<section class="contenido"><h2>¿Cuántos festivos hay al año?</h2>
<p>En España hay como máximo 14 fiestas laborales al año: 12 las fija el Estado y cada comunidad autónoma, que puede cambiar algunas fiestas nacionales por otras propias, y 2 son locales, elegidas por cada ayuntamiento. Por eso los festivos cambian de un municipio a otro aunque estén en la misma provincia.</p>
<p>El calendario nacional y autonómico se publica en el BOE en otoño del año anterior. Las fiestas locales las publica cada comunidad en su boletín oficial, normalmente entre el verano y el final del año anterior.</p></section>"""
    return pagina("/", f"Festivos de tu municipio {min(ANIOS)} y {max(ANIOS)}: calendario laboral de España",
                  "Busca tu municipio y consulta sus festivos locales, autonómicos y nacionales, los puentes y el próximo festivo. Datos del BOE y de los boletines oficiales.",
                  cuerpo, scripts="")


def legales():
    t = TITULAR
    sobre = f"""<h1>De dónde salen los datos</h1><div class="contenido">
<p>festivosde.es recoge los días festivos de cada municipio de España de las publicaciones oficiales:</p>
<ul><li><strong>Fiestas nacionales y autonómicas:</strong> la resolución anual de la Dirección General de Trabajo con la relación de fiestas laborales, publicada en el Boletín Oficial del Estado (BOE).</li>
<li><strong>Fiestas locales:</strong> las resoluciones u órdenes de cada comunidad autónoma con las dos fiestas locales de cada municipio, publicadas en su boletín oficial. Cuando una comunidad publica correcciones, se aplican.</li></ul>
<p>Cada página enlaza la publicación oficial de la que salen sus fechas. Si las fiestas locales de un municipio todavía no se han publicado, lo indicamos: nunca ponemos una fecha que no esté en un boletín oficial.</p>
<p>En algunas comunidades hay además fiestas de una isla o de un territorio concreto (por ejemplo, en Canarias); las indicamos con la nota del BOE.</p>
<p>Los datos se actualizan automáticamente cuando se publican nuevas resoluciones. Si encuentras un error, escríbenos a {t['email']}.</p></div>"""
    aviso = f"""<h1>Aviso legal</h1><div class="contenido">
<h2>Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE), se informa de los datos del titular de este sitio web:</p>
<p>Titular: {t['nombre']}<br>NIF: {t['nif']}<br>Domicilio: {t['domicilio']}<br>Correo electrónico: {t['email']}<br>Sitio web: {DOMINIO}</p>
<h2>Objeto y condiciones de uso</h2>
<p>festivosde.es ofrece de forma gratuita información sobre los días festivos de los municipios de España a partir de publicaciones oficiales. El acceso es libre y no requiere registro.</p>
<h2>Responsabilidad</h2>
<p>La información se muestra con fines informativos. Aunque se toma de los boletines oficiales, puede haber cambios o correcciones posteriores: para cuestiones laborales o legales, consulta siempre la publicación oficial enlazada. El titular no se hace responsable del contenido de sitios externos enlazados.</p>
<h2>Propiedad intelectual</h2>
<p>El diseño, los textos y el código de este sitio son del titular. Las publicaciones oficiales se citan y enlazan como fuente.</p>
<h2>Legislación aplicable</h2><p>Estas condiciones se rigen por la legislación española.</p></div>"""
    privacidad = f"""<h1>Política de privacidad</h1><div class="contenido">
<h2>Responsable</h2><p>{t['nombre']} ({t['email']}).</p>
<h2>Qué datos tratamos</h2>
<p>Esta web no tiene formularios de registro. Lo que escribes en el buscador se procesa en tu propio navegador y no se envía ni se guarda en ningún servidor. El archivo de calendario se genera también en tu navegador.</p>
<p>El proveedor de alojamiento (Cloudflare) puede registrar datos técnicos de la conexión, como la dirección IP, por motivos de seguridad y funcionamiento del servicio, y ofrece estadísticas de visitas sin cookies.</p>
<h2>Publicidad y cookies</h2>
<p>Esta web se financia con publicidad de Google AdSense, un servicio de Google Ireland Limited. Google, como proveedor externo, utiliza cookies para mostrar anuncios, medir su rendimiento y, si lo aceptas, personalizarlos según tus visitas a esta y otras webs.</p>
<p>La primera vez que entras se muestra el mensaje de consentimiento de Google, donde puedes aceptar, rechazar o elegir qué finalidades permites. Base legal: tu consentimiento. Mientras no lo des, no se usan cookies de publicidad. Puedes cambiar tu elección con el enlace «Configurar cookies» del pie de página.</p>
<p>Más información: <a href="https://policies.google.com/technologies/ads?hl=es" rel="noopener">cómo usa Google las cookies en la publicidad</a>.</p>
<h2>Destinatarios</h2>
<p>No cedemos datos a terceros salvo obligación legal. Google y Cloudflare pueden tratar datos como proveedores del servicio; algunos pueden estar fuera del Espacio Económico Europeo, con las garantías previstas en el RGPD.</p>
<h2>Tus derechos</h2>
<p>Puedes ejercer tus derechos de acceso, rectificación, supresión y demás escribiendo a {t['email']}. También puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p></div>"""
    guardar("/sobre-los-datos/", pagina("/sobre-los-datos/", "De dónde salen los datos de festivos | festivosde.es",
                                        "Los festivos de cada municipio salen del BOE y de los boletines oficiales de cada comunidad autónoma.",
                                        sobre, [("Sobre los datos", None)]))
    guardar("/aviso-legal/", pagina("/aviso-legal/", "Aviso legal | festivosde.es", "Aviso legal y datos del titular de festivosde.es.", aviso, [("Aviso legal", None)]))
    guardar("/privacidad/", pagina("/privacidad/", "Política de privacidad | festivosde.es", "Política de privacidad y cookies de festivosde.es.", privacidad, [("Privacidad", None)]))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Busca tu municipio desde la <a href="/">portada</a>.</p>', indexable=False))
    return ["/sobre-los-datos/", "/aviso-legal/", "/privacidad/"]


# ---------------------------------------------------------------- main

def main():
    global ANIOS, RUTAS_PROV
    datos = cargar()
    ANIOS = sorted(datos)
    muni = municipios()
    if len(muni) < 8000:
        sys.exit(f"ERROR: solo {len(muni)} municipios. No se publica.")

    # Rutas: /<slug>/ y, si el nombre se repite o choca con una ruta reservada, /<slug>-<provincia>/
    RUTAS_PROV = {p: f"/provincia/{slug(n)}/" for p, (n, _) in PROVINCIAS.items()}
    cuenta = {}
    for cod, nom in muni.items():
        cuenta[slug(corto(nom))] = cuenta.get(slug(corto(nom)), 0) + 1
    info = {}
    for cod, nom in muni.items():
        s = slug(corto(nom))
        if cuenta[s] > 1 or s in RESERVADOS or s.startswith("calendario-laboral"):
            s = f"{s}-{slug(PROVINCIAS[cod[:2]][0])}"
        info[cod] = {"nombre": bonito(nom), "nombre_ine": nom, "url": f"/{s}/"}
    assert len({m["url"] for m in info.values()}) == len(info), "rutas repetidas"

    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    for f in ("style.css", "app.js"):
        shutil.copy(PLANTILLA / f, WEB / "assets" / f)
    for f in ("og.png", "favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        if (PLANTILLA / f).exists():
            shutil.copy(PLANTILLA / f, WEB / f)

    rutas_sitemap = ["/"]
    por_prov = {}
    for cod, m in sorted(info.items(), key=lambda x: x[1]["nombre"]):
        por_prov.setdefault(cod[:2], []).append((cod, m))
    indexables = 0
    for codp, lista in por_prov.items():
        for i, (cod, m) in enumerate(lista):
            vecinos = [v for _, v in lista[max(0, i - 6):i + 7] if v is not m][:12]
            html = pagina_municipio(datos, cod, m, vecinos)
            guardar(m["url"], html)
            if 'name="robots" content="noindex"' not in html:
                rutas_sitemap.append(m["url"])
                indexables += 1
        html = pagina_provincia(datos, codp, lista)
        guardar(RUTAS_PROV[codp], html)
        if 'content="noindex"' not in html:
            rutas_sitemap.append(RUTAS_PROV[codp])
    for ccaa in COMUNIDADES:
        provs = sorted((p for p, (_, c) in PROVINCIAS.items() if c == ccaa), key=lambda p: PROVINCIAS[p][0])
        guardar(f"/comunidad/{ccaa}/", pagina_comunidad(datos, ccaa, provs))
        rutas_sitemap.append(f"/comunidad/{ccaa}/")
    for anio in ANIOS:
        guardar(f"/calendario-laboral-{anio}/", pagina_espana(datos, anio))
        rutas_sitemap.append(f"/calendario-laboral-{anio}/")
    guardar("/", portada(datos))
    rutas_sitemap += legales()

    # Índice del buscador: [nombre para buscar, nombre visible, ruta, provincia]
    indice = [[re.sub(r"[^a-z0-9ñ/ ]", " ", m["nombre"].lower()), m["nombre"], m["url"], PROVINCIAS[c[:2]][0]] for c, m in info.items()]
    (WEB / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    hoy = HOY.isoformat()
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoy}</lastmod></url>\n" for r in rutas_sitemap)
                                     + "</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    print(f"Web generada: {len(info)} municipios ({indexables} con fiestas locales, indexables), "
          f"{len(por_prov)} provincias, {len(COMUNIDADES)} comunidades, años {ANIOS}.")


ANIOS = []
RUTAS_PROV = {}

if __name__ == "__main__":
    main()
