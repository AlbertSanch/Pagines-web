/* festivosde.es: calculadora de días laborables y hábiles con los festivos de cada municipio */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  var $ = function (id) { return document.getElementById(id); };
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function bonita(s) { var d = deIso(s); return DIAS[d.getDay()] + ' ' + d.getDate() + ' de ' + MESES[d.getMonth()] + ' de ' + d.getFullYear(); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ/ ]/g, ' ').trim(); }

  var indice = null, elegido = null, festivos = null, cache = {};
  function cargarIndice() {
    if (!indice) indice = fetch('/indice.json').then(function (r) { return r.json(); }).then(function (d) { d.forEach(function (x) { x[0] = norm(x[1]); }); return d; });
    return indice;
  }
  function cargarProvincia(cod) {
    var p = cod.slice(0, 2);
    if (!cache[p]) cache[p] = fetch('/datos/' + p + '.json').then(function (r) { return r.json(); });
    return cache[p];
  }
  function elegir(x) {
    elegido = x; $('municipio').value = x[1] + ' (' + x[3] + ')'; $('sug-municipio').innerHTML = '';
    cargarProvincia(x[4]).then(function (d) {
      festivos = { porFecha: {}, sinLocales: [] };
      d.anios.forEach(function (a) {
        (d.comunidad[a] || []).forEach(function (f) { festivos.porFecha[f[0]] = f[1]; });
        (d.comunes[a] || []).forEach(function (f) { festivos.porFecha[f[0]] = f[1]; });
        var loc = (d.locales[a] || {})[x[4]];
        if (loc) loc.forEach(function (f) { festivos.porFecha[f[0]] = f[1]; }); else festivos.sinLocales.push(+a);
      });
      festivos.anios = d.anios.map(Number);
      calcular();
    });
  }

  var inp = $('municipio'), sug = $('sug-municipio');
  inp.addEventListener('focus', cargarIndice);
  inp.addEventListener('input', function () {
    elegido = null; var t = norm(inp.value);
    if (t.length < 2) { sug.innerHTML = ''; return; }
    cargarIndice().then(function (d) {
      var res = d.filter(function (x) { return x[0].indexOf(t) === 0 || x[0].indexOf(' ' + t) > 0; })
        .sort(function (a, b) { return (a[0].indexOf(t) === 0 ? 0 : 1) - (b[0].indexOf(t) === 0 ? 0 : 1) || a[0].length - b[0].length; }).slice(0, 8);
      sug.innerHTML = res.map(function (x, i) { return '<li><a href="#" data-i="' + d.indexOf(x) + '">' + txt(x[1]) + ' <small>' + txt(x[3]) + '</small></a></li>'; }).join('');
    });
  });
  sug.addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return; e.preventDefault();
    cargarIndice().then(function (d) { elegir(d[+a.getAttribute('data-i')]); });
  });

  function laborable(d, sabados) {
    var dow = d.getDay();
    if (dow === 0 || (dow === 6 && !sabados)) return false;
    return !festivos.porFecha[iso(d)];
  }
  function avisos(desde, hasta) {
    var a = [], y1 = desde.getFullYear(), y2 = hasta.getFullYear();
    for (var y = y1; y <= y2; y++) {
      if (festivos.anios.indexOf(y) < 0) a.push('Todavía no tenemos los festivos de ' + y + ': en ese año solo se descuentan los fines de semana.');
      else if (festivos.sinLocales.indexOf(y) >= 0) a.push('Las fiestas locales de ' + y + ' de este municipio aún no están publicadas: solo se descuentan los festivos nacionales y autonómicos.');
    }
    return a.length ? '<p class="nota">' + a.join('<br>') + '</p>' : '';
  }
  function calcular() {
    var res = $('resultado');
    if (!elegido || !festivos) { res.innerHTML = '<p>Elige tu municipio para empezar.</p>'; return; }
    var sab = $('sabados').checked, modo = $('modo').value, desde = $('desde').value;
    if (!desde) { res.innerHTML = '<p>Elige la fecha de inicio.</p>'; return; }
    var d = deIso(desde), lista = [], html;
    if (modo === 'entre') {
      var hasta = $('hasta').value;
      if (!hasta || hasta < desde) { res.innerHTML = '<p>Elige una fecha final posterior a la de inicio.</p>'; return; }
      var h = deIso(hasta), naturales = 0, lab = 0, findes = 0;
      for (var x = new Date(d); x <= h; x.setDate(x.getDate() + 1)) {
        naturales++;
        var f = festivos.porFecha[iso(x)], dow = x.getDay();
        if (f && dow !== 0 && !(dow === 6 && !sab)) lista.push([iso(x), f]);
        if (laborable(x, sab)) lab++;
        if (dow === 0 || (dow === 6 && !sab)) findes++;
      }
      html = '<div class="cifra-grande">' + lab + ' <small>días laborables</small></div>' +
        '<p>Entre el ' + bonita(desde) + ' y el ' + bonita(hasta) + ' en ' + txt(elegido[1]) + ': ' + naturales + ' días naturales, ' +
        findes + ' de fin de semana' + (sab ? ' (domingos)' : '') + ' y ' + lista.length + ' festivos entre semana.</p>';
      res.innerHTML = html + listaFestivos(lista) + avisos(d, h);
    } else {
      var n = Math.max(1, Math.min(400, +$('n').value || 0)), cont = 0, x2 = new Date(d);
      while (cont < n) {
        x2.setDate(x2.getDate() + 1);
        var f2 = festivos.porFecha[iso(x2)];
        if (f2 && x2.getDay() !== 0 && !(x2.getDay() === 6 && !sab)) lista.push([iso(x2), f2]);
        if (laborable(x2, sab)) cont++;
      }
      res.innerHTML = '<div class="cifra-grande">' + bonita(iso(x2)) + '</div><p>Es el día hábil número ' + n + ' contando desde el día siguiente al ' +
        bonita(desde) + ', en ' + txt(elegido[1]) + '.</p>' + listaFestivos(lista) + avisos(d, x2);
    }
  }
  function listaFestivos(l) {
    if (!l.length) return '';
    return '<p>Festivos descontados:</p><ul class="puentes">' + l.map(function (x) { return '<li><b>' + bonita(x[0]) + '</b> · ' + txt(x[1]) + '</li>'; }).join('') + '</ul>';
  }

  $('modo').addEventListener('change', function () {
    var sumar = $('modo').value === 'sumar';
    $('campo-hasta').hidden = sumar; $('campo-n').hidden = !sumar; calcular();
  });
  ['desde', 'hasta', 'n', 'sabados'].forEach(function (id) { $(id).addEventListener('input', calcular); $(id).addEventListener('change', calcular); });

  // Valores iniciales: hoy y fin de año; municipio de la URL (?m=código INE)
  var hoy = new Date(); $('desde').value = iso(hoy); $('hasta').value = hoy.getFullYear() + '-12-31';
  var m = new URLSearchParams(location.search).get('m');
  if (m) cargarIndice().then(function (d) { var x = d.filter(function (y) { return y[4] === m; })[0]; if (x) elegir(x); });
  else calcular();
})();
