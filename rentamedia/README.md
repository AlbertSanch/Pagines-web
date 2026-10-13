# Renta Media (rentamedia.es)

Renta media de cada municipio, provincia, comunidad y distrito de España, con los datos oficiales del
**Atlas de Distribución de Renta de los Hogares** del INE (de 2015 al último año publicado).
Web estática: GitHub Actions descarga y procesa los datos y genera las páginas; Cloudflare Pages publica `web/`.

## Carpetas

```
scripts/
  descargar_ine.py   descarga del INE las tablas de renta, fuentes de ingreso, Gini y demografía de cada provincia
  procesar_ine.py    las convierte en JSON compactos en data/ (los datos no publicados quedan como null)
  generar_web.py     genera web/ a partir de data/ y plantilla/
plantilla/           estilos, JavaScript (buscador, comparador, compartir), iconos e imagen para redes
data/                datos procesados (se suben a GitHub)
datos-ine/           CSV originales del INE (no se suben: se descargan en cada actualización)
web/                 la web generada: lo que publica Cloudflare Pages
```

## Actualización

El workflow `.github/workflows/rentamedia.yml` comprueba los datos del INE cada lunes de octubre a diciembre
(el INE publica el atlas en otoño) y el día 1 del resto de meses, regenera la web y la sube a `main`.
Al cambiar los scripts o la plantilla solo regenera la web. También se puede lanzar a mano desde Actions.

Para generarla en local: `python rentamedia/scripts/generar_web.py` (necesita `data/`).

## Reglas

- Nunca se estiman ni se inventan cifras: lo que el INE no publica (secreto estadístico) se dice tal cual.
- Los rankings de España y de las comunidades solo incluyen municipios de 2.000 habitantes o más, como el INE.
- Los nombres de distrito solo se ponen en Madrid y Barcelona, donde los distritos censales coinciden con los municipales.

## Cloudflare Pages

Proyecto conectado a este repositorio, rama `main`, sin comando de compilación y con la carpeta de salida
`rentamedia/web`. Dominio: rentamedia.es.
