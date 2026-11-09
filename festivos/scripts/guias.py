"""Guías de festivosde.es: artículos útiles sobre festivos y calendario laboral, con su base legal (BOE) y datos
calculados a partir de los festivos oficiales. Las genera generar_web.py (le pasa sus funciones de plantilla).

Bases legales comprobadas en el texto consolidado del BOE (noviembre de 2026):
- Estatuto de los Trabajadores (BOE-A-2015-11430), art. 37.2 (fiestas) y art. 38 (vacaciones).
- Real Decreto 2001/1983 (BOE-A-1983-20906), arts. 45 (fiestas nacionales y traslado), 46 (locales) y 47 (trabajo en festivo).
- Ley 39/2015 (BOE-A-2015-10565), art. 30 (cómputo de plazos administrativos).
"""
import datetime as dt
from html import escape

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
RD = "https://www.boe.es/buscar/act.php?id=BOE-A-1983-20906"
LEY39 = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565"
REVISADO = "noviembre de 2026"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
# fiestas nacionales de fecha fija (Real Decreto 2001/1983, art. 45.1)
FIJAS = [(1, 1, "Año Nuevo"), (1, 6, "Epifanía del Señor"), (5, 1, "Fiesta del Trabajo"), (8, 15, "Asunción de la Virgen"),
         (10, 12, "Fiesta Nacional de España"), (11, 1, "Todos los Santos"), (12, 6, "Día de la Constitución"),
         (12, 8, "Inmaculada Concepción"), (12, 25, "Natividad del Señor")]


