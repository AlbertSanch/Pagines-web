"""Artículos de «¿Cuántos se llaman?» (/articulos/): textos largos escritos a partir de los datos del INE.

Cada artículo explica una tendencia (los nombres de bebé que suben, cómo han cambiado los nombres por
décadas, los apellidos más comunes…) con las cifras calculadas en el momento de generar la web, así que
se actualizan solas cuando el INE publica datos nuevos. Solo usan datos del INE: no hay significados,
orígenes ni opiniones sobre los nombres.

Lo llama generar_web.main(), que le pasa su propio módulo (g) para reutilizar la plantilla y los enlaces.
"""
from html import escape

from tildes import mostrar, mostrar_apellido, normalizar

RAIZ_RUTA = "/articulos/"


def _tabla(cab, filas, num_desde=1):
    cl = lambda i: ' class="num"' if i >= num_desde else ""  # noqa: E731
    th = "".join(f"<th{cl(i)}>{h}</th>" for i, h in enumerate(cab))
    tr = "".join("<tr>" + "".join(f"<td{cl(i)}>{v}</td>" for i, v in enumerate(f)) + "</tr>" for f in filas)
    return f'<div class="table-wrap"><table class="data"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def _pct(x, d=1):
    return f"{x * 100:.{d}f}".replace(".", ",") + " %"


