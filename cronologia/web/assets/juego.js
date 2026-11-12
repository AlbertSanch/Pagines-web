/* ¿Qué fue antes?: juego diario de la línea del tiempo. Todo ocurre en el navegador; el progreso y las estadísticas
   se guardan en localStorage. Los hechos de cada día están en /d/<nombre>.json, codificados. */
(function () {
  'use strict';
  var SAL = 'qfa-31b7';  // la misma que en scripts/generar_web.py
  var DOMINIO = location.hostname.replace(/^www\./, '');
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  // dónde está cada época en el horizonte (en % del ancho), de los dinosaurios a los cohetes
  var EPOCAS = [[-3000, 7], [-500, 19], [476, 30], [1492, 39], [1789, 49], [1900, 60], [1950, 71], [2000, 82], [99999, 93]];
  var FRASES_OK = ['¡Bien visto!', '¡Exacto!', '¡Eso es!', '¡Qué memoria!', '¡Clavado!'];
  var FRASES_MAL = ['¡Uy! Casi…', 'Ese era más tarde…', '¡Ay, el tiempo!', 'No pasa nada, sigue'];
  var raiz = document.getElementById('juego');
  if (!raiz) return;
  var modo = raiz.dataset.modo, lanzamiento = raiz.dataset.lanzamiento;
  var tablero = raiz.querySelector('.tablero');
  var ticEl = document.getElementById('tic'), bocadillo = document.getElementById('bocadillo');
  var zonaTic = raiz.querySelector('.tic-zona');
  if (zonaTic) document.body.appendChild(zonaTic);  // se coloca respecto a la página, sobre el horizonte
  var tarjetas = null, numeroDia = null, dia = null, practica = null;

  // ---------- utilidades
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function hoyMadrid() { return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()); }
  function sumarDias(iso, n) { var p = iso.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2] + n)).toISOString().slice(0, 10); }
  function dias(a, b) { return Math.round((Date.parse(b) - Date.parse(a)) / 864e5); }
  function larga(iso) { var p = iso.split('-'); return +p[2] + ' de ' + MESES[+p[1] - 1] + ' de ' + p[0]; }
  function leer(k, def) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : def; } catch (e) { return def; } }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sin almacenamiento: se juega igual */ } }
  function sha256(t) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }
  function decodificar(b64, clave) {
    var bin = atob(b64), k = new TextEncoder().encode(clave), bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i) ^ k[i % k.length];
    return JSON.parse(new TextDecoder().decode(bytes));
  }
  function azar(semilla) {  // generador repetible para el modo práctica
    var x = semilla || Date.now();
    return function () { x = (x * 1103515245 + 12345) % 2147483648; return x / 2147483648; };
  }

  // ---------- escena: altura del cielo y Tic
  function ajustarEscena() {
    var fin = raiz.getBoundingClientRect().bottom + window.scrollY;
    document.body.style.setProperty('--escena', Math.max(window.innerHeight, fin) + 'px');
  }
  window.addEventListener('resize', ajustarEscena);
  function posTic(anio) {
    var x = 50;
    for (var i = 0; i < EPOCAS.length; i++) { if (anio < EPOCAS[i][0]) { x = EPOCAS[i][1]; break; } }
    return x;
  }
  function tic(anio, humor, frase) {
    if (!ticEl) return;
    var nueva = anio == null ? 50 : posTic(anio);
    var antes = parseFloat(getComputedStyle(document.body).getPropertyValue('--tic-x')) || 50;
    document.body.style.setProperty('--tic-x', nueva + '%');
    ticEl.className = 'tic' + (Math.abs(nueva - antes) > 1 ? ' anda' : '') + (humor === 'mal' ? ' triste' : '');
    if (bocadillo && frase) bocadillo.textContent = frase;
    setTimeout(function () {
      ticEl.className = 'tic' + (humor === 'ok' ? ' salta' : humor === 'mal' ? ' triste tiembla' : '');
    }, Math.abs(nueva - antes) > 1 ? 1400 : 10);
  }

  // ---------- estado de la partida
  // st = {orden: [índices colocados en la línea, por año], res: ['v'|'r', …], sig: índice de la próxima tarjeta}
  function claveEstado() { return modo === 'diario' ? 'qfa:' + dia : 'qfa:practica'; }
  function nuevoEstado() { return { orden: [0], res: [], sig: 1, fin: false }; }
  function estado() { return leer(claveEstado(), null) || nuevoEstado(); }

  function stats() { return leer('qfa:stats', { j: 0, perf: 0, racha: 0, mejor: 0, ult: null, dist: [0, 0, 0, 0, 0, 0] }); }
  function contar(st) {
    if (modo !== 'diario' || dia !== hoyMadrid() || st.contado) return;  // los días del archivo no cuentan
    var s = stats(), aciertos = st.res.filter(function (r) { return r === 'v'; }).length;
    s.j++; s.dist[aciertos]++;
    if (aciertos === 5) s.perf++;
    s.racha = s.ult && dias(s.ult, dia) === 1 ? s.racha + 1 : 1;
    s.mejor = Math.max(s.mejor, s.racha); s.ult = dia;
    guardar('qfa:stats', s); st.contado = true;
  }
  function pintarStats() {
    var cont = document.getElementById('estadisticas'), bloque = document.getElementById('estadisticas-bloque');
    if (!cont || modo !== 'diario') return;
    var s = stats();
    if (!s.j) return;
    bloque.hidden = false;
    var max = Math.max.apply(null, s.dist) || 1, st = estado();
    var mios = st.fin ? st.res.filter(function (r) { return r === 'v'; }).length : -1;
    cont.innerHTML = '<div class="stats"><div><b>' + s.j + '</b><span>Partidas</span></div><div><b>' + s.perf + '</b><span>Perfectas</span></div>'
      + '<div><b>' + s.racha + '</b><span>Racha</span></div><div><b>' + s.mejor + '</b><span>Mejor racha</span></div></div>'
      + '<div class="barras">' + s.dist.map(function (n, i) {
        return '<div class="barra' + (i === mios && dia === hoyMadrid() ? ' yo' : '') + '"><span>' + i + '/5</span><i style="width:' + Math.max(6, n / max * 100) + '%">' + n + '</i></div>';
      }).join('') + '</div>';
  }

  // ---------- pintar
  function puesta(t, i, st, clase) {
    var r = i === 0 ? '' : st.res[i - 1];  // las tarjetas se colocan en orden: la i-ésima tiene el resultado i-1
    return '<div class="puesta ' + (r === 'v' ? 'ok' : r === 'r' ? 'mal' : '') + (clase || '') + '"><span class="em">' + esc(t.e) + '</span>'
      + '<span class="txt">' + esc(t.t) + '</span><b class="ano">' + esc(t.y) + '</b></div>';
  }
  function marcador(st) {
    var h = '';
    for (var i = 0; i < 5; i++) h += '<i class="' + (st.res[i] === 'v' ? 'v' : st.res[i] === 'r' ? 'r' : '') + '"></i>';
    return '<span class="marcador">' + h + '</span>';
  }

  var seleccion = null, recienPuesta = null, ultimaNueva = null;
  function pintar() {
    var st = estado();
    if (st.fin) return pintarFin(st);
    var t = tarjetas[st.sig];
    var html = '<div class="marcador-linea"><span>Tarjeta ' + st.sig + ' de 5</span>' + marcador(st) + '</div>'
      + '<div class="nueva' + (ultimaNueva !== st.sig ? ' entra' : '') + '"><p class="q">¿Dónde va esta?</p><div class="t"><span>' + esc(t.e) + '</span>' + esc(t.t) + '</div></div>'
      + '<p class="ayuda">Toca el hueco donde encaja en el tiempo</p><div class="tl">';
    for (var p = 0; p <= st.orden.length; p++) {
      var etiqueta = p === 0 ? 'Antes' : p === st.orden.length ? 'Después' : 'Entre medias';
      html += '<button type="button" class="hueco' + (seleccion === p ? ' sel' : '') + '" data-p="' + p + '">' + etiqueta + (seleccion === p ? ' ✓' : '') + '</button>';
      if (p < st.orden.length) html += puesta(tarjetas[st.orden[p]], st.orden[p], st, st.orden[p] === recienPuesta ? ' nuevo' : '');
    }
    html += '</div><button type="button" class="btn btn-bloque" id="colocar"' + (seleccion == null ? ' disabled' : '') + '>Colocar</button>';
    tablero.innerHTML = html;
    ultimaNueva = st.sig;
    tablero.querySelectorAll('.hueco').forEach(function (b) {
      b.addEventListener('click', function () { seleccion = +b.dataset.p; pintar(); });
    });
    document.getElementById('colocar').addEventListener('click', colocar);
    recienPuesta = null;
    ajustarEscena();
  }

  function colocar() {
    if (seleccion == null) return;
    var st = estado(), i = st.sig, a = tarjetas[i].a;
    // posición correcta: detrás de todas las que son anteriores
    var correcta = st.orden.filter(function (j) { return tarjetas[j].a < a; }).length;
    var bien = correcta === seleccion;
    st.orden.splice(correcta, 0, i);
    st.res.push(bien ? 'v' : 'r');
    st.sig++;
    if (st.sig > 5) { st.fin = true; contar(st); }
    guardar(claveEstado(), st);
    seleccion = null; recienPuesta = i;
    tic(a, bien ? 'ok' : 'mal', (bien ? FRASES_OK : FRASES_MAL)[st.res.length % (bien ? FRASES_OK.length : FRASES_MAL.length)] + ' ' + tarjetas[i].y);
    pintar();
    pintarStats();
  }

  function compartirTexto(st) {
    var aciertos = st.res.filter(function (r) { return r === 'v'; }).length;
    var cab = modo === 'diario' ? '¿Qué fue antes? #' + numeroDia : '¿Qué fue antes? (práctica)';
    return cab + '\n' + st.res.map(function (r) { return r === 'v' ? '🟩' : '🟥'; }).join('') + ' ' + aciertos + '/5\n' + DOMINIO;
  }

  function pintarFin(st) {
    var aciertos = st.res.filter(function (r) { return r === 'v'; }).length;
    var titulo = aciertos === 5 ? '¡Línea del tiempo perfecta!' : aciertos >= 3 ? '¡Muy bien!' : aciertos >= 1 ? '¡Buen intento!' : 'La historia es traicionera…';
    var linea = '<div class="tl">' + st.orden.map(function (i) { return puesta(tarjetas[i], i, st, ''); }).join('<div style="height:8px"></div>') + '</div>';
    var expl = '<div class="explicaciones">' + st.orden.map(function (i) {
      var t = tarjetas[i];
      return '<details><summary>' + esc(t.e) + ' <b>' + esc(t.y) + '</b> · ' + esc(t.t) + '</summary><p>' + esc(t.x) + ' <a href="/hechos/' + esc(t.s) + '/">Leer más</a></p></details>';
    }).join('') + '</div>';
    var sig = modo === 'diario'
      ? (dia === hoyMadrid() ? '<p class="dia">Mañana, seis hechos nuevos. Mientras tanto, prueba el <a href="/practica/">modo práctica</a>.</p>' : '<p class="dia"><a href="/">Volver al día de hoy</a></p>')
      : '';
    tablero.innerHTML = linea + '<div class="resultado"><h2>' + titulo + '</h2><p class="grande">' + aciertos + '/5</p>'
      + '<p class="cuadros">' + st.res.map(function (r) { return r === 'v' ? '🟩' : '🟥'; }).join('') + '</p>'
      + '<div class="acciones"><button type="button" class="btn" id="compartir">Compartir</button>'
      + (modo === 'practica' ? '<button type="button" class="btn sec" id="otra">Otra partida</button>' : '<a class="btn sec" href="/practica/">Práctica</a>')
      + '</div><p class="copiado" id="copiado"></p>' + sig + '<h3>Qué pasó</h3>' + expl + '</div>';
    document.getElementById('compartir').addEventListener('click', function () {
      var txt = compartirTexto(st), aviso = document.getElementById('copiado');
      if (navigator.share && /Mobi|Android|iPhone/i.test(navigator.userAgent)) {
        navigator.share({ text: txt }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(txt).then(function () { aviso.textContent = '¡Copiado! Pégalo donde quieras.'; });
      } else { aviso.textContent = txt; }
    });
    var otra = document.getElementById('otra');
    if (otra) otra.addEventListener('click', function () { guardar('qfa:practica', null); empezarPractica(); });
    tic(tarjetas[st.orden[Math.floor(st.orden.length / 2)]].a, aciertos >= 3 ? 'ok' : 'mal', aciertos === 5 ? '¡Eres un reloj suizo!' : aciertos >= 3 ? '¡Bien jugado!' : '¡Mañana más!');
    ajustarEscena();
  }

  // ---------- carga
  function empezarPractica() {
    var guardada = leer('qfa:practica', null);
    if (guardada && guardada.ids) {
      tarjetas = guardada.ids.map(function (s) { return practica.filter(function (t) { return t.s === s; })[0]; }).filter(Boolean);
      if (tarjetas.length === 6) { pintar(); return; }
    }
    var r = azar(Date.now() % 2147483648), elegidas = [], usados = {};
    var mezcla = practica.slice().sort(function () { return r() - 0.5; });
    for (var i = 0; i < mezcla.length && elegidas.length < 6; i++) {
      if (!usados[mezcla[i].a]) { usados[mezcla[i].a] = 1; elegidas.push(mezcla[i]); }
    }
    var porAnio = elegidas.slice().sort(function (x, y) { return x.a - y.a; });
    var ancla = porAnio[1 + Math.floor(r() * 4)];
    tarjetas = [ancla].concat(elegidas.filter(function (t) { return t !== ancla; }));
    var st = nuevoEstado(); st.ids = tarjetas.map(function (t) { return t.s; });
    guardar('qfa:practica', st);
    pintar();
  }

  function iniciar() {
    tic(null, null, '¡Tic, tac! ¿Empezamos?');
    if (modo === 'practica') {
      fetch('/d/practica.json').then(function (r) { return r.json(); }).then(function (j) {
        practica = decodificar(j.x, SAL + 'practica');
        empezarPractica();
      }).catch(function () { tablero.innerHTML = '<p class="aviso">No se ha podido cargar el modo práctica. Recarga la página.</p>'; });
      return;
    }
    var hoy = hoyMadrid(), pedido = new URLSearchParams(location.search).get('d');
    dia = pedido && /^\d{4}-\d{2}-\d{2}$/.test(pedido) && pedido <= hoy && pedido >= lanzamiento ? pedido : hoy;
    if (dia < lanzamiento) {
      tablero.innerHTML = '<div class="aviso"><p><b>¡Ya casi está!</b></p><p>El primer día de ¿Qué fue antes? es el ' + larga(lanzamiento)
        + '. Mientras tanto, practica en el <a href="/practica/">modo práctica</a>.</p></div>';
      ajustarEscena();
      return;
    }
    numeroDia = dias(lanzamiento, dia) + 1;
    document.querySelectorAll('.js-numero').forEach(function (e) { e.textContent = '#' + numeroDia; });
    document.querySelectorAll('.js-fecha').forEach(function (e) { e.textContent = larga(dia); });
    sha256(SAL + dia).then(function (h) {
      return fetch('/d/' + h.slice(0, 20) + '.json', { cache: 'no-cache' });
    }).then(function (r) {
      if (!r.ok) throw new Error('sin datos');
      return r.json();
    }).then(function (j) {
      tarjetas = decodificar(j.x, SAL + dia);
      var st = estado();
      if (st.fin) tic(null, null, '¡Ya has jugado hoy!');
      pintar();
      pintarStats();
    }).catch(function () {
      tablero.innerHTML = '<p class="aviso">Hoy todavía no hay partida. Vuelve en un rato o juega al <a href="/practica/">modo práctica</a>.</p>';
      ajustarEscena();
    });
  }
  iniciar();
})();