def f_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def generar(datos, anios, comunidades, pagina, guardar, faq_html, faq_ld, de):
    """Crea /guias/ y cada guía. Devuelve sus rutas para el sitemap."""
    fuente = lambda *ls: '<p class="fuente">Fuentes: ' + ", ".join(f'<a href="{u}" rel="noopener">{escape(t)}</a>' for t, u in ls) + f". Revisado en {REVISADO}.</p>"  # noqa: E731
    boe = {a: datos[a]["boe"] for a in anios}
    nombre = lambda c: comunidades[c][0]  # noqa: E731
    lista_cc = sorted(datos[anios[-1]]["nacionales_autonomicos"], key=nombre)
    guias = []

    # ------------------------------------------------------------ 1. festivo en domingo
    filas, ejemplos = "", []
    for a in anios:
        for m, d, n in FIJAS:
            f = dt.date(a, m, d)
            if f.weekday() != 6:
                continue
            lunes = (f + dt.timedelta(days=1)).isoformat()
            si = [c for c in lista_cc if any(x["f"] == lunes for x in datos[a]["nacionales_autonomicos"][c])]
            no = [c for c in lista_cc if c not in si]
            filas += (f"<tr><td>{n}</td><td>{f_larga(f)} de {a}</td><td>{len(si)} de {len(lista_cc)}</td>"
                      f"<td>{escape(', '.join(nombre(c) for c in no)) if no and len(no) < len(lista_cc) else ('ninguna' if not no else 'todas')}</td></tr>")
            ejemplos.append((n, f, a, len(si)))
    tabla = (f'<div class="tabla-envoltorio"><table class="festivos completa"><thead><tr><th>Fiesta</th><th>Cae en domingo</th><th>Comunidades que dan el lunes</th>'
             f'<th>Comunidades que no</th></tr></thead><tbody>{filas}</tbody></table></div>') if filas else ""
    ej = ""
    if ejemplos:
        n, f, a, k = ejemplos[0]
        ej = (f"<p>Un ejemplo reciente: en {a}, {n} cae en domingo ({f_larga(f)}). Según la resolución del BOE, "
              f"{k} de las {len(lista_cc)} comunidades y ciudades autónomas trasladan el descanso al lunes siguiente y el resto "
              "lo sustituye por otra fiesta propia.</p>")
    preguntas = [
        ("Si un festivo cae en domingo, ¿se pasa al lunes?",
         "Para las fiestas nacionales, la regla general es que el descanso se traslada al lunes inmediatamente posterior "
         "(artículo 37.2 del Estatuto de los Trabajadores). Pero cada comunidad autónoma puede sustituir ese lunes por otra fiesta propia, "
         "así que depende de dónde vivas."),
        ("¿Y si la fiesta local de mi pueblo cae en domingo?",
         "Las dos fiestas locales las propone cada ayuntamiento y las aprueba la autoridad laboral de la comunidad. Lo que vale es la fecha "
         "publicada en el boletín oficial: búscala en la página de tu municipio."),
        ("¿Pierdo un festivo si cae en sábado?",
         "La ley solo prevé el traslado al lunes de las fiestas que caen en domingo. Si un festivo cae en sábado y tú no trabajas los sábados, "
         "no se recupera otro día, salvo que tu convenio colectivo diga otra cosa."),
    ]
    cuerpo = f"""<h1>¿Qué pasa si un festivo cae en domingo?</h1>
<p class="lead">Cuando una fiesta nacional coincide con domingo, el descanso pasa al lunes siguiente… salvo que tu comunidad autónoma decida cambiarlo por otra fiesta. Te explicamos la norma y cómo se ha aplicado.</p>
<section class="contenido"><h2>Qué dice la ley</h2>
<p>El <a href="{ET}" rel="noopener">artículo 37.2 del Estatuto de los Trabajadores</a> establece que será «en todo caso, objeto de traslado al lunes inmediatamente posterior el descanso laboral correspondiente a las fiestas que coincidan con domingo». El <a href="{RD}" rel="noopener">Real Decreto 2001/1983</a>, en su artículo 45, dice lo mismo para las fiestas nacionales: el descanso «se disfrutará el lunes inmediatamente posterior».</p>
<p>Pero el mismo artículo permite a las comunidades autónomas «sustituir el descanso del lunes de las fiestas nacionales que coincidan con domingo por la incorporación a la relación de fiestas de la comunidad autónoma de otras que les sean tradicionales». Por eso, cuando un festivo cae en domingo, en unas comunidades el lunes es festivo y en otras no: lo han cambiado por una fiesta propia.</p>
{ej}</section>
<section class="contenido"><h2>Festivos nacionales que caen en domingo</h2>
<p>Estas son las fiestas nacionales de fecha fija que caen en domingo en {" y ".join(str(a) for a in anios)}, y cuántas comunidades dan el lunes siguiente, según las resoluciones del BOE:</p>
{tabla or "<p>En estos años ninguna fiesta nacional de fecha fija cae en domingo.</p>"}
<p>Para saber exactamente qué días son festivos donde vives, <a href="/">busca tu municipio</a>: ahí verás los festivos nacionales, los de tu comunidad y las dos fiestas locales.</p></section>
<section class="contenido"><h2>¿Y los festivos que caen en sábado?</h2>
<p>La ley solo habla del traslado de las fiestas que coinciden con domingo. Si un festivo cae en sábado, no se pasa a otro día, aunque tú no trabajes los sábados. Algunos convenios colectivos sí lo compensan, así que conviene revisarlo.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
{fuente(("Estatuto de los Trabajadores, art. 37", ET), ("Real Decreto 2001/1983, art. 45", RD), *[(f"BOE, fiestas laborales {a}", boe[a]["url"]) for a in anios])}"""
    guias.append(("/guias/festivo-en-domingo/", "¿Qué pasa si un festivo cae en domingo? Se pasa al lunes…",
                  "Si un festivo nacional cae en domingo, el descanso pasa al lunes, salvo que tu comunidad lo cambie. Qué dice la ley y qué comunidades lo aplican.",
                  cuerpo, preguntas, "Festivo en domingo"))

    # ------------------------------------------------------------ 2. trabajar en festivo
    preguntas = [
        ("¿Cuánto se cobra por trabajar un festivo?",
         "Como mínimo, las horas trabajadas se pagan con un incremento del 75 % sobre su precio normal, además del salario de la semana, "
         "salvo que la empresa te dé un descanso compensatorio (artículo 47 del Real Decreto 2001/1983). Tu convenio puede mejorarlo."),
        ("¿Me pueden dar un día libre en lugar de pagarme más?",
         "Sí: la norma permite sustituir el pago por un descanso compensatorio. Cómo y cuándo se disfruta suele concretarlo el convenio colectivo."),
        ("¿Los festivos se recuperan?",
         "No. Las fiestas laborales son «retribuidas y no recuperables» (artículo 37.2 del Estatuto de los Trabajadores): si no trabajas, "
         "cobras el día igualmente y no tienes que devolver esas horas."),
    ]
    cuerpo = f"""<h1>¿Cuánto se cobra por trabajar un festivo?</h1>
<p class="lead">Si trabajas un día festivo, la ley obliga a pagarte esas horas con al menos un 75 % más, o a darte un descanso a cambio. Así se calcula y esto es lo que debes revisar.</p>
<section class="contenido"><h2>Lo que dice la norma</h2>
<p>Los festivos son días de descanso «retribuidos y no recuperables», según el <a href="{ET}" rel="noopener">artículo 37.2 del Estatuto de los Trabajadores</a>: si no trabajas, cobras el día y no tienes que recuperarlo.</p>
<p>Cuando, «excepcionalmente y por razones técnicas u organizativas», no se puede disfrutar el festivo, el <a href="{RD}" rel="noopener">artículo 47 del Real Decreto 2001/1983</a> obliga a la empresa a pagar, además del salario de la semana, «el importe de las horas trabajadas en el día festivo […] incrementadas en un 75 por 100, como mínimo, salvo descanso compensatorio».</p></section>
<section class="contenido"><h2>Un ejemplo</h2>
<p>Si tu hora de trabajo normal vale 12 €, cada hora trabajada en festivo se paga, como mínimo, a 21 € (12 € más el 75 %). Si trabajas una jornada de 8 horas, son 168 € por ese día, además de tu sueldo de la semana. La otra opción que permite la norma es que, en vez de pagarte ese extra, la empresa te dé un día de descanso a cambio.</p></section>
<section class="contenido"><h2>Revisa tu convenio colectivo</h2>
<p>El 75 % es el mínimo legal. Muchos convenios, sobre todo en hostelería, comercio, sanidad o transporte, fijan un plus por festivo, un porcentaje mayor o reglas concretas sobre el descanso compensatorio. Lo que diga tu convenio se aplica si es más favorable.</p>
<p>Para planificar el año, mira qué días son festivos <a href="/">en tu municipio</a> y calcula tus <a href="/calculadora-dias-laborables/">días laborables</a>.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
<p class="nota">Esta guía es informativa y no sustituye el asesoramiento de un profesional ni lo que establezca tu convenio colectivo.</p>
{fuente(("Estatuto de los Trabajadores, art. 37", ET), ("Real Decreto 2001/1983, art. 47", RD))}"""
    guias.append(("/guias/trabajar-en-festivo/", "¿Cuánto se cobra por trabajar un festivo? El mínimo legal",
                  "Trabajar en festivo se paga como mínimo con un 75 % más por hora o con un día de descanso. Qué dice la ley, un ejemplo y qué revisar en tu convenio.",
                  cuerpo, preguntas, "Trabajar en festivo"))

    # ------------------------------------------------------------ 3. cómo se fijan los festivos
    a = anios[-1]
    cuentas = {c: len(datos[a]["nacionales_autonomicos"][c]) for c in lista_cc}
    preguntas = [
        ("¿Cuántos festivos hay al año en España?",
         "Como máximo 14 fiestas laborales al año, de las cuales dos son locales (artículo 37.2 del Estatuto de los Trabajadores)."),
        ("¿Quién decide las fiestas locales?",
         "Las propone el pleno de cada ayuntamiento y las fija la autoridad laboral de la comunidad autónoma, que las publica en su boletín "
         "oficial o en el de la provincia (artículo 46 del Real Decreto 2001/1983)."),
        ("¿Cuándo se publican los festivos del año siguiente?",
         "Las comunidades comunican sus fiestas al Ministerio de Trabajo antes del 30 de septiembre y el BOE publica la relación de fiestas "
         "laborales normalmente en octubre. Las fiestas locales se publican en los boletines autonómicos o provinciales, a lo largo del otoño."),
    ]
    filas = "".join(f'<tr><td><a href="/comunidad/{c}/">{escape(nombre(c))}</a></td><td>{cuentas[c]}</td></tr>' for c in lista_cc)
    cuerpo = f"""<h1>¿Cómo se deciden los festivos en España?</h1>
<p class="lead">Hay tres tipos de festivos: los nacionales, los de cada comunidad autónoma y las dos fiestas locales de cada municipio. Te explicamos quién decide cada uno y cuándo se publican.</p>
<section class="contenido"><h2>El límite: 14 festivos al año</h2>
<p>El <a href="{ET}" rel="noopener">artículo 37.2 del Estatuto de los Trabajadores</a> fija que las fiestas laborales «no podrán exceder de catorce al año, de las cuales dos serán locales». Además, establece cuatro fiestas que se respetan siempre en toda España: Navidad (25 de diciembre), Año Nuevo (1 de enero), el 1 de mayo y el 12 de octubre.</p></section>
<section class="contenido"><h2>Las fiestas nacionales</h2>
<p>El <a href="{RD}" rel="noopener">artículo 45 del Real Decreto 2001/1983</a> enumera las fiestas de ámbito nacional:</p>
<ul><li><strong>De carácter cívico:</strong> 12 de octubre, Fiesta Nacional de España, y 6 de diciembre, Día de la Constitución.</li>
<li><strong>Según el Estatuto de los Trabajadores:</strong> 1 de enero, 1 de mayo y 25 de diciembre.</li>
<li><strong>Por el Acuerdo con la Santa Sede de 1979:</strong> 15 de agosto, 1 de noviembre, 8 de diciembre y Viernes Santo.</li>
<li><strong>Las que las comunidades pueden sustituir:</strong> Jueves Santo, 6 de enero y 19 de marzo (San José) o 25 de julio (Santiago Apóstol).</li></ul></section>
<section class="contenido"><h2>Las fiestas de cada comunidad autónoma</h2>
<p>Cada comunidad puede cambiar las fiestas del último grupo (y los lunes de las fiestas que caen en domingo) por otras propias: su día de la comunidad, el Lunes de Pascua, San Juan… Debe comunicarlas al Ministerio de Trabajo antes del 30 de septiembre, y la Dirección General de Trabajo publica cada año en el BOE la relación de fiestas de toda España. La de {a} es la <a href="{boe[a]['url']}" rel="noopener">{escape(boe[a]['titulo'])}</a></p>
<p>Por eso no todas las comunidades tienen el mismo número de festivos sin contar los locales. En {a}:</p>
<div class="tabla-envoltorio"><table class="festivos completa"><thead><tr><th>Comunidad</th><th>Festivos nacionales y autonómicos en {a}</th></tr></thead><tbody>{filas}</tbody></table></div></section>
<section class="contenido"><h2>Las dos fiestas locales</h2>
<p>Según el <a href="{RD}" rel="noopener">artículo 46 del Real Decreto 2001/1983</a>, cada municipio tiene hasta dos fiestas locales «que por tradición le sean propias», que fija la autoridad laboral autonómica a propuesta del pleno del ayuntamiento y que se publican en el boletín oficial de la comunidad y, en su caso, de la provincia. Si un ayuntamiento no las propone, ese año no tiene fiestas locales.</p>
<p>En festivosde.es recogemos esas publicaciones municipio a municipio: <a href="/">busca el tuyo</a> o consulta el <a href="/calendario-laboral-{a}/">calendario laboral de {a}</a>.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
{fuente(("Estatuto de los Trabajadores, art. 37", ET), ("Real Decreto 2001/1983, arts. 45 y 46", RD), (f"BOE, fiestas laborales {a}", boe[a]["url"]))}"""
    guias.append(("/guias/como-se-fijan-los-festivos/", "¿Cómo se deciden los festivos en España? Nacionales, autonómicos y locales",
                  "Quién decide los festivos nacionales, los de cada comunidad y las dos fiestas locales, cuándo se publican y cuántos tiene cada comunidad.",
                  cuerpo, preguntas, "Cómo se fijan los festivos"))

    # ------------------------------------------------------------ 4. días de vacaciones
    preguntas = [
        ("¿Cuántos días de vacaciones me corresponden al año?",
         "Como mínimo 30 días naturales al año (artículo 38 del Estatuto de los Trabajadores). Tu convenio o tu contrato pueden darte más, nunca menos."),
        ("¿Me pueden pagar las vacaciones en vez de disfrutarlas?",
         "No mientras sigas en la empresa: las vacaciones son «no sustituibles por compensación económica» (artículo 38.1). Las que no hayas disfrutado se pagan cuando termina la relación laboral, normalmente en el finiquito."),
        ("¿Con cuánta antelación tengo que saber mis vacaciones?",
         "Al menos dos meses antes de empezar a disfrutarlas, según el artículo 38.3 del Estatuto de los Trabajadores."),
    ]
    cuerpo = f"""<h1>¿Cuántos días de vacaciones me corresponden?</h1>
<p class="lead">La ley garantiza al menos 30 días naturales de vacaciones pagadas al año. Te explicamos cómo se cuentan, cuándo te las tienen que comunicar y qué pasa si coinciden con una baja.</p>
<section class="contenido"><h2>El mínimo: 30 días naturales</h2>
<p>El <a href="{ET}" rel="noopener">artículo 38 del Estatuto de los Trabajadores</a> dice que el periodo de vacaciones anuales retribuidas será el pactado en convenio o contrato y que «en ningún caso la duración será inferior a treinta días naturales». Naturales significa que cuentan todos los días, también sábados, domingos y festivos.</p>
<p>Muchos convenios expresan las vacaciones en días laborables, normalmente 22, que equivalen más o menos a los 30 naturales. Si tu convenio habla de días laborables, los festivos que caigan dentro de tus vacaciones no se descuentan.</p></section>
<section class="contenido"><h2>Cuándo se fijan</h2>
<p>Las fechas se acuerdan entre empresa y trabajador, según lo que diga el convenio sobre la planificación anual. El calendario de vacaciones se fija en cada empresa y debes conocer tus fechas «dos meses antes, al menos, del comienzo del disfrute». Si no hay acuerdo, decide un juzgado de lo social en un procedimiento rápido.</p></section>
<section class="contenido"><h2>Si coinciden con una baja</h2>
<p>El mismo artículo 38 establece que si tus vacaciones coinciden con una incapacidad temporal por embarazo, parto o lactancia, o con el permiso por nacimiento, tienes derecho a disfrutarlas en otra fecha, aunque haya terminado el año. Si coinciden con otra baja que te impide disfrutarlas durante el año, puedes hacerlo cuando termine la baja, siempre que no hayan pasado más de 18 meses desde el final del año en que se generaron.</p></section>
<section class="contenido"><h2>Si no has trabajado el año entero</h2>
<p>Lo habitual es calcularlas de forma proporcional al tiempo trabajado: 30 días entre 12 meses son 2,5 días por cada mes. Revisa lo que diga tu convenio.</p></section>
<section class="contenido"><h2>Saca más días libres</h2>
<p>Juntando tus días de vacaciones con festivos y fines de semana puedes conseguir periodos de descanso más largos. Prueba nuestro <a href="/planificador-vacaciones/">planificador de vacaciones</a>, que lo calcula con los festivos de tu municipio, y mira los <a href="/puentes-{anios[-1]}/">puentes de {anios[-1]}</a>.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
<p class="nota">Esta guía es informativa y no sustituye el asesoramiento de un profesional ni lo que establezca tu convenio colectivo.</p>
{fuente(("Estatuto de los Trabajadores, art. 38", ET))}"""
    guias.append(("/guias/dias-de-vacaciones/", "¿Cuántos días de vacaciones me corresponden? Lo que dice la ley",
                  "Al menos 30 días naturales de vacaciones pagadas al año: cómo se cuentan, cuándo te las tienen que comunicar y qué pasa si coinciden con una baja.",
                  cuerpo, preguntas, "Días de vacaciones"))

    # ------------------------------------------------------------ 5. días hábiles e inhábiles
    preguntas = [
        ("¿El sábado es día hábil?",
         "Para los plazos administrativos, no: los sábados, domingos y festivos son inhábiles (artículo 30.2 de la Ley 39/2015). "
         "En el ámbito laboral, en cambio, el sábado sí puede ser un día laborable."),
        ("¿Qué pasa si el último día de un plazo es festivo?",
         "Se prorroga automáticamente al primer día hábil siguiente (artículo 30.5 de la Ley 39/2015)."),
        ("Si es festivo en mi pueblo pero no donde está la Administración, ¿cuenta?",
         "Si un día es hábil donde vives e inhábil en la sede del organismo, o al revés, se considera inhábil en todo caso (artículo 30.6)."),
    ]
    cuerpo = f"""<h1>Días hábiles e inhábiles: cómo se cuentan los plazos</h1>
<p class="lead">No es lo mismo un día laborable que un día hábil. Si tienes que presentar algo ante la Administración, los sábados, domingos y festivos no cuentan. Te explicamos cómo se calculan los plazos.</p>
<section class="contenido"><h2>Laborable no es lo mismo que hábil</h2>
<p><strong>Día laborable</strong> es un día de trabajo según el calendario laboral: de lunes a sábado, salvo los festivos. <strong>Día hábil</strong> es un concepto de los procedimientos administrativos: el <a href="{LEY39}" rel="noopener">artículo 30.2 de la Ley 39/2015</a> dice que, cuando los plazos se señalan por días, «se entiende que éstos son hábiles, excluyéndose del cómputo los sábados, los domingos y los declarados festivos».</p></section>
<section class="contenido"><h2>Cómo se cuenta un plazo en días</h2>
<ul><li>Se empieza a contar el día siguiente a la notificación o publicación (artículo 30.3).</li>
<li>Se saltan los sábados, los domingos y los festivos.</li>
<li>Si el último día es inhábil, el plazo se alarga hasta el primer día hábil siguiente (artículo 30.5).</li>
<li>Si un día es hábil donde vives pero inhábil en la sede del organismo, o al revés, se considera inhábil (artículo 30.6). Por eso importan también las fiestas locales.</li></ul>
<p>Los plazos en meses o años funcionan distinto: se cuentan de fecha a fecha y terminan el mismo día del mes de vencimiento (artículo 30.4).</p></section>
<section class="contenido"><h2>Qué festivos cuentan</h2>
<p>La Administración General del Estado y cada comunidad autónoma publican antes de cada año su calendario de días inhábiles, que incluye los festivos nacionales, autonómicos y locales (artículo 30.7). Para saber qué días son festivos en tu municipio, <a href="/">búscalo aquí</a>; para contar días de trabajo, usa la <a href="/calculadora-dias-laborables/">calculadora de días laborables</a>.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
<p class="nota">Esta guía resume la norma general de los procedimientos administrativos. Otros ámbitos, como los juzgados, tienen reglas propias.</p>
{fuente(("Ley 39/2015, art. 30", LEY39))}"""
    guias.append(("/guias/dias-habiles-e-inhabiles/", "Días hábiles e inhábiles: cómo se cuentan los plazos",
                  "¿El sábado es día hábil? Qué días cuentan en los plazos administrativos, qué pasa si el último es festivo y la diferencia con día laborable.",
                  cuerpo, preguntas, "Días hábiles e inhábiles"))

    # ------------------------------------------------------------ 6. días laborables del año
    a = anios[-1]
    lab = []
    total = sum(1 for i in range(366 if a % 4 == 0 else 365) if (dt.date(a, 1, 1) + dt.timedelta(days=i)).weekday() < 5)
    for c in lista_cc:
        ent = {x["f"] for x in datos[a]["nacionales_autonomicos"][c] if dt.date.fromisoformat(x["f"]).weekday() < 5}
        lab.append((total - len(ent), c, len(ent)))
    lab.sort(key=lambda x: (-x[0], nombre(x[1])))
    filas = "".join(f'<tr><td><a href="/comunidad/{c}/">{escape(nombre(c))}</a></td><td>{n}</td><td>{e}</td></tr>' for n, c, e in lab)
    mas, menos = lab[0], lab[-1]
    preguntas = [
        (f"¿Cuántos días laborables tiene {a}?",
         f"{a} tiene {total} días de lunes a viernes. Descontando los festivos nacionales y autonómicos que caen entre semana, quedan entre "
         f"{menos[0]} y {mas[0]} según la comunidad, y a eso hay que restar las dos fiestas locales de cada municipio si caen entre semana."),
        (f"¿Qué comunidad tiene más días laborables en {a}?",
         (lambda top: f"Con los festivos nacionales y autonómicos, {escape(top[0])} es la que más tiene" if len(top) == 1 else
          f"Con los festivos nacionales y autonómicos, las que más tienen son {escape(', '.join(top[:-1]))} y {escape(top[-1])}")(
             [nombre(c) for n, c, _ in lab if n == mas[0]]) + f": {mas[0]} días de lunes a viernes."),
    ]
    cuerpo = f"""<h1>Días laborables de {a} en cada comunidad autónoma</h1>
<p class="lead">{a} tiene {total} días de lunes a viernes. Según cuántos festivos caigan entre semana en tu comunidad, te quedan entre {menos[0]} y {mas[0]} días laborables, antes de restar las fiestas locales.</p>
<section class="contenido"><h2>La tabla</h2>
<p>Días de lunes a viernes de {a}, menos los festivos nacionales y autonómicos que caen entre semana, según la <a href="{boe[a]['url']}" rel="noopener">resolución del BOE</a>:</p>
<div class="tabla-envoltorio"><table class="festivos completa"><thead><tr><th>Comunidad</th><th>Días laborables (lunes a viernes)</th><th>Festivos entre semana</th></tr></thead><tbody>{filas}</tbody></table></div>
<p>A estas cifras hay que restar las dos fiestas locales de tu municipio si caen entre semana. Para el cálculo exacto de tu pueblo o ciudad, entre las fechas que quieras, usa la <a href="/calculadora-dias-laborables/">calculadora de días laborables</a>.</p></section>
<section class="contenido"><h2>Por qué cambia de una comunidad a otra</h2>
<p>Las comunidades pueden sustituir algunas fiestas nacionales por otras propias y decidir si el lunes siguiente a un festivo que cae en domingo es festivo. Además, si una fiesta cae en sábado o domingo no resta ningún día laborable. Por eso el número de días de trabajo no es igual en todas. Lo explicamos en <a href="/guias/como-se-fijan-los-festivos/">cómo se deciden los festivos</a>.</p></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{faq_html(preguntas)}</section>
{fuente((f"BOE, fiestas laborales {a}", boe[a]["url"]))}"""
    guias.append((f"/guias/dias-laborables-{a}/", f"Días laborables de {a} en cada comunidad autónoma",
                  f"Cuántos días laborables tiene {a} en cada comunidad autónoma, con los festivos nacionales y autonómicos que caen entre semana.",
                  cuerpo, preguntas, f"Días laborables {a}"))

    # ------------------------------------------------------------ índice y páginas
    rutas = []
    tarjetas = ""
    for ruta, titulo, desc, cuerpo, preguntas, corto in guias:
        guardar(ruta, pagina(ruta, titulo, desc, f'<article class="guia">{cuerpo}</article>',
                             migas=[("Guías", "/guias/"), (corto, None)], extra_ld=[faq_ld(preguntas)]))
        rutas.append(ruta)
        tarjetas += f'<li><a href="{ruta}"><strong>{escape(corto)}</strong><span>{escape(desc)}</span></a></li>'
    indice = f"""<h1>Guías sobre festivos y calendario laboral</h1>
<p class="lead">Respuestas claras a las dudas más habituales sobre festivos, vacaciones y plazos, con la norma oficial enlazada en cada caso.</p>
<ul class="guias">{tarjetas}</ul>"""
    guardar("/guias/", pagina("/guias/", "Guías sobre festivos, vacaciones y calendario laboral | festivosde.es",
                              "Qué pasa si un festivo cae en domingo, cuánto se cobra por trabajar un festivo, cuántos días de vacaciones te corresponden y más.",
                              indice, migas=[("Guías", None)]))
    return ["/guias/"] + rutas


