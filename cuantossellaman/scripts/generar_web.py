"""Genera la web estática de «¿Cuántos se llaman?» en cuantossellaman/web/ a partir de /data.

Uso:
    python cuantossellaman/scripts/generar_web.py                 # umbral por defecto
    python cuantossellaman/scripts/generar_web.py --umbral 2000   # menos páginas de nombre

Umbral de indexación: un nombre tiene página propia (indexable y en el sitemap) si lo llevan al
menos UMBRAL personas en España (sumando hombres y mujeres) o si aparece en alguna tabla de
ranking del INE (top por provincia, por década o de bebés). El resto se consulta solo desde el
buscador, que lee /indice/<letra>.json y no crea ninguna URL.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tildes import mostrar, mostrar_apellido, normalizar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
WEB = RAIZ / "web"
PLANTILLA = RAIZ / "plantilla"
SIGNIFICADOS = RAIZ / "content" / "significados"
ORIGENES_APELLIDOS = RAIZ / "content" / "significados-apellidos"
DOMINIO = "https://cuantossellaman.es"
SITIO = "¿Cuántos se llaman?"
UMBRAL_POR_DEFECTO = 1000
UMBRAL_APELLIDOS_POR_DEFECTO = 2000  # personas con ese PRIMER apellido para tener página propia
MIN_PAGINAS = 500  # si salen menos, algo ha ido mal: el script falla para no publicar una web rota

TITULAR = {"nombre": "Albert Sanchez Guiu", "nif": "48167483D", "domicilio": "La Roca del Vallès (Barcelona), España",
           "email": "contacto.ahorrometro@gmail.com"}

PROVINCIAS = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila", "06": "Badajoz",
    "07": "Baleares", "08": "Barcelona", "09": "Burgos", "10": "Cáceres", "11": "Cádiz", "12": "Castellón",
    "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña", "16": "Cuenca", "17": "Girona", "18": "Granada",
    "19": "Guadalajara", "20": "Gipuzkoa", "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León",
    "25": "Lleida", "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
    "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas", "36": "Pontevedra",
    "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria", "40": "Segovia", "41": "Sevilla",
    "42": "Soria", "43": "Tarragona", "44": "Teruel", "45": "Toledo", "46": "Valencia", "47": "Valladolid",
    "48": "Bizkaia", "49": "Zamora", "50": "Zaragoza", "51": "Ceuta", "52": "Melilla",
}
SEXO = {"H": ("hombre", "hombres", "niños"), "M": ("mujer", "mujeres", "niñas")}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", normalizar(texto)).strip("-")


def n(x):
    return f"{x:,}".replace(",", ".")


def dec(x):
    return f"{x:.1f}".replace(".", ",")


def fecha_larga(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def etiqueta_decada(clave, d):
    if clave == "antes-1930":
        return "antes de 1930"
    return f"años {str(d['desde'])[2:]}" if d["desde"] < 2000 else f"años {d['desde']}"


def titulo_decada(clave, d):
    if clave == "antes-1930":
        return "Nombres más comunes de los nacidos antes de 1930"
    return f"Nombres más comunes de los nacidos en los {etiqueta_decada(clave, d)}"


# ------------------------------------------------------------------------------------- Carga
def cargar():
    leer = lambda f: json.loads((DATOS / f).read_text(encoding="utf-8"))  # noqa: E731
    return leer("nombres.json"), leer("provincias.json"), leer("decadas.json"), leer("bebes.json"), leer("apellidos.json")


def construir_indice(nombres, provincias, decadas, bebes, umbral):
    """Une hombres y mujeres por forma normalizada y decide qué nombres tienen página."""
    idx = {}
    for s in "HM":
        for x in nombres[s]:
            k = normalizar(x["n"])
            e = idx.setdefault(k, {"k": k, "ine": x["n"], "mostrar": mostrar(x["n"]), "H": None, "M": None})
            e[s] = {"f": x["f"], "r": x["r"], "e": x["e"]}
    for e in idx.values():
        e["total"] = sum(e[s]["f"] for s in "HM" if e[s])
        e["slug"] = slug(e["k"])
        e["prov"], e["dec"], e["beb"] = [], {}, {}

    en_listas = set()
    for cod, p in provincias.items():
        for s in "HM":
            for pos, (nom, f) in enumerate(p[s], 1):
                k = normalizar(nom)
                en_listas.add(k)
                if k in idx:
                    idx[k]["prov"].append({"cod": cod, "s": s, "pos": pos, "f": f})
    for clave, d in decadas.items():
        for s in "HM":
            for pos, (nom, f) in enumerate(d.get(s, []), 1):
                k = normalizar(nom)
                en_listas.add(k)
                if k in idx:
                    idx[k]["dec"].setdefault(clave, {})[s] = {"pos": pos, "f": f}
    for anio, zonas in bebes.items():
        for s in "HM":
            for pos, (nom, f) in enumerate(zonas["espana"][s]["top"], 1):
                k = normalizar(nom)
                en_listas.add(k)
                if k in idx:
                    idx[k]["beb"].setdefault(anio, {})[s] = {"pos": pos, "f": f}
            for zona, z in zonas.items():
                if zona != "espana":
                    for nom, _ in z[s]["top"]:
                        en_listas.add(normalizar(nom))

    for e in idx.values():
        e["pagina"] = e["total"] >= umbral or e["k"] in en_listas
    return idx


# ------------------------------------------------------------------------------------ Plantilla
def pagina(ruta, titulo, descripcion, cuerpo, migas=None, extra_ld=None, indexable=True):
    """ruta: '/nombre/albert/' (con barras). migas: [(texto, ruta o None), ...]."""
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
<meta name="theme-color" content="#3f51c4">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITIO}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
{f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''}
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
<body>
<header class="site-header">
  <div class="container">
    <a href="/" class="logo"><span class="logo-mark">?</span><span>¿Cuántos se <span class="hl">llaman</span>?</span></a>
    <nav class="nav">
      <a href="/apellidos/">Apellidos</a>
      <a href="/provincias/">Por provincia</a>
      <a href="/decadas/">Por década</a>
      <a href="/bebes/">Bebés</a>
      <a href="/sobre-los-datos/">Sobre los datos</a>
    </nav>
  </div>
</header>
<main class="container">
{migas_html}
{cuerpo}
</main>
<footer class="site-footer">
  <div class="container">
    <p><strong>{SITIO}</strong> responde cuántas personas se llaman o se apellidan de cada forma en España con los datos oficiales del Instituto Nacional de Estadística (INE).</p>
    <div class="links"><a href="/">Buscar un nombre</a><a href="/apellidos/">Apellidos</a><a href="/provincias/">Provincias</a><a href="/decadas/">Décadas</a><a href="/bebes/">Bebés</a><a href="/sobre-los-datos/">Sobre los datos</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a></div>
    <p>Fuente: INE. Datos reutilizados conforme a sus condiciones de uso; esta web no está vinculada al INE.</p>
  </div>
</footer>
</body>
</html>
"""


def guardar(ruta, html):
    destino = WEB / ruta.strip("/") / "index.html" if ruta.endswith("/") else WEB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


def enlace(idx, nombre_ine, texto=None):
    e = idx.get(normalizar(nombre_ine))
    t = escape(texto or (e["mostrar"] if e else mostrar(nombre_ine)))
    return f'<a href="/nombre/{e["slug"]}/">{t}</a>' if e and e["pagina"] else t


