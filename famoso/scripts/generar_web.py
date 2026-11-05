#!/usr/bin/env python3
"""Famoso del día (famosodeldia.es): genera la web estática a partir de data/mundial.json, data/espana.json y data/nombres.json.

Páginas:
  /                     los dos juegos del día (pestañas Mundial / España)
  /mundial/, /espana/   cada juego en su página
  /practica/            modo práctica con los famosos marcados «practica»
  /archivo/             famosos de días pasados y de práctica
  /famoso/<slug>/       ficha de cada famoso (los diarios, solo cuando su día ya ha pasado)
  /como-se-juega/, /sobre-nosotros/, /contacto/, /aviso-legal/, /privacidad/, /cookies/

Para que nadie vea las respuestas de días futuros, solo se publican los datos de los días pasados, de hoy y de mañana
(mañana hace falta para que el juego cambie a las 00:00 aunque el robot se retrase), cada día en un archivo con nombre
no adivinable y el contenido codificado. El juego elige el día con la hora de Madrid en el navegador.
"""
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
PLANTILLA = RAIZ / "plantilla"
WEB = RAIZ / "web"

DOMINIO = "https://famosodeldia.es"
SITIO = "Famoso del día"
LANZAMIENTO = dt.date(2026, 11, 9)  # día #1; cambia esta fecha si se lanza otro día
SAL = "fdd-7c1e"  # la misma en plantilla/juego.js: nombre y codificación de los archivos de cada día
VERSION = "3"
HOY = dt.date.fromisoformat(os.environ["FDD_HOY"]) if os.environ.get("FDD_HOY") else dt.datetime.now(ZoneInfo("Europe/Madrid")).date()  # FDD_HOY: solo para pruebas
# la bandera, dibujada: Windows no muestra los emojis de banderas (sale «ES»)
BANDERA = ('<svg class="bandera" viewBox="0 0 3 2" aria-hidden="true"><rect width="3" height="2" fill="#c60b1e"/>'
           '<rect y=".5" width="3" height="1" fill="#ffc400"/></svg>')
APARTADOS = {"mundial": ("Famoso mundial", "🌍"), "espana": ("Famoso español", BANDERA)}

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
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def numero(d):
    return (d - LANZAMIENTO).days + 1


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ñ ]", " ", t)).strip()


# ---------------------------------------------------------------- datos

def cargar():
    famosos = []
    for ap in APARTADOS:
        for e in json.loads((DATOS / f"{ap}.json").read_text(encoding="utf-8")):
            e["apartado"] = ap
            famosos.append(e)
    nombres = json.loads((DATOS / "nombres.json").read_text(encoding="utf-8"))
    return famosos, nombres


def validar(famosos, nombres):
    """Para antes de publicar nada roto: pistas, slugs, fechas y nombres del autocompletado."""
    errores, slugs, dias = [], set(), set()
    en_lista = {normalizar(n) for n in nombres}
    for e in famosos:
        s = e.get("slug", "?")
        for campo in ("slug", "nombre", "pistas", "resumen", "biografia", "fuente"):
            if not e.get(campo):
                errores.append(f"{s}: falta «{campo}»")
        if len(e.get("pistas", [])) != 6:
            errores.append(f"{s}: tiene {len(e.get('pistas', []))} pistas y deben ser 6")
        if s in slugs:
            errores.append(f"{s}: slug repetido")
        slugs.add(s)
        if not re.fullmatch(r"[a-z0-9-]+", s):
            errores.append(f"{s}: el slug solo puede tener minúsculas, números y guiones")
        if e.get("fecha"):
            try:
                f = dt.date.fromisoformat(e["fecha"])
            except ValueError:
                errores.append(f"{s}: fecha mal escrita ({e['fecha']}); formato AAAA-MM-DD")
                continue
            if (e["apartado"], f) in dias:
                errores.append(f"{s}: ya hay otro famoso {e['apartado']} el {e['fecha']}")
            dias.add((e["apartado"], f))
            if e.get("practica"):
                errores.append(f"{s}: no puede tener fecha y ser de práctica a la vez")
        elif not e.get("practica"):
            errores.append(f"{s}: necesita «fecha» o «practica»: true")
        if normalizar(e.get("nombre", "")) not in en_lista:
            errores.append(f"{s}: «{e.get('nombre')}» no está en data/nombres.json (el autocompletado no lo sugeriría)")
    if errores:
        sys.exit("ERRORES en los datos:\n  " + "\n  ".join(errores))


