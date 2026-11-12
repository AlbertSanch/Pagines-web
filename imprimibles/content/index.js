// Reúne todas las páginas de contenido y calcula lo que necesitan las plantillas.
const fs = require('fs');
const path = require('path');
const P = require('../lib/puzzles.js');
const slug = (t) => t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ñ/g, 'n').replace(/×/g, 'x').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const crudas = [
  ...require('./navidad.js'),
  ...require('./sopas.js'),
  ...require('./crucigramas.js'),
  ...require('./mandalas.js'),
  ...require('./logica.js'),
  ...require('./escuela.js'),
  ...require('./multdiv.js'),
  ...require('./caligrafia.js'),
  ...require('./calendarios.js')
];

const paginas = crudas.map((p) => {
  const url = '/' + p.cat + '/' + (p.slug ? p.slug + '/' : '');
  const base = P.hash(url);
  const nombreBase = slug(p.h1);
  const hojas = (p.hojas || []).map((spec, i) => {
    const seed = (base + i * 101) >>> 0;
    const archivo = nombreBase + (i ? '-' + (i + 1) : '') + '.png';
    const titulo = spec.titulo || spec.alt || p.h1;
    return {
      spec, seed, json: JSON.stringify(spec), aleatoria: P.esAleatorio(spec), svg: P.render(spec, seed).svg, tieneSol: !!P.render(spec, seed).sol,
      img: '/img/' + archivo, mini: '/img/mini/' + archivo,
      alt: (titulo === p.h1 ? p.h1 : p.h1 + ': ' + titulo.charAt(0).toLowerCase() + titulo.slice(1)) + ' (ficha para imprimir)',
      hayImg: fs.existsSync(path.join(__dirname, '../src/img', archivo))
    };
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
    esHub: !p.slug,
    imagen: hojas.length && hojas[0].hayImg ? hojas[0].img : null,
    mini: hojas.length && hojas[0].hayImg ? hojas[0].mini : null
  });
});

// Orden del menú y del índice de la portada (las que no estén aquí van al final)
const ORDEN = ['navidad', 'sopas-de-letras', 'crucigramas', 'mandalas', 'sudokus', 'laberintos', 'bingo', 'tablas-de-multiplicar', 'sumas-y-restas', 'multiplicaciones-y-divisiones', 'caligrafia', 'calendarios', 'papel'];
const pos = (c) => (ORDEN.indexOf(c) + 1) || 99;
const secciones = paginas.filter((p) => p.esHub).sort((a, b) => pos(a.cat) - pos(b.cat)).map((hub) => ({
  cat: hub.cat, nombre: hub.nav, url: hub.url, resumen: hub.resumen,
  hijas: paginas.filter((p) => p.cat === hub.cat && !p.esHub)
}));

module.exports = { paginas, secciones };