def tabla_ranking(idx, lista, sexo, extra_por_mil=None):
    filas = "".join(f'<tr><td class="num">{i}</td><td>{enlace(idx, nom)}</td><td class="num">{n(f)}</td></tr>'
                    for i, (nom, f) in enumerate(lista, 1))
    return (f'<div class="table-wrap"><table class="data"><thead><tr><th class="num">#</th><th>Nombre de {SEXO[sexo][0]}</th>'
            f'<th class="num">Personas</th></tr></thead><tbody>{filas}</tbody></table></div>')


def barras(filas_datos):
    """filas_datos: [(etiqueta, valor o None, texto_valor)]"""
    maximo = max([v for _, v, _ in filas_datos if v] or [1])
    li = ""
    for et, v, tv in filas_datos:
        if v:
            li += f'<li><span>{escape(et)}</span><span class="barra"><span style="width:{max(2, v / maximo * 100):.1f}%"></span></span><span class="v">{tv}</span></li>'
        else:
            li += f'<li class="vacio"><span>{escape(et)}</span><span class="barra"></span><span class="v">{tv}</span></li>'
    return f'<ul class="barras">{li}</ul>'


def top3(idx, lista, k=3):
    """Lista ordenada corta: 1. Lucía 3.325 · 2. Sofía 2.830 · 3. Martina 2.364"""
    return '<ol class="top3">' + "".join(f"<li>{enlace(idx, x)} <small>{n(f)}</small></li>" for x, f in lista[:k]) + "</ol>"


def movimientos(lista, anterior):
    """Compara dos tops del INE: nombres nuevos, los que más suben y los que más bajan (dentro del top)."""
    antes = {x: i for i, (x, _) in enumerate(anterior, 1)}
    ahora = {x: i for i, (x, _) in enumerate(lista, 1)}
    nuevos = [(x, ahora[x]) for x, _ in lista if x not in antes]
    cambios = [(x, antes[x] - ahora[x], ahora[x]) for x, _ in lista if x in antes]
    suben = sorted([c for c in cambios if c[1] > 0], key=lambda c: -c[1])[:5]
    bajan = sorted([c for c in cambios if c[1] < 0], key=lambda c: c[1])[:5]
    return nuevos, suben, bajan


def bloque_movimientos(idx, lista, anterior, etiqueta):
    """Columna «Niños» o «Niñas» del panel de cambios: suben, bajan y nuevos en el top."""
    nuevos, suben, bajan = movimientos(lista, anterior)
    fila = lambda x, insignia, p: (f'<li><span class="mov-nombre">{enlace(idx, x)}</span>{insignia}'  # noqa: E731
                                   f'<span class="mov-pos">{p}.º</span></li>')
    html = f'<section class="mov"><h3>{etiqueta}</h3>'
    if suben:
        html += '<h4>Los que más suben</h4><ul class="mov-lista">' + "".join(
            fila(x, f'<span class="mov-badge sube" title="Sube {d} puestos">▲ {d}</span>', p) for x, d, p in suben) + "</ul>"
    if bajan:
        html += '<h4>Los que más bajan</h4><ul class="mov-lista">' + "".join(
            fila(x, f'<span class="mov-badge baja" title="Baja {-d} puestos">▼ {-d}</span>', p) for x, d, p in bajan) + "</ul>"
    if nuevos:
        html += '<h4>Nuevos en el top 100</h4><ul class="mov-lista">' + "".join(
            fila(x, '<span class="mov-badge nuevo" title="No estaba entre los 100 primeros el año anterior">nuevo</span>', p) for x, p in nuevos) + "</ul>"
    return html + "</section>"


def panel_movimientos(idx, bebes, anio, anterior, titulo, extra=""):
    a, b = bebes[anio]["espana"], bebes[anterior]["espana"]
    return (f'<div class="content"><h2>{titulo}</h2><p class="updated">Cambios de puesto entre los 100 nombres más puestos de {anterior} y de {anio}.</p>'
            '<div class="mov-grid">'
            + bloque_movimientos(idx, a["H"]["top"], b["H"]["top"], "Niños")
            + bloque_movimientos(idx, a["M"]["top"], b["M"]["top"], "Niñas")
            + f"</div>{extra}</div>")


# ---------------------------------------------------------------------------------- Página nombre
def similares(e, idx, por_total):
    primera = e["k"].split()[0]
    raiz = primera[:4]
    variantes = [x for x in por_total if x is not e and x["pagina"] and len(x["k"].split()) <= 2
                 and x["k"].split()[0][:4] == raiz and abs(len(x["k"].split()[0]) - len(primera)) <= 3]
    variantes = sorted(variantes, key=lambda x: (x["k"].split()[0] != primera, -x["total"]))[:8]
    pos = por_total.index(e)
    cerca = [x for x in por_total[max(0, pos - 6):pos + 7] if x is not e and x["pagina"] and x not in variantes][:8]
    return variantes, cerca