def codificar(obj, clave):
    """JSON → bytes XOR clave → base64. No es cifrado fuerte: evita que la respuesta se lea a simple vista."""
    datos = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    k = clave.encode("utf-8")
    return base64.b64encode(bytes(b ^ k[i % len(k)] for i, b in enumerate(datos))).decode("ascii")


def ficha_juego(e):
    return {"n": e["nombre"], "a": e.get("alias", []), "p": e["pistas"], "r": e["resumen"], "s": e["slug"], "m": e.get("ambito", "")}


def token(fecha):
    return hashlib.sha256(f"{SAL}{fecha}".encode("utf-8")).hexdigest()[:20]


# ---------------------------------------------------------------- plantilla

def pagina(ruta, titulo, descripcion, cuerpo, ld=None, scripts="", indexable=True, clase=""):
    url = DOMINIO + ruta
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{url}">{'' if indexable else chr(10) + '<meta name="robots" content="noindex, follow">'}
<meta name="theme-color" content="#7a0f1d">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITIO}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMINIO}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
{ld_html}
{CABECERA_ANUNCIOS}
</head>
<body class="{clase}">
<header class="cab"><div class="cont">
<a class="logo" href="/"><span class="logo-ico">⭐</span> Famoso <b>del día</b></a>
<nav class="menu"><a href="/mundial/">🌍 Mundial</a><a href="/espana/">{BANDERA} España</a><a href="/practica/">🎯 Práctica</a><a href="/archivo/">📚 Archivo</a></nav>
</div></header>
<main class="cont">
{cuerpo}
</main>
<footer class="pie"><div class="cont">
<p><strong>{SITIO}</strong>: cada día, un famoso mundial y uno español para adivinar con seis pistas.</p>
<p class="enlaces"><a href="/">Jugar</a><a href="/practica/">Modo práctica</a><a href="/archivo/">Archivo de famosos</a><a href="/como-se-juega/">Cómo se juega</a><a href="/sobre-nosotros/">Sobre nosotros</a><a href="/contacto/">Contacto</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a>{CONFIGURAR_COOKIES}</p>
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


def bloque_juego(inicial, modo="diario"):
    """Contenedor del juego: lo rellena juego.js. El texto de dentro es lo que se ve sin JavaScript."""
    pestanas = "".join(f'<button type="button" class="pestana" role="tab" data-apartado="{ap}" aria-selected="{"true" if ap == inicial else "false"}">{ico} {n}</button>'
                       for ap, (n, ico) in APARTADOS.items())
    return f"""<section class="juego" id="juego" data-modo="{modo}" data-inicial="{inicial}" data-lanzamiento="{LANZAMIENTO.isoformat()}">
<div class="pestanas" role="tablist">{pestanas}</div>
<div class="tablero" aria-live="polite"><p class="cargando">Cargando el famoso… Si no aparece, comprueba que tienes JavaScript activado.</p></div>
</section>"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- páginas

def ficha_breve(e, publicado):
    """Enlace a la ficha si ya se puede ver."""
    return f'<a href="/famoso/{e["slug"]}/">{escape(e["nombre"])}</a>' if publicado else escape(e["nombre"])


def pagina_juego(ruta, apartado):
    n = numero(HOY)
    if ruta == "/":
        titulo = "Famoso del día: adivina el famoso con 6 pistas"
        desc = "Cada día, un famoso mundial y un famoso español para adivinar con seis pistas. Juega gratis, comparte tu resultado y mantén tu racha."
        h1 = "Adivina el famoso del día"
    elif apartado == "mundial":
        titulo = "Famoso mundial del día: adivina quién es con 6 pistas"
        desc = "Adivina el famoso mundial de hoy con seis pistas: deporte, música, cine, ciencia e historia. Un juego diario gratis."
        h1 = "Famoso mundial del día"
    else:
        titulo = "Famoso español del día: adivina quién es con 6 pistas"
        desc = "Adivina el famoso español de hoy con seis pistas: deportistas, artistas, actores y personajes históricos de España. Juego diario gratis."
        h1 = "Famoso español del día"
    preguntas = [
        ("¿Cuándo cambia el famoso del día?", "Cada día a las 00:00, hora peninsular española. Todos los jugadores tienen los mismos dos famosos."),
        ("¿Cómo se gana?", "Escribe el nombre del famoso. Si aciertas con la primera pista ganas 6 puntos; con cada pista más, uno menos. Si fallas las seis, 0 puntos."),
        ("¿Puedo jugar a famosos de otros días?", 'Sí: en el <a href="/practica/">modo práctica</a> hay famosos para jugar cuando quieras, y en el <a href="/archivo/">archivo</a> están las fichas de los famosos pasados.'),
    ]
    cuerpo = f"""<h1>{h1}</h1>
