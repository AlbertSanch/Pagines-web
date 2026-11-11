# imprimibles.es

Pasatiempos y fichas para imprimir: sopas de letras, sudokus, laberintos, bingo, tablas de multiplicar, sumas y restas y papel pautado. 45 páginas de contenido, la portada y 5 páginas legales.

## Cómo está hecho y por qué

- **Eleventy (generador estático).** La web es HTML plano: carga rápido, se aloja gratis y no hay base de datos ni servidor que mantener. Cada página pesa unos 10 KB comprimida, con el CSS incrustado y tres tipografías autoalojadas.
- **Un solo generador de fichas** (`lib/puzzles.js`) que se usa en dos sitios: al compilar, para dibujar la ficha que ve Google y el visitante, y en el navegador, para el botón «Otra distinta». Cada ficha es un SVG de 210 × 297 mm.
- **PDF reales**, generados en local con `npm run pdfs` y guardados en `src/pdf/`. El hosting no necesita navegador.
- **Sin cookies propias ni analítica** hasta que actives AdSense.

## Órdenes

```bash
npm install
```

```bash
npm start
```

Abre la web en `http://localhost:8080` y recompila al guardar.

```bash
npm run pdfs
```

Regenera todos los PDF, `og.png` y los iconos. Hazlo cada vez que añadas o cambies fichas (con `-- --nuevos` solo crea los que faltan). Necesita Playwright con Chromium (`npm i -D playwright && npx playwright install chromium`).

```bash
npm run comprobar
```

Revisa longitudes de title y description, enlaces internos rotos, PDF que faltan y prueba 200 semillas de cada generador.

```bash
npm run build
```

Deja la web lista en `_site/`.

## Crear páginas nuevas (la plantilla)

No hay que tocar HTML. Cada página es un objeto en `content/sopas.js`, `content/logica.js` o `content/escuela.js`:

```js
{
  cat: 'sopas-de-letras',          // sección (carpeta de la URL)
  slug: 'verano',                  // URL final: /sopas-de-letras/verano/
  corto: 'Verano',                 // nombre en índices y migas
  title: '…',                      // máx. 60 caracteres
  desc: '…',                       // máx. 155 caracteres
  h1: '…',
  entrada: '…',                    // primer párrafo
  hojas: [{ tipo: 'sopa', titulo: '…', nivel: 'medio', tam: 13, nPalabras: 14, palabras: [/* … */] }],
  copias: 2,                       // variantes de cada hoja en el PDF
  cuerpo: `<h2>…</h2><p>…</p>`,    // texto de la página
  faq: [['Pregunta', 'Respuesta']],            // opcional
  amazon: [['Texto del enlace', 'búsqueda']]   // opcional
}
```

Para una **sopa de letras temática** es aún más corto: añade un bloque a la lista `temas` de `content/sopas.js` (slug, nombre, palabras y dos frases) y el resto se rellena solo.

Tipos de hoja disponibles: `sopa`, `sudoku`, `laberinto`, `bingo90`, `bingo75`, `bingo-numeros`, `tabla`, `tablas-todas`, `pitagorica`, `mult-practica`, `operaciones` y `papel`. Los parámetros de cada uno están en los ejemplos de `content/`.

Después de añadir páginas: `npm run pdfs -- --nuevos`, `npm run comprobar` y publicar. El índice, las migas, el sitemap y los datos estructurados se actualizan solos.

## Arquitectura SEO

- **Portada** → 7 secciones → fichas. Toda página está a dos clics de la portada.
- **Enlazado interno:** menú con las 7 secciones, índice de la sección en cada página central, «Más en…» con las hermanas en cada ficha, lateral con las otras secciones y enlaces contextuales en el texto.
- **URL:** `/seccion/` y `/seccion/ficha/`.
- **Datos estructurados:** `WebSite` y `Organization` en la portada; `BreadcrumbList` en todas; `LearningResource` (con el PDF como `MediaObject`) en cada ficha; `CollectionPage` en las secciones; `FAQPage` donde hay preguntas.
- **Otros:** `sitemap.xml`, `robots.txt`, canonical, Open Graph, página 404, cabeceras de caché (`_headers`). Los PDF llevan `noindex` para que posicione la página y no el archivo.

