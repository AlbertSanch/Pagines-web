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

## 4. Pedir AdSense (cuando tengas unas 20–30 páginas)
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
- Metros cúbicos de hormigón, sacos de cemento o mortero
- Papel pintado: rollos necesarios
- Ahorro por bajar 1 °C la calefacción
- Gasto de agua de la ducha frente al baño
- Cuánto ahorro cambiando a bombillas LED
