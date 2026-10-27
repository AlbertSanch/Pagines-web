"""Genera la web estática de cuantosdiasfaltan a partir de cuantosdiasfaltan/eventos.json.

Páginas:
  /                     buscador, lo próximo por categorías y tu propia cuenta atrás
  /<categoria>/         fechas señaladas, videojuegos, películas, series, anime, deportes…
  /<evento>/            cuánto falta (o cuánto hace, si ya ha pasado) con la fecha y la fuente oficial
  /<serie>/             eventos de cada año (Fallas, Roland Garros…) en una URL sin año que enseña la próxima
                        edición; las URL antiguas con año redirigen (_redirects de Cloudflare Pages)
  /cuanto-hace/         cuánto tiempo ha pasado desde una fecha
  /sobre-nosotros/, /aviso-legal/, /privacidad/

Solo se publican fechas anunciadas oficialmente, con su fuente y la fecha en que se comprobó. Si algo no
tiene fecha oficial, la página lo dice y da la ventana anunciada («2027»), nunca rumores.

Uso: python cuantosdiasfaltan/scripts/generar_web.py
"""
import datetime as dt
import importlib.util
import json
import re
import os
import shutil
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
PLANTILLA = RAIZ / "plantilla"
EVENTOS = RAIZ / "eventos.json"
TEXTOS = RAIZ / "textos.json"  # «qué se sabe»: párrafos propios por evento (clave: slug o serie)
FUENTES = PLANTILLA / "fuentes"
FIJAS = RAIZ.parent / "festivos" / "scripts" / "cuanto_falta.py"  # mismas fechas que festivosde: Pascua, estaciones, Black Friday…
DOMINIO = os.environ.get("CDF_DOMINIO", "https://cuantosdiasfaltan.es")
NOMBRE_WEB = DOMINIO.split("//")[1]
VERSION = "3"
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
CATEGORIAS = {"fechas": ("Fechas señaladas", "📅"), "videojuegos": ("Videojuegos", "🎮"), "peliculas": ("Películas", "🎬"), "series": ("Series", "📺"), "anime": ("Anime", "⛩️"),
              "deportes": ("Deportes", "🏟️"), "musica": ("Música", "🎵"), "fiestas": ("Fiestas y cultura", "🎉"),
              "tecnologia": ("Tecnología", "📱"), "espacio": ("Ciencia y espacio", "🔭"), "eventos": ("Eventos", "🏆")}
FRASE_CAT = {"fechas": "las próximas fechas señaladas", "videojuegos": "los próximos videojuegos", "peliculas": "los próximos estrenos de cine", "series": "los próximos estrenos de series", "anime": "los próximos estrenos de anime",
             "deportes": "los próximos grandes eventos deportivos", "musica": "los próximos festivales y conciertos",
             "fiestas": "las próximas fiestas y eventos culturales", "tecnologia": "los próximos lanzamientos de tecnología",
             "espacio": "los próximos eclipses y fenómenos astronómicos", "eventos": "los próximos grandes eventos"}
RESERVADOS = set(CATEGORIAS) | {"assets", "cuanto-hace", "sobre-nosotros", "aviso-legal", "privacidad", "buscar", "contacto"}
FESTIVOSDE = "https://festivosde.es"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
PRECISIONES = {"dia", "mes", "trimestre", "anio", "sin_fecha"}
TEXTOS_EVENTO = {}
# sagas y temas para enlazar entre sí: título de la sección → expresión sobre el slug público
SAGAS = {"Más de Zelda": r"zelda", "Más de Marvel": r"vengadores|spider-man|daredevil", "Más de Star Wars": r"star-wars|ahsoka", "Más de DC": r"superman|batman",
         "Más carreras de Fórmula 1": r"(^|-)f1($|-)", "Más carreras de MotoGP": r"motogp", "Más de Pokémon": r"pokemon", "Más de Jujutsu Kaisen": r"jujutsu", "Más de Kusuriya no Hitorigoto": r"kusuriya",
         "Más de One Piece": r"one-piece", "Más de Final Fantasy": r"final-fantasy", "Más para Nintendo Switch 2": r"switch-2",
         "Más fiestas de Navidad": r"^(navidad|nochebuena|nochevieja|ano-nuevo|reyes|loteria-de-navidad|loteria-del-nino)$",
         "Las estaciones y el cambio de hora": r"^(primavera|verano|otono|invierno|cambio-de-hora)$", "Más lluvias de estrellas": r"leonidas|geminidas|cuadrantidas|liridas|perseidas",
         "Más eclipses y superlunas": r"eclipse|superluna", "Más tenis": r"roland-garros|wimbledon|mutua-madrid-open|atp-finals|copa-davis",
         "Más fútbol": r"supercopa|copa-del-rey|clasico|laliga|champions|europa-league|euroliga", "Más festivales de música": r"primavera-sound|sonar|mad-cool|bbk-live|^fib$|arenal|medusa|vina-rock|resurrection|cruilla",
         "Más premios de cine y música": r"oscar|goya|grammy", "Más maratones": r"maraton"}


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
    series = {e["serie"] for e in eventos if e.get("serie")}
    assert not series & (slugs | RESERVADOS), f"serie que choca con un slug: {series & (slugs | RESERVADOS)}"
    fijas = eventos_fijos()
    assert not {e["slug"] for e in fijas} & (slugs | series), "fecha señalada que choca con un evento"
    return eventos + fijas