<p class="sub">Famoso del día <strong class="js-numero">#{max(n, 1)}</strong> · Seis pistas, de la más difícil a la más fácil. ¿Con cuántas lo adivinas?</p>
{bloque_juego(apartado)}
<section class="stats-bloque"><h2>Tus estadísticas</h2><div id="estadisticas"><p>Juega tu primera partida para ver tus estadísticas.</p></div></section>
<section class="texto"><h2>Cómo se juega</h2>
<ol><li>Lee la primera pista y escribe el nombre del famoso.</li><li>Si fallas o pulsas «Pasar», verás la siguiente pista, más fácil.</li>
<li>Tienes seis pistas: cuantas menos uses, más puntos.</li><li>Cuando termines, comparte tu resultado sin desvelar la respuesta y juega al otro famoso.</li></ol>
<p>Más detalles en <a href="/como-se-juega/">cómo se juega</a>. ¿Te has quedado con ganas? Prueba el <a href="/practica/">modo práctica</a>.</p></section>
{faq_html(preguntas)}"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITIO, "url": DOMINIO + "/"}, faq_ld(preguntas)] if ruta == "/" else \
        [migas([("Inicio", "/"), (h1, ruta)]), faq_ld(preguntas)]
    return pagina(ruta, titulo, desc, cuerpo, ld, scripts=JUEGO_JS)


def pagina_practica(practica):
    cuerpo = f"""<h1>Modo práctica: adivina famosos sin esperar</h1>
<p class="sub">{len(practica)} famosos para jugar cuando quieras. Las partidas de práctica no cuentan para tus estadísticas ni tu racha.</p>
{bloque_juego("mundial", modo="practica")}
<section class="texto"><h2>Famosos del modo práctica</h2><p>Cuando adivines uno, podrás leer su ficha con las pistas, su biografía y datos curiosos. Todas las fichas están en el <a href="/archivo/">archivo</a>.</p></section>"""
    return pagina("/practica/", "Modo práctica: adivina famosos con pistas | Famoso del día",
                  f"Juega a adivinar {len(practica)} famosos mundiales y españoles con seis pistas, sin esperar al famoso del día.", cuerpo,
                  [migas([("Inicio", "/"), ("Modo práctica", "/practica/")])], scripts=JUEGO_JS)


