# ¿Cuántos se llaman? — cuantossellaman.es

Web estática que responde «¿Cuántas personas se llaman X en España?» y «¿Cuántas personas se
apellidan X?» con los datos oficiales del INE (estadística de nombres y apellidos a partir de los
Censos de población anuales, y estadística de nacimientos para los bebés).

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
    tildes.py          reconstruye las tildes para mostrar nombres y apellidos
  data/                JSON intermedios (nombres, provincias, décadas, bebés, apellidos)
  plantilla/           CSS, JavaScript del buscador y favicon
  content/
    tildes.csv               correcciones de tildes de nombres a mano
    tildes-apellidos.csv     correcciones de tildes de apellidos a mano
    significados/            significados de nombres escritos a mano (opcional)
    significados-apellidos/  origen de apellidos escrito a mano (opcional)
  web/                 la web generada: lo que publica Cloudflare Pages
```

## Regenerar los datos en local

```bash
pip install openpyxl xlrd
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

Un apellido tiene página propia (`/apellido/<slug>/`) si lo llevan al menos **2.000 personas como
primer apellido** o si está entre los 100 más frecuentes de España o los 50 de alguna provincia.

Con los datos a 1 de enero de 2025 salen **2.911 páginas de nombre y 2.471 de apellido**. Para
cambiar los umbrales:

```bash
python cuantossellaman/scripts/generar_web.py --umbral 2000 --umbral-apellidos 3000
```

o cambia `UMBRAL_POR_DEFECTO` y `UMBRAL_APELLIDOS_POR_DEFECTO` en `generar_web.py` (los usa el workflow).

El resto de nombres (unos 60.000) y de apellidos (unos 84.000) no tiene URL propia: se consultan
en el buscador de la portada, que lee `web/indice/<letra>.json` o `web/indice-apellidos/<letra>.json`
en el navegador. Si un nombre no está en los datos del INE, el
buscador dice «Hay menos de 20 personas con este nombre en España; el INE no publica la cifra
exacta». Nunca se estima ni se inventa esa cifra.

## Tildes

El INE publica nombres y apellidos en mayúsculas y sin tildes. `tildes.py` las reconstruye:

- **Nombres:** con una tabla de nombres españoles que llevan tilde.
- **Apellidos:** con una tabla de apellidos frecuentes y una regla para los patronímicos en -ez
  (Pérez, Rodríguez, Gutiérrez, Suárez…), con excepciones como Álvarez o Valdez.

Lo que no está en las tablas se muestra sin tilde. Para corregir una palabra, añade una línea a
`content/tildes.csv` o `content/tildes-apellidos.csv` (`PALABRA_SIN_TILDE,Forma correcta`) y
regenera la web.

## Añadir significados a mano

Crea `content/significados/<slug>.md` (por ejemplo `lucia.md`) con uno o varios párrafos.
Se mostrará en la página del nombre. Ver `content/significados/LEEME.md`.

## Pendiente

- **Significados y orígenes**: ninguno escrito todavía (`content/significados/` y
  `content/significados-apellidos/`).
- **Afiliados**: regalos personalizados en las páginas de nombre y genealogía (MyHeritage) en las de
  apellido, cuando haya tráfico y cuentas en esos programas.
- **Publicidad y analítica**: la web no tiene AdSense ni Google Analytics, así que no necesita
  aviso de cookies. Si se añaden, hay que actualizar `/privacidad/` y poner el mensaje de
  consentimiento.
