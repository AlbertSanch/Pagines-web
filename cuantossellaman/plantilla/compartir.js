/* ¿Cuántos se llaman? — botones de compartir de las páginas de nombre y apellido.
   WhatsApp y X son enlaces normales; aquí se activan «Más…» (menú del móvil) y «Copiar enlace». */
(function () {
  document.querySelectorAll('[data-compartir]').forEach(function (b) {
    if (!navigator.share) return;
    b.hidden = false;
    b.addEventListener('click', function () {
      navigator.share({ text: b.getAttribute('data-texto'), url: b.getAttribute('data-url') }).catch(function () {});
    });
  });
  document.querySelectorAll('[data-copiar]').forEach(function (b) {
    if (!navigator.clipboard) return;
    b.hidden = false;
    b.addEventListener('click', function () {
      navigator.clipboard.writeText(b.getAttribute('data-copiar')).then(function () {
        var t = b.textContent;
        b.textContent = '¡Copiado!';
        setTimeout(function () { b.textContent = t; }, 1800);
      }).catch(function () {});
    });
  });
})();
