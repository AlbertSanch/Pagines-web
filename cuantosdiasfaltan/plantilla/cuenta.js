/* cuantosdiasfaltan: cuentas atrás en directo (con la hora del visitante), buscador y herramientas. */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  function $(id) { return document.getElementById(id); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function hoy() { var a = new Date(); return new Date(a.getFullYear(), a.getMonth(), a.getDate()); }
  function bonita(d) { return DIAS[d.getDay()] + ' ' + d.getDate() + ' de ' + MESES[d.getMonth()] + ' de ' + d.getFullYear(); }
  function plural(n, a, b) { return n + ' ' + (n === 1 ? a : b); }
  function sumarMeses(d, n) {
    var m = d.getMonth() + n, a = d.getFullYear() + Math.floor(m / 12); m = ((m % 12) + 12) % 12;
    var ultimo = new Date(a, m + 1, 0).getDate();
    return new Date(a, m, Math.min(d.getDate(), ultimo));
  }
  // «1 año, 3 meses y 2 días» entre dos fechas (desde <= hasta)
  function tiempo(desde, hasta) {
    var meses = 0;
    while (sumarMeses(desde, meses + 1) <= hasta) meses++;
    var dias = Math.round((hasta - sumarMeses(desde, meses)) / 864e5), anios = Math.floor(meses / 12); meses %= 12;
    var p = [anios ? plural(anios, 'año', 'años') : '', meses ? plural(meses, 'mes', 'meses') : '', dias ? plural(dias, 'día', 'días') : ''].filter(Boolean);
    if (!p.length) return '0 días';
    return p.length === 1 ? p[0] : p.slice(0, -1).join(', ') + ' y ' + p[p.length - 1];
  }
  function fmt(n) { return n.toLocaleString('es-ES'); }

  // ---------- contadores: texto según la unidad elegida y segundos en directo
  var unidad = 'auto';
  try { unidad = localStorage.getItem('cdf-u') || 'auto'; } catch (e) { /* sin almacenamiento */ }
  function pintar(c) {
    var f = deIso(c.getAttribute('data-fecha')), hace = c.getAttribute('data-modo') === 'hace', ahora = new Date(), h = hoy();
    var dias = Math.round(Math.abs(f - h) / 864e5), ms = Math.abs(f - ahora);
    var g = c.querySelector('.c-grande'), d = c.querySelector('.c-dias'), v = c.querySelector('.c-vivo');
    var pre = hace ? 'Hace ' : (dias === 1 ? 'Falta ' : 'Faltan ');
    if (!hace && dias === 0) { g.textContent = '¡Es hoy! 🎉'; v.textContent = ''; return; }
    if (!hace && f < h) { g.textContent = 'Ya ha llegado'; return; }
    var t;
    if (unidad === 'dias') t = plural(dias, 'día', 'días').replace(/^\d+/, fmt(dias));
    else if (unidad === 'semanas') { var s = Math.floor(dias / 7), r = dias % 7; t = plural(s, 'semana', 'semanas') + (r ? ' y ' + plural(r, 'día', 'días') : ''); }
    else if (unidad === 'horas') { var hs = Math.floor(ms / 36e5); t = fmt(hs) + (hs === 1 ? ' hora' : ' horas'); }
    else t = hace ? tiempo(f, h) : tiempo(h, f);
    g.textContent = pre + t;
    // si el texto grande ya va en días, debajo basta la fecha
    var enDias = unidad === 'dias' || (unidad === 'auto' && !/mes|año/.test(t));
    d.innerHTML = (enDias ? '' : '<b>' + fmt(dias) + '</b> ' + (dias === 1 ? 'día' : 'días') + ' · ') + bonita(f);
    var sg = Math.floor(ms / 1000);
    v.textContent = Math.floor(sg / 86400) + ' d ' + ('0' + Math.floor(sg / 3600) % 24).slice(-2) + ' h ' + ('0' + Math.floor(sg / 60) % 60).slice(-2) + ' min ' + ('0' + sg % 60).slice(-2) + ' s';
  }
  function todos() { document.querySelectorAll('.contador[data-fecha]').forEach(pintar); }
  function marcar() { document.querySelectorAll('.c-unidades button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-u') === unidad); }); }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.c-unidades button'); if (!b) return;
    unidad = b.getAttribute('data-u');
    try { localStorage.setItem('cdf-u', unidad); } catch (er) { /* sin almacenamiento */ }
    marcar(); todos();
  });
  marcar(); todos(); setInterval(todos, 1000);

  function contador(fechaIso, hace) {
    return '<div class="contador" data-fecha="' + fechaIso + '" data-modo="' + (hace ? 'hace' : 'falta') + '"><p class="c-grande"></p><p class="c-dias"></p><p class="c-vivo"></p>' +
      '<div class="c-unidades"><button type="button" data-u="auto">Meses</button><button type="button" data-u="semanas">Semanas</button><button type="button" data-u="dias">Días</button><button type="button" data-u="horas">Horas</button></div></div>';
  }
  function poner(el, html) { el.innerHTML = html; marcar(); todos(); }

  // ---------- buscador (cabecera y portada): el índice se descarga al tocar la caja
  var indice = null;
  function cargarIndice() { if (!indice) indice = fetch('/indice.json').then(function (r) { return r.json(); }); return indice; }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  document.querySelectorAll('.js-q').forEach(function (q) {
    var sug = q.parentNode.querySelector('.sug');
    q.addEventListener('focus', cargarIndice);
    q.addEventListener('input', function () {
      var t = norm(q.value.trim());
      if (t.length < 2) { sug.innerHTML = ''; return; }
      cargarIndice().then(function (lista) {
        // primero los que empiezan por lo escrito («navi» → Navidad antes que Lotería de Navidad)
        sug.innerHTML = lista.filter(function (x) { return norm(x[0]).indexOf(t) >= 0; })
          .sort(function (a, b) { return (norm(a[0]).indexOf(t) > 0) - (norm(b[0]).indexOf(t) > 0); }).slice(0, 8)
          .map(function (x) { return '<li><a href="/' + x[1] + '/">' + x[2] + ' ' + txt(x[0]) + '</a></li>'; }).join('') ||
          '<li><a href="/#tu-cuenta">No lo tenemos todavía: crea tu propia cuenta atrás</a></li>';
      });
    });
    q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { var a = sug.querySelector('a'); if (a) location.href = a.href; } });
  });

  // ---------- copiar enlace y añadir al calendario (.ics de día completo)
  function copiar(b, url) {
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { b.textContent = '✔ Enlace copiado'; }, function () { prompt('Copia el enlace:', url); });
  }
  function calendario(fecha, titulo, url) {
    var fin = deIso(fecha); fin.setDate(fin.getDate() + 1);
    var limpio = (titulo || 'Cuenta atrás').replace(/[\\;,\n]/g, ' ');
    var ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//cuantosdiasfaltan.es//ES', 'BEGIN:VEVENT',
      'UID:' + fecha + '-' + Math.random().toString(36).slice(2) + '@cuantosdiasfaltan.es',
      'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z',
      'DTSTART;VALUE=DATE:' + fecha.replace(/-/g, ''), 'DTEND;VALUE=DATE:' + iso(fin).replace(/-/g, ''),
      'SUMMARY:' + limpio, 'URL:' + url, 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    a.download = norm(limpio).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '.ics';
    document.body.appendChild(a); a.click(); a.remove();
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copiar], [data-ics]'); if (!b) return;
    if (b.hasAttribute('data-copiar')) copiar(b, b.getAttribute('data-copiar'));
    else { var p = b.getAttribute('data-ics').split('|'); calendario(p[0], p[1], p[2]); }
  });

  // ---------- tu cuenta atrás (?t=&f=&a=1)
  if ($('c-crear')) {
    function mostrar(nombre, f, anual) {
      var d = deIso(f), h = hoy();
      if (anual) { d = new Date(h.getFullYear(), d.getMonth(), d.getDate()); if (d < h) d = new Date(h.getFullYear() + 1, d.getMonth(), d.getDate()); }
      var enlace = location.origin + '/?t=' + encodeURIComponent(nombre) + '&f=' + f + (anual ? '&a=1' : '');
      poner($('c-resultado'), '<h3>' + txt(nombre || 'Tu cuenta atrás') + '</h3>' + contador(iso(d), d < h) +
        '<p class="acciones"><a class="boton" href="https://wa.me/?text=' + encodeURIComponent('¿Cuánto falta para ' + (nombre || 'el gran día') + '? ' + enlace) + '" rel="noopener">💬 Compartir</a>' +
        '<button class="boton-sec" type="button" data-copiar="' + txt(enlace) + '">🔗 Copiar enlace</button>' +
        (d >= h ? '<button class="boton-sec" type="button" data-ics="' + iso(d) + '|' + txt(nombre || 'Mi cuenta atrás') + '|' + txt(enlace) + '">📅 Añadir al calendario</button>' : '') + '</p>');
      history.replaceState(null, '', enlace + '#tu-cuenta');
    }
    $('c-crear').addEventListener('click', function () { if ($('c-fecha').value) mostrar($('c-nombre').value.trim(), $('c-fecha').value, $('c-anual').checked); });
    var p = new URLSearchParams(location.search);
    if (/^\d{4}-\d{2}-\d{2}$/.test(p.get('f') || '')) {
      $('c-nombre').value = p.get('t') || ''; $('c-fecha').value = p.get('f'); $('c-anual').checked = p.get('a') === '1';
      mostrar(p.get('t') || '', p.get('f'), p.get('a') === '1'); $('tu-cuenta').scrollIntoView();
    }
  }

  // ---------- cuánto hace
  if ($('h-calc')) {
    $('h-calc').addEventListener('click', function () {
      var f = $('h-fecha').value; if (!f) return;
      poner($('h-resultado'), contador(f, deIso(f) <= hoy()));
    });
  }
})();
