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

// Google Analytics: solo se carga si el visitante ha aceptado las cookies
var GA_ID = 'G-C1GLQEHDV2';
var CONSENT_KEY = 'ahorrometro-cookies';
function loadAnalytics() {
  if (window.__gaLoaded) return;
  window.__gaLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA_ID);
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);
}
(function () {
  var consent = null;
  try { consent = localStorage.getItem(CONSENT_KEY); } catch (e) {}
  if (consent === 'accepted') loadAnalytics();
})();

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

  // Buscador de la portada
  var search = document.getElementById('search');
  if (search) {
    search.addEventListener('input', function () {
      var q = search.value.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
      document.querySelectorAll('.grid .card-link').forEach(function (card) {
        var t = card.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        card.style.display = t.indexOf(q) > -1 ? '' : 'none';
      });
    });
  }

  // Banner de cookies
  // IMPORTANTE: cuando AdSense te apruebe, activa el mensaje de consentimiento (CMP)
  // de Google en AdSense > Privacidad y mensajes, y elimina este banner.
  var saved = null;
  try { saved = localStorage.getItem(CONSENT_KEY); } catch (e) {}
  var banner = document.getElementById('cookie-banner');
  if (banner && !saved) {
    banner.classList.add('show');
    banner.querySelectorAll('[data-consent]').forEach(function (b) {
      b.addEventListener('click', function () {
        var choice = b.getAttribute('data-consent');
        try { localStorage.setItem(CONSENT_KEY, choice); } catch (e) {}
        banner.classList.remove('show');
        if (choice === 'accepted') loadAnalytics();
      });
    });
  }
});
