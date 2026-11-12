// Genera una imagen PNG de cada hoja que se ve en la web (src/img/) y su miniatura (src/img/mini/).
// Google Imágenes y Pinterest indexan estas imágenes; en la página se cambian por el SVG al imprimir.
// Uso: npm run imagenes  (con -- --nuevos solo crea las que faltan)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const sharp = require('sharp');
const P = require('../lib/puzzles.js');
const { paginas } = require('../content/index.js');

const raiz = path.join(__dirname, '..');
const fuentes = require('./fuentes.js');
const css = `
${fuentes}
html,body{margin:0;background:#fff}svg{display:block;width:620px;height:877px}`;

(async () => {
  const soloNuevas = process.argv.includes('--nuevas') || process.argv.includes('--nuevos');
  const dirG = path.join(raiz, 'src/img'), dirM = path.join(dirG, 'mini');
  fs.mkdirSync(dirM, { recursive: true });
  const nav = await chromium.launch();
  const grande = await nav.newPage({ viewport: { width: 620, height: 877 }, deviceScaleFactor: 2 });
  const mini = await nav.newPage({ viewport: { width: 620, height: 877 }, deviceScaleFactor: .5 });
  let n = 0;
  for (const p of paginas) {
    for (const h of p.hojas) {
      const fg = path.join(raiz, 'src', h.img), fm = path.join(raiz, 'src', h.mini);
      if (soloNuevas && fs.existsSync(fg) && fs.existsSync(fm)) continue;
      const html = `<!doctype html><meta charset="utf-8"><style>${css}</style>${P.render(h.spec, h.seed).svg}`;
      for (const [pag, destino] of [[grande, fg], [mini, fm]]) {
        await pag.setContent(html);
        await pag.evaluate(() => document.fonts.ready);
        const png = await pag.screenshot({ clip: { x: 0, y: 0, width: 620, height: 877 } });
        // PNG con paleta: en dibujos de línea apenas se nota y pesa entre un 50 y un 60 % menos
        await sharp(png).png({ palette: true, colors: 64, compressionLevel: 9, effort: 10 }).toFile(destino);
      }
      n++;
    }
  }
  await nav.close();
  console.log(n + ' imágenes generadas en src/img');
})();
