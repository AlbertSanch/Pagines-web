# festivosde.es

Festivos nacionales, autonómicos y locales de cada municipio de España.

- `fuentes.json`: lista de publicaciones oficiales (BOE y boletines autonómicos o provinciales) con su URL.
  Cuando sale una resolución nueva (por ejemplo, las fiestas locales del año siguiente) o una corrección, se añade aquí.
- `scripts/descargar_fuentes.py`: descarga las fuentes y guarda su texto en `fuentes/`.
- `scripts/procesar.py`: extrae los festivos y escribe `data/festivos_<año>.json` y `data/informe.txt` (avisos y cobertura).
- `scripts/generar_web.py`: genera `web/` (se publica con Cloudflare Pages, carpeta de salida `festivos/web`).
- `.github/workflows/festivos.yml`: lo ejecuta todo cada lunes y al cambiar los scripts en main.

Regla: nunca se inventa ni se supone una fecha. Si un municipio no tiene sus fiestas locales en un boletín
(o el boletín no se puede leer, como el de Burgos 2026, escaneado), la página lo dice y no se indexa.
