// Pines para los feeds RSS de Pinterest (/pinterest/<tablero>.xml).
// Hace una imagen vertical (1000x1500, JPG) por cada ficha de las secciones con tablero y les pone fecha de publicación:
// el feed solo enseña los pines cuya fecha ya ha llegado, y Pinterest publica los nuevos al leerlo (una vez al día).
// El robot .github/workflows/imprimibles-pines.yml regenera la web cada pocos días para que aparezcan los siguientes.
//
// Uso: node scripts/pines_feed.js        (solo crea las imágenes que faltan; las fechas ya asignadas no cambian)
// Escribe src/_data/pinesFeed.json y las imágenes en src/pines/.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { paginas } = require('../content/index.js');

const RAIZ = path.join(__dirname, '..');
const DATOS = path.join(RAIZ, 'src/_data/pinesFeed.json');
const IMGS = path.join(RAIZ, 'src/pines');

// tablero: [categoría de la web, etiqueta de la imagen, primer día, cada cuántos días, último día (o null)]
const TABLEROS = {
  navidad: { nombre: 'Navidad para imprimir', cat: 'navidad', etiqueta: 'Navidad', desde: '2026-12-02', cada: 2, hasta: '2027-01-05' },
  calendarios: { nombre: 'Calendarios 2027', cat: 'calendarios', etiqueta: 'Calendario 2027', desde: '2026-12-02', cada: 2, hasta: '2027-02-28', filtro: (p) => !p.slug.startsWith('escolar-') },
  'calendario-escolar': { nombre: 'Calendario escolar 2026-2027', cat: 'calendarios', etiqueta: 'Curso 2026-2027', desde: '2026-12-02', cada: 1, hasta: null,
    filtro: (p) => p.slug.startsWith('escolar-'), orden: ['', 'madrid', 'cataluna', 'valenciana', 'andalucia-sevilla', 'andalucia-malaga', 'galicia', 'castilla-y-leon', 'pais-vasco', 'murcia', 'andalucia-cadiz', 'castilla-la-mancha-toledo', 'aragon-zaragoza', 'baleares', 'asturias', 'extremadura', 'andalucia-granada', 'andalucia-cordoba', 'andalucia-almeria'] },
  'estimulacion-cognitiva': { nombre: 'Estimulación cognitiva para mayores', cat: 'estimulacion-cognitiva', etiqueta: 'Mayores', desde: '2026-12-03', cada: 3, hasta: null }
};

// Pines que Albert ya programó a mano en Pinterest (25-28 nov): no van al feed para no repetirlos.
const YA_PUBLICADOS = new Set(['/navidad/calendario-de-adviento/', '/navidad/amigo-invisible/', '/navidad/etiquetas-regalos/', '/navidad/menu-de-navidad/',
  '/navidad/lista-de-regalos/', '/navidad/bingo/', '/navidad/carta-papa-noel/', '/navidad/carta-reyes-magos/']);

const sumarDias = (iso, n) => { const d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };

function candidatos(t) {
  // primero la primera ficha de cada página; después las demás
  const ps = paginas.filter((p) => p.cat === t.cat && (!t.filtro || t.filtro(p)));
  if (t.orden) {  // las páginas de la lista, en ese orden, antes que el resto
    const pos = (p) => { const i = t.orden.indexOf(p.slug.replace(/^escolar-\d{4}-\d{4}-?/, '')); return i < 0 ? 999 : i; };
    ps.sort((a, b) => pos(a) - pos(b));
  }
  const rondas = [];
  ps.forEach((p) => p.hojas.forEach((h, i) => {
    if (!h.hayImg || (i === 0 && YA_PUBLICADOS.has(p.url))) return;  // su primera ficha ya está en Pinterest
    (rondas[i] = rondas[i] || []).push({ p, h, i });
  }));
  return rondas.flat();
}

const fuente = (f) => 'file://' + path.join(RAIZ, 'src/fonts', f);
const css = `@font-face{font-family:Besley;font-weight:800;src:url(${fuente('besley-800.woff2')})}
@font-face{font-family:Andika;font-weight:400;src:url(${fuente('andika-400.woff2')})}
@font-face{font-family:Andika;font-weight:700;src:url(${fuente('andika-700.woff2')})}
*{box-sizing:border-box}html,body{margin:0;width:1000px;height:1500px;overflow:hidden}
body{background:#f4efe3;color:#1b1b1f;font-family:Andika,sans-serif;position:relative}
.rayas{position:absolute;inset:0;background:repeating-linear-gradient(180deg,transparent 0 47px,#e2d9c3 47px 48px)}
.cab{position:absolute;left:70px;right:70px;top:70px}
.etq{display:inline-block;background:#ffe14d;font:700 34px Andika;padding:4px 18px;border-radius:6px;transform:rotate(-1.5deg)}
h1{font:800 72px/1.05 Besley,serif;margin:26px 0 18px;letter-spacing:-.01em}
.sub{font:400 34px/1.3 Andika;color:#5d5b55}
.hoja{position:absolute;left:50%;top:600px;width:620px;margin-left:-310px;background:#fff;padding:14px;
 box-shadow:0 18px 40px rgba(0,0,0,.18),0 2px 6px rgba(0,0,0,.12);transform:rotate(2deg)}
.hoja img{display:block;width:100%}
.pie{position:absolute;left:0;right:0;bottom:0;height:120px;background:#2340b0;color:#fff;display:flex;align-items:center;justify-content:center;gap:24px;font:700 42px Andika}
.pie b{font:800 46px Besley,serif}`;

