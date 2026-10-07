/* ¿Cuántos se llaman? — buscador de nombres.
   Carga bajo demanda /indice/<letra>.json (una lista por letra inicial, ordenada de más a menos
   frecuente) con este formato por nombre:
   [búsqueda, forma para mostrar, hombres, mujeres, puesto hombres, puesto mujeres,
    edad media hombres, edad media mujeres, slug de su página o ""]
   Los nombres sin página propia se muestran aquí mismo, sin crear ninguna URL. */
(function () {
  var form = document.getElementById('buscar');
  if (!form) return;
  var input = document.getElementById('q');
  var salida = document.getElementById('resultado');
  var lista = document.getElementById('sugerencias');
  var referencia = form.getAttribute('data-referencia') || '';
  var cache = {};

  function norm(t) {
    return t.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/·/g, '').replace(/\s+/g, ' ').trim();
  }
  function grupo(q) { var c = q.charAt(0); return /[a-z]/.test(c) ? c : 'otros'; }
  function cargar(q) {
    var g = grupo(q);
    if (!cache[g]) {
      cache[g] = fetch('/indice/' + g + '.json').then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
    }
    return cache[g];
  }
  function n(x) { return x.toLocaleString('es-ES'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function frase(e) {
    var partes = [];
    if (e[2]) partes.push('<strong>' + n(e[2]) + '</strong> hombre' + (e[2] === 1 ? '' : 's') + ' (puesto ' + n(e[4]) + ' entre los nombres de hombre' + (e[6] ? ', edad media ' + String(e[6]).replace('.', ',') + ' años' : '') + ')');
    if (e[3]) partes.push('<strong>' + n(e[3]) + '</strong> mujer' + (e[3] === 1 ? '' : 'es') + ' (puesto ' + n(e[5]) + ' entre los nombres de mujer' + (e[7] ? ', edad media ' + String(e[7]).replace('.', ',') + ' años' : '') + ')');
    return 'En España hay ' + partes.join(' y ') + ' que se llaman <strong>' + esc(e[1]) + '</strong>.';
  }

  function mostrar(html) { salida.innerHTML = '<div class="card">' + html + '</div>'; }

  function buscar(texto) {
    var q = norm(texto);
    if (!q) return;
    cargar(q).then(function (datos) {
      var e = null;
      for (var i = 0; i < datos.length; i++) { if (datos[i][0] === q) { e = datos[i]; break; } }
      if (e && e[8]) { location.href = '/nombre/' + e[8] + '/'; return; }
      if (e) {
        mostrar('<p>' + frase(e) + '</p><p class="updated">Datos del INE a ' + esc(referencia) + '.</p>');
        return;
      }
      mostrar('<p><strong>Hay menos de 20 personas con el nombre «' + esc(texto.trim()) + '» en España; el INE no publica la cifra exacta.</strong></p>' +
        '<p>Para proteger la privacidad, el INE solo publica los nombres que llevan al menos 20 personas en toda España. ' +
        'Si el tuyo no aparece, es un nombre muy poco común (o está escrito de otra forma: prueba sin abreviaturas, por ejemplo «María José» en vez de «Mª José»). ' +
        '<a href="/sobre-los-datos/">Más sobre los datos</a>.</p>');
    }).catch(function () {
      mostrar('<p>No se ha podido cargar el buscador. Comprueba tu conexión y vuelve a intentarlo.</p>');
    });
  }

  form.addEventListener('submit', function (ev) { ev.preventDefault(); buscar(input.value); });

  var temporizador;
  input.addEventListener('input', function () {
    clearTimeout(temporizador);
    temporizador = setTimeout(function () {
      var q = norm(input.value);
      lista.innerHTML = '';
      if (q.length < 2) return;
      cargar(q).then(function (datos) {
        var html = '', k = 0;
        for (var i = 0; i < datos.length && k < 8; i++) {
          if (datos[i][0].indexOf(q) === 0) {
            var e = datos[i];
            html += '<li><a href="' + (e[8] ? '/nombre/' + e[8] + '/' : '#') + '" data-n="' + esc(e[1]) + '">' + esc(e[1]) + '</a></li>';
            k++;
          }
        }
        lista.innerHTML = html;
      }).catch(function () {});
    }, 150);
  });
  lista.addEventListener('click', function (ev) {
    var a = ev.target.closest('a');
    if (!a || a.getAttribute('href') !== '#') return;
    ev.preventDefault();
    input.value = a.getAttribute('data-n');
    buscar(input.value);
  });

  var inicial = new URLSearchParams(location.search).get('q');
  if (inicial) { input.value = inicial; buscar(inicial); }
})();
