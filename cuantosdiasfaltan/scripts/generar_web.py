"""Genera la web estática de cuantosdiasfaltan a partir de cuantosdiasfaltan/eventos.json.

Páginas:
  /                     buscador, lo próximo por categorías y tu propia cuenta atrás
  /<categoria>/         videojuegos, películas, series, tecnología y eventos
  /<evento>/            cuánto falta (o cuánto hace, si ya ha pasado) con la fecha y la fuente oficial
  /cuanto-hace/         cuánto tiempo ha pasado desde una fecha
  /sobre-nosotros/, /aviso-legal/, /privacidad/

Solo se publican fechas anunciadas oficialmente, con su fuente y la fecha en que se comprobó. Si algo no
tiene fecha oficial, la página lo dice y da la ventana anunciada («2027»), nunca rumores.

Uso: python cuantosdiasfaltan/scripts/generar_web.py
"""
import datetime as dt
import json
import os
import shutil
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
PLANTILLA = RAIZ / "plantilla"
EVENTOS = RAIZ / "eventos.json"
DOMINIO = os.environ.get("CDF_DOMINIO", "https://cuantosdiasfaltan.es")
NOMBRE_WEB = DOMINIO.split("//")[1]
VERSION = "2"
HOY = dt.date.fromisoformat(os.environ["CDF_HOY"]) if os.environ.get("CDF_HOY") else dt.date.today()
ADSENSE = "ca-pub-8810566450749484"
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
CATEGORIAS = {"videojuegos": ("Videojuegos", "🎮"), "peliculas": ("Películas", "🎬"), "series": ("Series", "📺"), "anime": ("Anime", "⛩️"),
              "deportes": ("Deportes", "🏟️"), "musica": ("Música", "🎵"), "fiestas": ("Fiestas y cultura", "🎉"),
              "tecnologia": ("Tecnología", "📱"), "espacio": ("Ciencia y espacio", "🔭"), "eventos": ("Eventos", "🏆")}
FRASE_CAT = {"videojuegos": "los próximos videojuegos", "peliculas": "los próximos estrenos de cine", "series": "los próximos estrenos de series", "anime": "los próximos estrenos de anime",
             "deportes": "los próximos grandes eventos deportivos", "musica": "los próximos festivales y conciertos",
             "fiestas": "las próximas fiestas y eventos culturales", "tecnologia": "los próximos lanzamientos de tecnología",
             "espacio": "los próximos eclipses y fenómenos astronómicos", "eventos": "los próximos grandes eventos"}
RESERVADOS = set(CATEGORIAS) | {"assets", "cuanto-hace", "sobre-nosotros", "aviso-legal", "privacidad", "buscar"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
PRECISIONES = {"dia", "mes", "trimestre", "anio", "sin_fecha"}


def fecha_larga(d, con_anio=True):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}" + (f" de {d.year}" if con_anio else "")