def pagina_nombre(e, idx, por_total, ref, provincias, decadas, bebes):
    X = e["mostrar"]
    sexos = [s for s in "HM" if e[s]]
    referencia = fecha_larga(ref)
    # Respuesta directa
    if len(sexos) == 2:
        respuesta = (f"En España hay <strong>{n(e['H']['f'])} hombres</strong> y <strong>{n(e['M']['f'])} mujeres</strong> "
                     f"que se llaman {escape(X)}: {n(e['total'])} personas en total. Es el nombre número {n(e['H']['r'])} "
                     f"entre los hombres y el {n(e['M']['r'])} entre las mujeres.")
        cifra = n(e["total"])
    else:
        s = sexos[0]
        respuesta = (f"En España hay <strong>{n(e[s]['f'])} {SEXO[s][1]}</strong> que se llaman {escape(X)}. "
                     + (f"Es el nombre de {SEXO[s][0]} más frecuente de España." if e[s]["r"] == 1 else
                        f"Es el nombre de {SEXO[s][0]} número {n(e[s]['r'])} más frecuente."))
        cifra = n(e[s]["f"])
    edades = [f"{dec(e[s]['e'])} años ({SEXO[s][1]})" if len(sexos) == 2 else f"{dec(e[s]['e'])} años"
              for s in sexos if e[s]["e"] is not None]
    stats = "".join(
        f'<div class="stat"><b>{n(e[s]["f"])}</b><span>{SEXO[s][1]} · puesto {n(e[s]["r"])}</span></div>' for s in sexos)
    stats += "".join(f'<div class="stat"><b>{dec(e[s]["e"])} años</b><span>edad media ({SEXO[s][1]})</span></div>'
                     for s in sexos if e[s]["e"] is not None)

    cuerpo = [f'<h1>¿Cuántas personas se llaman {escape(X)} en España?</h1>',
              f'<div class="respuesta"><p>Según el INE</p><p class="cifra">{cifra}</p><p>{respuesta}</p></div>',
              f'<div class="stats">{stats}</div>',
              f'<p class="updated">Datos del INE a {referencia}. Solo cuenta a las personas cuyo nombre completo es «{escape(X)}» (no incluye nombres compuestos que lo contienen).</p>']

    # Significado opcional, escrito a mano
    md = SIGNIFICADOS / f"{e['slug']}.md"
    if md.exists():
        parrafos = [p.strip() for p in md.read_text(encoding="utf-8").split("\n\n") if p.strip() and not p.startswith("#")]
        cuerpo.append(f'<h2>Significado y origen de {escape(X)}</h2>' + "".join(f"<p>{escape(p)}</p>" for p in parrafos))

    faq = [(f"¿Cuántas personas se llaman {X} en España?", re.sub("<[^>]+>", "", respuesta) + f" Datos del INE a {referencia}.")]
    if edades:
        faq.append((f"¿Qué edad media tienen las personas que se llaman {X}?",
                    f"La edad media de las personas que se llaman {X} en España es de {' y '.join(edades)}."))

    # Provincias
    if e["prov"]:
        filas = sorted(e["prov"], key=lambda p: (p["pos"], -p["f"]))
        tabla = "".join(f'<tr><td><a href="/provincia/{slug(PROVINCIAS[p["cod"]])}/">{PROVINCIAS[p["cod"]]}</a></td>'
                        + (f'<td>{SEXO[p["s"]][1].capitalize()}</td>' if len(sexos) == 2 else "")
                        + f'<td class="num">{p["pos"]}.º</td><td class="num">{n(p["f"])}</td></tr>' for p in filas)
        cuerpo.append(f'<h2>Provincias donde {escape(X)} está entre los 50 nombres más comunes</h2>'
                      f'<div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th>'
                      + ("<th>Sexo</th>" if len(sexos) == 2 else "") +
                      f'<th class="num">Puesto</th><th class="num">Personas</th></tr></thead><tbody>{tabla}</tbody></table></div>')
        mejores = ", ".join(f"{PROVINCIAS[p['cod']]} (puesto {p['pos']})" for p in filas[:3])
        faq.append((f"¿En qué provincias es más común el nombre {X}?",
                    f"{X} está entre los 50 nombres más frecuentes en {len({p['cod'] for p in filas})} provincias. "
                    f"Donde ocupa los primeros puestos es en {mejores}."))
    else:
        cuerpo.append(f'<h2>¿En qué provincias es más común?</h2><p>{escape(X)} no está entre los 50 nombres más frecuentes de ninguna provincia, '
                      f'que es el detalle que publica el INE por provincia. Consulta los <a href="/provincias/">nombres más comunes de cada provincia</a>.</p>')

    # Décadas
    if e["dec"]:
        cuerpo.append(f'<h2>{escape(X)} por década de nacimiento</h2><p>Personas que se llaman {escape(X)} según la década en que nacieron, '
                      f'cuando el nombre está entre los 50 más frecuentes de esa década.</p>')
        for s in sexos:
            filas_d = [(etiqueta_decada(c, d).capitalize(), e["dec"][c][s]["f"], f'{n(e["dec"][c][s]["f"])} · n.º {e["dec"][c][s]["pos"]}')
                       for c, d in decadas.items() if s in e["dec"].get(c, {})]
            if filas_d:
                fuera = len(decadas) - len(filas_d)
                cuerpo.append((f"<h3>{SEXO[s][1].capitalize()}</h3>" if len(sexos) == 2 else "") + barras(filas_d)
                              + (f'<p class="updated">En las otras {fuera} décadas no está entre los 50 nombres más frecuentes.</p>' if fuera else ""))
        mejor = max(((c, s, v) for c, ds in e["dec"].items() for s, v in ds.items()), key=lambda t: t[2]["f"])
        faq.append((f"¿En qué década fue más popular {X}?",
                    f"Entre las personas que viven hoy en España, la década con más {SEXO[mejor[1]][1]} llamados {X} es la de los nacidos "
                    f"{etiqueta_decada(mejor[0], decadas[mejor[0]]) if mejor[0] == 'antes-1930' else 'en los ' + etiqueta_decada(mejor[0], decadas[mejor[0]])}: "
                    f"{n(mejor[2]['f'])} personas, el puesto {mejor[2]['pos']} de esa década."))

    # Bebés
    if e["beb"]:
        anios = sorted(bebes)
        cuerpo.append(f'<h2>{escape(X)} entre los bebés</h2><p>Recién nacidos a los que se puso el nombre {escape(X)} cada año, '
                      f'cuando está entre los 100 más frecuentes de España.</p>')
        for s in sexos:
            filas_b = [(a, e["beb"][a][s]["f"], f'{n(e["beb"][a][s]["f"])} · n.º {e["beb"][a][s]["pos"]}')
                       for a in reversed(anios) if s in e["beb"].get(a, {})]
            if filas_b:
                fuera = len(anios) - len(filas_b)
                cuerpo.append((f"<h3>{SEXO[s][2].capitalize()}</h3>" if len(sexos) == 2 else "") + barras(filas_b)
                              + (f'<p class="updated">De {anios[0]} a {anios[-1]}, en los otros {fuera} años no estuvo entre los 100 nombres más puestos.</p>' if fuera else ""))
        ultimo = max(e["beb"])
        s_ult, v_ult = next((s, v) for s, v in e["beb"][ultimo].items())
        faq.append((f"¿Es {X} un nombre popular entre los bebés?",
                    f"Sí: en {ultimo} se registraron {n(v_ult['f'])} {SEXO[s_ult][2]} llamados {X} en España, el puesto {v_ult['pos']} "
                    f"entre los nombres de {SEXO[s_ult][2]} más puestos ese año."))

    # Similares
    variantes, cerca = similares(e, idx, por_total)
    if variantes:
        cuerpo.append(f'<h2>Nombres parecidos a {escape(X)}</h2><ul class="chips">' + "".join(
            f'<li><a href="/nombre/{v["slug"]}/">{escape(v["mostrar"])} <small>{n(v["total"])}</small></a></li>' for v in variantes) + "</ul>")
    if cerca:
        cuerpo.append(f'<h2>Nombres con una frecuencia parecida</h2><ul class="chips">' + "".join(
            f'<li><a href="/nombre/{v["slug"]}/">{escape(v["mostrar"])} <small>{n(v["total"])}</small></a></li>' for v in cerca) + "</ul>")

    # Preguntas frecuentes
    cuerpo.append('<div class="content"><h2>Preguntas frecuentes</h2>' + "".join(
        f"<details><summary>{escape(q)}</summary><p>{escape(r)}</p></details>" for q, r in faq) + "</div>")
    cuerpo.append(f'<p class="fuente">Fuente: Instituto Nacional de Estadística (INE), estadística de nombres y apellidos a partir de los Censos de población anuales, '
                  f'datos a {referencia}; y estadística de nacimientos. <a href="/sobre-los-datos/">Cómo se calculan estos datos</a>.</p>')

    total_txt = (f"{n(e['H']['f'])} hombres y {n(e['M']['f'])} mujeres" if len(sexos) == 2 else f"{n(e[sexos[0]]['f'])} {SEXO[sexos[0]][1]}")
    titulo = f"¿Cuántas personas se llaman {X} en España?"
    desc = f"En España hay {total_txt} que se llaman {X}, según el INE. Edad media, provincias, décadas y bebés con ese nombre."
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}]
    return pagina(f"/nombre/{e['slug']}/", titulo, desc, "\n".join(cuerpo), [(X, None)], ld)


