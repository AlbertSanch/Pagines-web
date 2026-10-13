# Renta Media (rentamedia.es)

Renta media de cada municipio, provincia, comunidad y barrio de España, con los datos oficiales del
**Atlas de Distribución de Renta de los Hogares** del INE (de 2015 al último año publicado) y de la
**Estadística de los declarantes del IRPF** de la Agencia Tributaria (municipios de más de 1.000 habitantes y
códigos postales de las ciudades más grandes, un año más recientes que los del INE).
Web estática: GitHub Actions descarga y procesa los datos y genera las páginas; Cloudflare Pages publica `web/`.

## Carpetas

```
scripts/
  descargar_ine.py   descarga del INE las tablas de renta, fuentes de ingreso, Gini y demografía de cada provincia
  procesar_ine.py    las convierte en JSON compactos en data/ (los datos no publicados quedan como null)
  descargar_hacienda.py  lee las tablas web de Hacienda (municipios y códigos postales) y escribe data/hacienda.json
  descargar_mapas.py     descarga del servicio de mapas del INE los contornos de municipios y de las secciones censales
                         de las ciudades de más de 100.000 habitantes (data/geo_*.json) para los mapas coloreados
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
- Los nombres de distrito del INE solo se ponen en Madrid y Barcelona, donde los distritos censales coinciden con los municipales.
  Los barrios del resto de ciudades salen de los códigos postales de Hacienda, que ya traen su nombre.
- Las cifras del INE (renta neta por persona) y de Hacienda (renta bruta por declaración) se muestran siempre por separado.

## Cloudflare Pages

Proyecto conectado a este repositorio, rama `main`, sin comando de compilación y con la carpeta de salida
`rentamedia/web`. Dominio: rentamedia.es.