def pagina_ficha(e, pasados_por_slug):
    ap, (nombre_ap, ico) = e["apartado"], APARTADOS[e["apartado"]]
    nombre = e["nombre"]
    cuando = ""
    if e.get("fecha"):
        f = dt.date.fromisoformat(e["fecha"])
        cuando = f'<p class="sub">{ico} {nombre_ap} del día #{numero(f)} · {fecha_larga(f)}</p>'
    else:
        cuando = f'<p class="sub">{ico} {nombre_ap} · <a href="/practica/">modo práctica</a></p>'
    pistas = "".join(f"<li>{escape(p)}</li>" for p in e["pistas"])
    bio = "".join(f"<p>{escape(p)}</p>" for p in e["biografia"])
    curiosas = "".join(f"<li>{escape(c)}</li>" for c in e.get("curiosidades", []))
    preguntas = [(f"¿Quién es {nombre}?", escape(e["resumen"])),
                 (f"¿Cuándo nació {nombre}?", escape(e["pistas"][0])),
                 (f"¿Dónde nació {nombre}?", escape(e["pistas"][3]))]
    otros = [x for x in pasados_por_slug.values() if x["slug"] != e["slug"] and x["apartado"] == ap][:6]
    rel = "".join(f'<li><a href="/famoso/{x["slug"]}/">{escape(x["nombre"])}</a></li>' for x in otros)
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › <a href="/archivo/">Archivo</a> › {escape(nombre)}</nav>
<h1>{escape(nombre)}</h1>
{cuando}
<p class="lead">{escape(e["resumen"])}</p>
<section class="texto"><h2>Las 6 pistas</h2><ol class="pistas-ficha">{pistas}</ol></section>
<section class="texto"><h2>Biografía de {escape(nombre)}</h2>{bio}</section>
{f'<section class="texto"><h2>Datos curiosos</h2><ul>{curiosas}</ul></section>' if curiosas else ''}
{faq_html(preguntas)}
<p class="fuente">Fuente: <a href="{escape(e["fuente"])}" rel="nofollow noopener" target="_blank">{escape(e["fuente"].split("/")[2])}</a>. Si ves un error, escríbenos a {TITULAR['email']}.</p>
<p class="boton-linea"><a class="boton" href="/">⭐ Juega al famoso de hoy</a> <a class="boton sec" href="/practica/">🎯 Modo práctica</a></p>
{f'<section><h2>Más famosos</h2><ul class="lista-famosos">{rel}</ul></section>' if rel else ''}"""
    persona = {"@context": "https://schema.org", "@type": "Person", "name": nombre, "description": e["resumen"], "sameAs": [e["fuente"]]}
    titulo = f"{nombre}: biografía, pistas y datos curiosos | {SITIO}"
    if len(titulo) > 70:
        titulo = f"{nombre}: biografía y datos curiosos"
    desc = e["resumen"]
    if len(desc) > 155:
        desc = desc[:152].rsplit(" ", 1)[0] + "…"
    return pagina(f"/famoso/{e['slug']}/", titulo, desc, cuerpo,
                  [migas([("Inicio", "/"), ("Archivo", "/archivo/"), (nombre, f"/famoso/{e['slug']}/")]), persona, faq_ld(preguntas)])


def pagina_archivo(diarios_pasados, practica):
    filas = "".join(f'<tr><td>#{numero(dt.date.fromisoformat(e["fecha"]))}</td><td>{dt.date.fromisoformat(e["fecha"]).strftime("%d/%m/%Y")}</td>'
                    f'<td>{APARTADOS[e["apartado"]][1]}</td><td><a href="/famoso/{e["slug"]}/">{escape(e["nombre"])}</a></td></tr>'
                    for e in sorted(diarios_pasados, key=lambda x: (x["fecha"], x["apartado"]), reverse=True))
    tabla = (f'<div class="tabla-env"><table class="tabla"><thead><tr><th>Día</th><th>Fecha</th><th></th><th>Famoso</th></tr></thead><tbody>{filas}</tbody></table></div>'
             if filas else "<p>Aquí aparecerán los famosos de cada día a partir del día siguiente a que se jueguen.</p>")
    bloques = ""
    for ap, (n, ico) in APARTADOS.items():
        lista = sorted((e for e in practica if e["apartado"] == ap), key=lambda x: x["nombre"])
        bloques += f'<h3>{ico} {n}</h3><ul class="lista-famosos">' + "".join(f'<li><a href="/famoso/{e["slug"]}/">{escape(e["nombre"])}</a> <small>{escape(e.get("ambito", ""))}</small></li>' for e in lista) + "</ul>"
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › Archivo</nav>
<h1>Archivo de famosos</h1>
<p class="sub">Todos los famosos que ya han salido en el juego, con sus seis pistas, su biografía y datos curiosos. El famoso de hoy aparece aquí mañana.</p>
<section><h2>Famosos de días anteriores</h2>{tabla}</section>
<section><h2>Famosos del modo práctica</h2>{bloques}</section>"""
    return pagina("/archivo/", "Archivo de famosos: pistas y biografías | Famoso del día",
                  "Los famosos de días anteriores y del modo práctica, con sus seis pistas, una biografía breve y datos curiosos.", cuerpo,
                  [migas([("Inicio", "/"), ("Archivo", "/archivo/")])])


