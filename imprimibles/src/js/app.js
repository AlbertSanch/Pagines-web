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
  [].forEach.call(document.querySelectorAll('.practica[data-tablas]'), function (caja) {
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

/* Ejercicio de sumas y restas en pantalla. */
(function () {
  'use strict';
  function llevadas(a, b, resta) {
    var da = String(a).split('').reverse().map(Number), db = String(b).split('').reverse().map(Number), acarreo = 0, total = 0;
    da.forEach(function (x, i) {
      var y = db[i] || 0;
      if (resta) { if (x - acarreo < y) { acarreo = 1; total++; } else acarreo = 0; }
      else { if (x + y + acarreo > 9) { acarreo = 1; total++; } else acarreo = 0; }
    });
    return total;
  }
  [].forEach.call(document.querySelectorAll('.practica-ops'), function (caja) {
    var op = caja.getAttribute('data-op'), llevada = caja.getAttribute('data-llevada') === '1';
    var form = caja.querySelector('form'), lista = caja.querySelector('.ops-lista'), res = caja.querySelector('.practica-resultado');
    var id = 'o' + op + (llevada ? 'l' : 's');
    function entradas() { return [].slice.call(lista.querySelectorAll('input')); }
    function nuevas(dig) {
      var min = Math.pow(10, dig - 1), max = Math.pow(10, dig) - 1, ops = [], intentos = 0;
      while (ops.length < 6 && intentos++ < 50000) {
        var resta = op === 'resta' || (op === 'mixta' && ops.length % 2 === 1);
        var a = min + Math.floor(Math.random() * (max - min + 1)), b = min + Math.floor(Math.random() * (max - min + 1));
        if (resta && a < b) { var t = a; a = b; b = t; }
        if (resta && a === b) continue;
        if ((llevadas(a, b, resta) > 0) !== llevada) continue;
        if (ops.some(function (o) { return o.a === a && o.b === b; })) continue;
        ops.push({ a: a, b: b, resta: resta, r: resta ? a - b : a + b });
      }
      lista.innerHTML = ops.map(function (o, i) {
        return '<li><div class="op" aria-hidden="true"><span>' + o.a + '</span><span class="op-b"><span class="op-signo">' + (o.resta ? '−' : '+') + '</span>' + o.b +
          '</span></div><label class="solo-lector" for="' + id + '-' + i + '">' + o.a + (o.resta ? ' menos ' : ' más ') + o.b + '</label><input id="' + id + '-' + i +
          '" type="text" inputmode="numeric" autocomplete="off" maxlength="4" data-r="' + o.r + '"><span class="marca" aria-live="polite"></span></li>';
      }).join('');
      res.textContent = '';
      entradas()[0].focus();
    }
    function corrige() {
      var bien = 0, vacias = 0, todas = entradas();
      todas.forEach(function (inp) {
        var li = inp.parentNode, marca = li.querySelector('.marca'), v = inp.value.trim();
        li.classList.remove('ok', 'mal');
        if (!v) { vacias++; marca.textContent = ''; return; }
        if (Number(v) === Number(inp.getAttribute('data-r'))) { bien++; li.classList.add('ok'); marca.textContent = '✓'; }
        else { li.classList.add('mal'); marca.textContent = 'Es ' + inp.getAttribute('data-r'); }
      });
      var msg = 'Has acertado ' + bien + ' de ' + todas.length + '.';
      if (vacias) msg += ' Te quedan ' + vacias + ' sin hacer.';
      else if (bien === todas.length) msg += ' ¡Perfecto! Prueba con otras.';
      else msg += ' Revisa las que has fallado columna a columna, empezando por las unidades.';
      res.textContent = msg;
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); corrige(); });
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
    [].forEach.call(caja.querySelectorAll('[data-digitos]'), function (b) {
      b.addEventListener('click', function () { nuevas(Number(b.getAttribute('data-digitos'))); });
    });
  });
})();
