/* ¿Cuántos se llaman? — buscador de nombres y apellidos.
   Carga bajo demanda una lista por letra inicial, ordenada de más a menos frecuente:
   - /indice/<letra>.json (nombres): [búsqueda, forma para mostrar, hombres, mujeres, puesto hombres,
     puesto mujeres, edad media hombres, edad media mujeres, slug de su página o ""]
   - /indice-apellidos/<letra>.json: [búsqueda, forma para mostrar, primer apellido, segundo apellido,
     ambos, puesto, slug de su página o ""] (0 = el INE no publica la cifra)
   Los nombres sin página propia se muestran aquí mismo, sin crear ninguna URL. */
(function () {
  var form = document.getElementById('buscar');
  if (!form) return;
  var input = document.getElementById('q');
  var salida = document.getElementById('resultado');
  var lista = document.getElementById('sugerencias');
  var referencia = form.getAttribute('data-referencia') || '';
  var cache = {};
  var TIPOS = {
    nombre: { indice: '/indice/', ruta: '/nombre/', slug: 8, texto: 'Escribe un nombre, por ejemplo Lucía' },
    apellido: { indice: '/indice-apellidos/', ruta: '/apellido/', slug: 6, texto: 'Escribe un apellido, por ejemplo García' }
  };
  function tipo() {
    var r = form.parentNode.querySelector('input[name="tipo"]:checked');
    return r && TIPOS[r.value] ? r.value : 'nombre';
  }

  // Quita tildes y diéresis pero conserva ñ, ç y · (el INE distingue Marina de Mariña).
  function norm(t) {
    return t.normalize('NFD').replace(/([nNcC]?)([\u0300-\u036f])/g, function (m, l, d) {
      return l && ((d === '\u0303' && /n/i.test(l)) || (d === '\u0327' && /c/i.test(l))) ? m : l;
    }).normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  // Para comparar sin la ñ, la ç ni el ·: quien escribe «inaki» también encuentra «Iñaki».
  function suelto(q) { return q.replace(/ñ/g, 'n').replace(/ç/g, 'c').replace(/·/g, ''); }
  function grupo(q) { var c = q.charAt(0); return /[a-z]/.test(c) ? c : 'otros'; }
  function cargarTodo(q) {  // ñ y ç al principio van en «otros»: hay que mirar las dos listas
    var a = suelto(q), b = cargar(q);
    if (grupo(a) === grupo(q)) return b;
    return Promise.all([b, cargar(a)]).then(function (r) {
      return r[0].concat(r[1]).sort(function (x, y) { return peso(y) - peso(x); });
    });
  }
  function peso(e) { return tipo() === 'apellido' ? e[2] : e[2] + e[3]; }
  function cargar(q) {
    var g = grupo(q), t = tipo(), clave = t + g;
    if (!cache[clave]) {
      cache[clave] = fetch(TIPOS[t].indice + g + '.json').then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
    }
    return cache[clave];
  }
  function n(x) { return x.toLocaleString('es-ES'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function frase(e) {
    var partes = [];
    if (e[2]) partes.push('<strong>' + n(e[2]) + '</strong> hombre' + (e[2] === 1 ? '' : 's') + ' (puesto ' + n(e[4]) + ' entre los nombres de hombre' + (e[6] ? ', edad media ' + String(e[6]).replace('.', ',') + ' años' : '') + ')');
    if (e[3]) partes.push('<strong>' + n(e[3]) + '</strong> mujer' + (e[3] === 1 ? '' : 'es') + ' (puesto ' + n(e[5]) + ' entre los nombres de mujer' + (e[7] ? ', edad media ' + String(e[7]).replace('.', ',') + ' años' : '') + ')');
    return 'En España hay ' + partes.join(' y ') + ' que se llaman <strong>' + esc(e[1]) + '</strong>.';
  }

  function fraseApellido(e) {
    var t = 'En España hay <strong>' + n(e[2]) + '</strong> personas con <strong>' + esc(e[1]) + '</strong> como primer apellido (puesto ' + n(e[5]) + ')';
    t += e[3] ? ' y <strong>' + n(e[3]) + '</strong> como segundo apellido.' : '. El INE no publica la cifra del segundo apellido.';
    if (e[4]) t += ' ' + n(e[4]) + ' personas se apellidan ' + esc(e[1]) + ' ' + esc(e[1]) + '.';
    return t;
  }

  function mostrar(html) { salida.innerHTML = '<div class="card">' + html + '</div>'; }

  function buscar(texto) {
    var q = norm(texto), t = tipo(), cfg = TIPOS[t];
    if (!q) return;
    cargarTodo(q).then(function (datos) {
      var e = null, otras = [];
      for (var i = 0; i < datos.length; i++) {
        if (datos[i][0] === q) e = datos[i];
        else if (suelto(datos[i][0]) === suelto(q)) otras.push(datos[i]);
      }
      // Sin ñ, ç ni · en lo escrito («munoz», «inaki») gana la forma más frecuente; si las escribe, la suya.
      if (otras.length && (!e || (q === suelto(q) && peso(otras[0]) > peso(e)))) {
        if (e) otras.push(e);
        e = otras.shift();
      }
      if (e && e[cfg.slug]) { location.href = cfg.ruta + e[cfg.slug] + '/'; return; }
      if (e) {
        var extra = otras.map(function (o) {
          var href = o[cfg.slug] ? cfg.ruta + o[cfg.slug] + '/' : '/?' + (t === 'apellido' ? 'tipo=apellido&amp;' : '') + 'q=' + encodeURIComponent(o[1]);
          return '<a href="' + href + '">' + esc(o[1]) + '</a>';
        });
        mostrar('<p>' + (t === 'apellido' ? fraseApellido(e) : frase(e)) + '</p>' +
          (extra.length ? '<p>No confundir con ' + extra.join(' ni con ') + ': el INE cuenta por separado cada forma de escribirlo.</p>' : '') +
          '<p class="updated">Datos del INE a ' + esc(referencia) + '.</p>');
        return;
      }
      if (t === 'apellido') {
        mostrar('<p><strong>Hay menos de 20 personas con «' + esc(texto.trim()) + '» como primer apellido en España; el INE no publica la cifra exacta.</strong></p>' +
          '<p>Para proteger la privacidad, el INE solo publica los apellidos que llevan al menos 20 personas como primer apellido. ' +
          'Prueba a escribirlo sin partículas (por ejemplo «Fuente» en vez de «de la Fuente») o con otra grafía. <a href="/sobre-los-datos/">Más sobre los datos</a>.</p>');
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
      var qs = suelto(q);
      cargarTodo(q).then(function (datos) {
        var html = '', k = 0;
        for (var i = 0; i < datos.length && k < 8; i++) {
          if (suelto(datos[i][0]).indexOf(qs) === 0) {
            var e = datos[i];
            var cfg = TIPOS[tipo()];
            html += '<li><a href="' + (e[cfg.slug] ? cfg.ruta + e[cfg.slug] + '/' : '#') + '" data-n="' + esc(e[1]) + '">' + esc(e[1]) + '</a></li>';
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

  form.parentNode.querySelectorAll('input[name="tipo"]').forEach(function (r) {
    r.addEventListener('change', function () {
      input.placeholder = TIPOS[tipo()].texto;
      salida.innerHTML = '';
      lista.innerHTML = '';
      if (input.value) input.dispatchEvent(new Event('input'));
      input.focus();
    });
  });

  var params = new URLSearchParams(location.search);
  if (params.get('tipo') === 'apellido') {
    var r = form.parentNode.querySelector('input[name="tipo"][value="apellido"]');
    if (r) { r.checked = true; input.placeholder = TIPOS.apellido.texto; }
  }
  var inicial = params.get('q');
  if (inicial) { input.value = inicial; buscar(inicial); }
})();
