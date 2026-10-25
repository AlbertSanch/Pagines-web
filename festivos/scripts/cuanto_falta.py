"""Fechas para las cuentas atrás de festivosde.es (/cuanto-falta/).

Solo fechas fijas, con regla conocida o calculadas con astronomía; nada que dependa de anuncios de empresas:
  - fijas: Navidad, Reyes, San Valentín…
  - con regla: Día de la Madre (primer domingo de mayo), Black Friday (viernes siguiente al cuarto jueves
    de noviembre), Semana Santa y Carnaval (a partir del Domingo de Pascua, cómputo gregoriano)
  - astronómicas: inicio de cada estación (longitud aparente del sol 0°, 90°, 180° y 270°, algoritmo de la
    NOAA basado en Meeus, error de pocos minutos) y cambio de hora (zona horaria Europe/Madrid)
"""
import datetime as dt
import math
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")


def pascua(anio):
    """Domingo de Pascua (algoritmo anónimo gregoriano, Meeus/Jones/Butcher)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(anio, mes, dia)


def enesimo(anio, mes, dia_semana, n):
    """n-ésimo día de la semana (0 = lunes) de un mes."""
    d = dt.date(anio, mes, 1)
    d += dt.timedelta(days=(dia_semana - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def black_friday(anio):
    return enesimo(anio, 11, 3, 4) + dt.timedelta(days=1)  # el día después del 4.º jueves de noviembre


def _longitud_sol(jd):
    """Longitud aparente del sol en grados (NOAA)."""
    t = (jd - 2451545.0) / 36525
    l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360
    m = math.radians(357.52911 + t * (35999.05029 - 0.0001537 * t))
    c = (math.sin(m) * (1.914602 - t * (0.004817 + 0.000014 * t)) + math.sin(2 * m) * (0.019993 - 0.000101 * t)
         + math.sin(3 * m) * 0.000289)
    return (l0 + c - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * t))) % 360


def estacion(anio, grados):
    """Momento (hora de Madrid) en que el sol llega a 0° (primavera), 90° (verano), 180° (otoño) o 270° (invierno)."""
    mes = {0: 3, 90: 6, 180: 9, 270: 12}[grados]
    ini = dt.datetime(anio, mes, 15, tzinfo=dt.timezone.utc)
    jd0 = ini.date().toordinal() + 1721424.5
    a, b = 0.0, 15.0  # días desde el 15 del mes
    for _ in range(60):
        medio = (a + b) / 2
        if ((_longitud_sol(jd0 + medio) - grados + 180) % 360) - 180 < 0:
            a = medio
        else:
            b = medio
    return (ini + dt.timedelta(days=(a + b) / 2)).astimezone(MADRID)


def cambios_de_hora(anio):
    """[(fecha, +1 se adelanta / -1 se atrasa)] según la zona horaria de la península."""
    res, d = [], dt.date(anio, 1, 1)
    previo = dt.datetime(anio, 1, 1, 12, tzinfo=MADRID).utcoffset()
    while d.year == anio:
        d += dt.timedelta(days=1)
        ahora = dt.datetime(d.year, d.month, d.day, 12, tzinfo=MADRID).utcoffset()
        if ahora != previo:
            res.append((d, 1 if ahora > previo else -1))
            previo = ahora
    return res


def fijo(mes, dia):
    return lambda anio: dt.date(anio, mes, dia)


# Cuentas atrás de fechas generales: slug -> (nombre, categoría, función año -> fecha, explicación)
EVENTOS = {
    "navidad": ("Navidad", "fiestas", fijo(12, 25), "Navidad se celebra siempre el 25 de diciembre, festivo nacional en toda España."),
    "nochebuena": ("Nochebuena", "fiestas", fijo(12, 24), "Nochebuena es la noche del 24 de diciembre, víspera de Navidad. No es festivo, aunque muchos convenios dan la tarde libre."),
    "nochevieja": ("Nochevieja", "fiestas", fijo(12, 31), "Nochevieja es el 31 de diciembre, la última noche del año, con las campanadas a medianoche."),
    "ano-nuevo": ("Año Nuevo", "fiestas", fijo(1, 1), "El 1 de enero es Año Nuevo, festivo nacional en toda España."),
    "reyes": ("Reyes", "fiestas", fijo(1, 6), "El Día de Reyes (Epifanía del Señor) es el 6 de enero, festivo en toda España. La cabalgata es la tarde del 5."),
    "san-valentin": ("San Valentín", "fiestas", fijo(2, 14), "San Valentín, el día de los enamorados, es cada 14 de febrero."),
    "carnaval": ("Carnaval", "fiestas", lambda a: pascua(a) - dt.timedelta(days=47),
                 "El martes de Carnaval cae 47 días antes del Domingo de Pascua, así que cambia cada año. La cuenta atrás es hasta ese martes, el día grande en muchos sitios."),
    "dia-del-padre": ("Día del Padre", "fiestas", fijo(3, 19), "En España el Día del Padre es el 19 de marzo, San José. Es festivo en algunas comunidades."),
    "semana-santa": ("Semana Santa", "fiestas", lambda a: pascua(a) - dt.timedelta(days=7),
                     "La Semana Santa empieza el Domingo de Ramos y termina el Domingo de Pascua, que es el primer domingo después de la primera luna llena de primavera. Por eso cambia cada año. La cuenta atrás es hasta el Domingo de Ramos."),
    "sant-jordi": ("Sant Jordi", "fiestas", fijo(4, 23), "Sant Jordi, el día del libro y la rosa, es el 23 de abril. Es festivo en Aragón (San Jorge)."),
    "dia-de-la-madre": ("Día de la Madre", "fiestas", lambda a: enesimo(a, 5, 6, 1), "En España el Día de la Madre es el primer domingo de mayo."),
    "san-juan": ("San Juan", "fiestas", fijo(6, 24), "San Juan es el 24 de junio; la verbena y las hogueras son la noche del 23. Es festivo en Cataluña y en algunas otras comunidades."),
    "halloween": ("Halloween", "fiestas", fijo(10, 31), "Halloween es la noche del 31 de octubre, víspera de Todos los Santos."),
    "black-friday": ("Black Friday", "fiestas", black_friday, "El Black Friday es el viernes siguiente al Día de Acción de Gracias de Estados Unidos, que es el cuarto jueves de noviembre."),
    "loteria-de-navidad": ("la Lotería de Navidad", "fiestas", fijo(12, 22), "El sorteo extraordinario de la Lotería de Navidad, el del Gordo, se celebra cada 22 de diciembre por la mañana."),
    "loteria-del-nino": ("la Lotería del Niño", "fiestas", fijo(1, 6), "El sorteo del Niño se celebra el 6 de enero, día de Reyes."),
    "primavera": ("la primavera", "estaciones", lambda a: estacion(a, 0).date(), "La primavera empieza con el equinoccio de marzo, cuando el día y la noche duran casi lo mismo."),
    "verano": ("el verano", "estaciones", lambda a: estacion(a, 90).date(), "El verano empieza con el solsticio de junio, el día más largo del año."),
    "otono": ("el otoño", "estaciones", lambda a: estacion(a, 180).date(), "El otoño empieza con el equinoccio de septiembre."),
    "invierno": ("el invierno", "estaciones", lambda a: estacion(a, 270).date(), "El invierno empieza con el solsticio de diciembre, el día más corto del año."),
}
GRADOS = {"primavera": 0, "verano": 90, "otono": 180, "invierno": 270}


def proxima(slug, hoy):
    """Próxima fecha del evento (hoy incluido) y las de los años siguientes."""
    f = EVENTOS[slug][2]
    fechas = [f(a) for a in range(hoy.year, hoy.year + 6)]
    futuras = [x for x in fechas if x >= hoy]
    return futuras[0], futuras[1:5]


def proximo_cambio_de_hora(hoy):
    return [c for a in (hoy.year, hoy.year + 1, hoy.year + 2) for c in cambios_de_hora(a) if c[0] >= hoy]