def fecha_simple(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def sumar_meses(d, n):
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    ultimo = (dt.date(a + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).day
    return dt.date(a, m, min(d.day, ultimo))


def meses_y_dias(desde, hasta):
    """(meses, días) de calendario entre dos fechas (desde <= hasta)."""
    meses = 0
    while sumar_meses(desde, meses + 1) <= hasta:
        meses += 1
    return meses, (hasta - sumar_meses(desde, meses)).days


def plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


def texto_tiempo(desde, hasta):
    """«3 meses y 2 días», «1 año, 2 meses y 5 días», «12 días»."""
    m, d = meses_y_dias(desde, hasta)
    a, m = divmod(m, 12)
    partes = [p for p in (plural(a, "año", "años") if a else "", plural(m, "mes", "meses") if m else "", plural(d, "día", "días") if d else "") if p]
    if not partes:
        return "0 días"
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]


def cargar():
    eventos = json.loads(EVENTOS.read_text(encoding="utf-8"))
    slugs = set()
    for e in eventos:
        assert e["slug"] not in slugs and e["slug"] not in RESERVADOS, f"slug repetido o reservado: {e['slug']}"
        assert e["categoria"] in CATEGORIAS, e
        assert e["precision"] in PRECISIONES, e
        assert e["precision"] != "dia" or e.get("fecha"), f"falta la fecha: {e['slug']}"
        assert e.get("fuente_url") and e.get("comprobado"), f"falta la fuente o la fecha de comprobación: {e['slug']}"
        if e.get("estimada") or e.get("rango"):
            # una estimación nunca sale de rumores: solo de una ventana oficial o de la costumbre del propio organizador
            assert e["precision"] != "dia" and e.get("estimacion"), f"estimación sin motivo: {e['slug']}"
            assert not e.get("rango") or e.get("ventana"), f"rango sin ventana: {e['slug']}"
        slugs.add(e["slug"])
    return eventos


def fecha_de(e):
    return dt.date.fromisoformat(e["fecha"]) if e.get("fecha") and e["precision"] == "dia" else None


def estimada_de(e):
    """Fecha aproximada (no oficial) mientras no se anuncie el día; caducada no cuenta."""
    d = dt.date.fromisoformat(e["estimada"]) if e.get("estimada") and e["precision"] != "dia" else None
    return d if d and d >= HOY else None


RANGO_MAX = 125  # días: «finales de 2027» o un trimestre sí; un año entero («previsto 2027») no, que no dice nada


def rango_de(e):
    """(desde, hasta) de la ventana anunciada, para decir «faltan entre X y Y días» si es corta."""
    if not e.get("rango") or e["precision"] == "dia":
        return None
    desde, hasta = (dt.date.fromisoformat(x) for x in e["rango"])
    if (hasta - desde).days > RANGO_MAX:
        return None
    return (max(desde, HOY), hasta) if hasta >= HOY else None


def previsto(e):
    """Ventana anunciada demasiado larga para dar días («2027»): se dice tal cual."""
    return bool(e.get("rango") and e.get("ventana") and not rango_de(e) and dt.date.fromisoformat(e["rango"][1]) >= HOY)


# ---------------------------------------------------------------- plantilla de página

def pagina(ruta, titulo, descripcion, cuerpo, ld=None, scripts=""):
    url = DOMINIO + ruta
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    menu = "".join(f'<a href="/{c}/">{ico} {n}</a>' for c, (n, ico) in CATEGORIAS.items())
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#111111">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NOMBRE_WEB}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
{ld_html}
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{CABECERA_ANUNCIOS}
</head>
<body>
<header class="cab"><div class="cont">
<a class="logo" href="/"><span class="logo-ico">⏳</span><span>cuantos<b>dias</b>faltan</span></a>
<nav class="menu">{menu}</nav>
</div></header>
<main class="cont">
{cuerpo}
</main>
<footer class="pie"><div class="cont">
<p><strong>{NOMBRE_WEB}</strong>: cuántos días faltan para los próximos lanzamientos y eventos, con la fecha oficial y su fuente.</p>
<p class="enlaces"><a href="/">Inicio</a>{''.join(f'<a href="/{c}/">{n}</a>' for c, (n, _) in CATEGORIAS.items())}<a href="/cuanto-hace/">Cuánto hace</a><a href="/sobre-nosotros/">Sobre nosotros</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a>{CONFIGURAR_COOKIES}</p>
<p>¿Ha cambiado una fecha? Escríbenos a {TITULAR['email']}.</p>
</div></footer>
<script src="/assets/cuenta.js?v={VERSION}" defer></script>
{scripts}
</body>
</html>
"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- piezas

def contador(d, pasado=False):
    """La cuenta atrás grande: el texto en meses y días se ve sin script; el script la pone en directo
    y deja elegir días, semanas o meses."""
    if pasado:
        n = (HOY - d).days
        principal = f"Hace {texto_tiempo(d, HOY)}"
    else:
        n = (d - HOY).days
        principal = "¡Es hoy!" if n == 0 else ("Falta 1 día" if n == 1 else f"Faltan {texto_tiempo(HOY, d)}")
    return (f'<div class="contador" data-fecha="{d.isoformat()}" data-modo="{"hace" if pasado else "falta"}">'
            f'<p class="c-grande">{principal}</p>'
            f'<p class="c-dias"><b>{n}</b> {"día" if n == 1 else "días"}</p>'
            f'<p class="c-vivo"></p>'
            f'<div class="c-unidades" role="group" aria-label="Ver en"><button type="button" data-u="auto" aria-pressed="true">Meses</button>'
            f'<button type="button" data-u="semanas">Semanas</button><button type="button" data-u="dias">Días</button><button type="button" data-u="horas">Horas</button></div></div>')


def tarjeta(e):
    d = fecha_de(e)
    if d and d >= HOY:
        n = (d - HOY).days
        cifra, ud, cuando = n, "día" if n == 1 else "días", fecha_simple(e["fecha"])
    elif d:
        cifra, ud, cuando = "✓", "ya disponible", fecha_simple(e["fecha"])
    elif estimada_de(e):
        n = (estimada_de(e) - HOY).days
        cifra, ud, cuando = f"≈{n}", "días", f"Fecha estimada: {fecha_simple(e['estimada'])}"
    elif rango_de(e):
        a, b = rango_de(e)
        cifra, ud, cuando = f"{(a - HOY).days}–{(b - HOY).days}", "días", f"Previsto: {e['ventana']}"
    else:
        cifra, ud = "?", "previsto" if previsto(e) else "sin fecha"
        cuando = f"Previsto: {e['ventana']}" if previsto(e) else e.get("ventana") or "Fecha sin confirmar"
    ico = CATEGORIAS[e["categoria"]][1]
    return (f'<li><a href="/{e["slug"]}/"><span class="t-cifra"><b>{cifra}</b> {ud}</span><span class="t-tit">{ico} {escape(e["titulo"])}</span>'
            f'<span class="t-cuando">{escape(cuando)}</span></a></li>')


def orden(e):
    d = fecha_de(e)
    if d and d >= HOY:
        return (0, d.isoformat())
    aprox = estimada_de(e) or (rango_de(e) or [None])[0]
    if not d and aprox:
        return (0, aprox.isoformat())
    if not d:
        return (1, e.get("fecha") or "9999", e["titulo"])
    return (2, (dt.date.max - d).days)


def lista_tarjetas(eventos):
    return '<ul class="tarjetas">' + "".join(tarjeta(e) for e in sorted(eventos, key=orden)) + "</ul>"


# ---------------------------------------------------------------- páginas

def preguntas_de(e):
    """(H1, título) con la forma más buscada de cada tipo (Keyword Planner, octubre de 2026):
    «cuándo sale GTA 6» 22.200 frente a «cuánto falta» 170; «estreno Dune 3» 720 frente a «cuándo se estrena» 70;
    «cuánto falta para Navidad» 8.100 frente a «cuándo es» 3.600 y «cuántos días faltan» 2.900."""
    t, c = e.get("en_frase") or e["titulo"], e["categoria"]  # en_frase: «el iPhone 18», «la PlayStation 6»
    if c in ("videojuegos", "tecnologia"):
        return f"¿Cuándo sale {t}?", f"¿Cuándo sale {t}? Fecha de lanzamiento y cuenta atrás"
    if c == "peliculas":
        return f"¿Cuándo se estrena {t}?", f"Estreno de {t}: fecha en cines y cuenta atrás"
    if c == "anime":  # «solo leveling temporada 3» 6.600 frente a «cuándo sale jujutsu kaisen temporada 3» 390
        return f"¿Cuándo sale {t}?", f"{t}: fecha de estreno y cuenta atrás"
    if c == "series":
        return f"¿Cuándo se estrena {t}?", f"¿Cuándo se estrena {t}? Fecha de estreno y cuenta atrás"
    return f"¿Cuánto falta para {t}?", f"¿Cuánto falta para {t}? Fecha y cuenta atrás"


def pagina_evento(e, eventos):
    d = fecha_de(e)
    t = e["titulo"]
    cat, ico = CATEGORIAS[e["categoria"]]
    donde = e.get("plataformas") or e.get("lugar") or ""
    if d and d >= HOY:
        cab, titulo = preguntas_de(e)
        sub = f'{"Sale" if e["categoria"] in ("videojuegos", "tecnologia") else "Se estrena" if e["categoria"] in ("peliculas", "series", "anime") else "Es"} el <strong>{fecha_larga(d)}</strong>'
        bloque = contador(d)
        desc = f"Faltan {(d - HOY).days} días para {t}: {fecha_larga(d)}. Cuenta atrás en directo en meses, semanas, días y horas, con la fecha oficial."
    elif d:
        cab = f"¿Cuánto hace de {t}?"
        sub = f'Fue el <strong>{fecha_larga(d)}</strong>'
        bloque = contador(d, pasado=True)
        titulo = f"¿Cuánto hace de {t}? Fecha de lanzamiento"
        desc = f"{t} salió el {fecha_larga(d)}: hace {texto_tiempo(d, HOY)}."
        if e["categoria"] in ("series", "anime"):  # quien busca una temporada ya estrenada quiere saber desde cuándo y dónde verla
            cab = f"¿Cuándo se estrenó {t}?"
            sub = f'Se estrenó el <strong>{fecha_larga(d)}</strong>'
            titulo = f"{t}: fecha de estreno y dónde verla"
            desc = f"{t} se estrenó el {fecha_larga(d)}{f' en {donde}' if donde else ''}: hace {texto_tiempo(d, HOY)}."
    elif estimada_de(e):
        est = estimada_de(e)
        cab, titulo = preguntas_de(e)
        sub = f'<strong>Fecha estimada: {fecha_larga(est)}</strong> · aún no es oficial'
        bloque = '<p class="aviso-estimada">≈ Fecha aproximada, no oficial</p>' + contador(est)
        desc = f"Faltan unos {(est - HOY).days} días para {t}: fecha estimada {fecha_larga(est)}, aún no oficial. {e['estimacion']}."
    elif rango_de(e):
        a, b = rango_de(e)
        cab, titulo = preguntas_de(e)
        sub = f'<strong>Previsto: {escape(e["ventana"])}</strong> · aún sin día oficial'
        bloque = (f'<div class="contador sin-fecha"><p class="c-grande">Faltan entre {(a - HOY).days} y {(b - HOY).days} días</p>'
                  f'<p class="c-dias">Fecha aproximada: {escape(e["ventana"])}. Pondremos la cuenta atrás exacta en cuanto se anuncie el día.</p></div>')
        desc = f"{cab} Previsto para {e['ventana']}, entre {(a - HOY).days} y {(b - HOY).days} días desde hoy. Aún no hay día oficial."
    elif previsto(e):
        cab, titulo = preguntas_de(e)
        sub = f'<strong>Previsto: {escape(e["ventana"])}</strong> · aún sin día oficial'
        bloque = (f'<div class="contador sin-fecha"><p class="c-grande">Previsto para {escape(e["ventana"])}</p>'
                  '<p class="c-dias">Aún no hay día oficial. Pondremos aquí la cuenta atrás en cuanto se anuncie.</p></div>')
        desc = f"{cab} Está previsto para {e['ventana']}, pero aún no hay día oficial. Aquí verás la cuenta atrás en cuanto se anuncie."
    else:
        cab, titulo = preguntas_de(e)
        sub = f'<strong>Fecha sin confirmar</strong>{f": {escape(e["ventana"])}" if e.get("ventana") else ""}'
        bloque = ('<div class="contador sin-fecha"><p class="c-grande">Aún no hay fecha oficial</p>'
                  '<p class="c-dias">Pondremos aquí la cuenta atrás en cuanto se anuncie.</p></div>')
        ventana = f" ({e['ventana']})" if e.get("ventana") else ""
        desc = f"Cuándo sale {t}: todavía no hay fecha oficial{ventana}. Aquí verás la cuenta atrás en cuanto se anuncie."
    retrasos = ""
    if e.get("retrasos"):
        retrasos = '<p class="retrasos">Fechas anunciadas antes: ' + ", ".join(escape(fecha_simple(r) if len(r) == 10 and r[4] == "-" else r) for r in e["retrasos"]) + ".</p>"
    nota_ambito = f'<p class="nota">Fecha de estreno en {escape(e["ambito"])}.</p>' if e.get("ambito") and e["ambito"] not in ("España", "mundial") else ""
    fuente = (f'<p class="fuente">Fuente{"" if e.get("fuente_tipo") == "oficial" else " (medio)"}: <a href="{escape(e["fuente_url"])}" rel="nofollow noopener" target="_blank">'
              f'{escape(e.get("fuente_nombre") or "anuncio oficial")}</a> · Comprobado el {fecha_simple(e["comprobado"])}.</p>')
    if not d and (estimada_de(e) or rango_de(e) or previsto(e)):
        fuente = f'<p class="nota">Por qué esta fecha: {escape(e["estimacion"])}. La cambiaremos por la oficial en cuanto se anuncie.</p>' + fuente
    otros = [x for x in eventos if x["categoria"] == e["categoria"] and x is not e]
    otros = sorted(otros, key=orden)[:8]
    preguntas = []
    if d and d >= HOY:
        preguntas.append((f"¿Cuándo sale {t}?", f"{t}: {fecha_larga(d)}{f' ({donde})' if donde else ''}, según {e.get('fuente_nombre') or 'el anuncio oficial'}."))
        preguntas.append((f"¿Cuántos días faltan para {t}?", f"Hoy, {fecha_larga(HOY)}, faltan {(d - HOY).days} días ({texto_tiempo(HOY, d)})."))
    if not d and estimada_de(e):
        preguntas.append((cab, f"Aún no hay fecha oficial. La fecha estimada es el {fecha_larga(estimada_de(e))}: {e['estimacion']}."))
    elif not d and (rango_de(e) or previsto(e)):
        preguntas.append((cab, f"Aún no hay día oficial: está previsto para {e['ventana']}. {e['estimacion']}."))
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › <a href="/{e['categoria']}/">{cat}</a></nav>
<h1>{escape(cab)}</h1>
<p class="sub">{sub}{f' · {escape(donde)}' if donde else ''}</p>
{bloque}
<p class="acciones"><a class="boton" href="https://wa.me/?text={escape(f'¿Cuánto falta para {t}? {DOMINIO}/{e["slug"]}/')}" rel="noopener">💬 Compartir</a></p>
{nota_ambito}{retrasos}{fuente}
{f'<section><h2>{ico} Más {cat.lower()}</h2>{lista_tarjetas(otros)}</section>' if otros else ''}"""
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"},
        {"@type": "ListItem", "position": 2, "name": cat, "item": f"{DOMINIO}/{e['categoria']}/"},
        {"@type": "ListItem", "position": 3, "name": t, "item": f"{DOMINIO}/{e['slug']}/"}]}]
    if preguntas:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in preguntas]})
    return pagina(f"/{e['slug']}/", titulo, desc, cuerpo, ld)


def pagina_categoria(c, eventos):
    nombre, ico = CATEGORIAS[c]
    lista = [e for e in eventos if e["categoria"] == c]
    frase = FRASE_CAT[c]
    cuerpo = f"""<h1>{ico} ¿Cuánto falta para {frase}?</h1>
<p class="sub">{nombre}: las fechas oficiales (y la estimada si aún no la hay), ordenadas por lo que falta.</p>
{lista_tarjetas(lista)}"""
    return pagina(f"/{c}/", f"{frase[0].upper() + frase[1:]}: cuántos días faltan y fechas",
                  f"Cuántos días faltan para {frase}, con la fecha oficial de cada uno y una cuenta atrás en directo.", cuerpo)


def pagina_portada(eventos):
    proximos = [e for e in sorted(eventos, key=orden) if fecha_de(e) and fecha_de(e) >= HOY][:12]
    secciones = "".join(f'<section><h2><a href="/{c}/">{ico} {n}</a></h2>{lista_tarjetas([e for e in eventos if e["categoria"] == c][:8])}'
                        f'<p><a href="/{c}/">Ver todos →</a></p></section>' for c, (n, ico) in CATEGORIAS.items() if any(e["categoria"] == c for e in eventos))
    indice = [[e["titulo"], e["slug"], CATEGORIAS[e["categoria"]][1]] for e in eventos]
    cuerpo = f"""<section class="portada"><h1>¿Cuántos días faltan para…?</h1>
<p class="sub">Cuenta atrás para los videojuegos, películas, series y eventos que esperas, con la fecha oficial.</p>
<form class="buscador" role="search" onsubmit="return false"><input id="q" type="search" placeholder="Busca: GTA 6, Spider-Man, Eurovisión…" autocomplete="off" aria-label="Buscar"><ul id="sug" class="sug"></ul></form>
<script type="application/json" id="indice">{json.dumps(indice, ensure_ascii=False, separators=(",", ":"))}</script></section>
<section><h2>⏱️ Lo próximo</h2>{lista_tarjetas(proximos)}</section>
<section id="tu-cuenta" class="herramienta"><h2>🗓️ Tu cuenta atrás</h2>
<p>¿Tu cumpleaños, tu boda, tus vacaciones? Pon la fecha y comparte el enlace.</p>
<form onsubmit="return false"><input id="c-nombre" type="text" maxlength="60" placeholder="¿Para qué? (p. ej. Mis vacaciones)" aria-label="Nombre">
<input id="c-fecha" type="date" aria-label="Fecha"><label class="check"><input id="c-anual" type="checkbox"> Cada año</label>
<button class="boton" id="c-crear" type="button">Crear</button></form><div id="c-resultado"></div></section>
{secciones}
<section><h2>⌛ ¿Cuánto hace de…?</h2><p>Calcula cuánto tiempo ha pasado desde cualquier fecha: <a href="/cuanto-hace/">cuánto hace de…</a></p></section>"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NOMBRE_WEB, "url": DOMINIO + "/"}
    return pagina("/", "¿Cuántos días faltan para…? Cuenta atrás de videojuegos, películas y eventos",
                  "Cuántos días faltan para GTA 6, los próximos estrenos, series y grandes eventos, con la fecha oficial y una cuenta atrás en directo.",
                  cuerpo, ld)


def pagina_cuanto_hace(eventos):
    pasados = [e for e in eventos if fecha_de(e) and fecha_de(e) < HOY]
    cuerpo = f"""<h1>¿Cuánto hace de…?</h1>
<p class="sub">Pon una fecha y te decimos cuánto tiempo ha pasado: en años, meses, semanas, días y horas.</p>
<section class="herramienta"><form onsubmit="return false"><input id="h-fecha" type="date" aria-label="Fecha"><button class="boton" id="h-calc" type="button">Calcular</button></form><div id="h-resultado"></div></section>
{f'<section><h2>Ya han salido</h2>{lista_tarjetas(pasados)}</section>' if pasados else ''}"""
    return pagina("/cuanto-hace/", "¿Cuánto hace de…? Calcula el tiempo que ha pasado desde una fecha",
                  "Calcula cuántos años, meses, semanas y días han pasado desde cualquier fecha.", cuerpo)


def legales():
    t = TITULAR
    sobre = f"""<h1>Sobre nosotros</h1><div class="texto">
<p>{NOMBRE_WEB} reúne en un solo sitio cuántos días faltan para los lanzamientos y eventos que más se esperan: videojuegos, películas, series, tecnología y grandes eventos.</p>
<p><strong>Solo publicamos fechas anunciadas oficialmente</strong> por la empresa, el estudio, la plataforma o el organizador, y en cada página enlazamos la fuente y decimos cuándo la comprobamos. Si algo aún no tiene fecha oficial, lo decimos: no publicamos rumores.</p>
<p>Las fechas pueden cambiar (los retrasos son habituales). Si ves una fecha desactualizada, escríbenos a {t['email']} y la corregimos.</p></div>"""
    aviso = f"""<h1>Aviso legal</h1><div class="texto">
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE): titular {t['nombre']}, NIF {t['nif']}, domicilio en {t['domicilio']}, correo {t['email']}, sitio web {DOMINIO}.</p>
<p>La información se ofrece con fines informativos a partir de anuncios oficiales de terceros, que pueden cambiar. Las marcas y nombres de productos pertenecen a sus propietarios; esta web no está afiliada a ellos.</p>
<p>Estas condiciones se rigen por la legislación española.</p></div>"""
    privacidad = f"""<h1>Política de privacidad</h1><div class="texto">
<p>Responsable: {t['nombre']} ({t['email']}). Esta web no tiene registro ni formularios: las cuentas atrás que creas se calculan en tu navegador y no se envían a ningún servidor.</p>
<p>El alojamiento (Cloudflare) puede registrar datos técnicos de la conexión por seguridad y ofrece estadísticas de visitas sin cookies.</p>
<p>Esta web se financia con publicidad de Google AdSense (Google Ireland Limited), que usa cookies para mostrar y medir anuncios y, si lo aceptas, personalizarlos. La primera vez que entras se muestra el mensaje de consentimiento de Google; puedes cambiar tu elección en «Configurar cookies», al pie de la página. Más información: <a href="https://policies.google.com/technologies/ads?hl=es" rel="noopener">cómo usa Google las cookies en la publicidad</a>.</p>
<p>Puedes ejercer tus derechos escribiendo a {t['email']} y reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p></div>"""
    for ruta, tit, cuerpo in (("/sobre-nosotros/", "Sobre nosotros", sobre), ("/aviso-legal/", "Aviso legal", aviso), ("/privacidad/", "Política de privacidad", privacidad)):
        guardar(ruta, pagina(ruta, f"{tit} | {NOMBRE_WEB}", f"{tit} de {NOMBRE_WEB}.", cuerpo))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Vuelve a la <a href="/">portada</a> y búscalo.</p>'))
    return ["/sobre-nosotros/", "/aviso-legal/", "/privacidad/"]


def main():
    eventos = cargar()
    if len(eventos) < 10:
        sys.exit(f"ERROR: solo {len(eventos)} eventos")
    for e in eventos:
        if (e.get("estimada") and not estimada_de(e)) or (e.get("rango") and dt.date.fromisoformat(e["rango"][1]) < HOY):
            print(f"AVISO: la estimación de {e['slug']} ya ha pasado; hay que revisarla")
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    for f in ("style.css", "cuenta.js"):
        shutil.copy(PLANTILLA / f, WEB / "assets" / f)
    shutil.copy(PLANTILLA / "favicon.svg", WEB / "favicon.svg")
    rutas = ["/"]
    guardar("/", pagina_portada(eventos))
    for c in CATEGORIAS:
        if any(e["categoria"] == c for e in eventos):
            guardar(f"/{c}/", pagina_categoria(c, eventos))
            rutas.append(f"/{c}/")
    for e in eventos:
        guardar(f"/{e['slug']}/", pagina_evento(e, eventos))
        rutas.append(f"/{e['slug']}/")
    guardar("/cuanto-hace/", pagina_cuanto_hace(eventos))
    rutas.append("/cuanto-hace/")
    rutas += legales()
    hoy = HOY.isoformat()
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoy}</lastmod></url>\n" for r in rutas) + "</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    con_fecha = sum(1 for e in eventos if fecha_de(e))
    print(f"Web generada: {len(eventos)} eventos ({con_fecha} con fecha oficial), {len(rutas)} páginas en el sitemap.")


if __name__ == "__main__":
    main()
