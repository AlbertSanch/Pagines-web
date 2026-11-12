#!/usr/bin/env python3
"""¿Qué fue antes?: juego diario de ordenar momentos de la historia en una línea del tiempo.

Lee data/hechos.json (los hechos), data/verificacion.json (cuáles están comprobados) y data/dias.json (qué hechos
salen cada día; lo crea scripts/programar.py) y genera la web estática en web/.

Páginas:
  /                       el juego del día
  /practica/              partidas con hechos al azar
  /archivo/               días anteriores (se pueden volver a jugar)
  /hechos/                todos los hechos, por épocas
  /hechos/<slug>/         «¿En qué año…?»: el año, la explicación, qué más pasó por entonces y la fuente
  /como-se-juega/, /sobre-nosotros/, /contacto/, /aviso-legal/, /privacidad/, /cookies/

Uso: python cronologia/scripts/generar_web.py   (CRONO_HOY=AAAA-MM-DD para probar otro día)
"""
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
PLANTILLA = RAIZ / "plantilla"
WEB = RAIZ / "web"

DOMINIO = "https://quefueantes.es"  # provisional: cámbialo cuando esté decidido el nombre
SITIO = "¿Qué fue antes?"
LANZAMIENTO = dt.date(2026, 11, 23)  # día #1
DOMINIO_ACTIVO = False  # True cuando el dominio funcione: la dirección .pages.dev redirigirá a él
SAL = "qfa-31b7"  # la misma en plantilla/juego.js
VERSION = "1"
HOY = dt.date.fromisoformat(os.environ["CRONO_HOY"]) if os.environ.get("CRONO_HOY") else dt.datetime.now(ZoneInfo("Europe/Madrid")).date()

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
           "email": "contacto.ahorrometro@gmail.com"}  # provisional, hasta tener el correo del dominio
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
CATEGORIAS = {"historia": "Historia", "ciencia": "Ciencia", "inventos": "Inventos", "tecnologia": "Tecnología", "espacio": "Espacio",
              "arte": "Arte y monumentos", "literatura": "Literatura", "musica": "Música", "cine": "Cine", "television": "Televisión",
              "deporte": "Deporte", "videojuegos": "Videojuegos", "juguetes": "Juguetes", "marcas": "Marcas", "transporte": "Transporte",
              "ocio": "Ocio"}
EPOCAS = [(-10**9, -3000, "Prehistoria"), (-3000, 476, "Edad Antigua"), (476, 1492, "Edad Media"), (1492, 1789, "Edad Moderna"),
          (1789, 1900, "Siglo XIX"), (1900, 1950, "Primera mitad del siglo XX"), (1950, 2000, "Segunda mitad del siglo XX"), (2000, 10**6, "Siglo XXI")]


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def numero(d):
    return (d - LANZAMIENTO).days + 1


def anio_txt(h):
    if h.get("anio_texto"):
        return h["anio_texto"]
    return f'{-h["anio"]} a. C.' if h["anio"] < 0 else str(h["anio"])


def epoca(h):
    return next(n for a, b, n in EPOCAS if a <= h["anio"] < b)


def wiki_url(h):
    return "https://es.wikipedia.org/wiki/" + h["wiki"].replace(" ", "_")


# ---------------------------------------------------------------- datos

def cargar():
    hechos = json.loads((DATOS / "hechos.json").read_text(encoding="utf-8"))
    ver = json.loads((DATOS / "verificacion.json").read_text(encoding="utf-8")) if (DATOS / "verificacion.json").exists() else {}
    dias = json.loads((DATOS / "dias.json").read_text(encoding="utf-8")) if (DATOS / "dias.json").exists() else {}
    return hechos, ver, dias


