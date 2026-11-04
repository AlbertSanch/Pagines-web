# Famoso del día (famosodeldia.es)

Juego diario: cada día, un famoso mundial y uno español para adivinar con seis pistas. Web estática generada con Python
y publicada en Cloudflare Pages desde `famoso/web`, que genera el robot (`.github/workflows/famoso.yml`).

## Añadir famosos

Edita `data/mundial.json` o `data/espana.json` y añade un bloque como este:

```json
{
  "slug": "rafa-nadal",
  "fecha": "2026-12-01",
  "nombre": "Rafa Nadal",
  "alias": ["Rafael Nadal", "Nadal", "Rafa"],
  "ambito": "Deporte",
  "pistas": ["Nació en 1986.", "Es deportista.", "Logro concreto…", "Nació en Manacor (Mallorca).", "Dato muy reconocible…", "Sus iniciales son R. N."],
  "resumen": "Una o dos frases: se ven al terminar la partida.",
  "biografia": ["Párrafo 1…", "Párrafo 2…", "Párrafo 3…"],
  "curiosidades": ["Dato curioso 1", "Dato curioso 2"],
  "fuente": "https://es.wikipedia.org/wiki/Rafael_Nadal"
}
```

- **Famoso del día**: pon `"fecha"` (AAAA-MM-DD). Solo puede haber uno por día en cada archivo.
- **Modo práctica**: en lugar de la fecha, pon `"practica": true`.
- Las 6 pistas van de la más difícil a la más fácil.
- El `nombre` tiene que estar también en `data/nombres.json` (la lista del autocompletado). Añade ahí cualquier nombre
  nuevo, y algunos más que no sean soluciones, para que la lista no dé pistas.
- Los `alias` son otras formas válidas de escribir el nombre (no importan tildes ni mayúsculas).

El script comprueba todo al generar y, si algo está mal (6 pistas, slug repetido, dos famosos el mismo día, nombre que
no está en la lista…), se para y explica el error sin publicar nada. También avisa cuando quedan menos de 7 días con famoso.

## Generar y probar en local

```
python3 famoso/scripts/generar_web.py
python3 -m http.server 8000 -d famoso/web
```

Abre http://localhost:8000. Para probar como si fuera otro día: `FDD_HOY=2026-11-12 python3 famoso/scripts/generar_web.py`
(y en el navegador hay que cambiar también la fecha del sistema, porque el juego usa la hora de Madrid del navegador).

## Cómo se protegen las respuestas

Solo se publican los datos de los días pasados, de hoy y de mañana, cada día en `web/d/<nombre no adivinable>.json` y
con el contenido codificado. Los días futuros no están en la web. Las fichas `/famoso/<slug>/` de los famosos diarios solo
se publican cuando su día ya ha pasado. Ojo: el repositorio es público, así que los JSON de `data/` sí se pueden leer en GitHub.

## Fechas

- `LANZAMIENTO` en `scripts/generar_web.py` es el día #1. Si lanzas otro día, cámbialo y ajusta las fechas de los famosos.
