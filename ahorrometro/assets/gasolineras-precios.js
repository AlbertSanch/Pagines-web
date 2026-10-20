/* Ahorrómetro: las páginas de municipio se reescriben una vez por semana; al abrirlas, este script
   pone los precios del día (datos/gasolineras.json, que se actualiza dos veces al día) y reordena la tabla. */
(function () {
  var filas = document.querySelectorAll('tr[data-ll]');
  if (!filas.length || !window.fetch) return;
  function litro(p) { return p.toFixed(3).replace('.', ',') + ' €'; }
  fetch('../datos/gasolineras.json').then(function (r) { return r.json(); }).then(function (d) {
    var i = {}, por = {};
    d.campos.forEach(function (c, n) { i[c] = n; });
    d.gasolineras.forEach(function (g) { por[g[i.lat] + ',' + g[i.lon]] = g; });
    var tbody = filas[0].parentNode, lista = [];
    filas.forEach(function (tr) {
      var g = por[tr.getAttribute('data-ll')];
      if (g) tr.querySelectorAll('[data-c]').forEach(function (td) {
        var p = g[i[td.getAttribute('data-c')]];
        td.textContent = p == null ? '—' : litro(p);
      });
      lista.push({ tr: tr, p: g && g[i.gasolina95] != null ? g[i.gasolina95] : 9 });
    });
    lista.sort(function (a, b) { return a.p - b.p; }).forEach(function (x) { tbody.appendChild(x.tr); });
    var m = String(d.fecha).match(/^(\d+)\/(\d+)\/(\d+)\s+(\d+):(\d+)/), f = document.getElementById('gm-fecha');
    if (m && f) f.textContent = 'Precios del ' + +m[1] + '/' + +m[2] + '/' + m[3] + ', a las ' + +m[4] + ':' + m[5] + '. Se actualizan dos veces al día.';
  }).catch(function () { /* sin conexión: se quedan los precios de la página */ });
})();