def validar(hechos, ver, dias):
    errores, slugs = [], set()
    for h in hechos:
        s = h.get("slug", "?")
        for campo in ("slug", "anio", "emoji", "ambito", "categoria", "tarjeta", "pregunta", "explicacion", "wiki"):
            if h.get(campo) in (None, ""):
                errores.append(f"{s}: falta «{campo}»")
        if s in slugs:
            errores.append(f"{s}: slug repetido")
        slugs.add(s)
        if not re.fullmatch(r"[a-z0-9-]+", s):
            errores.append(f"{s}: el slug solo puede tener minúsculas, números y guiones")
        if h.get("categoria") not in CATEGORIAS:
            errores.append(f"{s}: categoría desconocida «{h.get('categoria')}»")
        if h.get("ambito") not in ("espana", "mundo"):
            errores.append(f"{s}: el ámbito tiene que ser «espana» o «mundo»")
        if len(h.get("tarjeta", "")) > 60:
            errores.append(f"{s}: la tarjeta es demasiado larga ({len(h['tarjeta'])} caracteres; máximo 60)")
    por_slug = {h["slug"]: h for h in hechos}
    for f, lista in dias.items():
        for x in lista:
            if x not in por_slug:
                errores.append(f"día {f}: el hecho «{x}» no existe")
            elif not ver.get(x, {}).get("ok"):
                errores.append(f"día {f}: el hecho «{x}» no está comprobado (ejecuta scripts/verificar.py)")
        if len({por_slug[x]["anio"] for x in lista if x in por_slug}) != len(lista):
            errores.append(f"día {f}: hay dos hechos del mismo año")
    if errores:
        sys.exit("ERRORES en los datos:\n  " + "\n  ".join(errores))


def codificar(obj, clave):
    """JSON → bytes XOR clave → base64. No es cifrado: solo evita leer las respuestas a simple vista."""
    datos = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    k = clave.encode("utf-8")
    return base64.b64encode(bytes(b ^ k[i % len(k)] for i, b in enumerate(datos))).decode("ascii")


def token(fecha):
    return hashlib.sha256(f"{SAL}{fecha}".encode("utf-8")).hexdigest()[:20]


def tarjeta_juego(h):
    return {"t": h["tarjeta"], "e": h["emoji"], "a": h["anio"], "y": anio_txt(h), "s": h["slug"], "x": h["explicacion"]}


# ---------------------------------------------------------------- plantilla

REDIRIGIR = ('\n<script>if(/\\.pages\\.dev$|^www\\./.test(location.hostname))location.replace("' + DOMINIO + '"+location.pathname+location.search)</script>'
             if DOMINIO_ACTIVO else "")
HORIZONTE = (PLANTILLA / "horizonte.svg").read_text(encoding="utf-8") if (PLANTILLA / "horizonte.svg").exists() else ""
TIC = (PLANTILLA / "tic.svg").read_text(encoding="utf-8") if (PLANTILLA / "tic.svg").exists() else ""


def pagina(ruta, titulo, descripcion, cuerpo, ld=None, scripts="", indexable=True, clase="", escena=False):
    url = DOMINIO + ruta
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    fondo = f'<div class="escena" aria-hidden="true"><div class="estrellas"></div><div class="sol"></div>{HORIZONTE}<div class="suelo"></div></div>' if escena else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{url}">{'' if indexable else chr(10) + '<meta name="robots" content="noindex, follow">'}
<meta name="theme-color" content="#2b1748">{REDIRIGIR}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{escape(SITIO)}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMINIO}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fuentes/fredoka-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
{ld_html}
{CABECERA_ANUNCIOS}
</head>
<body class="{clase}">
{fondo}
<header class="cab"><div class="cont">
<a class="logo" href="/">¿Qué fue <b>antes?</b></a>
<nav class="menu"><a href="/">Hoy</a><a href="/practica/">Práctica</a><a href="/archivo/">Archivo</a><a href="/hechos/">Hechos</a></nav>
</div></header>
<main class="cont">
{cuerpo}
</main>
<footer class="pie"><div class="cont">
<p><strong>{escape(SITIO)}</strong>: cada día, seis momentos de la historia para colocar en su sitio en la línea del tiempo.</p>
<p class="enlaces"><a href="/">Jugar</a><a href="/practica/">Práctica</a><a href="/archivo/">Archivo</a><a href="/hechos/">Todos los hechos</a><a href="/como-se-juega/">Cómo se juega</a><a href="/sobre-nosotros/">Sobre nosotros</a><a href="/contacto/">Contacto</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a>{CONFIGURAR_COOKIES}</p>
</div></footer>
{scripts}
</body>
</html>
"""


def migas(lista):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMINIO + r} for i, (n, r) in enumerate(lista)]}


def faq_ld(preguntas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for q, r in preguntas]}


def faq_html(preguntas):
    return '<section class="faq"><h2>Preguntas frecuentes</h2>' + "".join(f"<details><summary>{escape(q)}</summary><p>{r}</p></details>" for q, r in preguntas) + "</section>"


JUEGO_JS = f'<script src="/assets/juego.js?v={VERSION}" defer></script>'


def bloque_juego(modo):
    return f"""<section class="juego" id="juego" data-modo="{modo}" data-lanzamiento="{LANZAMIENTO.isoformat()}">
