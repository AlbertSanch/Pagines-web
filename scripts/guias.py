"""Genera las guías de ahorrometro (ahorrometro/guias/) con las cifras calculadas a partir de los datos de la web.

Las guías explican a fondo un tema (la factura de la luz, la calefacción, gasolina o diésel…) y hacen
las cuentas con los mismos datos y supuestos que las calculadoras:
  - ahorrometro/datos/luz.json        precio medio de la luz (Red Eléctrica, PVPC con impuestos)
  - ahorrometro/datos/carburantes.json precios de los carburantes (Ministerio)
  - ahorrometro/datos/butano.json      precio oficial de la bombona (BOE)
Crea una página por guía, el índice ahorrometro/guias/index.html y las entradas del sitemap entre
<!-- GUIAS:INICIO --> y <!-- GUIAS:FIN -->. Se ejecuta en el workflow de precios para que las cifras
sigan al día. La cabecera y el pie se copian de calculadoras/coste-viaje-coche.html.

Uso: python scripts/guias.py
"""

import json
import re
from datetime import date
from html import escape
from pathlib import Path

from paginas_consumo import WEB, DOMINIO, eur, num, plantilla_base, precio_luz, reemplazar_bloque

CARPETA = "guias"
AUTOR = "Albert Sanchez"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def leer(nombre):
    return json.loads((WEB / "datos" / nombre).read_text(encoding="utf-8"))


def fecha_larga(iso):
    a, m, d = (int(x) for x in iso[:10].split("-"))
    return f"{d} de {MESES[m - 1]} de {a}"


def c(x, dec=2):
    return num(x, dec)


def tabla(cabecera, filas, num_desde=1):
    """cabecera: lista de títulos; filas: listas de celdas (las columnas desde num_desde van a la derecha)."""
    cl = lambda i: ' class="num"' if i >= num_desde else ""  # noqa: E731
    th = "".join(f"<th{cl(i)}>{h}</th>" for i, h in enumerate(cabecera))
    tr = "".join("<tr>" + "".join(f"<td{cl(i)}>{v}</td>" for i, v in enumerate(f)) + "</tr>" for f in filas)
    return f'<div class="table-wrap"><table class="data"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


# ---------------------------------------------------------------- datos comunes
def contexto():
    luz, desde, hasta = precio_luz()
    dl = leer("luz.json")
    valle = dl.get("conImpuestos", {}).get("valle")
    carb = leer("carburantes.json")
    but = leer("butano.json")["historial"]
    luz_sin = dl.get("sinImpuestos", {}).get("media") or luz / 1.21 / 1.0511269632
    return dict(luz=luz, luz_sin=luz_sin, valle=valle, luz_desde=desde, luz_hasta=hasta, carb=carb,
                butano=but[0]["precio"], butano_desde=but[0]["desde"], butano_ant=but[1]["precio"] if len(but) > 1 else None)


