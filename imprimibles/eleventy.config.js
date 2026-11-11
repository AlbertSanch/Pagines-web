const P = require('./lib/puzzles.js');

module.exports = function (cfg) {
  cfg.addPassthroughCopy({ 'src/fonts': 'fonts', 'src/js': 'js', 'src/pdf': 'pdf', 'src/static': '/', 'lib/puzzles.js': 'js/puzzles.js' });
  cfg.addWatchTarget('./content/');
  cfg.addWatchTarget('./lib/');

  // Ficha suelta dentro de una plantilla: {{ {tipo:'sudoku', n:9} | ficha(7) | safe }}
  cfg.addFilter('ficha', (spec, seed) => P.render(spec, seed).svg);
  cfg.addFilter('json', (v) => JSON.stringify(v));
  cfg.addFilter('amazon', (q, tag) => 'https://www.amazon.es/s?k=' + encodeURIComponent(q) + '&tag=' + encodeURIComponent(tag));
  cfg.addFilter('pendiente', (v, etiqueta) => v || '[PENDIENTE: ' + etiqueta + ']');
  cfg.addFilter('sinHtml', (v) => String(v || '').replace(/<[^>]+>/g, ''));

  return { dir: { input: 'src', output: '_site' }, htmlTemplateEngine: 'njk', markdownTemplateEngine: 'njk' };
};