def eventos_fijos():
    """Fechas que vuelven cada año (Navidad, Reyes, estaciones…), calculadas con el mismo módulo que festivosde."""
    spec = importlib.util.spec_from_file_location("cuanto_falta", FIJAS)
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
    fijas = []
    for slug, (nombre, _, _, texto) in cf.EVENTOS.items():
        proxima, siguientes = cf.proxima(slug, HOY)
        titulo = nombre.split(" ", 1)[1] if nombre.split(" ", 1)[0] in ("la", "el") else nombre
        fijas.append({"titulo": titulo[0].upper() + titulo[1:], "en_frase": nombre, "slug": slug, "categoria": "fechas",
                      "fecha": proxima.isoformat(), "precision": "dia", "fija": texto, "siguientes": [d.isoformat() for d in siguientes]})
    cambios = cf.proximo_cambio_de_hora(HOY)
    fijas.append({"titulo": "Cambio de hora", "en_frase": "el cambio de hora", "slug": "cambio-de-hora", "categoria": "fechas",
                  "fecha": cambios[0][0].isoformat(), "precision": "dia",
                  "fija": ("En España la hora cambia dos veces al año: el último domingo de marzo se adelanta (a las 2:00 pasan a ser las 3:00) "
                           "y el último domingo de octubre se atrasa (a las 3:00 vuelven a ser las 2:00)."),
                  "siguientes": [c[0].isoformat() for c in cambios[1:5]]})
    return fijas


def resolver_series(eventos):
    """Una página por serie (/fallas/) con la próxima edición; las demás ediciones redirigen a ella."""
    grupos, visibles, redirecciones = {}, [], []
    for e in eventos:
        grupos.setdefault(e.get("serie") or e["slug"], []).append(e)
    for clave, eds in grupos.items():
        futuras = [x for x in eds if orden(x)[0] < 2 and (fecha_de(x) is None or fecha_de(x) >= HOY)]
        elegida = min(futuras, key=orden) if futuras else max(eds, key=lambda x: x.get("fecha") or "")
        v = dict(elegida, slug=clave)
        visibles.append(v)
        redirecciones += [(x["slug"], clave) for x in eds if x["slug"] != clave]
    return visibles, redirecciones


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