# ---------------------------------------------------------------- guía 1: factura de la luz
def guia_factura(x):
    p, v = x["luz"], x["valle"]
    # Ejemplo de factura mensual de un hogar medio (estimación con supuestos explícitos)
    kw, precio_kw, kwh = 3.45, 32, 250
    potencia = kw * precio_kw / 12
    energia = kwh * x["luz_sin"]  # precio del kWh sin impuestos: los impuestos van en sus propias líneas
    ie = (potencia + energia) * 0.0511269632
    contador = 0.81
    base = potencia + energia + ie + contador
    iva = base * 0.21
    total = base + iva
    filas = [
        ["Término de potencia", f"{c(kw)} kW × {precio_kw} €/kW al año ÷ 12", eur(potencia)],
        ["Término de energía", f"{kwh} kWh × {c(energia / kwh, 3)} €/kWh", eur(energia)],
        ["Impuesto sobre la electricidad", "5,11 % de potencia + energía", eur(ie)],
        ["Alquiler del contador", "contador digital monofásico", eur(contador)],
        ["IVA", "21 % de todo lo anterior", eur(iva)],
        ["<strong>Total</strong>", "", f"<strong>{eur(total)}</strong>"],
    ]
    ahorro_valle = (p - v) * 100 if v else None
    cuerpo = f"""
<p class="lead">La factura de la luz parece complicada, pero solo tiene cinco partes. En esta guía te explicamos qué es cada una, cuánto pesa en un recibo normal y en cuáles puedes ahorrar de verdad.</p>

<h2>Resumen rápido</h2>
<ul>
  <li><strong>Pagas por dos cosas:</strong> por la potencia que tienes contratada (aunque no gastes nada) y por la energía que consumes (los kWh).</li>
  <li><strong>Encima van dos impuestos:</strong> el impuesto sobre la electricidad (5,11 %) y el IVA (21 %).</li>
  <li><strong>Dónde se ahorra:</strong> bajando la potencia si te sobra, gastando menos kWh y moviendo consumos a las horas baratas.</li>
</ul>

<h2>Un recibo de ejemplo, línea a línea</h2>
<p>Este es el recibo aproximado de un mes para un piso con <strong>{c(kw)} kW contratados</strong> que gasta <strong>{kwh} kWh al mes</strong>, con el precio medio de la tarifa regulada (PVPC) de las últimas semanas: {c(p, 3)} €/kWh con impuestos.</p>
{tabla(["Concepto", "Cómo se calcula", "Importe"], filas, num_desde=2)}
<p class="note">Es una estimación para que veas el peso de cada parte. Tu recibo cambia según tu potencia, tu consumo, tu tarifa y el precio de cada hora. El precio de la potencia (unos 30–45 €/kW al año sumando los dos periodos) y el del contador son orientativos.</p>
<p>Fíjate en que <strong>la energía es la parte más grande</strong>, pero la potencia es un coste fijo: la pagas igual aunque estés un mes fuera de casa.</p>

<h2>1. El término de potencia</h2>
<p>La potencia contratada es la cantidad de electricidad que puedes usar <em>a la vez</em>, en kilovatios (kW). Si enciendes el horno, la lavadora y el secador al mismo tiempo y pasas de esa potencia, salta el limitador (el ICP).</p>
<p>En la tarifa doméstica (la 2.0TD, para potencias de hasta 15 kW) se contratan dos potencias: una para las horas punta y llano y otra para el valle (la noche y los fines de semana). Puedes contratar más en el valle si, por ejemplo, cargas un coche eléctrico por la noche.</p>
<p><strong>Cómo ahorrar:</strong> muchas casas tienen más potencia de la que necesitan. Cada kW de menos ahorra unos 30–45 € al año sin cambiar nada más. Con nuestra <a href="../calculadoras/potencia-contratada">calculadora de potencia contratada</a> puedes ver cuánta necesitas según los aparatos que usas a la vez.</p>

<h2>2. El término de energía</h2>
<p>Es lo que pagas por cada kilovatio hora (kWh) que gastas. Un kWh es, por ejemplo, tener encendido un aparato de 1.000 W durante una hora.</p>
<p>El precio del kWh no es igual todo el día. En la tarifa doméstica hay tres periodos:</p>
{tabla(["Periodo", "De lunes a viernes", "Precio"], [
        ["Punta", "10:00–14:00 y 18:00–22:00", "El más caro"],
        ["Llano", "8:00–10:00, 14:00–18:00 y 22:00–24:00", "Intermedio"],
        ["Valle", "0:00–8:00, y todo el día los fines de semana y festivos nacionales", "El más barato"],
    ], num_desde=9)}
<p>Si tienes la tarifa regulada (PVPC), además el precio cambia cada hora según el mercado. Puedes ver el de hoy en nuestra página del <a href="../precio-luz-hoy">precio de la luz hoy</a>.{f' En las últimas semanas, el valle ha salido de media a {c(v, 3)} €/kWh con impuestos, unos {c(ahorro_valle, 1)} céntimos menos que la media del día.' if ahorro_valle and ahorro_valle > 0 else ''}</p>
<p><strong>Cómo ahorrar:</strong> gastar menos kWh (mira <a href="../consumo-electrodomesticos">cuánto gasta cada electrodoméstico</a>) y poner la lavadora, el lavavajillas o la secadora en las horas baratas.</p>

<h2>3. El impuesto sobre la electricidad</h2>
<p>Es un impuesto especial del 5,11 % que se aplica sobre la suma de la potencia y la energía. No se puede evitar, pero baja solo cuando bajan las otras dos partes.</p>

<h2>4. El alquiler del contador</h2>
<p>Casi todos los contadores de las casas son de la distribuidora, que cobra un pequeño alquiler: menos de 1 € al mes en un contador digital normal. Si el contador fuera tuyo, no deberías pagar esta línea.</p>

<h2>5. El IVA</h2>
<p>Se aplica el 21 % sobre todo lo anterior, incluido el impuesto sobre la electricidad.</p>

<h2>Tarifa regulada (PVPC) o mercado libre</h2>
<ul>
  <li><strong>PVPC (tarifa regulada):</strong> solo para potencias de hasta 10 kW. El precio cambia cada hora. Suele salir bien de media, sobre todo si puedes mover consumos a las horas baratas, pero hay meses caros.</li>
  <li><strong>Mercado libre:</strong> cada compañía pone sus precios, normalmente fijos durante un año. Da tranquilidad, pero hay que comparar bien: el precio del kWh y el de la potencia cambian mucho de una oferta a otra.</li>
</ul>
<p>Para comparar dos ofertas, multiplica tus kWh y tu potencia de los últimos 12 meses (vienen en la factura o en la web de tu distribuidora) por los precios de cada una. Así ves cuál te sale más barata con tu consumo real, no con el de un anuncio.</p>

<h2>Las cinco formas de ahorrar que más se notan</h2>
<ol>
  <li><strong>Ajusta la potencia</strong> si nunca te salta el limitador: unos 30–45 € al año por cada kW.</li>
  <li><strong>Revisa la calefacción y el agua caliente eléctricas</strong>, que son lo que más gasta en invierno: mira <a href="calefaccion-mas-barata-comparativa">qué calefacción sale más barata</a>.</li>
  <li><strong>Lava en frío o a 30 °C</strong>: la lavadora gasta casi todo en calentar el agua.</li>
  <li><strong>Apaga los aparatos en espera</strong>: mira cuánto suman con la calculadora de <a href="../calculadoras/consumo-fantasma">consumo fantasma</a>.</li>
  <li><strong>Usa las horas valle</strong> para todo lo que se pueda programar.</li>
</ol>
<p>Tienes más ideas, con números, en la guía de <a href="como-bajar-la-factura-de-la-luz">cómo bajar la factura de la luz</a>.</p>
"""
    faq = [
        ("¿Qué partes tiene la factura de la luz?",
         "Término de potencia (lo que pagas por los kW contratados), término de energía (los kWh que gastas), impuesto sobre la electricidad (5,11 %), alquiler del contador e IVA (21 %)."),
        ("¿Por qué pago luz aunque no gaste nada?",
         "Porque el término de potencia y el alquiler del contador son fijos: los pagas por tener la luz contratada, gastes o no."),
        ("¿Cuáles son las horas más baratas de la luz?",
         "En la tarifa doméstica, el valle: de 0:00 a 8:00 de lunes a viernes y todo el día los fines de semana y festivos nacionales."),
        ("¿Cuánto se ahorra bajando la potencia contratada?",
         "Unos 30–45 € al año por cada kW, según la compañía. Comprueba antes que no te va a saltar el limitador con los aparatos que usas a la vez."),
    ]
    return cuerpo, faq


