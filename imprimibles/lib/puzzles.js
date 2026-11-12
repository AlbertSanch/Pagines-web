/*
 * Generadores de fichas de imprimibles.es
 * El mismo archivo se usa al compilar la web (Node) y en el navegador
 * (botón «Otra distinta»). Cada ficha es un SVG de 210 × 297 (A4 en mm).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Imprimibles = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var TINTA = '#1b1b1f';
  var ROJO = '#d5392b';
  var GRIS = '#55555c';

  // ---------- utilidades ----------
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function ri(r, a, b) { return a + Math.floor(r() * (b - a + 1)); }
  function shuffle(r, arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(r() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function f(n) { return Math.round(n * 100) / 100; }
  function hash(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function txt(x, y, s, o) {
    o = o || {};
    return '<text x="' + f(x) + '" y="' + f(y) + '" font-size="' + (o.size || 4) + '"' +
      (o.anchor ? ' text-anchor="' + o.anchor + '"' : '') +
      (o.bold ? ' font-weight="700"' : '') +
      (o.fill ? ' fill="' + o.fill + '"' : '') +
      (o.titular ? ' font-family="Besley,Georgia,serif" font-weight="800"' : '') +
      '>' + esc(s) + '</text>';
  }

  // Marco común de la hoja: título, instrucciones, nombre/fecha y pie
  function hoja(o, cuerpo) {
    var s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" role="img" aria-label="' +
      esc((o.titulo || o.alt || 'Ficha') + (o.sol ? ' (solución)' : '')) +
      '" font-family="\'Andika\',Arial,sans-serif" fill="' + TINTA + '">';
    s += '<rect width="210" height="297" fill="#fff"/>';
    if (o.titulo) {
      // los títulos largos se encogen para no chocar con el rótulo «Solución»
      s += txt(15, 24, o.titulo, { size: f(Math.min(8, 8 * 33 / o.titulo.length)), titular: true });
      if (o.sol) s += txt(195, 24, o.ingles ? 'Answers' : 'Solución', { size: 5, anchor: 'end', fill: ROJO, bold: true });
    }
    if (o.sub) s += txt(15, 31, o.sub, { size: 3.7, fill: GRIS });
    if (o.nombre && !o.sol) {
      s += txt(15, 40, o.ingles ? 'Name:' : 'Nombre:', { size: 3.7 }) + '<path d="M31 40.5H118" stroke="' + TINTA + '" stroke-width=".2"/>';
      s += txt(125, 40, o.ingles ? 'Date:' : 'Fecha:', { size: 3.7 }) + '<path d="M138 40.5H195" stroke="' + TINTA + '" stroke-width=".2"/>';
    }
    s += cuerpo;
    if (!o.sinPie) {
      s += txt(15, 289, 'imprimibles.es', { size: 3, fill: '#8a8a90' });
      if (o.seed != null) s += txt(195, 289, 'Ficha n.º ' + (o.seed % 100000), { size: 3, anchor: 'end', fill: '#8a8a90' });
    }
    return s + '</svg>';
  }

  // ---------- sopa de letras ----------
  function normaliza(p) {
    return p.toUpperCase().replace(/Ñ/g, '\u0001').normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/\u0001/g, 'Ñ').replace(/[^A-ZÑ]/g, '');
  }
  var DIRS = {
    facil: [[0, 1], [1, 0]],
    medio: [[0, 1], [1, 0], [1, 1], [-1, 1]],
    dificil: [[0, 1], [1, 0], [1, 1], [-1, 1], [0, -1], [-1, 0], [-1, -1], [1, -1]]
  };
  var TODAS = DIRS.dificil;
  var RELLENO = 'AAAAEEEEOOOIIIUUSSSRRRNNNLLLDDTTTCCMMPPBGVHFYQJZXÑ';
  var RELLENO_EN = 'EEEEEAAAOOOIIITTTTNNNSSSRRRHHHLLDDCCUUMMWWFGYYPBVK';

  function sopa(spec, seed) {
    var r = rng(seed), N = spec.tam || 12, dirs = DIRS[spec.nivel || 'medio'], RELL = spec.ingles ? RELLENO_EN : RELLENO;
    var max = spec.nPalabras || 12;
    var cand = shuffle(r, spec.palabras).map(function (p) { return Array.isArray(p) ? { ver: p[1].toUpperCase(), w: normaliza(p[0]) } : { ver: p.toUpperCase(), w: normaliza(p) }; })
      .filter(function (p) { return p.w.length >= 3 && p.w.length <= N; });
    var g = [], usada = [], i, j;
    for (i = 0; i < N; i++) { g.push(new Array(N).fill('')); usada.push(new Array(N).fill(false)); }
    var puestas = [];
    // se eligen al azar las palabras de la ficha y se colocan primero las largas;
    // el resto queda de reserva por si alguna no cabe
    var porLargo = function (a, b) { return b.w.length - a.w.length; };
    cand = cand.slice(0, max).sort(porLargo).concat(cand.slice(max));
    for (var k = 0; k < cand.length && puestas.length < max; k++) {
      var w = cand[k].w, ok = false;
      for (var t = 0; t < 300 && !ok; t++) {
        var d = dirs[ri(r, 0, dirs.length - 1)];
        var r0 = ri(r, 0, N - 1), c0 = ri(r, 0, N - 1);
        var r1 = r0 + d[0] * (w.length - 1), c1 = c0 + d[1] * (w.length - 1);
        if (r1 < 0 || r1 >= N || c1 < 0 || c1 >= N) continue;
        var cabe = true;
        for (i = 0; i < w.length; i++) {
          var ch = g[r0 + d[0] * i][c0 + d[1] * i];
          if (ch && ch !== w[i]) { cabe = false; break; }
        }
        if (!cabe) continue;
        for (i = 0; i < w.length; i++) { g[r0 + d[0] * i][c0 + d[1] * i] = w[i]; usada[r0 + d[0] * i][c0 + d[1] * i] = true; }
        puestas.push({ ver: cand[k].ver, w: w, r: r0, c: c0, dr: d[0], dc: d[1] });
        ok = true;
      }
    }
    for (i = 0; i < N; i++) for (j = 0; j < N; j++) if (!g[i][j]) g[i][j] = RELL[ri(r, 0, RELL.length - 1)];

    // Evita que el relleno forme por azar una segunda copia de alguna palabra
    function esLegitima(p, r0, c0, d) {
      if (p.r === r0 && p.c === c0 && p.dr === d[0] && p.dc === d[1]) return true;
      var L = p.w.length - 1; // la misma palabra leída al revés (palíndromos)
      return p.r + p.dr * L === r0 && p.c + p.dc * L === c0 && p.dr === -d[0] && p.dc === -d[1];
    }
    for (var pasada = 0; pasada < 40; pasada++) {
      var cambios = 0;
      puestas.forEach(function (p) {
        var L = p.w.length;
        for (var a = 0; a < N; a++) for (var b = 0; b < N; b++) TODAS.forEach(function (d) {
          var ra = a + d[0] * (L - 1), cb = b + d[1] * (L - 1);
          if (ra < 0 || ra >= N || cb < 0 || cb >= N) return;
          for (var q = 0; q < L; q++) if (g[a + d[0] * q][b + d[1] * q] !== p.w[q]) return;
          if (esLegitima(p, a, b, d)) return;
          for (q = 0; q < L; q++) {
            var rr = a + d[0] * q, cc = b + d[1] * q;
            if (!usada[rr][cc]) {
              var nueva;
              do { nueva = RELL[ri(r, 0, RELL.length - 1)]; } while (nueva === g[rr][cc]);
              g[rr][cc] = nueva; cambios++; return;
            }
          }
        });
      });
      if (!cambios) break;
    }
    puestas.sort(function (a, b) { return a.ver.localeCompare(b.ver, 'es'); });

    function dibuja(sol) {
      var lado = 165, x0 = 22.5, y0 = 47, c = lado / N, s = '';
      if (sol) puestas.forEach(function (p) {
        var L = p.w.length - 1;
        s += '<path d="M' + f(x0 + (p.c + .5) * c) + ' ' + f(y0 + (p.r + .5) * c) + 'L' + f(x0 + (p.c + p.dc * L + .5) * c) + ' ' +
          f(y0 + (p.r + p.dr * L + .5) * c) + '" stroke="' + ROJO + '" stroke-opacity=".32" stroke-width="' + f(c * .72) + '" stroke-linecap="round"/>';
      });
      s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + lado + '" height="' + lado + '" rx="3" fill="none" stroke="' + TINTA + '" stroke-width=".5"/>';
      var fs = f(c * .6);
      s += '<g font-size="' + fs + '" text-anchor="middle" font-weight="700">';
      for (var a = 0; a < N; a++) {
        for (var b = 0; b < N; b++) s += '<text x="' + f(x0 + (b + .5) * c) + '" y="' + f(y0 + (a + .5) * c + fs * .36) + '">' + g[a][b] + '</text>';
      }
      s += '</g>';
      var cols = 4, filas = Math.ceil(puestas.length / cols), ly = y0 + lado + 11;
      s += txt(15, ly - 1, (spec.rotuloLista || 'Palabras escondidas') + ' (' + puestas.length + ')', { size: 3.6, fill: GRIS });
      puestas.forEach(function (p, n) {
        var col = Math.floor(n / filas), fila = n % filas;
        s += '<rect x="' + f(15 + col * 46) + '" y="' + f(ly + 3.6 + fila * 7) + '" width="3" height="3" fill="none" stroke="' + TINTA + '" stroke-width=".25"/>';
        s += txt(20 + col * 46, ly + 6.6 + fila * 7, p.ver, { size: p.ver.length > 13 ? 3.4 : 4.1 });
      });
      return s;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || SUBS_SOPA[spec.nivel || 'medio'], nombre: spec.nombre !== false, ingles: !!spec.inglesRotulos, seed: seed };
    return {
      svg: hoja(o, dibuja(false)),
      sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true))
    };
  }
  var SUBS_SOPA = {
    facil: 'Las palabras están en horizontal (de izquierda a derecha) y en vertical (de arriba abajo).',
    medio: 'Las palabras están en horizontal, en vertical y en diagonal. Ninguna va al revés.',
    dificil: 'Las palabras pueden ir en cualquier dirección, también al revés. Se escriben sin tildes.'
  };

  // ---------- sudoku ----------
  var CAJA = { 4: [2, 2], 6: [2, 3], 9: [3, 3] };
  var PISTAS = { 4: { facil: 8, medio: 6, dificil: 5 }, 6: { facil: 20, medio: 16, dificil: 13 }, 9: { facil: 38, medio: 31, dificil: 26 } };

  function candidatos(g, n, pos) {
    var br = CAJA[n][0], bc = CAJA[n][1], rr = Math.floor(pos / n), cc = pos % n, m = 0, i;
    for (i = 0; i < n; i++) { m |= 1 << g[rr * n + i]; m |= 1 << g[i * n + cc]; }
    var r0 = rr - rr % br, c0 = cc - cc % bc;
    for (i = 0; i < br; i++) for (var j = 0; j < bc; j++) m |= 1 << g[(r0 + i) * n + c0 + j];
    var out = [];
    for (i = 1; i <= n; i++) if (!(m & (1 << i))) out.push(i);
    return out;
  }
  function resuelve(g, n, limite, r) {
    var mejor = -1, mc = null, i;
    for (i = 0; i < n * n; i++) if (!g[i]) {
      var c = candidatos(g, n, i);
      if (!c.length) return 0;
      if (!mc || c.length < mc.length) { mejor = i; mc = c; if (c.length === 1) break; }
    }
    if (mejor < 0) return 1;
    if (r) mc = shuffle(r, mc);
    var total = 0;
    for (i = 0; i < mc.length; i++) {
      g[mejor] = mc[i];
      total += resuelve(g, n, limite - total, r);
      if (total >= limite) { if (!r) g[mejor] = 0; return total; }
    }
    g[mejor] = 0;
    return total;
  }
  function unSudoku(n, nivel, r) {
    var sol = new Array(n * n).fill(0);
    resuelve(sol, n, 1, r); // con r no deshace: deja la rejilla completa
    var g = sol.slice(), pistas = n * n, objetivo = PISTAS[n][nivel];
    var orden = shuffle(r, g.map(function (_, i) { return i; }));
    for (var k = 0; k < orden.length && pistas > objetivo; k++) {
      var p = orden[k], v = g[p];
      g[p] = 0;
      if (resuelve(g.slice(), n, 2, null) === 1) pistas--; else g[p] = v;
    }
    return { g: g, sol: sol };
  }
  function rejilla(s, n, x, y, lado, conSol) {
    var br = CAJA[n][0], bc = CAJA[n][1], c = lado / n, o = '', i;
    var fino = '', grueso = '';
    for (i = 1; i < n; i++) {
      var v = 'M' + f(x + i * c) + ' ' + y + 'v' + lado, h = 'M' + x + ' ' + f(y + i * c) + 'h' + lado;
      if (i % bc === 0) grueso += v; else fino += v;
      if (i % br === 0) grueso += h; else fino += h;
    }
    o += '<path d="' + fino + '" stroke="' + TINTA + '" stroke-width=".18" fill="none"/>';
    o += '<path d="' + grueso + '" stroke="' + TINTA + '" stroke-width=".6" fill="none"/>';
    o += '<rect x="' + x + '" y="' + y + '" width="' + lado + '" height="' + lado + '" fill="none" stroke="' + TINTA + '" stroke-width=".9"/>';
    var fs = f(c * .58);
    o += '<g font-size="' + fs + '" text-anchor="middle">';
    for (i = 0; i < n * n; i++) {
      var dado = s.g[i], val = dado || (conSol ? s.sol[i] : 0);
      if (!val) continue;
      o += '<text x="' + f(x + (i % n + .5) * c) + '" y="' + f(y + (Math.floor(i / n) + .5) * c + fs * .36) + '"' +
        (dado ? ' font-weight="700"' : ' fill="' + ROJO + '"') + '>' + val + '</text>';
    }
    return o + '</g>';
  }
  function sudoku(spec, seed) {
    var r = rng(seed), n = spec.n || 9, nivel = spec.nivel || 'medio', lista = [], i;
    for (i = 0; i < 4; i++) lista.push(unSudoku(n, nivel, r));
    function dibuja(sol) {
      var s = '', pos = [[15, 46], [110, 46], [15, 152], [110, 152]];
      lista.forEach(function (su, k) {
        s += txt(pos[k][0], pos[k][1] - 2.5, 'Sudoku ' + (k + 1), { size: 3.6, fill: GRIS });
        s += rejilla(su, n, pos[k][0], pos[k][1], 85, sol);
      });
      s += txt(15, 250, n === 9
        ? 'Cada fila, cada columna y cada caja de 3 × 3 debe contener los números del 1 al 9 sin repetir.'
        : 'Cada fila, cada columna y cada caja marcada debe contener los números del 1 al ' + n + ' sin repetir.', { size: 3.6, fill: GRIS });
      return s;
    }
    var o = { titulo: spec.titulo, sub: spec.sub, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- laberinto ----------
  function laberinto(spec, seed) {
    var r = rng(seed), C = spec.cols, R = spec.filas, i;
    var der = [], aba = [], vis = [];
    for (i = 0; i < R * C; i++) { der.push(true); aba.push(true); vis.push(false); }
    var pila = [0]; vis[0] = true;
    while (pila.length) {
      var cur = pila[pila.length - 1], cr = Math.floor(cur / C), cc = cur % C, vec = [];
      if (cr > 0 && !vis[cur - C]) vec.push(cur - C);
      if (cr < R - 1 && !vis[cur + C]) vec.push(cur + C);
      if (cc > 0 && !vis[cur - 1]) vec.push(cur - 1);
      if (cc < C - 1 && !vis[cur + 1]) vec.push(cur + 1);
      if (!vec.length) { pila.pop(); continue; }
      var nx = vec[ri(r, 0, vec.length - 1)];
      if (nx === cur + 1) der[cur] = false; else if (nx === cur - 1) der[nx] = false;
      else if (nx === cur + C) aba[cur] = false; else aba[nx] = false;
      vis[nx] = true; pila.push(nx);
    }
    // camino de la solución (búsqueda en anchura)
    var prev = new Array(R * C).fill(-1), cola = [0]; prev[0] = 0;
    while (cola.length) {
      var u = cola.shift(), ur = Math.floor(u / C), uc = u % C;
      var pasos = [];
      if (uc < C - 1 && !der[u]) pasos.push(u + 1);
      if (uc > 0 && !der[u - 1]) pasos.push(u - 1);
      if (ur < R - 1 && !aba[u]) pasos.push(u + C);
      if (ur > 0 && !aba[u - C]) pasos.push(u - C);
      pasos.forEach(function (v) { if (prev[v] < 0) { prev[v] = u; cola.push(v); } });
    }
    var camino = [], p = R * C - 1;
    while (p !== 0) { camino.push(p); p = prev[p]; }
    camino.push(0); camino.reverse();

    var c = Math.min(180 / C, 226 / R), W = c * C, H = c * R, x0 = (210 - W) / 2, y0 = 50;
    function dibuja(sol) {
      var d = 'M' + f(x0 + c) + ' ' + y0 + 'H' + f(x0 + W) + 'V' + f(y0 + H) + 'M' + f(x0 + W - c) + ' ' + f(y0 + H) + 'H' + f(x0) + 'V' + y0;
      for (var a = 0; a < R; a++) for (var b = 0; b < C; b++) {
        var k = a * C + b;
        if (b < C - 1 && der[k]) d += 'M' + f(x0 + (b + 1) * c) + ' ' + f(y0 + a * c) + 'v' + f(c);
        if (a < R - 1 && aba[k]) d += 'M' + f(x0 + b * c) + ' ' + f(y0 + (a + 1) * c) + 'h' + f(c);
      }
      var s = '';
      if (sol) {
        var pd = 'M' + f(x0 + c / 2) + ' ' + f(y0 - 2);
        camino.forEach(function (k) { pd += 'L' + f(x0 + (k % C + .5) * c) + ' ' + f(y0 + (Math.floor(k / C) + .5) * c); });
        pd += 'L' + f(x0 + W - c / 2) + ' ' + f(y0 + H + 2);
        s += '<path d="' + pd + '" fill="none" stroke="' + ROJO + '" stroke-width="' + f(Math.max(.6, c * .22)) + '" stroke-linejoin="round" stroke-linecap="round"/>';
      }
      s += '<path d="' + d + '" fill="none" stroke="' + TINTA + '" stroke-width="' + f(Math.max(.35, Math.min(.9, c * .09))) + '" stroke-linecap="square"/>';
      s += '<path d="M' + f(x0 + c / 2 - 2) + ' ' + f(y0 - 6) + 'h4l-2 3.4z"/>' + txt(x0 + c / 2 + 4, y0 - 3.4, 'Entrada', { size: 3.4, fill: GRIS });
      s += '<path d="M' + f(x0 + W - c / 2 - 2) + ' ' + f(y0 + H + 2.6) + 'h4l-2 3.4z"/>' + txt(x0 + W - c / 2 - 4, y0 + H + 5.6, 'Salida', { size: 3.4, fill: GRIS, anchor: 'end' });
      return s;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || 'Encuentra el camino desde la entrada hasta la salida sin atravesar ninguna pared.', nombre: spec.nombre !== false, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- bingo ----------
  function carton90(r) {
    var filas;
    for (;;) {
      filas = [0, 1, 2].map(function () { return shuffle(r, [0, 1, 2, 3, 4, 5, 6, 7, 8]).slice(0, 5); });
      var cubre = new Array(9).fill(0);
      filas.forEach(function (fl) { fl.forEach(function (c) { cubre[c]++; }); });
      if (cubre.every(function (n) { return n > 0; })) break;
    }
    var g = [[], [], []];
    for (var c = 0; c < 9; c++) {
      var min = c === 0 ? 1 : c * 10, max = c === 8 ? 90 : c * 10 + 9, pool = [];
      for (var n = min; n <= max; n++) pool.push(n);
      var en = [0, 1, 2].filter(function (f2) { return filas[f2].indexOf(c) >= 0; });
      var nums = shuffle(r, pool).slice(0, en.length).sort(function (a, b) { return a - b; });
      en.forEach(function (f2, i) { g[f2][c] = nums[i]; });
    }
    return g;
  }
  function bingo90(spec, seed) {
    var r = rng(seed), s = '', y = 30, w = 20, h = 11.5;
    for (var k = 0; k < 6; k++) {
      var g = carton90(r);
      for (var a = 0; a < 3; a++) for (var b = 0; b < 9; b++) {
        var x = 15 + b * w, yy = y + a * h, n = g[a][b];
        s += '<rect x="' + x + '" y="' + f(yy) + '" width="' + w + '" height="' + h + '" fill="' + (n ? '#fff' : '#e4e1d8') + '" stroke="' + TINTA + '" stroke-width=".3"/>';
        if (n) s += txt(x + w / 2, yy + h / 2 + 2.5, n, { size: 7, anchor: 'middle', bold: true });
      }
      s += '<rect x="15" y="' + f(y) + '" width="180" height="' + (h * 3) + '" fill="none" stroke="' + TINTA + '" stroke-width=".8"/>';
      if (k < 5) s += '<path d="M10 ' + f(y + h * 3 + 3.5) + 'H200" stroke="#8a8a90" stroke-width=".2" stroke-dasharray="1.5 1.5"/>';
      y += h * 3 + 7;
    }
    return { svg: hoja({ titulo: spec.titulo || 'Cartones de bingo', seed: seed, sub: null }, s), sol: null };
  }
  function bingo75(spec, seed) {
    var r = rng(seed), s = '', pos = [[15, 34], [110, 34], [15, 146], [110, 146]], w = 17;
    pos.forEach(function (p) {
      var x0 = p[0], y0 = p[1];
      s += '<rect x="' + x0 + '" y="' + y0 + '" width="85" height="12" fill="' + TINTA + '"/>';
      'BINGO'.split('').forEach(function (l, i) { s += txt(x0 + i * w + w / 2, y0 + 9, l, { size: 8, anchor: 'middle', fill: '#fff', titular: true }); });
      for (var c = 0; c < 5; c++) {
        var pool = []; for (var n = c * 15 + 1; n <= c * 15 + 15; n++) pool.push(n);
        var nums = shuffle(r, pool).slice(0, 5);
        for (var a = 0; a < 5; a++) {
          var x = x0 + c * w, y = y0 + 12 + a * w, libre = c === 2 && a === 2;
          s += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + w + '" fill="' + (libre ? '#e4e1d8' : '#fff') + '" stroke="' + TINTA + '" stroke-width=".3"/>';
          s += libre ? txt(x + w / 2, y + w / 2 + 1.2, 'LIBRE', { size: 3.4, anchor: 'middle', bold: true })
            : txt(x + w / 2, y + w / 2 + 2.8, nums[a], { size: 8, anchor: 'middle', bold: true });
        }
      }
      s += '<rect x="' + x0 + '" y="' + y0 + '" width="85" height="97" fill="none" stroke="' + TINTA + '" stroke-width=".8"/>';
    });
    return { svg: hoja({ titulo: spec.titulo || 'Cartones de bingo de 75 bolas', seed: seed }, s), sol: null };
  }
  function bingoNumeros(spec) {
    var s = '', w = 18, total = spec.hasta || 90, filas = Math.ceil(total / 10);
    for (var n = 1; n <= total; n++) {
      var x = 15 + ((n - 1) % 10) * w, y = 40 + Math.floor((n - 1) / 10) * w;
      s += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + w + '" fill="#fff" stroke="#55555c" stroke-width=".25" stroke-dasharray="1.2 1.2"/>';
      s += txt(x + w / 2, y + w / 2 + 3.3, n, { size: 9, anchor: 'middle', bold: true });
      if (n === 6 || n === 9) s += '<path d="M' + (x + 6) + ' ' + (y + 14.5) + 'h6" stroke="' + TINTA + '" stroke-width=".5"/>';
    }
    s += txt(15, 40 + filas * w + 8, 'Recorta los números por la línea de puntos, dóblalos y mételos en una bolsa. El 6 y el 9 van subrayados para no confundirlos.', { size: 3.3, fill: GRIS });
    return { svg: hoja({ titulo: spec.titulo || 'Números del 1 al ' + total, sub: 'Para cantar el bingo sin bombo.' }, s), sol: null };
  }

  // ---------- tablas de multiplicar ----------
  function filaMult(x, y, a, b, size, res, colorRes) {
    var u = size / 10;
    return txt(x + 8 * u, y, a, { size: size, anchor: 'end', bold: true }) +
      txt(x + 12.5 * u, y, '×', { size: size, anchor: 'middle' }) +
      txt(x + 28 * u, y, b, { size: size, anchor: 'end', bold: true }) +
      txt(x + 33.5 * u, y, '=', { size: size, anchor: 'middle' }) +
      (res != null ? txt(x + 54 * u, y, res, { size: size, anchor: 'end', bold: true, fill: colorRes })
        : '<path d="M' + f(x + 39 * u) + ' ' + f(y + u) + 'h' + f(15 * u) + '" stroke="' + TINTA + '" stroke-width=".25"/>');
  }
  function tabla(spec, seed) {
    function dibuja(lleno, color) {
      var s = '';
      for (var b = 1; b <= 10; b++) s += filaMult(62, 50 + b * 21.5, spec.n, b, 13, lleno ? spec.n * b : null, color);
      return s;
    }
    var o = { titulo: spec.titulo || 'Tabla del ' + spec.n, sub: spec.vacia ? 'Completa los resultados.' : null, nombre: !!spec.vacia };
    return { svg: hoja(o, dibuja(!spec.vacia)), sol: spec.vacia ? hoja(Object.assign({}, o, { sol: true }), dibuja(true, ROJO)) : null };
  }
  function tablasTodas(spec) {
    function dibuja(lleno, color) {
      var s = '';
      for (var n = 1; n <= 10; n++) {
        var x = 15 + ((n - 1) % 5) * 36.5, y = n <= 5 ? 50 : 168;
        s += '<rect x="' + f(x) + '" y="' + (y - 6) + '" width="33" height="8.5" fill="' + TINTA + '"/>' +
          txt(x + 16.5, y, 'Tabla del ' + n, { size: 4.3, anchor: 'middle', fill: '#fff', bold: true });
        for (var b = 1; b <= 10; b++) s += filaMult(x + 3.5, y + 2 + b * 9.6, n, b, 5.2, lleno ? n * b : null, color);
      }
      return s;
    }
    var o = { titulo: spec.titulo || 'Tablas de multiplicar del 1 al 10', sub: spec.vacia ? 'Completa todos los resultados.' : null, nombre: !!spec.vacia };
    return { svg: hoja(o, dibuja(!spec.vacia)), sol: spec.vacia ? hoja(Object.assign({}, o, { sol: true }), dibuja(true, ROJO)) : null };
  }
  function pitagorica(spec) {
    function dibuja(lleno, color) {
      var s = '', c = 16, x0 = 17, y0 = 50;
      for (var a = 0; a <= 10; a++) for (var b = 0; b <= 10; b++) {
        var cab = a === 0 || b === 0, x = x0 + b * c, y = y0 + a * c;
        s += '<rect x="' + x + '" y="' + y + '" width="' + c + '" height="' + c + '" fill="' + (cab ? '#e4e1d8' : '#fff') + '" stroke="' + TINTA + '" stroke-width=".3"/>';
        var v = a === 0 && b === 0 ? '×' : cab ? a + b : (lleno ? a * b : '');
        if (v !== '') s += txt(x + c / 2, y + c / 2 + 2.3, v, { size: 6.2, anchor: 'middle', bold: cab, fill: !cab && color ? color : null });
      }
      s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + (c * 11) + '" height="' + (c * 11) + '" fill="none" stroke="' + TINTA + '" stroke-width=".8"/>';
      s += txt(15, y0 + c * 11 + 9, 'Busca un número en la primera columna y otro en la primera fila: donde se cruzan está el resultado.', { size: 3.5, fill: GRIS });
      return s;
    }
    var o = { titulo: spec.titulo || 'Tabla pitagórica', sub: spec.vacia ? 'Rellena cada casilla multiplicando su fila por su columna.' : null, nombre: !!spec.vacia };
    return { svg: hoja(o, dibuja(!spec.vacia)), sol: spec.vacia ? hoja(Object.assign({}, o, { sol: true }), dibuja(true, ROJO)) : null };
  }
  function multPractica(spec, seed) {
    var r = rng(seed), ops = [], ult = '';
    while (ops.length < 30) {
      var tanda = [];
      spec.tablas.forEach(function (n) { for (var b = 1; b <= 10; b++) tanda.push([n, b]); });
      tanda = shuffle(r, tanda);
      tanda.forEach(function (o) { if (ops.length < 30 && o.join() !== ult) { ops.push(o); ult = o.join(); } });
    }
    function dibuja(sol) {
      var s = '';
      ops.forEach(function (o, i) { s += filaMult(15 + Math.floor(i / 10) * 63, 60 + (i % 10) * 22, o[0], o[1], 8, sol ? o[0] * o[1] : null, ROJO); });
      return s;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || 'Resuelve las 30 multiplicaciones. Están desordenadas a propósito.', nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- sumas y restas ----------
  function digitos(n) { return String(n).split('').map(Number).reverse(); }
  function llevadas(a, b, resta) {
    var da = digitos(a), db = digitos(b), acarreo = 0, total = 0;
    for (var i = 0; i < da.length; i++) {
      var x = da[i], y = db[i] || 0;
      if (resta) { if (x - acarreo < y) { acarreo = 1; total++; } else acarreo = 0; }
      else { if (x + y + acarreo > 9) { acarreo = 1; total++; } else acarreo = 0; }
    }
    return total;
  }
  function operaciones(spec, seed) {
    var r = rng(seed), d = spec.digitos || 2, min = Math.pow(10, d - 1), max = Math.pow(10, d) - 1, ops = [], vistos = {};
    var intentos = 0;
    while (ops.length < 20 && intentos++ < 20000) {
      var resta = spec.op === 'resta' || (spec.op === 'mixta' && ops.length % 2 === 1);
      var a = ri(r, min, max), b = ri(r, min, max);
      if (resta && a < b) { var t = a; a = b; b = t; }
      if (resta && a === b) continue;
      if ((llevadas(a, b, resta) > 0) !== !!spec.llevada) continue;
      var clave = a + (resta ? '-' : '+') + b;
      if (vistos[clave]) continue;
      vistos[clave] = 1; ops.push({ a: a, b: b, resta: resta, res: resta ? a - b : a + b });
    }
    function num(x, y, n, color) {
      return String(n).split('').reverse().map(function (ch, i) {
        return txt(x - i * 6.4, y, ch, { size: 9.5, anchor: 'middle', bold: true, fill: color });
      }).join('');
    }
    function dibuja(sol) {
      var s = '';
      ops.forEach(function (o, i) {
        var xr = 15 + (i % 4) * 45 + 36, y = 60 + Math.floor(i / 4) * 46;
        s += num(xr, y, o.a) + num(xr, y + 11, o.b);
        s += txt(xr - (d + .4) * 6.4, y + 11, o.resta ? '−' : '+', { size: 9.5, anchor: 'middle' });
        s += '<path d="M' + f(xr - (d + 1) * 6.4) + ' ' + (y + 14.5) + 'H' + (xr + 4) + '" stroke="' + TINTA + '" stroke-width=".5"/>';
        if (sol) s += num(xr, y + 25, o.res, ROJO);
      });
      return s;
    }
    var o = { titulo: spec.titulo, sub: spec.sub, nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- papel ----------
  function lineas(x0, y0, x1, y1, paso, filtro) {
    var d = '', i, n;
    for (i = 0, n = Math.round((x1 - x0) / paso); i <= n; i++) if (filtro(i)) d += 'M' + f(x0 + i * paso) + ' ' + y0 + 'V' + y1;
    for (i = 0, n = Math.round((y1 - y0) / paso); i <= n; i++) if (filtro(i)) d += 'M' + x0 + ' ' + f(y0 + i * paso) + 'H' + x1;
    return d;
  }
  function papel(spec) {
    var s = '', c, y, i;
    if (spec.clase === 'milimetrado') {
      c = spec.color || '#c9772e';
      s += '<path d="' + lineas(10, 13, 200, 283, 1, function (i) { return i % 5 !== 0; }) + '" stroke="' + c + '" stroke-width=".07" stroke-opacity=".8" fill="none"/>';
      s += '<path d="' + lineas(10, 13, 200, 283, 5, function (i) { return i % 2 !== 0; }) + '" stroke="' + c + '" stroke-width=".14" fill="none"/>';
      s += '<path d="' + lineas(10, 13, 200, 283, 10, function () { return true; }) + '" stroke="' + c + '" stroke-width=".28" fill="none"/>';
    } else if (spec.clase === 'cuadriculado') {
      var p = spec.paso || 4, w = Math.floor(190 / p) * p, h = Math.floor(272 / p) * p, x0 = (210 - w) / 2, y0 = (297 - h) / 2 - 1;
      s += '<path d="' + lineas(x0, y0, x0 + w, y0 + h, p, function () { return true; }) + '" stroke="#7f93b8" stroke-width=".15" fill="none"/>';
    } else if (spec.clase === 'puntos') {
      var pp = spec.paso || 5;
      for (y = 15; y <= 282; y += pp) s += '<path d="M12.5 ' + y + 'H198" stroke="#77777f" stroke-width=".55" stroke-linecap="round" stroke-dasharray="0 ' + pp + '"/>';
    } else if (spec.clase === 'pautado') {
      var pa = spec.pauta || 3.5, d = '', d2 = '';
      for (y = 22; y + pa <= 280; y += pa * 3.2) { d += 'M15 ' + f(y) + 'H195M15 ' + f(y + pa) + 'H195'; }
      s += '<path d="' + d + '" stroke="#7f93b8" stroke-width=".2" fill="none"/>';
      s += '<path d="M28 12V285" stroke="' + ROJO + '" stroke-opacity=".6" stroke-width=".2"/>';
    } else if (spec.clase === 'rayado') {
      var pr = spec.paso || 8, dr = '';
      for (y = 28; y <= 282; y += pr) dr += 'M12 ' + y + 'H198';
      s += '<path d="' + dr + '" stroke="#7f93b8" stroke-width=".2" fill="none"/>';
      s += '<path d="M28 12V285" stroke="' + ROJO + '" stroke-opacity=".6" stroke-width=".2"/>';
    } else if (spec.clase === 'pentagrama') {
      var n = spec.n || 10, sep = spec.sep || 2, hueco = (262 - n * sep * 4) / (n - 1), dp = '';
      for (i = 0; i < n; i++) {
        var yy = 18 + i * (sep * 4 + hueco);
        for (var l = 0; l < 5; l++) dp += 'M15 ' + f(yy + l * sep) + 'H195';
        dp += 'M15 ' + f(yy) + 'v' + sep * 4 + 'M195 ' + f(yy) + 'v' + sep * 4;
      }
      s += '<path d="' + dp + '" stroke="' + TINTA + '" stroke-width=".2" fill="none"/>';
    }
    s += txt(105, 292.5, 'imprimibles.es', { size: 2.4, anchor: 'middle', fill: '#b5b5ba' });
    return { svg: hoja({ alt: spec.alt || 'Papel para imprimir', sinPie: true }, s), sol: null };
  }

  // ---------- Navidad ----------
  // Dibujos de línea (sin relleno, para colorear) centrados en cx, cy con tamaño s
  function dibujo(i, cx, cy, s, color, grosor) {
    var st = ' fill="none" stroke="' + (color || TINTA) + '" stroke-width="' + f(grosor || Math.max(.35, s * .06)) + '" stroke-linejoin="round" stroke-linecap="round"';
    var o = '', k, p = [];
    if (i === 0) { // estrella
      for (k = 0; k < 10; k++) {
        var rad = k % 2 ? s * .2 : s * .48, a = -Math.PI / 2 + k * Math.PI / 5;
        p.push(f(cx + rad * Math.cos(a)) + ',' + f(cy + rad * Math.sin(a) + s * .04));
      }
      o = '<polygon points="' + p.join(' ') + '"' + st + '/>';
    } else if (i === 1) { // árbol
      o = '<path d="M' + f(cx) + ' ' + f(cy - s * .48) + 'L' + f(cx + s * .24) + ' ' + f(cy - s * .1) + 'H' + f(cx + s * .12) +
        'L' + f(cx + s * .4) + ' ' + f(cy + s * .3) + 'H' + f(cx - s * .4) + 'L' + f(cx - s * .12) + ' ' + f(cy - s * .1) + 'H' + f(cx - s * .24) + 'Z' +
        'M' + f(cx - s * .08) + ' ' + f(cy + s * .3) + 'V' + f(cy + s * .48) + 'H' + f(cx + s * .08) + 'V' + f(cy + s * .3) + '"' + st + '/>';
    } else if (i === 2) { // regalo
      o = '<path d="M' + f(cx - s * .4) + ' ' + f(cy - s * .16) + 'h' + f(s * .8) + 'v' + f(s * .16) + 'h' + f(-s * .8) + 'z' +
        'M' + f(cx - s * .34) + ' ' + f(cy) + 'v' + f(s * .44) + 'h' + f(s * .68) + 'v' + f(-s * .44) +
        'M' + f(cx) + ' ' + f(cy - s * .16) + 'v' + f(s * .6) +
        'M' + f(cx) + ' ' + f(cy - s * .16) + 'C' + f(cx - s * .1) + ' ' + f(cy - s * .48) + ' ' + f(cx - s * .38) + ' ' + f(cy - s * .36) + ' ' + f(cx) + ' ' + f(cy - s * .16) +
        'C' + f(cx + s * .1) + ' ' + f(cy - s * .48) + ' ' + f(cx + s * .38) + ' ' + f(cy - s * .36) + ' ' + f(cx) + ' ' + f(cy - s * .16) + '"' + st + '/>';
    } else if (i === 3) { // campana
      o = '<path d="M' + f(cx - s * .42) + ' ' + f(cy + s * .26) + 'C' + f(cx - s * .3) + ' ' + f(cy + s * .14) + ' ' + f(cx - s * .32) + ' ' + f(cy - s * .4) +
        ' ' + f(cx) + ' ' + f(cy - s * .4) + 'C' + f(cx + s * .32) + ' ' + f(cy - s * .4) + ' ' + f(cx + s * .3) + ' ' + f(cy + s * .14) + ' ' + f(cx + s * .42) + ' ' + f(cy + s * .26) + 'Z' +
        'M' + f(cx) + ' ' + f(cy - s * .4) + 'V' + f(cy - s * .48) + '"' + st + '/>' +
        '<circle cx="' + f(cx) + '" cy="' + f(cy + s * .36) + '" r="' + f(s * .09) + '"' + st + '/>';
    } else if (i === 4) { // bola
      o = '<circle cx="' + f(cx) + '" cy="' + f(cy + s * .06) + '" r="' + f(s * .38) + '"' + st + '/>' +
        '<path d="M' + f(cx - s * .1) + ' ' + f(cy - s * .32) + 'v' + f(-s * .1) + 'h' + f(s * .2) + 'v' + f(s * .1) +
        'M' + f(cx - s * .36) + ' ' + f(cy + s * .02) + 'Q' + f(cx) + ' ' + f(cy + s * .16) + ' ' + f(cx + s * .36) + ' ' + f(cy + s * .02) + '"' + st + '/>';
    } else { // vela
      o = '<path d="M' + f(cx - s * .16) + ' ' + f(cy - s * .1) + 'V' + f(cy + s * .48) + 'H' + f(cx + s * .16) + 'V' + f(cy - s * .1) + 'Z' +
        'M' + f(cx) + ' ' + f(cy - s * .16) + 'C' + f(cx - s * .14) + ' ' + f(cy - s * .26) + ' ' + f(cx - s * .02) + ' ' + f(cy - s * .4) + ' ' + f(cx) + ' ' + f(cy - s * .48) +
        'C' + f(cx + s * .02) + ' ' + f(cy - s * .4) + ' ' + f(cx + s * .14) + ' ' + f(cy - s * .26) + ' ' + f(cx) + ' ' + f(cy - s * .16) + 'Z"' + st + '/>';
    }
    return o;
  }
  var NOMBRES_DIBUJO = ['estrella', 'árbol', 'regalo', 'campana', 'bola', 'vela'];

  // Sudoku con dibujos en lugar de números (4 × 4 o 6 × 6)
  function sudokuDibujos(spec, seed) {
    var r = rng(seed), n = spec.n || 4, nivel = spec.nivel || 'facil', lista = [], i;
    for (i = 0; i < 4; i++) lista.push(unSudoku(n, nivel, r));
    function rejillaD(su, x, y, lado, conSol) {
      var br = CAJA[n][0], bc = CAJA[n][1], c = lado / n, fino = '', grueso = '', o = '';
      for (i = 1; i < n; i++) {
        var v = 'M' + f(x + i * c) + ' ' + y + 'v' + lado, h = 'M' + x + ' ' + f(y + i * c) + 'h' + lado;
        if (i % bc === 0) grueso += v; else fino += v;
        if (i % br === 0) grueso += h; else fino += h;
      }
      o += '<path d="' + fino + '" stroke="' + TINTA + '" stroke-width=".2" fill="none"/><path d="' + grueso + '" stroke="' + TINTA + '" stroke-width=".7" fill="none"/>';
      o += '<rect x="' + x + '" y="' + y + '" width="' + lado + '" height="' + lado + '" fill="none" stroke="' + TINTA + '" stroke-width="1"/>';
      for (i = 0; i < n * n; i++) {
        var dado = su.g[i], val = dado || (conSol ? su.sol[i] : 0);
        if (val) o += dibujo(val - 1, x + (i % n + .5) * c, y + (Math.floor(i / n) + .5) * c, c * .66, dado ? TINTA : ROJO, dado ? null : c * .05);
      }
      return o;
    }
    function dibuja(sol) {
      var s = '', pos = [[15, 70], [110, 70], [15, 166], [110, 166]], w = 180 / n;
      for (i = 0; i < n; i++) {
        s += dibujo(i, 15 + (i + .5) * w, 52, 9) + txt(15 + (i + .5) * w, 62, NOMBRES_DIBUJO[i], { size: 3.4, anchor: 'middle', fill: GRIS });
      }
      lista.forEach(function (su, k) {
        s += txt(pos[k][0], pos[k][1] - 2.5, 'Sudoku ' + (k + 1), { size: 3.6, fill: GRIS });
        s += rejillaD(su, pos[k][0], pos[k][1], 85, sol);
      });
      s += txt(15, 264, 'En cada fila, cada columna y cada caja marcada tiene que estar cada dibujo una sola vez.', { size: 3.6, fill: GRIS });
      s += txt(15, 270, 'Dibuja los que faltan. Al terminar, puedes colorearlos.', { size: 3.6, fill: GRIS });
      return s;
    }
    var o = { titulo: spec.titulo, nombre: false, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // Bingo de palabras: dos cartones de 4 × 4 por hoja, con casillas grandes
  function lineasPalabra(t) {
    var p = t.split(' ');
    if (p.length < 2) return [t];
    var mejor = null;
    for (var i = 1; i < p.length; i++) {
      var a = p.slice(0, i).join(' '), b = p.slice(i).join(' '), d = Math.max(a.length, b.length);
      if (!mejor || d < mejor.d) mejor = { d: d, l: [a, b] };
    }
    return mejor.l;
  }
  function palabraEnCaja(t, cx, cy, ancho, max) {
    var l = lineasPalabra(t), largo = Math.max.apply(null, l.map(function (x) { return x.length; }));
    var size = Math.min(max, ancho / (largo * .68)), o = '';
    l.forEach(function (x, i) { o += txt(cx, cy + size * .36 + (i - (l.length - 1) / 2) * size * 1.12, x, { size: f(size), anchor: 'middle', bold: true }); });
    return o;
  }
  function bingoPalabras(spec, seed) {
    var r = rng(seed), s = '', w = 45, h = 26;
    [34, 160].forEach(function (y0, n) {
      var palabras = shuffle(r, spec.palabras).slice(0, 16);
      s += '<rect x="15" y="' + y0 + '" width="180" height="11" fill="' + TINTA + '"/>';
      s += txt(105, y0 + 7.8, spec.cabecera || 'BINGO', { size: 6.4, anchor: 'middle', fill: '#fff', titular: true });
      palabras.forEach(function (pal, k) {
        var x = 15 + (k % 4) * w, y = y0 + 11 + Math.floor(k / 4) * h;
        s += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="#fff" stroke="' + TINTA + '" stroke-width=".3"/>';
        s += palabraEnCaja(pal.toUpperCase(), x + w / 2, y + h / 2, w - 6, 6.6);
      });
      s += '<rect x="15" y="' + y0 + '" width="180" height="' + (11 + 4 * h) + '" fill="none" stroke="' + TINTA + '" stroke-width=".8"/>';
      if (!n) s += '<path d="M10 ' + (y0 + 11 + 4 * h + 5) + 'H200" stroke="#8a8a90" stroke-width=".2" stroke-dasharray="1.5 1.5"/>';
    });
    return { svg: hoja({ titulo: spec.titulo, seed: seed }, s), sol: null };
  }
  function bingoPalabrasLista(spec) {
    var s = '', w = 45, h = 18, lista = spec.palabras.slice().sort(function (a, b) { return a.localeCompare(b, 'es'); });
    lista.forEach(function (pal, k) {
      var x = 15 + (k % 4) * w, y = 42 + Math.floor(k / 4) * h;
      s += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="#fff" stroke="#55555c" stroke-width=".25" stroke-dasharray="1.2 1.2"/>';
      s += palabraEnCaja(pal.toUpperCase(), x + w / 2, y + h / 2, w - 8, 5.4);
    });
    var yf = 42 + Math.ceil(lista.length / 4) * h + 9;
    s += txt(15, yf, 'Recorta las palabras, dóblalas y mételas en una bolsa. Saca una cada vez y léela en voz alta.', { size: 3.4, fill: GRIS });
    s += txt(15, yf + 6, 'Imprime otra copia sin recortar para ir marcando las que ya han salido.', { size: 3.4, fill: GRIS });
    return { svg: hoja({ titulo: spec.titulo, sub: 'Las ' + lista.length + ' palabras que pueden salir en los cartones.' }, s), sol: null };
  }

  // Laberinto con forma de árbol de Navidad
  function laberintoArbol(spec, seed) {
    var r = rng(seed), C = spec.cols, R = spec.filas, cx = (C - 1) / 2, half = (C - 1) / 2;
    var tronco = Math.max(2, Math.round(R * .12)), cuerpo = R - tronco;
    var cortes = [0, Math.round(cuerpo * .3), Math.round(cuerpo * .63), cuerpo];
    var ini = [0, half * .3, half * .5], fin = [half * .45, half * .75, half];
    var anchoT = Math.max(1, Math.round(half * .12));
    function hw(fila) {
      if (fila >= cuerpo) return anchoT;
      for (var t = 0; t < 3; t++) if (fila < cortes[t + 1]) {
        var a = cortes[t], b = cortes[t + 1] - 1;
        return Math.round(ini[t] + (fin[t] - ini[t]) * (b > a ? (fila - a) / (b - a) : 1));
      }
    }
    var dentro = [], i, k;
    for (i = 0; i < R * C; i++) dentro.push(Math.abs(i % C - cx) <= hw(Math.floor(i / C)));
    var inicio = cx, final = (R - 1) * C + cx;
    var paso = {}, vis = {}, pila = [inicio];
    function clave(a, b) { return a < b ? a + '-' + b : b + '-' + a; }
    function vecinos(u) {
      var ur = Math.floor(u / C), uc = u % C, v = [];
      if (ur > 0) v.push(u - C); if (ur < R - 1) v.push(u + C);
      if (uc > 0) v.push(u - 1); if (uc < C - 1) v.push(u + 1);
      return v.filter(function (x) { return dentro[x]; });
    }
    vis[inicio] = 1;
    while (pila.length) {
      var cur = pila[pila.length - 1], libres = vecinos(cur).filter(function (x) { return !vis[x]; });
      if (!libres.length) { pila.pop(); continue; }
      var nx = libres[ri(r, 0, libres.length - 1)];
      paso[clave(cur, nx)] = 1; vis[nx] = 1; pila.push(nx);
    }
    var prev = {}, cola = [inicio]; prev[inicio] = inicio;
    while (cola.length) {
      var u = cola.shift();
      vecinos(u).forEach(function (v) { if (prev[v] == null && paso[clave(u, v)]) { prev[v] = u; cola.push(v); } });
    }
    var camino = [], p = final;
    while (p !== inicio) { camino.push(p); p = prev[p]; }
    camino.push(inicio); camino.reverse();

    var c = Math.min(180 / C, 210 / R), x0 = (210 - C * c) / 2, y0 = 60;
    function X(col) { return x0 + col * c; } function Y(fila) { return y0 + fila * c; }
    function dibuja(sol) {
      var d = '';
      for (k = 0; k < R * C; k++) {
        if (!dentro[k]) continue;
        var fr = Math.floor(k / C), fc = k % C;
        var arriba = fr > 0 ? k - C : -1, izq = fc > 0 ? k - 1 : -1, der = fc < C - 1 ? k + 1 : -1, abajo = fr < R - 1 ? k + C : -1;
        if ((arriba < 0 || !dentro[arriba]) && k !== inicio) d += 'M' + f(X(fc)) + ' ' + f(Y(fr)) + 'h' + f(c);
        if (izq < 0 || !dentro[izq]) d += 'M' + f(X(fc)) + ' ' + f(Y(fr)) + 'v' + f(c);
        if (der < 0 || !dentro[der] || !paso[clave(k, der)]) d += 'M' + f(X(fc + 1)) + ' ' + f(Y(fr)) + 'v' + f(c);
        if (abajo < 0 || !dentro[abajo] ? k !== final : !paso[clave(k, abajo)]) d += 'M' + f(X(fc)) + ' ' + f(Y(fr + 1)) + 'h' + f(c);
      }
      var s = '';
      if (sol) {
        var pd = 'M' + f(X(cx + .5)) + ' ' + f(y0 - 1.5);
        camino.forEach(function (q) { pd += 'L' + f(X(q % C + .5)) + ' ' + f(Y(Math.floor(q / C) + .5)); });
        pd += 'L' + f(X(cx + .5)) + ' ' + f(Y(R) + 1.5);
        s += '<path d="' + pd + '" fill="none" stroke="' + ROJO + '" stroke-width="' + f(Math.max(.6, c * .22)) + '" stroke-linejoin="round" stroke-linecap="round"/>';
      }
      s += '<path d="' + d + '" fill="none" stroke="' + TINTA + '" stroke-width="' + f(Math.max(.4, Math.min(.9, c * .1))) + '" stroke-linecap="square"/>';
      s += dibujo(0, X(cx + .5), y0 - 7.5, 12, TINTA, .55);
      s += txt(X(cx + .5) + 9, y0 - 6, 'Empieza aquí', { size: 3.4, fill: GRIS });
      s += dibujo(2, X(cx + .5), Y(R) + 8, 11, TINTA, .55);
      s += txt(X(cx + .5) + 9, Y(R) + 9, 'Llega al regalo', { size: 3.4, fill: GRIS });
      return s;
    }
    var o = { titulo: spec.titulo, sub: 'Baja desde la estrella hasta el regalo sin atravesar ninguna pared.', nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // Carta a los Reyes Magos o a Papá Noel
  function corona(x, y) {
    return '<path d="M' + x + ' ' + (y + 9) + 'V' + y + 'l3.5 4.5 3.5-6 3.5 6 3.5-4.5V' + (y + 9) + 'Z" fill="none" stroke="' + TINTA + '" stroke-width=".5" stroke-linejoin="round"/>' +
      '<circle cx="' + x + '" cy="' + (y - 1) + '" r="1" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>' +
      '<circle cx="' + (x + 7) + '" cy="' + (y - 2.6) + '" r="1" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>' +
      '<circle cx="' + (x + 14) + '" cy="' + (y - 1) + '" r="1" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>';
  }
  function carta(spec) {
    var reyes = spec.para !== 'papanoel', pauta = !!spec.pauta, s = '', y;
    var t = reyes
      ? { saludo: 'Queridos Reyes Magos:', pido: 'Este año os pido:', pidoDibujo: 'Os pido estos regalos (dibújalos o pega aquí los recortes del catálogo):', decir: 'También quiero deciros:', dibujo: 'Os he hecho este dibujo:', despedida: 'Un beso muy fuerte,' }
      : { saludo: 'Querido Papá Noel:', pido: 'Este año te pido:', pidoDibujo: 'Te pido estos regalos (dibújalos o pega aquí los recortes del catálogo):', decir: 'También quiero decirte:', dibujo: 'Te he hecho este dibujo:', despedida: 'Un beso muy fuerte,' };
    function renglon(x1, x2, yy) {
      if (!pauta) return '<path d="M' + x1 + ' ' + f(yy) + 'H' + x2 + '" stroke="#8a8a90" stroke-width=".25"/>';
      return '<path d="M' + x1 + ' ' + f(yy - 4) + 'H' + x2 + 'M' + x1 + ' ' + f(yy) + 'H' + x2 + '" stroke="#7f93b8" stroke-width=".25"/>';
    }
    if (reyes) { s += corona(148, 16) + corona(166, 13) + corona(184, 16); }
    else { s += dibujo(0, 160, 20, 13) + dibujo(3, 176, 20, 12) + dibujo(2, 191, 20, 12); }
    s += txt(15, 32, t.saludo, { size: 9, titular: true });
    s += txt(15, 46, 'Me llamo', { size: 5 }) + renglon(37, 125, 46) + txt(128, 46, 'y tengo', { size: 5 }) + renglon(148, 165, 46) + txt(167, 46, 'años.', { size: 5 });
    s += txt(15, 59, 'Este año me he portado:', { size: 5 });
    ['muy bien', 'bien', 'regular'].forEach(function (op, i) {
      var x = 83 + i * 37;
      s += '<rect x="' + x + '" y="54.6" width="5" height="5" rx=".6" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>' + txt(x + 7.5, 59, op, { size: 5 });
    });
    if (spec.modo === 'dibujar') {
      s += txt(15, 73, t.pidoDibujo, { size: 5, bold: true });
      for (y = 0; y < 4; y++) {
        var bx = 15 + (y % 2) * 92, by = 79 + Math.floor(y / 2) * 84;
        s += '<rect x="' + bx + '" y="' + by + '" width="88" height="78" rx="3" fill="none" stroke="' + TINTA + '" stroke-width=".4" stroke-dasharray="2 1.5"/>';
        s += '<circle cx="' + (bx + 7) + '" cy="' + (by + 7) + '" r="4" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>' + txt(bx + 7, by + 8.7, y + 1, { size: 4.6, anchor: 'middle', bold: true });
      }
      s += txt(15, 264, t.despedida, { size: 5 }) + renglon(70, 140, 264);
      return { svg: hoja({ alt: (reyes ? 'Carta a los Reyes Magos' : 'Carta a Papá Noel') + ' para dibujar o pegar los regalos' }, s), sol: null };
    }
    s += txt(15, 73, t.pido, { size: 5, bold: true });
    for (y = 0; y < 5; y++) s += txt(17, 85 + y * 11, (y + 1) + '.', { size: 5, fill: GRIS }) + renglon(25, 195, 85 + y * 11);
    s += txt(15, 145, t.decir, { size: 5, bold: true });
    for (y = 0; y < 3; y++) s += renglon(15, 195, 157 + y * 11);
    s += txt(15, 194, t.dibujo, { size: 5, bold: true });
    s += '<rect x="15" y="198" width="180" height="62" rx="3" fill="none" stroke="' + TINTA + '" stroke-width=".4" stroke-dasharray="2 1.5"/>';
    s += txt(15, 272, t.despedida, { size: 5 }) + renglon(70, 140, 272);
    var nombre = reyes ? 'Carta a los Reyes Magos' : 'Carta a Papá Noel';
    return { svg: hoja({ alt: nombre + (pauta ? ' con pauta' : '') }, s), sol: null };
  }

  // Sobre para la carta: plantilla para recortar y doblar (las solapas van hacia atrás)
  function sobre(spec) {
    var reyes = spec.para !== 'papanoel', W = 114, H = 152, x0 = (210 - W) / 2, y0 = 52, lado = 26, sup = 42, inf = 66, s = '';
    var corte = 'M' + x0 + ' ' + y0 + 'C' + (x0 + 8) + ' ' + (y0 - sup) + ' ' + (x0 + W - 8) + ' ' + (y0 - sup) + ' ' + (x0 + W) + ' ' + y0 +
      'L' + (x0 + W + lado) + ' ' + (y0 + 14) + 'V' + (y0 + H - 14) + 'L' + (x0 + W) + ' ' + (y0 + H) +
      'L' + (x0 + W - 10) + ' ' + (y0 + H + inf) + 'H' + (x0 + 10) + 'L' + x0 + ' ' + (y0 + H) +
      'L' + (x0 - lado) + ' ' + (y0 + H - 14) + 'V' + (y0 + 14) + 'Z';
    s += '<path d="' + corte + '" fill="none" stroke="' + TINTA + '" stroke-width=".5"/>';
    s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + W + '" height="' + H + '" fill="none" stroke="#8a8a90" stroke-width=".3" stroke-dasharray="2 1.5"/>';
    s += '<rect x="' + (x0 + W - 26) + '" y="' + (y0 + 8) + '" width="18" height="22" fill="none" stroke="' + TINTA + '" stroke-width=".4" stroke-dasharray="1 .8"/>';
    s += reyes ? corona(x0 + W - 24, y0 + 15) : dibujo(0, x0 + W - 17, y0 + 19, 12);
    var lineas = reyes ? ['A Sus Majestades', 'los Reyes Magos de Oriente', 'Palacio Real', 'Oriente'] : ['Para Papá Noel', 'Casa de Papá Noel', 'Polo Norte'];
    lineas.forEach(function (l, i) { s += txt(x0 + 12, y0 + 64 + i * 9, l, { size: i < (reyes ? 2 : 1) ? 6 : 5, titular: i < (reyes ? 2 : 1), fill: i < (reyes ? 2 : 1) ? TINTA : GRIS }); });
    s += txt(x0 + 12, y0 + 128, 'De:', { size: 4.6 }) + '<path d="M' + (x0 + 22) + ' ' + (y0 + 128) + 'H' + (x0 + W - 12) + '" stroke="#8a8a90" stroke-width=".25"/>';
    s += dibujo(reyes ? 0 : 3, x0 + 18, y0 + 34, 12) + dibujo(2, x0 + 34, y0 + 34, 11);
    s += txt(105, 14, 'Recorta por la línea continua. Dobla hacia atrás por las líneas de puntos: primero los laterales,', { size: 3.3, anchor: 'middle', fill: GRIS });
    s += txt(105, 19, 'después la solapa de abajo (pégala a los laterales) y, con la carta dentro, cierra con la de arriba.', { size: 3.3, anchor: 'middle', fill: GRIS });
    s += txt(105, 287, 'La carta cabe doblada en cuatro.', { size: 3.3, anchor: 'middle', fill: GRIS });
    return { svg: hoja({ alt: reyes ? 'Sobre para la carta a los Reyes Magos' : 'Sobre para la carta a Papá Noel', sinPie: true }, s), sol: null };
  }

  // Respuesta de los Reyes Magos al niño
  function parte(texto, max) {
    var out = [], l = '';
    texto.split(' ').forEach(function (w) { if ((l + ' ' + w).trim().length > max) { out.push(l); l = w; } else l = (l + ' ' + w).trim(); });
    if (l) out.push(l);
    return out;
  }
  function cartaRespuesta(spec) {
    var s = '', y = 52, carbon = spec.variante === 'carbon';
    function linea(yy, x1) { return '<path d="M' + (x1 || 15) + ' ' + f(yy) + 'H195" stroke="#8a8a90" stroke-width=".25"/>'; }
    function parrafo(t) { parte(t, 62).forEach(function (l) { s += txt(15, y, l, { size: 5.6 }); y += 8.6; }); y += 5; }
    s += corona(148, 16) + corona(166, 13) + corona(184, 16);
    s += txt(15, 32, 'Querido/a', { size: 9, titular: true }) + linea(32, 66);
    parrafo('Hemos recibido tu carta y nos ha hecho mucha ilusión. La hemos leído despacio, con los camellos asomándose por encima de nuestros hombros para no perderse nada.');
    parrafo('Sabemos que este año te has esforzado mucho en:');
    y += 1; s += linea(y); y += 11; s += linea(y); y += 11; s += linea(y); y += 13;
    parrafo('Y también sabemos que todavía puedes mejorar en:');
    y += 1; s += linea(y); y += 11; s += linea(y); y += 13;
    if (carbon) parrafo('Por eso, junto a tus regalos, te dejamos un trocito de carbón dulce. No es un castigo: es un recordatorio de que el año que viene puedes hacerlo todavía mejor. Confiamos mucho en ti.');
    else parrafo('Estamos muy orgullosos de ti. Sigue así: ayudando en casa, cuidando de los demás y aprendiendo cosas nuevas cada día.');
    parrafo('Esta noche dejaremos los regalos con mucho cuidado para no despertar a nadie. Gracias por el agua para los camellos y por el turrón: la noche del 5 de enero es muy larga.');
    parrafo('Un abrazo muy grande desde Oriente,');
    y += 16;
    ['Melchor', 'Gaspar', 'Baltasar'].forEach(function (n, i) {
      var x = 15 + i * 62;
      s += '<path d="M' + x + ' ' + f(y) + 'h52" stroke="' + TINTA + '" stroke-width=".3"/>' + txt(x + 26, y + 6.5, n, { size: 5.4, anchor: 'middle', titular: true });
    });
    s += txt(15, 280, 'Oriente, 6 de enero', { size: 4, fill: GRIS });
    return { svg: hoja({ alt: 'Carta de los Reyes Magos a los niños' + (carbon ? ' con carbón dulce' : ''), sinPie: true }, s), sol: null };
  }

  // ---------- crucigrama (palabras cruzadas, sin casillas negras) ----------
  function crucigrama(spec, seed) {
    var r = rng(seed), N = spec.n || 12, maxC = spec.maxCols || 16, maxR = spec.maxFilas || 14;
    var mejor = null;
    for (var intento = 0; intento < 30; intento++) {
      var res = colocaCruzadas(spec.palabras, N, maxC, maxR, r);
      if (!mejor || res.puestas.length > mejor.puestas.length || (res.puestas.length === mejor.puestas.length && res.cruces > mejor.cruces)) mejor = res;
      if (mejor.puestas.length >= N && intento >= 5) break;
    }
    var pz = mejor.puestas, minR = Infinity, minC = Infinity, maxRR = -Infinity, maxCC = -Infinity;
    Object.keys(mejor.celdas).forEach(function (k) {
      var rc = k.split(',').map(Number);
      minR = Math.min(minR, rc[0]); maxRR = Math.max(maxRR, rc[0]); minC = Math.min(minC, rc[1]); maxCC = Math.max(maxCC, rc[1]);
    });
    var filas = maxRR - minR + 1, cols = maxCC - minC + 1;
    // numeración: por filas y columnas; horizontal y vertical que empiezan juntas comparten número
    var inicios = {};
    pz.forEach(function (p) { var k = (p.r - minR) + ',' + (p.c - minC); (inicios[k] = inicios[k] || []).push(p); });
    var claves = Object.keys(inicios).sort(function (a, b) { var x = a.split(',').map(Number), y = b.split(',').map(Number); return x[0] - y[0] || x[1] - y[1]; });
    claves.forEach(function (k, i) { inicios[k].forEach(function (p) { p.num = i + 1; }); });
    var hor = pz.filter(function (p) { return p.dir === 'h'; }).sort(function (a, b) { return a.num - b.num; });
    var ver = pz.filter(function (p) { return p.dir === 'v'; }).sort(function (a, b) { return a.num - b.num; });

    var altoMax = spec.altoRejilla || 140;
    var c = Math.min(180 / cols, altoMax / filas, 12), x0 = (210 - cols * c) / 2, y0 = 46;
    function dibuja(sol) {
      var o = '';
      Object.keys(mejor.celdas).forEach(function (k) {
        var rc = k.split(',').map(Number), x = x0 + (rc[1] - minC) * c, y = y0 + (rc[0] - minR) * c;
        o += '<rect x="' + f(x) + '" y="' + f(y) + '" width="' + f(c) + '" height="' + f(c) + '" fill="#fff" stroke="' + TINTA + '" stroke-width=".35"/>';
        if (sol) o += txt(x + c / 2, y + c * .72, mejor.celdas[k], { size: f(c * .55), anchor: 'middle', bold: true, fill: ROJO });
      });
      claves.forEach(function (k, i) {
        var rc = k.split(',').map(Number);
        o += txt(x0 + rc[1] * c + c * .08, y0 + rc[0] * c + c * .3, i + 1, { size: f(Math.max(2.2, c * .26)), fill: TINTA });
      });
      var yy = y0 + filas * c + 10, tam = spec.tamPista || 3.5, paso = tam * 1.45;
      [[spec.ingles ? 'Across' : 'Horizontales', hor, 15], [spec.ingles ? 'Down' : 'Verticales', ver, 110]].forEach(function (col) {
        var y = yy;
        o += txt(col[2], y, col[0], { size: 4.4, titular: true });
        y += paso + 1.6;
        col[1].forEach(function (p) {
          var lineas = parte(p.num + '. ' + p.pista + ' (' + p.w.length + ')', 50);
          lineas.forEach(function (l, j) { o += txt(col[2] + (j ? 4 : 0), y, l, { size: tam }); y += paso; });
          y += .8;
        });
      });
      return o;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || 'Escribe cada palabra en su sitio, una letra por casilla. Entre paréntesis, el número de letras.', nombre: true, ingles: !!spec.ingles, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }
  function colocaCruzadas(banco, N, maxC, maxR, r) {
    var lista = shuffle(r, banco).map(function (x) { return { w: normaliza(x[0]), pista: x[1] }; })
      .filter(function (x) { return x.w.length >= 3 && x.w.length <= Math.min(maxC, maxR); });
    var celdas = {}, dirs = {}, puestas = [], cruces = 0, b = { r0: 0, r1: 0, c0: 0, c1: 0 };
    function cabe(w, r0, c0, dir) {
      var dr = dir === 'v' ? 1 : 0, dc = dir === 'h' ? 1 : 0, n = 0;
      var r1 = r0 + dr * (w.length - 1), c1 = c0 + dc * (w.length - 1);
      if (puestas.length && (Math.max(b.r1, r1) - Math.min(b.r0, r0) + 1 > maxR || Math.max(b.c1, c1) - Math.min(b.c0, c0) + 1 > maxC)) return -1;
      if (celdas[(r0 - dr) + ',' + (c0 - dc)] || celdas[(r1 + dr) + ',' + (c1 + dc)]) return -1;
      for (var i = 0; i < w.length; i++) {
        var rr = r0 + dr * i, cc = c0 + dc * i, k = rr + ',' + cc, ya = celdas[k];
        if (ya) {
          if (ya !== w[i] || (dirs[k] || '').indexOf(dir) >= 0) return -1;
          n++;
        } else if (celdas[(rr + dc) + ',' + (cc + dr)] || celdas[(rr - dc) + ',' + (cc - dr)]) return -1;
      }
      return n;
    }
    function pon(x, r0, c0, dir, n) {
      var dr = dir === 'v' ? 1 : 0, dc = dir === 'h' ? 1 : 0;
      for (var i = 0; i < x.w.length; i++) { var k = (r0 + dr * i) + ',' + (c0 + dc * i); celdas[k] = x.w[i]; dirs[k] = (dirs[k] || '') + dir; }
      b.r0 = Math.min(b.r0, r0); b.c0 = Math.min(b.c0, c0); b.r1 = Math.max(b.r1, r0 + dr * (x.w.length - 1)); b.c1 = Math.max(b.c1, c0 + dc * (x.w.length - 1));
      puestas.push({ w: x.w, pista: x.pista, r: r0, c: c0, dir: dir }); cruces += n;
    }
    // empieza por una palabra larga en horizontal
    lista.sort(function (a, b2) { return b2.w.length - a.w.length; });
    var primera = lista.splice(ri(r, 0, Math.min(3, lista.length - 1)), 1)[0];
    pon(primera, 0, 0, 'h', 0);
    lista = shuffle(r, lista);
    for (var pase = 0; pase < 2 && puestas.length < N; pase++) {
      lista = lista.filter(function (x) {
        if (puestas.length >= N) return true;
        var cand = [];
        Object.keys(celdas).forEach(function (k) {
          var rc = k.split(',').map(Number);
          for (var i = 0; i < x.w.length; i++) if (x.w[i] === celdas[k]) {
            ['h', 'v'].forEach(function (dir) {
              var r0 = dir === 'v' ? rc[0] - i : rc[0], c0 = dir === 'h' ? rc[1] - i : rc[1], n = cabe(x.w, r0, c0, dir);
              if (n > 0) cand.push({ r0: r0, c0: c0, dir: dir, n: n, z: r() });
            });
          }
        });
        if (!cand.length) return true;
        cand.sort(function (a, b2) { return b2.n - a.n || a.z - b2.z; });
        pon(x, cand[0].r0, cand[0].c0, cand[0].dir, cand[0].n);
        return false;
      });
    }
    return { celdas: celdas, puestas: puestas, cruces: cruces };
  }

  // ---------- caligrafía ----------
  var GRIS_REPASO = '#b4b4ba';
  function letraLigada(x, y, texto, fs, color, ancho) {
    return '<text x="' + f(x) + '" y="' + f(y) + '" font-family="\'Playwrite ES\',cursive" font-weight="300" font-size="' + f(fs) + '" fill="' + color + '"' +
      (ancho ? ' textLength="' + f(ancho) + '" lengthAdjust="spacing"' : '') + '>' + esc(texto) + '</text>';
  }
  function pautaLigada(y, h) {
    return '<path d="M15 ' + f(y - h * 1.96) + 'H195M15 ' + f(y + h) + 'H195" stroke="#c9c9d2" stroke-width=".2" stroke-dasharray="1 1"/>' +
      '<path d="M15 ' + f(y - h) + 'H195M15 ' + f(y) + 'H195" stroke="#7f93b8" stroke-width=".28"/>';
  }
  function caligrafiaLetras(spec) {
    var h = 5, fs = h / .52, y = 61, paso = 19, s = '';
    spec.letras.forEach(function (l) {
      [l, l.toUpperCase()].forEach(function (forma) {
        s += pautaLigada(y, h) + letraLigada(17, y, forma, fs, TINTA);
        s += letraLigada(36, y, Array(forma === l ? 9 : 7).fill(forma).join(' '), fs, GRIS_REPASO, 155);
        y += paso;
        s += pautaLigada(y, h);
        y += paso;
      });
    });
    var nombre = spec.letras.join(', ').replace(/, ([^,]*)$/, ' y $1');
    return { svg: hoja({ titulo: spec.titulo || 'Caligrafía: ' + nombre, sub: 'Repasa las letras grises sin salirte y luego escríbelas tú en el renglón de abajo.', nombre: true }, s), sol: null };
  }
  function caligrafiaFrases(spec, seed) {
    var r = rng(seed), h = 4.5, fs = h / .52, y = 60, paso = 17.5, s = '';
    shuffle(r, spec.frases).slice(0, 4).forEach(function (fr) {
      s += pautaLigada(y, h) + letraLigada(17, y, fr, fs, GRIS_REPASO);
      y += paso;
      for (var i = 0; i < 2; i++) { s += pautaLigada(y, h); y += paso; }
    });
    return { svg: hoja({ titulo: spec.titulo || 'Caligrafía: frases para copiar', sub: 'Repasa la frase gris y cópiala dos veces en los renglones de debajo.', nombre: true, seed: seed }, s), sol: null };
  }
  function trazosImprenta(spec) {
    var H = spec.alto || 14, fs = H / .72, y = 56 + H, paso = spec.paso || 30, s = '';
    spec.letras.forEach(function (l) {
      s += '<path d="M15 ' + f(y - H) + 'H195M15 ' + f(y) + 'H195" stroke="#7f93b8" stroke-width=".3"/>' +
        '<path d="M15 ' + f(y - H / 2) + 'H195" stroke="#c9c9d2" stroke-width=".25" stroke-dasharray="1.2 1.2"/>';
      s += '<text x="17" y="' + f(y) + '" font-size="' + f(fs) + '" fill="' + TINTA + '">' + esc(l) + '</text>';
      s += '<text x="' + f(17 + fs * .95) + '" y="' + f(y) + '" font-size="' + f(fs) + '" fill="' + GRIS_REPASO + '" textLength="' + f(176 - fs * .95) + '" lengthAdjust="spacing">' +
        esc(Array(spec.repeticiones || 6).fill(l).join(' ')) + '</text>';
      y += paso;
    });
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub || 'Empieza por la letra negra y repasa las grises siguiendo la forma.', nombre: true }, s), sol: null };
  }

  // ---------- multiplicaciones y divisiones ----------
  function cifras(x, y, n, color, tam) {
    tam = tam || 9.5;
    return String(n).split('').reverse().map(function (ch, i) {
      return txt(x - i * tam * .68, y, ch, { size: tam, anchor: 'middle', bold: true, fill: color });
    }).join('');
  }
  function aleatorioCifras(r, d) { return ri(r, Math.pow(10, d - 1), Math.pow(10, d) - 1); }
  function multiplicaciones(spec, seed) {
    var r = rng(seed), da = spec.a || 2, db = spec.b || 1, ops = [], vistos = {}, n = db === 1 ? 20 : 12;
    while (ops.length < n) {
      var a = aleatorioCifras(r, da), b = db === 1 ? ri(r, 2, 9) : aleatorioCifras(r, db);
      if (a % 10 === 0 || (db > 1 && (b % 10 < 2 || Math.floor(b / 10) % 10 < 2)) || vistos[a + 'x' + b]) continue;
      vistos[a + 'x' + b] = 1; ops.push({ a: a, b: b });
    }
    var cols = 4, w = 45, alto = db === 1 ? 46 : 74, t = 9.5, paso = t * .68;
    function dibuja(sol) {
      var o = '';
      ops.forEach(function (op, i) {
        var xr = 15 + (i % cols) * w + 36, y = 60 + Math.floor(i / cols) * alto;
        var ancho = (Math.max(String(op.a).length, String(op.b).length + 1, String(op.a * op.b).length) + .6) * paso;
        o += cifras(xr, y, op.a) + cifras(xr, y + 11, op.b);
        o += txt(xr - (String(op.b).length + .3) * paso, y + 11, '×', { size: t, anchor: 'middle' });
        o += '<path d="M' + f(xr - ancho) + ' ' + (y + 14.5) + 'H' + (xr + 4) + '" stroke="' + TINTA + '" stroke-width=".5"/>';
        if (db > 1) {
          o += '<path d="M' + f(xr - ancho) + ' ' + (y + 39.5) + 'H' + (xr + 4) + '" stroke="' + TINTA + '" stroke-width=".35"/>';
          if (sol) {
            var u = op.b % 10, dd = Math.floor(op.b / 10);
            o += cifras(xr, y + 25, op.a * u, ROJO) + cifras(xr - paso, y + 36, op.a * dd, ROJO) + cifras(xr, y + 50, op.a * op.b, ROJO);
          }
        } else if (sol) o += cifras(xr, y + 25, op.a * op.b, ROJO);
      });
      return o;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || (db > 1 ? 'Multiplica por las unidades, luego por las decenas (un lugar a la izquierda) y suma.' : 'Resuelve las multiplicaciones. Empieza por las unidades y no olvides lo que te llevas.'), nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }
  function divisiones(spec, seed) {
    var r = rng(seed), dd = spec.dividendo || 3, ops = [], vistos = {};
    while (ops.length < 12) {
      var d = ri(r, 2, 9), D = aleatorioCifras(r, dd);
      if (D < d * 10 || vistos[D + ':' + d]) continue;
      if (spec.exactas && D % d) continue;
      vistos[D + ':' + d] = 1; ops.push({ D: D, d: d, c: Math.floor(D / d), r: D % d });
    }
    var t = 9.5, paso = t * .68;
    function dibuja(sol) {
      var o = '';
      ops.forEach(function (op, i) {
        var x0 = 18 + (i % 3) * 61, y = 62 + Math.floor(i / 3) * 54, nD = String(op.D).length;
        var xl = x0 + nD * paso + 2;
        String(op.D).split('').forEach(function (ch, k) { o += txt(x0 + k * paso + paso / 2, y, ch, { size: t, anchor: 'middle', bold: true }); });
        o += '<path d="M' + f(xl) + ' ' + (y - 9) + 'V' + (y + 4) + 'H' + f(xl + 24) + '" fill="none" stroke="' + TINTA + '" stroke-width=".5"/>';
        o += txt(xl + 3, y, op.d, { size: t, bold: true });
        if (sol) {
          o += txt(xl + 3, y + 11, op.c, { size: t, bold: true, fill: ROJO });
          o += txt(x0 + nD * paso, y + 30, op.r, { size: t, anchor: 'end', bold: true, fill: ROJO });
          o += txt(x0, y + 30, 'resto', { size: 3, fill: ROJO });
        }
      });
      return o;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || 'Divide y escribe el cociente debajo del divisor y el resto al final, debajo del dividendo.', nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- mandalas ----------
  var NIVEL_MANDALA = {
    facil: { sim: [8], anillos: [3, 4], trazo: .8, detalle: 0 },
    medio: { sim: [10, 12], anillos: [5, 6], trazo: .55, detalle: .5 },
    dificil: { sim: [12, 16, 18], anillos: [8, 9], trazo: .4, detalle: .85 }
  };
  function mandala(spec, seed) {
    var r = rng(seed), cfg = NIVEL_MANDALA[spec.nivel || 'medio'], cx = 105, cy = 160, R = 90;
    var sim = cfg.sim[ri(r, 0, cfg.sim.length - 1)], nAn = ri(r, cfg.anillos[0], cfg.anillos[1]);
    function P(rad, a) { return f(cx + rad * Math.cos(a - Math.PI / 2)) + ' ' + f(cy + rad * Math.sin(a - Math.PI / 2)); }
    var d = '', i, k;
    // radios de los anillos con anchos algo irregulares
    var r0 = R * (spec.nivel === 'facil' ? .2 : .14), pesos = [], tot = 0;
    for (i = 0; i < nAn; i++) { var w = .7 + r() * .8; pesos.push(w); tot += w; }
    var radios = [r0];
    pesos.forEach(function (w) { radios.push(radios[radios.length - 1] + (R - r0) * w / tot); });
    // centro: flor sencilla
    var nc = sim, rc = r0;
    d += 'M' + P(rc * .32, 0) + 'A' + f(rc * .32) + ' ' + f(rc * .32) + ' 0 1 1 ' + P(rc * .32, Math.PI - .0001) + 'A' + f(rc * .32) + ' ' + f(rc * .32) + ' 0 1 1 ' + P(rc * .32, 0);
    for (k = 0; k < nc; k++) d += petalo(rc * .32, rc, k * 2 * Math.PI / nc, Math.PI / nc * .85);
    var motivos = ['petalos', 'arcos', 'hojas', 'circulos', 'zigzag', 'gotas', 'petalos', 'arcos'];
    var anterior = '';
    for (i = 0; i < nAn; i++) {
      var a1 = radios[i], a2 = radios[i + 1], m;
      do { m = motivos[ri(r, 0, motivos.length - 1)]; } while (m === anterior);
      anterior = m;
      var det = !!cfg.detalle && r() < cfg.detalle;
      var mult = (cfg.detalle > r() && i > 1) ? 2 : 1, n = sim * mult, paso = 2 * Math.PI / n, desf = (i % 2) * paso / 2;
      if (m === 'petalos' || m === 'gotas') {
        for (k = 0; k < n; k++) {
          var ang = k * paso + desf;
          d += m === 'petalos' ? petalo(a1, a2, ang, paso / 2 * .92) : gota(a1, a2, ang, paso / 2 * .9);
          if (det && m === 'petalos') d += petalo(a1, a1 + (a2 - a1) * .62, ang, paso / 2 * .5);
        }
      } else if (m === 'arcos') {
        for (k = 0; k < n; k++) {
          var b = k * paso + desf, rcp = 2 * a2 - a1 * Math.cos(paso / 2);
          d += 'M' + P(a1, b) + 'Q' + P(rcp, b + paso / 2) + ' ' + P(a1, b + paso);
          if (det) d += 'M' + P(a1, b + paso * .2) + 'Q' + P((rcp + a1) / 2, b + paso / 2) + ' ' + P(a1, b + paso * .8);
        }
      } else if (m === 'hojas') {
        for (k = 0; k < n; k++) {
          var c = k * paso + desf, rm = (a1 + a2) / 2;
          d += 'M' + P(a1, c) + 'Q' + P(rm, c - paso * .55) + ' ' + P(a2, c) + 'Q' + P(rm, c + paso * .55) + ' ' + P(a1, c);
          if (det) d += 'M' + P(a1 + (a2 - a1) * .15, c) + 'L' + P(a2 - (a2 - a1) * .15, c);
        }
      } else if (m === 'circulos') {
        var rm2 = (a1 + a2) / 2, rr = Math.min((a2 - a1) / 2 * .85, rm2 * Math.sin(paso / 2) * .85);
        for (k = 0; k < n; k++) {
          var cc = P(rm2, k * paso + desf).split(' ').map(Number);
          d += circulo(cc[0], cc[1], rr);
          if (det) d += circulo(cc[0], cc[1], rr * .45);
        }
      } else if (m === 'zigzag') {
        d += 'M' + P(a1, desf);
        for (k = 0; k < n; k++) d += 'L' + P(a2, k * paso + desf + paso / 2) + 'L' + P(a1, (k + 1) * paso + desf);
        if (det) {
          d += 'M' + P((a1 + a2) / 2, desf);
          for (k = 0; k < n; k++) d += 'L' + P(a2, k * paso + desf + paso / 2 - paso * .12) + 'M' + P(a2, k * paso + desf + paso / 2 + paso * .12) + 'L' + P((a1 + a2) / 2, (k + 1) * paso + desf);
        }
      }
      if (i < nAn - 1 && (m === 'zigzag' || m === 'circulos' || r() < .5)) d += circulo(cx, cy, a2);
    }
    d += circulo(cx, cy, R);
    function petalo(r1, r2, a, w) {
      var h = r2 - r1;
      return 'M' + P(r1, a - w) + 'C' + P(r1 + h * .55, a - w * 1.25) + ' ' + P(r2 - h * .12, a - w * .45) + ' ' + P(r2, a) +
        'C' + P(r2 - h * .12, a + w * .45) + ' ' + P(r1 + h * .55, a + w * 1.25) + ' ' + P(r1, a + w);
    }
    function gota(r1, r2, a, w) {
      var h = r2 - r1;
      return 'M' + P(r1, a) + 'C' + P(r1 + h * .45, a - w * .9) + ' ' + P(r2, a - w * 1.05) + ' ' + P(r2, a) +
        'C' + P(r2, a + w * 1.05) + ' ' + P(r1 + h * .45, a + w * .9) + ' ' + P(r1, a);
    }
    function circulo(x, y, rr) {
      return 'M' + f(x - rr) + ' ' + f(y) + 'a' + f(rr) + ' ' + f(rr) + ' 0 1 0 ' + f(2 * rr) + ' 0a' + f(rr) + ' ' + f(rr) + ' 0 1 0 ' + f(-2 * rr) + ' 0';
    }
    var cuerpo = '<path d="' + d + '" fill="none" stroke="' + TINTA + '" stroke-width="' + cfg.trazo + '" stroke-linejoin="round"/>';
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub || 'Colorea el mandala como quieras. Un truco: usa el mismo color en todas las piezas de cada anillo.', seed: seed }, cuerpo), sol: null };
  }

  // ---------- grafomotricidad y horario ----------
  function trazo(tipo, x0, x1, y, h) {
    var d = '', x, n, w, i;
    if (tipo === 'horizontal') { for (i = 0; i < 3; i++) d += 'M' + x0 + ' ' + f(y - h + i * h / 2) + 'H' + x1; }
    else if (tipo === 'vertical') { for (x = x0; x <= x1; x += 9) d += 'M' + f(x) + ' ' + f(y - h) + 'V' + f(y); }
    else if (tipo === 'diagonal') { for (x = x0; x + h * .6 <= x1; x += 9) d += 'M' + f(x) + ' ' + f(y - h) + 'L' + f(x + h * .6) + ' ' + f(y); }
    else if (tipo === 'zigzag') { w = h * .7; d = 'M' + x0 + ' ' + y; for (x = x0; x + w <= x1; x += w) d += 'L' + f(x + w / 2) + ' ' + f(y - h) + 'L' + f(x + w) + ' ' + y; }
    else if (tipo === 'castillo') { w = h * .8; d = 'M' + x0 + ' ' + y; for (x = x0; x + 2 * w <= x1; x += 2 * w) d += 'V' + f(y - h) + 'H' + f(x + w) + 'V' + y + 'H' + f(x + 2 * w); }
    else if (tipo === 'ondas') { w = h * 1.6; d = 'M' + x0 + ' ' + f(y - h / 2); for (x = x0; x + w <= x1; x += w) d += 'q' + f(w / 4) + ' ' + f(-h) + ' ' + f(w / 2) + ' 0q' + f(w / 4) + ' ' + f(h) + ' ' + f(w / 2) + ' 0'; }
    else if (tipo === 'puentes') { w = h * .9; d = 'M' + x0 + ' ' + y; for (x = x0; x + w <= x1; x += w) d += 'c0 ' + f(-h * 1.33) + ' ' + f(w) + ' ' + f(-h * 1.33) + ' ' + f(w) + ' 0'; }
    else if (tipo === 'copas') { w = h * .9; d = 'M' + x0 + ' ' + f(y - h); for (x = x0; x + w <= x1; x += w) d += 'c0 ' + f(h * 1.33) + ' ' + f(w) + ' ' + f(h * 1.33) + ' ' + f(w) + ' 0'; }
    else if (tipo === 'bucles') { w = h * .75; d = 'M' + x0 + ' ' + y; for (x = x0; x + w * 1.2 <= x1; x += w) d += 'c' + f(w * .9) + ' ' + f(-h * .3) + ' ' + f(w * .7) + ' ' + f(-h * 1.15) + ' ' + f(w * .3) + ' ' + f(-h) + 'c' + f(-w * .45) + ' ' + f(h * .15) + ' ' + f(-w * .1) + ' ' + f(h * .9) + ' ' + f(w * .7) + ' ' + f(h); }
    else if (tipo === 'espirales') { n = Math.floor((x1 - x0) / (h * 1.3)); for (i = 0; i < n; i++) { var cx = x0 + h * .65 + i * h * 1.3, cy = y - h / 2; d += 'M' + f(cx) + ' ' + f(cy); for (var t = 0; t <= 3 * 2 * Math.PI; t += .3) { var rr = h * .5 * t / (6 * Math.PI); d += 'L' + f(cx + rr * Math.cos(t)) + ' ' + f(cy + rr * Math.sin(t)); } } }
    return d;
  }
  function grafomotricidad(spec) {
    var y = 80, paso = spec.paso || 36, h = spec.alto || 16, s = '';
    spec.trazos.forEach(function (tp) {
      var d = trazo(tp, 22, 192, y, h);
      s += '<path d="' + d + '" fill="none" stroke="#9a9aa2" stroke-width=".7" stroke-dasharray="1.8 1.4" stroke-linecap="round" stroke-linejoin="round"/>';
      (d.match(/M[\d.]+ [\d.]+/g) || []).forEach(function (m) {
        var c = m.slice(1).split(' ');
        s += '<circle cx="' + c[0] + '" cy="' + c[1] + '" r="1.3" fill="' + TINTA + '"/>';
      });
      y += paso;
    });
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub || 'Empieza en el punto negro de cada trazo y repasa la línea de puntos sin levantar el lápiz.', nombre: true }, s), sol: null };
  }
  function horario(spec) {
    var dias = spec.dias || ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'], filas = spec.filas || 7;
    var x0 = 15, y0 = 50, ancho = 180, colH = 26, colD = (ancho - colH) / dias.length, alto = spec.altoFila || 25, cab = 11, s = '';
    s += txt(15, 42, 'Nombre:', { size: 3.7 }) + '<path d="M31 42.5H118" stroke="' + TINTA + '" stroke-width=".2"/>' + txt(125, 42, 'Curso:', { size: 3.7 }) + '<path d="M138 42.5H195" stroke="' + TINTA + '" stroke-width=".2"/>';
    s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + ancho + '" height="' + cab + '" fill="' + TINTA + '"/>';
    s += txt(x0 + colH / 2, y0 + 7.4, 'Hora', { size: 4, anchor: 'middle', fill: '#fff', bold: true });
    dias.forEach(function (dd, i) { s += txt(x0 + colH + (i + .5) * colD, y0 + 7.4, dd, { size: 4.2, anchor: 'middle', fill: '#fff', bold: true }); });
    var y = y0 + cab;
    for (var i = 0; i < filas; i++) {
      var recreo = spec.recreo && i === spec.recreo, hh = recreo ? 10 : alto;
      if (recreo) {
        s += '<rect x="' + x0 + '" y="' + f(y) + '" width="' + ancho + '" height="' + hh + '" fill="#e4e1d8" stroke="' + TINTA + '" stroke-width=".3"/>';
        s += txt(105, y + 6.6, 'R E C R E O', { size: 4, anchor: 'middle', bold: true, fill: GRIS });
      } else {
        s += '<rect x="' + x0 + '" y="' + f(y) + '" width="' + colH + '" height="' + hh + '" fill="#f3f1ea" stroke="' + TINTA + '" stroke-width=".3"/>';
        s += '<path d="M' + (x0 + 4) + ' ' + f(y + hh / 2) + 'h' + (colH - 8) + '" stroke="#b4b4ba" stroke-width=".2" stroke-dasharray="1 1"/>';
        dias.forEach(function (dd, j) { s += '<rect x="' + f(x0 + colH + j * colD) + '" y="' + f(y) + '" width="' + f(colD) + '" height="' + hh + '" fill="#fff" stroke="' + TINTA + '" stroke-width=".3"/>'; });
      }
      y += hh;
    }
    s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + ancho + '" height="' + f(y - y0) + '" fill="none" stroke="' + TINTA + '" stroke-width=".8"/>';
    return { svg: hoja({ titulo: spec.titulo || 'Horario escolar' }, s), sol: null };
  }

  // ---------- calendarios ----------
  var MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  var INICIALES = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
  function diasMes(a, m) { return new Date(Date.UTC(a, m + 1, 0)).getUTCDate(); }
  function primerDia(a, m) { return (new Date(Date.UTC(a, m, 1)).getUTCDay() + 6) % 7; } // 0 = lunes
  function claveDia(m, d) { return (m < 9 ? '0' : '') + (m + 1) + '-' + (d < 10 ? '0' : '') + d; }
  function calendarioAnual(spec) {
    var a = spec.anio, fest = {}, s = '';
    (spec.festivos || []).forEach(function (x) { fest[x[0]] = x[1]; });
    s += txt(15, 30, String(a), { size: 16, titular: true });
    var w = 58, h = 54, x0 = 15, y0 = 44, cw = w / 7;
    for (var m = 0; m < 12; m++) {
      var mx = x0 + (m % 3) * (w + 3), my = y0 + Math.floor(m / 3) * h;
      s += txt(mx + 1, my, MESES[m], { size: 4.6, titular: true });
      INICIALES.forEach(function (l, j) { s += txt(mx + (j + .5) * cw, my + 6.5, l, { size: 2.8, anchor: 'middle', bold: true, fill: j === 6 ? ROJO : GRIS }); });
      var p0 = primerDia(a, m), nd = diasMes(a, m);
      for (var d = 1; d <= nd; d++) {
        var pos = p0 + d - 1, col = pos % 7, fila = Math.floor(pos / 7), k = claveDia(m, d), rojo = col === 6 || fest[k];
        var cx = mx + (col + .5) * cw, cy = my + 13 + fila * 6.4;
        if (fest[k]) s += '<circle cx="' + f(cx) + '" cy="' + f(cy - 1.05) + '" r="2.55" fill="none" stroke="' + ROJO + '" stroke-width=".35"/>';
        s += txt(cx, cy, d, { size: 3.3, anchor: 'middle', bold: !!rojo, fill: rojo ? ROJO : TINTA });
      }
    }
    if (spec.festivos && spec.festivos.length) {
      var yy = y0 + 4 * h - 1;
      s += txt(15, yy, 'Festivos nacionales ' + a + ' (en rojo, con círculo)', { size: 3.3, bold: true });
      var lista = spec.festivos.map(function (x) { var mm = Number(x[0].slice(0, 2)) - 1, dd = Number(x[0].slice(3)); return dd + ' ' + MESES[mm].toLowerCase() + ': ' + x[1]; });
      var mitad = Math.ceil(lista.length / 2);
      lista.forEach(function (l, i) { s += txt(i < mitad ? 15 : 108, yy + 5 + (i % mitad) * 4.3, l, { size: 3 }); });
    }
    return { svg: hoja({ alt: 'Calendario ' + a, sinPie: false }, s), sol: null };
  }
  function calendarioMes(spec) {
    var a = spec.anio, m = spec.mes, fest = {}, s = '';
    (spec.festivos || []).forEach(function (x) { fest[x[0]] = x[1]; });
    s += txt(15, 30, MESES[m], { size: 13, titular: true }) + txt(195, 30, String(a), { size: 13, titular: true, anchor: 'end', fill: GRIS });
    var x0 = 15, y0 = 40, cw = 180 / 7, p0 = primerDia(a, m), nd = diasMes(a, m), filas = Math.ceil((p0 + nd) / 7), ch = 236 / filas;
    INICIALES.forEach(function (l, j) {
      var nombre = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][j];
      s += '<rect x="' + f(x0 + j * cw) + '" y="' + y0 + '" width="' + f(cw) + '" height="8" fill="' + (j === 6 ? ROJO : TINTA) + '"/>';
      s += txt(x0 + (j + .5) * cw, y0 + 5.6, nombre, { size: 3.4, anchor: 'middle', bold: true, fill: '#fff' });
    });
    for (var i = 0; i < filas * 7; i++) {
      var col = i % 7, fila = Math.floor(i / 7), d = i - p0 + 1, x = x0 + col * cw, y = y0 + 8 + fila * ch;
      var vale = d >= 1 && d <= nd, k = vale ? claveDia(m, d) : '', rojo = vale && (col === 6 || fest[k]);
      s += '<rect x="' + f(x) + '" y="' + f(y) + '" width="' + f(cw) + '" height="' + f(ch) + '" fill="' + (vale ? '#fff' : '#f3f1ea') + '" stroke="' + TINTA + '" stroke-width=".3"/>';
      if (vale) {
        s += txt(x + 2.2, y + 6.2, d, { size: 5.2, bold: true, fill: rojo ? ROJO : TINTA });
        if (fest[k]) parte(fest[k], 16).slice(0, 2).forEach(function (l, j) { s += txt(x + 2.2, y + ch - 5.2 + j * 3.2 - (parte(fest[k], 16).length > 1 ? 3.2 : 0), l, { size: 2.5, fill: ROJO }); });
      }
    }
    s += '<rect x="' + x0 + '" y="' + y0 + '" width="180" height="' + f(8 + filas * ch) + '" fill="none" stroke="' + TINTA + '" stroke-width=".7"/>';
    return { svg: hoja({ alt: 'Calendario de ' + MESES[m].toLowerCase() + ' de ' + a }, s), sol: null };
  }

  var TIPOS = {
    sopa: sopa, sudoku: sudoku, laberinto: laberinto, bingo90: bingo90, bingo75: bingo75, 'bingo-numeros': bingoNumeros,
    tabla: tabla, 'tablas-todas': tablasTodas, pitagorica: pitagorica, 'mult-practica': multPractica,
    operaciones: operaciones, papel: papel,
    'sudoku-dibujos': sudokuDibujos, 'bingo-palabras': bingoPalabras, 'bingo-palabras-lista': bingoPalabrasLista,
    'laberinto-arbol': laberintoArbol, carta: carta, sobre: sobre, 'carta-respuesta': cartaRespuesta, crucigrama: crucigrama,
    'caligrafia-letras': caligrafiaLetras, 'caligrafia-frases': caligrafiaFrases, 'trazos-imprenta': trazosImprenta,
    multiplicaciones: multiplicaciones, divisiones: divisiones, mandala: mandala,
    grafomotricidad: grafomotricidad, horario: horario, 'calendario-anual': calendarioAnual, 'calendario-mes': calendarioMes
  };
  // Tipos cuyo contenido cambia con la semilla (tienen botón «Otra distinta»)
  var ALEATORIOS = { sopa: 1, sudoku: 1, laberinto: 1, bingo90: 1, bingo75: 1, 'mult-practica': 1, operaciones: 1,
    'sudoku-dibujos': 1, 'bingo-palabras': 1, 'laberinto-arbol': 1, crucigrama: 1, 'caligrafia-frases': 1, multiplicaciones: 1, divisiones: 1, mandala: 1 };

  function render(spec, seed) {
    var fn = TIPOS[spec.tipo];
    if (!fn) throw new Error('Tipo de ficha desconocido: ' + spec.tipo);
    return fn(spec, seed >>> 0);
  }

  return { render: render, hash: hash, esAleatorio: function (spec) { return !!ALEATORIOS[spec.tipo]; } };
});
