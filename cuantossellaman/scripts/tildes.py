"""Restaura las tildes de los nombres del INE para mostrarlos.

El INE publica los nombres en mayúsculas y SIN tildes («MARIA CARMEN»): en los datos no existe
la forma con tildes. La reconstruimos palabra a palabra con una tabla de nombres españoles que
llevan tilde. Si una palabra no está en la tabla se muestra sin tilde: preferimos «Raul» a
inventar una tilde equivocada.

Para corregir o añadir palabras sin tocar el código, edita content/tildes.csv
(una línea por palabra: PALABRA_SIN_TILDE,Forma correcta; por ejemplo «ESTIBALIZ,Estíbaliz»).
"""
import csv
import unicodedata
from pathlib import Path

# La ñ y la ç no son tildes: MARIÑA y MARINA son nombres distintos en el INE (y también IÑAKI e INAKI,
# o MUÑOZ y MUNOZ). Se quitan las tildes y diéresis, pero se conservan esas dos letras.
_LETRAS = {"\u0303": "nN", "\u0327": "cC"}  # virgulilla de la ñ y cedilla de la ç


def _sin_tilde(texto):
    salida = []
    for c in unicodedata.normalize("NFD", texto):
        if unicodedata.category(c) != "Mn" or (salida and salida[-1] in _LETRAS.get(c, "")):
            salida.append(c)
    return unicodedata.normalize("NFC", "".join(salida)).upper()


# Solo palabras que se escriben con tilde. Lo que no esté aquí se muestra sin tilde.
# Forma castellana (el INE no distingue el idioma: «NURIA» se muestra «Nuria», no «Núria»).
CON_TILDE = """
Aarón Adrián Agustín Águeda Álex Álvaro Ámbar Anaís Andrés Ángel Ángela Ángeles Aníbal
Anunciación Arántzazu Aránzazu Ascensión Asunción Bárbara Bartolomé Belén Benjamín Concepción
Consolación Cristóbal Damián Darío Débora Efraín Elías Eloísa Encarnación Epifanía Estefanía
Fabián Fátima Félix Fermín Gastón Germán Gerónimo Ginés Héctor Hernán Hipólito Inés Isaías Iván
Jerónimo Jesús Joaquín Jonás José Josué Julián Lázaro Leónidas Leví Lía Lucía María Mariángeles
Marián Martín Matías Máximo Melquíades Mía Moisés Mónica Néstor Nicolás Noé Noemí Óscar Pío
Presentación Purificación Purísima Ramón Raúl Resurrección Rocío Román Rómulo Rosalía Rubén
Salomé Saúl Sebastián Simón Sofía Teófilo Tobías Tomás Tristán Úrsula Valentín Verónica Víctor
Visitación Zoé África Íñigo Ítalo Ícaro Estíbaliz Begoña
""".split()
# Nombres que solo existen en catalán y llevan acento
SOLO_CATALAN = ["Adrià", "Àngels", "Martí", "Agnès", "Mercè", "Pere-Joan"]

TILDES = {_sin_tilde(w): w for w in CON_TILDE + SOLO_CATALAN}

PARTICULAS = {"DE", "DEL", "LA", "LAS", "LOS", "Y", "I", "E"}


def _cargar_correcciones():
    ruta = Path(__file__).resolve().parent.parent / "content" / "tildes.csv"
    if not ruta.exists():
        return
    with ruta.open(encoding="utf-8") as f:
        for fila in csv.reader(f):
            if len(fila) >= 2 and fila[0].strip() and not fila[0].lstrip().startswith("#"):
                TILDES[_sin_tilde(fila[0].strip())] = fila[1].strip()


_cargar_correcciones()


def mostrar(nombre_ine):
    """'MARIA DEL CARMEN' -> 'María del Carmen'; 'JOSE LUIS' -> 'José Luis'."""
    palabras = []
    for i, p in enumerate(nombre_ine.split()):
        if i and p in PARTICULAS:
            palabras.append(p.lower())
        else:
            palabras.append("-".join(TILDES.get(_sin_tilde(x), x.capitalize()) for x in p.split("-")))
    return " ".join(palabras)


def normalizar(texto):
    """Forma para buscar: minúsculas, sin tildes (pero con ñ, ç y ·: Mariña no es Marina ni Nel·lo es Nello), espacios simples ('  María  José' -> 'maria jose')."""
    return " ".join(_sin_tilde(texto).lower().split())