# ---------------------------------------------------------------- guía 2: calefacción
def guia_calefaccion(x):
    p = x["luz"]
    m2, zona, aisl = 80, 75, 1.0
    demanda = m2 * zona * aisl
    pr = dict(gas=0.07, pellet=0.32, gasoleo=1.05, butano=x["butano"], scop=3.5)
    sistemas = [
        ("Bomba de calor / aerotermia", demanda / pr["scop"] * p, f"{c(pr['scop'], 1)} kWh de calor por kWh de luz", "../cuanto-gasta/bomba-de-calor"),
        ("Gas natural", demanda / 0.92 * pr["gas"], f"{c(pr['gas'], 2)} €/kWh, caldera del 92 %", None),
        ("Pellets", demanda / 0.9 / 4.8 * pr["pellet"], f"{c(pr['pellet'], 2)} €/kg, estufa del 90 %", "../calculadoras/sacos-pellets"),
        ("Gasóleo", demanda / 0.9 / 10 * pr["gasoleo"], f"{c(pr['gasoleo'], 2)} €/L, caldera del 90 %", None),
        ("Butano", demanda / 0.95 / (12.5 * 12.87) * pr["butano"], f"bombona a {eur(pr['butano'])}", "../calculadoras/duracion-bombona-butano"),
        ("Radiadores eléctricos", demanda * p, f"{c(p, 3)} €/kWh", "../calculadoras/radiador-electrico"),
    ]
    sistemas.sort(key=lambda s: s[1])
    barato, caro = sistemas[0], sistemas[-1]
    filas = [[f'<a href="{u}">{n}</a>' if u else n, d, eur(v), eur(v / 5)] for n, v, d, u in sistemas]
    cuerpo = f"""
<p class="lead">¿Bomba de calor, gas, pellets, butano o radiadores eléctricos? Hemos hecho las cuentas para una casa normal con los precios actuales de la energía. La diferencia entre el sistema más barato y el más caro puede pasar de los {c((caro[1] - barato[1]) // 100 * 100, 0)} € al año.</p>

<h2>El resultado: coste de un invierno</h2>
<p>Piso de <strong>{m2} m²</strong> en clima medio (Madrid, interior peninsular, valle del Ebro), con un aislamiento normal. Necesita unos <strong>{c(demanda, 0)} kWh de calor</strong> en todo el invierno. Esto es lo que cuesta producir ese calor con cada sistema:</p>
{tabla(["Sistema", "Precio y rendimiento usados", "Al año", "Al mes*"], filas, num_desde=2)}
<p class="note">* Repartido en 5 meses de calefacción. Solo cuenta la energía: no incluye la instalación, el mantenimiento ni los costes fijos (por ejemplo, el término fijo del gas). Luz: media de la tarifa regulada con impuestos de las últimas semanas. Butano: precio máximo oficial vigente. Gas natural, pellets y gasóleo: precios medios orientativos; cámbialos por los tuyos en la <a href="../calculadoras/calefaccion-mas-barata">calculadora de calefacción</a>.</p>

<h2>Por qué la bomba de calor sale tan barata</h2>
<p>Un radiador eléctrico convierte 1 kWh de luz en 1 kWh de calor. Una bomba de calor (un aire acondicionado con modo calor o una aerotermia) usa ese kWh para «mover» calor del aire de fuera hacia dentro, y da entre 3 y 4 kWh de calor. Por eso, con la misma luz, calienta tres o cuatro veces más.</p>
<p>Si ya tienes un split con bomba de calor, usarlo para calentar es casi siempre lo más barato. Su punto débil es que calienta el aire y no las paredes, y que en climas muy fríos rinde algo menos.</p>

<h2>Gas natural y pellets: los siguientes</h2>
<p>El gas natural y los pellets quedan cerca entre sí. El gas tiene la ventaja de la comodidad y la desventaja del término fijo mensual, que se paga todo el año. Los pellets necesitan una estufa o caldera específica, espacio para guardar los sacos y algo de limpieza, pero su precio es estable. Si estás pensando en pellets, calcula <a href="../calculadoras/sacos-pellets">cuántos sacos necesitarías</a>.</p>

<h2>Butano: barato de instalar, caro de usar</h2>
<p>Una estufa de butano cuesta poco y no necesita obra, por eso es tan común. Pero el calor del butano sale bastante más caro que el de una bomba de calor. Además, hay que ventilar la habitación y no se debe usar en dormitorios mientras se duerme. Compara tu caso con la calculadora de <a href="../calculadoras/estufa-butano-o-electrica">estufa de butano o eléctrica</a> y mira el <a href="../precio-bombona-butano">precio de la bombona hoy</a>.</p>

<h2>Radiadores eléctricos: solo para ratos cortos</h2>
<p>Son el sistema más caro si calientan toda la casa durante muchas horas. Tienen sentido para calentar una habitación pequeña un rato, o en zonas templadas donde la calefacción se usa poco. Para eso, un radiador de aceite con termostato o una <a href="../calculadoras/manta-electrica-o-calefaccion">manta eléctrica</a> son mucho más baratos que calentar toda la casa.</p>

<h2>Cómo cambia el resultado según tu casa</h2>
<ul>
  <li><strong>Clima:</strong> en la costa mediterránea la demanda puede ser la mitad, y en el norte o en zonas de montaña, un tercio más.</li>
  <li><strong>Aislamiento:</strong> una casa antigua con ventanas simples puede necesitar un 40 % más de calor que una normal; una nueva o reformada, un 40 % menos.</li>
  <li><strong>Termostato:</strong> cada grado de menos ahorra alrededor de un 7 %. Calcúlalo con la <a href="../calculadoras/bajar-temperatura-calefaccion">calculadora de ahorro por grado</a>.</li>
</ul>

<h2>¿Compensa cambiar de sistema?</h2>
<p>Depende de lo que cueste el cambio y de lo que gastes ahora. En este piso, pasar de radiadores eléctricos a bomba de calor ahorra unos {eur(demanda * p - demanda / pr['scop'] * p)} al año: un aire acondicionado con bomba de calor se paga en pocos inviernos. En cambio, sustituir una caldera de gas que funciona bien por una aerotermia, que es mucho más cara de instalar, ahorra solo {eur(demanda / 0.92 * pr['gas'] - demanda / pr['scop'] * p)} al año y puede tardar muchos años en compensar.</p>
"""
    faq = [
        ("¿Cuál es la calefacción más barata?",
         f"Con los precios actuales, la bomba de calor: unos {eur(barato[1])} al año para un piso de 80 m² en clima medio, frente a {eur(caro[1])} con radiadores eléctricos."),
        ("¿Es más barato el butano o la luz para calentar?",
         "El butano es más barato que un radiador eléctrico normal, pero bastante más caro que una bomba de calor (un aire acondicionado con modo calor)."),
        ("¿Cuánto se ahorra bajando un grado la calefacción?",
         "Alrededor de un 7 % del gasto de calefacción por cada grado."),
    ]
    return cuerpo, faq