# ------------------------------------------------------------------------------- Rankings e índices
def paginas_ranking(idx, nombres, provincias, decadas, bebes, ref_nombres, ref_prov, ref_dec):
    rutas = []
    # Provincias
    orden = sorted(provincias, key=lambda c: slug(PROVINCIAS[c]))
    for cod in orden:
        p, nombre = provincias[cod], PROVINCIAS[cod]
        ruta = f"/provincia/{slug(nombre)}/"
        cuerpo = (f"<h1>Nombres más comunes en {escape(nombre)}</h1>"
                  f'<p class="lead">Los 50 nombres de hombre y de mujer más frecuentes entre las personas que viven en {escape(nombre)}. '
                  f"El más común es {enlace(idx, p['H'][0][0])} entre los hombres ({n(p['H'][0][1])}) y {enlace(idx, p['M'][0][0])} entre las mujeres ({n(p['M'][0][1])}).</p>"
                  f'<p class="updated">Datos del INE a {fecha_larga(ref_prov)}, por provincia de residencia.</p>'
                  f'<div class="dos-col"><div><h2>Hombres</h2>{tabla_ranking(idx, p["H"], "H")}</div><div><h2>Mujeres</h2>{tabla_ranking(idx, p["M"], "M")}</div></div>'
                  f'<h2>Otras provincias</h2><ul class="columnas">' + "".join(
                      f'<li><a href="/provincia/{slug(PROVINCIAS[c])}/">{PROVINCIAS[c]}</a></li>' for c in orden if c != cod) + "</ul>")
        guardar(ruta, pagina(ruta, f"Nombres más comunes en {nombre}: los 50 más frecuentes",
                             f"Los 50 nombres de hombre y de mujer más frecuentes en {nombre} según el INE. El más común: {mostrar(p['H'][0][0])} y {mostrar(p['M'][0][0])}.",
                             cuerpo, [("Provincias", "/provincias/"), (nombre, None)]))
        rutas.append(ruta)
    cuerpo = ('<h1>Nombres más comunes por provincia</h1><p class="lead">Los tres nombres de hombre y de mujer más frecuentes de cada provincia. Elige una para ver sus 50 primeros.</p>'
              '<div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th><th>Hombres</th><th>Mujeres</th></tr></thead><tbody>'
              + "".join(f'<tr><td><a href="/provincia/{slug(PROVINCIAS[c])}/">{PROVINCIAS[c]}</a></td><td>{top3(idx, provincias[c]["H"])}</td>'
                        f'<td>{top3(idx, provincias[c]["M"])}</td></tr>' for c in orden) +
              f'</tbody></table></div><p class="updated">Datos del INE a {fecha_larga(ref_prov)}.</p>')
    guardar("/provincias/", pagina("/provincias/", "Nombres más comunes en cada provincia de España",
                                   "Los tres nombres más comunes de cada provincia y los 50 más frecuentes de hombre y de mujer, con datos del INE.",
                                   cuerpo, [("Provincias", None)]))
    rutas.append("/provincias/")

    # Décadas
    claves = list(decadas)
    for clave in claves:
        d = decadas[clave]
        ruta = f"/decada/{clave}/"
        titulo = titulo_decada(clave, d)
        nac = "antes de 1930" if clave == "antes-1930" else f"entre {d['desde']} y {d['hasta']}"
        cuerpo = (f"<h1>{escape(titulo)}</h1>"
                  f'<p class="lead">Los 50 nombres más frecuentes entre las personas nacidas {nac} que viven hoy en España. '
                  f"Encabezan la lista {enlace(idx, d['H'][0][0])} y {enlace(idx, d['M'][0][0])}.</p>"
                  f'<p class="updated">Datos del INE a {fecha_larga(ref_dec)}. Cuenta a quienes siguen viviendo en España en esa fecha.</p>'
                  f'<div class="dos-col"><div><h2>Hombres</h2>{tabla_ranking(idx, d["H"], "H")}</div><div><h2>Mujeres</h2>{tabla_ranking(idx, d["M"], "M")}</div></div>'
                  '<h2>Otras décadas</h2><ul class="chips">' + "".join(
                      f'<li><a href="/decada/{c}/">{etiqueta_decada(c, decadas[c]).capitalize()}</a></li>' for c in claves if c != clave) + "</ul>")
        guardar(ruta, pagina(ruta, titulo, f"{titulo} en España según el INE: los 50 más frecuentes de hombre y de mujer. "
                                           f"Encabezan {mostrar(d['H'][0][0])} y {mostrar(d['M'][0][0])}.",
                             cuerpo, [("Décadas", "/decadas/"), (etiqueta_decada(clave, d).capitalize(), None)]))
        rutas.append(ruta)
    # Nombres que encabezan alguna década, para contar el relevo generacional
    lideres = {s: [(c, decadas[c][s][0][0]) for c in claves] for s in "HM"}
    relevo = ""
    for s in "HM":
        cambios = [f"{enlace(idx, nom)} ({etiqueta_decada(c, decadas[c])})" for i, (c, nom) in enumerate(lideres[s]) if i == 0 or nom != lideres[s][i - 1][1]]
        relevo += f"<p><strong>{SEXO[s][1].capitalize()}:</strong> " + " → ".join(cambios) + ".</p>"
    cuerpo = ('<h1>Nombres más comunes por década de nacimiento</h1><p class="lead">Cómo han cambiado los nombres en España: los tres más frecuentes según la década en que nacieron las personas.</p>'
              '<div class="table-wrap"><table class="data"><thead><tr><th>Década</th><th>Hombres</th><th>Mujeres</th></tr></thead><tbody>'
              + "".join(f'<tr><td><a href="/decada/{c}/">{etiqueta_decada(c, decadas[c]).capitalize()}</a></td><td>{top3(idx, decadas[c]["H"])}</td>'
                        f'<td>{top3(idx, decadas[c]["M"])}</td></tr>' for c in claves) + "</tbody></table></div>"
              + f'<div class="content"><h2>El relevo de los nombres más comunes</h2><p>Qué nombre ha encabezado la lista en cada época, entre las personas que viven hoy en España:</p>{relevo}</div>')
    guardar("/decadas/", pagina("/decadas/", "Nombres más comunes por década en España",
                                "Los nombres más frecuentes de cada década de nacimiento, desde antes de 1930 hasta los años 2020, con datos del INE.",
                                cuerpo, [("Décadas", None)]))
    rutas.append("/decadas/")

    # Bebés
    anios = sorted(bebes, reverse=True)
    for anio in anios:
        z = bebes[anio]
        esp = z["espana"]
        ruta = f"/bebes/{anio}/"
        comunidades = "".join(
            f'<tr><td>{escape(v["nombre"].strip())}</td><td>{", ".join(enlace(idx, x) for x, _ in v["H"]["top"][:3])}</td>'
            f'<td>{", ".join(enlace(idx, x) for x, _ in v["M"]["top"][:3])}</td></tr>' for k, v in z.items() if k != "espana")
        cuerpo = (f"<h1>Nombres de bebé más puestos en {anio}</h1>"
                  f'<p class="lead">En {anio} nacieron en España {n(esp["H"]["total"])} niños y {n(esp["M"]["total"])} niñas. '
                  f"Los nombres más puestos fueron {enlace(idx, esp['H']['top'][0][0])} ({n(esp['H']['top'][0][1])} niños) y "
                  f"{enlace(idx, esp['M']['top'][0][0])} ({n(esp['M']['top'][0][1])} niñas).</p>"
                  f'<div class="dos-col"><div><h2>Niños</h2>{tabla_ranking(idx, esp["H"]["top"], "H")}</div><div><h2>Niñas</h2>{tabla_ranking(idx, esp["M"]["top"], "M")}</div></div>'
                  + (panel_movimientos(idx, bebes, anio, str(int(anio) - 1), f"Novedades respecto a {int(anio) - 1}")
                     if str(int(anio) - 1) in bebes else "")
                  + f'<h2>Los más puestos en cada comunidad autónoma</h2><div class="table-wrap"><table class="data"><thead><tr><th>Comunidad</th><th>Niños</th><th>Niñas</th></tr></thead><tbody>{comunidades}</tbody></table></div>'
                  '<h2>Otros años</h2><ul class="chips">' + "".join(f'<li><a href="/bebes/{a}/">{a}</a></li>' for a in anios if a != anio) + "</ul>"
                  '<p class="fuente">Fuente: INE, estadística de nacimientos (nombres de los recién nacidos). El INE publica los 100 nombres más puestos de España y los 10 más puestos de cada comunidad.</p>')
        guardar(ruta, pagina(ruta, f"Nombres de bebé más puestos en {anio} en España",
                             f"Los 100 nombres de niño y de niña más puestos en España en {anio} según el INE: {mostrar(esp['H']['top'][0][0])} y {mostrar(esp['M']['top'][0][0])}, los primeros.",
                             cuerpo, [("Bebés", "/bebes/"), (anio, None)]))
        rutas.append(ruta)
    ultimo, anterior = anios[0], anios[1] if len(anios) > 1 else None
    numero1 = ""
    for s, txt in (("H", "niños"), ("M", "niñas")):
        veces = {}
        for a in anios:
            veces.setdefault(bebes[a]["espana"][s]["top"][0][0], []).append(int(a))
        orden1 = sorted(veces.items(), key=lambda kv: (-len(kv[1]), -max(kv[1])))
        numero1 += f"<p><strong>{txt.capitalize()}:</strong> " + ", ".join(
            (f"{enlace(idx, nom)} ({len(a)} años seguidos, de {min(a)} a {max(a)})" if max(a) - min(a) + 1 == len(a)
             else f"{enlace(idx, nom)} ({len(a)} años entre {min(a)} y {max(a)})") if len(a) > 1 else f"{enlace(idx, nom)} (en {a[0]})"
            for nom, a in orden1) + ".</p>"
    novedades = ""
    if anterior:
        novedades = panel_movimientos(idx, bebes, ultimo, anterior, f"Qué ha cambiado en {ultimo}",
                                      f'<p><a href="/bebes/{ultimo}/">Ver los 100 nombres más puestos en {ultimo} →</a></p>')
    cuerpo = ('<h1>Nombres de bebé más puestos en España por año</h1><p class="lead">Los tres nombres de niño y de niña más puestos a los recién nacidos cada año desde '
              f'{anios[-1]}, según el INE.</p>{novedades}'
              '<div class="table-wrap"><table class="data"><thead><tr><th>Año</th><th>Niños</th><th>Niñas</th></tr></thead><tbody>'
              + "".join(f'<tr><td><a href="/bebes/{a}/">{a}</a></td><td>{top3(idx, bebes[a]["espana"]["H"]["top"])}</td>'
                        f'<td>{top3(idx, bebes[a]["espana"]["M"]["top"])}</td></tr>' for a in anios) + "</tbody></table></div>"
              + f'<div class="content"><h2>Los nombres que han sido número 1</h2><p>Cuántos años ha sido cada nombre el más puesto de España desde {anios[-1]}:</p>{numero1}</div>')
    guardar("/bebes/", pagina("/bebes/", "Nombres de bebé más puestos en España por año",
                              f"Los tres nombres más puestos a los bebés en España cada año desde {anios[-1]} hasta {anios[0]}, los que más suben y los que han sido número 1. Datos del INE.",
                              cuerpo, [("Bebés", None)]))
    rutas.append("/bebes/")
    return rutas


