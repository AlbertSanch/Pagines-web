/* Famoso del día: juego diario y modo práctica. Todo ocurre en el navegador; el progreso y las estadísticas
   se guardan en localStorage. Los datos de cada día están en /d/<nombre>.json, codificados. */
(function () {
  'use strict';
  var SAL = 'fdd-7c1e';  // la misma que en scripts/generar_web.py
  var BANDERA = '<svg class="bandera" viewBox="0 0 3 2" aria-hidden="true"><rect width="3" height="2" fill="#c60b1e"/><rect y=".5" width="3" height="1" fill="#ffc400"/></svg>';
  // ico: lo que se ve en la web (la bandera dibujada, porque Windows no pinta los emojis de banderas); emoji: el texto para compartir
  var APARTADOS = { mundial: { nombre: 'Famoso mundial', ico: '🌍', emoji: '🌍' }, espana: { nombre: 'Famoso español', ico: BANDERA, emoji: '🇪🇸' } };
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var raiz = document.getElementById('juego');
  if (!raiz) return;
  var modo = raiz.dataset.modo, apartado = raiz.dataset.inicial, lanzamiento = raiz.dataset.lanzamiento;
  var tablero = raiz.querySelector('.tablero');
  var datosDia = null, practica = null, nombres = null, actualPractica = null;

  // ---------- utilidades
  function norm(t) {
    return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ ]/g, ' ').replace(/\s+/g, ' ').trim();
  }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function hoyMadrid() { return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()); }
  function sumarDias(iso, n) { var p = iso.split('-'); var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2] + n)); return d.toISOString().slice(0, 10); }
  function larga(iso) { var p = iso.split('-'); return +p[2] + ' de ' + MESES[+p[1] - 1]; }
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
  function cargarNombres() {
    if (nombres) return Promise.resolve(nombres);
    return fetch('/assets/nombres.json').then(function (r) { return r.json(); }).then(function (l) {
      nombres = l.map(function (n) { return { n: n, k: norm(n) }; }); return nombres;
    }).catch(function () { nombres = []; return nombres; });
  }

  // ---------- estado
  var hoy = hoyMadrid();
  function claveEstado(ap) { return modo === 'diario' ? 'fdd:' + hoy + ':' + ap : 'fdd:practica:' + (actualPractica && actualPractica.s); }
  function estado(ap) { return leer(claveEstado(ap), { fallos: [], fin: false, ok: false }); }
  function famosoActual(ap) { return modo === 'diario' ? datosDia && datosDia[ap] : actualPractica; }
  function acierta(f, intento) {
    var k = norm(intento);
    if (!k) return false;
    return [f.n].concat(f.a || []).some(function (x) { return norm(x) === k; });
  }

  // ---------- estadísticas (solo modo diario)
  function stats(ap) { return leer('fdd:stats:' + ap, { j: 0, g: 0, racha: 0, mejor: 0, ult: null, dist: [0, 0, 0, 0, 0, 0, 0] }); }
  function contar(ap, st) {
    if (modo !== 'diario' || st.contado) return;
    var s = stats(ap);
    s.j++;
    if (st.ok) {
      s.g++;
      s.racha = s.ult === sumarDias(hoy, -1) ? s.racha + 1 : 1;
      s.ult = hoy;
      s.mejor = Math.max(s.mejor, s.racha);
      s.dist[st.fallos.length + 1]++;
    } else { s.racha = 0; s.dist[0]++; }
    guardar('fdd:stats:' + ap, s);
    st.contado = true;
  }
  function pintarStats() {
    var caja = document.getElementById('estadisticas');
    if (!caja || modo !== 'diario') return;
    var s = stats(apartado);
    if (!s.j) { caja.innerHTML = '<p>Juega tu primera partida de ' + APARTADOS[apartado].nombre.toLowerCase() + ' para ver tus estadísticas.</p>'; return; }
    var max = Math.max.apply(null, s.dist) || 1;
    var barras = [1, 2, 3, 4, 5, 6, 0].map(function (i) {
      return '<div class="barra"><span>' + (i ? i : '✗') + '</span><b style="width:' + Math.max(6, Math.round(s.dist[i] / max * 100)) + '%">' + s.dist[i] + '</b></div>';
    }).join('');
    caja.innerHTML = '<p class="stats-tit">' + APARTADOS[apartado].ico + ' ' + APARTADOS[apartado].nombre + '</p><div class="stats-num">' +
      '<div><strong>' + s.j + '</strong>Jugadas</div><div><strong>' + Math.round(s.g / s.j * 100) + '%</strong>Aciertos</div>' +
      '<div><strong>' + s.racha + '</strong>Racha</div><div><strong>' + s.mejor + '</strong>Mejor racha</div></div>' +
      '<p class="stats-sub">Pistas que usaste para acertar</p><div class="dist">' + barras + '</div>';
  }

  // ---------- compartir
  function cuadros(st) {
    var r = '';
    for (var i = 0; i < st.fallos.length; i++) r += '🟥';
    if (st.ok) r += '🟩';
    return r + ' ' + (st.ok ? (st.fallos.length + 1) : 'X') + '/6';
  }
  function textoCompartir() {
    var n = datosDia ? datosDia.n : '';
    var lineas = ['Famoso del día #' + n];
    Object.keys(APARTADOS).forEach(function (ap) {
      var st = leer('fdd:' + hoy + ':' + ap, null);
      if (st && st.fin) lineas.push(APARTADOS[ap].emoji + ' ' + cuadros(st));
    });
    lineas.push(location.host || 'famosodeldia.es');
    return lineas.join('\n');
  }
  function compartir(boton) {
    var t = textoCompartir();
    if (navigator.share && /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent)) {
      navigator.share({ text: t }).catch(function () {});
      return;
    }
    var hecho = function () { boton.textContent = '✅ ¡Copiado!'; setTimeout(function () { boton.textContent = '📤 Compartir'; }, 2000); };
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(hecho, function () { prompt('Copia tu resultado:', t); });
    else prompt('Copia tu resultado:', t);
  }

  // ---------- pintar el juego
  function pintar(celebrar) {
    var f = famosoActual(apartado);
    raiz.querySelectorAll('.pestana').forEach(function (b) { b.setAttribute('aria-selected', b.dataset.apartado === apartado ? 'true' : 'false'); });
    if (modo === 'diario' && hoy < lanzamiento) { avisoLanzamiento(); return; }
    if (!f) {
      tablero.innerHTML = '<p class="aviso">Hoy no hay ' + APARTADOS[apartado].nombre.toLowerCase() + '. Mientras tanto, prueba el <a href="/practica/">modo práctica</a>.</p>';
      pintarStats();
      return;
    }
    var st = estado(apartado);
    var visibles = st.fin ? 6 : Math.min(6, st.fallos.length + 1);
    var pistas = f.p.slice(0, visibles).map(function (p, i) {
      return '<li class="pista' + (i === visibles - 1 && !st.fin ? ' nueva' : '') + '"><span class="num">' + (i + 1) + '</span>' + esc(p) + '</li>';
    }).join('');
    var fallos = st.fallos.filter(Boolean).map(function (x) { return '<li>✗ ' + esc(x) + '</li>'; }).join('');
    var html = '<ol class="pistas">' + pistas + '</ol>';
    if (fallos) html += '<ul class="fallos">' + fallos + '</ul>';
    if (!st.fin) {
      html += '<form class="respuesta" autocomplete="off" onsubmit="return false">' +
        '<div class="campo"><input type="text" class="js-intento" placeholder="Escribe un nombre…" aria-label="¿Quién es?" autocapitalize="words" spellcheck="false">' +
        '<ul class="sugerencias" role="listbox"></ul></div>' +
        '<div class="botones"><button type="submit" class="boton js-probar">Probar</button><button type="button" class="boton sec js-pasar">Pasar (ver pista ' + Math.min(6, visibles + 1) + ')</button></div>' +
        '<p class="restan">Pista ' + visibles + ' de 6 · ' + (7 - visibles) + (7 - visibles === 1 ? ' punto' : ' puntos') + ' si aciertas ahora</p></form>';
    } else {
      var puntos = st.ok ? 6 - st.fallos.length : 0;
      var otro = apartado === 'mundial' ? 'espana' : 'mundial';
      var otroHecho = modo === 'diario' && datosDia && datosDia[otro] && leer('fdd:' + hoy + ':' + otro, {}).fin;
      html += '<div class="final ' + (st.ok ? 'ok' : 'ko') + (celebrar ? ' celebrar' : '') + '">' +
        '<p class="final-tit">' + (st.ok ? '🎉 ¡Correcto! Era' : 'La respuesta era') + '</p><p class="final-nombre">' + esc(f.n) + '</p>' +
        '<p class="final-res">' + esc(f.r) + '</p>' +
        '<p class="final-puntos">' + (st.ok ? 'Acertaste con ' + (st.fallos.length + 1) + (st.fallos.length ? ' pistas' : ' pista') + ': <strong>' + puntos + (puntos === 1 ? ' punto' : ' puntos') + '</strong>' : '0 puntos') + ' · ' + cuadros(st) + '</p>' +
        (modo === 'diario' ? '<p class="final-ficha">Su ficha completa, con biografía y curiosidades, se publica mañana en el <a href="/archivo/">archivo</a>.</p>'
          : '<p class="final-ficha"><a href="/famoso/' + esc(f.s) + '/">Lee su ficha: biografía y datos curiosos →</a></p>') +
        '<div class="botones">' +
        (modo === 'diario' ? '<button type="button" class="boton js-compartir">📤 Compartir</button>' : '<button type="button" class="boton js-otro-practica">🎯 Otro famoso</button>') +
        (modo === 'diario' && !otroHecho && datosDia && datosDia[otro] ? '<button type="button" class="boton grande js-otro" data-apartado="' + otro + '">Ahora juega el ' + (otro === 'espana' ? 'español' : 'mundial') + ' ' + APARTADOS[otro].ico + '</button>'
          : modo === 'diario' ? '<a class="boton sec" href="/practica/">🎯 Sigue en el modo práctica</a>' : '') +
        '</div></div>';
    }
    tablero.innerHTML = html;
    activar(f, st);
    pintarStats();
  }

  function activar(f, st) {
    var input = tablero.querySelector('.js-intento');
    if (input) {
      var lista = tablero.querySelector('.sugerencias'), sel = -1, opciones = [];
      var pintarLista = function () {
        var q = norm(input.value);
        if (q.length < 2 || !nombres) { lista.innerHTML = ''; opciones = []; return; }
        var empiezan = [], contienen = [];
        nombres.forEach(function (x) {
          if (x.k.indexOf(q) === 0 || x.k.indexOf(' ' + q) > -1) empiezan.push(x.n);
          else if (x.k.indexOf(q) > -1) contienen.push(x.n);
        });
        opciones = empiezan.concat(contienen).slice(0, 8);
        if (opciones.length === 1 && norm(opciones[0]) === q) opciones = [];  // ya está escrito entero: que no tape los botones
        sel = -1;
        lista.innerHTML = opciones.map(function (n, i) { return '<li role="option" data-i="' + i + '">' + esc(n) + '</li>'; }).join('');
      };
      cargarNombres().then(pintarLista);
      input.addEventListener('input', pintarLista);
      input.addEventListener('blur', function () { setTimeout(function () { lista.innerHTML = ''; opciones = []; }, 150); });
      input.addEventListener('keydown', function (ev) {
        if (!opciones.length) return;
        if (ev.key === 'ArrowDown') { sel = Math.min(opciones.length - 1, sel + 1); ev.preventDefault(); }
        else if (ev.key === 'ArrowUp') { sel = Math.max(0, sel - 1); ev.preventDefault(); }
        else if (ev.key === 'Enter' && sel > -1) { input.value = opciones[sel]; lista.innerHTML = ''; opciones = []; ev.preventDefault(); return; }
        else return;
        lista.querySelectorAll('li').forEach(function (li, i) { li.classList.toggle('activa', i === sel); });
      });
      lista.addEventListener('mousedown', function (ev) {
        var li = ev.target.closest('li'); if (!li) return;
        ev.preventDefault(); input.value = opciones[+li.dataset.i]; lista.innerHTML = ''; opciones = []; probar();
      });
      var probar = function () {
        var v = input.value.trim();
        if (!v) { input.focus(); return; }
        if (acierta(f, v)) { st.ok = true; st.fin = true; }
        else {
          st.fallos.push(v);
          if (st.fallos.length >= 6) st.fin = true;
        }
        terminarSiToca(st);
      };
      tablero.querySelector('form').addEventListener('submit', probar);
      tablero.querySelector('.js-pasar').addEventListener('click', function () {
        st.fallos.push('');
        if (st.fallos.length >= 6) st.fin = true;
        terminarSiToca(st);
      });
      if (window.matchMedia('(min-width: 720px)').matches) input.focus();
    }
    var bc = tablero.querySelector('.js-compartir');
    if (bc) bc.addEventListener('click', function () { compartir(bc); });
    var bo = tablero.querySelector('.js-otro');
    if (bo) bo.addEventListener('click', function () { cambiar(bo.dataset.apartado); });
    var bp = tablero.querySelector('.js-otro-practica');
    if (bp) bp.addEventListener('click', function () { elegirPractica(true); pintar(); });
  }

  function terminarSiToca(st) {
    if (st.fin) contar(apartado, st);
    guardar(claveEstado(apartado), st);
    if (modo === 'practica' && st.fin) {
      var hechos = leer('fdd:practica:hechos', []);
      if (hechos.indexOf(actualPractica.s) < 0) { hechos.push(actualPractica.s); guardar('fdd:practica:hechos', hechos); }
    }
    pintar(st.fin && st.ok);
  }

  function cambiar(ap) {
    apartado = ap;
    if (modo === 'practica') elegirPractica(false);
    pintar();
    raiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ---------- modo práctica
  function elegirPractica(nuevo) {
    var lista = practica.filter(function (x) { return x.ap === apartado; });
    var guardado = leer('fdd:practica:actual:' + apartado, null);
    var hechos = leer('fdd:practica:hechos', []);
    if (!nuevo && guardado) {
      var g = lista.filter(function (x) { return x.s === guardado; })[0];
      if (g) { actualPractica = g; return; }
    }
    var pendientes = lista.filter(function (x) { return hechos.indexOf(x.s) < 0 && (!actualPractica || x.s !== actualPractica.s); });
    if (!pendientes.length) pendientes = lista.filter(function (x) { return !actualPractica || x.s !== actualPractica.s; });
    actualPractica = pendientes[Math.floor(Math.random() * pendientes.length)];
    try { localStorage.removeItem('fdd:practica:' + actualPractica.s); } catch (e) { /* nada */ }
    guardar('fdd:practica:actual:' + apartado, actualPractica.s);
  }

  function avisoLanzamiento() {
    tablero.innerHTML = '<p class="aviso">El primer famoso del día llega el <strong>' + larga(lanzamiento) + '</strong>. Mientras tanto, entrena en el <a href="/practica/">modo práctica</a>.</p>';
    raiz.parentNode.querySelectorAll('.js-numero').forEach(function (x) { x.textContent = '#1 el ' + larga(lanzamiento); });
  }

  // ---------- arranque
  raiz.querySelectorAll('.pestana').forEach(function (b) {
    b.addEventListener('click', function () { cambiar(b.dataset.apartado); });
  });

  if (modo === 'practica') {
    fetch('/d/practica.json').then(function (r) { return r.json(); }).then(function (d) {
      practica = decodificar(d.x, SAL + 'practica');
      elegirPractica(false);
      pintar();
    }).catch(function () { tablero.innerHTML = '<p class="aviso">No se ha podido cargar el modo práctica. Prueba a recargar la página.</p>'; });
    return;
  }

  if (hoy < lanzamiento) { avisoLanzamiento(); return; }
  sha256(SAL + hoy).then(function (h) {
    return fetch('/d/' + h.slice(0, 20) + '.json', { cache: 'no-cache' });
  }).then(function (r) {
    if (!r.ok) throw new Error('sin datos');
    return r.json();
  }).then(function (d) {
    var clave = SAL + d.f;
    datosDia = { n: d.n };
    Object.keys(APARTADOS).forEach(function (ap) { if (d[ap]) datosDia[ap] = decodificar(d[ap], clave); });
    raiz.parentNode.querySelectorAll('.js-numero').forEach(function (x) { x.textContent = '#' + d.n; });
    pintar();
  }).catch(function () {
    tablero.innerHTML = '<p class="aviso">No hemos podido cargar el famoso de hoy. Recarga la página en un momento o juega al <a href="/practica/">modo práctica</a>.</p>';
  });
})();
