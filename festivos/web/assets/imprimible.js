/* festivosde.es: calendario laboral de un año en una hoja A4 para imprimir o guardar en PDF */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  var TIPOS = { n: 'Nacional', a: 'Autonómico', l: 'Local' };
  var $ = function (id) { return document.getElementById(id); };
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ/ ]/g, ' ').trim(); }

  var indice = null, elegido = null, cache = {};
  function cargarIndice() {
    if (!indice) indice = fetch('/indice.json').then(function (r) { return r.json(); }).then(function (d) { d.forEach(function (x) { x[0] = norm(x[1]); }); return d; });
    return indice;
  }
  function cargarProvincia(cod) {
    var p = cod.slice(0, 2);
    if (!cache[p]) cache[p] = fetch('/datos/' + p + '.json').then(function (r) { return r.json(); });
    return cache[p];
  }

  var inp = $('municipio'), sug = $('sug-municipio'), selAnio = $('anio'), hoja = $('hoja');
  function elegir(x) {
    elegido = x; inp.value = x[1] + ' (' + x[3] + ')'; sug.innerHTML = '';
    dibujar();
  }
  inp.addEventListener('focus', cargarIndice);
  inp.addEventListener('input', function () {
    var t = norm(inp.value);
    if (t.length < 2) { sug.innerHTML = ''; return; }
    cargarIndice().then(function (d) {
      var res = d.filter(function (x) { return x[0].indexOf(t) === 0 || x[0].indexOf(' ' + t) > 0; })
        .sort(function (a, b) { return (a[0].indexOf(t) === 0 ? 0 : 1) - (b[0].indexOf(t) === 0 ? 0 : 1) || a[0].length - b[0].length; }).slice(0, 8);
      sug.innerHTML = res.map(function (x) { return '<li><a href="#" data-i="' + d.indexOf(x) + '">' + txt(x[1]) + ' <small>' + txt(x[3]) + '</small></a></li>'; }).join('');
    });
  });
  sug.addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return; e.preventDefault();
    cargarIndice().then(function (d) { elegir(d[+a.getAttribute('data-i')]); });
  });
  ['anio', 'bn', 'lista'].forEach(function (id) { $(id).addEventListener('change', dibujar); });

  function dibujar() {
    if (!elegido) return;
    var anio = selAnio.value, cod = elegido[4];
    history.replaceState(null, '', '?m=' + cod + '&a=' + anio);
    cargarProvincia(cod).then(function (d) {
      var lista = [], marcas = {};
      (d.comunidad[anio] || []).forEach(function (f) { lista.push([f[0], f[1], f[2] === 'a' ? 'a' : 'n']); });
      (d.comunes[anio] || []).forEach(function (f) { lista.push([f[0], f[1], 'l']); });
      var loc = (d.locales[anio] || {})[cod];
      (loc || []).forEach(function (f) { lista.push([f[0], f[1], 'l']); });
      lista.sort(function (a, b) { return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0; });
      lista.forEach(function (x) { if (!marcas[x[0]]) marcas[x[0]] = x; });

      var html = '<div class="hoja-cab"><div><h2>Calendario laboral ' + anio + '</h2><p>' + txt(elegido[1]) + ' · ' + txt(elegido[3]) + '</p></div>' +
        '<div class="leyenda"><span><i class="n"></i>Nacional</span><span><i class="a"></i>Autonómico</span><span><i class="l"></i>Local</span></div></div>';
      html += '<div class="calendario">';
      for (var m = 0; m < 12; m++) {
        var primero = new Date(+anio, m, 1), hueco = (primero.getDay() + 6) % 7, total = new Date(+anio, m + 1, 0).getDate();
        html += '<div class="mes"><h4>' + MESES[m] + '</h4><div class="dias">' +
          ['L', 'M', 'X', 'J', 'V', 'S', 'D'].map(function (c) { return '<span class="cab">' + c + '</span>'; }).join('');
        for (var h = 0; h < hueco; h++) html += '<span></span>';
        for (var dd = 1; dd <= total; dd++) {
          var f = iso(new Date(+anio, m, dd)), x = marcas[f], dow = new Date(+anio, m, dd).getDay();
          html += '<span class="' + (x ? x[2] : (dow === 0 || dow === 6 ? 'finde' : '')) + '"' + (x ? ' title="' + txt(x[1]) + '"' : '') + '>' + dd + '</span>';
        }
        html += '</div></div>';
      }
      html += '</div>';
      if ($('lista').checked) {
        html += '<ol class="hoja-lista">' + lista.map(function (x) {
          var dt = deIso(x[0]);
          return '<li><b>' + dt.getDate() + ' ' + MESES[dt.getMonth()].slice(0, 3) + '</b> ' + DIAS[dt.getDay()].slice(0, 3) + ' · ' + txt(x[1]) +
            ' <small>(' + TIPOS[x[2]].toLowerCase() + ')</small></li>';
        }).join('') + '</ol>';
      }
      if (!loc) html += '<p class="hoja-aviso">Las fiestas locales de ' + txt(elegido[1]) + ' para ' + anio + ' aún no se han publicado en el boletín oficial: ' +
        'este calendario solo tiene los festivos nacionales y autonómicos. Vuelve a descargarlo cuando se publiquen.</p>';
      html += '<p class="hoja-pie">festivosde.es · Festivos del BOE y del boletín oficial de la comunidad autónoma</p>';
      hoja.innerHTML = html;
      hoja.className = 'hoja-a4' + ($('bn').checked ? ' bn' : '');
      hoja.hidden = false;
      $('imprimir').disabled = false;
      $('resumen').textContent = lista.length + ' festivos en ' + anio + (loc ? '' : ' (sin las fiestas locales, aún no publicadas)') + '.';
    });
  }

  $('imprimir').addEventListener('click', function () { if (elegido) window.print(); });

  // Valores iniciales: año de la URL o el más reciente, municipio de la URL (?m=código INE)
  var q = new URLSearchParams(location.search), a = q.get('a'), m = q.get('m');
  if (a && [].some.call(selAnio.options, function (o) { return o.value === a; })) selAnio.value = a;
  if (m) cargarIndice().then(function (d) { var x = d.filter(function (y) { return y[4] === m; })[0]; if (x) elegir(x); });
})();
