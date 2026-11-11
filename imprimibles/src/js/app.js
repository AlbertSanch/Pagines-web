/* Botones de la mesa: imprimir, otra ficha distinta y ver solución. */
(function () {
  'use strict';
  var mesa = document.querySelector('.mesa');
  if (!mesa || !window.Imprimibles) return;
  var conSolucion = false;

  function hojas() { return [].slice.call(mesa.querySelectorAll('.hoja[data-spec]')); }

  function pinta(h) {
    var r = Imprimibles.render(JSON.parse(h.getAttribute('data-spec')), +h.getAttribute('data-seed'));
    h.querySelector('.papel').innerHTML = r.svg;
    var sig = h.nextElementSibling;
    if (sig && sig.classList.contains('solucion')) sig.remove();
    if (conSolucion && r.sol) {
      var s = document.createElement('figure');
      s.className = 'hoja solucion';
      s.innerHTML = '<div class="papel">' + r.sol + '</div>';
      h.after(s);
    }
  }

  mesa.addEventListener('click', function (e) {
    var b = e.target.closest('[data-accion]');
    if (!b) return;
    var accion = b.getAttribute('data-accion');
    if (accion === 'imprimir') window.print();
    if (accion === 'otra') {
      hojas().forEach(function (h) {
        if (!h.hasAttribute('data-aleatoria')) return;
        h.setAttribute('data-seed', Math.floor(Math.random() * 4294967295));
        pinta(h);
      });
    }
    if (accion === 'solucion') {
      conSolucion = !conSolucion;
      b.setAttribute('aria-pressed', conSolucion);
      b.textContent = conSolucion ? 'Ocultar solución' : 'Ver solución';
      hojas().forEach(pinta);
    }
  });
})();

/* Ejercicio de tablas en pantalla: corregir y pedir otras 10 preguntas. */
(function () {
  'use strict';
  [].forEach.call(document.querySelectorAll('.practica'), function (caja) {
    var tablas = caja.getAttribute('data-tablas').split(',').map(Number);
    var form = caja.querySelector('form'), lista = caja.querySelector('.practica-lista'), res = caja.querySelector('.practica-resultado');
    var id = 'p' + tablas.join('');

    function entradas() { return [].slice.call(lista.querySelectorAll('input')); }

    function nuevas() {
      var pares = [], ult = '';
      while (pares.length < 10) {
        var a = tablas[Math.floor(Math.random() * tablas.length)], b = 1 + Math.floor(Math.random() * 10), k = a + 'x' + b;
        if (k === ult || pares.some(function (p) { return p[2] === k; })) continue;
        pares.push([a, b, k]); ult = k;
      }
      lista.innerHTML = pares.map(function (p, i) {
        return '<li><label for="' + id + '-' + i + '">' + p[0] + ' × ' + p[1] + ' =</label><input id="' + id + '-' + i +
          '" type="text" inputmode="numeric" autocomplete="off" maxlength="3" data-r="' + p[0] * p[1] + '"><span class="marca" aria-live="polite"></span></li>';
      }).join('');
      res.textContent = '';
      entradas()[0].focus();
    }

    function corrige() {
      var bien = 0, vacias = 0;
      entradas().forEach(function (inp) {
        var li = inp.parentNode, marca = li.querySelector('.marca'), v = inp.value.trim();
        li.classList.remove('ok', 'mal');
        if (!v) { vacias++; marca.textContent = ''; return; }
        if (Number(v) === Number(inp.getAttribute('data-r'))) { bien++; li.classList.add('ok'); marca.textContent = '✓'; }
        else { li.classList.add('mal'); marca.textContent = 'Es ' + inp.getAttribute('data-r'); }
      });
      var total = entradas().length;
      var msg = 'Has acertado ' + bien + ' de ' + total + '.';
      if (vacias) msg += ' Te quedan ' + vacias + ' sin contestar.';
      else if (bien === total) msg += ' ¡Perfecto! Pulsa «Otras 10» para seguir.';
      else if (bien >= 7) msg += ' Muy bien: repasa las que has fallado.';
      else msg += ' Vuelve a mirar la tabla y prueba otra vez.';
      res.textContent = msg;
    }

    form.addEventListener('submit', function (e) { e.preventDefault(); corrige(); });
    // Intro pasa a la siguiente casilla; en la última, corrige
    lista.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || e.target.tagName !== 'INPUT') return;
      e.preventDefault();
      var todas = entradas(), i = todas.indexOf(e.target);
      if (i < todas.length - 1) todas[i + 1].focus(); else corrige();
    });
    lista.addEventListener('input', function (e) {
      e.target.value = e.target.value.replace(/\D/g, '');
      var li = e.target.parentNode; li.classList.remove('ok', 'mal'); li.querySelector('.marca').textContent = '';
    });
    caja.querySelector('[data-practica=otras]').addEventListener('click', nuevas);
  });
})();
