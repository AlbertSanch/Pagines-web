// Reúne todas las páginas de contenido y calcula lo que necesitan las plantillas.
const P = require('../lib/puzzles.js');
const crudas = [
  ...require('./sopas.js'),
  ...require('./logica.js'),
  ...require('./escuela.js')
];

const paginas = crudas.map((p) => {
  const url = '/' + p.cat + '/' + (p.slug ? p.slug + '/' : '');
  const base = P.hash(url);
  const hojas = (p.hojas || []).map((spec, i) => {
    const seed = (base + i * 101) >>> 0;
    return { spec, seed, json: JSON.stringify(spec), aleatoria: P.esAleatorio(spec), svg: P.render(spec, seed).svg, tieneSol: !!P.render(spec, seed).sol };
  });
  const pdf = hojas.length ? '/pdf/' + (p.slug ? p.cat + '-' + p.slug : p.cat) + '.pdf' : null;
  const aleatoria = hojas.some((h) => h.aleatoria);
  const nSol = hojas.filter((h) => h.tieneSol).length;
  const copias = aleatoria ? (p.copias || 1) : 1;
  return Object.assign({}, p, {
    url, base, hojas, pdf, aleatoria, copias,
    tieneSol: nSol > 0,
    pdfHojas: hojas.length * copias,
    pdfSoluciones: nSol * copias,
    esHub: !p.slug
  });
});

const secciones = paginas.filter((p) => p.esHub).map((hub) => ({
  cat: hub.cat, nombre: hub.nav, url: hub.url, resumen: hub.resumen,
  hijas: paginas.filter((p) => p.cat === hub.cat && !p.esHub)
}));

module.exports = { paginas, secciones };
