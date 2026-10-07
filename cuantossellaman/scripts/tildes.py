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

def _sin_tilde(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").upper()


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
    """Forma para buscar: minúsculas, sin tildes, espacios simples ('  María  José' -> 'maria jose')."""
    return " ".join(_sin_tilde(texto).lower().replace("·", "").split())
