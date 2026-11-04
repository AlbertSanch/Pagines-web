/* cuantosdiasfaltan: calculadora de fechas (días entre fechas, sumar o restar días y qué día de la semana cae).
   Todo se calcula en el navegador con fechas en UTC, para que el cambio de hora no descuadre ningún día. */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  var DIA = 864e5;
  function $(id) { return document.getElementById(id); }
  function deIso(s) { var p = s.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  function iso(t) { return new Date(t).toISOString().slice(0, 10); }
  function bonita(t) { var d = new Date(t); return DIAS[d.getUTCDay()] + ' ' + d.getUTCDate() + ' de ' + MESES[d.getUTCMonth()] + ' de ' + d.getUTCFullYear(); }
  function plural(n, a, b) { return n.toLocaleString('es-ES') + ' ' + (n === 1 ? a : b); }
  function lista(p) { return p.length === 1 ? p[0] : p.slice(0, -1).join(', ') + ' y ' + p[p.length - 1]; }
  function sumarMeses(t, n) {
    var d = new Date(t), m = d.getUTCMonth() + n, a = d.getUTCFullYear() + Math.floor(m / 12); m = ((m % 12) + 12) % 12;
    return Date.UTC(a, m, Math.min(d.getUTCDate(), new Date(Date.UTC(a, m + 1, 0)).getUTCDate()));
  }
  function aniosMesesDias(desde, hasta) {
    var meses = 0;
    while (sumarMeses(desde, meses + 1) <= hasta) meses++;
    var dias = Math.round((hasta - sumarMeses(desde, meses)) / DIA), anios = Math.floor(meses / 12); meses %= 12;
    var p = [anios ? plural(anios, 'año', 'años') : '', meses ? plural(meses, 'mes', 'meses') : '', dias ? plural(dias, 'día', 'días') : ''].filter(Boolean);
    return p.length ? lista(p) : '0 días';
  }
  function laborables(desde, hasta) {  // lunes a viernes entre desde y hasta, ambos incluidos
    var n = 0;
    for (var t = desde; t <= hasta; t += DIA) { var w = new Date(t).getUTCDay(); if (w !== 0 && w !== 6) n++; }
    return n;
  }
  function semanaIso(t) {
    var d = new Date(t), w = d.getUTCDay() || 7;
    var jueves = t + (4 - w) * DIA, inicio = Date.UTC(new Date(jueves).getUTCFullYear(), 0, 1);
    var n = Math.floor((jueves - inicio) / DIA / 7) + 1, anio = new Date(jueves).getUTCFullYear();
    return anio === d.getUTCFullYear() ? String(n) : n + ' de ' + anio;  // el 1 de enero puede caer en la última semana del año anterior
  }
  function poner(el, html) { el.innerHTML = html; el.hidden = false; }
  var hoy = (function () { var a = new Date(); return Date.UTC(a.getFullYear(), a.getMonth(), a.getDate()); })();
  ['f-desde', 'f-base', 'f-dia'].forEach(function (id) { if ($(id) && !$(id).value) $(id).value = iso(hoy); });

  // 1) días entre dos fechas
  function entre() {
    if (!$('f-desde').value || !$('f-hasta').value) return;
    var a = deIso($('f-desde').value), b = deIso($('f-hasta').value), signo = '';
    if (b < a) { var x = a; a = b; b = x; signo = ' (la segunda fecha es anterior a la primera)'; }
    var dias = Math.round((b - a) / DIA), incluir = $('f-incluir').checked, total = dias + (incluir ? 1 : 0);
    var hastaLab = incluir ? b : b - DIA, lab = hastaLab >= a ? laborables(a, hastaLab) : 0;
    poner($('r-entre'), '<p class="r-grande">' + plural(total, 'día', 'días') + '</p>' +
      '<ul class="lista-datos"><li>Del ' + bonita(a) + ' al ' + bonita(b) + signo + '.</li>' +
      '<li>' + plural(Math.floor(total / 7), 'semana', 'semanas') + (total % 7 ? ' y ' + plural(total % 7, 'día', 'días') : '') + '.</li>' +
      '<li>' + aniosMesesDias(a, b) + '.</li>' +
      '<li>' + plural(lab, 'día', 'días') + ' de lunes a viernes (sin descontar festivos).</li></ul>');
  }
  // 2) sumar o restar días
  function sumar() {
    if (!$('f-base').value || $('f-n').value === '') return;
    var t = deIso($('f-base').value), n = Math.abs(parseInt($('f-n').value, 10) || 0), signo = $('f-op').value === 'restar' ? -1 : 1;
    var tipo = $('f-tipo').value, r = t;
    if (tipo === 'naturales') r = t + signo * n * DIA;
    else if (tipo === 'semanas') r = t + signo * n * 7 * DIA;
    else if (tipo === 'meses') r = sumarMeses(t, signo * n);
    else { var k = 0; while (k < n) { r += signo * DIA; var w = new Date(r).getUTCDay(); if (w !== 0 && w !== 6) k++; } }
    var nombre = { naturales: ['día', 'días'], laborables: ['día laborable', 'días laborables'], semanas: ['semana', 'semanas'], meses: ['mes', 'meses'] }[tipo];
    poner($('r-sumar'), '<p class="r-grande">' + bonita(r) + '</p><p>' + bonita(t) + (signo > 0 ? ' más ' : ' menos ') + plural(n, nombre[0], nombre[1]) +
      (tipo === 'laborables' ? ' (de lunes a viernes, sin descontar festivos)' : '') + '.</p>');
  }
  // 3) qué día de la semana cae
  function dia() {
    if (!$('f-dia').value) return;
    var t = deIso($('f-dia').value), d = new Date(t), y = d.getUTCFullYear();
    var n = Math.round((t - Date.UTC(y, 0, 1)) / DIA) + 1, bis = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0, dif = Math.round((t - hoy) / DIA);
    poner($('r-dia'), '<p class="r-grande">' + DIAS[d.getUTCDay()].charAt(0).toUpperCase() + DIAS[d.getUTCDay()].slice(1) + '</p><ul class="lista-datos">' +
      '<li>El ' + bonita(t) + '.</li><li>Es el día ' + n + ' de ' + (bis ? 366 : 365) + ' del año y cae en la semana ' + semanaIso(t) + '.</li>' +
      '<li>' + (dif === 0 ? 'Es hoy.' : dif > 0 ? 'Faltan ' + plural(dif, 'día', 'días') + '.' : 'Fue hace ' + plural(-dif, 'día', 'días') + '.') + '</li></ul>');
  }
  [['f-entre', entre], ['f-sumar', sumar], ['f-calc-dia', dia]].forEach(function (x) {
    if ($(x[0])) $(x[0]).addEventListener('click', x[1]);
  });
  ['f-desde', 'f-hasta', 'f-incluir'].forEach(function (id) { if ($(id)) $(id).addEventListener('change', entre); });
  ['f-base', 'f-n', 'f-op', 'f-tipo'].forEach(function (id) { if ($(id)) $(id).addEventListener('change', sumar); });
  if ($('f-dia')) $('f-dia').addEventListener('change', dia);
  dia();
})();
