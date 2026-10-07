# ¿Cuántos se llaman? — cuantossellaman.es

Web estática que responde «¿Cuántas personas se llaman X en España?» con los datos oficiales del
INE (estadística de nombres y apellidos a partir de los Censos de población anuales, y estadística
de nacimientos para los bebés).

Mismo sistema que Ahorrómetro: scripts de Python que generan HTML estático, un workflow de
GitHub Actions que actualiza los datos y Cloudflare Pages, que publica la carpeta `web/` en cada
cambio de `main`.

## Estructura

```
cuantossellaman/
  scripts/
    descargar_ine.py   descarga las hojas de cálculo del INE en datos-ine/ (no se suben a GitHub)
    procesar_ine.py    las convierte en JSON en data/ y falla si el formato del INE cambia
    generar_web.py     genera la web en web/ a partir de data/
    tildes.py          reconstruye las tildes para mostrar los nombres
  data/                JSON intermedios (nombres, provincias, décadas, bebés)
  plantilla/           CSS, JavaScript del buscador y favicon
  content/
    tildes.csv         correcciones de tildes a mano
    significados/      significados de nombres escritos a mano (opcional)
  web/                 la web generada: lo que publica Cloudflare Pages
```

## Regenerar los datos en local

```bash
pip install openpyxl
python cuantossellaman/scripts/descargar_ine.py   # necesita acceso a ine.es
python cuantossellaman/scripts/procesar_ine.py
python cuantossellaman/scripts/generar_web.py
python -m http.server 8000 -d cuantossellaman/web   # y abre http://localhost:8000
```

Si solo cambias el diseño o los textos, basta con `generar_web.py`: usa los JSON de `data/`.

## Actualización automática

`.github/workflows/datos-nombres.yml` se ejecuta el 1 de junio, el 1 de julio y el 1 de diciembre
(el INE publica los nombres de la población en mayo y los de los bebés en noviembre), al cambiar
los scripts o la plantilla, y a mano desde **Actions → Datos de nombres (INE) → Run workflow**.

Si la descarga falla, el INE cambia el formato de sus ficheros o salen menos de 500 páginas de
nombre, el workflow falla (GitHub te avisa por correo) y no publica nada: la web sigue con los
últimos datos buenos.

## Umbral de indexación

Un nombre tiene página propia (`/nombre/<slug>/`, indexable y en el sitemap) si:

- lo llevan al menos **1.000 personas** en España, sumando hombres y mujeres, o
- aparece en alguna tabla de ranking del INE: los 50 más frecuentes de una provincia, los 50 más
  frecuentes de una década o los 100 más puestos a los bebés en algún año (o los 10 de una comunidad).

Con los datos a 1 de enero de 2025 salen 2.911 páginas de nombre. Para cambiar el umbral:

```bash
python cuantossellaman/scripts/generar_web.py --umbral 2000
```

o cambia `UMBRAL_POR_DEFECTO` en `generar_web.py` (lo usa el workflow).

El resto de nombres (unos 60.000) no tiene URL propia: se consultan en el buscador de la portada,
que lee `web/indice/<letra>.json` en el navegador. Si un nombre no está en los datos del INE, el
buscador dice «Hay menos de 20 personas con este nombre en España; el INE no publica la cifra
exacta». Nunca se estima ni se inventa esa cifra.

## Tildes

El INE publica los nombres en mayúsculas y sin tildes. `tildes.py` las reconstruye con una tabla
de nombres españoles que llevan tilde; lo que no está en la tabla se muestra sin tilde. Para
corregir una palabra, añade una línea a `content/tildes.csv` (`PALABRA_SIN_TILDE,Forma correcta`)
y regenera la web.

## Añadir significados a mano

Crea `content/significados/<slug>.md` (por ejemplo `lucia.md`) con uno o varios párrafos.
Se mostrará en la página del nombre. Ver `content/significados/LEEME.md`.

## Pendiente

- **Apellidos**: `descargar_ine.py` ya descarga `apellidos_frecuencia.xls` y
  `apellidos_mas_frecuentes.xls`, pero aún no se procesan ni tienen páginas. La lectura de tablas
  de `procesar_ine.py` (`bloques_ancho`) sirve para ellos.
- **Significados**: ninguno escrito todavía.
- **Publicidad y analítica**: la web no tiene AdSense ni Google Analytics, así que no necesita
  aviso de cookies. Si se añaden, hay que actualizar `/privacidad/` y poner el mensaje de
  consentimiento.
