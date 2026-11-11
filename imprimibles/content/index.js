// Reúne todas las páginas de contenido y calcula lo que necesitan las plantillas.
const P = require('../lib/puzzles.js');
const crudas = [
  ...require('./navidad.js'),
  ...require('./sopas.js'),
  ...require('./crucigramas.js'),
  ...require('./mandalas.js'),
  ...require('./logica.js'),
  ...require('./escuela.js'),
  ...require('./multdiv.js'),
  ...require('./caligrafia.js')
];

const paginas = crudas.map((p) => {
  const url = '/' + p.cat + '/' + (p.slug ? p.slug + '/' : '');
  const base = P.hash(url);
  const hojas = (p.hojas || []).map((spec, i) => {
    const seed = (base + i * 101) >>> 0;
    return { spec, seed, json: JSON.stringify(spec), aleatoria: P.esAleatorio(spec), svg: P.render(spec, seed).svg, tieneSol: !!P.render(spec, seed).sol };
  });
  const extra = (p.pdfExtra || []).map((spec, i) => {
    const seed = (base + (100 + i) * 101) >>> 0;
    return { spec, seed, aleatoria: P.esAleatorio(spec), tieneSol: !!P.render(spec, seed).sol };
  });
  const pdf = hojas.length ? '/pdf/' + (p.slug ? p.cat + '-' + p.slug : p.cat) + '.pdf' : null;
  const aleatoria = hojas.some((h) => h.aleatoria);
  const nSol = hojas.filter((h) => h.tieneSol).length;
  const copias = aleatoria ? (p.copias || 1) : 1;
  return Object.assign({}, p, {
    url, base, hojas, pdf, aleatoria, copias,
    tieneSol: nSol > 0,
    hojasExtra: extra,
    pdfHojas: hojas.concat(extra).reduce((n, h) => n + (h.aleatoria ? copias : 1), 0),
    pdfSoluciones: hojas.concat(extra).reduce((n, h) => n + (h.tieneSol ? (h.aleatoria ? copias : 1) : 0), 0),
    esHub: !p.slug
  });
});

// Orden del menú y del índice de la portada (las que no estén aquí van al final)
const ORDEN = ['navidad', 'sopas-de-letras', 'crucigramas', 'mandalas', 'sudokus', 'laberintos', 'bingo', 'tablas-de-multiplicar', 'sumas-y-restas', 'multiplicaciones-y-divisiones', 'caligrafia', 'papel'];
const pos = (c) => (ORDEN.indexOf(c) + 1) || 99;
const secciones = paginas.filter((p) => p.esHub).sort((a, b) => pos(a.cat) - pos(b.cat)).map((hub) => ({
  cat: hub.cat, nombre: hub.nav, url: hub.url, resumen: hub.resumen,
  hijas: paginas.filter((p) => p.cat === hub.cat && !p.esHub)
}));

module.exports = { paginas, secciones };
