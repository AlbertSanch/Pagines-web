"""Datos y utilidades comunes de festivosde.es."""
import json
import pathlib
import re
import unicodedata

BASE = pathlib.Path(__file__).resolve().parent.parent
DATA = BASE / "data"
FUENTES = BASE / "fuentes"

# Comunidades: clave, nombre visible y nombre de la columna en la tabla del BOE
COMUNIDADES = {
    "andalucia": ("Andalucía", "Andalucía"), "aragon": ("Aragón", "Aragón"), "asturias": ("Asturias", "Asturias"),
    "baleares": ("Illes Balears", "Illes Balears"), "canarias": ("Canarias", "Canarias"), "cantabria": ("Cantabria", "Cantabria"),
    "castilla-la-mancha": ("Castilla-La Mancha", "Castilla-La Mancha"), "castilla-y-leon": ("Castilla y León", "Castilla y León"),
    "cataluna": ("Cataluña", "Cataluña"), "extremadura": ("Extremadura", "Extremadura"), "galicia": ("Galicia", "Galicia"),
    "madrid": ("Comunidad de Madrid", "Madrid"), "murcia": ("Región de Murcia", "Murcia"), "navarra": ("Navarra", "Navarra"),
    "pais-vasco": ("País Vasco", "País Vasco"), "la-rioja": ("La Rioja", "Rioja"), "valenciana": ("Comunitat Valenciana", "Valenciana"),
    "ceuta": ("Ceuta", "Ceuta"), "melilla": ("Melilla", "Melilla"),
}

# Provincias: código INE -> (nombre visible, comunidad)
PROVINCIAS = {
    "01": ("Álava", "pais-vasco"), "02": ("Albacete", "castilla-la-mancha"), "03": ("Alicante", "valenciana"),
    "04": ("Almería", "andalucia"), "05": ("Ávila", "castilla-y-leon"), "06": ("Badajoz", "extremadura"),
    "07": ("Illes Balears", "baleares"), "08": ("Barcelona", "cataluna"), "09": ("Burgos", "castilla-y-leon"),
    "10": ("Cáceres", "extremadura"), "11": ("Cádiz", "andalucia"), "12": ("Castellón", "valenciana"),
    "13": ("Ciudad Real", "castilla-la-mancha"), "14": ("Córdoba", "andalucia"), "15": ("A Coruña", "galicia"),
    "16": ("Cuenca", "castilla-la-mancha"), "17": ("Girona", "cataluna"), "18": ("Granada", "andalucia"),
    "19": ("Guadalajara", "castilla-la-mancha"), "20": ("Gipuzkoa", "pais-vasco"), "21": ("Huelva", "andalucia"),
    "22": ("Huesca", "aragon"), "23": ("Jaén", "andalucia"), "24": ("León", "castilla-y-leon"), "25": ("Lleida", "cataluna"),
    "26": ("La Rioja", "la-rioja"), "27": ("Lugo", "galicia"), "28": ("Madrid", "madrid"), "29": ("Málaga", "andalucia"),
    "30": ("Murcia", "murcia"), "31": ("Navarra", "navarra"), "32": ("Ourense", "galicia"), "33": ("Asturias", "asturias"),
    "34": ("Palencia", "castilla-y-leon"), "35": ("Las Palmas", "canarias"), "36": ("Pontevedra", "galicia"),
    "37": ("Salamanca", "castilla-y-leon"), "38": ("Santa Cruz de Tenerife", "canarias"), "39": ("Cantabria", "cantabria"),
    "40": ("Segovia", "castilla-y-leon"), "41": ("Sevilla", "andalucia"), "42": ("Soria", "castilla-y-leon"),
    "43": ("Tarragona", "cataluna"), "44": ("Teruel", "aragon"), "45": ("Toledo", "castilla-la-mancha"),
    "46": ("Valencia", "valenciana"), "47": ("Valladolid", "castilla-y-leon"), "48": ("Bizkaia", "pais-vasco"),
    "49": ("Zamora", "castilla-y-leon"), "50": ("Zaragoza", "aragon"), "51": ("Ceuta", "ceuta"), "52": ("Melilla", "melilla"),
}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def clave_nombre(t):
    """Normaliza el nombre de un municipio para cruzarlo con el del INE."""
    t = sin_tildes(t).lower().replace("’", "'").replace("`", "'")
    t = re.sub(r"\s+", " ", t).strip(" .;,")
    # «Alcázares, Los» / «Alcázares (Los)» -> «los alcázares»
    m = re.match(r"^(.*?)\s*[,(]\s*(el|la|los|las|l'|lo|els|les|o|a|os|as|sa|ses|es|s')\s*\)?$", t)
    if m:
        art = m.group(2)
        t = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
    t = re.sub(r"[^a-z0-9ñ' ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def slug(t):
    t = sin_tildes(t).lower().replace("ñ", "n")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def municipios():
    """Código INE -> nombre oficial del INE."""
    return json.loads((DATA / "municipios.json").read_text(encoding="utf-8"))


# Nombres que los boletines escriben distinto que el INE (comprobados uno a uno)
ALIAS = {
    "canarias": {"la frontera": "frontera", "san bartolome de lanzarote": "san bartolome",
                 "santa lucia": "santa lucia de tirajana", "santa maria de guia": "santa maria de guia de gran canaria",
                 "valsequillo": "valsequillo de gran canaria"},
    "murcia": {"fuente alamo": "fuente alamo de murcia"},
    "la-rioja": {"pradillo de cameros": "pradillo"},
}


def indice_nombres(ccaa):
    """Nombre normalizado -> código INE, solo para los municipios de una comunidad.

    Incluye cada parte de los nombres bilingües («Elx/Elche» -> «elx», «elche»)."""
    idx = {}
    for cod, nombre in municipios().items():
        if PROVINCIAS[cod[:2]][1] != ccaa:
            continue
        partes = {nombre} | set(re.split(r"\s*/\s*", nombre)) | set(re.split(r"\s+-\s+", nombre))
        for p in partes:
            idx.setdefault(clave_nombre(p), set()).add(cod)
    for otro, oficial in ALIAS.get(ccaa, {}).items():
        idx[otro] = idx[oficial]
    return idx
