# OjoMascota — siguientes pasos

Esta carpeta contiene una web estática lista para publicar: comparativa de cámaras para vigilar mascotas + 3 páginas legales. No necesita ningún servidor especial, solo archivos HTML/CSS.

## 1. Elegir y comprar un dominio

Algunas ideas de nombre (comprueba disponibilidad real al comprarlo, la disponibilidad cambia constantemente):

- ojomascota.com
- vigilamimascota.com
- camaraparamimascota.com
- mimascotaencasa.com
- guardianmascota.es

Regístralo en Namecheap, Porkbun o IONOS (los tres son fiables y baratos, ~8-15€/año). Evita registradores que te obliguen a contratar hosting junto con el dominio si vas a usar hosting gratuito.

## 2. Publicar la web gratis con Netlify (recomendado, el más sencillo)

1. Crea una cuenta gratuita en netlify.com.
2. Arrastra esta carpeta completa (`camara-mascotas-site`) a la zona "Deploy manually" del panel de Netlify, o conecta un repositorio de GitHub si prefieres control de versiones.
3. Netlify te dará una URL tipo `algo-random.netlify.app`. Ve a "Domain settings" → "Add custom domain" y añade tu dominio comprado en el paso 1.
4. Netlify te indicará los registros DNS (normalmente un CNAME o un ALIAS) que debes configurar en el panel de tu registrador de dominio. Tarda entre unos minutos y unas horas en propagarse.

Alternativa equivalente: GitHub Pages (gratis, requiere subir esta carpeta a un repositorio de GitHub y activar Pages en la configuración del repo).

## 3. Crear tu cuenta de Amazon Afiliados (Amazon Associates)

Esto lo tienes que hacer tú directamente en https://afiliados.amazon.es, porque requiere tus datos personales/fiscales y datos bancarios para cobrar las comisiones — es información que no debo introducir por ti.

Pasos:
1. Regístrate con tu cuenta de Amazon habitual.
2. Cuando te pidan la URL de tu web, usa la de tu dominio ya publicado (mejor esperar a tener el sitio en vivo antes de solicitarlo).
3. Amazon suele pedir que generes algunas ventas de prueba en los primeros 180 días para mantener la cuenta activa — no publiques la web y la dejes sin promoción, intenta compartirla o hacer algo de SEO desde el primer día.
4. Una vez aprobado, te darán un "ID de seguimiento" (Tracking ID), con formato parecido a `tunombre-21`.

## 4. Sustituir los enlaces de afiliado (muy importante)

En `index.html` verás 3 botones "Ver precio actual en Amazon" con el atributo `href="#"` y `data-affiliate-slot="..."`. Son placeholders a propósito: **no he inventado ningún enlace ni ASIN de producto**, porque un enlace de afiliado mal generado no cuenta la venta y no cobras la comisión.

Para generarlos correctamente una vez tengas la cuenta aprobada:
1. Instala la barra SiteStripe de Amazon (aparece automáticamente arriba de Amazon.es cuando inicias sesión con tu cuenta de afiliado).
2. Busca cada producto exacto que quieras enlazar (Tapo C21A, Tapo C220, Furbo) en Amazon.es.
3. Haz clic en "Texto" o "Enlace corto" en la barra SiteStripe: te genera automáticamente la URL con tu Tracking ID incluido.
4. Sustituye el `href="#"` de cada botón en `index.html` por ese enlace real.

Guarda también los ASIN y precios reales que veas en ese momento — los precios de este comparativa son orientativos (verificados en septiembre 2026) y hay que mantenerlos razonablemente actualizados.

## 5. Antes de publicar, rellena los datos legales

En `aviso-legal.html` y `politica-privacidad.html` hay campos entre corchetes `[...]` con tu nombre/razón social, NIF, dirección y correo. Es obligatorio por la LSSICE tener estos datos identificativos visibles en cualquier web con actividad comercial (incluida la afiliación).

## 6. Ideas de contenido para las próximas semanas

Una sola página no basta para posicionar en Google a medio plazo. Próximos artículos sugeridos, todos dentro del mismo ángulo (mascotas solas en casa):

- "Cómo saber si tu perro tiene ansiedad por separación (y cómo ayudarle con una cámara)"
- "Cámara con dispensador de premios: ¿merece la pena o es solo marketing?"
- "Cámara para vigilar a tu gato: diferencias con las cámaras para perros"
- Reseña individual más extensa de cada uno de los 3 productos comparados

Si quieres, en la próxima sesión puedo ayudarte a redactar estos artículos siguiendo la misma estructura y estilo que la página de inicio.
