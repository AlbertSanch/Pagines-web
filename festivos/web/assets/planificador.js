/* festivosde.es: planificador de vacaciones. Con los festivos de tu municipio, dice qué días pedir
   para encadenar más días libres: primero los puentes que más rinden y luego unas vacaciones largas. */
(function () {
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  var $ = function (id) { return document.getElementById(id); };
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ/ ]/g, ' ').trim(); }

  var indice = null, elegido = null, cache = {};
  function cargarIndice() {
    if (!indice) indice = fetch('/indice.json').then(function (r) { return r.json(); }).then(function (d) { d.forEach(function (x) { x[0] = norm(x[1]); }); return d; });
    return indice;
  }
  function cargarProvincia(cod) {
    var p = cod.slice(0, 2);
    if (!cache[p]) cache[p] = fetch('/datos/' + p + '.json').then(function (r) { return r.json(); });
    return cache[p];
  }

  var inp = $('municipio'), sug = $('sug-municipio'), res = $('plan');
  function elegir(x) {
    elegido = x; inp.value = x[1] + ' (' + x[3] + ')'; sug.innerHTML = '';
    calcular();
  }
  inp.addEventListener('focus', cargarIndice);
  inp.addEventListener('input', function () {
    var t = norm(inp.value);
    if (t.length < 2) { sug.innerHTML = ''; return; }
    cargarIndice().then(function (d) {
      var r = d.filter(function (x) { return x[0].indexOf(t) === 0 || x[0].indexOf(' ' + t) > 0; })
        .sort(function (a, b) { return (a[0].indexOf(t) === 0 ? 0 : 1) - (b[0].indexOf(t) === 0 ? 0 : 1) || a[0].length - b[0].length; }).slice(0, 8);
      sug.innerHTML = r.map(function (x) { return '<li><a href="#" data-i="' + d.indexOf(x) + '">' + txt(x[1]) + ' <small>' + txt(x[3]) + '</small></a></li>'; }).join('');
    });
  });
  sug.addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return; e.preventDefault();
    cargarIndice().then(function (d) { elegir(d[+a.getAttribute('data-i')]); });
  });
  ['anio', 'dias', 'mes'].forEach(function (id) { $(id).addEventListener('change', calcular); });

  // Días del año (desde hoy si es el año en curso) y bloques de días libres seguidos
  function preparar(anio, marcas) {
    var dias = [], hoy = new Date(), d = new Date(+anio, 0, 1);
    hoy = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
    if (d < hoy) d = new Date(hoy.getTime() + 864e5);
    for (; d.getFullYear() === +anio; d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1)) {
      var dow = d.getDay();
      dias.push({ f: new Date(d), libre: dow === 0 || dow === 6 || !!marcas[iso(d)] });
    }
    var bloques = [];
    dias.forEach(function (x, i) {
      if (!x.libre) return;
      if (i > 0 && dias[i - 1].libre) bloques[bloques.length - 1].fin = i;
      else bloques.push({ ini: i, fin: i });
    });
    return { dias: dias, bloques: bloques };
  }

  // Candidatos: unir los bloques i..j cogiendo de vacaciones los días laborables que hay entre ellos.
  // Con «sueltos», también alargar un bloque con días que no llegan al siguiente (un viernes antes del fin de semana).
  function candidatos(t, maxCoste, sueltos) {
    var lista = [], b = t.bloques;
    function nuevo(ini, fin, coste) { lista.push({ ini: ini, fin: fin, coste: coste, largo: fin - ini + 1, ratio: (fin - ini + 1) / coste }); }
    for (var i = 0; i < b.length; i++) {
      var coste = 0;
      for (var j = i + 1; j < b.length; j++) {
        coste += b[j].ini - b[j - 1].fin - 1;
        if (coste > maxCoste) break;
        nuevo(b[i].ini, b[j].fin, coste);
      }
      if (!sueltos) continue;
      var antes = i > 0 ? b[i].ini - b[i - 1].fin - 1 : b[i].ini, despues = i < b.length - 1 ? b[i + 1].ini - b[i].fin - 1 : t.dias.length - 1 - b[i].fin;
      for (var k = 1; k <= maxCoste; k++) {
        if (k < antes) nuevo(b[i].ini - k, b[i].fin, k);
        if (k < despues) nuevo(b[i].ini, b[i].fin + k, k);
      }
    }
    return lista;
  }
  function choca(c, elegidos) { return elegidos.some(function (e) { return c.ini <= e.fin && e.ini <= c.fin; }); }
  function conFestivo(t, c, marcas) {
    for (var k = c.ini; k <= c.fin; k++) if (marcas[iso(t.dias[k].f)]) return true;
    return false;
  }

  function planificar(t, marcas, total, mes) {
    var elegidos = [], resto = total;
    // 1) Puentes: alrededor de un festivo y que rindan al menos 2,5 días libres por día de vacaciones.
    //    Si hay vacaciones largas, se guardan para ellas todos los días menos 10 (y como mínimo una semana).
    var reserva = mes >= 0 ? Math.min(total, Math.max(5, total - 10)) : 0;
    candidatos(t, Math.min(total, 9)).filter(function (c) { return c.ratio >= 2.5 && conFestivo(t, c, marcas); })
      .sort(function (a, b) { return b.ratio - a.ratio || b.largo - a.largo || a.ini - b.ini; })
      .forEach(function (c) {
        if (c.coste <= resto - reserva && !choca(c, elegidos)) { elegidos.push(c); resto -= c.coste; c.tipo = 'puente'; }
      });
    // 2) Vacaciones largas en el mes elegido: el bloque más largo que quepa con los días que quedan
    if (mes >= 0 && resto > 0) {
      var largas = candidatos(t, resto).filter(function (c) { return t.dias[c.ini].f.getMonth() === mes && !choca(c, elegidos); })
        .sort(function (a, b) { return b.largo - a.largo || a.coste - b.coste || a.ini - b.ini; })[0];
      if (largas) {
        largas.tipo = 'largas'; elegidos.push(largas); resto -= largas.coste;
        // Los días que no llegan a otra semana entera se pegan al final de las vacaciones (o al principio)
        [1, -1].forEach(function (lado) {
          while (resto > 0) {
            var k = lado > 0 ? largas.fin + 1 : largas.ini - 1;
            if (k < 0 || k >= t.dias.length || choca({ ini: k, fin: k }, elegidos.filter(function (e) { return e !== largas; }))) break;
            if (!t.dias[k].libre) { resto--; largas.coste++; }
            if (lado > 0) largas.fin = k; else largas.ini = k;
            largas.largo++;
          }
        });
        // y los días libres que vienen justo después también cuentan
        while (largas.fin + 1 < t.dias.length && t.dias[largas.fin + 1].libre && !choca({ ini: largas.fin + 1, fin: largas.fin + 1 }, elegidos.filter(function (e) { return e !== largas; }))) { largas.fin++; largas.largo++; }
        while (largas.ini > 0 && t.dias[largas.ini - 1].libre && !choca({ ini: largas.ini - 1, fin: largas.ini - 1 }, elegidos.filter(function (e) { return e !== largas; }))) { largas.ini--; largas.largo++; }
      }
    }
    // 3) Sin vacaciones largas (o si el mes ya ha pasado): escapadas, las que más días libres dan por día de vacaciones
    if (resto > 0) {
      candidatos(t, resto, true).sort(function (a, b) { return b.ratio - a.ratio || b.largo - a.largo || a.ini - b.ini; })
        .forEach(function (c) {
          if (c.coste <= resto && !choca(c, elegidos)) { c.tipo = 'escapada'; elegidos.push(c); resto -= c.coste; }
        });
    }
    elegidos.sort(function (a, b) { return a.ini - b.ini; });
    return { plan: elegidos, sobran: resto };
  }

  function fechaCorta(d) { return DIAS[d.getDay()] + ' ' + d.getDate() + (arguments[1] ? '' : ' de ' + MESES[d.getMonth()]); }
  function rango(a, b) {
    return a.getMonth() === b.getMonth() ? 'del ' + fechaCorta(a, 1) + ' al ' + fechaCorta(b) : 'del ' + fechaCorta(a) + ' al ' + fechaCorta(b);
  }
  // Días de vacaciones de un bloque: del primer al último laborable (los días libres de en medio no se piden)
  function diasVacaciones(t, c) {
    var a = c.ini, b = c.fin;
    while (t.dias[a].libre) a++;
    while (t.dias[b].libre) b--;
    return a === b ? 'el ' + fechaCorta(t.dias[a].f) : rango(t.dias[a].f, t.dias[b].f);
  }

  function calcular() {
    if (!elegido) return;
    var anio = $('anio').value, cod = elegido[4], total = Math.max(1, Math.min(40, +$('dias').value || 22)), mes = +$('mes').value;
    history.replaceState(null, '', '?m=' + cod + '&a=' + anio + '&d=' + total + '&v=' + mes);
    cargarProvincia(cod).then(function (d) {
      var marcas = {}, nombres = {};
      function marca(f, n, tipo) { if (!marcas[f]) { marcas[f] = tipo; nombres[f] = n; } }
      (d.comunidad[anio] || []).forEach(function (f) { marca(f[0], f[1], f[2] === 'a' ? 'a' : 'n'); });
      (d.comunes[anio] || []).forEach(function (f) { marca(f[0], f[1], 'l'); });
      var loc = (d.locales[anio] || {})[cod];
      (loc || []).forEach(function (f) { marca(f[0], f[1], 'l'); });

      var t = preparar(anio, marcas);
      if (!t.dias.length) { res.innerHTML = '<p>Este año ya ha terminado: elige el siguiente.</p>'; return; }
      var r = planificar(t, marcas, total, mes), usados = total - r.sobran;
      var libres = r.plan.reduce(function (s, c) { return s + c.largo; }, 0);
      var enPlan = {};
      r.plan.forEach(function (c) { for (var k = c.ini; k <= c.fin; k++) enPlan[k] = t.dias[k].libre ? 'b' : 'v'; });

      var html = '<div class="plan-resumen"><p class="cifra-grande">' + libres + ' días libres <small>con ' + usados + ' días de vacaciones</small></p>' +
        '<p>En ' + txt(elegido[1]) + ', ' + anio + ': ' + r.plan.length + (r.plan.length === 1 ? ' periodo' : ' periodos') + ' de descanso. ' +
        'Cada día de vacaciones te da de media <b>' + (usados ? (libres / usados).toFixed(1).replace('.', ',') : '0') + ' días libres</b>.' +
        (r.sobran ? ' Te sobran <b>' + r.sobran + (r.sobran === 1 ? ' día' : ' días') + '</b> para cuando quieras.' : '') + '</p></div>';
      if (!loc) html += '<p class="hoja-aviso">Las fiestas locales de ' + txt(elegido[1]) + ' para ' + anio + ' aún no se han publicado en el boletín oficial: ' +
        'el plan solo tiene en cuenta los festivos nacionales y autonómicos. Vuelve cuando se publiquen, porque pueden salir más puentes.</p>';
      html += '<ol class="plan-lista">' + r.plan.map(function (c) {
        var a = t.dias[c.ini].f, b = t.dias[c.fin].f, fiestas = [];
        for (var k = c.ini; k <= c.fin; k++) { var f = iso(t.dias[k].f); if (nombres[f] && fiestas.indexOf(nombres[f]) < 0) fiestas.push(nombres[f]); }
        var etiqueta = c.tipo === 'largas' ? '🏖️ Vacaciones' : c.tipo === 'escapada' ? '🎒 Escapada' : '🌉 Puente';
        return '<li class="plan-' + c.tipo + '"><span class="plan-etq">' + etiqueta + (fiestas.length ? ' · ' + txt(fiestas.join(', ')) : '') + '</span>' +
          '<b>' + c.largo + ' días libres</b>, ' + rango(a, b) + '.<br>Pide ' + c.coste + (c.coste === 1 ? ' día' : ' días laborables') + ': ' + diasVacaciones(t, c) + '.</li>';
      }).join('') + '</ol>';

      html += '<div class="hoja-a4" id="hoja-plan"><div class="hoja-cab"><div><h2>Mis vacaciones ' + anio + '</h2><p>' + txt(elegido[1]) + ' · ' + txt(elegido[3]) + '</p></div>' +
        '<div class="leyenda"><span><i class="v"></i>Pedir vacaciones</span><span><i class="b"></i>Libre</span><span><i class="n"></i>Festivo</span><span><i class="l"></i>Fiesta local</span></div></div>' +
        '<div class="calendario">';
      var porFecha = {};
      t.dias.forEach(function (x, i) { porFecha[iso(x.f)] = i; });
      for (var m = 0; m < 12; m++) {
        var primero = new Date(+anio, m, 1), hueco = (primero.getDay() + 6) % 7, n = new Date(+anio, m + 1, 0).getDate();
        html += '<div class="mes"><h4>' + MESES[m] + '</h4><div class="dias">' +
          ['L', 'M', 'X', 'J', 'V', 'S', 'D'].map(function (c) { return '<span class="cab">' + c + '</span>'; }).join('');
        for (var h = 0; h < hueco; h++) html += '<span></span>';
        for (var dd = 1; dd <= n; dd++) {
          var fe = new Date(+anio, m, dd), f = iso(fe), i = porFecha[f], dow = fe.getDay(), cls = [];
          if (marcas[f]) cls.push(marcas[f] === 'l' ? 'l' : 'n');
          else if (dow === 0 || dow === 6) cls.push('finde');
          if (i !== undefined && enPlan[i]) cls.push(enPlan[i] === 'v' ? 'v' : 'b');
          html += '<span class="' + cls.join(' ') + '"' + (nombres[f] ? ' title="' + txt(nombres[f]) + '"' : '') + '>' + dd + '</span>';
        }
        html += '</div></div>';
      }
      html += '</div><p class="hoja-pie">festivosde.es/planificador-vacaciones · Festivos del BOE y del boletín oficial de la comunidad autónoma</p></div>' +
        '<p class="acciones"><button class="boton-imprimir" id="imprimir" type="button">🖨️ Imprimir o guardar en PDF</button>' +
        '<button class="boton-sec" id="copiar" type="button">🔗 Copiar enlace a mi plan</button></p>';
      res.innerHTML = html;
      res.hidden = false;
      $('imprimir').addEventListener('click', function () { window.print(); });
      $('copiar').addEventListener('click', function (e) {
        var b = e.currentTarget;
        (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () { b.textContent = '¡Enlace copiado!'; },
          function () { window.prompt('Copia el enlace:', location.href); });
      });
    });
  }

  // Valores iniciales desde la URL: ?m=código INE&a=año&d=días&v=mes (−1: sin vacaciones largas)
  var q = new URLSearchParams(location.search), a = q.get('a'), m = q.get('m'), dq = q.get('d'), v = q.get('v');
  if (a && [].some.call($('anio').options, function (o) { return o.value === a; })) $('anio').value = a;
  if (dq && +dq > 0) $('dias').value = Math.min(40, +dq);
  if (v !== null && [].some.call($('mes').options, function (o) { return o.value === v; })) $('mes').value = v;
  if (m) cargarIndice().then(function (d) { var x = d.filter(function (y) { return y[4] === m; })[0]; if (x) elegir(x); });
})();