# ---------------------------------------------------------------- guía 3: gasolina o diésel
def guia_gasolina_diesel(x):
    e = x["carb"]["espana"]
    g, d = e["gasolina95"]["media"], e["diesel"]["media"]
    cg, cd = 6.5, 5.0  # L/100 km de un coche compacto
    km_g, km_d = g * cg / 100, d * cd / 100
    filas = []
    for km in (10000, 15000, 20000, 30000):
        filas.append([f"{c(km, 0)} km", eur(km * km_g), eur(km * km_d), eur(km * (km_g - km_d))])
    dif = km_g - km_d
    provs = [v for v in x["carb"]["provincias"].values() if "gasolina95" in v and "diesel" in v]
    mas_barata = min(provs, key=lambda v: v["gasolina95"]["media"])
    mas_cara = max(provs, key=lambda v: v["gasolina95"]["media"])
    fecha = x["carb"]["fechaMinisterio"].split(" ")[0]
    dd, mm, aa = fecha.split("/")
    fecha = f"{int(dd)} de {MESES[int(mm) - 1]} de {aa}"
    sobrecoste = 2000
    cuerpo = f"""
<p class="lead">El diésel gasta menos litros, pero no siempre sale más barato. Con los precios de hoy y el consumo real de cada coche, te explicamos cuándo compensa cada uno y cuántos kilómetros hacen falta para recuperar lo que cuesta de más un diésel.</p>

<h2>Precios de hoy</h2>
<p>Media de España el {fecha}, según el Ministerio para la Transición Ecológica:</p>
{tabla(["Combustible", "Precio medio"], [["Gasolina 95", f"{c(g, 3)} €/L"], ["Diésel", f"{c(d, 3)} €/L"]])}
<p>{'Ahora mismo el diésel es más caro por litro que la gasolina, algo que antes era al revés.' if d > g else 'Ahora mismo el diésel es más barato por litro que la gasolina.'} Puedes ver los precios de tu provincia en <a href="../precio-gasolina-hoy">precio de la gasolina hoy</a>: la gasolina 95 está más barata en {escape(mas_barata['nombre'])} ({c(mas_barata['gasolina95']['media'], 3)} €/L) y más cara en {escape(mas_cara['nombre'])} ({c(mas_cara['gasolina95']['media'], 3)} €/L). Canarias, Ceuta y Melilla suelen ser las más baratas porque allí los carburantes pagan menos impuestos.</p>

<h2>Lo que de verdad importa: el coste por kilómetro</h2>
<p>Un diésel gasta menos litros para recorrer lo mismo. Para un coche compacto, unos valores realistas son <strong>{c(cg, 1)} L/100 km en gasolina</strong> y <strong>{c(cd, 1)} L/100 km en diésel</strong>. Con los precios de hoy:</p>
<ul>
  <li>Gasolina: {c(cg, 1)} L × {c(g, 3)} € = <strong>{eur(km_g * 100)} cada 100 km</strong></li>
  <li>Diésel: {c(cd, 1)} L × {c(d, 3)} € = <strong>{eur(km_d * 100)} cada 100 km</strong></li>
</ul>
<p>{'El diésel sale más barato por kilómetro' if dif > 0 else 'La gasolina sale más barata por kilómetro'}: {c(abs(dif) * 100, 2)} € cada 100 km. Esto es lo que gastarías al año:</p>
{tabla(["Kilómetros al año", "Gasolina", "Diésel", "Diferencia"], filas)}

<h2>¿Cuántos kilómetros para recuperar el diésel?</h2>
<p>Un coche diésel suele costar más que el mismo modelo de gasolina. Si la diferencia fuera, por ejemplo, de {c(sobrecoste, 0)} €, {f'harían falta <strong>unos {c(round(sobrecoste / dif, -2), 0)} km</strong> para recuperarla solo con el combustible: unos {c(sobrecoste / dif / 15000, 1)} años haciendo 15.000 km al año.' if dif > 0 else 'no se recuperaría nunca, porque con los precios actuales el diésel ni siquiera es más barato por kilómetro.'}</p>
<p>Por eso la regla de siempre sigue valiendo: <strong>el diésel solo compensa si haces muchos kilómetros</strong>, sobre todo por carretera.</p>

<h2>Otras cosas que cuentan</h2>
<ul>
  <li><strong>Etiqueta ambiental:</strong> un gasolina tiene etiqueta C desde 2006, pero un diésel solo desde septiembre de 2015. Con las zonas de bajas emisiones, esto puede decidir si puedes entrar en el centro de tu ciudad. Comprueba la tuya con la <a href="../calculadoras/etiqueta-ambiental-dgt">calculadora de etiqueta de la DGT</a>.</li>
  <li><strong>Trayectos cortos:</strong> los diésel modernos llevan filtro de partículas, que necesita trayectos largos para limpiarse. Si casi todo es ciudad, el gasolina o un híbrido dan menos problemas.</li>
  <li><strong>Mantenimiento:</strong> un diésel moderno suele tener averías más caras (inyectores, filtro de partículas, válvula EGR).</li>
  <li><strong>Valor de reventa:</strong> los diésel antiguos se venden peor que antes por las restricciones de circulación.</li>
</ul>

<h2>¿Y un eléctrico o un híbrido?</h2>
<p>Si puedes cargar en casa, un coche eléctrico gasta mucho menos por kilómetro: calcula cuánto te costaría con la calculadora de <a href="../calculadoras/cargar-coche-electrico">cargar un coche eléctrico</a>. Para ver el gasto total de un coche (seguro, impuestos, mantenimiento, depreciación), usa la de <a href="../calculadoras/coste-mantener-coche">cuánto cuesta mantener un coche</a>. Y para un viaje concreto, la de <a href="../calculadoras/coste-viaje-coche">coste de un viaje en coche</a>.</p>
"""
    faq = [
        ("¿Qué sale más barato, gasolina o diésel?",
         f"Con los precios de hoy, cada 100 km cuestan unos {eur(km_g * 100)} con un gasolina ({c(cg, 1)} L/100 km) y {eur(km_d * 100)} con un diésel ({c(cd, 1)} L/100 km). El diésel solo compensa si haces muchos kilómetros al año."),
        ("¿A partir de cuántos kilómetros compensa un diésel?",
         f"Depende de cuánto cueste de más el coche. Con {c(sobrecoste, 0)} € de diferencia y los precios actuales, " + (f"harían falta unos {c(round(sobrecoste / dif, -2), 0)} km para recuperarlos." if dif > 0 else "no se recuperarían nunca, porque el diésel no es más barato por kilómetro.")),
        ("¿Qué etiqueta de la DGT tiene un diésel?",
         "La C si se matriculó desde septiembre de 2015 (Euro 6), la B entre 2006 y agosto de 2015, y ninguna si es anterior a 2006."),
    ]
    return cuerpo, faq


