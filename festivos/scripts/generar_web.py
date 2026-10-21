"""Genera la web estática de festivosde.es a partir de festivos/data/ (lo crea procesar.py).

Páginas:
  /                              portada: buscador, próximos festivos nacionales y comunidades
  /<municipio>/                  festivos de cada municipio (nacionales, autonómicos y locales) de cada año
  /comunidad/<slug>/             calendario laboral de la comunidad y sus provincias
  /provincia/<slug>/             festivos locales de todos sus municipios
  /calendario-laboral-<año>/     calendario de toda España: qué fiesta tiene cada comunidad
  /es-festivo/<día>-de-<mes>/    dónde es festivo cada día del año (y /es-festivo/: ¿es festivo hoy?)
  /planificador-vacaciones/      qué días pedir de vacaciones para encadenar más días libres en tu municipio
  /sobre-los-datos/, /aviso-legal/, /privacidad/

Todo sale del BOE y de los boletines oficiales de cada comunidad. Si un municipio todavía no tiene
sus fiestas locales publicadas, se dice así: nunca se inventa ni se supone una fecha.

Uso: python festivos/scripts/generar_web.py
"""
import datetime as dt
import json
import os
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
VERSION = "9"
HOY = dt.date.fromisoformat(os.environ["FESTIVOS_HOY"]) if os.environ.get("FESTIVOS_HOY") else dt.date.today()  # FESTIVOS_HOY: para probar
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
RESERVADOS = {"comunidad", "provincia", "assets", "sobre-los-datos", "aviso-legal", "privacidad", "indice", "datos",
              "calculadora-dias-laborables", "planificador-vacaciones", "calendario-escolar", "es-festivo"}
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


def de(nombre):
    """«de la Comunidad de Madrid», «de las Illes Balears», «de Andalucía»."""
    if nombre.startswith(("Comunidad", "Región", "Comunitat")):
        return f"de la {nombre}"
    if nombre.startswith("Illes"):
        return f"de las {nombre}"
    return f"de {nombre}"


def en(nombre):
    """«en la Comunidad de Madrid», «en las Illes Balears», «en Andalucía»."""
    return "en " + de(nombre)[3:]


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


def calcular_puentes(lista):
    """Para cada festivo entre semana: el bloque de días libres seguidos (fines de semana y festivos)
    y la mejor forma de alargarlo cogiendo 1 o 2 días de vacaciones."""
    libres = {dt.date.fromisoformat(x["f"]) for x in lista}
    nombres = {}
    for x in lista:
        nombres.setdefault(dt.date.fromisoformat(x["f"]), []).append(x["n"])
    un_dia = dt.timedelta(days=1)

    def libre(d):
        return d.weekday() >= 5 or d in libres

    def bloque(d):
        ini, fin = d, d
        while libre(ini - un_dia):
            ini -= un_dia
        while libre(fin + un_dia):
            fin += un_dia
        return ini, fin

    vistos, res = set(), []
    for d in sorted(libres):
        if d.weekday() >= 5:
            continue
        ini, fin = bloque(d)
        if (ini, fin) in vistos:
            continue
        vistos.add((ini, fin))
        opciones = []
        for lado in (-1, 1):  # alargar hacia atrás o hacia delante
            vac, x = [], (ini - un_dia if lado < 0 else fin + un_dia)
            while not libre(x) and len(vac) < 2:
                vac.append(x)
                x += un_dia * lado
            if vac and libre(x):
                i2, f2 = bloque(x)
                nuevo_ini, nuevo_fin = (i2, fin) if lado < 0 else (ini, f2)
                opciones.append(((nuevo_fin - nuevo_ini).days + 1, sorted(vac), nuevo_ini, nuevo_fin))
        opciones.sort(key=lambda o: (len(o[1]), -o[0]))
        mejor = next((o for o in opciones if o[0] - ((fin - ini).days + 1) >= 2), None)
        fiestas = [n for f in sorted(libres) if ini <= f <= fin for n in nombres[f]]
        res.append({"ini": ini, "fin": fin, "dias": (fin - ini).days + 1, "fiestas": fiestas, "mejor": mejor})
    return res


def rango(ini, fin):
    if ini.month == fin.month:
        return f"del {DIAS[ini.weekday()]} {ini.day} al {DIAS[fin.weekday()]} {fin.day} de {MESES[fin.month - 1]}"
    return f"del {DIAS[ini.weekday()]} {ini.day} de {MESES[ini.month - 1]} al {DIAS[fin.weekday()]} {fin.day} de {MESES[fin.month - 1]}"


def texto_puente(p):
    """Frase de un puente: sin coger vacaciones o cogiendo 1-2 días."""
    fiesta = escape(" y ".join(dict.fromkeys(p["fiestas"])))
    partes = []
    if p["dias"] >= 3:
        partes.append(f'<span class="largo">{p["dias"]} días libres sin coger vacaciones</span>, {rango(p["ini"], p["fin"])}')
    if p["mejor"]:
        total, vac, i2, f2 = p["mejor"]
        dias_vac = " y ".join(f"{DIAS[v.weekday()]} {v.day}" for v in vac)
        partes.append(f'<span class="puente">coge el {dias_vac} y tendrás {total} días libres</span>, {rango(i2, f2)}')
    if not partes:
        return ""
    return f"<li><b>{fiesta}</b>: " + "; o ".join(partes) + ".</li>"


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
    <a href="/" class="logo"><span class="logo-hoja"><b id="logo-dia"></b><i id="logo-mes"></i></span><script>(function(){{var d=new Date();document.getElementById("logo-dia").textContent=d.getDate();document.getElementById("logo-mes").textContent={json.dumps([m[:3] for m in MESES])}[d.getMonth()]}})()</script><span>festivos<span class="de">de</span>.es</span></a>
    <nav class="menu">
      <a href="/calendario-laboral-{max(ANIOS)}/">Calendario {max(ANIOS)}</a>
      <a href="/puentes-{max(ANIOS)}/">Puentes {max(ANIOS)}</a>
      <a href="/calendario-escolar/">Calendario escolar</a>
      <a href="/planificador-vacaciones/">Vacaciones</a>
      <a href="/calendario-laboral-para-imprimir/">Para imprimir</a>
      <a href="/calculadora-dias-laborables/">Días laborables</a>
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
    <div class="enlaces"><a href="/">Buscar un municipio</a>{''.join(f'<a href="/calendario-laboral-{a}/">Calendario laboral {a}</a><a href="/puentes-{a}/">Puentes {a}</a>' for a in ANIOS)}<a href="/es-festivo/">¿Es festivo hoy?</a><a href="/calculadora-dias-laborables/">Calculadora de días laborables</a><a href="/planificador-vacaciones/">Planificador de vacaciones</a><a href="/calendario-escolar/">Calendario escolar</a><a href="/calendario-laboral-para-imprimir/">Calendario para imprimir</a><a href="/#comunidades">Comunidades autónomas</a><a href="/sobre-los-datos/">De dónde salen los datos</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad y cookies</a>{CONFIGURAR_COOKIES}</div>
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
        f'<tr class="t-{x["t"]}"><td><a href="{ruta_dia(dt.date.fromisoformat(x["f"]))}"><time datetime="{x["f"]}">{fecha_larga(x["f"], False)}</time></a></td>'
        f'<td>{DIAS[dt.date.fromisoformat(x["f"]).weekday()]}</td><td>{escape(x["n"])}</td>'
        f'<td><span class="marca {x["t"]}">{TIPOS[x["t"]]}</span></td></tr>' for x in lista)
    return ('<div class="tabla-envoltorio"><table class="festivos"><thead><tr><th>Fecha</th><th>Día</th><th>Fiesta</th>'
            f'<th>Ámbito</th></tr></thead><tbody>{filas}</tbody></table></div>')


def hojas_html(lista, clase="hojas"):
    """Fechas como hojas de calendario: [{f, n}]."""
    return f'<ul class="{clase}">' + "".join(
        f'<li class="hoja"><span class="hoja-mes">{MESES[int(x["f"][5:7]) - 1][:3]}</span><b>{int(x["f"][8:])}</b>'
        f'<span class="hoja-dia">{DIAS[dt.date.fromisoformat(x["f"]).weekday()]}</span><small>{escape(x["n"])}</small></li>' for x in lista) + "</ul>"


def bloque_puentes(lista, anio, titulo=None):
    items = "".join(texto_puente(p) for p in calcular_puentes(lista))
    if not items:
        return ""
    return f'<h3>{titulo or f"Puentes de {anio}"}</h3><ul class="puentes">{items}</ul>'


