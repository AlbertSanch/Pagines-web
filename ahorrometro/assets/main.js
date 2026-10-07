/* Ahorrómetro — script común a todas las páginas */

// Formato de números al estilo español
function fmt(n, dec) {
  if (!isFinite(n)) return '—';
  return n.toLocaleString('es-ES', { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
}
function eur(n) {
  if (!isFinite(n)) return '—';
  return n.toLocaleString('es-ES', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function num(id) {
  var el = document.getElementById(id);
  if (!el) return NaN;
  return parseFloat(String(el.value).replace(',', '.'));
}
function showResult(id, html) {
  var el = document.getElementById(id);
  el.innerHTML = html;
  el.classList.add('show');
  if (window.innerWidth < 900) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Google Analytics con el modo de consentimiento de Google.
// El consentimiento lo gestiona el mensaje de Google (AdSense → Privacidad y mensajes):
// cada página fija por defecto «denegado» para el EEE, Reino Unido y Suiza en el <head>,
// y el mensaje de Google lo actualiza cuando el visitante elige. Sin consentimiento,
// Analytics no guarda cookies.
var GA_ID = 'G-C1GLQEHDV2';
(function () {
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA_ID);
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);
})();

// Volver a mostrar el mensaje de consentimiento de Google (enlace «Configurar cookies»)
function showCookieSettings() {
  window.googlefc = window.googlefc || {};
  window.googlefc.callbackQueue = window.googlefc.callbackQueue || [];
  window.googlefc.callbackQueue.push(function () { window.googlefc.showRevocationMessage(); });
}

// Menú móvil
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', nav.classList.contains('open'));
    });
  }

  // Portada: buscador y filtro por temas (se combinan)
  var search = document.getElementById('search');
  var chips = document.querySelectorAll('[data-tema]');
  if (search || chips.length) {
    var tema = '';
    try { tema = new URLSearchParams(location.search).get('tema') || ''; } catch (e) {}
    var norm = function (t) { return t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); };
    var apply = function () {
      var q = search ? norm(search.value.trim()) : '';
      var total = 0;
      document.querySelectorAll('.grid').forEach(function (grid) {
        var visibles = 0;
        grid.querySelectorAll('.card-link').forEach(function (card) {
          var cats = (card.getAttribute('data-cat') || '').split(' ');
          var ok = (!tema || cats.indexOf(tema) > -1) && (!q || norm(card.textContent).indexOf(q) > -1);
          card.style.display = ok ? '' : 'none';
          if (ok) visibles++;
        });
        var h = grid.previousElementSibling;
        if (h && h.tagName === 'H2') h.style.display = visibles ? '' : 'none';
        total += visibles;
      });
      chips.forEach(function (b) { if (!b.classList.contains('link-btn')) b.setAttribute('aria-pressed', b.getAttribute('data-tema') === tema); });
      var empty = document.getElementById('no-results');
      if (empty) empty.hidden = total > 0;
    };
    chips.forEach(function (b) {
      b.addEventListener('click', function () {
        tema = b.getAttribute('data-tema');
        try {
          var url = new URL(location.href);
          if (tema) url.searchParams.set('tema', tema); else url.searchParams.delete('tema');
          history.replaceState(null, '', url);
        } catch (e) {}
        apply();
      });
    });
    if (search) search.addEventListener('input', apply);
    apply();
  }

  document.querySelectorAll('[data-cookie-settings]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); showCookieSettings(); });
  });
});
