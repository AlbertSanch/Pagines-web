/* festivosde.es: buscador, «¿es festivo hoy?», calendario por meses y archivo .ics */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function bonita(s) { var d = deIso(s); return DIAS[d.getDay()] + ' ' + d.getDate() + ' de ' + MESES[d.getMonth()]; }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }

  // ---------- buscador
  var q = document.getElementById('q');
  if (q) {
    var indice = null, lista = document.getElementById('sugerencias');
    function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ/ ]/g, ' ').trim(); }
    function cargar() { if (!indice) { indice = fetch('/indice.json').then(function (r) { return r.json(); }).then(function (d) { d.forEach(function (x) { x[0] = norm(x[1]); }); return d; }); } return indice; }
    q.addEventListener('focus', cargar);
    q.addEventListener('input', function () {
      var t = norm(q.value);
      if (t.length < 2) { lista.innerHTML = ''; return; }
      cargar().then(function (d) {
        var emp = [], con = [];
        d.forEach(function (x) { var i = x[0].indexOf(t); if (i === 0 || x[0].indexOf(' ' + t) > 0 || x[0].indexOf('/' + t) > 0) emp.push(x); else if (i > 0) con.push(x); });
        lista.innerHTML = emp.concat(con).slice(0, 8).map(function (x) { return '<li><a href="' + x[2] + '">' + txt(x[1]) + ' <small>' + txt(x[3]) + '</small></a></li>'; }).join('');
      });
    });
    q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { var a = lista.querySelector('a'); if (a) location.href = a.href; } });
  }

  // ---------- página de municipio
  var bloque = document.getElementById('datos-festivos');
  if (!bloque) return;
  var datos = JSON.parse(bloque.textContent), todos = [];
  Object.keys(datos.festivos).forEach(function (a) { datos.festivos[a].forEach(function (x) { todos.push(x); }); });
  todos.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
  var hoy = iso(new Date());

  // ¿Es festivo hoy? y próximo festivo
  var caja = document.getElementById('hoy');
  if (caja && todos.length) {
    // Si faltan las fiestas locales de un año, no se puede asegurar que un día no sea festivo
    function conLocales(f) { return (datos.locales || []).indexOf(+f.slice(0, 4)) >= 0; }
    var deHoy = todos.filter(function (x) { return x[0] === hoy; });
    var prox = todos.filter(function (x) { return x[0] > hoy; })[0];
    var no = conLocales(hoy) ? 'No, hoy no es festivo' : 'Hoy no es festivo nacional ni autonómico';
    var html = '<div class="tarjeta' + (deHoy.length ? ' si' : '') + '"><div class="etq">¿Es festivo hoy en ' + txt(datos.municipio) + '?</div><div class="gran">' +
      (deHoy.length ? 'Sí: ' + txt(deHoy[0][1]) : no) + '</div><div>' + bonita(hoy) +
      (deHoy.length || conLocales(hoy) ? '' : ' · faltan las fiestas locales de ' + hoy.slice(0, 4)) + '</div></div>';
    if (prox) {
      var dias = Math.round((deIso(prox[0]) - deIso(hoy)) / 864e5);
      var etq = conLocales(hoy) && conLocales(prox[0]) ? 'Próximo festivo' : 'Próximo festivo nacional o autonómico';
      html += '<div class="tarjeta si"><div class="etq">' + etq + '</div><div class="gran">' + bonita(prox[0]) + '</div><div>' + txt(prox[1]) +
        ' · ' + (dias === 1 ? 'mañana' : 'dentro de ' + dias + ' días') + '</div></div>';
    }
    caja.innerHTML = html;
  }

  // Calendario por meses
  document.querySelectorAll('.calendario[data-anio]').forEach(function (cont) {
    var anio = +cont.getAttribute('data-anio'), marcas = {};
    (datos.festivos[anio] || []).forEach(function (x) { marcas[x[0]] = x; });
    var html = '';
    for (var m = 0; m < 12; m++) {
      var primero = new Date(anio, m, 1), hueco = (primero.getDay() + 6) % 7, total = new Date(anio, m + 1, 0).getDate();
      html += '<div class="mes"><h4>' + MESES[m] + ' ' + anio + '</h4><div class="dias">' +
        ['L', 'M', 'X', 'J', 'V', 'S', 'D'].map(function (d) { return '<span class="cab">' + d + '</span>'; }).join('');
      for (var h = 0; h < hueco; h++) html += '<span></span>';
      for (var d = 1; d <= total; d++) {
        var f = iso(new Date(anio, m, d)), x = marcas[f], dow = new Date(anio, m, d).getDay(), cl = [];
        if (x) cl.push(x[2]); else if (dow === 0 || dow === 6) cl.push('finde');
        if (f === hoy) cl.push('hoy-d');
        html += '<span class="' + cl.join(' ') + '"' + (x ? ' title="' + txt(x[1]) + '"' : '') + '>' + d + '</span>';
      }
      html += '</div></div>';
    }
    cont.innerHTML = html;
    var ley = document.createElement('div');
    ley.className = 'leyenda';
    ley.innerHTML = '<span><span class="marca nacional">Nacional</span></span><span><span class="marca autonomico">Autonómica</span></span><span><span class="marca local">Local</span></span>';
    cont.parentNode.insertBefore(ley, cont);
  });

  // Archivo .ics para añadir al calendario del móvil
  document.querySelectorAll('.boton-ics').forEach(function (b) {
    b.addEventListener('click', function () {
      var l = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//festivosde.es//ES', 'CALSCALE:GREGORIAN', 'X-WR-CALNAME:Festivos ' + datos.municipio];
      todos.forEach(function (x) {
        var d = x[0].replace(/-/g, ''), sig = iso(new Date(deIso(x[0]).getTime() + 864e5 + 3600e3)).replace(/-/g, '');
        l.push('BEGIN:VEVENT', 'UID:' + d + '-' + x[2] + '@festivosde.es', 'DTSTAMP:' + d + 'T000000Z', 'DTSTART;VALUE=DATE:' + d, 'DTEND;VALUE=DATE:' + sig,
          'SUMMARY:' + x[1].replace(/[,;]/g, ' ') + ' (festivo)', 'TRANSP:TRANSPARENT', 'END:VEVENT');
      });
      l.push('END:VCALENDAR');
      var blob = new Blob([l.join('\r\n')], { type: 'text/calendar' }), a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'festivos-' + datos.municipio.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-') + '.ics';
      document.body.appendChild(a); a.click(); a.remove();
    });
  });
})();