def portada(idx, nombres, bebes, referencia, n_paginas):
    ultimo = max(bebes)
    esp = bebes[ultimo]["espana"]
    top = nombres["top100"]
    lista = lambda l: "".join(f"<li>{enlace(idx, x)} <small>{n(f)}</small></li>" for x, f in l[:10])  # noqa: E731
    cuerpo = f"""
<section class="hero">
  <h1>¿Cuántas personas se llaman como tú?</h1>
  <p>Escribe un nombre o un apellido y descubre cuántas personas lo llevan en España, su edad media y dónde es más común. Datos oficiales del INE.</p>
  {formulario("nombre", referencia)}
</section>
<div class="grid">
  <a class="card" href="/apellidos/"><h3>Apellidos</h3><p>Cuántos se apellidan como tú y los apellidos más comunes de cada provincia.</p></a>
  <a class="card" href="/provincias/"><h3>Por provincia</h3><p>Los 50 nombres más comunes de cada provincia.</p></a>
  <a class="card" href="/decadas/"><h3>Por década</h3><p>De José y María a Hugo y Lucía: cómo han cambiado los nombres.</p></a>
  <a class="card" href="/bebes/"><h3>Nombres de bebé</h3><p>Los más puestos cada año desde {min(bebes)}. En {ultimo}: {escape(mostrar(esp['H']['top'][0][0]))} y {escape(mostrar(esp['M']['top'][0][0]))}.</p></a>
</div>
<div class="dos-col">
  <div class="content"><h2>Nombres de hombre más comunes</h2><ol>{lista(top['H'])}</ol></div>
  <div class="content"><h2>Nombres de mujer más comunes</h2><ol>{lista(top['M'])}</ol></div>
</div>
<div class="content">
  <h2>¿De dónde salen estos datos?</h2>
  <p>Del Instituto Nacional de Estadística (INE), que cada año publica cuántas personas residentes en España tienen cada nombre. Los datos actuales son a {fecha_larga(referencia)}. Por privacidad, el INE solo publica los nombres que llevan al menos 20 personas en toda España: si un nombre no aparece, hay menos de 20 personas que lo llevan. <a href="/sobre-los-datos/">Más sobre los datos</a>.</p>
</div>
<script src="/assets/app.js?v={VERSION}" defer></script>"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITIO, "url": DOMINIO + "/",
           "potentialAction": {"@type": "SearchAction", "target": DOMINIO + "/?q={search_term_string}",
                               "query-input": "required name=search_term_string"}}]
    return pagina("/", "¿Cuántas personas se llaman como tú? Nombres y apellidos",
                  "Descubre cuántas personas se llaman o se apellidan como tú en España, su edad media y en qué provincias es más común. Datos oficiales del INE.",
                  cuerpo, None, ld)


def paginas_legales(referencia, umbral):
    t = TITULAR
    sobre = f"""<h1>Sobre los datos</h1>
<div class="content">
<h2>De dónde salen</h2>
<p>Todos los datos proceden del <strong>Instituto Nacional de Estadística (INE)</strong>:</p>
<ul>
<li><strong>Nombres de la población:</strong> estadística de nombres y apellidos más frecuentes, elaborada a partir de los Censos de población anuales. Los datos actuales son a {fecha_larga(referencia)}. Incluye todos los nombres que llevan al menos 20 personas en España, con su edad media, los 50 más frecuentes de cada provincia de residencia y los 50 más frecuentes de cada década de nacimiento.</li>
<li><strong>Apellidos:</strong> todos los apellidos que llevan al menos 20 personas como primer apellido, con cuántas lo tienen como primero, como segundo y en ambos, y los 50 más frecuentes de cada provincia de residencia y de nacimiento.</li>
<li><strong>Nombres de los bebés:</strong> estadística de nacimientos, con los 100 nombres más puestos cada año en España y los 10 más puestos en cada comunidad autónoma.</li>
</ul>
<p>El INE actualiza estos datos una vez al año, normalmente en mayo. Esta web los descarga y regenera sus páginas automáticamente.</p>
<h2>El límite de 20 personas</h2>
<p>Para proteger la privacidad, el INE no publica los nombres que llevan menos de 20 personas en toda España, ni los que llevan menos de 5 en una provincia. Con los apellidos ocurre lo mismo: solo se publican los que llevan al menos 20 personas como primer apellido, y algunas cifras (como el segundo apellido de los apellidos poco frecuentes) aparecen como no publicadas. Por eso, si buscas un nombre muy poco común, verás el mensaje «menos de 20 personas»: el número exacto no se conoce y aquí nunca lo estimamos ni lo inventamos.</p>
<h2>Cómo se cuenta un nombre</h2>
<p>El INE cuenta el nombre completo tal y como figura en el padrón. «María José» y «María» son nombres distintos: una persona que se llama María José no cuenta como María. Los nombres se publican en mayúsculas y sin tildes; las tildes que ves en esta web las hemos añadido para facilitar la lectura y pueden no coincidir con cómo escribe su nombre cada persona.</p>
<h2>Qué nombres tienen página propia</h2>
<p>Tienen página propia los nombres que llevan al menos {n(umbral)} personas en España (y los apellidos que llevan al menos {n(UMBRAL_APELLIDOS_POR_DEFECTO)} personas como primer apellido) y los que aparecen en alguna tabla de ranking (por provincia, por década o de bebés). Cualquier otro nombre con datos se puede consultar en el buscador de la portada.</p>
<h2>Condiciones de uso de los datos</h2>
<p>Los datos del INE se reutilizan conforme a su aviso legal, citando la fuente. {SITIO} no está vinculada ni avalada por el INE.</p>
</div>"""
    aviso = f"""<h1>Aviso legal</h1><div class="content">