<div class="tablero" aria-live="polite"><p class="cargando">Cargando la partida… Si no aparece, comprueba que tienes JavaScript activado.</p></div>
<div class="tic-zona" aria-hidden="true"><div class="bocadillo" id="bocadillo">¡Tic, tac! ¿Empezamos?</div><div class="tic" id="tic">{TIC}</div></div>
</section>"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- páginas

def pagina_portada():
    n = max(numero(HOY), 1)
    preguntas = [
        ("¿Cómo se juega?", "Cada día hay seis momentos de la historia. El primero ya está en la línea del tiempo; los otros cinco te salen de uno en uno y tienes que tocar el hueco donde encajan: antes, entre medias o después de los que ya están."),
        ("¿Cuándo cambian los hechos?", "Cada día a las 00:00, hora peninsular española. Todos los jugadores tienen los mismos seis."),
        ("¿Puedo jugar a días anteriores?", 'Sí, en el <a href="/archivo/">archivo</a>. Y si te quedas con ganas, en el <a href="/practica/">modo práctica</a> te salen hechos al azar.'),
        ("¿De dónde salen los años?", 'Cada hecho está comprobado con su artículo de Wikipedia en español, que enlazamos en su ficha. Puedes verlos todos en <a href="/hechos/">hechos</a>.'),
    ]
    cuerpo = f"""<section class="portada">
<p class="etq">Juego diario · En español · Gratis</p>
<h1>¿Qué fue antes?</h1>
<p class="sub">Coloca cada momento de la historia en su sitio de la línea del tiempo.</p>
<p class="dia">Día <strong class="js-numero">#{n}</strong> · <span class="js-fecha">{fecha_larga(HOY)}</span></p>
</section>
{bloque_juego("diario")}
<section class="stats-bloque" id="estadisticas-bloque" hidden><h2>Tus estadísticas</h2><div id="estadisticas"></div></section>
<section class="texto"><h2>Cómo se juega</h2>
<ol><li>Mira el primer hecho: ya está en la línea del tiempo, con su año.</li><li>Te sale otro hecho. Toca el hueco donde crees que va: antes, entre medias o después.</li>
<li>Si aciertas, se queda en su sitio. Si fallas, salta a su lugar correcto y se marca en rojo.</li><li>Son cinco hechos por día. Al terminar verás todos los años y podrás compartir tu resultado sin destripar nada.</li></ol>
<p>Más detalles en <a href="/como-se-juega/">cómo se juega</a>.</p></section>
{faq_html(preguntas)}"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITIO, "url": DOMINIO + "/"}, faq_ld(preguntas)]
    return pagina("/", "¿Qué fue antes? El juego diario de la línea del tiempo",
                  "Cada día, seis momentos de la historia para ordenar en una línea del tiempo: inventos, música, cine, deporte e historia de España y del mundo. Juego gratis.",
                  cuerpo, ld, scripts=JUEGO_JS, clase="con-escena", escena=True)


def pagina_practica(n_hechos):
    cuerpo = f"""<section class="portada"><h1>Modo práctica</h1>