def pagina_como():
    preguntas = [
        ("¿A qué hora cambia el famoso?", "A las 00:00 de la hora peninsular española, para todo el mundo a la vez."),
        ("¿Cómo escribo el nombre?", "Empieza a escribir y elige el nombre en la lista. No importan las tildes ni las mayúsculas, y valen los nombres más conocidos: «Messi» o «Leo Messi» cuentan igual que «Lionel Messi»."),
        ("¿Se guardan mis partidas?", "Sí, en tu propio navegador: si recargas la página sigues donde lo dejaste. Tus estadísticas tampoco salen de tu dispositivo, así que si cambias de móvil o borras los datos del navegador empiezan de cero."),
        ("¿Puedo jugar a días anteriores?", 'Los famosos diarios se juegan solo su día, pero en el <a href="/practica/">modo práctica</a> hay muchos más famosos para jugar cuando quieras.'),
    ]
    cuerpo = f"""<nav class="migas"><a href="/">Inicio</a> › Cómo se juega</nav>
<h1>Cómo se juega a Famoso del día</h1>
<div class="texto">
<p>Cada día hay dos famosos para adivinar, los mismos para todos los jugadores: un <strong>famoso mundial</strong> (deporte, música, cine, ciencia, historia…) y un <strong>famoso español</strong>, actual o histórico.</p>
<h2>Las pistas</h2>
<p>Cada famoso tiene seis pistas, de la más difícil a la más fácil. Al empezar ves la primera, normalmente su año de nacimiento. Cada vez que fallas o pulsas «Pasar» aparece la siguiente: a qué se dedica, un logro concreto, dónde nació, un dato muy conocido y, por último, sus iniciales.</p>
<h2>La puntuación</h2>
<ul><li>Aciertas con 1 pista: <strong>6 puntos</strong>.</li><li>Con 2 pistas: 5 puntos… y así hasta 1 punto con las 6 pistas.</li><li>Si fallas las seis: 0 puntos y te mostramos la solución.</li></ul>
<h2>Comparte tu resultado</h2>
<p>Al terminar puedes compartir tu resultado sin desvelar el nombre, con un cuadrado por cada pista: 🟥 fallo y 🟩 acierto. Por ejemplo:</p>
<pre class="ejemplo">Famoso del día #12
🌍 🟥🟥🟩 3/6
🇪🇸 🟥🟩 2/6
famosodeldia.es</pre>
<h2>Estadísticas y rachas</h2>
<p>Guardamos en tu navegador cuántas partidas has jugado, tu porcentaje de aciertos, tu racha actual, tu mejor racha y con cuántas pistas sueles acertar, por separado para cada apartado.</p>
</div>
{faq_html(preguntas)}"""
    return pagina("/como-se-juega/", "Cómo se juega a Famoso del día: pistas y puntos",
                  "Las reglas del juego: seis pistas por famoso, puntos según las pistas que uses, rachas y cómo compartir tu resultado.", cuerpo,
                  [migas([("Inicio", "/"), ("Cómo se juega", "/como-se-juega/")]), faq_ld(preguntas)])