def pagina(ruta, titulo, descripcion, cuerpo, ld=None, scripts="", buscador=True, imagen="/og/portada.png", indexable=True):
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
<link rel="canonical" href="{url}">{'' if indexable else chr(10) + '<meta name="robots" content="noindex, follow">'}
<meta name="theme-color" content="#111111">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NOMBRE_WEB}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMINIO}{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{ld_html}
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{CABECERA_ANUNCIOS}
</head>
<body>
<header class="cab"><div class="cont">
<a class="logo" href="/"><span class="logo-ico">⏳</span><span>cuantos<b>dias</b>faltan</span></a>
<form class="buscador buscador-cab{'' if buscador else ' oculto'}" role="search" onsubmit="return false"><input class="js-q" type="search" placeholder="Buscar: Navidad, GTA 6, Fallas…" autocomplete="off" aria-label="Buscar un evento"><ul class="sug"></ul></form>
<nav class="menu">{menu}</nav>
</div></header>
<main class="cont">
{cuerpo}
</main>
<footer class="pie"><div class="cont">
<p><strong>{NOMBRE_WEB}</strong>: cuántos días faltan para los próximos lanzamientos y eventos, con la fecha oficial y su fuente.</p>
<p class="enlaces"><a href="/">Inicio</a>{''.join(f'<a href="/{c}/">{n}</a>' for c, (n, _) in CATEGORIAS.items())}<a href="/cuanto-hace/">Cuánto hace</a><a href="/sobre-nosotros/">Sobre nosotros</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/contacto/">Contacto</a>{CONFIGURAR_COOKIES}</p>
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

def hora_de(e):
    """(día en España, «21:00», qué empieza, aproximada) si se conoce la hora de inicio en España."""
    if not e.get("hora") or not fecha_de(e):
        return None
    dia = dt.date.fromisoformat(e["hora_dia"]) if e.get("hora_dia") else fecha_de(e)
    return dia, e["hora"], e.get("hora_que") or "empieza", bool(e.get("hora_aprox"))


def texto_hora(e, corto=False):
    """«La carrera es a las 21:00 en España (20:00 en Canarias)»."""
    h = hora_de(e)
    if not h:
        return ""
    dia, hora, que, aprox = h
    momento_can = dt.datetime.combine(dia, dt.time.fromisoformat(hora)) - dt.timedelta(hours=1)
    canarias = momento_can.strftime("%H:%M")
    hora_txt, can_txt = hora.lstrip("0") if not hora.startswith("00") else "0" + hora[2:], canarias.lstrip("0") if not canarias.startswith("00") else "0" + canarias[2:]
    otro_dia = f"el {DIAS[dia.weekday()]} {dia.day} de {MESES[dia.month - 1]} " if dia != fecha_de(e) else ""
    if corto:
        return f"{otro_dia}a las {hora_txt}".strip()
    dia_can = f" del {DIAS[momento_can.weekday()]}" if momento_can.date() != dia else ""
    if e.get("hora_nota"):  # p. ej. un eclipse: la hora cambia según el lugar y en Canarias no es el mismo fenómeno
        return f"{que[0].upper() + que[1:]} es hacia las {hora_txt}, hora peninsular: {e['hora_nota']}"
    texto = f"{que[0].upper() + que[1:]} es {otro_dia}a las {hora_txt} en España ({can_txt}{dia_can} en Canarias)"
    return texto + (": es la hora habitual, aún sin confirmar" if aprox else "")


def contador(d, pasado=False, hora=None):
    """La cuenta atrás grande: el texto en meses y días se ve sin script; el script la pone en directo
    y deja elegir días, semanas o meses."""
    if pasado:
        n = (HOY - d).days
        principal = f"Hace {texto_tiempo(d, HOY)}"
    else:
        n = (d - HOY).days
        principal = "¡Es hoy!" if n == 0 else ("Falta 1 día" if n == 1 else f"Faltan {texto_tiempo(HOY, d)}")
    return (f'<div class="contador" data-fecha="{d.isoformat()}"{f' data-hora="{hora}"' if hora else ""} data-modo="{"hace" if pasado else "falta"}">'
            f'<p class="c-grande">{principal}</p>'
            f'<p class="c-dias">{f"<b>{n}</b> {plural_sin_n(n)} · " if principal_con_meses(d, pasado) else ""}{fecha_larga(d)}</p>'
            f'<p class="c-vivo"></p>'
            f'<div class="c-unidades" role="group" aria-label="Ver en"><button type="button" data-u="auto" aria-pressed="true">Meses</button>'
            f'<button type="button" data-u="semanas">Semanas</button><button type="button" data-u="dias">Días</button><button type="button" data-u="horas">Horas</button></div></div>')


def plural_sin_n(n):
    return "día" if n == 1 else "días"


def principal_con_meses(d, pasado):
    """Si el texto grande ya va en días («Faltan 24 días»), debajo basta la fecha."""
    m, _ = meses_y_dias(*((d, HOY) if pasado else (HOY, d)))
    return m > 0


def tarjeta(e):
    d = fecha_de(e)
    if d and d >= HOY:
        n = (d - HOY).days
        cifra, ud, cuando = n, "día" if n == 1 else "días", fecha_simple(e["fecha"]) + (f" · {texto_hora(e, corto=True)}" if hora_de(e) else "")
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
    largo = ' class="t-largo"' if len(str(cifra)) > 4 else ""
    return (f'<li><a href="/{e["slug"]}/"><span class="t-cifra"><b{largo}>{cifra}</b> {ud}</span><span class="t-tit">{ico} {escape(e["titulo"])}</span>'
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
    if c == "fechas":
        return f"¿Cuánto falta para {t}?", f"¿Cuánto falta para {t} {e['fecha'][:4]}? Días, horas y cuenta atrás"
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
        h = hora_de(e)
        bloque = contador(h[0], hora=h[1]) if h and h[0] >= HOY else contador(d)
        if h:
            sub += f' · <strong>{escape(texto_hora(e))}</strong>'
        n = (d - HOY).days
        tf = e.get("en_frase") or t
        desc = (f"¿Cuántos días faltan para {tf}? Faltan {n}: {fecha_larga(d)}. Cuenta atrás en directo en meses, semanas, días y horas."
                if e["categoria"] == "fechas" else
                f"Faltan {n} días para {tf}: {fecha_larga(d)}. Cuenta atrás en directo en meses, semanas, días y horas, con la fecha oficial.")
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
    if e.get("hora_fuente"):
        retrasos += f'<p class="fuente">Horario: <a href="{escape(e["hora_fuente"])}" rel="nofollow noopener" target="_blank">{escape(e["hora_fuente"].split("/")[2].removeprefix("www."))}</a>.</p>'
    if e.get("fija"):
        fuente = f'<p class="fuente">{escape(e["fija"])}</p>'
    else:
        fuente = (f'<p class="fuente">Fuente{"" if e.get("fuente_tipo") == "oficial" else " (medio)"}: <a href="{escape(e["fuente_url"])}" rel="nofollow noopener" target="_blank">'
                  f'{escape(e.get("fuente_nombre") or "anuncio oficial")}</a> · Comprobado el {fecha_simple(e["comprobado"])}.</p>')
    if not d and (estimada_de(e) or rango_de(e) or previsto(e)):
        fuente = f'<p class="nota">Por qué esta fecha: {escape(e["estimacion"])}. La cambiaremos por la oficial en cuanto se anuncie.</p>' + fuente
    objetivo = d if d and d >= HOY else estimada_de(e)
    url = f"{DOMINIO}/{e['slug']}/"
    t_frase = e.get("en_frase") or t
    botones = [f'<a class="boton" href="https://wa.me/?text={escape(f"¿Cuánto falta para {t_frase}? {url}")}" rel="noopener">💬 Compartir</a>',
               f'<button class="boton-sec" type="button" data-copiar="{url}">🔗 Copiar enlace</button>']
    if objetivo:
        botones.append(f'<button class="boton-sec" type="button" data-ics="{objetivo.isoformat()}|{escape(t)}|{url}">📅 Añadir al calendario</button>')
    datos, preguntas = datos_y_preguntas(e, d, objetivo, cab, donde)
    siguientes = ""
    if e.get("siguientes"):
        siguientes = ('<section><h2>Los próximos años</h2><ul class="lista-datos">'
                      + "".join(f"<li>{fecha_larga(dt.date.fromisoformat(x))}</li>" for x in e["siguientes"]) + "</ul></section>")
    sabe = ""
    if TEXTOS_EVENTO.get(e["slug"]):
        sabe = (f'<section class="texto"><h2>{"Sobre " + e["titulo"] if e.get("fija") else "Qué se sabe"}</h2>'
                + "".join(f"<p>{p}</p>" for p in TEXTOS_EVENTO[e["slug"]]) + "</section>")
    faq = ""
    if preguntas:
        faq = '<section class="faq"><h2>Preguntas frecuentes</h2>' + "".join(f"<h3>{escape(q)}</h3><p>{escape(r)}</p>" for q, r in preguntas) + "</section>"
    saga = next((n for n, rx in SAGAS.items() if re.search(rx, e["slug"])), None)
    de_saga = sorted([x for x in eventos if saga and x["slug"] != e["slug"] and re.search(SAGAS[saga], x["slug"])], key=orden)[:6]
    vistos = {x["slug"] for x in de_saga}
    otros = [x for x in eventos if x["categoria"] == e["categoria"] and x["slug"] != e["slug"] and x["slug"] not in vistos]
    otros = sorted(otros, key=orden)[:6]
    proximos = [x for x in sorted(eventos, key=orden) if x["categoria"] != e["categoria"] and fecha_de(x) and fecha_de(x) >= HOY][:4]
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › <a href="/{e['categoria']}/">{cat}</a></nav>
<h1>{escape(cab)}</h1>
<p class="sub">{sub}{f' · {escape(donde)}' if donde else ''}</p>
{respuesta_directa(e, d, objetivo)}
{bloque}
<p class="acciones">{"".join(botones)}</p>
{nota_ambito}{retrasos}{fuente}
{sabe}{datos}{siguientes}{faq}
{f'<section><h2>{saga}</h2>{lista_tarjetas(de_saga)}</section>' if de_saga else ''}
{f'<section><h2>{ico} Más {cat.lower()}</h2>{lista_tarjetas(otros)}<p><a href="/{e["categoria"]}/">Ver todos →</a></p></section>' if otros else ''}
{f'<section><h2>⏱️ También llega pronto</h2>{lista_tarjetas(proximos)}</section>' if proximos else ''}
<p class="nota">¿Esperas otra cosa? <a href="/#tu-cuenta">Crea tu propia cuenta atrás</a> y compártela.</p>"""
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"},
        {"@type": "ListItem", "position": 2, "name": cat, "item": f"{DOMINIO}/{e['categoria']}/"},
        {"@type": "ListItem", "position": 3, "name": t, "item": url}]}]
    ev_ld = evento_ld(e, d, url)
    if ev_ld:
        ld.append(ev_ld)
    if preguntas:  # las mismas preguntas que se ven en la página
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in preguntas]})
    return pagina(f"/{e['slug']}/", titulo, desc, cuerpo, ld, imagen=f"/og/{e['slug']}.png", indexable=indexable(e))


def evento_ld(e, d, url):
    """Event de schema.org para lo que es un evento con lugar (partidos, festivales, conciertos, fiestas)."""
    if e["categoria"] not in ("deportes", "musica", "fiestas", "eventos") or not d or not e.get("lugar") or e["lugar"] == "España":
        return None
    inicio = d.isoformat()
    h = hora_de(e)
    if h and not e.get("hora_aprox"):
        momento = dt.datetime.combine(h[0], dt.time.fromisoformat(h[1]))
        verano = dt.date(momento.year, 3, 31) - dt.timedelta(days=(dt.date(momento.year, 3, 31).weekday() + 1) % 7) <= momento.date() < \
            dt.date(momento.year, 10, 31) - dt.timedelta(days=(dt.date(momento.year, 10, 31).weekday() + 1) % 7)
        inicio = momento.strftime("%Y-%m-%dT%H:%M") + ("+02:00" if verano else "+01:00")
    texto = re.sub(r"<[^>]+>", "", " ".join(TEXTOS_EVENTO.get(e["slug"], [])[:1])) or e["titulo"]
    lugar = re.split(r"[;(]", e["lugar"])[0].strip(" ,")
    ld = {"@context": "https://schema.org", "@type": "Event", "name": e["titulo"], "startDate": inicio, "description": texto,
          "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "location": {"@type": "Place", "name": lugar, "address": lugar}, "image": f"{DOMINIO}/og/{e['slug']}.png", "url": url}
    # Fin: el del evento si dura varios días; si es de un día (una carrera, una final, una gala), el mismo.
    if e.get("fin"):
        ld["endDate"] = e["fin"]
    elif UN_DIA.search(e["slug"]):
        ld["endDate"] = inicio
    if e.get("organizador"):
        ld["organizer"] = {"@type": "Organization", "name": e["organizador"]["nombre"], "url": e["organizador"]["url"]}
    if e.get("artista"):
        ld["performer"] = {"@type": "MusicGroup", "name": e["artista"]}
    return ld


UN_DIA = re.compile(r"^(gp-|final-|super-bowl|eurovision|maraton|oscar|premios-goya|grammy|f1-|motogp-)")


def respuesta_directa(e, d, objetivo):
    """Una frase que responde sola a la búsqueda, con la fecha completa (que no caduca aunque Google guarde la página)."""
    tf = e.get("en_frase") or e["titulo"]
    if objetivo:
        n = (objetivo - HOY).days
        cuando = "hoy" if n == 0 else f"{'falta' if n == 1 else 'faltan'} {'unos ' if objetivo != d else ''}<strong>{plural(n, 'día', 'días')}</strong>"
        hora = f", {texto_hora(e, corto=True)} en España" if hora_de(e) and objetivo == d and hora_de(e)[0] == d else ""
        estimada = " (fecha estimada, aún no oficial)" if objetivo != d else ""
        frase = f"Hoy, {fecha_larga(HOY)}, {cuando} para {escape(tf)}: el {fecha_larga(objetivo)}{hora}{estimada}." if n else f"¡Es hoy! {escape(tf[0].upper() + tf[1:])}: {fecha_larga(objetivo)}{hora}."
    elif d:
        verbo = "se estrenó" if e["categoria"] in ("series", "anime", "peliculas") else "salió" if e["categoria"] in ("videojuegos", "tecnologia") else "fue"
        frase = f"{escape(tf[0].upper() + tf[1:])} {verbo} el {fecha_larga(d)}: hace {texto_tiempo(d, HOY)}."
    elif rango_de(e) or previsto(e):
        frase = f"Todavía no hay día oficial para {escape(tf)}: está previsto para {escape(e['ventana'])}."
    else:
        frase = f"Todavía no hay fecha oficial para {escape(tf)}."
    return f'<p class="respuesta">{frase}</p>'


UNA_VEZ = {"deportes", "musica", "fiestas", "eventos", "espacio"}  # categorías con eventos que pasan y ya no se buscan


def indexable(e):
    """Sin fecha, sin ventana y sin texto propio, la página casi no tiene nada que Google pueda enseñar: noindex
    (con follow) hasta que lo tenga; se indexa sola en cuanto haya fecha o texto."""
    d = fecha_de(e)
    if d and not e.get("serie") and e["categoria"] in UNA_VEZ and (HOY - d).days > 30:
        return False  # un concierto o un eclipse de hace más de un mes: ya nadie lo busca
    return bool(d or estimada_de(e) or rango_de(e) or previsto(e) or TEXTOS_EVENTO.get(e["slug"]))


def cuando_corto(e):
    """La fecha tal como va en la imagen de compartir (no cambia cada día, para que las redes la guarden)."""
    d = fecha_de(e)
    if d:
        texto = fecha_larga(d) + (f" · {texto_hora(e, corto=True)}" if hora_de(e) and hora_de(e)[0] == d else "")
    elif estimada_de(e):
        texto = f"≈ {fecha_larga(estimada_de(e))} (estimada)"
    elif rango_de(e) or previsto(e):
        texto = f"Previsto: {e['ventana']}"
    else:
        texto = e.get("ventana") or "Fecha por confirmar"
    return texto[0].upper() + texto[1:]


def imagenes_compartir(eventos):
    """Una imagen 1200×630 por evento para WhatsApp y redes: nombre, fecha y la web."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("AVISO: sin Pillow no se generan las imágenes de compartir")
        return
    negra, gruesa = (str(FUENTES / "Inter-Black.otf"), str(FUENTES / "Inter-Bold.otf"))
    (WEB / "og").mkdir(parents=True, exist_ok=True)

    def partir(texto, fuente, ancho, dibujo):
        lineas, actual = [], ""
        for palabra in texto.split():
            prueba = f"{actual} {palabra}".strip()
            if dibujo.textlength(prueba, font=fuente) <= ancho or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        return lineas + [actual]

    def dibujar(ruta, arriba, titulo, abajo):
        im = Image.new("RGB", (1200, 630), "#111111")
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 1200, 12), fill="#f97316")
        d.text((80, 70), arriba.upper(), font=ImageFont.truetype(gruesa, 30), fill="#a1a1aa")
        for tam in (84, 72, 62, 54, 46):
            f = ImageFont.truetype(negra, tam)
            lineas = partir(titulo, f, 1040, d)
            if len(lineas) <= 3:
                break
        y = 130
        for linea in lineas[:3]:
            d.text((80, y), linea, font=f, fill="#ffffff")
            y += int(tam * 1.15)
        fb = ImageFont.truetype(negra, 50 if len(abajo) < 34 else 40)
        d.text((80, max(y + 40, 330)), abajo, font=fb, fill="#f97316")
        pie = ImageFont.truetype(gruesa, 34)
        d.text((80, 545), "cuantos", font=pie, fill="#ffffff")
        x = 80 + d.textlength("cuantos", font=pie)
        d.text((x, 545), "dias", font=pie, fill="#f97316")
        x += d.textlength("dias", font=pie)
        d.text((x, 545), "faltan.es", font=pie, fill="#ffffff")
        d.text((1120 - d.textlength("Cuenta atrás en directo →", font=pie), 545), "Cuenta atrás en directo →", font=pie, fill="#a1a1aa")
        im.quantize(colors=48, method=Image.Quantize.MEDIANCUT).save(WEB / "og" / ruta, optimize=True)

    dibujar("portada.png", "Cuenta atrás", "¿Cuántos días faltan para…?", "Navidad, estrenos, partidos y fiestas")
    for e in eventos:
        titulo = preguntas_de(e)[0] if not fecha_de(e) or fecha_de(e) >= HOY else e["titulo"]
        dibujar(f"{e['slug']}.png", CATEGORIAS[e["categoria"]][0], titulo, cuando_corto(e))