<p class="sub">Partidas con hechos al azar entre los {n_hechos} que tenemos. No cuentan para tus estadísticas ni tu racha.</p></section>
{bloque_juego("practica")}"""
    return pagina("/practica/", "Modo práctica: ordena la historia sin esperar | ¿Qué fue antes?",
                  "Juega todas las partidas que quieras a ordenar momentos de la historia en la línea del tiempo, con hechos al azar.",
                  cuerpo, [migas([("Inicio", "/"), ("Modo práctica", "/practica/")])], scripts=JUEGO_JS, clase="con-escena", escena=True)


def lista_tarjetas(hs, enlazar=True):
    return '<ol class="linea-lista">' + "".join(
        f'<li><span class="ano">{escape(anio_txt(h))}</span><span class="em">{h["emoji"]}</span>'
        + (f'<a href="/hechos/{h["slug"]}/">{escape(h["tarjeta"])}</a>' if enlazar else escape(h["tarjeta"])) + "</li>"
        for h in sorted(hs, key=lambda x: x["anio"])) + "</ol>"


def pagina_archivo(pasados, por_slug):
    filas = "".join(
        f'<details class="dia-archivo"><summary><b>#{numero(f)}</b> · {fecha_larga(f)} <a class="jugar" href="/?d={f.isoformat()}">Jugar</a></summary>'
        f'{lista_tarjetas([por_slug[s] for s in lista])}</details>'
        for f, lista in sorted(pasados.items(), reverse=True))
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › Archivo</nav>
<h1>Archivo de días anteriores</h1>
<p class="sub">Vuelve a jugar cualquier día o mira cómo quedó su línea del tiempo. El día de hoy aparece aquí mañana.</p>
{filas or '<p>Aquí aparecerán los días anteriores a partir del día siguiente al lanzamiento.</p>'}"""
    return pagina("/archivo/", "Archivo: juega los días anteriores | ¿Qué fue antes?",
                  "Todos los días anteriores de ¿Qué fue antes?, para volver a jugarlos o ver su línea del tiempo con los años.", cuerpo,
                  [migas([("Inicio", "/"), ("Archivo", "/archivo/")])])