def legales():
    t = TITULAR
    paginas = {
        "/sobre-nosotros/": ("Sobre nosotros", f"""<p>{SITIO} es un juego diario gratuito hecho en España: cada día proponemos un famoso mundial y uno español para adivinar con seis pistas, igual para todos los jugadores.</p>
<p>Todas las pistas y fichas las escribimos nosotros y las comprobamos con fuentes fiables, como Wikipedia y las webs oficiales de premios, federaciones o instituciones. Cada ficha enlaza su fuente. Solo incluimos información pública sobre la trayectoria de cada persona, nunca sobre su vida privada.</p>
<p>¿Has visto un error o quieres proponer un famoso? Escríbenos a {t['email']}.</p>"""),
        "/contacto/": ("Contacto", f"""<p>Para avisar de un error en una pista, proponer famosos o cualquier otra cosa, escríbenos a <a href="mailto:{t['email']}">{t['email']}</a>.</p>
<p>Si nos avisas de un dato que crees que está mal, indica el famoso y, si puedes, una fuente: lo revisamos y lo corregimos.</p>"""),
        "/aviso-legal/": ("Aviso legal", f"""<h2>Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE): titular {t['nombre']}, NIF {t['nif']}, domicilio en {t['domicilio']}, correo {t['email']}, sitio web {DOMINIO}.</p>
<h2>Objeto</h2><p>{SITIO} ofrece gratuitamente un juego de adivinar personajes conocidos a partir de pistas de texto y fichas informativas sobre ellos. No requiere registro.</p>
<h2>Responsabilidad</h2><p>La información se ofrece con fines de entretenimiento e informativos y se revisa con cuidado, pero puede contener errores. Los nombres de personas, marcas y obras citados pertenecen a sus titulares; esta web no está vinculada a ellos.</p>
<h2>Propiedad intelectual</h2><p>Los textos, el diseño y el código de esta web pertenecen al titular.</p>
<h2>Legislación aplicable</h2><p>Estas condiciones se rigen por la legislación española.</p>"""),
        "/privacidad/": ("Política de privacidad", f"""<h2>Responsable</h2><p>{t['nombre']} ({t['email']}).</p>
<h2>Qué datos tratamos</h2><p>Esta web no tiene registro ni formularios. Tus partidas, tu progreso del día y tus estadísticas se guardan solo en tu navegador (almacenamiento local) y no se envían a ningún servidor.</p>
<p>El alojamiento (Cloudflare) puede registrar datos técnicos de la conexión, como la dirección IP, por seguridad, y ofrece estadísticas de visitas sin cookies.</p>
<h2>Publicidad</h2><p>Esta web se financia con publicidad de Google AdSense (Google Ireland Limited). Consulta la <a href="/cookies/">política de cookies</a>.</p>
<h2>Destinatarios</h2><p>No cedemos datos a terceros salvo obligación legal. Google y Cloudflare pueden tratar datos como proveedores del servicio, algunos fuera del Espacio Económico Europeo con las garantías del RGPD.</p>
<h2>Tus derechos</h2><p>Puedes ejercer tus derechos de acceso, rectificación, supresión y demás escribiendo a {t['email']}, y reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p>"""),
        "/cookies/": ("Política de cookies", f"""<p>Una cookie es un pequeño archivo que una web guarda en tu navegador.</p>
<h2>Cookies propias</h2><p>No usamos cookies propias. El juego guarda tu progreso y tus estadísticas en el almacenamiento local de tu navegador, que no se envía a ningún servidor; puedes borrarlo desde la configuración de tu navegador.</p>
<h2>Cookies de terceros: publicidad</h2><p>Google AdSense, de Google Ireland Limited, usa cookies para mostrar anuncios, medir su rendimiento y, si lo aceptas, personalizarlos según tus visitas a esta y otras webs.</p>
<p>La primera vez que entras se muestra el mensaje de consentimiento de Google, donde puedes aceptar, rechazar o elegir qué finalidades permites. Mientras no des tu consentimiento no se usan cookies de publicidad. Puedes cambiar tu elección en cualquier momento con el enlace «Configurar cookies» del pie de página.</p>
<p>Más información: <a href="https://policies.google.com/technologies/ads?hl=es" rel="noopener">cómo usa Google las cookies en la publicidad</a>.</p>"""),
    }
    for ruta, (tit, html) in paginas.items():
        guardar(ruta, pagina(ruta, f"{tit} | {SITIO}", f"{tit} de {SITIO}.", f'<h1>{tit}</h1><div class="texto">{html}</div>'))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Vuelve a la <a href="/">portada</a> y juega al famoso de hoy.</p>', indexable=False))
    return list(paginas)


# ---------------------------------------------------------------- main