def entre(desde, hasta, dias_semana):
    """Días entre hoy y la fecha (sin contar ninguno de los dos) que caen en esos días de la semana."""
    return sum(1 for k in range(1, (hasta - desde).days) if (desde + dt.timedelta(days=k)).weekday() in dias_semana)


def datos_y_preguntas(e, d, objetivo, cab, donde):
    """Datos calculados para la fecha (día de la semana, fines de semana, laborables…) y las preguntas frecuentes que se
    muestran en la página y van también como FAQPage."""
    t = e.get("en_frase") or e["titulo"]
    preguntas, datos = [], []
    fuente = "" if e.get("fija") else f", según {e.get('fuente_nombre') or 'el anuncio oficial'}"
    if objetivo:
        n = (objetivo - HOY).days
        estimada = objetivo != d
        aprox = "aproximadamente " if estimada else ""
        finde, laborables = entre(HOY, objetivo, {5}), entre(HOY, objetivo, {0, 1, 2, 3, 4})
        dia_mes = f"{objetivo.day} de {MESES[objetivo.month - 1]}"
        en_meses = texto_tiempo(HOY, objetivo)
        en_meses = "" if en_meses == plural(n, "día", "días") else en_meses
        semanas = f"{plural(n // 7, 'semana', 'semanas')}" + (f" y {plural(n % 7, 'día', 'días')}" if n % 7 else "")
        datos = [f"Cae en <strong>{DIAS[objetivo.weekday()]}</strong>, el día {objetivo.timetuple().tm_yday} del año {objetivo.year}.",
                 f"Faltan <strong>{plural(n, 'día', 'días')}</strong>: " + (f"{en_meses}, o " if en_meses else "") + f"{semanas}.",
                 f"Por el camino quedan <strong>{plural(finde, 'fin de semana', 'fines de semana')}</strong> y {plural(laborables, 'día', 'días')} de lunes a viernes.",
                 f'¿Es festivo ese día? Míralo en <a href="{FESTIVOSDE}/es-festivo/{objetivo.day}-de-{MESES[objetivo.month - 1]}/">¿Es festivo el {dia_mes}?</a>']
        cuenta = f"Hoy, {fecha_larga(HOY)}, faltan {aprox}{plural(n, 'día', 'días')}" + (f" ({en_meses})" if en_meses else "")
        if estimada:
            preguntas.append((cab, f"Aún no hay fecha oficial. La fecha estimada es el {fecha_larga(objetivo)}: {e['estimacion']}."))
        elif cab.startswith("¿Cuánto falta"):
            preguntas.append((cab, f"{cuenta}: es el {fecha_larga(objetivo)}{f' ({donde})' if donde else ''}{fuente}."))
        else:
            preguntas.append((cab, f"{e['titulo']}: {fecha_larga(objetivo)}{f' ({donde})' if donde else ''}{fuente}."))
        if estimada or not cab.startswith("¿Cuánto falta"):
            preguntas.append((f"¿Cuántos días faltan para {t}?", f"{cuenta}."))
        if hora_de(e) and not estimada:
            preguntas.append((f"¿A qué hora es {t} en España?", texto_hora(e) + "."))
            datos.insert(1, f"<strong>{escape(texto_hora(e))}</strong>.")
        preguntas.append((f"¿Qué día de la semana cae {t}?", f"Cae en {DIAS[objetivo.weekday()]}: {objetivo.day} de {MESES[objetivo.month - 1]} de {objetivo.year}."))
        preguntas.append((f"¿Cuántos fines de semana quedan hasta {t}?", f"Quedan {plural(finde, 'fin de semana', 'fines de semana')} y {plural(laborables, 'día', 'días')} de lunes a viernes."))
    elif d:
        preguntas.append((cab, f"{e['titulo']}: {fecha_larga(d)}{f' ({donde})' if donde else ''}, hace {texto_tiempo(d, HOY)}{fuente}."))
    elif rango_de(e) or previsto(e):
        preguntas.append((cab, f"Aún no hay día oficial: está previsto para {e['ventana']}. {e['estimacion']}."))
    lista = f'<section><h2>En datos</h2><ul class="lista-datos">{"".join(f"<li>{x}</li>" for x in datos)}</ul></section>' if datos else ""
    return lista, preguntas


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
    proximos = [e for e in sorted(eventos, key=orden) if fecha_de(e) and fecha_de(e) >= HOY and e["categoria"] != "fechas"][:8]
    vistos = {e["slug"] for e in proximos}
    secciones = ""
    for c, (n, ico) in CATEGORIAS.items():
        lista = [e for e in sorted(eventos, key=orden) if e["categoria"] == c and e["slug"] not in vistos][:6 if c == "fechas" else 4]
        if lista:
            secciones += f'<section><h2><a href="/{c}/">{ico} {n}</a></h2>{lista_tarjetas(lista)}<p><a href="/{c}/">Ver {"todas" if c == "fechas" else "todos"} →</a></p></section>'
    cuerpo = f"""<section class="portada"><h1>¿Cuántos días faltan para…?</h1>
<p class="sub">Cuenta atrás para Navidad, Reyes, el verano y los estrenos, partidos y fiestas que esperas, con la fecha oficial.</p>
<form class="buscador" role="search" onsubmit="return false"><input class="js-q" type="search" placeholder="Busca: Navidad, GTA 6, Fallas, Eurovisión…" autocomplete="off" aria-label="Buscar"><ul class="sug"></ul></form></section>
<section><h2>⏱️ Lo próximo</h2>{lista_tarjetas(proximos)}</section>
<section id="tu-cuenta" class="herramienta"><h2>🗓️ Tu cuenta atrás</h2>
<p>¿Tu cumpleaños, tu boda, tus vacaciones? Pon la fecha y comparte el enlace.</p>
<form onsubmit="return false"><input id="c-nombre" type="text" maxlength="60" placeholder="¿Para qué? (p. ej. Mis vacaciones)" aria-label="Nombre">
<input id="c-fecha" type="date" aria-label="Fecha"><label class="check"><input id="c-anual" type="checkbox"> Cada año</label>
<button class="boton" id="c-crear" type="button">Crear</button></form><div id="c-resultado"></div></section>
{secciones}
<section><h2>⌛ ¿Cuánto hace de…?</h2><p>Calcula cuánto tiempo ha pasado desde cualquier fecha: <a href="/cuanto-hace/">cuánto hace de…</a></p></section>"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NOMBRE_WEB, "url": DOMINIO + "/"}
    return pagina("/", "¿Cuántos días faltan para…? Navidad, estrenos y eventos: cuenta atrás",
                  "Cuántos días faltan para Navidad, Reyes, el verano, GTA 6, los próximos estrenos, partidos y fiestas, con la fecha oficial y una cuenta atrás en directo.",
                  cuerpo, ld, buscador=False)


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
<p>{NOMBRE_WEB} reúne en un solo sitio cuántos días faltan para las fechas señaladas (Navidad, Reyes, el verano…) y para los lanzamientos y eventos que más se esperan: videojuegos, películas, series, anime, deportes, música, fiestas y tecnología.</p>
<p>Las fechas señaladas se calculan con las reglas del calendario (por ejemplo, la Semana Santa a partir de la Pascua, y las estaciones con la posición del Sol), con el mismo método que <a href="{FESTIVOSDE}/">festivosde.es</a>, nuestra web de festivos.</p>
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
    contacto = f"""<h1>Contacto</h1><div class="texto">
