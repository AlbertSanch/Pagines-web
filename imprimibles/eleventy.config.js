const P = require('./lib/puzzles.js');

module.exports = function (cfg) {
  cfg.addPassthroughCopy({ 'src/fonts': 'fonts', 'src/js': 'js', 'src/pdf': 'pdf', 'src/img': 'img', 'src/static': '/', 'src/pines': 'pines', 'lib/puzzles.js': 'js/puzzles.js' });
  cfg.addWatchTarget('./content/');
  cfg.addWatchTarget('./lib/');

  // Ficha suelta dentro de una plantilla: {{ {tipo:'sudoku', n:9} | ficha(7) | safe }}
  cfg.addFilter('ficha', (spec, seed) => P.render(spec, seed).svg);
  cfg.addFilter('json', (v) => JSON.stringify(v));
  // Busca una página de contenido por su URL (para enlaces destacados)
  cfg.addFilter('pagina', (url) => require('./content/index.js').paginas.find((p) => p.url === url));
  cfg.addFilter('amazon', (q, tag) => 'https://www.amazon.es/s?k=' + encodeURIComponent(q) + '&tag=' + encodeURIComponent(tag));
  cfg.addFilter('pendiente', (v, etiqueta) => v || '[PENDIENTE: ' + etiqueta + ']');
  // Fecha AAAA-MM-DD en el formato de los feeds RSS (a las 8:00, hora de Madrid)
  cfg.addFilter('rfc822', (iso) => new Date(iso + 'T07:00:00Z').toUTCString().replace('GMT', '+0000'));
  cfg.addFilter('sinHtml', (v) => String(v || '').replace(/<[^>]+>/g, ''));

  return { dir: { input: 'src', output: '_site' }, htmlTemplateEngine: 'njk', markdownTemplateEngine: 'njk' };
};
