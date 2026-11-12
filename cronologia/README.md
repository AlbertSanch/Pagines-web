# ¿Qué fue antes? (nombre y dominio provisionales)

Juego diario: cada día, seis momentos de la historia. El primero sale ya colocado en la línea del tiempo y los otros
cinco hay que colocarlos, de uno en uno, en su hueco (antes, entre medias o después). Tic, el relojito, camina por el
horizonte de épocas (dinosaurios, pirámides, castillo, carabela, tren, coche, tele, cohete) hasta la época de cada hecho.

## Datos

- `data/hechos.json`: los hechos (tarjeta, año, emoji, ámbito, categoría, pregunta para Google, explicación y artículo
  de Wikipedia en español). Se crea con `scripts/hechos_base.py` (primera tanda); los siguientes se pueden añadir a mano.
- `data/verificacion.json`: resultado de `scripts/verificar.py`, que comprueba que el artículo de Wikipedia de cada hecho
  existe y menciona su año. Solo se publican los hechos comprobados.
- `data/dias.json`: qué seis hechos salen cada día (el primero es el ancla). Lo amplía `scripts/programar.py`; los días
  ya programados no cambian.

## Órdenes

```bash
python cronologia/scripts/verificar.py --solo-nuevos   # comprobar los hechos nuevos
python cronologia/scripts/programar.py 45              # programar 45 días hacia delante
python cronologia/scripts/generar_web.py               # generar cronologia/web
```

El robot (`.github/workflows/cronologia.yml`) programa y regenera la web dos veces al día.

## Para lanzarla

1. Elegir nombre y dominio y cambiar `DOMINIO`, `LANZAMIENTO`, `DOMINIO_ACTIVO` y el correo de `TITULAR` en
   `scripts/generar_web.py`.
2. Cloudflare Pages: proyecto nuevo conectado al repositorio, sin orden de compilación, directorio de salida
   `cronologia/web` y «Build watch paths» `cronologia/web/*`.
3. Añadir el dominio en «Custom domains», Search Console, Web Analytics y AdSense, como con las otras webs.