(async () => {
  const previo = fs.existsSync(DATOS) ? JSON.parse(fs.readFileSync(DATOS, 'utf8')) : { pines: [] };
  const hechos = new Map(previo.pines.map((x) => [x.id, x]));
  const pines = [];
  for (const [clave, t] of Object.entries(TABLEROS)) {
    let fecha = t.desde;
    const ultimas = previo.pines.filter((x) => x.tablero === clave).map((x) => x.fecha).sort();
    for (const { p, h, i } of candidatos(t)) {
      const id = clave + '-' + path.basename(h.img, '.png');
      if (hechos.has(id)) { pines.push(hechos.get(id)); continue; }  // los ya programados no cambian de fecha
      if (ultimas.length && fecha <= ultimas[ultimas.length - 1]) fecha = sumarDias(ultimas[ultimas.length - 1], t.cada);
      if (t.hasta && fecha > t.hasta) break;
      // título del pin: el de la página y, para las demás fichas, lo que las distingue («difícil», «con actividades»…)
      let resto = (h.spec.titulo || '').trim();
      for (const pre of [p.h1, p.corto || '', (p.corto || '').replace(/ para imprimir$/, '')]) {
        if (pre && resto.toLowerCase().startsWith(pre.toLowerCase())) { resto = resto.slice(pre.length).replace(/^[\s:·-]+/, ''); break; }
      }
      resto = resto.replace(/^\((.*)\)$/, '$1');
      const titulo = i === 0 ? p.h1 : resto ? `${p.h1} · ${resto}`.slice(0, 95) : `${p.h1} (modelo ${i + 1})`;
      pines.push({ id, tablero: clave, fecha, url: p.url, titulo, descripcion: p.desc, imagen: `/pines/${id}.jpg`, origen: h.img });
      ultimas.push(fecha);
      fecha = sumarDias(fecha, t.cada);
    }
  }
  fs.mkdirSync(IMGS, { recursive: true });
  const nav = await chromium.launch();
  const pag = await nav.newPage({ viewport: { width: 1000, height: 1500 } });
  let nuevas = 0;
  for (const x of pines) {
    const destino = path.join(RAIZ, 'src', x.imagen);
    if (fs.existsSync(destino)) continue;
    const t = TABLEROS[x.tablero];
    const p = paginas.find((q) => q.url === x.url);
    const html = path.join(IMGS, '_pin.html');
    const titulo = x.titulo.length <= 60 && x.tablero !== 'calendario-escolar' ? x.titulo : p.corto && p.corto.length <= 45 ? p.corto : p.h1;
    fs.writeFileSync(html, `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="rayas"></div>
<div class="cab"><span class="etq">${t.etiqueta}</span><h1>${titulo}</h1><div class="sub">Descárgalo gratis en PDF, listo para imprimir</div></div>
<div class="hoja"><img src="file://${path.join(RAIZ, 'src', x.origen)}"></div><div class="pie"><b>imprimibles.es</b> · gratis para imprimir</div>`);
    await pag.goto('file://' + html);
    await pag.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images].map((im) => im.decode().catch(() => {}))]));
    await pag.screenshot({ path: destino, type: 'jpeg', quality: 82 });
    nuevas++;
  }
  fs.rmSync(path.join(IMGS, '_pin.html'), { force: true });
  await nav.close();
  fs.writeFileSync(DATOS, JSON.stringify({ tableros: Object.fromEntries(Object.entries(TABLEROS).map(([k, t]) => [k, t.nombre])), pines }, null, 1) + '\n');
  const resumen = Object.keys(TABLEROS).map((k) => { const xs = pines.filter((x) => x.tablero === k); return `${k}: ${xs.length} pines, hasta el ${xs[xs.length - 1].fecha}`; });
  console.log(`${nuevas} imágenes nuevas. ${resumen.join(' · ')}`);
})();
