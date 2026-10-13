/* Renta Media — buscador de municipios de la portada.
   /indice/<letra>.json: [[claves normalizadas], nombre, slug, provincia, renta por persona, habitantes].
   A igual coincidencia, primero los municipios más grandes. */
(function () {
  var form = document.getElementById('buscador');
  if (!form) return;
  var input = document.getElementById('q');
  var lista = document.getElementById('sugerencias');
  var cache = {}, ultimo = [];

  function norm(t) {
    return t.toLowerCase().replace(/ñ/g, '\u0001').normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/\u0001/g, 'ñ').replace(/[^a-z0-9ñ ]+/g, ' ').replace(/\s+/g, ' ').trim();
  }
  function grupo(q) { var c = q.charAt(0); return /[a-z]/.test(c) ? c : 'otros'; }
  function cargar(g) {
    if (!cache[g]) cache[g] = fetch('/indice/' + g + '.json').then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; });
    return cache[g];
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function eur(x) { return x ? String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' €' : 'sin dato'; }

  function buscar() {
    var q = norm(input.value);
    if (q.length < 2) { lista.innerHTML = ''; ultimo = []; return; }
    cargar(grupo(q)).then(function (entradas) {
      if (norm(input.value) !== q) return;
      var res = [];
      entradas.forEach(function (e) {
        var mejor = 9;
        e[0].forEach(function (k) {
          if (k === q) mejor = Math.min(mejor, 0);
          else if (k.indexOf(q) === 0) mejor = Math.min(mejor, 1);
          else if ((' ' + k).indexOf(' ' + q) >= 0) mejor = Math.min(mejor, 2);
        });
        if (mejor < 9) res.push([mejor, -(e[5] || 0), e]);
      });
      res.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
      ultimo = res.slice(0, 8).map(function (r) { return r[2]; });
      lista.innerHTML = ultimo.length ? ultimo.map(function (e) {
        return '<li><a href="/municipio/' + e[2] + '/"><span>' + esc(e[1]) + '</span><small>' + esc(e[3]) + ' · ' + eur(e[4]) + '</small></a></li>';
      }).join('') : '<li><a href="/provincias/"><span>No encontramos «' + esc(input.value) + '»</span><small>Ver por provincias</small></a></li>';
    });
  }
  input.addEventListener('input', buscar);
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (ultimo.length) location.href = '/municipio/' + ultimo[0][2] + '/';
    else buscar();
  });
  var inicial = new URLSearchParams(location.search).get('q');
  if (inicial) { input.value = inicial; buscar(); }
})();
