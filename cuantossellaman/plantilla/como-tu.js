/* ¿Cuántos se llaman? — «¿Cuántas personas se llaman exactamente como tú?».
   El INE no publica combinaciones de nombre y apellidos: esto es una ESTIMACIÓN que supone que se combinan al azar:
     personas con el nombre × (primer apellido / total de primeros apellidos) × (segundo apellido / total de segundos)
   Si los dos apellidos son iguales usa el dato real de cuántos se apellidan igual dos veces.
   Datos: /indice/<letra>.json, /indice-apellidos/<letra>.json y /datos/totales.json. */
(function () {
  var form = document.getElementById('como-tu');
  if (!form) return;
  var salida = document.getElementById('como-tu-resultado');
  var cache = {};

  function norm(t) {
    return t.normalize('NFD').replace(/([nNcC]?)([̀-ͯ])/g, function (m, l, d) {
      return l && ((d === '̃' && /n/i.test(l)) || (d === '̧' && /c/i.test(l))) ? m : l;
    }).normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  function suelto(q) { return q.replace(/ñ/g, 'n').replace(/ç/g, 'c').replace(/·/g, ''); }
  function grupo(q) { var c = q.charAt(0); return /[a-z]/.test(c) ? c : 'otros'; }
  function json(url) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    return cache[url];
  }
  // Busca la forma exacta; si no está y se escribió sin ñ/ç, la más frecuente que coincida sin ellas
  function buscar(carpeta, texto, peso) {
    var q = norm(texto);
    if (!q) return Promise.resolve(null);
    var grupos = [grupo(q)];
    if (grupo(suelto(q)) !== grupos[0]) grupos.push(grupo(suelto(q)));
    return Promise.all(grupos.map(function (g) { return json(carpeta + g + '.json').catch(function () { return []; }); }))
      .then(function (listas) {
        var todo = [].concat.apply([], listas), exacto = null, mejor = null;
        for (var i = 0; i < todo.length; i++) {
          if (todo[i][0] === q) exacto = todo[i];
          else if (suelto(todo[i][0]) === suelto(q) && (!mejor || peso(todo[i]) > peso(mejor))) mejor = todo[i];
        }
        // Sin ñ ni ç en lo escrito («munoz») gana la forma más frecuente (Muñoz); si las escribe, la suya
        if (exacto && (q !== suelto(q) || !mejor || peso(exacto) >= peso(mejor))) return exacto;
        return mejor;
      });
  }
  function n(x) { return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function redondear(x) {
    var paso = x < 100 ? 5 : x < 1000 ? 10 : x < 10000 ? 100 : 1000;
    return Math.max(paso, Math.round(x / paso) * paso);
  }
  function enlace(ruta, e, i) { return e[i] ? '<a href="' + ruta + e[i] + '/">' + esc(e[1]) + '</a>' : esc(e[1]); }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var tn = document.getElementById('ct-nombre').value.trim();
    var t1 = document.getElementById('ct-ap1').value.trim();
    var t2 = document.getElementById('ct-ap2').value.trim();
    if (!tn || !t1) return;
    Promise.all([
      json('/datos/totales.json'),
      buscar('/indice/', tn, function (e) { return e[2] + e[3]; }),
      buscar('/indice-apellidos/', t1, function (e) { return e[2]; }),
      t2 ? buscar('/indice-apellidos/', t2, function (e) { return e[2]; }) : Promise.resolve(null)
    ]).then(function (r) {
      var tot = r[0], en = r[1], e1 = r[2], e2 = r[3];
      // El nombre completo bien escrito (con tildes) cuando está en los datos
      var completo = esc([en ? en[1] : tn, e1 ? e1[1] : t1, t2 ? (e2 ? e2[1] : t2) : ''].filter(Boolean).join(' '));
      var datos = [], unico = '';
      if (!en) unico = 'Tu nombre lo llevan menos de 20 personas en España (el INE no publica la cifra), así que';
      else if (!e1) unico = 'Tu primer apellido lo llevan menos de 20 personas en España (el INE no publica la cifra), así que';
      else if (t2 && !e2) unico = 'Tu segundo apellido lo llevan menos de 20 personas en España (el INE no publica la cifra), así que';
      if (en) datos.push(n(en[2] + en[3]) + ' personas se llaman ' + enlace('/nombre/', en, 8));
      if (e1) datos.push(n(e1[2]) + ' tienen ' + enlace('/apellido/', e1, 6) + ' como primer apellido');
      if (e2) datos.push(n(e2[3] || e2[2]) + ' tienen ' + enlace('/apellido/', e2, 6) + ' como segundo apellido');
      var html;
      if (unico) {
        html = '<p class="ct-frase">' + unico + ' es muy probable que seas <strong>la única persona en España</strong> que se llama ' + completo + '.</p>';
      } else {
        var est = (en[2] + en[3]);
        if (e2 && e2[0] === e1[0] && e1[4]) est *= e1[4] / tot.primer;          // mismo apellido dos veces: dato real del INE
        else {
          est *= e1[2] / tot.primer;
          if (e2) est *= (e2[3] ? e2[3] / tot.segundo : e2[2] / tot.primer);
        }
        if (est < 0.5) html = '<p class="ct-frase">Según nuestra estimación, probablemente seas <strong>la única persona en España</strong> que se llama ' + completo + '.</p>';
        else if (est < 1.5) html = '<p class="ct-frase">Seguramente eres <strong>la única persona en España</strong> que se llama ' + completo + ', o como mucho hay alguna más.</p>';
        else if (est < 10) html = '<p class="ct-frase">En España hay <strong>muy pocas personas</strong> que se llamen ' + completo + ': según nuestra estimación, menos de 10.</p>';
        else html = '<p>Se estima que en España hay</p><p class="cifra">unas ' + n(redondear(est)) + '</p><p>personas que se llaman ' + completo + '.</p>';
      }
      salida.innerHTML = '<div class="respuesta">' + html + '</div>'
        + '<div class="card"><p><strong>Estimación, no es un dato oficial.</strong> El INE no publica cuántas personas tienen a la vez un nombre y unos apellidos. '
        + 'Lo calculamos combinando sus datos: ' + datos.join('; ') + '.</p>'
        + '<p class="updated">Supone que nombres y apellidos se combinan al azar. En nombres y apellidos de la misma zona (Jordi Puig, Iker Etxeberria) la cifra real suele ser más alta.</p></div>';
    }).catch(function () {
      salida.innerHTML = '<div class="card"><p>No se han podido cargar los datos. Comprueba tu conexión y vuelve a intentarlo.</p></div>';
    });
  });
})();
