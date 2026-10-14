"""Convierte las fuentes oficiales descargadas en datos de festivos por municipio.

Lee festivos/fuentes/ (ver descargar_fuentes.py) y escribe festivos/data/festivos_{año}.json:
  {"anio", "nacionales_autonomicos": {comunidad: [{f, n, t}]}, "notas": {comunidad: [texto]},
   "locales": {código INE: [{f, n}]}, "fuentes": {comunidad: {...}}, "boe": {...}}
t = «nacional» o «autonomico». Nunca se inventa una fecha: si un municipio no
aparece en su boletín, simplemente no tiene festivos locales en los datos.
Cada lector comprueba lo que puede (día de la semana, dos festivos por municipio)
y los avisos se escriben en festivos/data/informe.txt.
"""
import datetime as dt
import html
import json
import re

from comun import COMUNIDADES, DATA, FUENTES, MESES, DIAS, PROVINCIAS, clave_nombre, indice_nombres, municipios

AVISOS = []


def aviso(t):
    AVISOS.append(t)


def fecha(anio, dia, mes):
    mes = MESES.index(mes.lower().strip()) + 1
    return dt.date(anio, mes, int(dia))


RE_MES = "(" + "|".join(MESES) + ")"


# ------------------------------------------------------------------ BOE
def leer_boe(anio):
    x = (FUENTES / f"boe_{anio}.xml").read_text(encoding="utf-8")
    limpio = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
    cab = [limpio(c) for c in re.findall(r"<th[^>]*>(.*?)</th>", x, re.S)][2:]
    columnas = []
    for c in cab:
        clave = next((k for k, (_, b) in COMUNIDADES.items() if b.lower() in c.lower()), None)
        if not clave:
            raise SystemExit(f"BOE {anio}: columna desconocida «{c}»")
        columnas.append(clave)
    assert len(columnas) == 19, columnas
    res = {k: [] for k in COMUNIDADES}
    mes = None
    for fila in re.findall(r"<tr>(.*?)</tr>", x[x.find("<tbody>"):x.find("</tbody>")], re.S):
        celdas = [limpio(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", fila, re.S)]
        if len(celdas) != 20:
            continue
        primera = celdas[0]
        if primera.lower() in MESES:
            mes = primera.lower()
            continue
        m = re.match(r"(\d{1,2})\s+(.*?)\.?$", primera)
        if not m or not mes:
            aviso(f"BOE {anio}: fila no entendida «{primera}»")
            continue
        f = fecha(anio, m.group(1), mes)
        for clave, marca in zip(columnas, celdas[1:]):
            if marca:
                res[clave].append({"f": f.isoformat(), "n": m.group(2).strip(), "t": "autonomico" if marca == "***" else "nacional"})
    notas = {}
    for p in re.findall(r'<p class="parrafo[^"]*">(\d\.\s.*?)</p>', x, re.S):
        t = limpio(p)
        for clave, (nombre, _) in COMUNIDADES.items():
            if f"Comunidad Autónoma de {nombre}" in t or f"Comunidad Autónoma de {_}" in t:
                notas.setdefault(clave, []).append(re.sub(r"^\d\.\s*", "", t))
    ident = re.search(r'<identificador>(.*?)</identificador>', x).group(1)
    titulo = limpio(re.search(r"<titulo>(.*?)</titulo>", x, re.S).group(1))
    publicado = re.search(r"<fecha_publicacion>(\d{8})</fecha_publicacion>", x).group(1)
    for clave, lista in res.items():
        if len(lista) < 12:
            aviso(f"BOE {anio}: {clave} tiene solo {len(lista)} fiestas")
    return res, notas, {"id": ident, "titulo": titulo, "publicado": f"{publicado[:4]}-{publicado[4:6]}-{publicado[6:]}",
                        "url": f"https://www.boe.es/buscar/doc.php?id={ident}"}


# ------------------------------------------------------------------ lectores autonómicos
def trozo(txt, desde, hasta):
    i = txt.find(desde)
    j = txt.find(hasta, i + 1) if hasta else -1
    return txt[i if i >= 0 else 0: j if j > 0 else None]


def fechas_en(texto, anio):
    """«3 de mayo (San X) y 22 y 23 de julio (Y)» o «2 de abril, Jueves Santo; 13 de abril, San Vicente» -> [(fecha, nombre)]."""
    res = []
    patron = (r"(\d{1,2})((?:\s*(?:,|y|e|i)\s*\d{1,2})*)\s+(?:de\s+|del\s+)?" + RE_MES +
              r"\b(?:\s+de\s+\d{4})?\s*(?:\(([^)\n]*)\)?|,\s*(?!\d)([^;\n]*?)(?=;|\.\s|\.$|\s+y\s+\d|\n|$))?")
    for m in re.finditer(patron, texto, re.I):
        anio_escrito = re.search(r"de\s+(\d{4})", m.group(0)[:40])
        if anio_escrito and int(anio_escrito.group(1)) != anio:
            continue  # «Barcelona, 11 de diciembre de 2025»: fecha de firma, no festivo
        dias = [m.group(1)] + re.findall(r"\d{1,2}", m.group(2) or "")
        nombre = (m.group(4) or m.group(5) or "").strip(" .,;")
        if re.fullmatch(r"(fiestas?|festivos?) locales?|", nombre, re.I) or len(nombre) > 90:
            nombre = ""
        for d in dias:
            try:
                res.append((fecha(anio, d, m.group(3)), nombre[:1].upper() + nombre[1:]))
            except ValueError:
                aviso(f"Fecha imposible: «{m.group(0)}»")
    return res


def nombre_provincia(linea, ccaa):
    """Si la línea es la cabecera de una provincia de la comunidad, devuelve su código."""
    clave_cab = re.search(r"(?i)provincia|relaci[oó]n|anexo|territorio|isla", linea)
    if not clave_cab and not (linea.isupper() and not linea.rstrip().endswith(".")):
        return None  # una línea suelta en minúsculas suele ser un municipio, no una cabecera
    t = clave_nombre(re.sub(r"(?i)relaci[oó]n de (las )?fiestas locales (de la |en la |de |en )?|provincia de|provincia|anexo [ivx]+\.?|fiestas locales|territorio hist[oó]rico de", " ", linea))
    t = re.sub(r"\b(19|20)\d\d\b", "", t).strip(" -.:")
    for cod, (nombre, c) in PROVINCIAS.items():
        if c == ccaa and t and t in {clave_nombre(x) for x in nombre.split("/")} | {clave_nombre(nombre)}:
            return cod
    if ccaa == "baleares":
        return None
    alt = {"alacant": "03", "alicante": "03", "castello": "12", "valencia": "46", "a coruna": "15", "la coruna": "15",
           "araba": "01", "alava": "01", "bizkaia": "48", "vizcaya": "48", "gipuzkoa": "20", "guipuzcoa": "20", "girona": "17",
           "gerona": "17", "lleida": "25", "lerida": "25", "ourense": "32", "orense": "32", "las palmas": "35",
           "santa cruz de tenerife": "38"}
    return alt.get(t) if t in alt and PROVINCIAS[alt[t]][1] == ccaa else None


INICIO = re.compile(r"^(?:[—–-]\s*|\d{1,3}[.)]\s+|[•·]\s*)?([A-Za-zÁÉÍÓÚÑÜáéíóúñüÀÈÒàèòÏïÇç'’ .()/-]{2,70}?)\s*(?::|\.\s*-|,|\.)\s+(\d{1,2}\b.*)$")
TABLA = re.compile(r"^(?:\d{1,3}\s+)?([A-ZÁÉÍÓÚÑÜ][A-Za-zÁÉÍÓÚÑÜáéíóúñüÀÈÒàèòÏïÇç'’ ,.()/-]{1,70}?)\s{2,}(\d{1,2}\b.*)$")


def leer_general(txt, anio, ccaa):
    """Lector para las listas «Municipio: 3 de mayo y 14 de septiembre» en sus variantes (dos puntos, coma,
    punto y guion, tabla en columnas, nombre en una línea y fechas en la siguiente), con cabeceras de provincia."""
    entradas, prov, pendiente = [], None, None
    lineas, crudas = [], txt.replace("\ufffd", " ").splitlines()
    # «8 de» al final de una línea y el mes en la siguiente (celdas partidas): se juntan
    for i in range(len(crudas) - 1):
        if re.search(r"\b\d{1,2} de\s*$", crudas[i]):
            m = re.search(r"\b(" + "|".join(MESES) + r")\b", crudas[i + 1], re.I)
            if m:
                crudas[i] = crudas[i].rstrip() + " " + m.group(1)
                crudas[i + 1] = crudas[i + 1][:m.start()] + " " * len(m.group(1)) + crudas[i + 1][m.end():]
    for linea in crudas:
        # «Sahún. 24 de junio y 8 de septiembre. Eriste. 20 de enero…»: una entrada por localidad
        lineas += re.split(r"(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÑ][^\d.:;]{1,60}[.:]\s*\d)", linea)
    for linea in lineas:
        s = linea.strip()
        if s[:1] in "•·" or re.match(r"^[-–]\s+\d", s):
            s = s.lstrip("•·-– \t")
        if not s:
            continue
        if not re.search(r"\d", s) and len(s) < 70:
            p = nombre_provincia(s, ccaa)
            if p:
                prov, pendiente = p, None
                continue
        m = INICIO.match(s) or TABLA.match(s)
        if m and not re.match(r"(?i)^(?:(?:de|del|y)\b|art[ií]culo|resoluci|orden\b|disposici|p[aá]g\b|n[uú]m\b|bolet)", m.group(1)):
            entradas.append([m.group(1).strip(" .-—"), prov, m.group(2)])
            pendiente = None
        elif re.match(r"^\d{1,2}\b", s) and pendiente:
            entradas.append([pendiente, prov, s])
            pendiente = None
        elif re.match(r"^\d{1,2}\s+(?:de\s+)?(" + "|".join(MESES) + r")\b", s, re.I) and entradas and len(fechas_en(entradas[-1][2], anio)) < 2:
            entradas[-1][2] += " ; " + s  # segunda fecha en su propia línea
        elif not re.search(r"\d", s) and len(s) < 60 and re.match(r"^[A-ZÁÉÍÓÚÑ]", s):
            pendiente = s
        elif entradas and not re.search(r"\d{1,2} de ", s) and len(entradas[-1][2]) < 300 and (
                s[:1].islower() or not entradas[-1][2].rstrip().endswith((".", ")"))):
            entradas[-1][2] += " " + s
    res = []
    for nombre, prov, resto in entradas:
        f = fechas_en(resto, anio)
        if f:
            res.append((nombre, prov, f))
    return res


def leer_murcia(txt, anio):
    """Tabla: n.º, MUNICIPIO, día semana, día, mes, día semana, día, mes."""
    res = {}
    patron = re.compile(r"^\s*\d+\s+(.+?)\s{2,}(" + "|".join(DIAS) + r")\s+(\d{1,2})\s+(?:de\s+)?" + RE_MES +
                        r"\s+(" + "|".join(DIAS) + r")\s+(\d{1,2})\s+(?:de\s+)?" + RE_MES + r"\s*$", re.I)
    for linea in txt.splitlines():
        m = patron.match(linea)
        if not m:
            continue
        lista = []
        for ds, d, mes in ((m.group(2), m.group(3), m.group(4)), (m.group(5), m.group(6), m.group(7))):
            f = fecha(anio, d, mes)
            if DIAS[f.weekday()] != ds.lower():
                aviso(f"Murcia {anio}: {m.group(1)} {f} figura como {ds} y es {DIAS[f.weekday()]}")
            lista.append((f, ""))
        res[m.group(1).strip()] = lista
    return [(k, None, v) for k, v in res.items()]


def leer_entradas_dos_puntos(txt, anio):
    """«Logroño: 11 de junio (San Bernabé) y 21 de septiembre (San Mateo)», con líneas partidas
    y varias localidades separadas por «;» (La Rioja)."""
    plano = re.sub(r"www\.laboral-social\.com", " ", txt)
    plano = re.sub(r"\s+", " ", plano)
    nombre_re = r"[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñüÜ'’ .-]{1,60}?"
    res = {}
    for m in re.finditer(r"(?:^|[;)\s])(" + nombre_re + r"):\s(.*?)(?=(?:[;)]|\s)\s*" + nombre_re + r":\s|$)", plano):
        lista = fechas_en(m.group(2), anio)
        if lista:
            res[m.group(1).strip()] = lista
    return [(k, None, v) for k, v in res.items()]


def leer_canarias(txt, anio):
    """«INGENIO.» y debajo «2 de febrero: Festividad de …»."""
    res, actual = {}, None
    for linea in txt.splitlines():
        s = linea.strip()
        m = re.match(r"^(\d{1,2}) de " + RE_MES + r":\s*(.*?)\.?$", s, re.I)
        if m and actual:
            res[actual].append((fecha(anio, m.group(1), m.group(2)), m.group(3).strip()))
        elif re.match(r"^[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ,'’().-]+\.$", s) and len(s) < 60:
            actual = s.rstrip(".")
            res[actual] = []
        elif m is None and actual and s and res[actual] and not s[0].isdigit():
            # nombre de la fiesta partido en dos líneas
            f, n = res[actual][-1]
            if not re.match(r"^[A-ZÁÉÍÓÚÑÜ ]+\.$", s):
                res[actual][-1] = (f, (n + " " + s).strip().rstrip("."))
    return [(k, None, v) for k, v in res.items() if v]


# Fiestas «locales» comunes a todo un territorio (frase del propio boletín)
COMUNES = [
    r"[Dd][ií]a de fiesta del territorio hist[oó]rico:\s*(\d.*?\))",                       # Álava
    r"todo el Territorio Hist[oó]rico de \w+,\s*(el\s+\d.*?)\.(?:\s|$)",                  # Bizkaia
    r"(\d{1,2} de \w+, [^,]{3,60}), en todo el Territorio Hist[oó]rico",  # Gipuzkoa
    r"festividad del (\d{1,2} de \w+, [^,]+, D[ií]a de Navarra), como\s+com[uú]n a todo",  # Navarra
]


def fiestas_comunes(txt, anio):
    plano = re.sub(r"-\s*\n\s*", "", txt)
    plano = re.sub(r"\s+", " ", plano)
    for patron in COMUNES:
        m = re.search(patron, plano)
        if m:
            return fechas_en(m.group(1).replace("Día de Navarra", "").strip(" ,") , anio) or []
    return []


def leer_ceuta(txt, anio, ccaa):
    """«-20 de marzo: Fiesta de …» entre «a continuación» y «Segundo»."""
    t = trozo(txt, "a continuación", "Segundo")
    t = re.sub(r"(\d{1,2} de \w+):", r"\1,", t)
    return [("Ceuta", None, fechas_en(t, anio))]


def leer_melilla(txt, anio, ccaa):
    """«tienen la consideración de locales son los días 8 de septiembre (…) y el 17 de septiembre (…)»."""
    plano = re.sub(r"\s+", " ", txt)
    m = re.search(r"consideraci[oó]n de locales son los d[ií]as (.*?\))\s*\.", plano)
    return [("Melilla", None, fechas_en(m.group(1), anio))] if m else []


def leer_proximidad(txt, anio, ccaa):
    """Tablas con celdas centradas en vertical (Cantabria): el nombre del municipio va en la primera
    columna y cada fecha (día y mes, a veces en líneas distintas) se asigna al municipio más cercano.
    Cada municipio tiene dos fiestas locales."""
    nombres, fechas, dia_pend = [], [], None
    for i, linea in enumerate(txt.replace("\ufffd", " ").splitlines()):
        if re.match(r"^[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ,.'()/-]{2,}", linea):
            nombre = re.split(r"\s{2,}", linea.strip())[0]
            if not re.search(r"\d", nombre) and len(nombre) > 2:
                nombres.append([i, nombre, []])
        dia = re.search(r"\s(\d{1,2})(?:\s|$)", linea)
        mes = re.search(r"\b(" + "|".join(MESES) + r")\b", linea, re.I)
        if dia and mes:
            fechas.append((i, dia.group(1), mes.group(1)))
            dia_pend = None
        elif dia:
            dia_pend = (i, dia.group(1))
        elif mes and dia_pend:
            fechas.append((dia_pend[0], dia_pend[1], mes.group(1)))
            dia_pend = None
    for linea_f, d, mes in fechas:  # cada fecha es del último municipio que empieza en su línea o antes
        previos = [x for x in nombres if x[0] <= linea_f]
        if previos and len(previos[-1][2]) < 2:
            previos[-1][2].append((fecha(anio, d, mes), ""))
        elif previos:
            aviso(f"{ccaa} {anio}: fecha {d} {mes} sin municipio libre (línea {linea_f})")
    return [(n, None, f) for _, n, f in nombres if f]


def leer_centrado(txt, anio, ccaa):
    """Tablas con el nombre del municipio centrado en su bloque (Asturias): cada fecha va al municipio
    cuya línea está más cerca. Se guarda el texto de la fiesta (que a veces dice a qué parroquia afecta)."""
    lineas = txt.replace("\ufffd", " ").splitlines()
    nombres, fechas, pend = [], [], None
    for i, linea in enumerate(lineas):
        m = re.match(r"^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ,.'()/-]{2,})(?=\s{2,}|$)", linea)
        if m and not re.search(r"\d", m.group(1)):
            nombre = m.group(1).strip()
            # nombres partidos en dos líneas («BELMONTE DE» / «MIRANDA»)
            if nombre.endswith((" DE", " DEL", " DE LA", " Y")) and i + 1 < len(lineas):
                sig = re.match(r"^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ,.'()/-]{2,})(?=\s{2,}|$)", lineas[i + 1])
                if sig:
                    nombre += " " + sig.group(1).strip()
            elif nombres and nombres[-1][0] == i - 1 and nombres[-1][1].endswith((" DE", " DEL", " DE LA", " Y")):
                continue
            nombres.append([i, nombre, []])
        resto = linea[m.end():] if m else linea
        dm = re.search(r"(\d{1,2}) de\s*(?:(" + "|".join(MESES) + r")\b)?\s*(.*)$", resto, re.I)
        mes_solo = re.match(r"^\s+(" + "|".join(MESES) + r")\b\s*(.*)$", resto, re.I)
        if dm and dm.group(2):
            fechas.append([i, dm.group(1), dm.group(2), dm.group(3).strip()])
        elif dm:
            pend = [i, dm.group(1), dm.group(3).strip()]
        elif mes_solo and pend:
            fechas.append([pend[0], pend[1], mes_solo.group(1), (pend[2] + " " + mes_solo.group(2)).strip()])
            pend = None
        elif pend and resto.strip() and not re.search(r"\d", resto):
            pend[2] = (pend[2] + " " + resto.strip()).strip()
        elif fechas and resto.strip() and not re.search(r"\d", resto) and fechas[-1][0] == i - 1:
            fechas[-1][3] = (fechas[-1][3] + " " + resto.strip()).strip()
    for linea_f, d, mes, texto in fechas:
        if not nombres:
            break
        n = min(nombres, key=lambda x: (abs(x[0] - linea_f), -x[0] if x[0] <= linea_f else x[0]))
        if abs(n[0] - linea_f) <= 4:
            n[2].append((fecha(anio, d, mes), re.sub(r"\s+", " ", texto)[:120]))
    return [(n, None, f) for _, n, f in nombres if f]


def preparar_correccion(txt):
    """En las correcciones «donde dice … debe decir …» solo cuenta lo que «debe decir»."""
    # «la festividad local del Municipio de Bilbao para el año 2026 será el 28 de agosto (…)» -> «Bilbao: 28 de agosto (…)»
    plano = re.sub(r"\s+", " ", txt)
    frases = re.findall(r"[Mm]unicipio de ([A-ZÁÉÍÓÚÑ][\w' -]+?) para el año \d{4} (?:será|serán) (?:el|los)? ?(\d.*?\))", plano)
    if frases:
        return "\n".join(f"{a}: {b}" for a, b in frases)
    # catalán -> castellano (meses y conjunción) para las órdenes del DOGC
    for ca, es in (("gener", "enero"), ("febrer", "febrero"), ("març", "marzo"), ("maig", "mayo"), ("juny", "junio"),
                   ("juliol", "julio"), ("setembre", "septiembre"), ("novembre", "noviembre"), ("desembre", "diciembre")):
        txt = re.sub(rf"\b{ca}\b", es, txt)
    txt = re.sub(r"\bd['’](agost|abril|octubre)\b", lambda m: "de " + {"agost": "agosto"}.get(m.group(1), m.group(1)), txt)
    txt = re.sub(r"(\d) i (\d)", r"\1 y \2", txt)
    # «donde dice … debe decir …» / «on diu … ha de dir …»: solo cuenta lo nuevo
    txt = re.sub(r"(?is)(donde dice|on diu):?.*?(debe decir|ha de dir):?", "\n", txt)
    citas = re.findall(r"[«“\"]([^»”\"]{5,400})[»”\"]", txt)
    if citas:
        lineas = []
        for c in citas:
            for l in re.split(r"\n|(?<=\.)\s+(?=[A-ZÁÉÍÓÚ])", c):
                lineas.append(re.sub(r"^(.*?[^\d,:])\s+(\d)", r"\1: \2", re.sub(r"\s+", " ", l).strip(), count=1))
        return "\n".join(lineas)
    return txt


LECTORES = {
    "murcia": lambda t, a, c: leer_murcia(t, a),
    "la-rioja": lambda t, a, c: leer_entradas_dos_puntos(trozo(t, "Ábalos", "Restantes municipios"), a) or leer_entradas_dos_puntos(t, a),
    "canarias": lambda t, a, c: leer_canarias(t, a),
    "ceuta": leer_ceuta,
    "melilla": leer_melilla,
    "cantabria": leer_proximidad,
    "asturias": leer_centrado,
}


# ------------------------------------------------------------------ cruce con el INE
def asignar(ccaa, anio, entradas, fuente, provincia=None):
    idx = indice_nombres(ccaa)
    res, sin_cruce = {}, []
    for nombre, prov, lista in entradas:
        cods = idx.get(clave_nombre(nombre))
        if not cods:
            sin_cruce.append(nombre)
            continue
        if provincia:  # boletín provincial: solo municipios de esa provincia
            cods = {c for c in cods if c[:2] == provincia}
        elif len(cods) > 1 and prov:  # cabecera de provincia: solo para desempatar
            cods = {c for c in cods if c[:2] == prov} or cods
        if not cods:
            sin_cruce.append(nombre)
            continue
        if len(cods) != 1:
            aviso(f"{ccaa} {anio}: «{nombre}» corresponde a varios municipios {sorted(cods)}; se omite")
            continue
        cod = next(iter(cods))
        fiestas = sorted({(f.isoformat(), n) for f, n in lista})
        vistas, limpias = set(), []
        for f, n in fiestas:  # una fecha, una vez (con el nombre más largo)
            if f in vistas:
                limpias = [x for x in limpias if x["f"] != f or len(x["n"]) >= len(n)] + ([] if any(x["f"] == f and len(x["n"]) >= len(n) for x in limpias) else [{"f": f, "n": n}])
                continue
            vistas.add(f)
            limpias.append({"f": f, "n": n})
        if cod in res:  # la primera aparición es la de la lista; las siguientes suelen ser firmas o notas
            aviso(f"{ccaa} {anio}: {nombre} aparece dos veces en {fuente}; se queda la primera")
            continue
        res[cod] = sorted(limpias, key=lambda x: x["f"])
        if len(res[cod]) > 2 and ccaa not in ("canarias",):
            aviso(f"{ccaa} {anio}: {nombre} tiene {len(res[cod])} festivos locales en {fuente}")
    if sin_cruce:
        aviso(f"{ccaa} {anio} {fuente}: {len(sin_cruce)} nombres sin municipio del INE (pedanías o variantes): " + ", ".join(sorted(set(sin_cruce))[:60]))
    return res


def main():
    cfg = json.loads((FUENTES.parent / "fuentes.json").read_text(encoding="utf-8"))
    registro = json.loads((FUENTES / "registro.json").read_text(encoding="utf-8"))
    for anio in cfg["anios"]:
        if not (FUENTES / f"boe_{anio}.xml").exists():
            continue
        generales, notas, boe = leer_boe(anio)
        locales, fuentes, comun = {}, {}, {}
        for f in cfg["locales"]:
            if f["anio"] != anio or f.get("tipo") == "consolidado":
                continue
            ruta = FUENTES / f"{f['id']}.txt"
            if not ruta.exists():
                aviso(f"{f['id']}: no descargado")
                continue
            txt = ruta.read_text(encoding="utf-8", errors="replace").replace("\ufffd", " ")
            if f.get("tipo") in ("correccion", "complementaria"):
                txt = preparar_correccion(txt)
            lector = LECTORES.get(f["ccaa"], leer_general)
            entradas = lector(txt, anio, f["ccaa"])
            nuevos = asignar(f["ccaa"], anio, entradas, f["id"], f.get("provincia"))
            comunes = fiestas_comunes(txt, anio) if f.get("tipo") not in ("correccion", "complementaria") else []
            if comunes:
                clave = f.get("provincia") or next(p for p, (_, c) in PROVINCIAS.items() if c == f["ccaa"])
                comun[clave] = [{"f": fe.isoformat(), "n": nom} for fe, nom in comunes]
                aviso(f"{f['id']}: fiesta común a toda la provincia {clave}: {comun[clave]}")
            if f.get("tipo") in ("correccion", "complementaria"):
                aviso(f"{f['id']}: corrige o añade {len(nuevos)} municipios: " + ", ".join(sorted(municipios()[c] for c in nuevos)[:20]))
            locales.update(nuevos)
            if f.get("tipo") not in ("correccion", "complementaria"):
                fuentes.setdefault(f["ccaa"], {"titulo": f.get("titulo", ""), "url": registro.get(f["id"], {}).get("url") or f["descarga"],
                                               "publicado": f.get("publicado", "")})
                resto = re.search(r"Restantes municipios[^:]*:\s*([^\n]+)", txt)
                if resto:
                    fuentes[f["ccaa"]]["resto"] = resto.group(1).strip()
        for ccaa in COMUNIDADES:
            total = sum(1 for c in municipios() if PROVINCIAS[c[:2]][1] == ccaa)
            con = sum(1 for c in locales if PROVINCIAS[c[:2]][1] == ccaa)
            aviso(f"== {anio} {ccaa}: {con} de {total} municipios con fiestas locales")
        salida = {"anio": anio, "boe": boe, "nacionales_autonomicos": generales, "notas": notas,
                  "locales": dict(sorted(locales.items())), "comunes": comun, "fuentes": fuentes}
        (DATA / f"festivos_{anio}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"{anio}: {len(locales)} municipios con festivos locales; comunidades: {sorted(fuentes)}")
    (DATA / "informe.txt").write_text("\n".join(AVISOS) + "\n", encoding="utf-8")
    print("\n".join(AVISOS))


if __name__ == "__main__":
    main()
