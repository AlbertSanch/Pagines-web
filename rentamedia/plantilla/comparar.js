/* Renta Media — «¿Tu hogar está por encima de la media?».
   Ajusta los ingresos del hogar con la escala de la OCDE modificada (1 el primer adulto, 0,5 cada adulto más,
   0,3 cada menor de 14) y los compara con la mediana por unidad de consumo del municipio. Todo en el navegador. */
(function () {
  var form = document.getElementById('calc');
  if (!form) return;
  var salida = document.getElementById('calc-resultado');
  function eur(x) { return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' €'; }
  function dec(x) { return x.toFixed(1).replace('.', ','); }
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var ingresos = parseFloat(form.ingresos.value), adultos = Math.max(1, parseInt(form.adultos.value, 10) || 1),
        ninos = Math.max(0, parseInt(form.ninos.value, 10) || 0);
    if (!(ingresos > 0)) return;
    var uc = 1 + 0.5 * (adultos - 1) + 0.3 * ninos;
    var tuyo = ingresos / uc, mediana = parseFloat(form.dataset.mediana), dif = (tuyo - mediana) / mediana * 100;
    var lugar = form.dataset.lugar, anio = form.dataset.anio;
    var frase = Math.abs(dif) < 3
      ? 'Estás <strong>justo en la mitad</strong>: ganas más o menos lo mismo que el vecino típico de ' + lugar + '.'
      : dif > 0
        ? 'Estás <strong>por encima de la mitad de tus vecinos</strong>: un ' + dec(dif) + ' % más que la mediana de ' + lugar + '.'
        : 'Estás <strong>por debajo de la mitad de tus vecinos</strong>: un ' + dec(-dif) + ' % menos que la mediana de ' + lugar + '.';
    salida.innerHTML = '<div class="respuesta"><p>' + frase + '</p></div>'
      + '<p class="updated">Tu renta por unidad de consumo: ' + eur(tuyo) + ' (' + eur(ingresos) + ' ÷ ' + dec(uc) + '). '
      + 'Mediana de ' + lugar + ' en ' + anio + ': ' + eur(mediana) + '.</p>';
  });
})();
