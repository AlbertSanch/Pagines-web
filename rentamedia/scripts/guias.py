"""Guías de rentamedia.es: explican qué significa cada cifra de renta, con los datos del INE y de Hacienda ya calculados.

Se llama desde generar_web.py: guias.generar(g, T, con_dato, anios), donde g es el propio módulo generar_web
(para usar su plantilla, sus formatos y sus rutas). Todas las cifras salen de rentamedia/data/: no hay ninguna escrita a mano.
"""
from html import escape

INE_ATLAS = ("https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177088&menu=ultiDatos&idp=1254735976608",
             "INE, Atlas de Distribución de Renta de los Hogares")
AEAT_IRPF = ("https://sede.agenciatributaria.gob.es/Sede/estadisticas.html",
             "Agencia Tributaria, Estadística de los declarantes del IRPF por municipios")

GUIAS = [
    ("que-es-la-renta-neta-media", "¿Qué es la renta neta media y cómo se calcula?",
     "Qué significa la renta neta media por persona, en qué se diferencia de la bruta y de la mediana, y cómo la calcula el INE."),
    ("renta-media-por-comunidades", "Renta media en España por comunidades autónomas",
     "Renta neta media por persona y por hogar de cada comunidad autónoma, ordenadas de mayor a menor, con datos del INE."),
    ("renta-por-persona-o-por-hogar", "Renta por persona o por hogar: ¿cuál hay que mirar?",
     "Por qué una comunidad puede estar arriba en renta por hogar y abajo en renta por persona: el tamaño de los hogares."),
    ("renta-y-salario", "Renta y salario no son lo mismo: de dónde salen los ingresos",
     "Qué parte de la renta de los hogares viene del salario, de las pensiones y de las prestaciones, por comunidades."),
    ("desigualdad-de-renta", "Desigualdad de renta en España: índice de Gini por comunidades",
     "Qué es el índice de Gini y la ratio P80/P20, cuánta desigualdad hay en cada comunidad y la distancia entre municipios."),
]