# ------------------------------------------------------------------------------------- Apellidos
# Apellidos frecuentes que llevan tilde y no siguen la regla de los patronímicos en -ez.
APELLIDOS_CON_TILDE = """
Álvarez García Martín Marín Díaz Muñoz Cortés León Román Durán Galán Beltrán Millán Roldán Julián
Adán Chacón Calderón Alarcón Rincón Colón Aragón Pinzón Ramón Simón Garzón Carrión Barragán Guzmán
Guillén Jerónimo Cristóbal Andrés Tomás Nicolás Inés Ginés Moisés Valdés Hernán Agustín Fermín
Joaquín Jesús Ángel María Sáez Díez Sáenz Laínez Castañón Arévalo Ávila Álamo Cánovas Cáceres
Córdoba Málaga Gómara Bolívar Galván Bernabé Cebrián Lucía Montalbán Morán Quintín Sebastián
Tristán Valentín Zurbarán Álvaro Ávalos Herrán Lázaro Ríos Gascón Garcés Solís Alcántara Bárcena
Cámara Cárdenas Fábregas Mármol Úbeda Ágreda Ábalos Belén Ibáñez Ordóñez Núñez Rubén Cristián
""".split()
_APELLIDOS = {_sin_tilde(w): w for w in APELLIDOS_CON_TILDE}
# Apellidos en -EZ que se pronuncian agudos y no llevan tilde
_EZ_SIN_TILDE = {"VALDEZ", "ALDEZ", "GODEZ"}
_VOCALES = "AEIOU"
_FUERTES = "AEO"
_ACENTO = {"A": "á", "E": "é", "I": "í", "O": "ó", "U": "ú"}


def _patronimico(p):
    """Apellidos en -EZ llanos: Pérez, López, Rodríguez, Gutiérrez, Suárez... (tilde en la penúltima sílaba)."""
    raiz = p[:-2]
    if len(raiz) < 2 or not any(c in _VOCALES for c in raiz):
        return None
    if raiz[-1] == "U" and len(raiz) > 1 and raiz[-2] in "QG":  # RODRIGU-EZ, VAZQU-EZ: la u no suena
        raiz = raiz[:-1]
    # último grupo de vocales de la raíz
    fin = max(i for i, c in enumerate(raiz) if c in _VOCALES)
    ini = fin
    while ini > 0 and raiz[ini - 1] in _VOCALES:
        ini -= 1
    grupo = raiz[ini:fin + 1]
    # en un diptongo la tilde va en la vocal abierta (GUTIERREZ -> Gutiérrez, SUAREZ -> Suárez)
    k = next((j for j, c in enumerate(grupo) if c in _FUERTES), len(grupo) - 1)
    pos = ini + k
    palabra = p.capitalize()
    return palabra[:pos] + _ACENTO[p[pos]] + palabra[pos + 1:]


def mostrar_apellido(ine):
    """'SANCHEZ' -> 'Sánchez'; 'GARCIA' -> 'García'; 'DE LA FUENTE' -> 'de la Fuente'."""
    partes = []
    for i, p in enumerate(ine.split()):
        if p in PARTICULAS:
            partes.append(p.lower())
            continue
        trozos = []
        for x in p.split("-"):
            clave = _sin_tilde(x)
            if clave in TILDES_APELLIDOS_EXTRA:
                trozos.append(TILDES_APELLIDOS_EXTRA[clave])
            elif clave in _APELLIDOS:
                trozos.append(_APELLIDOS[clave])
            elif clave.endswith("EZ") and len(clave) > 4 and clave not in _EZ_SIN_TILDE:
                trozos.append(_patronimico(clave) or x.capitalize())
            else:
                trozos.append(x.capitalize())
        partes.append("-".join(trozos))
    texto = " ".join(partes)
    return texto[:1].upper() + texto[1:]


TILDES_APELLIDOS_EXTRA = {}


def _cargar_correcciones_apellidos():
    ruta = Path(__file__).resolve().parent.parent / "content" / "tildes-apellidos.csv"
    if not ruta.exists():
        return
    with ruta.open(encoding="utf-8") as f:
        for fila in csv.reader(f):
            if len(fila) >= 2 and fila[0].strip() and not fila[0].lstrip().startswith("#"):
                TILDES_APELLIDOS_EXTRA[_sin_tilde(fila[0].strip())] = fila[1].strip()


_cargar_correcciones_apellidos()