<h2>Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 (LSSI-CE), se informa de los datos del titular de este sitio web:</p>
<p>Titular: {t['nombre']}<br>NIF: {t['nif']}<br>Domicilio: {t['domicilio']}<br>Correo electrónico: {t['email']}<br>Sitio web: {DOMINIO}</p>
<h2>Objeto y condiciones de uso</h2>
<p>{SITIO} ofrece de forma gratuita información estadística sobre la frecuencia de los nombres en España a partir de datos públicos del INE. El acceso es libre y no requiere registro. Al usar el sitio te comprometes a hacerlo de forma lícita.</p>
<h2>Responsabilidad</h2>
<p>Los datos se muestran tal y como los publica el INE, con fines informativos. El titular no se hace responsable de posibles errores en los datos de origen ni del contenido de sitios externos enlazados.</p>
<h2>Propiedad intelectual</h2>
<p>El diseño, los textos y el código de este sitio son del titular. Los datos estadísticos son del INE y se reutilizan citando la fuente.</p>
<h2>Legislación aplicable</h2>
<p>Estas condiciones se rigen por la legislación española.</p></div>"""
    privacidad = f"""<h1>Política de privacidad</h1><div class="content">
<h2>Responsable</h2><p>{t['nombre']} ({t['email']}).</p>
<h2>Qué datos tratamos</h2>
<p>Esta web no tiene formularios ni registro, no instala cookies y no usa herramientas de analítica ni de publicidad. Los nombres que escribes en el buscador se buscan en tu propio navegador y no se envían ni se guardan en ningún servidor.</p>
<p>El proveedor de alojamiento (Cloudflare) puede registrar datos técnicos de la conexión, como la dirección IP, por motivos de seguridad y funcionamiento del servicio.</p>
<h2>Tus derechos</h2>
<p>Puedes ejercer tus derechos de acceso, rectificación, supresión y demás escribiendo a {t['email']}. También puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p>
<h2>Cambios</h2><p>Si en el futuro se añade publicidad o analítica, esta política se actualizará y se pedirá tu consentimiento cuando sea necesario.</p></div>"""
    guardar("/sobre-los-datos/", pagina("/sobre-los-datos/", "Sobre los datos: de dónde salen y el límite de 20 personas",
                                        "De dónde salen los datos de nombres (INE), cada cuánto se actualizan y por qué no se publican los nombres con menos de 20 personas.",
                                        sobre, [("Sobre los datos", None)]))
    guardar("/aviso-legal/", pagina("/aviso-legal/", f"Aviso legal | {SITIO}", "Aviso legal y datos del titular de cuantossellaman.es.", aviso, [("Aviso legal", None)]))
    guardar("/privacidad/", pagina("/privacidad/", f"Política de privacidad | {SITIO}", "Política de privacidad de cuantossellaman.es: sin cookies ni analítica.", privacidad, [("Privacidad", None)]))
    guardar("/404.html", pagina("/404.html", "Página no encontrada", "Esta página no existe.",
                                '<h1>Página no encontrada</h1><p>Prueba a buscar el nombre desde la <a href="/">portada</a>.</p>', indexable=False))
    return ["/sobre-los-datos/", "/aviso-legal/", "/privacidad/"]


def indices_busqueda(idx):
    grupos = {}
    for e in sorted(idx.values(), key=lambda x: -x["total"]):
        c = e["k"][:1]
        g = c if "a" <= c <= "z" else "otros"
        grupos.setdefault(g, []).append([e["k"], e["mostrar"],
                                         e["H"]["f"] if e["H"] else 0, e["M"]["f"] if e["M"] else 0,
                                         e["H"]["r"] if e["H"] else 0, e["M"]["r"] if e["M"] else 0,
                                         e["H"]["e"] if e["H"] else 0, e["M"]["e"] if e["M"] else 0,
                                         e["slug"] if e["pagina"] else ""])
    (WEB / "indice").mkdir(parents=True, exist_ok=True)
    for g, lista in grupos.items():
        (WEB / "indice" / f"{g}.json").write_text(json.dumps(lista, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return grupos


# ------------------------------------------------------------------------------------- Apellidos
def construir_indice_apellidos(apellidos, umbral):
    idx = {}
    for x in apellidos["lista"]:
        k = normalizar(x["n"])
        if k in idx:  # por si el INE repitiera una forma: nos quedamos con la primera (más frecuente)
            continue
        idx[k] = {"k": k, "mostrar": mostrar_apellido(x["n"]), "slug": slug(k), "r": x["r"],
                  "p1": x["p1"], "p2": x["p2"], "ambos": x["ambos"], "res": [], "nac": []}
    en_listas = {normalizar(a) for a, _ in apellidos["top100"]}
    for cod, p in apellidos["provincias"].items():
        for clave in ("res", "nac"):
            for pos, (a, f) in enumerate(p[clave], 1):
                k = normalizar(a)
                en_listas.add(k)
                if k in idx:
                    idx[k][clave].append({"cod": cod, "pos": pos, "f": f})
    for e in idx.values():
        e["pagina"] = e["p1"] >= umbral or e["k"] in en_listas
        e["total"] = (e["p1"] + e["p2"] - e["ambos"]) if e["p2"] is not None and e["ambos"] is not None else None
    return idx


def enlace_apellido(idx, ine, texto=None):
    e = idx.get(normalizar(ine))
    t = escape(texto or (e["mostrar"] if e else mostrar_apellido(ine)))
    return f'<a href="/apellido/{e["slug"]}/">{t}</a>' if e and e["pagina"] else t


def tabla_apellidos(idx, lista):
    filas = "".join(f'<tr><td class="num">{i}</td><td>{enlace_apellido(idx, a)}</td><td class="num">{n(f)}</td></tr>'
                    for i, (a, f) in enumerate(lista, 1))
    return ('<div class="table-wrap"><table class="data"><thead><tr><th class="num">#</th><th>Primer apellido</th>'
            f'<th class="num">Personas</th></tr></thead><tbody>{filas}</tbody></table></div>')


def formulario(tipo, referencia):
    marcado = lambda t: " checked" if t == tipo else ""  # noqa: E731
    texto = "Escribe un apellido, por ejemplo García" if tipo == "apellido" else "Escribe un nombre, por ejemplo Lucía"
    return f"""<form class="buscador" id="buscar" role="search" data-referencia="{fecha_larga(referencia)}" action="/" method="get">
    <input id="q" name="q" type="search" placeholder="{texto}" autocomplete="off" aria-label="Nombre o apellido" required>
    <button class="btn" type="submit">Buscar</button>
  </form>
  <div class="tipo-busqueda" role="radiogroup" aria-label="Qué quieres buscar">
    <label><input type="radio" name="tipo" value="nombre"{marcado("nombre")}> Nombre</label>
    <label><input type="radio" name="tipo" value="apellido"{marcado("apellido")}> Apellido</label>
  </div>
  <ul class="sugerencias" id="sugerencias" aria-live="polite"></ul>
  <div class="resultado" id="resultado" aria-live="polite"></div>"""


def pagina_apellido(e, idx, por_p1, referencia):
    X = e["mostrar"]
    ref = fecha_larga(referencia)
    p2 = f"{n(e['p2'])}" if e["p2"] is not None else None
    respuesta = (f"En España hay <strong>{n(e['p1'])} personas</strong> que tienen {escape(X)} como primer apellido"
                 + (f" y <strong>{p2}</strong> que lo tienen como segundo." if p2 else ". El INE no publica la cifra del segundo apellido.")
                 + (" Es el apellido más frecuente de España." if e["r"] == 1 else f" Es el apellido número {n(e['r'])} más frecuente."))
    stats = f'<div class="stat"><b>{n(e["p1"])}</b><span>como primer apellido · puesto {n(e["r"])}</span></div>'
    if p2:
        stats += f'<div class="stat"><b>{p2}</b><span>como segundo apellido</span></div>'
    if e["ambos"] is not None:
        stats += f'<div class="stat"><b>{n(e["ambos"])}</b><span>se apellidan {escape(X)} {escape(X)}</span></div>'
    if e["total"] is not None:
        stats += f'<div class="stat"><b>{n(e["total"])}</b><span>personas con el apellido (primero, segundo o ambos)</span></div>'
    cuerpo = [f"<h1>¿Cuántas personas se apellidan {escape(X)} en España?</h1>",
              f'<div class="respuesta"><p>Según el INE, como primer apellido</p><p class="cifra">{n(e["p1"])}</p><p>{respuesta}</p></div>',
              f'<div class="stats">{stats}</div>',
              f'<p class="updated">Datos del INE a {ref}. El INE publica los apellidos sin tildes; aquí las añadimos para facilitar la lectura.</p>']
    md = ORIGENES_APELLIDOS / f"{e['slug']}.md"
    if md.exists():
        parrafos = [p.strip() for p in md.read_text(encoding="utf-8").split("\n\n") if p.strip() and not p.startswith("#")]
        cuerpo.append(f"<h2>Origen del apellido {escape(X)}</h2>" + "".join(f"<p>{escape(p)}</p>" for p in parrafos))

    faq = [(f"¿Cuántas personas se apellidan {X} en España?", re.sub("<[^>]+>", "", respuesta) + f" Datos del INE a {ref}.")]
    if e["ambos"] is not None:
        faq.append((f"¿Cuántas personas se apellidan {X} {X}?",
                    f"{n(e['ambos'])} personas tienen {X} como primer y como segundo apellido en España."))
    for clave, titulo, verbo in (("res", "viven", "residencia"), ("nac", "nacieron", "nacimiento")):
        if not e[clave]:
            continue
        filas = sorted(e[clave], key=lambda p: (p["pos"], -p["f"]))
        tabla = "".join(f'<tr><td><a href="/apellidos/provincia/{slug(PROVINCIAS[p["cod"]])}/">{PROVINCIAS[p["cod"]]}</a></td>'
                        f'<td class="num">{p["pos"]}.º</td><td class="num">{n(p["f"])}</td></tr>' for p in filas)
        cuerpo.append(f"<h2>Provincias donde {escape(X)} está entre los 50 apellidos más comunes (por provincia de {verbo})</h2>"
                      f'<div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th><th class="num">Puesto</th>'
                      f'<th class="num">Personas</th></tr></thead><tbody>{tabla}</tbody></table></div>')
        if clave == "res":
            mejores = ", ".join(f"{PROVINCIAS[p['cod']]} (puesto {p['pos']})" for p in filas[:3])
            faq.append((f"¿Dónde es más común el apellido {X}?",
                        f"{X} está entre los 50 primeros apellidos más frecuentes en {len(filas)} provincias. Donde ocupa los primeros puestos es en {mejores}."))
    if not e["res"] and not e["nac"]:
        cuerpo.append(f'<h2>¿Dónde es más común?</h2><p>{escape(X)} no está entre los 50 apellidos más frecuentes de ninguna provincia, '
                      f'que es el detalle que publica el INE por provincia. Consulta los <a href="/apellidos/">apellidos más comunes de cada provincia</a>.</p>')

    raiz = e["k"].split()[0][:4]
    variantes = [x for x in por_p1 if x is not e and x["pagina"] and x["k"].split()[0][:4] == raiz][:8]
    pos = por_p1.index(e)
    cerca = [x for x in por_p1[max(0, pos - 6):pos + 7] if x is not e and x["pagina"] and x not in variantes][:8]
    if variantes:
        cuerpo.append(f"<h2>Apellidos parecidos a {escape(X)}</h2><ul class=\"chips\">" + "".join(
            f'<li><a href="/apellido/{v["slug"]}/">{escape(v["mostrar"])} <small>{n(v["p1"])}</small></a></li>' for v in variantes) + "</ul>")
    if cerca:
        cuerpo.append('<h2>Apellidos con una frecuencia parecida</h2><ul class="chips">' + "".join(
            f'<li><a href="/apellido/{v["slug"]}/">{escape(v["mostrar"])} <small>{n(v["p1"])}</small></a></li>' for v in cerca) + "</ul>")
    cuerpo.append('<div class="content"><h2>Preguntas frecuentes</h2>' + "".join(
        f"<details><summary>{escape(q)}</summary><p>{escape(r)}</p></details>" for q, r in faq) + "</div>")
    cuerpo.append(f'<p class="fuente">Fuente: Instituto Nacional de Estadística (INE), estadística de apellidos a partir de los Censos de población anuales, '
                  f'datos a {ref}. <a href="/sobre-los-datos/">Cómo se calculan estos datos</a>.</p>')
    titulo = f"¿Cuántas personas se apellidan {X} en España?"
    desc = (f"{n(e['p1'])} personas tienen {X} como primer apellido en España" + (f" y {p2} como segundo" if p2 else "")
            + ", según el INE. Puesto, provincias donde es más común y cuántos se apellidan " + f"{X} {X}.")
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}]
    return pagina(f"/apellido/{e['slug']}/", titulo, desc, "\n".join(cuerpo), [("Apellidos", "/apellidos/"), (X, None)], ld)


def paginas_apellidos(idx, apellidos):
    ref = apellidos["referencia"]
    provincias = apellidos["provincias"]
    orden = sorted(provincias, key=lambda c: slug(PROVINCIAS[c]))
    rutas = []
    for cod in orden:
        nombre, p = PROVINCIAS[cod], provincias[cod]
        ruta = f"/apellidos/provincia/{slug(nombre)}/"
        cuerpo = (f"<h1>Apellidos más comunes en {escape(nombre)}</h1>"
                  f'<p class="lead">Los 50 primeros apellidos más frecuentes entre las personas que viven en {escape(nombre)} y entre las nacidas allí. '
                  f"El más común es {enlace_apellido(idx, p['res'][0][0])}, con {n(p['res'][0][1])} personas.</p>"
                  f'<p class="updated">Datos del INE a {fecha_larga(ref)}.</p>'
                  f'<div class="dos-col"><div><h2>Por provincia de residencia</h2>{tabla_apellidos(idx, p["res"])}</div>'
                  f'<div><h2>Por provincia de nacimiento</h2>{tabla_apellidos(idx, p["nac"])}</div></div>'
                  f'<p>Consulta también los <a href="/provincia/{slug(nombre)}/">nombres más comunes en {escape(nombre)}</a>.</p>'
                  '<h2>Otras provincias</h2><ul class="columnas">' + "".join(
                      f'<li><a href="/apellidos/provincia/{slug(PROVINCIAS[c])}/">{PROVINCIAS[c]}</a></li>' for c in orden if c != cod) + "</ul>")
        guardar(ruta, pagina(ruta, f"Apellidos más comunes en {nombre}: los 50 más frecuentes",
                             f"Los 50 apellidos más frecuentes en {nombre} según el INE, por provincia de residencia y de nacimiento. El más común: {mostrar_apellido(p['res'][0][0])}.",
                             cuerpo, [("Apellidos", "/apellidos/"), (nombre, None)]))
        rutas.append(ruta)
    cuerpo = ("<h1>¿Cuántas personas se apellidan como tú?</h1>"
              '<p class="lead">Busca un apellido y descubre cuántas personas lo llevan en España como primer y como segundo apellido, y dónde es más común.</p>'
              f'<section class="hero" style="padding-top:8px">{formulario("apellido", ref)}</section>'
              f'<script src="/assets/app.js?v={VERSION}" defer></script>'
              f'<div class="dos-col"><div><h2>Los 100 apellidos más comunes de España</h2>{tabla_apellidos(idx, apellidos["top100"])}</div>'
              '<div><h2>El apellido más común de cada provincia</h2><div class="table-wrap"><table class="data"><thead><tr><th>Provincia</th><th>Apellido</th></tr></thead><tbody>'
              + "".join(f'<tr><td><a href="/apellidos/provincia/{slug(PROVINCIAS[c])}/">{PROVINCIAS[c]}</a></td>'
                        f'<td>{enlace_apellido(idx, provincias[c]["res"][0][0])}</td></tr>' for c in orden)
              + f'</tbody></table></div></div></div><p class="fuente">Fuente: INE, estadística de apellidos a partir de los Censos de población anuales, datos a {fecha_larga(ref)}. '
              'Solo se publican los apellidos que llevan al menos 20 personas como primer apellido.</p>')
    guardar("/apellidos/", pagina("/apellidos/", "Apellidos en España: cuántas personas se apellidan como tú",
                                  "Busca un apellido y descubre cuántas personas lo llevan en España, los 100 más comunes y el apellido más frecuente de cada provincia. Datos del INE.",
                                  cuerpo, [("Apellidos", None)]))
    rutas.append("/apellidos/")
    return rutas


def indices_apellidos(idx):
    grupos = {}
    for e in sorted(idx.values(), key=lambda x: -x["p1"]):
        c = e["k"][:1]
        g = c if "a" <= c <= "z" else "otros"
        grupos.setdefault(g, []).append([e["k"], e["mostrar"], e["p1"], e["p2"] or 0, e["ambos"] or 0, e["r"],
                                         e["slug"] if e["pagina"] else ""])
    (WEB / "indice-apellidos").mkdir(parents=True, exist_ok=True)
    for g, lista in grupos.items():
        (WEB / "indice-apellidos" / f"{g}.json").write_text(json.dumps(lista, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return grupos


VERSION = "4"


def main():
    parser = argparse.ArgumentParser(description="Genera la web de cuantossellaman.es")
    parser.add_argument("--umbral-apellidos", type=int, default=UMBRAL_APELLIDOS_POR_DEFECTO,
                        help=f"personas con ese primer apellido para que tenga página propia (por defecto {UMBRAL_APELLIDOS_POR_DEFECTO})")
    parser.add_argument("--umbral", type=int, default=UMBRAL_POR_DEFECTO,
                        help=f"personas mínimas para que un nombre tenga página propia (por defecto {UMBRAL_POR_DEFECTO})")
    args = parser.parse_args()

    nombres, prov, dec, beb, ape = cargar()
    idx = construir_indice(nombres, prov["provincias"], dec["decadas"], beb["anios"], args.umbral)
    con_pagina = [e for e in idx.values() if e["pagina"]]
    if len(con_pagina) < MIN_PAGINAS:
        sys.exit(f"ERROR: solo {len(con_pagina)} nombres tienen página (mínimo {MIN_PAGINAS}). No se publica.")

    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    shutil.copy(PLANTILLA / "style.css", WEB / "assets" / "style.css")
    shutil.copy(PLANTILLA / "app.js", WEB / "assets" / "app.js")
    for icono in ("favicon.svg", "favicon.ico", "favicon-48.png", "favicon-96.png", "favicon-192.png", "apple-touch-icon.png"):
        shutil.copy(PLANTILLA / icono, WEB / icono)

    por_total = sorted(idx.values(), key=lambda x: -x["total"])
    for e in con_pagina:
        guardar(f"/nombre/{e['slug']}/", pagina_nombre(e, idx, por_total, nombres["referencia"], prov["provincias"], dec["decadas"], beb["anios"]))
    rutas = paginas_ranking(idx, nombres, prov["provincias"], dec["decadas"], beb["anios"],
                            nombres["referencia"], prov["referencia"], dec["referencia"])
    rutas += paginas_legales(nombres["referencia"], args.umbral)
    idx_ape = construir_indice_apellidos(ape, args.umbral_apellidos)
    ape_pagina = [e for e in idx_ape.values() if e["pagina"]]
    if len(ape_pagina) < MIN_PAGINAS:
        sys.exit(f"ERROR: solo {len(ape_pagina)} apellidos tienen página (mínimo {MIN_PAGINAS}). No se publica.")
    por_p1 = sorted(idx_ape.values(), key=lambda x: -x["p1"])
    for e in ape_pagina:
        guardar(f"/apellido/{e['slug']}/", pagina_apellido(e, idx_ape, por_p1, ape["referencia"]))
    rutas += paginas_apellidos(idx_ape, ape)
    indices_apellidos(idx_ape)
    guardar("/", portada(idx, nombres, beb["anios"], nombres["referencia"], len(con_pagina)))
    grupos = indices_busqueda(idx)

    hoy = date.today().isoformat()
    urls = (["/"] + rutas + [f"/nombre/{e['slug']}/" for e in sorted(con_pagina, key=lambda x: x["slug"])]
            + [f"/apellido/{e['slug']}/" for e in sorted(ape_pagina, key=lambda x: x["slug"])])
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"  <url><loc>{DOMINIO}{u}</loc><lastmod>{hoy}</lastmod></url>\n" for u in urls) + "</urlset>\n",
                                     encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /indice/\nDisallow: /indice-apellidos/\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    print(f"Web generada: {len(con_pagina)} páginas de nombre (umbral {args.umbral}), "
          f"{len(ape_pagina)} de apellido (umbral {args.umbral_apellidos}), {len(rutas)} páginas más, "
          f"{len(idx)} nombres en el buscador ({len(grupos)} ficheros de índice). Datos a {nombres['referencia']}.")


if __name__ == "__main__":
    main()