# ---------------------------------------------------------------- guía 4: bajar la factura
def guia_bajar_luz(x):
    p, v = x["luz"], x["valle"]
    standby_w = 30
    standby = standby_w * 24 * 365 / 1000 * p
    led = (60 - 9) * 3 * 365 / 1000 * p
    pot = 1.15 * 32
    lav_40, lav_30 = 0.9, 0.5
    lavadora = (lav_40 - lav_30) * 4 * 52 * p
    term = (2000 * 4 * 0.6 / 1000) * 30 * 5 * p * 0.07  # radiador 2 kW, 4 h/día, 5 meses, un grado menos
    secadora = 4.0 * 3 * 52 * p
    valle_txt = ""
    if v and p > v:
        ahorro_valle = (p - v) * (15.6 + 21.7) * 12
        valle_txt = f"<p>Moviendo la lavadora y el lavavajillas (unos 37 kWh al mes entre los dos) a las horas valle, con la diferencia de precio de las últimas semanas ({c((p - v) * 100, 1)} céntimos por kWh), ahorrarías unos <strong>{eur(ahorro_valle)} al año</strong>. Es poco por sí solo, pero no cuesta nada: casi todos los aparatos tienen inicio diferido.</p>"
    cambios = [
        ("Bajar la potencia de 4,6 a 3,45 kW", pot, "Si nunca te salta el limitador"),
        ("Quitar 30 W de aparatos en espera", standby, "Regletas con interruptor"),
        ("Lavar a 30 °C en vez de a 40 °C (4 lavados/semana)", lavadora, "Detergente para baja temperatura"),
        ("Cambiar una bombilla de 60 W por un LED de 9 W (3 h/día)", led, "Por cada bombilla"),
        ("Tender en vez de usar la secadora (3 secados/semana)", secadora, "Cuando el tiempo lo permite"),
    ]
    filas = [[n, eur(a), como] for n, a, como in sorted(cambios, key=lambda t: -t[1])]
    cuerpo = f"""
<p class="lead">Hay muchos consejos para ahorrar luz, pero no todos ahorran lo mismo. Hemos calculado cuánto se ahorra de verdad con cada uno, con el precio medio actual de la luz ({c(p, 3)} €/kWh con impuestos), para que empieces por los que más se notan.</p>

<h2>Los cambios, ordenados por ahorro</h2>
{tabla(["Cambio", "Ahorro al año", "Cómo"], filas, num_desde=1)}
<p class="note">Estimaciones con el precio medio de la tarifa regulada de las últimas semanas. El ahorro de la potencia supone unos 32 €/kW al año. Calcula tu caso con las calculadoras enlazadas abajo.</p>

<h2>1. Revisa la potencia contratada</h2>
<p>Es el ahorro más fácil: se cambia con una llamada o desde la web de tu compañía y no tienes que hacer nada más. Si tienes 4,6 kW y nunca te salta el limitador, probablemente te basta con 3,45 kW, y te ahorras unos {eur(pot)} al año. Antes de bajarla, suma los aparatos que usas a la vez con la <a href="../calculadoras/potencia-contratada">calculadora de potencia contratada</a>.</p>

<h2>2. Apaga lo que está en espera</h2>
<p>La tele, el decodificador, la consola, el microondas con reloj, los altavoces inteligentes… Cada uno gasta poco, pero están encendidos las 24 horas. Si entre todos suman 30 W, que es fácil, son {c(standby_w * 24 * 365 / 1000, 0)} kWh al año, unos <strong>{eur(standby)}</strong>. Una regleta con interruptor lo soluciona. Haz la cuenta de tu casa con la calculadora de <a href="../calculadoras/consumo-fantasma">consumo fantasma</a>.</p>

<h2>3. Lava a menos temperatura</h2>
<p>La lavadora gasta casi todo en calentar el agua. Un lavado a 40 °C consume unos {c(lav_40, 1)} kWh y uno a 30 °C, alrededor de {c(lav_30, 1)} kWh. Con 4 lavados a la semana, bajar de 40 a 30 °C ahorra unos <strong>{eur(lavadora)} al año</strong>. Lavar en frío ahorra todavía más. Mira <a href="../cuanto-gasta/lavadora">cuánto gasta una lavadora</a>.</p>

<h2>4. La secadora, solo cuando haga falta</h2>
<p>Una secadora de condensación gasta unos 4 kWh por secado. Con 3 a la semana son <strong>{eur(secadora)} al año</strong>. Tender cuando se pueda, o centrifugar a más revoluciones antes de secar, reduce mucho el gasto. Compara con la calculadora de <a href="../calculadoras/secadora-o-tender">secadora o tender</a>.</p>

<h2>5. Pásate al LED</h2>
<p>Una bombilla LED de 9 W da la misma luz que una incandescente de 60 W. Si está encendida 3 horas al día, ahorras unos <strong>{eur(led)} al año por bombilla</strong>, y el LED cuesta pocos euros y dura años. Si ya tienes todo en LED, aquí no queda nada que ganar.</p>

<h2>6. Usa las horas baratas</h2>
{valle_txt or '<p>Las horas valle (de 0:00 a 8:00 y los fines de semana) suelen ser las más baratas. Programa allí la lavadora, el lavavajillas y la carga del coche eléctrico.</p>'}
<p>Puedes ver qué horas son más baratas hoy en el <a href="../precio-luz-hoy">precio de la luz hoy</a>.</p>

<h2>7. En invierno, la calefacción manda</h2>
<p>Si te calientas con electricidad, nada de lo anterior pesa tanto como la calefacción. Un radiador de 2.000 W usado 4 horas al día gasta unos 144 kWh al mes. Bajar un grado el termostato ahorra alrededor de un 7 %, unos {eur(term)} en un invierno con ese radiador. Pero el gran cambio es pasar a una bomba de calor: mira la guía de <a href="calefaccion-mas-barata-comparativa">qué calefacción sale más barata</a>.</p>

<h2>Lo que no ahorra tanto como parece</h2>
<ul>
  <li><strong>Desenchufar el cargador del móvil:</strong> sin el móvil conectado gasta menos de medio vatio, apenas unos céntimos al año.</li>
  <li><strong>Apagar y encender el aire acondicionado a cada rato:</strong> gasta más en volver a enfriar que manteniéndolo a una temperatura razonable.</li>
  <li><strong>Lavar a mano para ahorrar:</strong> fregar con agua caliente suele gastar más energía que un lavavajillas lleno en programa eco.</li>
</ul>
"""
    faq = [
        ("¿Qué es lo que más ahorra en la factura de la luz?",
         f"Si te calientas con electricidad, usar una bomba de calor en lugar de radiadores. Después, usar menos la secadora (unos {eur(secadora)} al año con 3 secados a la semana), apagar los aparatos en espera y ajustar la potencia contratada (unos {eur(pot)} al año por bajar de 4,6 a 3,45 kW)."),
        ("¿Cuánto gastan los aparatos en espera?",
         f"Si entre todos suman 30 W, unos {c(standby_w * 24 * 365 / 1000, 0)} kWh al año: alrededor de {eur(standby)} con el precio medio de la luz."),
        ("¿Se ahorra lavando en frío?",
         "Sí. La lavadora gasta casi todo en calentar el agua, así que lavar a 30 °C o en frío reduce mucho su consumo."),
    ]
    return cuerpo, faq