def pagina_hecho(h, hechos):
    cerca = sorted((x for x in hechos if x is not h and abs(x["anio"] - h["anio"]) <= max(15, abs(h["anio"]) // 50)),
                   key=lambda x: abs(x["anio"] - h["anio"]))[:6]
    antes = max((x for x in hechos if x["anio"] < h["anio"]), key=lambda x: x["anio"], default=None)
    despues = min((x for x in hechos if x["anio"] > h["anio"]), key=lambda x: x["anio"], default=None)
    misma_cat = [x for x in hechos if x["categoria"] == h["categoria"] and x is not h]
    respuesta = anio_txt(h)
    preguntas = [(h["pregunta"], f'{respuesta[:1].upper()}{respuesta[1:]}. {h["explicacion"]}')]
    if antes:
        preguntas.append((f"¿Qué fue antes, «{h['tarjeta']}» o «{antes['tarjeta']}»?",
                          f"Fue antes «{antes['tarjeta']}» ({anio_txt(antes)}); «{h['tarjeta']}» llegó en {respuesta}."))
    if despues:
        preguntas.append((f"¿Qué fue antes, «{h['tarjeta']}» o «{despues['tarjeta']}»?",
                          f"Fue antes «{h['tarjeta']}» ({respuesta}); «{despues['tarjeta']}» llegó en {anio_txt(despues)}."))
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › <a href="/hechos/">Hechos</a> › {escape(h["tarjeta"])}</nav>
<article class="ficha">
<p class="etq">{escape(CATEGORIAS[h["categoria"]])} · {"España" if h["ambito"] == "espana" else "Mundo"} · {escape(epoca(h))}</p>
<h1>{escape(h["pregunta"])}</h1>
<div class="respuesta"><span class="em">{h["emoji"]}</span><div><p class="r-ano">{escape(respuesta)}</p><p class="r-txt">{escape(h["tarjeta"])}</p></div></div>
<p class="lead">{escape(h["explicacion"])}</p>
{f'<section><h2>Qué más pasó por esa época</h2>{lista_tarjetas(cerca + [h])}</section>' if cerca else ''}
{f'<section><h2>Más de {escape(CATEGORIAS[h["categoria"]].lower())} en la línea del tiempo</h2>{lista_tarjetas(misma_cat[:8] + [h])}</section>' if misma_cat else ''}
{faq_html(preguntas)}
<p class="fuente">Fuente: <a href="{escape(wiki_url(h))}" rel="nofollow noopener" target="_blank">Wikipedia, «{escape(h["wiki"])}»</a>. ¿Has visto un error? Escríbenos a {TITULAR['email']}.</p>
<p class="boton-linea"><a class="boton" href="/">⏳ Juega al de hoy</a> <a class="boton sec" href="/practica/">🎯 Modo práctica</a></p>
</article>"""
    titulo = f"{h['pregunta']} | {SITIO}"
    if len(titulo) > 70:
        titulo = h["pregunta"]
    desc = f"{respuesta[:1].upper()}{respuesta[1:]}: {h['explicacion']}"
    if len(desc) > 155:
        desc = desc[:152].rsplit(" ", 1)[0] + "…"
    return pagina(f"/hechos/{h['slug']}/", titulo, desc, cuerpo,
                  [migas([("Inicio", "/"), ("Hechos", "/hechos/"), (h["tarjeta"], f"/hechos/{h['slug']}/")]), faq_ld(preguntas)])


def pagina_hechos(hechos):
    bloques = ""
    for a, b, nombre in EPOCAS:
        hs = [h for h in hechos if a <= h["anio"] < b]
        if hs:
            bloques += f"<section><h2>{escape(nombre)}</h2>{lista_tarjetas(hs)}</section>"
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › Hechos</nav>
<h1>Todos los hechos, en orden</h1>
<p class="sub">Los {len(hechos)} momentos de la historia que salen en el juego, de más antiguo a más reciente. Cada uno tiene su ficha con el año, qué pasó y su fuente.</p>
{bloques}"""
    return pagina("/hechos/", "Línea del tiempo de la historia: inventos, cine, música y deporte | ¿Qué fue antes?",
                  f"{len(hechos)} momentos de la historia de España y del mundo ordenados en una línea del tiempo, con su año y su explicación.", cuerpo,
                  [migas([("Inicio", "/"), ("Hechos", "/hechos/")])])


def pagina_como():
    preguntas = [
        ("¿A qué hora cambian los hechos?", "A las 00:00 de la hora peninsular española, para todo el mundo a la vez."),
        ("¿Qué pasa si dos hechos son del mismo año?", "No pasa: cada día los seis hechos son de años distintos."),
        ("¿Se guardan mis partidas?", "Sí, en tu propio navegador: si recargas la página sigues donde lo dejaste. Tus estadísticas no salen de tu dispositivo."),
    ]
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › Cómo se juega</nav>
<h1>Cómo se juega a ¿Qué fue antes?</h1>
<div class="texto">
<p>Cada día hay seis momentos de la historia, los mismos para todos: inventos, canciones, películas, deporte, monumentos y momentos clave de la historia de España y del mundo.</p>
<h2>La línea del tiempo</h2>
<p>El primer hecho ya está colocado, con su año. Los otros cinco te salen de uno en uno, sin año. Toca el hueco donde crees que encaja y pulsa «Colocar». Si aciertas, se queda en su sitio y se ve su año; si fallas, salta a su lugar correcto y se marca en rojo. Cada hecho colocado te ayuda con los siguientes.</p>
<h2>La puntuación</h2>
<p>Un punto por cada hecho bien colocado: de 0 a 5. Al terminar puedes compartir tu resultado sin desvelar los hechos:</p>
<pre class="ejemplo">¿Qué fue antes? #12
🟩🟩🟥🟩🟩 4/5
{DOMINIO.replace("https://", "")}</pre>
<h2>Tic</h2>
<p>Tic es el relojito que te acompaña: camina por la línea del tiempo hasta la época de cada hecho que colocas, de los dinosaurios a los cohetes.</p>
</div>
{faq_html(preguntas)}"""
    return pagina("/como-se-juega/", "Cómo se juega a ¿Qué fue antes?",
                  "Las reglas: seis hechos al día, colócalos en la línea del tiempo, un punto por acierto y comparte tu resultado.", cuerpo,
                  [migas([("Inicio", "/"), ("Cómo se juega", "/como-se-juega/")]), faq_ld(preguntas)])


def legales():
    t = TITULAR
    paginas = {
        "/sobre-nosotros/": ("Sobre nosotros", f"""<p>{escape(SITIO)} es un juego diario gratuito hecho en España: cada día proponemos seis momentos de la historia para colocar en una línea del tiempo, iguales para todos los jugadores.</p>
<p>Escribimos cada hecho nosotros y comprobamos su año con su artículo de Wikipedia en español, que enlazamos en la ficha de cada hecho. Cuando la fecha es aproximada (la prehistoria o la Antigüedad), lo decimos.</p>
<p>¿Has visto un error o quieres proponer un hecho? Escríbenos a {t['email']}.</p>"""),
        "/contacto/": ("Contacto", f"""<p>Para avisar de un error, proponer hechos o cualquier otra cosa, escríbenos a <a href="mailto:{t['email']}">{t['email']}</a>.</p>
<p>Si nos avisas de un año que crees que está mal, indica el hecho y, si puedes, una fuente: lo revisamos y lo corregimos.</p>"""),
        "/aviso-legal/": ("Aviso legal", f"""<h2>Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE): titular {t['nombre']}, NIF {t['nif']}, domicilio en {t['domicilio']}, correo {t['email']}, sitio web {DOMINIO}.</p>
<h2>Objeto</h2><p>{escape(SITIO)} ofrece gratuitamente un juego de ordenar hechos históricos y fichas informativas sobre ellos. No requiere registro.</p>
<h2>Responsabilidad</h2><p>La información se ofrece con fines de entretenimiento e informativos y se revisa con cuidado, pero puede contener errores. Las marcas citadas pertenecen a sus titulares; esta web no está vinculada a ellos.</p>
<h2>Propiedad intelectual</h2><p>Los textos, el diseño, los dibujos y el código de esta web pertenecen al titular.</p>
<h2>Legislación aplicable</h2><p>Estas condiciones se rigen por la legislación española.</p>"""),
        "/privacidad/": ("Política de privacidad", f"""<h2>Responsable</h2><p>{t['nombre']} ({t['email']}).</p>
<h2>Qué datos tratamos</h2><p>Esta web no tiene registro ni formularios. Tus partidas y estadísticas se guardan solo en tu navegador (almacenamiento local) y no se envían a ningún servidor.</p>
<p>El alojamiento (Cloudflare) puede registrar datos técnicos de la conexión, como la dirección IP, por seguridad, y ofrece estadísticas de visitas sin cookies.</p>
<h2>Publicidad</h2><p>Esta web se financia con publicidad de Google AdSense (Google Ireland Limited). Consulta la <a href="/cookies/">política de cookies</a>.</p>
<h2>Destinatarios</h2><p>No cedemos datos a terceros salvo obligación legal. Google y Cloudflare pueden tratar datos como proveedores del servicio, algunos fuera del Espacio Económico Europeo con las garantías del RGPD.</p>
<h2>Tus derechos</h2><p>Puedes ejercer tus derechos de acceso, rectificación, supresión y demás escribiendo a {t['email']}, y reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p>"""),
        "/cookies/": ("Política de cookies", """<p>Una cookie es un pequeño archivo que una web guarda en tu navegador.</p>
<h2>Cookies propias</h2><p>No usamos cookies propias. El juego guarda tu progreso y tus estadísticas en el almacenamiento local de tu navegador, que no se envía a ningún servidor.</p>
<h2>Cookies de terceros: publicidad</h2><p>Google AdSense, de Google Ireland Limited, usa cookies para mostrar anuncios, medir su rendimiento y, si lo aceptas, personalizarlos.</p>
<p>La primera vez que entras se muestra el mensaje de consentimiento de Google, donde puedes aceptar, rechazar o elegir qué finalidades permites. Puedes cambiar tu elección con el enlace «Configurar cookies» del pie de página.</p>
<p>Más información: <a href="https://policies.google.com/technologies/ads?hl=es" rel="noopener">cómo usa Google las cookies en la publicidad</a>.</p>"""),
    }
    for ruta, (tit, html) in paginas.items():
        guardar(ruta, pagina(ruta, f"{tit} | {SITIO}", f"{tit} de {SITIO}.", f'<h1>{tit}</h1><div class="texto">{html}</div>'))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Vuelve a la <a href="/">portada</a> y juega al de hoy.</p>', indexable=False))
    return list(paginas)


# ---------------------------------------------------------------- main

def main():
    hechos, ver, dias = cargar()
    validar(hechos, ver, dias)
    buenos = [h for h in hechos if ver.get(h["slug"], {}).get("ok")]
    por_slug = {h["slug"]: h for h in hechos}
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets" / "fuentes").mkdir(parents=True)
    (WEB / "d").mkdir()
    (WEB / "assets" / "style.css").write_text((PLANTILLA / "fuentes" / "fuentes.css").read_text(encoding="utf-8")
                                              + (PLANTILLA / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copy(PLANTILLA / "juego.js", WEB / "assets" / "juego.js")
    for f in (PLANTILLA / "fuentes").glob("*.woff2"):
        shutil.copy(f, WEB / "assets" / "fuentes" / f.name)
    for f in ("favicon.svg", "og.png"):
        if (PLANTILLA / f).exists():
            shutil.copy(PLANTILLA / f, WEB / f)

    # días: pasados (archivo), hoy y mañana; nunca más allá
    publicados = {}
    for f, lista in dias.items():
        d = dt.date.fromisoformat(f)
        if LANZAMIENTO <= d <= HOY + dt.timedelta(days=1):
            clave = SAL + f
            contenido = {"f": f, "n": numero(d), "x": codificar([tarjeta_juego(por_slug[s]) for s in lista], clave)}
            (WEB / "d" / f"{token(f)}.json").write_text(json.dumps(contenido, separators=(",", ":")), encoding="utf-8")
            publicados[d] = lista
    (WEB / "d" / "practica.json").write_text(json.dumps({"x": codificar([tarjeta_juego(h) for h in buenos], SAL + "practica")},
                                                        separators=(",", ":")), encoding="utf-8")

    rutas = ["/"]
    guardar("/", pagina_portada())
    guardar("/practica/", pagina_practica(len(buenos)))
    rutas.append("/practica/")
    pasados = {d: lista for d, lista in publicados.items() if d < HOY}
    guardar("/archivo/", pagina_archivo(pasados, por_slug))
    rutas.append("/archivo/")
    guardar("/hechos/", pagina_hechos(buenos))
    rutas.append("/hechos/")
    for h in buenos:
        guardar(f"/hechos/{h['slug']}/", pagina_hecho(h, buenos))
        rutas.append(f"/hechos/{h['slug']}/")
    guardar("/como-se-juega/", pagina_como())
    rutas.append("/como-se-juega/")
    rutas += legales()

    hoy = HOY.isoformat()
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoy if r in ('/', '/archivo/') else LANZAMIENTO.isoformat()}</lastmod></url>\n" for r in rutas)
                                     + "</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /d/\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (WEB / "_headers").write_text("/d/*\n  Cache-Control: no-cache\n  X-Robots-Tag: noindex\n/assets/*\n  Cache-Control: public, max-age=86400\n", encoding="utf-8")

    futuros = sorted(d for d in map(dt.date.fromisoformat, dias) if d >= HOY)
    if not futuros or (futuros[-1] - HOY).days < 14:
        print(f"AVISO: quedan pocos días programados (último: {futuros[-1] if futuros else 'ninguno'}). Ejecuta scripts/programar.py.")
    print(f"Web generada: {len(rutas)} páginas, {len(buenos)} hechos, {len(publicados)} días publicados.")


if __name__ == "__main__":
    main()
