# Ahorrómetro: guía rápida

## 1. Antes de publicar (obligatorio)
Busca y reemplaza en todos los archivos:
- `[TU NOMBRE Y APELLIDOS]`, `[TU NIF]`, `[TU DIRECCIÓN O LOCALIDAD]`, `[TU EMAIL DE CONTACTO]`
- Escribe tu historia en `sobre-nosotros.html` (donde pone `[ESCRIBE AQUÍ TU HISTORIA…]`).
- Si al final usas otro dominio, reemplaza `ahorrometro.es` en todos los archivos.
- Revisa los textos legales. Son plantillas generales, no asesoramiento jurídico.

## 2. Publicar gratis (Cloudflare Pages o Netlify)
1. Compra el dominio (DonDominio, Namecheap, Cloudflare…).
2. Crea una cuenta gratuita en https://pages.cloudflare.com o https://app.netlify.com
3. Crea un sitio nuevo y arrastra la carpeta `ahorrometro` completa.
4. En la configuración del sitio, añade tu dominio personalizado y sigue los pasos de DNS.

## 3. Google Search Console
1. Da de alta el dominio en https://search.google.com/search-console
2. Envía `https://ahorrometro.es/sitemap.xml` en el apartado «Sitemaps».
3. Cada vez que añadas una página nueva, añádela también al `sitemap.xml`.

## 4. AdSense
> Hecho el 7 de octubre de 2026: el script de AdSense (ID `ca-pub-8810566450749484`) está en todas las
> páginas y `ads.txt` en la raíz. El mensaje de consentimiento de Google (3 opciones) está activo y ha sustituido
> al banner propio: cada página fija en el `<head>` el modo de consentimiento («denegado» por defecto en el EEE,
> Reino Unido y Suiza) y el pie tiene el enlace «Configurar cookies». Pendiente: aprobación y bloques de anuncio (paso 5).

1. Regístrate en https://adsense.google.com con tu dominio.
2. AdSense te dará un script `<script async src="...adsbygoogle.js?client=ca-pub-...">`.
   Pégalo en cada página, donde está el comentario `<!-- ADSENSE: pega aquí el script de AdSense -->`.
3. Crea un archivo `ads.txt` en la raíz con la línea que te indique AdSense.
4. **Cookies:** en AdSense ve a «Privacidad y mensajes» y activa el mensaje de consentimiento
   de Google (RGPD, gratuito y obligatorio en la UE). Después elimina el banner propio
   (el bloque `cookie-banner` de cada página y su código en `assets/main.js`).
5. Cuando te aprueben, sustituye los bloques `<div class="ad-slot">…</div>` por tus bloques de anuncio,
   o activa los «Anuncios automáticos» y borra los huecos.

## 5. Añadir una calculadora nueva
1. Copia una existente de `calculadoras/` (por ejemplo `pintura.html`) con un nombre nuevo.
2. Cambia el título, la descripción, la URL canónica, el formulario, el script y los textos.
3. Añádela a la portada (`index.html`, sección `grid`), a `sitemap.xml` y a los enlaces relacionados.

## 6. Amazon Afiliados
- Los bloques «Ver precio en Amazon» (7 calculadoras) usan enlaces de búsqueda con el ID `albert671-21`.
- En Amazon Afiliados → **Configuración de la cuenta → Editar la lista de sitios web**, añade `https://ahorrometro.es`.
- Opcional: crea un ID propio (p. ej. `ahorrometro-21`) y pide a Claude que lo cambie, para medir las ventas de esta web por separado.
- Para cambiar un producto: edita el bloque `<section class="affiliate">` de la calculadora. Puedes sustituir el enlace de búsqueda
  por el de un producto concreto generado con SiteStripe.
- No pongas precios fijos junto a los productos: Amazon no lo permite si no se actualizan automáticamente.

### Ideas para las próximas calculadoras
- Consumo del termo eléctrico o de la bomba de calor
- Cuánto cuesta cargar un coche eléctrico
- Comparador de precio por kilo o por litro en el supermercado
- Calculadora de lavadoras al mes (agua + luz)
- Calefacción: gas frente a bomba de calor frente a pellets
- Ahorro por bajar 1 °C la calefacción
- Gasto de agua de la ducha frente al baño
- Cuánto ahorro cambiando a bombillas LED

## 7. Precio de la gasolina (se actualiza solo)
- La página `precio-gasolina-hoy.html` lee el archivo `datos/carburantes.json`.
- Ese archivo lo genera el proceso automático de GitHub **Precios de carburantes**
  (`.github/workflows/precios-carburantes.yml`) dos veces al día, con los datos del Ministerio.
  Cada actualización hace un commit en `main` y Cloudflare Pages la publica sola.
- Para forzar una actualización: en GitHub, pestaña **Actions → Precios de carburantes → Run workflow**.
- Si el proceso falla, GitHub te avisará por correo. La web seguirá mostrando los últimos precios guardados.
- La calculadora de viaje usa también este archivo para proponer el precio medio de España.
- El mismo proceso genera también una página por provincia en `gasolina/` (por ejemplo `gasolina/madrid.html`),
  la lista de provincias de `precio-gasolina-hoy.html` y sus entradas del `sitemap.xml`
  (entre los comentarios `PROVINCIAS:INICIO` y `PROVINCIAS:FIN`). No edites esas partes a mano:
  se sobrescriben en cada actualización. El diseño de esas páginas está en `scripts/paginas_provincia.py`.

## 8. Si cambias `style.css` o `main.js`
Cloudflare deja que los navegadores guarden estos archivos varias horas. Cuando los cambies,
sube el número de versión en todas las páginas (`style.css?v=2` → `style.css?v=3`, y lo mismo con
`main.js`), incluida la plantilla de `scripts/paginas_provincia.py`, para que los visitantes vean
el cambio al momento.

## 9. Precios que se actualizan solos en las calculadoras
- El mismo proceso automático guarda en `datos/luz.json` el precio medio de la luz (PVPC de Red Eléctrica)
  de las últimas 4 semanas, con impuestos, y el de las horas valle (`scripts/actualizar_luz.py`).
- Las casillas con `data-precio="luz"`, `"luz-valle"` o `"gasolina95"` toman ese valor al abrir la página
  (código en `assets/main.js`). Para que una casilla nueva se rellene sola, añádele ese atributo.
- Si la descarga de Red Eléctrica falla, el proceso sigue con la gasolina y las calculadoras usan el
  valor escrito en la página.
- Butano, gas natural, gasóleo C, pellets y leña no tienen una fuente oficial automática: sus precios
  siguen escritos a mano en cada calculadora. El butano cambia el tercer martes de enero, marzo, mayo,
  julio, septiembre y noviembre.

## 10. Páginas «¿Cuánto gasta…?»
- `scripts/paginas_consumo.py` genera `consumo-electrodomesticos.html` y una página por aparato en `cuanto-gasta/`
  con los costes calculados con el precio de la luz de `datos/luz.json`. Se regeneran solas en cada actualización.
- Para añadir un aparato, añádelo a la lista `APARATOS` del script. No edites esas páginas a mano.