def generar(g, T, con_dato, anios):
    """Crea /guias/ y las guías. Devuelve sus rutas para el sitemap."""
    u = anios[-1]
    es = lambda ind, tabla="agr_renta": g.agregado(T, "es", ind, tabla)[-1]
    ccaa = []
    for ine, nombre in g.COMUNIDADES.items():
        if ine in ("Ceuta", "Melilla"):
            continue
        k = "ccaa:" + ine
        ccaa.append({"ine": ine, "nombre": nombre, "ruta": g.ruta_ccaa(ine),
                     "persona": g.agregado(T, k)[-1], "hogar": g.agregado(T, k, g.HOGAR)[-1],
                     "serie": g.agregado(T, k), "bruta": g.agregado(T, k, g.BRUTA_PERSONA)[-1],
                     "mediana_uc": g.agregado(T, k, g.MEDIANA_UC)[-1],
                     "tam": g.agregado(T, k, "Tamaño medio del hogar", "agr_demografia")[-1],
                     "gini": g.agregado(T, k, "Índice de Gini", "agr_gini")[-1],
                     "p80": g.agregado(T, k, "Distribución de la renta P80/P20", "agr_gini")[-1],
                     "fuentes": {corto: g.agregado(T, k, largo, "agr_fuentes")[-1] for largo, corto in g.FUENTES}})
    ccaa = [c for c in ccaa if c["persona"]]
    d = {"u": u, "persona": es(g.PERSONA), "hogar": es(g.HOGAR), "bruta": es(g.BRUTA_PERSONA),
         "bruta_hogar": es("Renta bruta media por hogar"), "media_uc": es(g.MEDIA_UC), "mediana_uc": es(g.MEDIANA_UC),
         "tam": es("Tamaño medio del hogar", "agr_demografia"), "gini": es("Índice de Gini", "agr_gini"),
         "p80": es("Distribución de la renta P80/P20", "agr_gini"),
         "fuentes": {corto: es(largo, "agr_fuentes") for largo, corto in g.FUENTES}}
    serie_es = g.agregado(T, "es")
    d["anio_ant"], d["persona_ant"] = next(((a, v) for a, v in zip(anios, serie_es) if v), (None, None))
    grandes = [m for m in con_dato if (m["poblacion"] or 0) >= g.MIN_HAB_RANKING]
    rutas = []

    def fuentes_html(extra=()):
        return ('<p class="fuente">Fuentes: ' + " · ".join(f'<a href="{url}" rel="noopener">{escape(t)}</a>'
                                                       for url, t in (INE_ATLAS,) + tuple(extra))
                + f'. Datos de {u}, los últimos publicados. <a href="/sobre-los-datos/">Sobre los datos</a>.</p>')

    def publicar(slug_g, titulo, desc, cuerpo, preguntas, extra_fuentes=()):
        ruta = f"/guias/{slug_g}/"
        otras = "".join(f'<li><a href="/guias/{s}/">{escape(t)}</a></li>' for s, t, _ in GUIAS if s != slug_g)
        html = (f'<article class="guia"><h1>{escape(titulo)}</h1>{cuerpo}'
                f'<div class="content"><h2>Preguntas frecuentes</h2>{g.faq_html(preguntas)}</div>'
                f'{fuentes_html(extra_fuentes)}<h2>Otras guías</h2><ul>{otras}</ul></article>')
        g.guardar(ruta, g.pagina(ruta, f"{titulo} | {g.SITIO}", desc, html, [("Guías", "/guias/"), (titulo, None)],
                                 extra_ld=[g.faq_ld(preguntas)]))
        rutas.append(ruta)

    # ------------------------------------------------ 1. qué es la renta neta media
    uc = 1 + 0.5 + 0.3 + 0.3
    cuerpo = f"""<p class="lead">La renta neta media por persona es lo que ingresa de media cada habitante de un lugar en un año, después de pagar impuestos y cotizaciones. En España fue de <strong>{g.euros(d['persona'])}</strong> en {u}, según el INE.</p>
<div class="content">
<h2>Cómo se calcula</h2>
<p>El INE suma todos los ingresos de los hogares de un municipio (sueldos, pensiones, prestaciones, alquileres, intereses…) a partir de los datos fiscales de la Agencia Tributaria y de las haciendas forales del País Vasco y Navarra, les resta el IRPF y las cotizaciones sociales y divide el resultado entre todas las personas que viven en esos hogares, <strong>niños incluidos</strong>. Por eso la cifra parece baja comparada con un sueldo: un hogar de dos adultos que ganan 25.000 € netos cada uno y tienen dos hijos sale a 12.500 € por persona.</p>
<h2>Las cifras de España en {u}</h2>
<div class="table-wrap"><table class="data"><thead><tr><th>Indicador</th><th class="num">España {u}</th><th>Qué mide</th></tr></thead><tbody>
<tr><td>Renta neta media por persona</td><td class="num">{g.euros(d['persona'])}</td><td>Ingresos después de impuestos, divididos entre todos los habitantes.</td></tr>
<tr><td>Renta neta media por hogar</td><td class="num">{g.euros(d['hogar'])}</td><td>Lo mismo, dividido entre los hogares.</td></tr>
<tr><td>Renta bruta media por persona</td><td class="num">{g.euros(d['bruta'])}</td><td>Antes de restar el IRPF y las cotizaciones.</td></tr>
<tr><td>Renta bruta media por hogar</td><td class="num">{g.euros(d['bruta_hogar'])}</td><td>Ingresos brutos de un hogar medio.</td></tr>
<tr><td>Media por unidad de consumo</td><td class="num">{g.euros(d['media_uc'])}</td><td>Renta del hogar ajustada por cuántas personas viven en él.</td></tr>
<tr><td>Mediana por unidad de consumo</td><td class="num">{g.euros(d['mediana_uc'])}</td><td>La mitad de las personas está por encima y la otra mitad por debajo.</td></tr>
</tbody></table></div>
<h2>Neta y bruta</h2>
<p>La diferencia entre la renta bruta ({g.euros(d['bruta'])}) y la neta ({g.euros(d['persona'])}) por persona son los impuestos y cotizaciones que se pagan de media: unos {g.euros(d['bruta'] - d['persona'])} al año por habitante, el {g.pct((d['bruta'] - d['persona']) / d['bruta'] * 100)} de la renta bruta.</p>
<h2>Media y mediana</h2>
<p>La media se dispara con unos pocos hogares muy ricos; la mediana no. Por eso la mediana por unidad de consumo ({g.euros(d['mediana_uc'])}) es menor que la media ({g.euros(d['media_uc'])}): hay más hogares por debajo de la media que por encima. Si quieres saber si tu hogar «está en la media», la cifra buena es la mediana.</p>
<h2>Qué es una unidad de consumo</h2>
<p>Para comparar hogares de distinto tamaño, el INE usa la escala de la OCDE modificada: el primer adulto cuenta 1, cada adulto más 0,5 y cada menor de 14 años 0,3. Una pareja con dos niños pequeños suma {g.dec(uc)} unidades de consumo: si ingresa 42.000 € netos, su renta por unidad de consumo es de {g.euros(42000 / uc)}. Con esa cifra puedes compararte en el <a href="/comparar-renta/">comparador de renta</a>.</p>
<h2>Por qué los datos son de {u}</h2>
<p>El INE necesita las declaraciones de la renta de cada año, que se presentan al año siguiente, así que publica el Atlas con unos dos años de retraso. {f"Desde {d['anio_ant']}, la renta neta por persona en España ha pasado de {g.euros(d['persona_ant'])} a {g.euros(d['persona'])} ({g.pct((d['persona'] - d['persona_ant']) / d['persona_ant'] * 100)} más), sin descontar la inflación." if d['persona_ant'] and d['anio_ant'] != u else ''}</p>
</div>"""
    publicar(*GUIAS[0][:1], GUIAS[0][1], GUIAS[0][2], cuerpo, [
        ("¿Cuál es la renta neta media por persona en España?",
         f"Fue de {g.euros(d['persona'])} al año en {u}, según el Atlas de Distribución de Renta de los Hogares del INE."),
        ("¿La renta media es lo mismo que el sueldo medio?",
         "No. La renta incluye también pensiones, prestaciones y otros ingresos, se calcula después de impuestos y se divide entre todas las personas del hogar, también los niños y los jubilados."),
        ("¿Qué es mejor para compararse, la media o la mediana?",
         f"La mediana: deja a la mitad de las personas por encima y a la mitad por debajo. En España, la mediana por unidad de consumo fue de {g.euros(d['mediana_uc'])} en {u}."),
    ])

    # ------------------------------------------------ 2. por comunidades
    orden = sorted(ccaa, key=lambda c: -c["persona"])
    # año base común: el primero en que todas las comunidades tienen dato
    i0 = max(next(i for i, v in enumerate(c["serie"]) if v) for c in ccaa)
    a0 = anios[i0]
    filas = "".join(f'<tr><td>{i}</td><td><a href="{c["ruta"]}">{escape(c["nombre"])}</a></td><td class="num">{g.euros(c["persona"])}</td>'
                    f'<td class="num">{g.euros(c["hogar"])}</td><td class="num">{g.variacion(c["serie"][i0], c["persona"])}</td></tr>'
                    for i, c in enumerate(orden, 1))
    alto, bajo = orden[0], orden[-1]
    cuerpo = f"""<p class="lead">En {u}, la renta neta media por persona en España fue de {g.euros(d['persona'])}. La comunidad con más renta es <strong>{escape(alto['nombre'])}</strong> ({g.euros(alto['persona'])}) y la que menos, <strong>{escape(bajo['nombre'])}</strong> ({g.euros(bajo['persona'])}): {g.pct((alto['persona'] / bajo['persona'] - 1) * 100, 0)} de diferencia.</p>
<div class="table-wrap"><table class="data ranking"><thead><tr><th>#</th><th>Comunidad</th><th class="num">Por persona</th><th class="num">Por hogar</th><th class="num">Desde {a0}</th></tr></thead><tbody>{filas}</tbody></table></div>
<div class="content">
<h2>Qué explica las diferencias</h2>
<p>La renta de cada comunidad depende de cuánta gente trabaja, de los sueldos y del peso de las pensiones y las prestaciones: en la guía de <a href="/guias/renta-y-salario/">renta y salario</a> está de dónde salen los ingresos en cada una. Las diferencias dentro de cada comunidad son mucho mayores que entre comunidades: en la página de cada una están sus municipios ordenados de más a menos renta.</p>
<h2>Cuidado con el coste de la vida</h2>
<p>Estas cifras no descuentan lo que cuesta vivir en cada sitio. La vivienda, sobre todo, es mucho más cara en Madrid, Barcelona, Baleares o el País Vasco, así que una renta más alta no siempre significa más poder de compra. Puedes comparar con el <a href="/alquiler/">precio del alquiler</a> de cada municipio.</p>
<p>Ceuta y Melilla no aparecen en la tabla: el INE las publica como ciudades autónomas y están en sus propias páginas.</p>
</div>"""
    publicar(GUIAS[1][0], GUIAS[1][1], GUIAS[1][2], cuerpo, [
        (f"¿Qué comunidad tiene la renta más alta de España?",
         f"{alto['nombre']}, con {g.euros(alto['persona'])} netos por persona en {u}, según el INE."),
        (f"¿Qué comunidad tiene la renta más baja?",
         f"{bajo['nombre']}, con {g.euros(bajo['persona'])} netos por persona en {u}."),
        ("¿Estas cifras tienen en cuenta el coste de la vida?",
         "No. Son ingresos netos sin ajustar por precios: la vivienda y otros gastos varían mucho entre comunidades."),
    ])

    # ------------------------------------------------ 3. por persona o por hogar
    por_hogar = sorted(ccaa, key=lambda c: -c["hogar"])
    puesto_p = {c["ine"]: i for i, c in enumerate(orden, 1)}
    puesto_h = {c["ine"]: i for i, c in enumerate(por_hogar, 1)}
    filas = "".join(f'<tr><td><a href="{c["ruta"]}">{escape(c["nombre"])}</a></td><td class="num">{g.dec(c["tam"], 1) if c["tam"] else "—"}</td>'
                    f'<td class="num">{puesto_p[c["ine"]]}.º</td><td class="num">{puesto_h[c["ine"]]}.º</td></tr>'
                    for c in sorted(ccaa, key=lambda c: -(c["tam"] or 0)))
    salto = max(ccaa, key=lambda c: puesto_p[c["ine"]] - puesto_h[c["ine"]])
    cuerpo = f"""<p class="lead">La renta por hogar suma lo que ingresan todos los que viven juntos; la renta por persona la reparte entre todos ellos. Cuanta más gente vive en cada casa, más se separan las dos cifras. En España, el hogar medio tiene {g.dec(d['tam'], 1)} personas: {g.euros(d['hogar'])} por hogar y {g.euros(d['persona'])} por persona en {u}.</p>
<div class="content">
<h2>Cuándo mirar cada una</h2>
<ul>
<li><strong>Por persona</strong>: para comparar el nivel de vida de dos lugares. Es la que usa el INE en sus notas de prensa y la principal de esta web.</li>
<li><strong>Por hogar</strong>: para hacerse una idea de cuánto entra en una casa al año. Sale más alta en los sitios con familias grandes.</li>
<li><strong>Por unidad de consumo</strong>: para compararte tú. Ajusta por el tamaño del hogar y por si hay niños (ver <a href="/guias/que-es-la-renta-neta-media/">qué es la renta neta media</a>).</li>
</ul>
<h2>El ranking cambia según la cifra</h2>
<p>Las comunidades con hogares más grandes suben en el ranking por hogar y bajan en el de por persona. El caso más claro en {u} es {escape(salto['nombre'])}: {puesto_p[salto['ine']]}.ª por persona y {puesto_h[salto['ine']]}.ª por hogar, con {g.dec(salto['tam'], 1)} personas por hogar de media.</p>
</div>
<div class="table-wrap"><table class="data"><thead><tr><th>Comunidad</th><th class="num">Personas por hogar</th><th class="num">Puesto por persona</th><th class="num">Puesto por hogar</th></tr></thead><tbody>{filas}</tbody></table></div>"""
    publicar(GUIAS[2][0], GUIAS[2][1], GUIAS[2][2], cuerpo, [
        ("¿Por qué la renta por hogar es mucho más alta que la renta por persona?",
         f"Porque en un hogar viven de media {g.dec(d['tam'], 1)} personas en España: los ingresos de la casa se reparten entre todas, incluidos niños y jubilados."),
        ("¿Qué cifra sirve para comparar el nivel de vida?",
         "La renta por persona o, mejor aún, la renta por unidad de consumo, que tiene en cuenta el tamaño del hogar."),
        ("¿Cuántas personas viven de media en un hogar en España?",
         f"{g.dec(d['tam'], 1)} personas en {u}, según el INE."),
    ])

    # ------------------------------------------------ 4. renta y salario
    f = d["fuentes"]
    nombres_f = [corto for _, corto in g.FUENTES]
    filas = "".join(f'<tr><td><a href="{c["ruta"]}">{escape(c["nombre"])}</a></td>'
                    + "".join(f'<td class="num">{g.pct(c["fuentes"][x]) if c["fuentes"].get(x) is not None else "—"}</td>' for x in nombres_f[:3])
                    + "</tr>" for c in sorted(ccaa, key=lambda c: -(c["fuentes"].get("Salarios") or 0)))
    mas_pens = max(ccaa, key=lambda c: c["fuentes"].get("Pensiones") or 0)
    hac = g.HACIENDA.get("espana") or {}
    bloque_hac = ""
    extra = ()
    if hac.get("bruta_media"):
        extra = (AEAT_IRPF,)
        bloque_hac = f"""<h2>Lo que dice Hacienda</h2>
<p>La Agencia Tributaria publica otra cifra: la renta media <em>por declaración</em> del IRPF. En {g.HACIENDA.get('anio_municipios')} hubo {g.n(hac['declaraciones'])} declaraciones en España, con una renta bruta media de {g.euros(hac['bruta_media'])} y una renta disponible (después de impuestos) de {g.euros(hac['disponible_media'])}. La mediana bruta fue de {g.euros(hac['bruta_mediana'])}. Son cifras más altas que las del INE porque se dividen entre declarantes, no entre todos los habitantes: los niños y muchas personas sin ingresos no declaran.</p>"""
    cuerpo = f"""<p class="lead">Mucha gente compara la renta media de su municipio con su sueldo y no le cuadra. Es normal: la renta de los hogares no es solo salario. En España, en {u}, el {g.pct(f['Salarios'])} de la renta bruta de los hogares venía del trabajo asalariado y el {g.pct(f['Pensiones'])} de las pensiones.</p>
<div class="content">
<h2>De dónde salen los ingresos de los hogares</h2>
<div class="table-wrap"><table class="data"><thead><tr><th>Fuente</th><th class="num">España {u}</th></tr></thead><tbody>
{"".join(f'<tr><td>{x}</td><td class="num">{g.pct(f[x]) if f.get(x) is not None else "—"}</td></tr>' for x in nombres_f)}
</tbody></table></div>
<p>«Otros ingresos» incluye el trabajo por cuenta propia, los alquileres, los intereses y los dividendos.</p>
<h2>Tres diferencias con un sueldo</h2>
<ul>
<li><strong>Se reparte entre todos</strong>: la renta por persona divide los ingresos del hogar también entre los niños y quienes no trabajan.</li>
<li><strong>Incluye pensiones y prestaciones</strong>: en los municipios con mucha población mayor, las pensiones pesan más que los salarios.</li>
<li><strong>Es neta</strong>: ya están restados el IRPF y las cotizaciones a la Seguridad Social.</li>
</ul>
{bloque_hac}
<h2>Por comunidades</h2>
<p>{escape(mas_pens['nombre'])} es la comunidad donde más pesan las pensiones: el {g.pct(mas_pens['fuentes']['Pensiones'])} de la renta bruta de sus hogares.</p>
</div>
<div class="table-wrap"><table class="data"><thead><tr><th>Comunidad</th>{"".join(f'<th class="num">{x}</th>' for x in nombres_f[:3])}</tr></thead><tbody>{filas}</tbody></table></div>"""
    publicar(GUIAS[3][0], GUIAS[3][1], GUIAS[3][2], cuerpo, [
        ("¿Por qué la renta media de mi municipio es más baja que mi sueldo?",
         "Porque la renta por persona reparte los ingresos del hogar entre todos los que viven en él, también los niños y quienes no trabajan, y ya tiene restados los impuestos."),
        ("¿Qué parte de la renta de los hogares viene del salario?",
         f"El {g.pct(f['Salarios'])} de la renta bruta en España en {u}; las pensiones aportan el {g.pct(f['Pensiones'])}."),
        ("¿Qué diferencia hay entre los datos del INE y los de Hacienda?",
         "Hacienda divide la renta entre las declaraciones del IRPF; el INE, entre todos los habitantes. Por eso las cifras de Hacienda son más altas."),
    ], extra)

    # ------------------------------------------------ 5. desigualdad
    filas = "".join(f'<tr><td><a href="{c["ruta"]}">{escape(c["nombre"])}</a></td><td class="num">{g.dec(c["gini"]) if c["gini"] else "—"}</td>'
                    f'<td class="num">{g.dec(c["p80"]) if c["p80"] else "—"}</td></tr>'
                    for c in sorted(ccaa, key=lambda c: -(c["gini"] or 0)))
    mas_d = max(ccaa, key=lambda c: c["gini"] or 0)
    menos_d = min(ccaa, key=lambda c: c["gini"] or 100)
    rico, pobre = grandes[0], grandes[-1]
    cuerpo = f"""<p class="lead">El índice de Gini mide cómo de repartida está la renta: 0 sería que todos ingresan lo mismo y 100, que una sola persona lo tiene todo. En España fue de <strong>{g.dec(d['gini'])}</strong> en {u}, según el INE.</p>
<div class="content">
<h2>Dos formas de medirla</h2>
<ul>
<li><strong>Índice de Gini</strong>: resume toda la distribución en una cifra. Cuanto más alto, más desigual.</li>
<li><strong>Ratio P80/P20</strong>: cuántas veces más ingresa una persona en el 20 % más rico que una en el 20 % más pobre. En España, {g.dec(d['p80'])} veces.</li>
</ul>
<h2>Por comunidades</h2>
<p>La comunidad más desigual en {u} es {escape(mas_d['nombre'])} (Gini {g.dec(mas_d['gini'])}) y la menos, {escape(menos_d['nombre'])} ({g.dec(menos_d['gini'])}). La desigualdad no va siempre de la mano de la renta: hay comunidades ricas con mucha desigualdad y otras con menos renta y más igualdad.</p>
</div>
<div class="table-wrap"><table class="data"><thead><tr><th>Comunidad</th><th class="num">Índice de Gini</th><th class="num">P80/P20</th></tr></thead><tbody>{filas}</tbody></table></div>
<div class="content">
<h2>Entre municipios, la distancia es mucho mayor</h2>
<p>Entre los municipios de más de {g.n(g.MIN_HAB_RANKING)} habitantes, el de más renta por persona es <a href="{g.ruta_mun(rico)}">{escape(rico['nombre'])}</a> ({g.euros(rico['renta'])}) y el de menos, <a href="{g.ruta_mun(pobre)}">{escape(pobre['nombre'])}</a> ({g.euros(pobre['renta'])}): {g.dec(rico['renta'] / pobre['renta'])} veces más. Puedes ver los extremos en los rankings de <a href="/municipios-mas-ricos-de-espana/">municipios más ricos</a> y <a href="/municipios-mas-pobres-de-espana/">más pobres</a>, y dentro de las grandes ciudades en los <a href="/barrios/">barrios</a>.</p>
</div>"""
    publicar(GUIAS[4][0], GUIAS[4][1], GUIAS[4][2], cuerpo, [
        ("¿Qué es el índice de Gini?",
         "Un indicador de desigualdad de 0 a 100: 0 si todos tienen la misma renta y 100 si una sola persona lo tiene todo."),
        ("¿Cuál es el índice de Gini de España?",
         f"{g.dec(d['gini'])} en {u}, según el Atlas de Distribución de Renta de los Hogares del INE."),
        ("¿Qué comunidad es la más desigual?",
         f"{mas_d['nombre']}, con un índice de Gini de {g.dec(mas_d['gini'])} en {u}."),
    ])

    # ------------------------------------------------ índice
    tarjetas = "".join(f'<a class="card" href="/guias/{s}/"><h3>{escape(t)}</h3><p>{escape(ds)}</p></a>' for s, t, ds in GUIAS)
    g.guardar("/guias/", g.pagina("/guias/", f"Guías sobre la renta en España | {g.SITIO}",
                                  "Guías para entender la renta media: qué es, cómo se calcula, por comunidades, por hogar, salarios y desigualdad.",
                                  f'<h1>Guías sobre la renta</h1><p class="lead">Qué significan las cifras de renta del INE y cómo leerlas, con los datos de {u} ya calculados.</p><div class="grid">{tarjetas}</div>',
                                  [("Guías", None)]))
    return ["/guias/"] + rutas
