/* ¿Cuántos se llaman? — «¿Qué puesto tenía tu nombre el año que naciste?».
   /datos/rankings.json: {anios: {"2024": {H: [nombres], M: [...]}}, decadas: {"1990": {etiqueta, desde, hasta, H, M}}}
   con los nombres normalizados igual que el buscador, en orden de puesto. La cifra de hoy sale de /indice/<letra>.json. */
(function () {
  var form = document.getElementById('ano');
  if (!form) return;
  var salida = document.getElementById('ano-resultado');
  var datos = null, indices = {};
  // [bebés con artículo, personas con artículo, nacidos, singular, plural sin artículo]
  var SEXO = { H: ['los niños', 'los hombres', 'nacidos', 'hombre', 'hombres'], M: ['las niñas', 'las mujeres', 'nacidas', 'mujer', 'mujeres'] };

  function norm(t) {
    return t.normalize('NFD').replace(/([nNcC]?)([̀-ͯ])/g, function (m, l, d) {
      return l && ((d === '̃' && /n/i.test(l)) || (d === '̧' && /c/i.test(l))) ? m : l;
    }).normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  function grupo(q) { var c = q.charAt(0); return /[a-z]/.test(c) ? c : 'otros'; }
  function json(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function n(x) { return x.toLocaleString('es-ES'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function entrada(q) {
    var g = grupo(q);
    if (!indices[g]) indices[g] = json('/indice/' + g + '.json').catch(function () { return []; });
    return indices[g].then(function (lista) {
      for (var i = 0; i < lista.length; i++) if (lista[i][0] === q) return lista[i];
      return null;
    });
  }

  function puesto(lista, q) { var i = lista.indexOf(q); return i < 0 ? 0 : i + 1; }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var texto = document.getElementById('ano-nombre').value.trim();
    var anio = parseInt(document.getElementById('ano-anio').value, 10);
    var s = form.querySelector('input[name="ano-sexo"]:checked').value;
    var q = norm(texto);
    if (!q || !anio) return;
    (datos ? Promise.resolve(datos) : json('/datos/rankings.json').then(function (d) { datos = d; return d; }))
      .then(function (d) { return Promise.all([d, entrada(q)]); })
      .then(function (r) {
        var d = r[0], e = r[1];
        var anios = Object.keys(d.anios).sort(), ultimo = anios[anios.length - 1];
        if (anio > +ultimo || anio < 1900) {
          salida.innerHTML = '<div class="card"><p>Escribe un año entre 1900 y ' + ultimo + '.</p></div>';
          return;
        }
        // Si el nombre solo lo llevan personas del otro sexo, cambiamos de sexo
        var aviso = '';
        if (e && !e[s === 'H' ? 2 : 3] && e[s === 'H' ? 3 : 2]) {
          s = s === 'H' ? 'M' : 'H';
          aviso = '<p class="updated">En los datos del INE, ' + esc(e[1]) + ' es nombre de ' + SEXO[s][3] + ', así que mostramos sus cifras como ' + SEXO[s][3] + '.</p>';
        }
        var nombre = e ? e[1] : texto;
        var p = [];
        var entonces = 0, hoy = puesto(d.anios[ultimo][s], q);
        if (d.anios[anio]) {
          entonces = puesto(d.anios[anio][s], q);
          p.push(entonces
            ? 'En <strong>' + anio + '</strong>, <strong>' + esc(nombre) + '</strong> fue el <strong>' + entonces + '.º</strong> nombre más puesto a ' + SEXO[s][0] + ' en España.'
            : 'En ' + anio + ', <strong>' + esc(nombre) + '</strong> no estaba entre los 100 nombres más puestos a ' + SEXO[s][0] + '.');
        } else {
          var c = null;
          Object.keys(d.decadas).forEach(function (k) {
            var x = d.decadas[k];
            if ((x.desde == null || anio >= x.desde) && anio <= x.hasta) c = x;
          });
          if (c) {
            entonces = puesto(c[s], q);
            p.push(entonces
              ? 'Entre ' + SEXO[s][1] + ' ' + SEXO[s][2] + ' ' + (c.desde == null ? '' : 'en los ') + esc(c.etiqueta) + ', <strong>' + esc(nombre) + '</strong> es el <strong>' + entonces + '.º</strong> nombre más común.'
              : 'Entre ' + SEXO[s][1] + ' ' + SEXO[s][2] + ' ' + (c.desde == null ? '' : 'en los ') + esc(c.etiqueta) + ', <strong>' + esc(nombre) + '</strong> no está entre los 50 nombres más comunes.');
          }
        }
        p.push(hoy
          ? 'En ' + ultimo + ' fue el <strong>' + hoy + '.º</strong> más puesto a ' + SEXO[s][0] + '.'
          : 'En ' + ultimo + ' no estuvo entre los 100 más puestos a ' + SEXO[s][0] + '.');
        if (entonces && hoy) p.push(hoy < entonces ? 'Hoy está todavía más de moda que cuando naciste.' : hoy > entonces ? 'Hoy se pone menos que cuando naciste.' : 'Sigue igual de de moda.');
        else if (entonces && !hoy) p.push('Era un nombre de moda que hoy ya casi no se pone.');
        else if (!entonces && hoy) p.push('Hoy se pone más que cuando naciste.');
        var f = e ? e[s === 'H' ? 2 : 3] : 0, edad = e ? e[s === 'H' ? 6 : 7] : 0;
        var total = f
          ? '<p>Hoy se llaman ' + esc(nombre) + ' <strong>' + n(f) + ' ' + SEXO[s][4] + '</strong> en España' + (edad ? ', con una edad media de ' + String(edad).replace('.', ',') + ' años' : '') + '. '
            + (e[8] ? '<a href="/nombre/' + e[8] + '/">Ver todos los datos de ' + esc(nombre) + ' →</a>' : '<a href="/?q=' + encodeURIComponent(nombre) + '">Ver sus datos →</a>') + '</p>'
          : '<p>No hay ' + SEXO[s][4] + ' con este nombre en los datos del INE, que solo publica los nombres de al menos 20 personas.</p>';
        salida.innerHTML = '<div class="card"><p>' + p.join(' ') + '</p>' + total + aviso
          + '<p class="updated">Datos del INE a ' + esc(window.REFERENCIA || '') + '.</p></div>';
      })
      .catch(function () { salida.innerHTML = '<div class="card"><p>No se han podido cargar los datos. Comprueba tu conexión y vuelve a intentarlo.</p></div>'; });
  });
})();
