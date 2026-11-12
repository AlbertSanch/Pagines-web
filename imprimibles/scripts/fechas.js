// Mantiene src/_data/fechas.json: la fecha en que cambió por última vez el contenido de cada página.
// Guarda una huella (hash) del contenido; si cambia, apunta la fecha de hoy. Ejecútalo antes de publicar
// (npm run fechas). El sitemap y los datos estructurados usan estas fechas.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { paginas } = require('../content/index.js');

const raiz = path.join(__dirname, '..');
const archivo = path.join(raiz, 'src/_data/fechas.json');
const previas = fs.existsSync(archivo) ? JSON.parse(fs.readFileSync(archivo, 'utf8')) : {};
const hoy = new Date().toISOString().slice(0, 10);
const huella = (t) => crypto.createHash('sha1').update(t).digest('hex').slice(0, 12);

const actuales = {};
for (const p of paginas) {
  actuales[p.url] = huella(JSON.stringify([p.title, p.desc, p.h1, p.entrada, p.antes, p.cuerpo, p.faq, p.hojas.map((h) => h.json), p.copias]));
}
// Páginas fijas: la huella es el contenido de su plantilla
const fijas = { '/sobre/': 'sobre.njk', '/contacto/': 'contacto.njk', '/aviso-legal/': 'aviso-legal.njk', '/privacidad/': 'privacidad.njk', '/cookies/': 'cookies.njk', '/': 'index.njk' };
for (const [url, f] of Object.entries(fijas)) actuales[url] = huella(fs.readFileSync(path.join(raiz, 'src', f), 'utf8'));

const salida = {};
let cambios = 0;
for (const [url, h] of Object.entries(actuales)) {
  if (previas[url] && previas[url].huella === h) salida[url] = previas[url];
  else { salida[url] = { fecha: hoy, huella: h }; cambios++; }
}
fs.writeFileSync(archivo, JSON.stringify(salida, null, 1) + '\n');
console.log(cambios + ' páginas con fecha nueva (' + hoy + ')');
