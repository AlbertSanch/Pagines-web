// Genera los PDF descargables (src/pdf/*.pdf) y las imágenes para redes e iconos.
// Se ejecuta en local con `npm run pdfs` cuando se añaden o cambian fichas;
// los PDF se guardan en el repositorio, así el hosting no necesita navegador.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const P = require('../lib/puzzles.js');
const { paginas } = require('../content/index.js');

const raiz = path.join(__dirname, '..');
const fuente = (f) => 'file://' + path.join(raiz, 'src/fonts', f);
const css = `
@font-face{font-family:Besley;src:url(${fuente('besley-800.woff2')});font-weight:800}
@font-face{font-family:"Andika";src:url(${fuente('andika-400.woff2')});font-weight:400}
@font-face{font-family:"Andika";src:url(${fuente('andika-700.woff2')});font-weight:700}
@page{size:A4;margin:0}html,body{margin:0}
svg{display:block;width:210mm;height:296.5mm;break-after:page}`;

(async () => {
  const soloNuevos = process.argv.includes('--nuevos');
  const dir = path.join(raiz, 'src/pdf');
  fs.mkdirSync(dir, { recursive: true });
  const navegador = await chromium.launch();
  const pag = await navegador.newPage();
  let hechos = 0;
  for (const p of paginas) {
    if (!p.pdf) continue;
    const destino = path.join(dir, path.basename(p.pdf));
    if (soloNuevos && fs.existsSync(destino)) continue;
    const fichas = [], soluciones = [];
    for (let v = 0; v < p.copias; v++) {
      p.hojas.forEach((h) => {
        if (v > 0 && !h.aleatoria) return;
        const r = P.render(h.spec, (h.seed + v * 7919) >>> 0);
        fichas.push(r.svg);
        if (r.sol) soluciones.push(r.sol);
      });
    }
    await pag.setContent(`<!doctype html><meta charset="utf-8"><title>${p.h1}</title><style>${css}</style>${fichas.join('')}${soluciones.join('')}`);
    await pag.evaluate(() => document.fonts.ready);
    await pag.pdf({ path: destino, format: 'A4', printBackground: true });
    hechos++;
  }
  console.log(hechos + ' PDF generados en src/pdf');

  // Imagen para compartir (1200 × 630) e iconos
  const est = path.join(raiz, 'src/static');
  const hoja = (spec, seed) => P.render(spec, seed).svg;
  await pag.setViewportSize({ width: 1200, height: 630 });
  await pag.setContent(`<!doctype html><style>
@font-face{font-family:Besley;src:url(${fuente('besley-800.woff2')});font-weight:800}
@font-face{font-family:"Andika";src:url(${fuente('andika-700.woff2')});font-weight:700}
body{margin:0;width:1200px;height:630px;background:#f4efe3;overflow:hidden;position:relative;font-family:"Andika"}
h1{font:800 84px/1.02 Besley;margin:0;position:absolute;left:70px;top:150px;width:560px;letter-spacing:-.02em;color:#1b1b1f}
p{position:absolute;left:70px;top:70px;margin:0;font:800 40px Besley;color:#1b1b1f}p b{color:#c42e21}
small{position:absolute;left:70px;bottom:70px;font-size:26px;letter-spacing:.12em;text-transform:uppercase;color:#c42e21;font-weight:700}
div{position:absolute;width:330px;background:#fff;box-shadow:0 0 0 1px rgba(0,0,0,.2),0 24px 30px -18px rgba(0,0,0,.6)}div svg{display:block;width:100%;height:auto}
.a{left:650px;top:150px;transform:rotate(-7deg)}.b{left:850px;top:60px;transform:rotate(5deg)}.c{left:745px;top:210px;transform:rotate(-1.5deg)}
</style><p>imprimibles<b>.es</b></p><h1>Pasatiempos y fichas para imprimir</h1><small>A4 · PDF · con solución</small>
<div class="a">${hoja({ tipo: 'laberinto', titulo: 'Laberinto', cols: 14, filas: 17, nombre: false }, 2027)}</div>
<div class="b">${hoja({ tipo: 'sudoku', n: 9, nivel: 'facil', titulo: 'Sudokus fáciles' }, 41)}</div>
<div class="c">${hoja({ tipo: 'sopa', titulo: 'Sopa de letras', nivel: 'medio', tam: 11, nPalabras: 12, nombre: false, palabras: ['lápiz', 'goma', 'cuaderno', 'tijeras', 'regla', 'folio', 'carpeta', 'estuche', 'papel', 'tinta', 'ficha', 'hoja', 'sobre', 'grapa', 'sello', 'clip'] }, 7)}</div>`);
  await pag.evaluate(() => document.fonts.ready);
  await pag.screenshot({ path: path.join(est, 'og.png') });
  const icono = fs.readFileSync(path.join(est, 'favicon.svg'), 'utf8');
  for (const n of [180, 512]) {
    await pag.setViewportSize({ width: n, height: n });
    await pag.setContent(`<style>body{margin:0}svg{display:block;width:${n}px;height:${n}px}</style>${icono}`);
    await pag.screenshot({ path: path.join(est, `icono-${n}.png`) });
  }
  await navegador.close();
  console.log('og.png e iconos actualizados');
})();