def _lista_y(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def _rachas(serie):
    """[(nombre, desde, hasta), …] de una lista ordenada [(año, nombre), …]."""
    out = []
    for a, nom in serie:
        if out and out[-1][0] == nom:
            out[-1][2] = a
        else:
            out.append([nom, a, a])
    return out


# ------------------------------------------------------------------ 1. Nombres de bebé que suben y bajan
def art_bebes_suben(g, idx, bebes):
    anios = sorted(bebes)
    ult = anios[-1]
    base = str(int(ult) - 5) if str(int(ult) - 5) in bebes else anios[0]
    primero = anios[0]
    en = lambda nom: g.enlace(idx, nom)  # noqa: E731
    secciones, resumen = "", []
    for s in "MH":
        r_ult = {nom: i + 1 for i, (nom, _) in enumerate(bebes[ult]["espana"][s]["top"])}
        r_base = {nom: i + 1 for i, (nom, _) in enumerate(bebes[base]["espana"][s]["top"])}
        f_ult = dict(bebes[ult]["espana"][s]["top"])
        sube = sorted((k for k in r_ult if k in r_base and r_base[k] > r_ult[k]), key=lambda k: r_ult[k] - r_base[k])[:10]
        baja = sorted((k for k in r_ult if k in r_base and r_ult[k] > r_base[k]), key=lambda k: r_base[k] - r_ult[k])[:10]
        nuevos = sorted((k for k in r_ult if k not in r_base), key=lambda k: r_ult[k])
        salen = sorted((k for k in r_base if k not in r_ult), key=lambda k: r_base[k])
        nino, a_los = {"H": ("niño", "a los niños"), "M": ("niña", "a las niñas")}[s]
        resumen.append((s, sube[:3]))
        secciones += (
            f'<h2>Los nombres de {nino} que más suben</h2>'
            f'<p>Puesto entre los 100 nombres más puestos {a_los} en {base} y en {ult}, ordenados por los puestos que han ganado.</p>'
            + _tabla(["Nombre", f"Puesto en {base}", f"Puesto en {ult}", "Puestos ganados", f"Bebés en {ult}"],
                     [[en(k), f"{r_base[k]}.º", f"{r_ult[k]}.º", f"+{r_base[k] - r_ult[k]}", g.n(f_ult[k])] for k in sube])
            + f'<h2>Los nombres de {nino} que más bajan</h2>'
            + _tabla(["Nombre", f"Puesto en {base}", f"Puesto en {ult}", "Puestos perdidos"],
                     [[en(k), f"{r_base[k]}.º", f"{r_ult[k]}.º", f"−{r_ult[k] - r_base[k]}"] for k in baja])
            + (f'<p><strong>Nuevos en el top 100 de {ult}</strong> (no estaban en {base}): {_lista_y(en(k) for k in nuevos)}.</p>' if nuevos else "")
            + (f'<p><strong>Han salido del top 100</strong>: {_lista_y(en(k) for k in salen)}.</p>' if salen else "")
        )

    # Número 1 de cada año
    rachas = {s: _rachas([(a, bebes[a]["espana"][s]["top"][0][0]) for a in anios]) for s in "HM"}
    filas_1 = []
    for s in "MH":
        for nom, d, h in rachas[s]:
            filas_1.append([g.SEXO[s][2].capitalize(), en(nom), d if d == h else f"{d}–{h}", str(int(h) - int(d) + 1)])
    larga = max(((s, r) for s in "HM" for r in rachas[s]), key=lambda t: int(t[1][2]) - int(t[1][1]))
    larga_txt = (f"La racha más larga es la de {en(larga[1][0])}: número 1 de las {g.SEXO[larga[0]][2]} "
                 f"{int(larga[1][2]) - int(larga[1][1]) + 1} años seguidos, de {larga[1][1]} a {larga[1][2]}.")

    # Cada vez más variedad
    conc = []
    for s in "MH":
        for a in (primero, ult):
            t = bebes[a]["espana"][s]
            conc.append((s, a, sum(f for _, f in t["top"][:10]) / t["total"], sum(f for _, f in t["top"]) / t["total"], t["total"]))
    filas_c = [[g.SEXO[s][2].capitalize(), a, g.n(tot), _pct(t10), _pct(t100)] for s, a, t10, t100, tot in conc]
    m10 = {(s, a): t10 for s, a, t10, _, _ in conc}

    ultimos_1 = {s: bebes[ult]["espana"][s]["top"][0][0] for s in "HM"}
    cuerpo = (
        f'<h1>Los nombres de bebé que más suben y más bajan en España</h1>'
        f'<p class="lead">¿Qué nombres se ponen cada vez más y cuáles se están quedando atrás? Comparamos los 100 nombres más puestos a los recién nacidos '
        f'en {base} y en {ult}: entre las niñas suben con fuerza {_lista_y(en(k) for k in resumen[0][1])}, y entre los niños, {_lista_y(en(k) for k in resumen[1][1])}.</p>'
        f'<p class="updated">Datos del INE: nombres de los nacidos en España de {primero} a {ult}.</p>'
        + g.bloque_compartir(f"Los nombres de bebé que más suben en España: {', '.join(mostrar(k) for k in resumen[0][1])}…", RAIZ_RUTA + "nombres-de-bebe-que-mas-suben/")
        + '<div class="content">'
        + secciones
        + f'<h2>El número 1 de cada año desde {primero}</h2>'
        f'<p>En {ult}, los nombres más puestos fueron {en(ultimos_1["M"])} para las niñas y {en(ultimos_1["H"])} para los niños. {larga_txt}</p>'
        + _tabla(["", "Nombre", "Años", "Años como n.º 1"], filas_1, num_desde=3)
        + '<h2>Cada vez más variedad de nombres</h2>'
        f'<p>Los nombres de moda pesan cada vez menos. En {primero}, los 10 nombres más puestos a las niñas se los llevaban el {_pct(m10[("M", primero)], 0)} '
        f'de las recién nacidas; en {ult}, solo el {_pct(m10[("M", ult)], 0)}. Con los niños pasa lo mismo: del {_pct(m10[("H", primero)], 0)} al {_pct(m10[("H", ult)], 0)}. '
        'Es decir, los padres eligen entre muchos más nombres que hace veinte años, y cada vez es más raro que en una clase coincidan varios niños con el mismo nombre.</p>'
        + _tabla(["", "Año", "Bebés", "Con uno de los 10 más puestos", "Con uno de los 100 más puestos"], filas_c, num_desde=2)
        + f'<p>La tabla también muestra otra cosa: cada vez nacen menos bebés. Puedes ver la lista completa de cada año en <a href="/bebes/">nombres de bebé</a>, '
        'buscar ideas en <a href="/ideas/">ideas para bebé</a> o mirar los <a href="/articulos/nombres-de-bebe-por-comunidad/">nombres más puestos en cada comunidad</a>.</p>'
        '<h2>Cómo están hechos estos datos</h2>'
        '<p>El INE publica cada año los 100 nombres más puestos a los niños y a las niñas nacidos en España, con el número de bebés de cada uno. '
        'Comparamos el puesto de cada nombre entre dos años; los que no estaban en el top 100 en alguno de los dos aparecen como nuevos o como salidas.</p>'
        '</div>'
    )
    desc = f"Los nombres de niña y de niño que más puestos ganan y pierden entre {base} y {ult}, el número 1 de cada año desde {primero} y por qué hay cada vez más variedad. Datos del INE."
    return "nombres-de-bebe-que-mas-suben", f"Los nombres de bebé que más suben y más bajan ({base}–{ult})", desc, cuerpo, \
        "Los nombres de bebé que más suben y más bajan", "Qué nombres se ponen cada vez más y cuáles se quedan atrás."


# ------------------------------------------------------------------ 2. Cómo han cambiado los nombres por décadas
def art_decadas(g, idx, decadas, referencia):
    en = lambda nom: g.enlace(idx, nom)  # noqa: E731
    claves = list(decadas)
    filas, stats = [], []
    for c in claves:
        d = decadas[c]
        et = g.etiqueta_decada(c, d)
        filas.append([f'<a href="/decada/{c}/">{escape(et.capitalize())}</a>'] + [_lista_y(en(nom) for nom, _ in d[s][:3]) for s in "MH"])
        comp = {s: sum(1 for nom, _ in d[s] if " " in nom) for s in "HM"}
        largo = {s: sum(len(nom.replace(" ", "")) for nom, _ in d[s][:20]) / 20 for s in "HM"}
        stats.append((c, et, comp, largo))
    pico = max(stats, key=lambda t: t[2]["M"])
    ultimo = stats[-1]
    filas_s = [[escape(et.capitalize()), str(comp["M"]), str(comp["H"]), g.dec(largo["M"]), g.dec(largo["H"])] for c, et, comp, largo in stats]
    sin_comp = [et for c, et, comp, _ in stats if comp["M"] == 0 and comp["H"] == 0]
    primera = stats[0]
    cuerpo = (
        '<h1>Cómo han cambiado los nombres en España, década a década</h1>'
        f'<p class="lead">De José y María Carmen a Mateo y Lucía: los nombres de las personas que viven hoy en España cuentan casi un siglo de modas. '
        'Hemos repasado los nombres más comunes según la década de nacimiento y hay dos cambios que saltan a la vista: '
        'los nombres compuestos han desaparecido y los nombres son cada vez más cortos.</p>'
        f'<p class="updated">Datos del INE a {g.fecha_larga(referencia)}: nombres más comunes de las personas que viven en España, según su década de nacimiento.</p>'
        + g.bloque_compartir("Cómo han cambiado los nombres en España, década a década:", RAIZ_RUTA + "como-han-cambiado-los-nombres/")
        + '<div class="content">'
        '<h2>Los tres nombres más comunes de cada década</h2>'
        + _tabla(["Nacidos en", "Mujeres", "Hombres"], filas, num_desde=9)
        + '<p>Ojo: son los nombres de las personas que <em>viven hoy</em> en España, no exactamente los que se pusieron en cada época. '
        'En las décadas más antiguas faltan quienes ya han fallecido o emigraron, y en las recientes cuentan también quienes llegaron de otros países.</p>'
        '<h2>El fin de los nombres compuestos</h2>'
        f'<p>Entre las mujeres nacidas en los {escape(pico[1])}, {pico[2]["M"]} de los 50 nombres más comunes eran compuestos: María Carmen, Ana María, María Pilar, María Dolores… '
        + (f'Entre las nacidas en los {escape(ultimo[1])} {"no hay ninguno" if ultimo[2]["M"] == 0 else "solo hay " + str(ultimo[2]["M"])}. ' if ultimo[2]["M"] < pico[2]["M"] else "")
        + (f'Desde los {escape(sin_comp[0])}, ninguno de los 50 nombres más comunes, ni de hombre ni de mujer, es compuesto.' if sin_comp else "")
        + '</p>'
        '<h2>Nombres cada vez más cortos</h2>'
        f'<p>Contando las letras de los 20 nombres más comunes de cada década, los de mujer han pasado de {g.dec(max(s[3]["M"] for s in stats))} letras de media en la década '
        f'con nombres más largos a {g.dec(ultimo[3]["M"])} entre las nacidas en los {escape(ultimo[1])}. Nombres cortos y simples como Lucía, Sofía, Hugo, Leo o Mateo han sustituido a los compuestos.</p>'
        + _tabla(["Nacidos en", "Compuestos entre los 50 de mujer", "Compuestos entre los 50 de hombre", "Letras (mujer)", "Letras (hombre)"], filas_s)
        + '<p class="note">«Letras» es la media de letras de los 20 nombres más comunes de esa década, sin contar los espacios.</p>'
        '<h2>Sigue explorando</h2>'
        '<p>Cada década tiene su página con los 50 nombres más comunes: <a href="/decadas/">nombres por década</a>. '
        'Si quieres saber si tu nombre estaba de moda cuando naciste, prueba <a href="/tu-nombre-el-ano-que-naciste/">tu nombre el año que naciste</a>, '
        'y para los nombres que ya casi no se ponen, los <a href="/nombres-en-peligro-de-extincion/">nombres en peligro de extinción</a>.</p>'
        '</div>'
    )
    desc = "Los nombres más comunes de cada década desde antes de 1930, el fin de los nombres compuestos y por qué los nombres son cada vez más cortos. Con datos del INE."
    return "como-han-cambiado-los-nombres", "Cómo han cambiado los nombres en España, década a década", desc, cuerpo, \
        "Cómo han cambiado los nombres, década a década", "De José y María Carmen a Mateo y Lucía."


# ------------------------------------------------------------------ 3. Apellidos más comunes
def art_apellidos(g, idx_ape, apellidos):
    lista = apellidos["lista"]
    total = sum(x["p1"] for x in lista)
    ea = lambda nom: g.enlace_apellido(idx_ape, nom)  # noqa: E731
    top = lista[:20]
    filas = [[str(x["r"]), ea(x["n"]), g.n(x["p1"]), _pct(x["p1"] / total, 2), g.n(x["ambos"]) if x["ambos"] else "—"] for x in top]
    top10 = sum(x["p1"] for x in lista[:10]) / total
    top100 = sum(x["p1"] for x in lista[:100]) / total
    dobles = sorted((x for x in lista if x["ambos"]), key=lambda x: -x["ambos"])[:10]
    filas_d = [[f"{ea(x['n'])} {escape(mostrar_apellido(x['n']))}", g.n(x["ambos"])] for x in dobles]
    provs = apellidos["provincias"]
    primero = lista[0]["n"]
    distintas = sorted(((cod, p["res"][0][0]) for cod, p in provs.items() if normalizar(p["res"][0][0]) != normalizar(primero)),
                       key=lambda t: g.PROVINCIAS[t[0]])
    gana = len(provs) - len(distintas)
    por_ape = {}
    for cod, a in distintas:
        por_ape.setdefault(a, []).append(g.PROVINCIAS[cod])
    filas_p = [[ea(a), _lista_y(escape(p) for p in ps)] for a, ps in sorted(por_ape.items(), key=lambda t: -len(t[1]))]
    g_ = lista[0]
    cuerpo = (
        '<h1>Los apellidos más comunes de España</h1>'
        f'<p class="lead">{escape(mostrar_apellido(primero))} es el apellido más común de España: lo llevan como primer apellido {g.n(g_["p1"])} personas, '
        f'y {g.n(g_["ambos"])} se apellidan {escape(mostrar_apellido(primero))} {escape(mostrar_apellido(primero))}. Repasamos los 20 más frecuentes, los dobles apellidos más repetidos '
        'y en qué provincias el más común es otro.</p>'
        f'<p class="updated">Datos del INE a {g.fecha_larga(apellidos["referencia"])}: personas que viven en España, según su primer apellido.</p>'
        + g.bloque_compartir(f"{mostrar_apellido(primero)} es el apellido más común de España: {g.n(g_['p1'])} personas lo llevan como primer apellido.",
                             RAIZ_RUTA + "apellidos-mas-comunes-de-espana/")
        + '<div class="content">'
        '<h2>Los 20 apellidos más comunes</h2>'
        + _tabla(["#", "Apellido", "Primer apellido", "% del total", "Con los dos iguales"], filas, num_desde=2)
        + f'<p>«% del total» es la parte de todas las personas con un primer apellido publicado por el INE. Solo los 10 primeros los llevan el {_pct(top10, 0)} de las personas, '
        f'y los 100 más comunes, el {_pct(top100, 0)}.</p>'
        '<h2>Los dobles apellidos más repetidos</h2>'
        '<p>Personas que tienen el mismo apellido como primero y como segundo:</p>'
        + _tabla(["Apellidos", "Personas"], filas_d)
        + f'<h2>Las provincias donde no gana {escape(mostrar_apellido(primero))}</h2>'
        f'<p>{escape(mostrar_apellido(primero))} es el primer apellido más común en {gana} de las {len(provs)} provincias y ciudades autónomas. En el resto gana otro:</p>'
        + _tabla(["Apellido más común", "Provincias"], filas_p, num_desde=9)
        + '<p>Puedes ver los 50 apellidos más comunes de cada provincia, con su mapa, en <a href="/apellidos/">apellidos</a>, '
        'buscar el tuyo letra a letra en <a href="/apellidos/a/">apellidos de la A a la Z</a> o calcular '
        '<a href="/cuantos-se-llaman-como-tu/">cuántas personas tienen tu nombre y tus dos apellidos</a>.</p>'
        '<h2>Cómo están hechos estos datos</h2>'
        '<p>El INE publica cuántas personas tienen cada apellido como primero, como segundo y en los dos, siempre que lo lleven al menos 20 personas. '
        'Las cifras por provincia son de las personas que viven en cada provincia, según su primer apellido.</p>'
        '</div>'
    )
    desc = f"Los 20 apellidos más comunes de España, los dobles apellidos más repetidos ({mostrar_apellido(primero)} {mostrar_apellido(primero)}…) y las provincias donde gana otro apellido. Datos del INE."
    return "apellidos-mas-comunes-de-espana", "Los apellidos más comunes de España (y de cada provincia)", desc, cuerpo, \
        "Los apellidos más comunes de España", "Los 20 más frecuentes, los dobles apellidos y las provincias donde gana otro."


# ------------------------------------------------------------------ 4. Nombres más jóvenes y más mayores
def art_edades(g, idx, nombres, referencia, minimo=20000):
    en = lambda nom: g.enlace(idx, nom)  # noqa: E731
    secciones, ejemplos = "", {}
    for s in "MH":
        L = [x for x in nombres[s] if x["f"] >= minimo and x["e"] is not None and " " not in x["n"]]
        jov = sorted(L, key=lambda x: x["e"])[:12]
        may = sorted(L, key=lambda x: -x["e"])[:12]
        ejemplos[s] = (jov[:3], may[:3])
        pl = g.SEXO[s][1]
        secciones += (
            f'<h2>Los nombres de {g.SEXO[s][0]} más jóvenes</h2>'
            + _tabla(["Nombre", pl.capitalize(), "Edad media"], [[en(x["n"]), g.n(x["f"]), f"{g.dec(x['e'])} años"] for x in jov])
            + f'<h2>Los nombres de {g.SEXO[s][0]} más mayores</h2>'
            + _tabla(["Nombre", pl.capitalize(), "Edad media"], [[en(x["n"]), g.n(x["f"]), f"{g.dec(x['e'])} años"] for x in may])
        )
    comunes = {s: nombres[s][0] for s in "HM"}
    cuerpo = (
        '<h1>Los nombres más jóvenes y más mayores de España</h1>'
        f'<p class="lead">Dime cómo te llamas y te diré qué edad tienes. Las mujeres que se llaman {_lista_y(en(x["n"]) for x in ejemplos["M"][0])} tienen de media '
        f'menos de {int(max(x["e"] for x in ejemplos["M"][0])) + 1} años; las que se llaman {_lista_y(en(x["n"]) for x in ejemplos["M"][1])}, más de {int(min(x["e"] for x in ejemplos["M"][1]))}. '
        'Estos son los nombres con la edad media más baja y más alta de España.</p>'
        f'<p class="updated">Datos del INE a {g.fecha_larga(referencia)}: edad media de las personas que viven en España con cada nombre. Solo nombres simples que llevan al menos {g.n(minimo)} personas.</p>'
        + g.bloque_compartir("Los nombres más jóvenes y más mayores de España. ¿Qué edad tiene tu nombre?", RAIZ_RUTA + "nombres-mas-jovenes-y-mas-mayores/")
        + '<div class="content">'
        + secciones
        + '<h2>¿Y los nombres más comunes?</h2>'
        f'<p>El nombre de mujer más común de España, {en(comunes["M"]["n"])}, tiene una edad media de {g.dec(comunes["M"]["e"])} años, '
        f'y el de hombre, {en(comunes["H"]["n"])}, de {g.dec(comunes["H"]["e"])} años. Los nombres más comunes suelen ser de personas mayores, '
        'porque se pusieron muchísimo durante décadas en las que nacían más niños que ahora y casi todo el mundo se llamaba igual.</p>'
        '<h2>Para qué sirve la edad media</h2>'
        '<p>La edad media de un nombre es una buena pista de cuándo estuvo de moda: un nombre con 8 años de media es una moda de ahora, y uno con 70 se puso sobre todo en los años 40 y 50. '
        'En la página de cada nombre puedes ver su edad media y en qué década se puso más. Para los nombres que ya casi no se ponen, mira los '
        '<a href="/nombres-en-peligro-de-extincion/">nombres en peligro de extinción</a>, y para los que se ponen ahora, los '
        '<a href="/articulos/nombres-de-bebe-que-mas-suben/">nombres de bebé que más suben</a>.</p>'
        '</div>'
    )
    desc = (f"Los nombres de mujer y de hombre con la edad media más baja y más alta de España: de {_lista_y(mostrar(x['n']) for x in ejemplos['M'][0])} "
            f"a {_lista_y(mostrar(x['n']) for x in ejemplos['M'][1])}. Datos del INE.")
    return "nombres-mas-jovenes-y-mas-mayores", "Los nombres más jóvenes y más mayores de España", desc, cuerpo, \
        "Los nombres más jóvenes y más mayores", "Qué edad media tiene la gente según su nombre."


# ------------------------------------------------------------------ 5. Nombres de bebé por comunidad
def art_comunidades(g, idx, bebes):
    en = lambda nom: g.enlace(idx, nom)  # noqa: E731
    ult = max(bebes)
    datos = bebes[ult]
    esp = {s: datos["espana"][s]["top"][0][0] for s in "HM"}
    filas, distintas = [], {"H": [], "M": []}
    for clave, d in sorted(((k, v) for k, v in datos.items() if k != "espana"), key=lambda t: t[1]["nombre"]):
        celdas = [escape(d["nombre"])]
        for s in "MH":
            nom, f = d[s]["top"][0]
            celdas.append(f"{en(nom)} <small>({g.n(f)})</small>")
            if normalizar(nom) != normalizar(esp[s]):
                distintas[s].append((d["nombre"], nom))
        filas.append(celdas)

    def frase(s):
        if not distintas[s]:
            return f"{en(esp[s])} es el más puesto en todas las comunidades."
        return (f"{en(esp[s])} no gana en todas. Estas son las comunidades donde el número 1 es otro: "
                + _lista_y(f"{escape(c)} ({en(nom)})" for c, nom in distintas[s]) + ".")
    cuerpo = (
        f'<h1>Los nombres de bebé más puestos en cada comunidad ({ult})</h1>'
        f'<p class="lead">En {ult}, los nombres más puestos en España fueron {en(esp["M"])} y {en(esp["H"])}. Pero cada comunidad tiene sus gustos: '
        'aquí tienes el nombre de niña y de niño número 1 en cada comunidad autónoma, con el número de bebés que lo recibieron.</p>'
        f'<p class="updated">Datos del INE: nombres de los nacidos en {ult}, por comunidad autónoma de residencia de la madre.</p>'
        + g.bloque_compartir(f"Los nombres de bebé más puestos en cada comunidad en {ult}:", RAIZ_RUTA + "nombres-de-bebe-por-comunidad/")
        + '<div class="content">'
        f'<h2>El número 1 de cada comunidad</h2>'
        + _tabla(["Comunidad", "Niñas", "Niños"], filas, num_desde=9)
        + f'<h2>Las niñas: {escape(mostrar(esp["M"]))} y las excepciones</h2><p>{frase("M")}</p>'
        f'<h2>Los niños: {escape(mostrar(esp["H"]))} y las excepciones</h2><p>{frase("H")}</p>'
        '<p>Las diferencias suelen venir de las lenguas propias y de las tradiciones de cada zona: en Cataluña y Baleares aparecen nombres en catalán, '
        'en el País Vasco nombres en euskera y en Andalucía siguen muy presentes los nombres de toda la vida. En las comunidades pequeñas y en Ceuta y Melilla '
        'nacen pocos bebés, así que unos pocos niños bastan para cambiar el número 1.</p>'
        '<h2>Sigue explorando</h2>'
        f'<p>Los 100 nombres más puestos de cada año desde {min(bebes)} están en <a href="/bebes/">nombres de bebé</a>, '
        'los que más suben en <a href="/articulos/nombres-de-bebe-que-mas-suben/">los nombres de bebé que más suben</a>, '
        'y los nombres de los adultos de cada provincia en <a href="/provincias/">nombres por provincia</a>.</p>'
        '</div>'
    )
    desc = f"El nombre de niña y de niño más puesto en {ult} en cada comunidad autónoma, con el número de bebés, y las comunidades donde gana otro nombre. Datos del INE."
    return "nombres-de-bebe-por-comunidad", f"Los nombres de bebé más puestos en cada comunidad ({ult})", desc, cuerpo, \
        "Los nombres de bebé más puestos en cada comunidad", f"El número 1 de niña y de niño en cada comunidad en {ult}."


def paginas_articulos(g, idx, idx_ape, nombres, decadas, bebes, apellidos):
    arts = [
        art_bebes_suben(g, idx, bebes),
        art_comunidades(g, idx, bebes),
        art_decadas(g, idx, decadas, nombres["referencia"]),
        art_edades(g, idx, nombres, nombres["referencia"]),
        art_apellidos(g, idx_ape, apellidos),
    ]
    rutas = []
    for slug, titulo, desc, cuerpo, corto, resumen in arts:
        ruta = f"{RAIZ_RUTA}{slug}/"
        otros = "".join(f'<li><a href="{RAIZ_RUTA}{s}/">{escape(c)}</a></li>' for s, _, _, _, c, _ in arts if s != slug)
        cuerpo += f'<div class="content"><h2>Más artículos</h2><ul>{otros}</ul></div>'
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": titulo, "description": desc, "url": g.DOMINIO + ruta,
               "inLanguage": "es-ES", "image": f"{g.DOMINIO}/og.png", "author": {"@type": "Person", "name": "Albert Sanchez Guiu"},
               "publisher": {"@type": "Organization", "name": g.SITIO, "url": g.DOMINIO + "/"}}]
        g.guardar(ruta, g.pagina(ruta, titulo, desc, cuerpo, [("Artículos", RAIZ_RUTA), (corto, None)], ld))
        rutas.append(ruta)
    tarjetas = "".join(f'<a class="card" href="{RAIZ_RUTA}{s}/"><h3>{escape(c)}</h3><p>{escape(r)}</p></a>' for s, _, _, _, c, r in arts)
    cuerpo = ('<h1>Artículos sobre nombres y apellidos</h1>'
              '<p class="lead">Las tendencias que esconden los datos del INE: qué nombres se ponen cada vez más, cómo han cambiado en casi un siglo, '
              'qué apellidos son los más comunes y qué edad tiene la gente según su nombre.</p>'
              f'<div class="grid">{tarjetas}</div>')
    g.guardar(RAIZ_RUTA, g.pagina(RAIZ_RUTA, "Artículos sobre nombres y apellidos en España",
                                  "Tendencias de nombres y apellidos en España explicadas con los datos del INE: nombres de bebé que suben, cambios por décadas, apellidos más comunes y más.",
                                  cuerpo, [("Artículos", None)]))
    return [RAIZ_RUTA] + rutas, arts
