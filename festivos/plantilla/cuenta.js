/* festivosde.es: cuentas atrás (/cuanto-falta/). Todo se calcula en el navegador con su fecha y hora. */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  function $(id) { return document.getElementById(id); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function bonita(s) { var d = deIso(s); return DIAS[d.getDay()] + ' ' + d.getDate() + ' de ' + MESES[d.getMonth()] + ' de ' + d.getFullYear(); }
  function dosCifras(n) { return ('0' + n).slice(-2); }

  // ---------- cuentas atrás en directo: hasta las 0:00 del día objetivo
  function pintar(caja) {
    var objetivo = deIso(caja.getAttribute('data-objetivo')), ahora = new Date();
    var hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
    var dias = Math.round((objetivo - hoy) / 864e5), ms = objetivo - ahora;
    var num = caja.querySelector('.cuenta-num b'), ud = caja.querySelector('.cuenta-num span'), vivo = caja.querySelector('.cuenta-vivo');
    if (num) { num.textContent = Math.max(dias, 0); ud.textContent = dias === 1 ? 'día' : 'días'; }
    if (!vivo) return;
    if (ms <= 0) { vivo.textContent = dias === 0 ? '¡Es hoy! 🎉' : 'Ya ha pasado'; return; }
    var s = Math.floor(ms / 1000);
    vivo.textContent = Math.floor(s / 86400) + ' d ' + dosCifras(Math.floor(s / 3600) % 24) + ' h ' + dosCifras(Math.floor(s / 60) % 60) + ' min ' + dosCifras(s % 60) + ' s';
  }
  function todas() { document.querySelectorAll('.cuenta[data-objetivo]').forEach(pintar); }
  todas();
  setInterval(todas, 1000);

  function caja(fechaIso, pie) {
    return '<div class="cuenta" data-objetivo="' + fechaIso + '"><div class="cuenta-num"><b></b><span></span></div><div class="cuenta-vivo"></div><p class="cuenta-pie">' + pie + '</p></div>';
  }
  function poner(cont, html) { cont.innerHTML = html; todas(); }

  // ---------- vacaciones del cole: según la comunidad elegida (se recuerda)
  var sel = $('territorio'), datosCole = $('datos-cole');
  if (sel && datosCole) {
    var opciones = JSON.parse(datosCole.textContent);
    function elegir() {
      var o = opciones.filter(function (x) { return x.id === sel.value; })[0];
      if (!o) { $('cuenta-cole').innerHTML = ''; return; }
      try { localStorage.setItem('fd-cole', o.id); } catch (e) { /* sin almacenamiento */ }
      poner($('cuenta-cole'), caja(o.fecha, txt(o.nombre) + ': ' + bonita(o.fecha)));
    }
    sel.addEventListener('change', elegir);
    try { var guardado = localStorage.getItem('fd-cole'); if (guardado) { sel.value = guardado; elegir(); } } catch (e) { /* sin almacenamiento */ }
  }

  // ---------- tu cuenta atrás (?t=nombre&f=AAAA-MM-DD&a=1 para que se repita cada año)
  var form = $('form-cuenta');
  if (form) {
    function proxima(fechaIso, anual) {
      if (!anual) return fechaIso;
      var d = deIso(fechaIso), hoy = new Date(), h = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
      var x = new Date(h.getFullYear(), d.getMonth(), d.getDate());
      if (x < h) x = new Date(h.getFullYear() + 1, d.getMonth(), d.getDate());
      return iso(x);
    }
    function mostrar(nombre, fechaIso, anual) {
      var objetivo = proxima(fechaIso, anual), enlace = location.origin + location.pathname + '?t=' + encodeURIComponent(nombre) + '&f=' + fechaIso + (anual ? '&a=1' : '');
      var titulo = nombre ? txt(nombre) : 'Tu fecha';
      poner($('c-resultado'), '<h3>' + titulo + '</h3>' + caja(objetivo, bonita(objetivo)) +
        '<p class="acciones"><a class="boton-sec" href="https://wa.me/?text=' + encodeURIComponent('¿Cuánto falta para ' + (nombre || 'el gran día') + '? ' + enlace) + '" rel="noopener">💬 Compartir por WhatsApp</a> ' +
        '<button class="boton-sec" type="button" id="c-copiar">🔗 Copiar enlace</button></p>');
      history.replaceState(null, '', enlace);
      $('c-copiar').addEventListener('click', function () {
        (navigator.clipboard ? navigator.clipboard.writeText(enlace) : Promise.reject()).then(function () { $('c-copiar').textContent = '✔ Enlace copiado'; }, function () { prompt('Copia el enlace:', enlace); });
      });
    }
    $('c-crear').addEventListener('click', function () {
      var f = $('c-fecha').value;
      if (!f) { $('c-resultado').innerHTML = '<p class="pendiente">Elige una fecha.</p>'; return; }
      mostrar($('c-nombre').value.trim(), f, $('c-anual').checked);
    });
    var p = new URLSearchParams(location.search);
    if (/^\d{4}-\d{2}-\d{2}$/.test(p.get('f') || '')) {
      $('c-nombre').value = p.get('t') || ''; $('c-fecha').value = p.get('f'); $('c-anual').checked = p.get('a') === '1';
      mostrar(p.get('t') || '', p.get('f'), p.get('a') === '1');
      $('tu-cuenta').scrollIntoView();
    }
  }

  // ---------- próximo festivo en tu municipio (mismo índice y datos por provincia que el resto de la web)
  var q = $('municipio'), lista = $('sug-municipio');
  if (q && lista && $('m-resultado')) {
    var indice = null;
    function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ/ ]/g, ' ').trim(); }
    function cargar() { if (!indice) indice = fetch('/indice.json').then(function (r) { return r.json(); }).then(function (d) { d.forEach(function (x) { x[0] = norm(x[1]); }); return d; }); return indice; }
    q.addEventListener('focus', cargar);
    q.addEventListener('input', function () {
      var t = norm(q.value);
      if (t.length < 2) { lista.innerHTML = ''; return; }
      cargar().then(function (d) {
        var emp = d.filter(function (x) { return x[0].indexOf(t) === 0; }).sort(function (a, b) { return a[0].length - b[0].length; });
        lista.innerHTML = emp.slice(0, 8).map(function (x, i) { return '<li><a href="#" data-i="' + d.indexOf(x) + '">' + txt(x[1]) + ' <small>' + txt(x[3]) + '</small></a></li>'; }).join('');
      });
    });
    lista.addEventListener('click', function (e) {
      var a = e.target.closest('a'); if (!a) return;
      e.preventDefault();
      cargar().then(function (d) {
        var m = d[+a.getAttribute('data-i')], cod = m[4];
        q.value = m[1]; lista.innerHTML = '';
        fetch('/datos/' + cod.slice(0, 2) + '.json').then(function (r) { return r.json(); }).then(function (p) {
          var hoy = iso(new Date()), todos = [], conLocales = {};
          p.anios.forEach(function (an) {
            (p.comunidad[an] || []).forEach(function (x) { todos.push([x[0], x[1]]); });
            (p.comunes[an] || []).forEach(function (x) { todos.push([x[0], x[1]]); });
            var loc = (p.locales[an] || {})[cod];
            if (loc) { conLocales[an] = true; loc.forEach(function (x) { todos.push([x[0], x[1] + ' (fiesta local)']); }); }
          });
          todos.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
          var px = todos.filter(function (x) { return x[0] >= hoy; })[0];
          if (!px) { $('m-resultado').innerHTML = '<p class="pendiente">Aún no tenemos los festivos del año que viene.</p>'; return; }
          var aviso = conLocales[px[0].slice(0, 4)] ? '' : '<p class="nota">Las fiestas locales de ' + px[0].slice(0, 4) + ' de ' + txt(m[1]) + ' todavía no están en nuestros datos: este es el próximo festivo nacional o autonómico.</p>';
          poner($('m-resultado'), caja(px[0], txt(px[1]) + ': ' + bonita(px[0])) + aviso + '<p><a href="' + m[2] + '">Todos los festivos de ' + txt(m[1]) + ' →</a></p>');
        });
      });
    });
  }
})();