def fuentes_html(datos, anio, ccaa, con_locales):
    d = datos[anio]
    partes = [f'<a href="{d["boe"]["url"]}" rel="nofollow noopener">{escape(d["boe"]["titulo"])}</a> (BOE de {fecha_larga(d["boe"]["publicado"], False)} de {d["boe"]["publicado"][:4]})']
    f = d["fuentes"].get(ccaa)
    if con_locales and f:
        partes.append(f'<a href="{escape(f["url"])}" rel="nofollow noopener">fiestas locales {escape(de(COMUNIDADES[ccaa][0]))} para {anio}</a>'
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
                              + f". Además, hay {len(lista) - len(locales)} festivos nacionales y {escape(de(ccaa_nombre))}."))
        else:
            resto = datos[anio]["fuentes"].get(ccaa, {}).get("resto")
            if resto:
                pendiente = (f"El boletín oficial {escape(de(ccaa_nombre))} no indica fechas concretas para {escape(N)}: dice «{escape(resto)}». "
                             "Consulta las fechas exactas en tu ayuntamiento.")
            else:
                pendiente = (f"Las dos fiestas locales de {escape(N)} para {anio} todavía no están publicadas en nuestros datos. "
                             f"Las aprueba cada año el boletín oficial {escape(de(ccaa_nombre))} y las añadiremos en cuanto salgan.")
            resumen = f'<p class="pendiente">{pendiente}</p><p>De momento, estos son los {len(lista)} festivos nacionales y {escape(de(ccaa_nombre))} que también se celebran en {escape(N)}:</p>'
        n_puentes = sum(1 for p in calcular_puentes(lista) if p["dias"] >= 3 or p["mejor"])
        cifras = (f'<ul class="cifras"><li><b>{len(lista)}</b><span>festivos en {anio}</span></li>'
                  f'<li><b>{len(locales) if tiene_locales(datos, anio, cod) else "–"}</b><span>fiestas locales</span></li>'
                  f'<li><b>{n_puentes}</b><span>puentes y fines de semana largos</span></li></ul>')
        destacadas = (f'<h3>Fiestas locales de {escape(N)} en {anio}</h3>' + hojas_html(locales, "hojas locales")) if tiene_locales(datos, anio, cod) else ""
        secciones.append(f"""<section class="anio" id="festivos-{anio}" data-anio="{anio}">
<h2>Festivos de {escape(N)} en {anio}</h2>
{cifras}
{destacadas}
{resumen}
{aviso_varias}
{tabla_festivos(lista)}
<div class="calendario" data-anio="{anio}"></div>
<p class="acciones"><button class="boton-imprimir" type="button" data-anio="{anio}">🖨️ Imprimir calendario {anio}</button>
<a class="boton-sec" href="/calendario-laboral-para-imprimir/?m={cod}&amp;a={anio}">📄 Calendario {anio} en PDF</a>
<a class="boton-sec" href="/planificador-vacaciones/?m={cod}&amp;a={anio}">🏖️ Planificar mis vacaciones {anio}</a>
<a class="boton-sec" href="/calculadora-dias-laborables/?m={cod}">🧮 Calcular días laborables en {escape(N)}</a></p>
{bloque_puentes(lista, anio)}
{notas_html(datos, anio, cod)}
{fuentes_html(datos, anio, ccaa, tiene_locales(datos, anio, cod))}
</section>""")
        preguntas.append((f"¿Cuántos festivos hay en {N} en {anio}?",
                          f"En {escape(N)} hay {len(lista)} días festivos en {anio}: "
                          f"{sum(1 for x in lista if x['t'] == 'nacional')} nacionales, {sum(1 for x in lista if x['t'] == 'autonomico')} {escape(de(ccaa_nombre))}"
                          + (f" y {len(locales)} locales." if locales else ". Las fiestas locales aún no están publicadas.")))
    lista_vecinos = "".join(f'<li><a href="{v["url"]}">{escape(v["nombre"])}</a></li>' for v in vecinos)
    proximos = [x for a in ANIOS for x in festivos_de(datos, a, cod) if x["f"] >= HOY.isoformat()][:4]
    cuerpo = f"""<section class="cabecera-muni">
<div><h1>Festivos en {escape(N)}</h1>
<p class="lead">Calendario laboral de {escape(N)} ({escape(prov_nombre)}): fiestas locales, {escape(de(ccaa_nombre))} y nacionales de {' y '.join(map(str, ANIOS))}.</p>
<ul class="chips"><li><a href="/planificador-vacaciones/?m={cod}&amp;a={max(ANIOS)}">🏖️ Planificar vacaciones</a></li><li><a href="/calculadora-dias-laborables/?m={cod}">🧮 Días laborables</a></li><li><a href="/puentes-{max(ANIOS)}/">🌉 Puentes {max(ANIOS)}</a></li><li><a href="{RUTAS_PROV[cod[:2]]}">Provincia de {escape(prov_nombre)}</a></li><li><a href="/comunidad/{ccaa}/">{escape(ccaa_nombre)}</a></li></ul></div>
<div class="hoy" id="hoy" data-municipio="{escape(N)}"></div>
</section>
<section><h2>Próximos festivos en {escape(N)}</h2><div id="proximos">{hojas_html(proximos)}</div></section>
<nav class="pestanas" aria-label="Año">{''.join(f'<a href="#festivos-{a}" data-anio="{a}">{a}</a>' for a in ANIOS)}<button class="boton-ics" type="button">📅 Añadir a mi calendario</button></nav>
{''.join(secciones)}
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>
<section><h2>Otros municipios de {escape(prov_nombre)}</h2><ul class="lista-municipios">{lista_vecinos}</ul>
<p><a href="{RUTAS_PROV[cod[:2]]}">Todos los festivos locales de la provincia de {escape(prov_nombre)} →</a> · <a href="/comunidad/{ccaa}/">Calendario laboral {escape(de(ccaa_nombre))} →</a></p></section>
<script type="application/json" id="datos-festivos">{json.dumps({"municipio": N, "festivos": embebido, "locales": [a for a in ANIOS if tiene_locales(datos, a, cod)]}, ensure_ascii=False, separators=(",", ":"))}</script>"""
    anio_tit = max(a for a in ANIOS)
    titulo = f"Festivos en {corto(m['nombre_ine'])} {min(ANIOS)} y {anio_tit}: calendario laboral"
    if len(titulo) > 65:
        titulo = f"Festivos en {corto(m['nombre_ine'])} {min(ANIOS)} y {anio_tit}"
    con_locales = [a for a in ANIOS if tiene_locales(datos, a, cod)]
    # Descripción para Google: qué hay en la página, sin dar las fechas (si las da, nadie entra)
    desc = (f"Cuáles son las fiestas locales de {N} en {' y '.join(map(str, ANIOS))}, el próximo festivo, "
            f"los puentes y todos los festivos {de(ccaa_nombre)}, con el boletín oficial. Añádelos a tu calendario.")
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
<p class="lead">Las dos fiestas locales de cada municipio de {escape(nombre)} y el <a href="/comunidad/{ccaa}/">calendario laboral {escape(de(COMUNIDADES[ccaa][0]))}</a>.</p>
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
        secciones.append(f"""<section id="festivos-{anio}"><h2>Calendario laboral {escape(de(nombre))} {anio}</h2>
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
        filas.append(f'<tr class="t-{tipo}"><td><a href="{ruta_dia(dt.date.fromisoformat(f))}"><time datetime="{f}">{fecha_larga(f, False)}</time></a></td><td>{DIAS[dt.date.fromisoformat(f).weekday()]}</td>'
                     f'<td>{escape(n)}</td><td>{donde}</td></tr>')
    comunes = [f for (f, n), cc in fechas.items() if len(cc) == todas]
    cuerpo = f"""<h1>Calendario laboral {anio}</h1>
<p class="lead">Todos los festivos de {anio} en España según el BOE: {len(comunes)} fiestas comunes a todo el país y las de cada comunidad autónoma. Busca tu municipio para ver también sus dos fiestas locales.</p>
<div class="tabla-envoltorio"><table class="festivos"><thead><tr><th>Fecha</th><th>Día</th><th>Fiesta</th><th>Dónde es festivo</th></tr></thead><tbody>{''.join(filas)}</tbody></table></div>
<p class="fuente">Fuente: <a href="{datos[anio]['boe']['url']}" rel="nofollow noopener">{escape(datos[anio]['boe']['titulo'])}</a>, publicada en el BOE el {fecha_larga(datos[anio]['boe']['publicado'], False)} de {datos[anio]['boe']['publicado'][:4]}.</p>
<p class="acciones"><a class="boton-sec" href="/calendario-laboral-para-imprimir/?a={anio}">🖨️ Calendario laboral {anio} para imprimir con tus fiestas locales</a></p>
<section id="comunidades"><h2>Calendario laboral {anio} por comunidad</h2>{lista_comunidades()}</section>"""
    return pagina(f"/calendario-laboral-{anio}/", f"Calendario laboral {anio}: todos los festivos de España",
                  f"Festivos de {anio} en España según el BOE: fiestas nacionales, de cada comunidad autónoma y locales de cada municipio.",
                  cuerpo, [(f"Calendario laboral {anio}", None)])


def pagina_puentes(datos, anio):
    d = datos[anio]["nacionales_autonomicos"]
    fechas_comunes = set.intersection(*[{x["f"] for x in lista} for lista in d.values()])
    comunes = [x for x in d["madrid"] if x["f"] in fechas_comunes]
    secciones = []
    for ccaa, (nombre, _) in sorted(COMUNIDADES.items(), key=lambda x: x[1][0]):
        items = "".join(texto_puente(p) for p in calcular_puentes(d[ccaa]))
        if items:
            secciones.append(f'<h3 id="{ccaa}"><a href="/comunidad/{ccaa}/">{escape(nombre)}</a></h3><ul class="puentes">{items}</ul>')
    resumen = calcular_puentes(comunes)
    largos = sum(1 for p in resumen if p["dias"] >= 3)
    cuerpo = f"""<h1>Puentes {anio}</h1>
<p class="lead">Todos los puentes de {anio} en España y en cada comunidad autónoma, según el calendario laboral publicado en el BOE: cuándo tienes fines de semana largos y qué días te conviene pedir de vacaciones para encadenar más días libres.</p>
<p>Las fiestas locales de cada municipio pueden añadir más puentes: <a href="/">busca tu municipio</a> para verlos todos, o usa el <a href="/planificador-vacaciones/?a={anio}">planificador de vacaciones</a> para que te diga qué días pedir con tus días de vacaciones.</p>
<h2>Puentes en toda España</h2>
<p>Con las fiestas que se celebran en todas las comunidades hay {largos} fines de semana largos sin coger vacaciones.</p>
<ul class="puentes">{''.join(texto_puente(p) for p in resumen)}</ul>
<h2>Puentes de {anio} por comunidad autónoma</h2>
{''.join(secciones)}
<p class="fuente">Fuente: <a href="{datos[anio]['boe']['url']}" rel="nofollow noopener">{escape(datos[anio]['boe']['titulo'])}</a>.</p>"""
    return pagina(f"/puentes-{anio}/", f"Puentes {anio}: todos los puentes y festivos de España",
                  f"Cuándo hay puente en {anio} en España y en cada comunidad, qué días pedir de vacaciones para tener más días libres y los fines de semana largos.",
                  cuerpo, [(f"Puentes {anio}", None)])


def pagina_calculadora(datos):
    anios = " y ".join(map(str, ANIOS))
    preguntas = [
        ("¿Qué son los días laborables?", "Los días en los que se trabaja: de lunes a viernes, sin contar los festivos nacionales, autonómicos y locales. Si trabajas los sábados, marca la casilla para contarlos."),
        ("¿Qué son los días hábiles?", "En los plazos administrativos (Ley 39/2015) son hábiles todos los días menos los sábados, los domingos y los festivos. Para un plazo de un trámite, cuenta de lunes a viernes y elige el municipio de la administración donde lo presentas."),
        ("¿Cuántos días laborables tiene un año?", "Depende del municipio, porque las fiestas locales cambian. Con 52 o 53 fines de semana y 14 festivos, suelen salir entre 248 y 252 días laborables de lunes a viernes."),
    ]
    cuerpo = f"""<h1>Calculadora de días laborables y días hábiles</h1>
<p class="lead">Cuenta los días laborables entre dos fechas, o suma días hábiles a una fecha, descontando los fines de semana y los festivos nacionales, autonómicos y locales de tu municipio ({anios}).</p>
<form class="calc" id="calc" onsubmit="return false">
  <div class="campo"><label for="municipio">Municipio</label>
    <input id="municipio" type="search" autocomplete="off" placeholder="Escribe tu municipio"><ul id="sug-municipio" class="sugerencias"></ul></div>
  <div class="campo"><label for="modo">¿Qué quieres calcular?</label>
    <select id="modo"><option value="entre">Días laborables entre dos fechas</option><option value="sumar">Sumar días hábiles a una fecha</option></select></div>
  <div class="fila">
    <div class="campo"><label for="desde">Desde</label><input id="desde" type="date"></div>
    <div class="campo" id="campo-hasta"><label for="hasta">Hasta (incluido)</label><input id="hasta" type="date"></div>
    <div class="campo" id="campo-n" hidden><label for="n">Días hábiles a sumar</label><input id="n" type="number" min="1" max="400" value="10"></div>
  </div>
  <label class="check"><input id="sabados" type="checkbox"> Contar los sábados como laborables</label>
  <div class="resultado" id="resultado" aria-live="polite"></div>
</form>
<section class="contenido"><h2>Cómo se calcula</h2>
<p>Se recorren todos los días del periodo y se descuentan los domingos (y los sábados, salvo que marques la casilla) y los festivos de tu municipio: los nacionales y autonómicos del BOE y las dos fiestas locales del boletín oficial de tu comunidad. Si las fiestas locales de un año aún no están publicadas, te lo avisamos.</p>
<p>Al sumar días hábiles a una fecha, el primer día que cuenta es el siguiente a la fecha de inicio, como en los plazos administrativos.</p></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    return pagina("/calculadora-dias-laborables/", f"Calculadora de días laborables y hábiles {anios} por municipio",
                  "Calcula cuántos días laborables o hábiles hay entre dos fechas, o suma días hábiles a una fecha, con los festivos de tu municipio.",
                  cuerpo, [("Calculadora de días laborables", None)], [faq_ld(preguntas)],
                  scripts=f'<script src="/assets/calculadora.js?v={VERSION}" defer></script>')


def pagina_imprimible(datos):
    ult = max(ANIOS)
    opciones = "".join(f'<option value="{a}"{" selected" if a == ult else ""}>{a}</option>' for a in sorted(ANIOS, reverse=True))
    preguntas = [
        ("¿Cómo guardo el calendario en PDF?", "Pulsa «Imprimir o guardar en PDF» y, en la ventana de impresión, elige «Guardar como PDF» en lugar de tu impresora. En el móvil, la opción aparece al compartir o imprimir la página."),
        ("¿Qué festivos incluye?", "Los festivos nacionales y los de tu comunidad autónoma que publica el BOE, y las dos fiestas locales de tu municipio que publica el boletín oficial de tu comunidad o provincia."),
        (f"¿Cuándo se publican las fiestas locales de {ult}?", "Cada comunidad las publica en su boletín oficial, normalmente entre octubre y enero. Si las de tu municipio aún no están, el calendario te lo avisa y solo incluye los festivos nacionales y autonómicos."),
        ("¿Se puede imprimir en blanco y negro?", "Sí. Marca «Blanco y negro» y los festivos se distinguen por el relleno (locales en negro, autonómicos en gris y nacionales con un recuadro), sin gastar tinta de color."),
    ]
    cuerpo = f"""<style>@page {{ size: A4 landscape; margin: 8mm; }}</style>
<h1>Calendario laboral {ult} para imprimir</h1>
<p class="lead">Elige tu municipio y descarga en PDF o imprime el calendario de todo el año en una sola hoja, con los festivos nacionales, autonómicos y las fiestas locales de tu pueblo o ciudad. Gratis y sin registrarte.</p>
<form class="calc" onsubmit="return false">
  <div class="campo"><label for="municipio">Municipio</label>
    <input id="municipio" type="search" autocomplete="off" placeholder="Escribe tu municipio"><ul id="sug-municipio" class="sugerencias"></ul></div>
  <div class="opciones-hoja">
    <label>Año <select id="anio">{opciones}</select></label>
    <label class="check"><input id="bn" type="checkbox"> Blanco y negro (ahorra tinta)</label>
    <label class="check"><input id="lista" type="checkbox" checked> Con la lista de festivos</label>
  </div>
  <p><button class="boton-imprimir" id="imprimir" type="button" disabled>🖨️ Imprimir o guardar en PDF</button> <span id="resumen" class="fuente"></span></p>
</form>
<div id="hoja" class="hoja-a4" hidden></div>
<section class="contenido"><h2>Un calendario para la nevera, la oficina o la agenda</h2>
<p>El calendario ocupa una hoja A4 apaisada: los doce meses con los festivos marcados por colores y, debajo, la lista de todos los festivos con su día de la semana. Los datos son los mismos que en la página de cada municipio: el BOE para los festivos nacionales y autonómicos y el boletín oficial de cada comunidad para las fiestas locales.</p>
<p>Si quieres organizar las vacaciones, usa el <a href="/planificador-vacaciones/">planificador de vacaciones</a>, mira los <a href="/puentes-{ult}/">puentes de {ult}</a> o cuenta los <a href="/calculadora-dias-laborables/">días laborables</a> entre dos fechas.</p></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    return pagina("/calendario-laboral-para-imprimir/", f"Calendario laboral {ult} para imprimir (PDF) con tus festivos locales",
                  f"Descarga en PDF o imprime el calendario laboral de {ult} de tu municipio en una hoja: festivos nacionales, autonómicos y fiestas locales.",
                  cuerpo, [("Calendario para imprimir", None)], [faq_ld(preguntas)],
                  scripts=f'<script src="/assets/imprimible.js?v={VERSION}" defer></script>')


def pagina_planificador(datos):
    ult = max(ANIOS)
    opciones = "".join(f'<option value="{a}"{" selected" if a == ult else ""}>{a}</option>' for a in sorted(ANIOS, reverse=True))
    meses = "".join(f'<option value="{i}"{" selected" if i == 7 else ""}>En {m}</option>' for i, m in enumerate(MESES))
    preguntas = [
        ("¿Cómo elige el planificador los días de vacaciones?", "Primero busca los puentes: los días laborables entre un festivo y un fin de semana, que con uno o dos días de vacaciones te dan cuatro o cinco días libres seguidos. Elige los que más días libres dan por cada día de vacaciones. Con el resto de días arma unas vacaciones largas en el mes que elijas, juntándolas con los fines de semana y los festivos de ese mes."),
        ("¿Cuántos días de vacaciones tengo al año?", "El Estatuto de los Trabajadores fija un mínimo de 30 días naturales al año, que en la práctica suelen ser 22 días laborables (de lunes a viernes). Tu convenio colectivo o tu contrato pueden darte más."),
        ("¿Tiene en cuenta las fiestas locales de mi municipio?", "Sí: usa los festivos nacionales y autonómicos del BOE y las dos fiestas locales que publica el boletín oficial de tu comunidad o provincia. Si las fiestas locales del año aún no están publicadas, te avisa y planifica solo con las nacionales y autonómicas."),
        ("¿Puedo guardar o imprimir mi plan?", "Sí. Pulsa «Imprimir o guardar en PDF» para tener el calendario con los días marcados en una hoja, o «Copiar enlace a mi plan» para guardarlo o enviárselo a quien quieras."),
    ]
    cuerpo = f"""<style>@page {{ size: A4 landscape; margin: 8mm; }}</style>
<h1>Planificador de vacaciones {ult}</h1>
<p class="lead">Dinos tu municipio y cuántos días de vacaciones tienes, y te decimos qué días pedir para encadenar el máximo de días libres con los puentes, los fines de semana y los festivos de tu pueblo o ciudad.</p>
<form class="calc" onsubmit="return false">
  <div class="campo"><label for="municipio">Municipio</label>
    <input id="municipio" type="search" autocomplete="off" placeholder="Escribe tu municipio"><ul id="sug-municipio" class="sugerencias"></ul></div>
  <div class="fila">
    <div class="campo"><label for="anio">Año</label><select id="anio">{opciones}</select></div>
    <div class="campo"><label for="dias">Días de vacaciones (laborables)</label><input id="dias" type="number" min="1" max="40" value="22"></div>
    <div class="campo"><label for="mes">Vacaciones largas</label><select id="mes">{meses}<option value="-1">Sin vacaciones largas: todo en puentes y escapadas</option></select></div>
  </div>
</form>
<div id="plan" hidden aria-live="polite"></div>
<section class="contenido"><h2>Cómo sacar más días libres de tus vacaciones</h2>
<p>El truco está en los puentes: cuando un festivo cae en martes o jueves, pedir el lunes o el viernes te da cuatro días libres seguidos por un solo día de vacaciones. Si cae en miércoles, con dos días tienes cinco. El planificador busca todos esos huecos con los festivos de tu municipio, elige los que más rinden y deja el resto de días para unas vacaciones largas en el mes que prefieras.</p>
<p>Los festivos son los mismos que en la página de cada municipio: el BOE para los nacionales y autonómicos y el boletín oficial de cada comunidad para las fiestas locales. Antes de pedir los días, confirma con tu empresa el calendario laboral y si tu convenio tiene días de libre disposición o fiestas propias.</p>
<p>Mira también los <a href="/puentes-{ult}/">puentes de {ult}</a> en cada comunidad, el <a href="/calendario-laboral-para-imprimir/">calendario laboral para imprimir</a> o cuenta los <a href="/calculadora-dias-laborables/">días laborables</a> entre dos fechas.</p></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    return pagina("/planificador-vacaciones/", f"Planificador de vacaciones {ult}: qué días pedir para tener más días libres",
                  f"Elige tu municipio y tus días de vacaciones y te decimos qué días pedir en {ult} para aprovechar los puentes y los festivos locales. Gratis.",
                  cuerpo, [("Planificador de vacaciones", None)], [faq_ld(preguntas)],
                  scripts=f'<script src="/assets/planificador.js?v={VERSION}" defer></script>')


# ---------------------------------------------------------------- ¿es festivo el...?

def ruta_dia(d):
    return f"/es-festivo/{d.day}-de-{MESES[d.month - 1]}/"


def indice_fechas(datos, anio):
    """Para cada fecha de un año: dónde es festivo.
    {f: {"ccaa": {fiesta: [ccaa]}, "prov": [(codp, fiesta)], "mun": {codp: [(cod, fiesta)]}}}"""
    d, idx = datos[anio], {}

    def de_fecha(f):
        return idx.setdefault(f, {"ccaa": {}, "prov": [], "mun": {}})
    for c, lista in d["nacionales_autonomicos"].items():
        for x in lista:
            de_fecha(x["f"])["ccaa"].setdefault(x["n"], []).append(c)
    for p, lista in d.get("comunes", {}).items():
        for x in lista:
            de_fecha(x["f"])["prov"].append((p, x["n"] or "Fiesta local"))
    for cod, lista in d["locales"].items():
        if cod not in INFO:
            continue
        for f in sorted({x["f"] for x in lista}):
            nombres = [x["n"] for x in lista if x["f"] == f and x["n"]]
            de_fecha(f)["mun"].setdefault(cod[:2], []).append((cod, nombres[0] if nombres else ""))
    return idx


def regiones(donde):
    return {c for cc in donde["ccaa"].values() for c in cc}


def lista_y(partes):
    return ", ".join(partes[:-1]) + " y " + partes[-1] if len(partes) > 1 else "".join(partes)


def resumen_dia(donde, con_enlaces=False):
    """«en toda España (Todos los Santos)», «en Andalucía y Madrid (…)», «fiesta local en 12 municipios»."""
    partes = []
    for fiesta, cc in sorted(donde["ccaa"].items(), key=lambda x: -len(x[1])):
        if len(cc) == len(COMUNIDADES):
            partes.append(f"en toda España ({escape(fiesta)})")
        else:
            nombres = [f'<a href="/comunidad/{c}/">{escape(COMUNIDADES[c][0])}</a>' if con_enlaces else escape(COMUNIDADES[c][0])
                       for c in sorted(cc, key=lambda c: COMUNIDADES[c][0])]
            partes.append(f"en {lista_y(nombres)} ({escape(fiesta)})")
    for p, fiesta in donde["prov"]:
        partes.append(f"en toda la provincia de {escape(PROVINCIAS[p][0])} ({escape(fiesta)})")
    n_mun = sum(len(v) for v in donde["mun"].values())
    if n_mun:
        partes.append(f"fiesta local en {n_mun} {'municipio' if n_mun == 1 else 'municipios'}")
    return lista_y(partes)


def miles(n):
    return f"{n:,}".replace(",", ".")


def respuesta_dia(datos, anio, d, donde):
    """Respuesta a «¿es festivo el …?»: (sí/no, html)."""
    publicados = len(datos[anio]["locales"])
    fecha = f"{fecha_larga(d)} de {anio}"
    if donde and (donde["ccaa"] or donde["prov"] or donde["mun"]):
        todas = len(regiones(donde)) == len(COMUNIDADES)
        if donde["ccaa"] or donde["prov"]:
            texto = f"{'Sí' if todas else 'Sí, pero no en toda España'}: el {fecha} es festivo {resumen_dia(donde, True)}."
        else:
            texto = f"Solo en algunos municipios: el {fecha} es {resumen_dia(donde)}."
        si = True
    else:
        texto = (f"No: el {fecha} no es fiesta nacional ni autonómica en ninguna comunidad, ni fiesta local en ninguno de los "
                 f"{miles(publicados)} municipios de los que tenemos las fiestas locales de {anio}.")
        si = False
    pendientes = len(INFO) - publicados
    if pendientes > 0:
        texto += (f" Faltan en nuestros datos las fiestas locales de {anio} de {miles(pendientes)} municipios"
                  + (": la mayoría de comunidades aún no las han publicado." if pendientes > len(INFO) / 2 else "."))
    if d.weekday() >= 5:
        texto += f" Además, cae en {DIAS[d.weekday()]}."
    return si, texto


def municipios_dia(donde):
    bloques = []
    for p in sorted(donde["mun"], key=lambda p: slug(PROVINCIAS[p][0])):
        cods = sorted(donde["mun"][p], key=lambda x: slug(INFO[x[0]]["nombre"]))
        enlaces = "".join(f'<li><a href="{INFO[c]["url"]}">{escape(INFO[c]["nombre"])}</a>{f" <small>({escape(n)})</small>" if n else ""}</li>'
                          for c, n in cods)
        bloques.append(f'<details><summary>Provincia de {escape(PROVINCIAS[p][0])}: {len(cods)} '
                       f'{"municipio" if len(cods) == 1 else "municipios"}</summary><ul class="lista-municipios">{enlaces}</ul></details>')
    return f'<div class="faq">{"".join(bloques)}</div>'


def mes_enlazado(anio, mes, idx, marcado=None):
    """Hoja de un mes con cada día enlazado a su página: azul si es festivo en toda España, verde si en alguna comunidad."""
    d = dt.date(anio, mes, 1)
    celdas = [f'<span class="cab">{x[:2]}</span>' for x in DIAS] + ["<span></span>"] * d.weekday()
    while d.month == mes:
        donde = idx.get(d.isoformat())
        r = regiones(donde) if donde else set()
        clase = "n" if len(r) == len(COMUNIDADES) else "a" if r else "finde" if d.weekday() >= 5 else ""
        if d == marcado:
            clase += " sel"
        celdas.append(f'<a class="{clase.strip()}" href="{ruta_dia(d)}">{d.day}</a>')
        d += dt.timedelta(days=1)
    return f'<div class="mes"><h4>{MESES[mes - 1]} {anio}</h4><div class="dias">{"".join(celdas)}</div></div>'


def anio_proximo(mes, dia):
    """Año de la próxima vez que llega esta fecha (o el último año con datos)."""
    return next((a for a in ANIOS if dt.date(a, mes, dia) >= HOY), max(ANIOS))


def pagina_dia(datos, idx, mes, dia):
    nombre_dia = f"{dia} de {MESES[mes - 1]}"
    a_prox = anio_proximo(mes, dia)
    orden = [a_prox] + [a for a in ANIOS if a != a_prox]
    secciones, preguntas = [], []
    for anio in orden:
        d = dt.date(anio, mes, dia)
        donde = idx[anio].get(d.isoformat())
        si, texto = respuesta_dia(datos, anio, d, donde)
        pregunta = f"¿Es festivo el {fecha_larga(d)} de {anio}?"
        preguntas.append((pregunta, texto))
        detalle = municipios_dia(donde) if donde and donde["mun"] else ""
        if detalle:
            detalle = f"<h3>Municipios donde el {nombre_dia} de {anio} es fiesta local</h3>{detalle}"
        secciones.append(f"""<section id="festivo-{anio}"><h2>{escape(pregunta)}</h2>
<div class="hoy"><div class="tarjeta{' si' if si else ''}"><span class="etq">{fecha_larga(d)} de {anio}</span>
<p class="gran">{('No es festivo' if len(datos[anio]["locales"]) > len(INFO) / 2 else 'No es festivo nacional ni autonómico') if not si else 'Sí, es festivo en toda España' if len(regiones(donde)) == len(COMUNIDADES) else 'Festivo en algunas comunidades' if regiones(donde) else 'Festivo solo en algunos municipios'}</p></div></div>
<p>{texto}</p>
{detalle}
<p class="fuente">Fuente: <a href="{datos[anio]['boe']['url']}" rel="nofollow noopener">{escape(datos[anio]['boe']['titulo'])}</a> y los boletines oficiales de cada comunidad con las fiestas locales.</p></section>""")
    # Próximos festivos nacionales o autonómicos después de esta fecha
    base = dt.date(a_prox, mes, dia).isoformat()
    siguientes = sorted((f, a) for a in ANIOS for f, dn in idx[a].items() if f > base and dn["ccaa"])[:4]
    proximos = "".join(f'<li><a href="{ruta_dia(dt.date.fromisoformat(f))}">{fecha_larga(f)} de {a}</a>: festivo {resumen_dia(idx[a][f])}.</li>'
                       for f, a in siguientes)
    hoy_d = dt.date(a_prox, mes, dia)
    ayer, manana = hoy_d - dt.timedelta(days=1), hoy_d + dt.timedelta(days=1)
    if (ayer.month, ayer.day) == (2, 29):
        ayer -= dt.timedelta(days=1)
    cuerpo = f"""<h1>¿Es festivo el {nombre_dia}?</h1>
<p class="lead">Dónde es festivo el {nombre_dia} en {' y '.join(map(str, orden))}: fiestas nacionales y autonómicas del BOE y fiestas locales de cada municipio según los boletines oficiales.</p>
<p class="saltos"><a href="{ruta_dia(ayer)}">← {ayer.day} de {MESES[ayer.month - 1]}</a><a href="/es-festivo/">¿Es festivo hoy?</a><a href="{ruta_dia(manana)}">{manana.day} de {MESES[manana.month - 1]} →</a></p>
{''.join(secciones)}
{f'<section><h2>Próximos festivos después del {nombre_dia} de {a_prox}</h2><ul class="puentes">{proximos}</ul><p>Las fiestas locales cambian en cada municipio: <a href="/">busca el tuyo</a> para ver todos sus festivos.</p></section>' if proximos else ''}
<section><h2>Otros días de {MESES[mes - 1]}</h2><div class="calendario">{mes_enlazado(a_prox, mes, idx[a_prox], hoy_d)}</div>
<p class="leyenda"><span><span class="muestra n"></span> Festivo en toda España</span><span><span class="muestra a"></span> Festivo en alguna comunidad</span></p>
<p>Mira también el <a href="/calendario-laboral-{a_prox}/">calendario laboral de {a_prox}</a>, los <a href="/puentes-{a_prox}/">puentes de {a_prox}</a> o planifica tus días libres con el <a href="/planificador-vacaciones/">planificador de vacaciones</a>.</p></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    d = dt.date(a_prox, mes, dia)
    titulo = f"¿Es festivo el {fecha_larga(d)} de {a_prox}? Dónde es festivo"
    if len(titulo) > 65:
        titulo = f"¿Es festivo el {fecha_larga(d)} de {a_prox}?"
    desc = (f"Comprueba si el {nombre_dia} es festivo en tu comunidad o en tu municipio en {' y '.join(map(str, ANIOS))}: "
            "fiestas nacionales, autonómicas y locales según el BOE y los boletines oficiales.")
    return pagina(ruta_dia(d), titulo, desc, cuerpo, [("¿Es festivo hoy?", "/es-festivo/"), (nombre_dia.capitalize(), None)], [faq_ld(preguntas)])


def caja_dia(id_, etiqueta, d, resumen):
    """Respuesta de hoy o mañana tal como la escribe el script de /es-festivo/ (que la recalcula con la fecha del navegador)."""
    r = resumen.get(d.isoformat())
    texto = (("Festivo " if r.startswith("en ") else "Es ") + r) if r else "No es festivo en ninguna comunidad"
    return (f'<div class="tarjeta{" si" if r else ""}" id="{id_}"><span class="etq">{etiqueta}, {fecha_larga(d)}</span>'
            f'<p class="gran">{texto}</p><a href="{ruta_dia(d)}">Ver dónde es festivo →</a></div>')


def pagina_es_festivo(datos, idx):
    a = anio_proximo(HOY.month, HOY.day) if HOY.year in ANIOS else max(ANIOS)
    # Resumen corto de cada fecha para la respuesta de hoy y mañana (se calcula en el navegador con su fecha)
    resumen = {f: re.sub("<[^>]+>", "", resumen_dia(dn)) for an in ANIOS for f, dn in idx[an].items()}
    meses = "".join(mes_enlazado(a, m, idx[a]) for m in range(1, 13))
    preguntas = [
        ("¿Cómo sé si hoy es festivo en mi municipio?", "Busca tu municipio en el buscador de la portada: verás sus fiestas locales, las de tu comunidad y las nacionales, y si hoy o mañana es festivo allí."),
        ("¿Por qué un día es festivo en unas comunidades y en otras no?", "El Estado fija las fiestas nacionales, pero cada comunidad puede cambiar algunas por fiestas propias. Además, cada ayuntamiento elige dos fiestas locales al año."),
        ("¿Cuántos festivos hay al año en España?", "Como máximo 14 fiestas laborales retribuidas al año: 12 nacionales y autonómicas, que fija el BOE para cada comunidad, y 2 locales, que elige cada ayuntamiento."),
    ]
    script = ("<script>(function(){var R=" + json.dumps(resumen, ensure_ascii=False, separators=(",", ":")) + ",M="
              + json.dumps(MESES) + ",D=" + json.dumps(DIAS, ensure_ascii=False) + ";"
              "function iso(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}"
              "function caja(id,et,d){var e=document.getElementById(id);if(!e)return;var r=R[iso(d)],f=D[(d.getDay()+6)%7]+' '+d.getDate()+' de '+M[d.getMonth()];"
              "e.className='tarjeta'+(r?' si':'');e.innerHTML='<span class=\"etq\">'+et+', '+f+'</span><p class=\"gran\">'+(r?(r.indexOf('en ')===0?'Festivo ':'Es ')+r:'No es festivo en ninguna comunidad')+'</p>"
              "<a href=\"/es-festivo/'+d.getDate()+'-de-'+M[d.getMonth()]+'/\">Ver dónde es festivo →</a>'}"
              "var h=new Date();caja('f-hoy','Hoy',h);caja('f-manana','Mañana',new Date(h.getFullYear(),h.getMonth(),h.getDate()+1))})();</script>")
    cuerpo = f"""<h1>¿Es festivo hoy?</h1>
<p class="lead">Mira si hoy o mañana es festivo en España, en tu comunidad o en tu municipio, y elige cualquier día del año para ver dónde es festivo. Con los datos del BOE y de los boletines oficiales de cada comunidad.</p>
<div class="hoy">{caja_dia("f-hoy", "Hoy", HOY, resumen)}{caja_dia("f-manana", "Mañana", HOY + dt.timedelta(days=1), resumen)}</div>
<p>Las fiestas locales cambian en cada pueblo y ciudad: <a href="/">busca tu municipio</a> para ver exactamente sus festivos.</p>
<section><h2>Elige un día de {a}</h2>
<p class="leyenda"><span><span class="muestra n"></span> Festivo en toda España</span><span><span class="muestra a"></span> Festivo en alguna comunidad</span></p>
<div class="calendario">{meses}</div></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    return pagina("/es-festivo/", "¿Es festivo hoy? Mira si hoy o mañana es festivo en España",
                  "Comprueba si hoy o mañana es festivo en España, en tu comunidad o en tu municipio, y dónde es festivo cualquier día del año.",
                  cuerpo, [("¿Es festivo hoy?", None)], [faq_ld(preguntas)], scripts=script)


# ---------------------------------------------------------------- calendario escolar

ESCOLAR = RAIZ / "data" / "escolar.json"
CLASES_FUERA = "fuera"


def cargar_escolar():
    return json.loads(ESCOLAR.read_text(encoding="utf-8")) if ESCOLAR.exists() else None


def rango_escolar(desde, hasta):
    a, b = dt.date.fromisoformat(desde), dt.date.fromisoformat(hasta)
    if a == b:
        return f"el {fecha_larga(a)}"
    return rango(a, b)


def rango_corto(desde, hasta):
    a, b = dt.date.fromisoformat(desde), dt.date.fromisoformat(hasta)
    return f"{a.day} {MESES[a.month - 1][:3]} – {b.day} {MESES[b.month - 1][:3]}"


def fecha_corta(f):
    d = dt.date.fromisoformat(f)
    return f"{d.day} {MESES[d.month - 1][:3]}"


def principal(lista):
    """La fila de Infantil y Primaria (la que más gente busca) o, si no hay, la primera."""
    return next((x for x in lista if "Primaria" in x["etapas"]), lista[0]) if lista else None


def resumen_escolar(t):
    vac = {k: next((v for v in t["vacaciones"] if k in v["nombre"].lower()), None) for k in ("navidad", "semana santa")}
    if not vac["semana santa"]:
        vac["semana santa"] = next((v for v in t["vacaciones"] if "pascua" in v["nombre"].lower() or "pasqua" in v["nombre"].lower()), None)
    return principal(t["inicio"]), principal(t["fin"]), vac["navidad"], vac["semana santa"]


def calendario_escolar(t, datos):
    """Septiembre a junio con los días sin clase marcados (vacaciones, no lectivos y festivos de la comunidad)."""
    ini, fin, _, _ = resumen_escolar(t)
    d0, d1 = dt.date.fromisoformat(ini["fecha"]), dt.date.fromisoformat(fin["fecha"])
    festivos = {}
    for anio in (2026, 2027):
        if anio in datos:
            for x in datos[anio]["nacionales_autonomicos"].get(t["ccaa"], []):
                festivos[x["f"]] = ("n" if x["t"] == "nacional" else "a", x["n"])
    marcas = {}
    for v in t["vacaciones"]:
        d, h = dt.date.fromisoformat(v["desde"]), dt.date.fromisoformat(v["hasta"])
        while d <= h:
            marcas.setdefault(d.isoformat(), ("vac", v["nombre"]))
            d += dt.timedelta(days=1)
    for x in t["no_lectivos"]:
        marcas.setdefault(x["fecha"], ("nl", x["motivo"]))
    html = []
    for anio, mes in [(2026, m) for m in range(9, 13)] + [(2027, m) for m in range(1, 7)]:
        primero = dt.date(anio, mes, 1)
        celdas = ['<span class="cab">' + c + "</span>" for c in "LMXJVSD"] + ["<span></span>"] * primero.weekday()
        d = primero
        while d.month == mes:
            f = d.isoformat()
            clase, titulo = "", ""
            if f in festivos:
                clase, titulo = festivos[f]
            elif d.weekday() >= 5:
                clase = "finde"
            elif d < d0 or d > d1:
                clase, titulo = CLASES_FUERA, "Sin clase (fuera del curso)"
            elif f in marcas:
                clase, titulo = marcas[f]
            celdas.append(f'<span class="{clase}"' + (f' title="{escape(titulo)}"' if titulo else "") + f">{d.day}</span>")
            d += dt.timedelta(days=1)
        html.append(f'<div class="mes"><h4>{MESES[mes - 1]} {anio}</h4><div class="dias">{"".join(celdas)}</div></div>')
    leyenda = ('<div class="leyenda"><span><i class="vac"></i>Vacaciones</span><span><i class="nl"></i>Día no lectivo</span>'
               '<span><i class="n"></i>Festivo nacional</span><span><i class="a"></i>Festivo autonómico</span></div>')
    return leyenda + '<div class="calendario">' + "".join(html) + "</div>"


def fuente_escolar(t):
    enlaces = " · ".join(f'<a href="{escape(u)}" rel="nofollow noopener">documento oficial{"" if i == 0 else f" ({i + 1})"}</a>'
                         for i, u in enumerate(dict.fromkeys(u for u in t["urls"].values() if u)))
    return f'<p class="fuente">Fuente: {escape(t["norma"] or "norma oficial de la consejería de educación")}. {enlaces}.</p>'


def seccion_escolar(t, datos, titulo):
    filas = []
    for etiqueta, lista in (("Empiezan las clases", t["inicio"]), ("Terminan las clases", t["fin"])):
        for x in lista:
            filas.append(f"<tr><td>{etiqueta}</td><td>{escape(x['etapas'])}</td><td><b>{fecha_larga(x['fecha'])} de {x['fecha'][:4]}</b></td></tr>")
    vac = "".join(f"<li><b>{escape(v['nombre'])}</b>: {rango_escolar(v['desde'], v['hasta'])}.</li>" for v in t["vacaciones"])
    nl = "".join(f"<li>{fecha_larga(x['fecha'])} de {x['fecha'][:4]}: {escape(x['motivo'])}.</li>" for x in sorted(t["no_lectivos"], key=lambda x: x["fecha"]))
    locales = f'<p class="nota"><b>Días locales:</b> {escape(t["locales"])}</p>' if t.get("locales") else ""
    return f"""<section class="escolar" id="{t['id']}"><h2>{escape(titulo)}</h2>
<div class="tabla-envoltorio"><table class="festivos tabla-escolar"><thead><tr><th></th><th>Enseñanzas</th><th>Fecha</th></tr></thead><tbody>{''.join(filas)}</tbody></table></div>
<h3>Vacaciones</h3><ul>{vac}</ul>
{f'<h3>Otros días sin clase</h3><ul>{nl}</ul>' if nl else ''}
{locales}
<h3>El curso de un vistazo</h3>
{calendario_escolar(t, datos)}
{fuente_escolar(t)}
</section>"""


def pagina_escolar_ccaa(esc, ccaa, datos):
    nombre = COMUNIDADES[ccaa][0]
    ts = [t for t in esc["territorios"] if t["ccaa"] == ccaa]
    curso = esc["curso"]
    ini, fin, nav, ss = resumen_escolar(ts[0])
    varias = len(ts) > 1
    if varias:
        filas = "".join(
            f'<tr><td><a href="#{t["id"]}">{escape(t["provincia"])}</a></td><td>{fecha_corta(r[0]["fecha"])}</td>'
            f'<td>{fecha_corta(r[1]["fecha"])}</td><td>{rango_corto(r[2]["desde"], r[2]["hasta"]) if r[2] else "—"}</td>'
            f'<td>{rango_corto(r[3]["desde"], r[3]["hasta"]) if r[3] else "—"}</td></tr>'
            for t, r in ((t, resumen_escolar(t)) for t in ts))
        cabeza = (f'<p>En {escape(nombre)} cada provincia aprueba su propio calendario escolar. Este es el resumen para Infantil y Primaria; '
                  f'pulsa en tu provincia para ver todas las etapas y los días sin clase.</p>'
                  f'<div class="tabla-envoltorio"><table class="festivos tabla-escolar"><thead><tr><th>Provincia</th><th>Empiezan</th><th>Terminan</th>'
                  f'<th>Navidad</th><th>Semana Santa</th></tr></thead><tbody>{filas}</tbody></table></div>')
    else:
        cabeza = f"""<ul class="cifras escolar-cifras">
<li><span>Empiezan las clases</span><b>{fecha_larga(ini['fecha'], False)}</b><span>{escape(ini['etapas'])}</span></li>
<li><span>Terminan</span><b>{fecha_larga(fin['fecha'], False)}</b><span>{escape(fin['etapas'])}</span></li>
<li><span>Navidad</span><b>{rango_escolar(nav['desde'], nav['hasta']) if nav else '—'}</b><span>vacaciones</span></li></ul>"""
    secciones = "".join(seccion_escolar(t, datos, f"Calendario escolar en {t['provincia']}" if varias else "Fechas del curso por etapas") for t in ts)
    pendientes = [p["provincia"] for p in esc["pendientes"] if p["ccaa"] == ccaa and p.get("provincia")]
    aviso = (f'<p class="pendiente">Todavía no tenemos comprobado el calendario de {", ".join(pendientes)}: lo añadiremos en cuanto lo tengamos del documento oficial.</p>'
             if pendientes else "")
    preguntas = [(f"¿Cuándo empiezan las clases en {nombre} en el curso {curso}?",
                  f"Infantil y Primaria empiezan el {fecha_larga(ini['fecha'])} de {ini['fecha'][:4]}" + (" (según la provincia puede variar; mira la tabla)" if varias else "") + "."),
                 (f"¿Cuándo terminan las clases en {nombre}?", f"Infantil y Primaria terminan el {fecha_larga(fin['fecha'])} de {fin['fecha'][:4]}.")]
    if nav:
        preguntas.append((f"¿Cuándo son las vacaciones de Navidad {curso} en {nombre}?", f"Las vacaciones de Navidad son {rango_escolar(nav['desde'], nav['hasta'])}."))
    if ss:
        preguntas.append((f"¿Cuándo son las vacaciones de Semana Santa 2027 en {nombre}?", f"Las vacaciones de Semana Santa son {rango_escolar(ss['desde'], ss['hasta'])}."))
    cuerpo = f"""<h1>Calendario escolar {curso} {escape(de(nombre))}</h1>
<p class="lead">Cuándo empiezan y terminan las clases, las vacaciones de Navidad y Semana Santa y los días sin cole del curso {curso} {escape(en(nombre))}, sacados de la norma oficial de la consejería de educación.</p>
{cabeza}{aviso}
{secciones}
<section class="contenido"><h2>Organiza las vacaciones con las de los niños</h2>
<p>Mira los <a href="/comunidad/{ccaa}/">festivos {escape(de(nombre))}</a> y las fiestas locales de tu municipio, que también son días sin clase, o usa el <a href="/planificador-vacaciones/">planificador de vacaciones</a> para encadenar puentes. Puedes ver el <a href="/calendario-escolar/">calendario escolar de todas las comunidades</a>.</p>
<p>Cada centro puede tener además días de libre disposición o fiestas propias: confírmalos siempre con el colegio o el instituto.</p></section>
<section><h2>Preguntas frecuentes</h2><div class="faq">{faq_html(preguntas)}</div></section>"""
    return pagina(f"/calendario-escolar/{ccaa}/", f"Calendario escolar {curso} {de(nombre)}: inicio de curso y vacaciones",
                  f"Cuándo empiezan las clases en {nombre} en el curso {curso}, las vacaciones de Navidad y Semana Santa y los días no lectivos, según la norma oficial.",
                  cuerpo, [("Calendario escolar", "/calendario-escolar/"), (nombre, None)], [faq_ld(preguntas)])


def pagina_escolar_indice(esc):
    curso = esc["curso"]
    por_ccaa = {}
    for t in esc["territorios"]:
        por_ccaa.setdefault(t["ccaa"], []).append(t)
    filas = []
    for ccaa, (nombre, _) in sorted(COMUNIDADES.items(), key=lambda x: x[1][0]):
        if ccaa not in por_ccaa:
            continue
        ts = por_ccaa[ccaa]
        res = [resumen_escolar(t) for t in ts]
        def celda(i, fmt):
            vals = sorted({fmt(r[i]) for r in res if r[i]})
            return " / ".join(vals) if len(vals) <= 2 else "según la provincia"
        def dias(i):
            fs = sorted({r[i]["fecha"] for r in res if r[i]})
            return fecha_corta(fs[0]) if len(fs) == 1 else f"{fecha_corta(fs[0])} – {fecha_corta(fs[-1])}"
        filas.append(f'<tr><td><a href="/calendario-escolar/{ccaa}/">{escape(nombre)}</a></td>'
                     f'<td>{dias(0)}</td><td>{dias(1)}</td>'
                     f'<td>{celda(2, lambda v: rango_corto(v["desde"], v["hasta"]))}</td><td>{celda(3, lambda v: rango_corto(v["desde"], v["hasta"]))}</td></tr>')
    faltan = sorted({COMUNIDADES[c][0] for c in COMUNIDADES if c not in por_ccaa})
    cuerpo = f"""<h1>Calendario escolar {curso} por comunidades</h1>
<p class="lead">Cuándo empiezan las clases, las vacaciones de Navidad y Semana Santa y cuándo acaba el curso {curso} en cada comunidad autónoma, sacado de la orden o resolución oficial de cada consejería de educación.</p>
<div class="tabla-envoltorio"><table class="festivos tabla-escolar"><thead><tr><th>Comunidad</th><th>Empiezan (Primaria)</th><th>Terminan</th><th>Navidad</th><th>Semana Santa</th></tr></thead>
<tbody>{''.join(filas)}</tbody></table></div>
{f'<p class="pendiente">Estamos comprobando con el documento oficial el calendario de {", ".join(faltan)}. Lo añadiremos en cuanto esté verificado: no publicamos fechas sacadas de la prensa.</p>' if faltan else ''}
<section class="contenido"><h2>Cómo leer el calendario escolar</h2>
<p>Cada comunidad aprueba cada primavera el calendario del curso siguiente: el primer y el último día de clase de cada etapa, las vacaciones de Navidad y Semana Santa y otros días no lectivos. En algunas, como Andalucía, Aragón o Castilla-La Mancha, cada provincia tiene su propio calendario.</p>
<p>Además, las dos fiestas locales de cada municipio son días sin clase, y muchos centros tienen días de libre disposición que fija su consejo escolar. Consulta los <a href="/">festivos de tu municipio</a> y confirma siempre los días propios con el colegio.</p></section>"""
    return pagina("/calendario-escolar/", f"Calendario escolar {curso}: inicio de curso y vacaciones por comunidades",
                  f"Cuándo empiezan las clases del curso {curso} en cada comunidad autónoma, las vacaciones de Navidad y Semana Santa y el fin de curso, según las normas oficiales.",
                  cuerpo, [("Calendario escolar", None)])


def datos_provincias(datos, info):
    """Un JSON por provincia para la calculadora: festivos de cada municipio y año."""
    (WEB / "datos").mkdir(exist_ok=True)
    for codp, (_, ccaa) in PROVINCIAS.items():
        salida = {"anios": ANIOS, "comunidad": {}, "comunes": {}, "locales": {}}
        for anio in ANIOS:
            d = datos[anio]
            salida["comunidad"][anio] = [[x["f"], x["n"], x["t"][0]] for x in d["nacionales_autonomicos"][ccaa]]
            salida["comunes"][anio] = [[x["f"], x["n"] or "Fiesta local"] for x in d.get("comunes", {}).get(codp, [])]
            salida["locales"][anio] = {c: [[x["f"], x["n"] or "Fiesta local"] for x in v] for c, v in d["locales"].items() if c[:2] == codp}
        (WEB / "datos" / f"{codp}.json").write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def lista_comunidades():
    return '<ul class="lista-municipios">' + "".join(f'<li><a href="/comunidad/{c}/">{escape(n)}</a></li>' for c, (n, _) in
                                                       sorted(COMUNIDADES.items(), key=lambda x: x[1][0])) + "</ul>"


def portada(datos):
    anio_sig = max(ANIOS)
    d_sig = datos[anio_sig]["nacionales_autonomicos"]
    comunes_sig = set.intersection(*[{x["f"] for x in l} for l in d_sig.values()])
    nacionales = [x for x in d_sig["madrid"] if x["f"] in comunes_sig]
    # Festivos comunes a toda España de todos los años, para la cuenta atrás y las hojas de calendario
    todos = []
    for a in ANIOS:
        da = datos[a]["nacionales_autonomicos"]
        com = set.intersection(*[{x["f"] for x in l} for l in da.values()])
        todos += [[x["f"], x["n"]] for x in da["madrid"] if x["f"] in com]
    proximos = [x for x in todos if x[0] >= HOY.isoformat()][:4]
    hojas = "".join(
        f'<li class="hoja"><span class="hoja-mes">{MESES[int(f[5:7]) - 1][:3]}</span><b>{int(f[8:])}</b>'
        f'<span class="hoja-dia">{DIAS[dt.date.fromisoformat(f).weekday()]}</span><small>{escape(n)}</small></li>' for f, n in proximos)
    populares = ["28079", "08019", "46250", "41091", "50297", "29067", "30030", "03065", "03014", "48020", "28065", "14021", "47186", "36057", "33024", "26089"]
    chips = "".join(f'<li><a href="{INFO[c]["url"]}">{escape(INFO[c]["nombre"].split(" / ")[-1])}</a></li>' for c in populares if c in INFO)
    tarjetas_ccaa = "".join(
        f'<li><a href="/comunidad/{c}/"><b>{escape(n)}</b><span>{len(d_sig[c])} festivos en {anio_sig}</span></a></li>'
        for c, (n, _) in sorted(COMUNIDADES.items(), key=lambda x: x[1][0]))
    embebido = {"municipio": "España", "festivos": {anio_sig: [[x["f"], x["n"], "n"] for x in nacionales]}, "locales": [], "proximos": todos}
    cuerpo = f"""<section class="portada">
<div class="portada-texto">
<h1>Los festivos de tu municipio</h1>
<p class="lead">Fiestas locales, autonómicas y nacionales de los más de 8.000 municipios de España, con los puentes y el próximo festivo. Sacadas del BOE y de los boletines oficiales de cada comunidad.</p>
<form class="buscador" role="search" action="/" onsubmit="return false"><label for="q" class="oculto">Municipio</label>
<input id="q" type="search" placeholder="Busca tu municipio: Getafe, Elche, Reus…" autocomplete="off"><ul id="sugerencias" class="sugerencias"></ul></form>
<ul class="chips">{chips}</ul>
</div>
<div class="hoy-portada" id="hoy-portada"><span class="etq">Hoy es</span><b id="hoy-fecha">{fecha_larga(HOY)}</b>
<span class="etq">Próximo festivo en toda España</span><b id="prox-fecha">{fecha_larga(proximos[0][0]) if proximos else ''}</b>
<span id="prox-nombre">{escape(proximos[0][1]) if proximos else ''}</span><span class="cuenta" id="prox-cuenta"></span></div>
</section>
<section><h2>Próximos festivos nacionales</h2><ul class="hojas">{hojas}</ul></section>
<section class="accesos">
<a class="acceso" href="/calendario-laboral-{anio_sig}/"><span class="ico">📅</span><b>Calendario laboral {anio_sig}</b><span>Todos los festivos de España y qué se celebra en cada comunidad.</span></a>
<a class="acceso" href="/puentes-{anio_sig}/"><span class="ico">🌉</span><b>Puentes {anio_sig}</b><span>Qué días pedir de vacaciones para encadenar más días libres.</span></a>
<a class="acceso" href="/es-festivo/"><span class="ico">❓</span><b>¿Es festivo hoy?</b><span>Si hoy o mañana es festivo y dónde es festivo cualquier día del año.</span></a>
<a class="acceso" href="/calendario-escolar/"><span class="ico">🎒</span><b>Calendario escolar</b><span>Cuándo empiezan las clases y las vacaciones de Navidad y Semana Santa en cada comunidad.</span></a>
<a class="acceso" href="/planificador-vacaciones/"><span class="ico">🏖️</span><b>Planificador de vacaciones</b><span>Qué días pedir en tu municipio para tener más días libres con tus días de vacaciones.</span></a>
<a class="acceso" href="/calendario-laboral-para-imprimir/"><span class="ico">🖨️</span><b>Calendario para imprimir</b><span>El año entero en una hoja A4, con las fiestas de tu pueblo. En PDF.</span></a>
<a class="acceso" href="/calculadora-dias-laborables/"><span class="ico">🧮</span><b>Días laborables</b><span>Cuenta días laborables o hábiles con los festivos de tu municipio.</span></a>
</section>
<section><h2>{anio_sig} de un vistazo</h2>
<p>Los {len(nacionales)} festivos nacionales que se celebran en toda España. Busca tu municipio para ver también los de tu comunidad y tus fiestas locales.</p>
<div class="calendario" data-anio="{anio_sig}"></div></section>
<section id="comunidades"><h2>Festivos por comunidad autónoma</h2><ul class="tarjetas-ccaa">{tarjetas_ccaa}</ul></section>
<section class="contenido"><h2>¿Cuántos festivos hay al año?</h2>
<p>En España hay como máximo 14 fiestas laborales al año: 12 las fija el Estado y cada comunidad autónoma, que puede cambiar algunas fiestas nacionales por otras propias, y 2 son locales, elegidas por cada ayuntamiento. Por eso los festivos cambian de un municipio a otro aunque estén en la misma provincia.</p>
<p>El calendario nacional y autonómico se publica en el BOE en otoño del año anterior. Las fiestas locales las publica cada comunidad en su boletín oficial, normalmente entre el verano y el final del año anterior.</p></section>
<script type="application/json" id="datos-festivos">{json.dumps(embebido, ensure_ascii=False, separators=(",", ":"))}</script>"""
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
    global ANIOS, RUTAS_PROV, INFO
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
        if cuenta[s] > 1 or s in RESERVADOS or s.startswith(("calendario-laboral", "puentes-")):
            s = f"{s}-{slug(PROVINCIAS[cod[:2]][0])}"
        info[cod] = {"nombre": bonito(nom), "nombre_ine": nom, "url": f"/{s}/"}
    assert len({m["url"] for m in info.values()}) == len(info), "rutas repetidas"
    INFO = info

    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    for f in ("style.css", "app.js", "calculadora.js", "imprimible.js", "planificador.js"):
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
        guardar(f"/puentes-{anio}/", pagina_puentes(datos, anio))
        rutas_sitemap += [f"/calendario-laboral-{anio}/", f"/puentes-{anio}/"]
    guardar("/calculadora-dias-laborables/", pagina_calculadora(datos))
    rutas_sitemap.append("/calculadora-dias-laborables/")
    guardar("/calendario-laboral-para-imprimir/", pagina_imprimible(datos))
    rutas_sitemap.append("/calendario-laboral-para-imprimir/")
    guardar("/planificador-vacaciones/", pagina_planificador(datos))
    rutas_sitemap.append("/planificador-vacaciones/")
    esc = cargar_escolar()
    if esc:
        guardar("/calendario-escolar/", pagina_escolar_indice(esc))
        rutas_sitemap.append("/calendario-escolar/")
        for ccaa in sorted({t["ccaa"] for t in esc["territorios"]}):
            guardar(f"/calendario-escolar/{ccaa}/", pagina_escolar_ccaa(esc, ccaa, datos))
            rutas_sitemap.append(f"/calendario-escolar/{ccaa}/")
    idx = {a: indice_fechas(datos, a) for a in ANIOS}
    guardar("/es-festivo/", pagina_es_festivo(datos, idx))
    rutas_sitemap.append("/es-festivo/")
    for mes in range(1, 13):
        for dia in range(1, 32):
            try:
                dt.date(2027, mes, dia)  # año no bisiesto: sin 29 de febrero
            except ValueError:
                continue
            html = pagina_dia(datos, idx, mes, dia)
            guardar(f"/es-festivo/{dia}-de-{MESES[mes - 1]}/", html)
            rutas_sitemap.append(f"/es-festivo/{dia}-de-{MESES[mes - 1]}/")
    datos_provincias(datos, info)
    guardar("/", portada(datos))
    rutas_sitemap += legales()

    # Índice del buscador: [nombre para buscar, nombre visible, ruta, provincia]
    indice = [[re.sub(r"[^a-z0-9ñ/ ]", " ", m["nombre"].lower()), m["nombre"], m["url"], PROVINCIAS[c[:2]][0], c] for c, m in info.items()]
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
INFO = {}

if __name__ == "__main__":
    main()
