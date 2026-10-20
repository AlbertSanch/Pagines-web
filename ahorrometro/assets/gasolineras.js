/* Ahorrómetro: gasolineras baratas cerca de mí. Todo se calcula en el navegador con la lista
   oficial de gasolineras (datos/gasolineras.json): la ubicación no se envía a ningún sitio. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var res = $('gc-resultado');
  if (!res) return;
  var NOMBRES = { gasolina95: 'gasolina 95', diesel: 'diésel', gasolina98: 'gasolina 98', glp: 'GLP' };
  var datos = null, centro = null, lugar = '', comb = 'gasolina95';
  try { comb = localStorage.getItem('gc-comb') || comb; } catch (e) { /* sin almacenamiento */ }
  if (!NOMBRES[comb]) comb = 'gasolina95';
  var params = new URLSearchParams(location.search), marca = (params.get('marca') || '').toUpperCase();
  if (params.get('lowcost') === '1') $('gc-low').checked = true;
  // Misma normalización que clave_marca() en scripts/paginas_gasolineras.py
  function claveMarca(s) { return String(s).toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }

  function txt(s) { var e = document.createElement('span'); e.textContent = s == null ? '' : s; return e.innerHTML; }
  function litro(p) { return p.toFixed(3).replace('.', ','); }
  function euros(x) { return x.toFixed(2).replace('.', ',') + ' €'; }
  function norm(s) { return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ ]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function km(a, b, c, d) {
    var r = Math.PI / 180, x = Math.sin((c - a) * r / 2), y = Math.sin((d - b) * r / 2);
    return 12742 * Math.asin(Math.sqrt(x * x + Math.cos(a * r) * Math.cos(c * r) * y * y));
  }
  // Horario del Ministerio («L-V: 07:00-22:00; S: 08:00-15:00», «L-D: 24H»…) → abierta ahora: true, false o null si no se entiende.
  var DIAS = 'LMXJVSD';
  function franjas(horario) {
    var porDia = {}, ok = false, segs = String(horario || '').toUpperCase().split(';');
    segs.forEach(function (seg) {
      var m = seg.trim().match(/^([LMXJVSD](?:\s*-\s*[LMXJVSD])?(?:\s*,\s*[LMXJVSD](?:\s*-\s*[LMXJVSD])?)*)\s*:\s*(.+)$/);
      if (!m) return;
      var dias = [];
      m[1].split(',').forEach(function (p) {
        var r = p.split('-').map(function (x) { return DIAS.indexOf(x.trim()); });
        for (var d = r[0]; d <= (r[1] != null ? r[1] : r[0]); d++) dias.push(d);
      });
      var rangos = [];
      if (/24\s*H/.test(m[2])) rangos.push([0, 1440]);
      else m[2].split(/\s+Y\s+|,/).forEach(function (t) {
        var h = t.trim().match(/^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$/);
        if (!h) return;
        var a = +h[1] * 60 + +h[2], b = +h[3] * 60 + +h[4];
        if (b === 0 || b === 1439) b = 1440;
        rangos.push([a, b]);
      });
      if (!rangos.length) return;
      dias.forEach(function (d) { porDia[d] = (porDia[d] || []).concat(rangos); });
      ok = true;
    });
    // «L: 07:00-22:00» como único tramo suele querer decir todos los días: mejor no adivinar
    if (!ok || (segs.length === 1 && Object.keys(porDia).length === 1 && porDia[0])) return null;
    return porDia;
  }
  function abierta(horario, ahora) {
    var f = franjas(horario);
    if (!f) return null;
    var d = (ahora.getDay() + 6) % 7, min = ahora.getHours() * 60 + ahora.getMinutes(), ayer = (d + 6) % 7;
    var hoy = (f[d] || []).some(function (r) { return r[0] <= r[1] ? (min >= r[0] && min < r[1]) : min >= r[0]; });
    var deAyer = (f[ayer] || []).some(function (r) { return r[0] > r[1] && min < r[1]; });  // franjas que pasan de medianoche
    return hoy || deAyer;
  }

  function cargar() {
    if (!datos) datos = fetch('datos/gasolineras.json').then(function (r) { return r.json(); }).then(function (d) {
      var i = {}; d.campos.forEach(function (c, n) { i[c] = n; }); d.i = i; return d;
    });
    return datos;
  }
  function aviso(t) { res.innerHTML = '<p class="gp-status">' + t + '</p>'; }

  function pintar() {
    if (!centro) return;
    cargar().then(function (d) {
      var i = d.i, radio = +$('gc-radio').value, low = $('gc-low').checked, h24 = $('gc-24').checked, col = i[comb];
      var ahora = new Date(), soloAbiertas = $('gc-abierta').checked;
      var lista = [];
      d.gasolineras.forEach(function (g) {
        if (g[col] == null) return;
        if (low && !g[i.lowcost]) return;
        if (marca && claveMarca(g[i.marca]) !== marca) return;
        if (h24 && !/24\s*H/i.test(g[i.horario])) return;
        var dist = km(centro[0], centro[1], g[i.lat], g[i.lon]);
        if (dist > radio) return;
        var ab = abierta(g[i.horario], ahora);
        if (soloAbiertas && ab !== true) return;
        lista.push({ g: g, d: dist, ab: ab });
      });
      if (!lista.length) {
        aviso('No hay gasolineras' + (marca ? ' de esa marca' : '') + (low ? ' low cost' : '') + (h24 ? ' abiertas 24 horas' : '') + (soloAbiertas ? ' abiertas ahora' : '') + ' con ' + NOMBRES[comb] + ' a menos de ' + radio + ' km' + (lugar ? ' ' + txt(lugar) : '') + '. Prueba con más distancia.');
        return;
      }
      lista.sort(function (a, b) { return a.g[col] - b.g[col] || a.d - b.d; });
      var barata = lista[0].g[col], cara = lista[lista.length - 1].g[col];
      var cab = '<p class="gc-resumen"><strong>' + lista.length + (lista.length === 1 ? ' gasolinera' : ' gasolineras') + '</strong> con ' + NOMBRES[comb] + ' a menos de ' + radio + ' km' + (lugar ? ' ' + txt(lugar) : ' de ti') + '. ' +
        (cara > barata ? 'Llenar 50 litros en la más barata te ahorra <strong class="gp-cheap">' + euros((cara - barata) * 50) + '</strong> frente a la más cara de la zona.' : '') + '</p>';
      var filas = lista.slice(0, 40).map(function (x, n) {
        var g = x.g;
        return '<li' + (n === 0 ? ' class="gc-top"' : '') + '><div><strong>' + txt(g[i.marca] || 'Gasolinera') + '</strong>' + (g[i.lowcost] ? '<span class="gc-badge">low cost</span>' : '') +
          '<div class="sub">' + txt(g[i.direccion]) + ' · ' + txt(g[i.municipio]) + ' · ' + x.d.toFixed(1).replace('.', ',') + ' km</div>' +
          (g[i.horario] ? '<div class="sub">' + (x.ab === true ? '<span class="gc-abierta">● Abierta ahora</span> · ' : x.ab === false ? '<span class="gc-cerrada">● Cerrada ahora</span> · ' : '') + 'Horario: ' + txt(g[i.horario]) + '</div>' : '') + '</div>' +
          '<div class="gc-precio">' + litro(g[col]) + ' €</div>' +
          '<a href="https://www.google.com/maps/dir/?api=1&amp;destination=' + g[i.lat] + ',' + g[i.lon] + '" target="_blank" rel="noopener">Cómo llegar →</a></li>';
      }).join('');
      if (marca) cab = '<p class="gc-resumen">Solo gasolineras <strong>' + txt(lista[0].g[i.marca]) + '</strong> · <a href="' + location.pathname + '#buscador">ver todas las marcas</a></p>' + cab;
      res.innerHTML = cab + '<ol class="gc-lista">' + filas + '</ol>' +
        (lista.length > 40 ? '<p class="gp-updated">Se muestran las 40 más baratas.</p>' : '') +
        '<p class="gp-updated">Precios del Ministerio del ' + txt(d.fecha) + '. Confírmalos en el surtidor.</p>';
    });
  }

  $('gc-ubicacion').addEventListener('click', function () {
    if (!navigator.geolocation) { aviso('Tu navegador no permite usar la ubicación: escribe tu código postal o tu municipio.'); return; }
    aviso('Buscando tu ubicación…');
    cargar();
    navigator.geolocation.getCurrentPosition(function (p) {
      centro = [p.coords.latitude, p.coords.longitude]; lugar = ''; pintar();
    }, function () {
      aviso('No hemos podido usar tu ubicación (quizá no has dado permiso). Escribe tu código postal o tu municipio.');
    }, { enableHighAccuracy: false, timeout: 12000, maximumAge: 300000 });
  });

  $('gc-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var q = $('gc-lugar').value.trim();
    if (!q) return;
    aviso('Buscando…');
    cargar().then(function (d) {
      var i = d.i, elegidas = [];
      if (/^\d{4,5}$/.test(q)) {
        var cp = q.length === 4 ? '0' + q : q;
        for (var largo = 5; largo >= 3 && !elegidas.length; largo--) {
          elegidas = d.gasolineras.filter(function (g) { return String(g[i.cp]).slice(0, largo) === cp.slice(0, largo); });
        }
        lugar = 'del código postal ' + cp;
      } else {
        var t = norm(q);
        elegidas = d.gasolineras.filter(function (g) { return norm(g[i.municipio]) === t; });
        if (!elegidas.length) elegidas = d.gasolineras.filter(function (g) { return norm(g[i.municipio]).indexOf(t) === 0; });
        if (elegidas.length) {
          var cuenta = {};
          elegidas.forEach(function (g) { cuenta[g[i.municipio]] = (cuenta[g[i.municipio]] || 0) + 1; });
          var mejor = Object.keys(cuenta).sort(function (a, b) { return cuenta[b] - cuenta[a]; })[0];
          elegidas = elegidas.filter(function (g) { return g[i.municipio] === mejor; });
          lugar = 'de ' + mejor;
        }
      }
      if (!elegidas.length) { aviso('No encontramos gasolineras en «' + txt(q) + '». Prueba con el código postal o con un municipio cercano.'); return; }
      var la = 0, lo = 0;
      elegidas.forEach(function (g) { la += g[i.lat]; lo += g[i.lon]; });
      centro = [la / elegidas.length, lo / elegidas.length];
      pintar();
    });
  });

  document.querySelectorAll('[data-comb]').forEach(function (b) {
    b.setAttribute('aria-pressed', b.getAttribute('data-comb') === comb);
    b.addEventListener('click', function () {
      comb = b.getAttribute('data-comb');
      try { localStorage.setItem('gc-comb', comb); } catch (e) { /* sin almacenamiento */ }
      document.querySelectorAll('[data-comb]').forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
      pintar();
    });
  });
  if (params.get('abierta') === '1') $('gc-abierta').checked = true;
  ['gc-radio', 'gc-low', 'gc-24', 'gc-abierta'].forEach(function (id) { $(id).addEventListener('change', pintar); });
})();