## Antes de publicar: `src/_data/site.js`

| Campo | Qué poner |
|---|---|
| `legal.titular`, `nif`, `domicilio`, `email` | Obligatorio. Mientras falten, el aviso legal muestra `[PENDIENTE: …]` |
| `adsenseId` | Tu `ca-pub-…`. Vacío = sin anuncios ni huecos |
| `adsSlots` | Los tres bloques que crees en AdSense: `contenido`, `lateral`, `final` |
| `amazonTag` | Tu tag de Amazon.es. Vacío = sin enlaces de afiliado |
| `cfBeacon` | Opcional: token de Cloudflare Web Analytics (sin cookies) |

Los textos legales son una plantilla razonable, no asesoría jurídica: revísalos con tus datos reales.

## Publicar

1. **Dominio.** Registra `imprimibles.es` (y `imprimible.es` para redirigirlo). Unos 8-10 € al año en cualquier registrador español.
2. **Repositorio.** Sube esta carpeta a un repositorio privado de GitHub.
3. **Hosting: Cloudflare Pages** (gratis). Crea un proyecto conectado al repositorio con orden de compilación `npm run build` y directorio de salida `_site`. Cada `git push` publica.
4. **Dominio en Cloudflare.** En el proyecto, «Custom domains» → `imprimibles.es` y `www.imprimibles.es`; redirige `www` al dominio sin `www`.
5. **Correo.** Crea `hola@imprimibles.es` con Cloudflare Email Routing (gratis), reenviado a tu correo.
6. **Google Search Console.** Añade la propiedad de dominio (verificación por DNS), envía `https://imprimibles.es/sitemap.xml` y pide la indexación de la portada y las 7 secciones.
7. **Bing Webmaster Tools.** Importa la propiedad desde Search Console.

## AdSense

1. Solicita la revisión con la web ya publicada y los datos legales rellenos. Pon tu `ca-pub-…` en `adsenseId` y deja `adsSlots` vacío: así se carga el script que Google necesita para verificar la web, pero no aparece ningún hueco de anuncio.
2. Al aprobarte, crea tres bloques adaptables (contenido, lateral, final), copia sus identificadores en `adsSlots` y publica. Se genera `ads.txt` automáticamente.
3. **Consentimiento (RGPD).** En AdSense, «Privacidad y mensajes» → crea el mensaje de consentimiento europeo con tres opciones (aceptar, rechazar, gestionar). Es la plataforma de Google, certificada por Google y por IAB TCF, gratuita, y se sirve con el mismo script de AdSense: no hay que añadir código. El enlace «Configurar cookies» del pie ya la reabre. Por eso la web no lleva un banner propio: un banner hecho a mano no está certificado y Google no lo acepta para servir anuncios en la UE. Alternativas certificadas si prefieres otra: CookieYes o Cookiebot.
4. Los huecos tienen altura reservada (280 px en contenido, 600 px en el lateral de escritorio), así que el texto no salta al cargar. No se imprimen.

## Amazon Afiliados

Encaja solo en parte del nicho, así que está limitado a un recuadro «Material que viene bien» en las páginas donde tiene sentido (bombo y fichas en bingo, fundas de plastificar y rotuladores borrables en tablas, cuadernos de música en pentagramas…). Los enlaces son búsquedas de Amazon.es con tu tag, marcados con `rel="sponsored nofollow"`, con aviso junto al recuadro, en el pie y en el aviso legal. No actives el tag hasta tener tráfico: Amazon cierra las cuentas sin ventas en 180 días.
