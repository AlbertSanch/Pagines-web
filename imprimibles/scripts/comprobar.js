// Comprobaciones antes de publicar: metadatos, enlaces internos y generadores.
const fs = require('fs');
const path = require('path');
const P = require('../lib/puzzles.js');
const { paginas } = require('../content/index.js');
const site = require('../src/_data/site.js');
let fallos = 0;
const mal = (m) => { fallos++; console.log('  ✗ ' + m); };

console.log('Metadatos');
const vistos = {};
for (const p of paginas) {
  if (p.title.length > 60) mal(`title de ${p.title.length} caracteres: ${p.url}`);
  if (p.desc.length > 158) mal(`description de ${p.desc.length} caracteres: ${p.url}`);
  if (vistos[p.title]) mal(`title repetido: ${p.url} y ${vistos[p.title]}`);
  vistos[p.title] = p.url;
  if (!p.cuerpo) mal(`sin texto: ${p.url}`);
  if (p.pdf && !fs.existsSync(path.join(__dirname, '../src', p.pdf))) mal(`falta el PDF (npm run pdfs): ${p.pdf}`);
}

console.log('Enlaces internos');
const urls = new Set(['/', '/sobre/', '/contacto/', '/aviso-legal/', '/privacidad/', '/cookies/', ...paginas.map((p) => p.url)]);
for (const p of paginas) {
  for (const m of (p.cuerpo + (p.entrada || '')).matchAll(/href="(\/[^"#]*)"/g)) if (!urls.has(m[1])) mal(`enlace roto en ${p.url}: ${m[1]}`);
}

console.log('Generadores (200 semillas por ficha aleatoria)');
const tipos = {};
for (const p of paginas) for (const h of p.hojas) {
  if (!h.aleatoria) continue;
  for (let s = 1; s <= 200; s++) {
    let r;
    try { r = P.render(h.spec, s * 7919); } catch (e) { mal(`${p.url} semilla ${s}: ${e.message}`); break; }
    if (h.spec.tipo === 'sopa') {
      const n = Number((r.svg.match(/Palabras escondidas \((\d+)\)/) || [])[1]);
      if (n < Math.min(h.spec.nPalabras, 8)) mal(`${p.url} semilla ${s}: solo caben ${n} palabras`);
      tipos.sopaMin = Math.min(tipos.sopaMin || 99, n - h.spec.nPalabras);
    }
  }
}
if (tipos.sopaMin < 0) console.log(`  aviso: alguna sopa coloca hasta ${-tipos.sopaMin} palabras menos de las pedidas`);

console.log('Configuración');
if (!site.legal.titular || !site.legal.nif) console.log('  aviso: faltan los datos legales en src/_data/site.js');
if (!site.adsenseId) console.log('  aviso: AdSense sin configurar (no se muestran anuncios)');
if (!site.amazonTag) console.log('  aviso: Amazon Afiliados sin configurar (no se muestran enlaces)');

console.log(fallos ? `\n${fallos} problema(s)` : '\nTodo correcto');
process.exit(fallos ? 1 : 0);