<p>¿Ha cambiado una fecha, falta un evento o has visto un error? Escríbenos a <a href="mailto:{t['email']}">{t['email']}</a> y lo revisamos.</p>
<p>Si nos avisas de una fecha nueva, incluye el enlace al anuncio oficial: solo publicamos fechas con fuente.</p></div>"""
    for ruta, tit, cuerpo in (("/contacto/", "Contacto", contacto), ("/sobre-nosotros/", "Sobre nosotros", sobre), ("/aviso-legal/", "Aviso legal", aviso), ("/privacidad/", "Política de privacidad", privacidad)):
        guardar(ruta, pagina(ruta, f"{tit} | {NOMBRE_WEB}", f"{tit} de {NOMBRE_WEB}.", cuerpo))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Vuelve a la <a href="/">portada</a> y búscalo.</p>'))
    return ["/contacto/", "/sobre-nosotros/", "/aviso-legal/", "/privacidad/"]


def main():
    global TEXTOS_EVENTO
    TEXTOS_EVENTO = json.loads(TEXTOS.read_text(encoding="utf-8")) if TEXTOS.exists() else {}
    todos = cargar()
    eventos, redirecciones = resolver_series(todos)
    if len(eventos) < 10:
        sys.exit(f"ERROR: solo {len(eventos)} eventos")
    for e in todos:
        if (e.get("estimada") and not estimada_de(e)) or (e.get("rango") and dt.date.fromisoformat(e["rango"][1]) < HOY):
            print(f"AVISO: la estimación de {e['slug']} ya ha pasado; hay que revisarla")
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    for f in ("style.css", "cuenta.js"):
        shutil.copy(PLANTILLA / f, WEB / "assets" / f)
    for f in ("favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        shutil.copy(PLANTILLA / f, WEB / f)
    rutas = ["/"]
    guardar("/", pagina_portada(eventos))
    for c in CATEGORIAS:
        if any(e["categoria"] == c for e in eventos):
            guardar(f"/{c}/", pagina_categoria(c, eventos))
            rutas.append(f"/{c}/")
    for e in eventos:
        guardar(f"/{e['slug']}/", pagina_evento(e, eventos))
        if indexable(e):
            rutas.append(f"/{e['slug']}/")
    for clave in set(TEXTOS_EVENTO) - {e["slug"] for e in eventos}:
        print(f"AVISO: textos.json tiene «{clave}», que no es ninguna página")
    imagenes_compartir(eventos)
    guardar("/cuanto-hace/", pagina_cuanto_hace(eventos))
    rutas.append("/cuanto-hace/")
    rutas += legales()
    hoy = HOY.isoformat()
    # fecha en que cambian de verdad los datos de cada evento (no la de cada noche), para que Google se fíe del sitemap
    modificado = {f"/{e['slug']}/": e["comprobado"] for e in eventos if e.get("comprobado")}
    (WEB / "_redirects").write_text("".join(f"/{a}/ /{b}/ 301\n/{a} /{b}/ 301\n" for a, b in redirecciones), encoding="utf-8")
    (WEB / "indice.json").write_text(json.dumps([[e["titulo"], e["slug"], CATEGORIAS[e["categoria"]][1]] for e in sorted(eventos, key=orden)],
                                                ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{modificado.get(r, hoy)}</lastmod></url>\n" for r in rutas) + "</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    con_fecha = sum(1 for e in eventos if fecha_de(e))
    print(f"Web generada: {len(eventos)} eventos ({con_fecha} con fecha), {len(redirecciones)} redirecciones, {len(rutas)} páginas en el sitemap.")


if __name__ == "__main__":
    main()