# ---------------------------------------------------------------- guía 5: bombona de butano
def guia_butano(x):
    precio, ant = x["butano"], x["butano_ant"]
    kwh_bomb = 12.5 * 12.87
    eur_kwh = precio / kwh_bomb
    usos = [("Estufa a potencia baja", 1.4), ("Estufa a potencia media", 2.8), ("Estufa a potencia máxima", 4.2),
            ("Un fuego de la cocina", 1.8), ("Calentador de agua de 11 litros", 19)]
    filas = [[n, f"{c(kw, 1)} kW", f"{c(kwh_bomb / kw, 0)} h", eur(precio / (kwh_bomb / kw))] for n, kw in usos]
    var = f" En la revisión anterior costaba {eur(ant)}, así que {'subió' if precio > ant else 'bajó'} un {c(abs(precio / ant - 1) * 100, 1)} %." if ant else ""
    luz = x["luz"]
    cuerpo = f"""
<p class="lead">La bombona de butano sigue siendo la calefacción y el agua caliente de muchas casas. Te explicamos cómo se fija su precio, cuánto dura según el uso y cuándo sale más barata que la luz.</p>

<h2>Precio de la bombona hoy</h2>
<p>La bombona naranja de 12,5 kg cuesta como máximo <strong>{eur(precio)}</strong> en la Península y Baleares desde el {fecha_larga(x['butano_desde'])}, con impuestos incluidos.{var} Puedes ver el historial en la página del <a href="../precio-bombona-butano">precio de la bombona de butano</a>.</p>

<h2>Cómo se fija el precio</h2>
<p>El precio de la bombona de 12,5 kg está regulado: el Gobierno lo revisa cada dos meses y lo publica en el BOE. Las revisiones son el tercer martes de enero, marzo, mayo, julio, septiembre y noviembre. En cada revisión el precio puede subir o bajar como mucho un 5 %, para que no haya saltos bruscos.</p>
<p>El precio que se publica es el máximo: algunas distribuidoras pueden venderla más barata, pero no más cara. Las bombonas de otros tamaños, el propano y las botellas de camping no están reguladas.</p>

<h2>Cuánto dura una bombona</h2>
<p>Una bombona de 12,5 kg tiene unos <strong>{c(kwh_bomb, 0)} kWh</strong> de energía (cada kilo de butano da unos 12,9 kWh). Lo que dura depende de la potencia del aparato:</p>
{tabla(["Uso", "Potencia", "Horas que dura", "Coste por hora"], filas)}
<p class="note">Duración aproximada a potencia constante. Calcula tu caso, con tus horas al día, en la calculadora de <a href="../calculadoras/duracion-bombona-butano">cuánto dura una bombona</a>.</p>
<p>Por eso las duchas son lo que más bombonas gasta en una casa: un calentador consume en una hora lo mismo que una estufa a potencia media en casi siete.</p>

<h2>¿Butano o luz?</h2>
<p>Con el precio de hoy, el calor del butano sale a unos <strong>{c(eur_kwh, 3)} € por kWh</strong> (contando que la estufa aprovecha casi todo). La luz cuesta de media {c(luz, 3)} €/kWh. Por tanto:</p>
<ul>
  <li><strong>El butano es más barato que un radiador o un calefactor eléctrico</strong>, que convierten 1 kWh de luz en 1 kWh de calor.</li>
  <li><strong>Pero es más caro que una bomba de calor</strong> (un aire acondicionado con modo calor), que da 3 o 4 kWh de calor por cada kWh de luz: unos {c(luz / 3.5, 3)} € por kWh de calor.</li>
</ul>
<p>Compara las dos opciones para tu habitación con la calculadora de <a href="../calculadoras/estufa-butano-o-electrica">estufa de butano o eléctrica</a>, o mira todos los sistemas en la guía de <a href="calefaccion-mas-barata-comparativa">qué calefacción es más barata</a>.</p>

<h2>Seguridad con las estufas de butano</h2>
<ul>
  <li><strong>Ventila</strong> la habitación varias veces al día: la estufa consume oxígeno.</li>
  <li><strong>No la uses en dormitorios mientras duermes</strong>, ni en baños o espacios pequeños y cerrados.</li>
  <li><strong>Revisa la goma y el regulador:</strong> la goma lleva impresa su fecha de caducidad.</li>
  <li><strong>Pon un detector de monóxido de carbono</strong> si usas la estufa a menudo. Cuesta poco y puede salvar vidas.</li>
</ul>
"""
    faq = [
        ("¿Cuánto cuesta la bombona de butano?",
         f"El precio máximo de la bombona de 12,5 kg es de {eur(precio)} en la Península y Baleares desde el {fecha_larga(x['butano_desde'])}."),
        ("¿Cada cuánto cambia el precio del butano?",
         "Cada dos meses: el tercer martes de enero, marzo, mayo, julio, septiembre y noviembre. En cada revisión puede variar como mucho un 5 %."),
        ("¿Cuánto dura una bombona de butano con una estufa?",
         f"A potencia media (unos 2,8 kW), unas {c(kwh_bomb / 2.8, 0)} horas. A potencia máxima, unas {c(kwh_bomb / 4.2, 0)} horas."),
    ]
    return cuerpo, faq