def sobre_datos(datos, anios, comunidades, provincias, cfg, municipios, pagina, guardar):
    """Página de transparencia: fuentes oficiales por comunidad, cobertura real y método. Se recalcula en cada generación."""
    total = len(municipios)
    por_cc = {}
    for cod in municipios:
        por_cc.setdefault(provincias[cod[:2]][1], []).append(cod)
    filas = ""
    for c in sorted(por_cc, key=lambda c: comunidades[c][0]):
        celdas = ""
        for a in anios:
            con = sum(1 for cod in por_cc[c] if cod in datos[a]["locales"])
            sin = sum(1 for cod in por_cc[c] if cod in set(datos[a].get("sin_propuesta", [])))
            celdas += f"<td>{con} de {len(por_cc[c])}" + (f"<br><small>{sin} sin fiestas propuestas</small>" if sin else "") + "</td>"
        enlaces = []
        for f in cfg["locales"]:
            if f["ccaa"] != c or f["anio"] not in anios:
                continue
            url = f.get("oficial") or f.get("descarga")
            if not url:
                continue
            etq = str(f["anio"])
            if f.get("provincia"):
                etq += f", {provincias[f['provincia']][0]}"
            if f.get("tipo") in ("correccion", "complementaria"):
                etq += ", corrección" if f["tipo"] == "correccion" else ", complemento"
            enlaces.append(f'<a href="{escape(url)}" rel="nofollow noopener">{escape(etq)}</a>')
        filas += (f'<tr><td><a href="/comunidad/{c}/">{escape(comunidades[c][0])}</a></td>{celdas}'
                  f'<td>{" · ".join(enlaces) if enlaces else "Pendiente de publicación"}</td></tr>')
    resumen = []
    for a in anios:
        con = len(datos[a]["locales"])
        resumen.append(f"<li><strong>{a}:</strong> {con} de {total} municipios con sus dos fiestas locales publicadas"
                       + (f"; en {len(datos[a].get('sin_propuesta', []))} la resolución oficial dice que el ayuntamiento no las propuso" if datos[a].get("sin_propuesta") else "")
                       + f". Fiestas nacionales y autonómicas: <a href=\"{datos[a]['boe']['url']}\" rel=\"noopener\">{escape(datos[a]['boe']['titulo'])}</a></li>")
    cuerpo = f"""<h1>De dónde salen los datos</h1>
<p class="lead">Todos los festivos de festivosde.es salen de publicaciones oficiales: el Boletín Oficial del Estado y los boletines de cada comunidad autónoma y provincia. Aquí explicamos cuáles usamos, cómo los procesamos y qué datos tenemos ahora mismo.</p>
<section class="contenido"><h2>Las fuentes</h2>
<ul><li><strong>Fiestas nacionales y autonómicas:</strong> la resolución anual de la Dirección General de Trabajo con la relación de fiestas laborales de toda España, publicada en el BOE en otoño del año anterior.</li>
<li><strong>Fiestas locales:</strong> las resoluciones u órdenes de cada comunidad autónoma (o de cada provincia, en Castilla y León y el País Vasco) con las dos fiestas locales de cada municipio, y sus correcciones posteriores.</li>
<li><strong>Calendario escolar:</strong> las resoluciones de las consejerías de educación de cada comunidad.</li>
<li><strong>Municipios:</strong> la relación de municipios del Instituto Nacional de Estadística (INE), con su código oficial.</li></ul></section>
<section class="contenido"><h2>Qué datos tenemos ahora</h2>
<ul>{"".join(resumen)}</ul>
<p>Detalle por comunidad, con el enlace a cada boletín oficial que usamos:</p>
<div class="tabla-envoltorio"><table class="festivos completa"><thead><tr><th>Comunidad</th>{"".join(f"<th>Fiestas locales {a}</th>" for a in anios)}<th>Boletines oficiales</th></tr></thead><tbody>{filas}</tbody></table></div>
<p class="fuente">Datos comprobados por última vez el {(lambda h: f"{h.day} de {MESES[h.month - 1]} de {h.year}")(dt.date.today())}.</p></section>
<section class="contenido"><h2>Cómo lo hacemos</h2>
<ol><li>Un programa revisa a diario los boletines oficiales y descarga las resoluciones de fiestas en cuanto se publican.</li>
<li>Extrae de cada resolución el nombre de cada municipio y sus dos fechas, y lo cruza con la relación de municipios del INE para asignar cada fiesta al municipio correcto, también cuando el boletín escribe el nombre de otra forma («Prat de Llobregat, El», «A Coruña», nombres bilingües…).</li>
<li>Aplica las correcciones que publican después los propios boletines («donde dice…, debe decir…»).</li>
<li>Cuando un boletín publica la lista como imagen escaneada, la transcribimos y revisamos fila a fila, y dejamos constancia de cualquier errata del original.</li>
<li>Comprobamos cada actualización comparándola con la anterior para que ningún municipio pierda datos por error.</li></ol>
<p><strong>Nunca ponemos una fecha que no esté publicada.</strong> Si las fiestas locales de un municipio no aparecen en su resolución, lo decimos en su página en lugar de suponerlas.</p></section>
<section class="contenido"><h2>Limitaciones</h2>
<ul><li>Algunas fiestas son solo de una pedanía, una parroquia o un núcleo concreto (por ejemplo, en Navarra, el Valle de Arán o Asturias). Mostramos las del municipio y avisamos cuando hay fiestas que no son para todo el término.</li>
<li>En Canarias hay fiestas propias de cada isla, que el BOE indica en nota y nosotros también.</li>
<li>Los convenios colectivos pueden añadir días de descanso propios de un sector o una empresa: no forman parte del calendario oficial y no aparecen aquí.</li>
<li>Para trámites legales o laborales importantes, consulta siempre la publicación oficial enlazada.</li></ul></section>
<section class="contenido"><h2>¿Has visto un error?</h2>
<p>Si una fecha no coincide con lo que ha aprobado tu ayuntamiento o falta tu municipio, escríbenos desde la página de <a href="/contacto/">contacto</a> indicando el municipio y, si puedes, el boletín donde lo has visto. Lo revisamos con la publicación oficial y lo corregimos.</p></section>"""
    guardar("/sobre-los-datos/", pagina("/sobre-los-datos/", "De dónde salen los datos de festivos | festivosde.es",
                                        "Las fuentes oficiales de festivosde.es (BOE y boletines de cada comunidad), cómo las procesamos y cuántos municipios tienen ya sus fiestas locales.",
                                        cuerpo, migas=[("De dónde salen los datos", None)]))
