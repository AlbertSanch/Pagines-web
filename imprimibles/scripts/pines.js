// Imágenes verticales (1000x1500) para Pinterest a partir de las fichas de la web, con el estilo de imprimibles.es.
// Uso: node scripts/pines.js CARPETA_DE_SALIDA
// Escribe un PNG por pin y pines.txt con el título, la descripción y el enlace de cada uno.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { paginas } = require('../content/index.js');

const RAIZ = path.join(__dirname, '..');
const DOMINIO = 'https://imprimibles.es';

// [URL de la página, etiqueta de arriba, título grande, subtítulo, tablero de Pinterest]
const PINES = [
  ['/calendarios/', 'Calendario 2027', 'Calendario 2027 para imprimir', 'Una hoja A4 con los festivos nacionales · PDF gratis', 'Calendarios 2027'],
  ['/calendarios/mensual-2027/', 'Calendario 2027', 'Calendario mensual 2027', 'Un mes por hoja con sitio para apuntar · PDF gratis', 'Calendarios 2027'],
  ['/calendarios/2027-con-semanas/', 'Calendario 2027', 'Calendario 2027 con números de semana', 'Para la oficina y la planificación · PDF gratis', 'Calendarios 2027'],
  ['/calendarios/2027-madrid/', 'Calendario 2027', 'Calendario 2027 de Madrid con festivos', 'Anual y mes a mes · PDF y Excel gratis', 'Calendarios 2027'],
  ['/calendarios/2027-andalucia/', 'Calendario 2027', 'Calendario 2027 de Andalucía con festivos', 'Anual y mes a mes · PDF y Excel gratis', 'Calendarios 2027'],
  ['/navidad/carta-reyes-magos/', 'Navidad', 'Carta a los Reyes Magos para imprimir', 'Varios modelos para que los niños escriban · gratis', 'Navidad para imprimir'],
  ['/navidad/carta-papa-noel/', 'Navidad', 'Carta a Papá Noel para imprimir', 'Lista para que los niños la rellenen · gratis', 'Navidad para imprimir'],
  ['/navidad/bingo/', 'Navidad', 'Bingo de Navidad para imprimir', 'Cartones con dibujos para jugar en familia · gratis', 'Navidad para imprimir'],
  ['/estimulacion-cognitiva/deterioro-leve/', 'Mayores', 'Fichas de estimulación cognitiva', 'Para mayores con deterioro cognitivo leve · PDF gratis', 'Estimulación cognitiva para mayores'],
  ['/navidad/calendario-de-adviento/', 'Navidad', 'Calendario de Adviento para imprimir', 'Del 1 al 24 de diciembre, con actividades en familia · gratis', 'Navidad para imprimir'],
  ['/navidad/amigo-invisible/', 'Navidad', 'Amigo invisible para imprimir', 'Papelitos para el sorteo y hoja para organizarlo · gratis', 'Navidad para imprimir'],
  ['/navidad/etiquetas-regalos/', 'Navidad', 'Etiquetas para regalos de Navidad', '12 por hoja, para recortar y colorear · gratis', 'Navidad para imprimir'],
  ['/navidad/menu-de-navidad/', 'Navidad', 'Menú de Nochebuena y Nochevieja', 'Plantillas para la mesa, para rellenar a mano · gratis', 'Navidad para imprimir'],
  ['/navidad/lista-de-regalos/', 'Navidad', 'Lista de regalos de Navidad', 'Para quién, qué regalo y cuánto cuesta · gratis', 'Navidad para imprimir'],
  ['/estimulacion-cognitiva/dinamicas-grupales/', 'Mayores', 'Dinámicas de grupo para mayores', 'Juegos para trabajar la memoria en residencias y centros de día · gratis', 'Estimulación cognitiva para mayores'],
];

const fuente = (f) => 'file://' + path.join(RAIZ, 'src/fonts', f);
const css = `@font-face{font-family:Besley;font-weight:800;src:url(${fuente('besley-800.woff2')})}
@font-face{font-family:Andika;font-weight:400;src:url(${fuente('andika-400.woff2')})}
@font-face{font-family:Andika;font-weight:700;src:url(${fuente('andika-700.woff2')})}
*{box-sizing:border-box}html,body{margin:0;width:1000px;height:1500px;overflow:hidden}
body{background:#f4efe3;color:#1b1b1f;font-family:Andika,sans-serif;position:relative}
.rayas{position:absolute;inset:0;background:repeating-linear-gradient(180deg,transparent 0 47px,#e2d9c3 47px 48px)}
.cab{position:absolute;left:70px;right:70px;top:70px}
.etq{display:inline-block;background:#ffe14d;font:700 34px Andika;padding:4px 18px;border-radius:6px;transform:rotate(-1.5deg)}
h1{font:800 76px/1.05 Besley,serif;margin:26px 0 18px;letter-spacing:-.01em}
.sub{font:400 34px/1.3 Andika;color:#5d5b55}
.hoja{position:absolute;left:50%;top:560px;width:640px;margin-left:-320px;background:#fff;padding:14px;
 box-shadow:0 18px 40px rgba(0,0,0,.18),0 2px 6px rgba(0,0,0,.12);transform:rotate(2deg)}
.hoja img{display:block;width:100%}
.pie{position:absolute;left:0;right:0;bottom:0;height:120px;background:#2340b0;color:#fff;display:flex;align-items:center;justify-content:center;gap:24px;font:700 42px Andika}
.pie b{font:800 46px Besley,serif}`;

(async () => {
  const salida = path.resolve(process.argv[2] || 'pines');
  fs.mkdirSync(salida, { recursive: true });
  const nav = await chromium.launch();
  const pag = await nav.newPage({ viewport: { width: 1000, height: 1500 } });
  let txt = '';
  for (const [i, [url, etq, titulo, sub, tablero]] of PINES.entries()) {
    const p = paginas.find((x) => x.url === url);
    if (!p || !p.imagen) throw new Error('Sin página o sin imagen: ' + url);
    const img = 'file://' + path.join(RAIZ, 'src', p.imagen);
    // se abre como archivo (no con setContent) para que pueda cargar las fuentes y la ficha del disco
    const html = path.join(salida, '_pin.html');
    fs.writeFileSync(html, `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="rayas"></div>
<div class="cab"><span class="etq">${etq}</span><h1>${titulo}</h1><div class="sub">${sub}</div></div>
<div class="hoja"><img src="${img}"></div><div class="pie"><b>imprimibles.es</b> · gratis para imprimir</div>`);
    await pag.goto('file://' + html);
    await pag.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images].map((im) => im.decode().catch(() => {}))]));
    const nombre = String(i + 1).padStart(2, '0') + '-' + url.replace(/\W+/g, '-').replace(/^-|-$/g, '') + '.png';
    await pag.screenshot({ path: path.join(salida, nombre) });
    txt += `${nombre}\nTablero: ${tablero}\nTítulo: ${titulo}\nDescripción: ${p.desc}\nEnlace: ${DOMINIO}${url}\n\n`;
  }
  fs.writeFileSync(path.join(salida, 'pines.txt'), txt);
  fs.rmSync(path.join(salida, '_pin.html'), { force: true });
  await nav.close();
  console.log(PINES.length + ' pines en ' + salida);
})();