GUIAS = [
    dict(slug="factura-de-la-luz-explicada", icono="🧾", funcion=guia_factura,
         titulo="Cómo entender la factura de la luz, línea a línea",
         h1="Cómo entender la factura de la luz",
         desc="Qué es el término de potencia, el de energía, los impuestos y el alquiler del contador, cuánto pesa cada uno en un recibo normal y dónde se puede ahorrar.",
         corto="Qué pagas en cada línea del recibo y dónde se ahorra."),
    dict(slug="calefaccion-mas-barata-comparativa", icono="🔥", funcion=guia_calefaccion,
         titulo="¿Qué calefacción es más barata? Comparativa con precios actuales",
         h1="¿Qué calefacción es más barata?",
         desc="Bomba de calor, gas natural, pellets, gasóleo, butano o radiadores eléctricos: cuánto cuesta calentar un piso todo el invierno con cada sistema, con los precios actuales.",
         corto="Bomba de calor, gas, pellets, butano y radiadores: el coste de un invierno."),
    dict(slug="gasolina-o-diesel", icono="⛽", funcion=guia_gasolina_diesel,
         titulo="¿Gasolina o diésel? Cuál sale más barato con los precios de hoy",
         h1="¿Gasolina o diésel? Cuál sale más barato",
         desc="Coste por kilómetro de un coche de gasolina y uno diésel con los precios de hoy, cuántos kilómetros hacen falta para que compense el diésel y qué más tener en cuenta.",
         corto="Coste por kilómetro con los precios de hoy y cuándo compensa el diésel."),
    dict(slug="como-bajar-la-factura-de-la-luz", icono="💡", funcion=guia_bajar_luz,
         titulo="Cómo bajar la factura de la luz: cuánto ahorra cada truco",
         h1="Cómo bajar la factura de la luz",
         desc="Potencia, aparatos en espera, lavadora, secadora, LED y horas valle: cuánto se ahorra de verdad con cada consejo, calculado con el precio actual de la luz.",
         corto="Los consejos para ahorrar luz, ordenados por lo que ahorran de verdad."),
    dict(slug="bombona-de-butano", icono="🧯", funcion=guia_butano,
         titulo="Bombona de butano: precio, cuánto dura y si sale a cuenta",
         h1="Bombona de butano: precio, duración y si compensa",
         desc="Cómo se fija el precio de la bombona de butano, cuántas horas dura con una estufa o un calentador y cuándo sale más barata que la luz.",
         corto="Cómo se fija su precio, cuánto dura y si sale más barata que la luz."),
]