def main():
    famosos, nombres = cargar()
    validar(famosos, nombres)
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    (WEB / "d").mkdir()
    for f in ("style.css", "juego.js"):
        shutil.copy(PLANTILLA / f, WEB / "assets" / f)
    for f in ("favicon.svg", "og.png"):
        if (PLANTILLA / f).exists():
            shutil.copy(PLANTILLA / f, WEB / f)

    diarios = [e for e in famosos if e.get("fecha")]
    practica = [e for e in famosos if e.get("practica")]
    # datos de cada día: pasados, hoy y mañana; nunca más allá
    por_dia = {}
    for e in diarios:
        f = dt.date.fromisoformat(e["fecha"])
        if f <= HOY + dt.timedelta(days=1):
            por_dia.setdefault(f, {})[e["apartado"]] = ficha_juego(e)
    for f, aps in por_dia.items():
        clave = SAL + f.isoformat()
        contenido = {"f": f.isoformat(), "n": numero(f), **{ap: codificar(x, clave) for ap, x in aps.items()}}
        (WEB / "d" / f"{token(f.isoformat())}.json").write_text(json.dumps(contenido, separators=(",", ":")), encoding="utf-8")
    (WEB / "d" / "practica.json").write_text(json.dumps({"x": codificar([dict(ficha_juego(e), ap=e["apartado"]) for e in practica], SAL + "practica")},
                                                        separators=(",", ":")), encoding="utf-8")
    (WEB / "assets" / "nombres.json").write_text(json.dumps(sorted(set(nombres), key=str.lower), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    rutas = []
    for ruta, ap in (("/", "mundial"), ("/mundial/", "mundial"), ("/espana/", "espana")):
        guardar(ruta, pagina_juego(ruta, ap))
        rutas.append(ruta)
    guardar("/practica/", pagina_practica(practica))
    rutas.append("/practica/")
    # fichas: práctica siempre; diarios solo cuando su día ya ha pasado (nunca hoy ni futuros)
    pasados = [e for e in diarios if dt.date.fromisoformat(e["fecha"]) < HOY]
    publicables = {e["slug"]: e for e in sorted(pasados, key=lambda x: x["fecha"], reverse=True) + practica}
    for e in publicables.values():
        guardar(f"/famoso/{e['slug']}/", pagina_ficha(e, publicables))
        rutas.append(f"/famoso/{e['slug']}/")
    guardar("/archivo/", pagina_archivo(pasados, practica))
    rutas.append("/archivo/")
    guardar("/como-se-juega/", pagina_como())
    rutas.append("/como-se-juega/")
    rutas += legales()

    modificado = {f"/famoso/{e['slug']}/": e["fecha"] for e in pasados}
    hoy = HOY.isoformat()
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{modificado.get(r, hoy)}</lastmod></url>\n" for r in rutas)
                                     + "</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /d/\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (WEB / "ads.txt").write_text(f"google.com, {ADSENSE.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (WEB / "_headers").write_text("/d/*\n  Cache-Control: no-cache\n  X-Robots-Tag: noindex\n/assets/*\n  Cache-Control: public, max-age=86400\n", encoding="utf-8")

    # aviso si quedan pocos días con famoso asignado
    for ap in APARTADOS:
        futuros = sorted(dt.date.fromisoformat(e["fecha"]) for e in diarios if e["apartado"] == ap and dt.date.fromisoformat(e["fecha"]) >= HOY)
        ultimo = futuros[-1] if futuros else None
        if not ultimo or (ultimo - HOY).days < 7:
            print(f"AVISO: quedan pocos famosos {ap}: el último día asignado es {ultimo or 'ninguno'}. Añade más en data/{ap}.json.")
        if HOY >= LANZAMIENTO and not any(dt.date.fromisoformat(e["fecha"]) == HOY for e in diarios if e["apartado"] == ap):
            print(f"AVISO: hoy no hay famoso {ap}.")
    print(f"Web generada: {len(rutas)} páginas en el sitemap, {len(publicables)} fichas, {len(por_dia)} días publicados, {len(practica)} famosos de práctica.")


if __name__ == "__main__":
    main()
