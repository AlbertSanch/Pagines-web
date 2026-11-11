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