def head(titulo, desc, url, ld, head_assets):
    e = escape
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#1f7a55">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Ahorrómetro">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{e(titulo)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{DOMINIO}/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {json.dumps(ld, ensure_ascii=False)}
  </script>
{head_assets}</head>
"""


def pagina_guia(g, x, base, hoy):
    head_assets, header, footer = base
    cuerpo, faq = g["funcion"](x)
    url = f"{DOMINIO}/{CARPETA}/{g['slug']}"
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": g["titulo"], "description": g["desc"],
         "url": url, "inLanguage": "es-ES", "author": {"@type": "Person", "name": "Albert Sanchez Guiu"},
         "publisher": {"@type": "Organization", "name": "Ahorrómetro", "url": DOMINIO + "/"},
         "image": f"{DOMINIO}/assets/og-image.png", "dateModified": hoy.isoformat()},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guías", "item": f"{DOMINIO}/{CARPETA}/"},
            {"@type": "ListItem", "position": 3, "name": g["h1"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]},
    ]
    faq_html = "".join(f"<details><summary>{escape(q)}</summary><p>{escape(r)}</p></details>" for q, r in faq)
    otras = "".join(f'<li><a href="{o["slug"]}">{o["icono"]} {escape(o["h1"])}</a></li>' for o in GUIAS if o is not g)
    return (head(g["titulo"], g["desc"], url, ld, head_assets) + header + f"""<main class="container">
  <nav class="breadcrumbs"><a href="../">Inicio</a> › <a href="./">Guías</a> › {escape(g['h1'])}</nav>
  <div class="layout">
    <article>
      <h1>{escape(g['h1'])}</h1>
      <p class="updated">Por {AUTOR} · Cifras actualizadas el {fecha_larga(hoy.isoformat())}</p>
      <div class="content">
{cuerpo}
        <h2>Preguntas frecuentes</h2>
        {faq_html}
        <h2>De dónde salen los datos</h2>
        <p>Los precios de la luz son la media de la tarifa regulada (PVPC) que publica Red Eléctrica; los de los carburantes, los del Ministerio para la Transición Ecológica; y el de la bombona de butano, el del BOE. Se actualizan solos cada día. Los consumos y rendimientos de los aparatos son valores típicos: para tu caso concreto, usa las calculadoras enlazadas. Más detalles en <a href="../sobre-nosotros">sobre nosotros</a>.</p>
      </div>
    </article>

    <aside class="sidebar">
      <div class="side-box">
        <h3>Otras guías</h3>
        <ul>{otras}</ul>
      </div>
    </aside>
  </div>
</main>

""" + footer + "</body>\n</html>\n")


def pagina_indice(base, hoy):
    head_assets, header, footer = base
    url = f"{DOMINIO}/{CARPETA}/"
    desc = "Guías para entender la factura de la luz, elegir la calefacción más barata, decidir entre gasolina y diésel y ahorrar en casa, con las cuentas hechas con precios actuales."
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Guías de ahorro", "url": url, "description": desc,
           "inLanguage": "es-ES"},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"},
              {"@type": "ListItem", "position": 2, "name": "Guías", "item": url}]}]
    tarjetas = "".join(f'<li><a href="{g["slug"]}"><strong>{g["icono"]} {escape(g["h1"])}</strong></a><br>{escape(g["corto"])}</li>' for g in GUIAS)
    return (head("Guías para ahorrar en casa | Ahorrómetro", desc, url, ld, head_assets) + header + f"""<main class="container" style="max-width:820px">
  <nav class="breadcrumbs"><a href="../">Inicio</a> › Guías</nav>
  <h1>Guías para ahorrar en casa</h1>
  <div class="content">
    <p class="lead">Explicaciones a fondo, con las cuentas hechas con los precios actuales de la luz, los carburantes y el butano. Para tu caso concreto, cada guía enlaza a las calculadoras.</p>
    <ul class="lista-guias">{tarjetas}</ul>
    <p class="updated">Cifras actualizadas el {fecha_larga(hoy.isoformat())}.</p>
  </div>
</main>

""" + footer + "</body>\n</html>\n")


def main():
    hoy = date.today()
    x = contexto()
    base = plantilla_base()
    carpeta = WEB / CARPETA
    carpeta.mkdir(exist_ok=True)
    for g in GUIAS:
        (carpeta / f"{g['slug']}.html").write_text(pagina_guia(g, x, base, hoy), encoding="utf-8")
    (carpeta / "index.html").write_text(pagina_indice(base, hoy), encoding="utf-8")
    entradas = [f'\n  <url><loc>{DOMINIO}/{CARPETA}/</loc><lastmod>{hoy}</lastmod><priority>0.9</priority></url>']
    entradas += [f'\n  <url><loc>{DOMINIO}/{CARPETA}/{g["slug"]}</loc><lastmod>{hoy}</lastmod><priority>0.9</priority></url>' for g in GUIAS]
    reemplazar_bloque(WEB / "sitemap.xml", "".join(entradas) + "\n  ", marca="GUIAS")
    print(f"{len(GUIAS)} guías en {carpeta}")


if __name__ == "__main__":
    main()
