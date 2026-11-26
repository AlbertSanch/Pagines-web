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
    var r = rng(seed), dd = spec.dividendo || 3, dos = spec.divisor === 2, ops = [], vistos = {};
    var total = dos ? 8 : 12;
    while (ops.length < total) {
      var d = dos ? ri(r, 12, 98) : ri(r, 2, 9), D = aleatorioCifras(r, dd);
      if (dos && d % 10 === 0) continue;
      if (D < d * (dos && dd === 3 ? 2 : 10) || vistos[D + ':' + d]) continue;
      if (spec.exactas && D % d) continue;
      vistos[D + ':' + d] = 1; ops.push({ D: D, d: d, c: Math.floor(D / d), r: D % d });
    }
    var t = 9.5, paso = t * .68;
    function dibuja(sol) {
      var o = '';
      ops.forEach(function (op, i) {
        var cols = dos ? 2 : 3, x0 = 18 + (i % cols) * (dos ? 95 : 61), y = 62 + Math.floor(i / cols) * 54, nD = String(op.D).length;
        var xl = x0 + nD * paso + 2;
        String(op.D).split('').forEach(function (ch, k) { o += txt(x0 + k * paso + paso / 2, y, ch, { size: t, anchor: 'middle', bold: true }); });
        o += '<path d="M' + f(xl) + ' ' + (y - 9) + 'V' + (y + 4) + 'H' + f(xl + (dos ? 28 : 24)) + '" fill="none" stroke="' + TINTA + '" stroke-width=".5"/>';
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
    if (spec.navidad) d += copo(rc * .95, 0);
    else for (k = 0; k < nc; k++) d += petalo(rc * .32, rc, k * 2 * Math.PI / nc, Math.PI / nc * .85);
    var motivos = spec.navidad ? ['iconos', 'copos', 'arcos', 'iconos', 'circulos', 'zigzag', 'petalos', 'copos'] : ['petalos', 'arcos', 'hojas', 'circulos', 'zigzag', 'gotas', 'petalos', 'arcos'];
    var extra = '';
    var anterior = '';
    for (i = 0; i < nAn; i++) {
      var a1 = radios[i], a2 = radios[i + 1], m;
      do { m = motivos[ri(r, 0, motivos.length - 1)]; } while (m === anterior);
      anterior = m;
      var det = !!cfg.detalle && r() < cfg.detalle;
      var mult = (cfg.detalle > r() && i > 1) ? 2 : 1, n = sim * mult, paso = 2 * Math.PI / n, desf = (i % 2) * paso / 2;
      if (m === 'iconos') {
        var nIc = Math.max(6, Math.min(sim, Math.floor(2 * Math.PI * (a1 + a2) / 2 / ((a2 - a1) * 1.05)))), pasoIc = 2 * Math.PI / nIc, tam = Math.min((a2 - a1) * .92, (a1 + a2) / 2 * pasoIc * .8);
        var cual = ri(r, 0, 5), otro = (cual + 1 + ri(r, 0, 4)) % 6;
        for (k = 0; k < nIc; k++) {
          var ai = k * pasoIc, xy = P((a1 + a2) / 2, ai).split(' ').map(Number);
          extra += '<g transform="rotate(' + f(ai * 180 / Math.PI) + ' ' + f(xy[0]) + ' ' + f(xy[1]) + ')">' + dibujo(k % 2 && nIc % 2 === 0 ? otro : cual, xy[0], xy[1], tam, TINTA, cfg.trazo) + '</g>';
        }
      } else if (m === 'copos') {
        var nCo = n, rmc = (a1 + a2) / 2, rco = Math.min((a2 - a1) / 2 * .9, rmc * Math.sin(paso / 2) * .9);
        for (k = 0; k < nCo; k++) { var cxy = P(rmc, k * paso + desf).split(' ').map(Number); d += copoEn(cxy[0], cxy[1], rco); }
      } else if (m === 'petalos' || m === 'gotas') {
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
    function copoEn(x, y, rr) {
      var o = '';
      for (var b = 0; b < 6; b++) {
        var an = b * Math.PI / 3, ex = x + rr * Math.cos(an), ey = y + rr * Math.sin(an);
        o += 'M' + f(x) + ' ' + f(y) + 'L' + f(ex) + ' ' + f(ey);
        var mx = x + rr * .6 * Math.cos(an), my = y + rr * .6 * Math.sin(an), lb = rr * .3;
        o += 'M' + f(mx + lb * Math.cos(an + .7)) + ' ' + f(my + lb * Math.sin(an + .7)) + 'L' + f(mx) + ' ' + f(my) + 'L' + f(mx + lb * Math.cos(an - .7)) + ' ' + f(my + lb * Math.sin(an - .7));
      }
      return o;
    }
    function copo(rr) { return copoEn(cx, cy, rr); }
    function circulo(x, y, rr) {
      return 'M' + f(x - rr) + ' ' + f(y) + 'a' + f(rr) + ' ' + f(rr) + ' 0 1 0 ' + f(2 * rr) + ' 0a' + f(rr) + ' ' + f(rr) + ' 0 1 0 ' + f(-2 * rr) + ' 0';
    }
    var cuerpo = '<path d="' + d + '" fill="none" stroke="' + TINTA + '" stroke-width="' + cfg.trazo + '" stroke-linejoin="round" stroke-linecap="round"/>' + extra;
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
  // Número de semana ISO 8601 (la semana 1 es la que contiene el primer jueves del año)
  function semanaISO(a, m, d) { var t = new Date(Date.UTC(a, m, d)), dia = (t.getUTCDay() + 6) % 7; t.setUTCDate(t.getUTCDate() - dia + 3); var j = new Date(Date.UTC(t.getUTCFullYear(), 0, 4)); return 1 + Math.round(((t - j) / 864e5 - 3 + ((j.getUTCDay() + 6) % 7)) / 7); }
  function claveDia(m, d) { return (m < 9 ? '0' : '') + (m + 1) + '-' + (d < 10 ? '0' : '') + d; }
  function calendarioAnual(spec) {
    var a = spec.anio, fest = {}, s = '';
    (spec.festivos || []).forEach(function (x) { fest[x[0]] = x[1]; });
    s += txt(15, 30, String(a), { size: 16, titular: true });
    if (spec.region) s += txt(195, 30, spec.region, { size: spec.region.length > 18 ? 6.5 : 8, titular: true, anchor: 'end', fill: GRIS });
    // Con números de semana (ISO 8601) cada mes tiene una columna más a la izquierda
    var sem = !!spec.semanas, w = 58, h = 54, x0 = 15, y0 = 44, cw = w / (sem ? 8 : 7), dx = sem ? cw : 0;
    for (var m = 0; m < 12; m++) {
      var mx = x0 + (m % 3) * (w + 3), my = y0 + Math.floor(m / 3) * h;
      s += txt(mx + 1, my, MESES[m], { size: 4.6, titular: true });
      if (sem) s += txt(mx + cw * .5, my + 6.5, 'S', { size: 2.4, anchor: 'middle', fill: GRIS });
      INICIALES.forEach(function (l, j) { s += txt(mx + dx + (j + .5) * cw, my + 6.5, l, { size: 2.8, anchor: 'middle', bold: true, fill: j === 6 ? ROJO : GRIS }); });
      var p0 = primerDia(a, m), nd = diasMes(a, m);
      for (var d = 1; d <= nd; d++) {
        var pos = p0 + d - 1, col = pos % 7, fila = Math.floor(pos / 7), k = claveDia(m, d), rojo = col === 6 || fest[k];
        var cx = mx + dx + (col + .5) * cw, cy = my + 13 + fila * 6.4;
        if (sem && (col === 0 || d === 1)) {
          s += '<rect x="' + f(mx + .4) + '" y="' + f(cy - 3.6) + '" width="' + f(cw - .8) + '" height="4.6" rx=".8" fill="#f1efe8"/>';
          s += txt(mx + cw * .5, cy - .2, semanaISO(a, m, d), { size: 2.5, anchor: 'middle', fill: GRIS });
        }
        if (fest[k]) s += '<circle cx="' + f(cx) + '" cy="' + f(cy - 1.05) + '" r="' + (sem ? 2.3 : 2.55) + '" fill="none" stroke="' + ROJO + '" stroke-width=".35"/>';
        s += txt(cx, cy, d, { size: sem ? 3.1 : 3.3, anchor: 'middle', bold: !!rojo, fill: rojo ? ROJO : TINTA });
      }
    }
    if (spec.festivos && spec.festivos.length) {
      var yy = y0 + 4 * h - 1, n = spec.festivos.length, cols = n > 10 ? 3 : 2, corto = cols === 3;
      s += txt(15, yy, (spec.leyenda || 'Festivos nacionales ' + a) + ' (en rojo, con círculo)', { size: 3.3, bold: true });
      var lista = spec.festivos.map(function (x) { var mm = Number(x[0].slice(0, 2)) - 1, dd = Number(x[0].slice(3)); return dd + ' ' + (corto ? MESES[mm].slice(0, 3).toLowerCase() : MESES[mm].toLowerCase()) + ': ' + x[1]; });
      var porCol = Math.ceil(n / cols);
      lista.forEach(function (l, i) {
        var c = Math.floor(i / porCol), tam = corto ? 2.7 : 3, max = corto ? 40 : 60;
        if (l.length > max) l = l.slice(0, max - 1) + '…';
        s += txt(15 + c * (corto ? 61 : 93), yy + 5 + (i % porCol) * 4.3, l, { size: tam });
      });
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

  // Calendario escolar de un curso (septiembre a junio): vacaciones, días no lectivos y festivos marcados
  function calendarioEscolar(spec) {
    var s = '', a0 = Number(spec.curso.slice(0, 4)), marcas = spec.marcas || {}, ini = spec.inicio, fin = spec.fin;
    var VERDE_C = '#d8eecf', NARANJA_C = '#fbe0c2', AZUL = '#2340b0';
    s += txt(15, 25, 'Calendario escolar ' + spec.curso, { size: 9, titular: true });
    if (spec.region) s += txt(15, 34, spec.region, { size: 5.5, titular: true, fill: GRIS });
    var w = 58, h = 57, x0 = 15, y0 = spec.region ? 45 : 40, cw = w / 7;
    for (var i = 0; i < 10; i++) {
      var m = (8 + i) % 12, a = i < 4 ? a0 : a0 + 1, mx = x0 + (i % 3) * (w + 3), my = y0 + Math.floor(i / 3) * h;
      s += txt(mx + 1, my, MESES[m] + ' ' + a, { size: 4.2, titular: true });
      INICIALES.forEach(function (l, j) { s += txt(mx + (j + .5) * cw, my + 6, l, { size: 2.6, anchor: 'middle', bold: true, fill: GRIS }); });
      var p0 = primerDia(a, m), nd = diasMes(a, m);
      for (var d = 1; d <= nd; d++) {
        var pos = p0 + d - 1, col = pos % 7, fila = Math.floor(pos / 7), iso = a + '-' + claveDia(m, d), mk = marcas[iso];
        var cx = mx + (col + .5) * cw, cy = my + 12 + fila * 6.3, fuera = (ini && iso < ini) || (fin && iso > fin), finde = col >= 5;
        if (mk && !finde && !fuera) {
          var fondo = mk[0] === 'vac' ? VERDE_C : mk[0] === 'nl' ? NARANJA_C : null;
          if (fondo) s += '<rect x="' + f(cx - cw / 2 + .3) + '" y="' + f(cy - 4.1) + '" width="' + f(cw - .6) + '" height="5.4" rx=".8" fill="' + fondo + '"/>';
          if (mk[0] === 'fest') s += '<circle cx="' + f(cx) + '" cy="' + f(cy - 1.1) + '" r="2.4" fill="none" stroke="' + ROJO + '" stroke-width=".35"/>';
        }
        if (ini && (iso === ini || iso === fin)) s += '<rect x="' + f(cx - 2.7) + '" y="' + f(cy - 3.9) + '" width="5.4" height="5" rx=".6" fill="none" stroke="' + AZUL + '" stroke-width=".55"/>';
        var color = fuera || finde ? '#a4a4aa' : mk && mk[0] === 'fest' ? ROJO : TINTA;
        s += txt(cx, cy, d, { size: 3.1, anchor: 'middle', bold: !fuera && !finde, fill: color });
      }
    }
    // leyenda y fechas clave en los dos huecos que quedan
    var lx = x0 + (10 % 3) * (w + 3), ly = y0 + 3 * h, ly2 = ly;
    s += txt(lx + 1, ly, 'Leyenda', { size: 4.2, titular: true });
    [['rect', VERDE_C, 'Vacaciones'], ['rect', NARANJA_C, 'Día no lectivo'], ['circ', ROJO, 'Festivo']].concat(ini ? [['caja', AZUL, 'Primer y último día de clase']] : []).concat([['gris', '#a4a4aa', 'Sin clase (fin de semana o fuera del curso)']]).forEach(function (l, k) {
      var yy = ly + 7 + k * 6.2;
      if (l[0] === 'rect') s += '<rect x="' + (lx + 1) + '" y="' + f(yy - 3.6) + '" width="6" height="4.6" rx=".8" fill="' + l[1] + '"/>';
      else if (l[0] === 'circ') s += '<circle cx="' + (lx + 4) + '" cy="' + f(yy - 1.3) + '" r="2.3" fill="none" stroke="' + l[1] + '" stroke-width=".4"/>';
      else if (l[0] === 'caja') s += '<rect x="' + (lx + 1.3) + '" y="' + f(yy - 3.6) + '" width="5.4" height="4.6" rx=".6" fill="none" stroke="' + l[1] + '" stroke-width=".55"/>';
      else s += txt(lx + 4, yy, '7', { size: 3.1, anchor: 'middle', fill: l[1] });
      parte(l[2], 30).forEach(function (t2, j) { s += txt(lx + 9, yy + j * 3.4, t2, { size: 2.9 }); });
    });
    var fx = x0 + (11 % 3) * (w + 3);
    s += txt(fx + 1, ly2, 'Fechas clave', { size: 4.2, titular: true });
    var fy = ly2 + 7;
    (spec.clave || []).slice(0, 8).forEach(function (l) { var ls = parte(l, 34).slice(0, 3); ls.forEach(function (t2, j) { s += txt(fx + 1, fy + j * 3.4, t2, { size: 2.8 }); }); fy += 3.4 * ls.length + 2.8; });
    if (spec.nota) s += txt(15, 282, spec.nota, { size: 2.6, fill: GRIS });
    return { svg: hoja({ alt: 'Calendario escolar ' + spec.curso + (spec.region ? ' de ' + spec.region : '') }, s), sol: null };
  }

  // ---------- problemas de matemáticas ----------
  // Cada plantilla recibe el generador aleatorio y devuelve el enunciado, la operación y la solución.
  var NOMBRES = ['Lucía', 'Hugo', 'Martina', 'Leo', 'Sofía', 'Mateo', 'Daniela', 'Pablo', 'Valeria', 'Álvaro', 'Carmen', 'Marcos', 'Julia', 'Daniel', 'Paula', 'Adrián', 'Noa', 'Mario', 'Alba', 'Iker', 'Aitana', 'Bruno', 'Vega', 'Nico'];
  var PROBLEMAS = {
    sumas: [
      function (r, N) { var a = ri(r, 12, 60), b = ri(r, 5, 35); return [N + ' tiene ' + a + ' cromos y su abuela le regala ' + b + ' más. ¿Cuántos cromos tiene ahora?', a + ' + ' + b + ' = ' + (a + b), (a + b) + ' cromos']; },
      function (r) { var a = ri(r, 25, 60), b = ri(r, 5, a - 8); return ['En el autobús van ' + a + ' personas. En la parada se bajan ' + b + '. ¿Cuántas personas quedan en el autobús?', a + ' − ' + b + ' = ' + (a - b), (a - b) + ' personas']; },
      function (r, N) { var t = ri(r, 6, 9) * 10, a = ri(r, 15, t - 12); return [N + ' ha leído ' + a + ' páginas de un libro de ' + t + ' páginas. ¿Cuántas páginas le faltan por leer?', t + ' − ' + a + ' = ' + (t - a), (t - a) + ' páginas']; },
      function (r) { var a = ri(r, 12, 45), b = ri(r, 12, 45); return ['En una caja hay ' + a + ' lápices rojos y ' + b + ' lápices azules. ¿Cuántos lápices hay en total?', a + ' + ' + b + ' = ' + (a + b), (a + b) + ' lápices']; },
      function (r, N) { var a = ri(r, 20, 50), b = ri(r, 6, a - 5); return [N + ' tenía ' + a + ' euros y se ha gastado ' + b + ' euros en un libro. ¿Cuánto dinero le queda?', a + ' − ' + b + ' = ' + (a - b), (a - b) + ' euros']; },
      function (r) { var a = ri(r, 14, 40), b = ri(r, 6, 25); return ['En el patio hay ' + a + ' niños jugando y llegan ' + b + ' más. ¿Cuántos niños hay ahora en el patio?', a + ' + ' + b + ' = ' + (a + b), (a + b) + ' niños']; },
      function (r) { var a = ri(r, 15, 48), b = ri(r, 12, 40); return ['Un granjero recoge ' + a + ' huevos por la mañana y ' + b + ' por la tarde. ¿Cuántos huevos ha recogido en todo el día?', a + ' + ' + b + ' = ' + (a + b), (a + b) + ' huevos']; },
      function (r, N) { var a = ri(r, 11, 16), b = ri(r, 2, 6); return [N + ' tiene ' + a + ' años y su hermana pequeña tiene ' + b + ' años menos. ¿Cuántos años tiene su hermana?', a + ' − ' + b + ' = ' + (a - b), (a - b) + ' años']; },
      function (r) { var a = ri(r, 40, 90), b = ri(r, 12, a - 15); return ['En una estantería de la biblioteca había ' + a + ' libros y se han prestado ' + b + '. ¿Cuántos libros quedan en la estantería?', a + ' − ' + b + ' = ' + (a - b), (a - b) + ' libros']; },
      function (r, N) { var a = ri(r, 25, 65), b = ri(r, 25, 65); return [N + ' ha hecho ' + a + ' puntos en la primera partida y ' + b + ' en la segunda. ¿Cuántos puntos ha hecho en total?', a + ' + ' + b + ' = ' + (a + b), (a + b) + ' puntos']; }
    ],
    mult: [
      function (r) { var a = ri(r, 3, 9), b = ri(r, 6, 12); return ['En una caja hay ' + a + ' paquetes de ' + b + ' galletas. ¿Cuántas galletas hay en total?', a + ' × ' + b + ' = ' + a * b, a * b + ' galletas']; },
      function (r, N) { var k = ri(r, 3, 8), q = ri(r, 4, 12); return [N + ' quiere repartir ' + k * q + ' caramelos entre ' + k + ' amigos a partes iguales. ¿Cuántos caramelos le tocan a cada uno?', k * q + ' : ' + k + ' = ' + q, q + ' caramelos']; },
      function (r) { var f = ri(r, 9, 14), a = 4; return ['Un autobús tiene ' + f + ' filas de ' + a + ' asientos. ¿Cuántos asientos tiene el autobús?', f + ' × ' + a + ' = ' + f * a, f * a + ' asientos']; },
      function (r) { var p = ri(r, 5, 9), k = ri(r, 3, 8); return ['Una entrada de cine cuesta ' + p + ' euros. ¿Cuánto pagan ' + k + ' amigos por sus entradas?', k + ' × ' + p + ' = ' + k * p, k * p + ' euros']; },
      function (r) { var k = ri(r, 4, 6), q = ri(r, 4, 7), re = ri(r, 1, k - 1), t = k * q + re; return ['En una clase de educación física hay ' + t + ' alumnos y se hacen equipos de ' + k + '. ¿Cuántos equipos completos se forman? ¿Cuántos alumnos sobran?', t + ' : ' + k + ' = ' + q + ', resto ' + re, q + ' equipos y sobran ' + re + ' alumnos']; },
      function (r) { var k = ri(r, 3, 9); return ['Una semana tiene 7 días. ¿Cuántos días hay en ' + k + ' semanas?', k + ' × 7 = ' + 7 * k, 7 * k + ' días']; },
      function (r, N) { var a = ri(r, 3, 9) * 5, k = ri(r, 3, 9); return [N + ' ahorra ' + a + ' euros cada mes. ¿Cuánto dinero habrá ahorrado en ' + k + ' meses?', a + ' × ' + k + ' = ' + a * k, a * k + ' euros']; },
      function (r) { var k = ri(r, 3, 9); return ['Una caja de huevos lleva 12 huevos. ¿Cuántas cajas hacen falta para guardar ' + 12 * k + ' huevos?', 12 * k + ' : 12 = ' + k, k + ' cajas']; },
      function (r) { var v = ri(r, 6, 12) * 10, h = ri(r, 2, 5); return ['Un tren recorre ' + v + ' kilómetros cada hora. ¿Cuántos kilómetros recorre en ' + h + ' horas?', v + ' × ' + h + ' = ' + v * h, v * h + ' kilómetros']; },
      function (r) { var f = ri(r, 4, 9), q = ri(r, 6, 12); return ['En un parque se han plantado ' + f * q + ' árboles en ' + f + ' filas iguales. ¿Cuántos árboles hay en cada fila?', f * q + ' : ' + f + ' = ' + q, q + ' árboles']; }
    ],
    mixto: [
      function (r, N) { var k = ri(r, 3, 5), p = ri(r, 2, 4), B = k * p < 10 ? 10 : 20; return [N + ' compra ' + k + ' cuadernos a ' + p + ' euros cada uno y paga con un billete de ' + B + ' euros. ¿Cuánto dinero le devuelven?', k + ' × ' + p + ' = ' + k * p + '; ' + B + ' − ' + k * p + ' = ' + (B - k * p), (B - k * p) + ' euros']; },
      function (r) { var g = ri(r, 8, 25), c = ri(r, 3, 12); return ['En una granja hay ' + g + ' gallinas y ' + c + ' vacas. ¿Cuántas patas hay en total?', g + ' × 2 = ' + 2 * g + '; ' + c + ' × 4 = ' + 4 * c + '; ' + 2 * g + ' + ' + 4 * c + ' = ' + (2 * g + 4 * c), (2 * g + 4 * c) + ' patas']; },
      function (r, N) { var d = ri(r, 8, 15), k = ri(r, 3, 6), t = d * k + ri(r, 20, 80); return ['Un libro tiene ' + t + ' páginas. ' + N + ' lee ' + d + ' páginas cada día durante ' + k + ' días. ¿Cuántas páginas le quedan por leer?', d + ' × ' + k + ' = ' + d * k + '; ' + t + ' − ' + d * k + ' = ' + (t - d * k), (t - d * k) + ' páginas']; },
      function (r) { var c = ri(r, 4, 6) * 10, a = ri(r, 70, 140), p = ri(r, 4, 8), tot = a + p, bus = Math.ceil(tot / c); return ['A una excursión van ' + a + ' alumnos y ' + p + ' profesores. En cada autobús caben ' + c + ' personas. ¿Cuántos autobuses hacen falta?', a + ' + ' + p + ' = ' + tot + '; ' + tot + ' : ' + c + ' = ' + Math.floor(tot / c) + (tot % c ? ', resto ' + tot % c + ' → hace falta uno más' : ''), bus + ' autobuses']; },
      function (r, N) { var a = ri(r, 20, 60), k = ri(r, 2, 5), b = 5, g = ri(r, 5, 15); return [N + ' tenía ' + a + ' cromos. Ha comprado ' + k + ' sobres de ' + b + ' cromos y ha regalado ' + g + ' a un amigo. ¿Cuántos cromos tiene ahora?', k + ' × ' + b + ' = ' + k * b + '; ' + a + ' + ' + k * b + ' = ' + (a + k * b) + '; ' + (a + k * b) + ' − ' + g + ' = ' + (a + k * b - g), (a + k * b - g) + ' cromos']; },
      function (r) { var a = ri(r, 25, 60), b = ri(r, 25, 60), t = a + b + ri(r, 15, 60); return ['En una tienda había ' + t + ' camisetas. Por la mañana se venden ' + a + ' y por la tarde ' + b + '. ¿Cuántas camisetas quedan?', a + ' + ' + b + ' = ' + (a + b) + '; ' + t + ' − ' + (a + b) + ' = ' + (t - a - b), (t - a - b) + ' camisetas']; },
      function (r) { var c = ri(r, 8, 20), j = ri(r, 10, 30), k = 4; while ((c + j) % k) j++; return ['Cuatro amigos compran una pelota de ' + c + ' euros y un juego de mesa de ' + j + ' euros, y pagan entre todos a partes iguales. ¿Cuánto paga cada uno?', c + ' + ' + j + ' = ' + (c + j) + '; ' + (c + j) + ' : 4 = ' + (c + j) / 4, (c + j) / 4 + ' euros']; },
      function (r, N) { var p = ri(r, 2, 4), k = ri(r, 3, 6), e = ri(r, 3, 8); return [N + ' compra ' + k + ' bocadillos a ' + p + ' euros cada uno y ' + k + ' zumos a 1 euro cada uno. Además, compra un postre de ' + e + ' euros. ¿Cuánto gasta en total?', k + ' × ' + p + ' = ' + k * p + '; ' + k + ' × 1 = ' + k + '; ' + k * p + ' + ' + k + ' + ' + e + ' = ' + (k * p + k + e), (k * p + k + e) + ' euros']; }
    ]
  };
  function problemas(spec, seed) {
    var r = rng(seed), lista = shuffle(r, PROBLEMAS[spec.nivel || 'sumas'].map(function (fn, i) { return i; })).slice(0, spec.n || 6);
    var nombres = shuffle(r, NOMBRES), items = lista.map(function (i, k) { return PROBLEMAS[spec.nivel || 'sumas'][i](r, nombres[k]); });
    var alto = spec.nivel === 'mixto' ? 47 : 39;
    function dibuja(sol) {
      var o = '', y = 52;
      items.forEach(function (it, k) {
        o += '<circle cx="19" cy="' + f(y - 1.5) + '" r="3.6" fill="' + TINTA + '"/>' + txt(19, y, k + 1, { size: 4, anchor: 'middle', bold: true, fill: '#fff' });
        var lineas = parte(it[0], 82);
        lineas.forEach(function (l, j) { o += txt(26, y + j * 5.6, l, { size: 4.2 }); });
        var yo = y + lineas.length * 5.6 + 1;
        o += txt(26, yo + 2, 'Operaciones:', { size: 3.2, fill: GRIS });
        if (sol) o += txt(26, yo + 9, it[1], { size: 3.8, bold: true, fill: ROJO });
        var ys = y + alto - 8;
        o += txt(122, ys, 'Solución:', { size: 3.8, bold: true }) + '<path d="M140 ' + f(ys + .6) + 'H195" stroke="' + TINTA + '" stroke-width=".25"/>';
        if (sol) o += txt(142, ys - .6, it[2], { size: 3.8, bold: true, fill: ROJO });
        o += '<path d="M15 ' + f(y + alto - 4) + 'H195" stroke="' + '#c9c9d2' + '" stroke-width=".25" stroke-dasharray="1 1"/>';
        y += alto;
      });
      return o;
    }
    var o = { titulo: spec.titulo, sub: spec.sub || 'Lee bien cada problema, haz las operaciones en el recuadro y escribe la solución con su unidad.', nombre: true, seed: seed };
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // ---------- estimulación cognitiva para mayores ----------
  // Letra grande, mucho espacio y una sola tarea por hoja. «tam» es el tamaño de la letra de los ejercicios (en mm).
  function enunciado(texto, y, size) {
    var o = '', l = parte(texto, Math.floor(180 / (size * .52)));
    l.forEach(function (x, i) { o += txt(15, y + i * size * 1.3, x, { size: size, bold: true }); });
    return { svg: o, y: y + l.length * size * 1.3 };
  }
  var FORMAS = ['círculo', 'cuadrado', 'triángulo', 'estrella', 'corazón', 'rombo', 'luna', 'cruz'];
  var FORMAS_PL = ['círculos', 'cuadrados', 'triángulos', 'estrellas', 'corazones', 'rombos', 'lunas', 'cruces'];
  function forma(k, cx, cy, s, grosor, color) {
    var st = ' fill="none" stroke="' + (color || TINTA) + '" stroke-width="' + f(grosor || Math.max(.5, s * .05)) + '" stroke-linejoin="round" stroke-linecap="round"';
    var h = s / 2, p = [], i;
    if (k === 0) return '<circle cx="' + f(cx) + '" cy="' + f(cy) + '" r="' + f(h * .9) + '"' + st + '/>';
    if (k === 1) return '<rect x="' + f(cx - h * .8) + '" y="' + f(cy - h * .8) + '" width="' + f(s * .8) + '" height="' + f(s * .8) + '"' + st + '/>';
    if (k === 2) return '<polygon points="' + f(cx) + ',' + f(cy - h * .9) + ' ' + f(cx + h * .95) + ',' + f(cy + h * .78) + ' ' + f(cx - h * .95) + ',' + f(cy + h * .78) + '"' + st + '/>';
    if (k === 3) {
      for (i = 0; i < 10; i++) { var rad = i % 2 ? h * .42 : h * .98, a = -Math.PI / 2 + i * Math.PI / 5; p.push(f(cx + rad * Math.cos(a)) + ',' + f(cy + rad * Math.sin(a) + h * .08)); }
      return '<polygon points="' + p.join(' ') + '"' + st + '/>';
    }
    if (k === 4) return '<path d="M' + f(cx) + ' ' + f(cy + h * .85) + 'C' + f(cx - h * 1.25) + ' ' + f(cy - h * .05) + ' ' + f(cx - h * .65) + ' ' + f(cy - h * 1.05) + ' ' + f(cx) + ' ' + f(cy - h * .42) +
      'C' + f(cx + h * .65) + ' ' + f(cy - h * 1.05) + ' ' + f(cx + h * 1.25) + ' ' + f(cy - h * .05) + ' ' + f(cx) + ' ' + f(cy + h * .85) + 'Z"' + st + '/>';
    if (k === 5) return '<polygon points="' + f(cx) + ',' + f(cy - h * .95) + ' ' + f(cx + h * .72) + ',' + f(cy) + ' ' + f(cx) + ',' + f(cy + h * .95) + ' ' + f(cx - h * .72) + ',' + f(cy) + '"' + st + '/>';
    if (k === 6) { // luna creciente
      var R = h * .9;
      return '<path d="M' + f(cx + R * .25) + ' ' + f(cy - R) + 'A' + f(R) + ' ' + f(R) + ' 0 1 0 ' + f(cx + R * .25) + ' ' + f(cy + R) +
        'A' + f(R * .78) + ' ' + f(R * .78) + ' 0 1 1 ' + f(cx + R * .25) + ' ' + f(cy - R) + 'Z"' + st + '/>';
    }
    var c = h * .3, b = h * .88;
    return '<path d="M' + f(cx - c) + ' ' + f(cy - b) + 'H' + f(cx + c) + 'V' + f(cy - c) + 'H' + f(cx + b) + 'V' + f(cy + c) + 'H' + f(cx + c) + 'V' + f(cy + b) +
      'H' + f(cx - c) + 'V' + f(cy + c) + 'H' + f(cx - b) + 'V' + f(cy - c) + 'H' + f(cx - c) + 'Z"' + st + '/>';
  }
  function marca(cx, cy, rad) { return '<circle cx="' + f(cx) + '" cy="' + f(cy) + '" r="' + f(rad) + '" fill="none" stroke="' + ROJO + '" stroke-width=".9"/>'; }
  function euros(n) { return (Math.round(n * 100) / 100).toFixed(Number.isInteger(Math.round(n * 100) / 100) ? 0 : 2).replace('.', ',') + ' €'; }
  function cabCog(spec, seed) { return { titulo: spec.titulo, nombre: spec.nombre !== false, seed: seed }; }
  function dos(spec, seed, dibuja) {
    var o = cabCog(spec, seed);
    return { svg: hoja(o, dibuja(false)), sol: hoja(Object.assign({}, o, { sol: true }), dibuja(true)) };
  }

  // Atención: rodear todas las letras o dibujos iguales al modelo
  function cancelacion(spec, seed) {
    var r = rng(seed), F = spec.filas || 10, C = spec.cols || 10, formas = !!spec.formas;
    var objs = [].concat(spec.objetivo != null ? spec.objetivo : (formas ? 4 : 'A'));
    var pool = formas ? (spec.pool || [0, 1, 2, 3, 4, 5]) : (spec.letras || 'ABCDEFGHIJLMNOPRSTUV').split('');
    var otros = pool.filter(function (x) { return objs.indexOf(x) < 0; }), celdas = [], i;
    for (i = 0; i < F * C; i++) celdas.push(r() < (spec.prop || .2) ? objs[ri(r, 0, objs.length - 1)] : otros[ri(r, 0, otros.length - 1)]);
    var minimo = Math.max(1, Math.round(F * C * (spec.prop || .2) * .7));
    for (var t = 0; t < 500 && celdas.filter(function (v) { return objs.indexOf(v) >= 0; }).length < minimo; t++) celdas[ri(r, 0, celdas.length - 1)] = objs[ri(r, 0, objs.length - 1)];
    var nombreObj = formas ? objs.map(function (k) { return 'todos los ' + FORMAS_PL[k]; }).join(' y ').replace('todos los estrellas', 'todas las estrellas').replace('todos los lunas', 'todas las lunas').replace('todos los cruces', 'todas las cruces')
      : 'todas las letras ' + objs.join(' y ');
    var total = celdas.filter(function (v) { return objs.indexOf(v) >= 0; }).length;
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || ('Rodea ' + nombreObj + '.'), 52, spec.tamInstr || 6.4), o = e.svg;
      var y0 = e.y + 4, xm = 15;
      o += txt(xm, y0 + 6, 'Modelo:', { size: 5, fill: GRIS });
      objs.forEach(function (v, k) {
        var cx = xm + 34 + k * 22;
        o += '<rect x="' + f(cx - 9) + '" y="' + f(y0 - 2) + '" width="18" height="18" rx="2" fill="none" stroke="' + TINTA + '" stroke-width=".6"/>';
        o += formas ? forma(v, cx, y0 + 7, 13, 1) : txt(cx, y0 + 12, v, { size: 12, anchor: 'middle', bold: true });
      });
      var top = y0 + 24, w = 180 / C, h = Math.min(w * 1.15, (280 - top) / F), size = Math.min(w, h) * (formas ? .72 : .62);
      celdas.forEach(function (v, k) {
        var cx = 15 + (k % C + .5) * w, cy = top + (Math.floor(k / C) + .5) * h;
        o += formas ? forma(v, cx, cy, size, Math.max(.6, size * .06)) : txt(cx, cy + size * .36, v, { size: f(size), anchor: 'middle', bold: true });
        if (sol && objs.indexOf(v) >= 0) o += marca(cx, cy, Math.min(w, h) * .46);
      });
      if (sol) o += txt(195, top - 4, 'Hay ' + total, { size: 5, anchor: 'end', bold: true, fill: ROJO });
      return o;
    });
  }

  // Lenguaje y memoria: completar refranes (escribiendo o eligiendo entre tres finales)
  function refranes(spec, seed) {
    var r = rng(seed), n = spec.n || 6, lista = shuffle(r, spec.lista).slice(0, n), size = spec.tam || 5.6;
    var opciones = lista.map(function (rf) {
      if (!spec.opciones) return null;
      var otros = shuffle(r, spec.lista.filter(function (x) { return x !== rf; })).slice(0, 2).map(function (x) { return x[1]; });
      return shuffle(r, [rf[1]].concat(otros));
    });
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || (spec.opciones ? 'Lee el principio de cada refrán y rodea el final correcto.' : 'Completa cada refrán con el final que falta.'), 52, 6.2), o = e.svg, y = e.y + 8;
      var alto = (280 - y) / n;
      lista.forEach(function (rf, k) {
        o += txt(15, y, (k + 1) + '. ' + rf[0] + '…', { size: size, bold: true });
        if (opciones[k]) {
          opciones[k].forEach(function (op, j) {
            var yy = y + size * 1.55 * (j + 1);
            o += '<circle cx="24" cy="' + f(yy - size * .32) + '" r="' + f(size * .32) + '" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>' + txt(29, yy, '…' + op, { size: f(size * .92) });
            if (sol && op === rf[1]) o += marca(24, yy - size * .32, size * .6) + '<circle cx="24" cy="' + f(yy - size * .32) + '" r="' + f(size * .2) + '" fill="' + ROJO + '"/>';
          });
        } else {
          var yl = y + size * 1.9;
          o += '<path d="M24 ' + f(yl) + 'H195" stroke="' + GRIS + '" stroke-width=".3"/>';
          if (sol) o += txt(26, yl - 1.2, '…' + rf[1], { size: size, fill: ROJO, bold: true });
        }
        y += alto;
      });
      return o;
    });
  }

  // Cálculo y razonamiento: series de números en las que faltan uno o dos
  function series(spec, seed) {
    var r = rng(seed), n = spec.n || 6, largo = spec.largo || 6, huecos = spec.huecos || 2, pasos = spec.pasos || [2, 3, 5, 10, -2, -5, 'x2'], lista = [], k;
    for (k = 0; k < n; k++) {
      var paso = pasos[ri(r, 0, pasos.length - 1)], ini, nums = [], i;
      if (paso === 'x2') { ini = ri(r, 1, 3); for (i = 0; i < largo; i++) nums.push(ini * Math.pow(2, i)); }
      else { ini = paso < 0 ? ri(r, -paso * largo + 2, -paso * largo + 30) : ri(r, 1, spec.max || 20); for (i = 0; i < largo; i++) nums.push(ini + paso * i); }
      var pos = spec.alFinal ? [largo - 1] : shuffle(r, Array.from({ length: largo - 2 }, function (_, j) { return j + 2; })).slice(0, huecos);
      lista.push({ nums: nums, huecos: pos });
    }
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || 'Mira cómo cambian los números y escribe los que faltan en los recuadros.', 52, 6.2), o = e.svg, y = e.y + 10;
      var alto = (282 - y) / n, w = 180 / largo, lado = Math.min(w - 4, alto - 8, 26);
      lista.forEach(function (s, k) {
        s.nums.forEach(function (v, i) {
          var cx = 15 + (i + .5) * w, cy = y + lado / 2, hueco = s.huecos.indexOf(i) >= 0;
          o += '<rect x="' + f(cx - lado / 2) + '" y="' + f(y) + '" width="' + f(lado) + '" height="' + f(lado) + '" rx="2" fill="' + (hueco ? '#fff' : '#f1efe8') + '" stroke="' + TINTA + '" stroke-width="' + (hueco ? .8 : .3) + '"/>';
          if (!hueco || sol) o += txt(cx, cy + lado * .17, v, { size: f(lado * .46), anchor: 'middle', bold: true, fill: hueco ? ROJO : TINTA });
        });
        y += alto;
      });
      return o;
    });
  }

  // Cálculo de la vida diaria: la compra
  // [nombre, unidad del precio, dos unidades, precio mínimo y máximo orientativos en euros]
  var PRODUCTOS = [['pan', 'barra', 'dos barras de pan', .8, 1.5], ['leche', 'litro', 'dos litros de leche', .9, 1.4], ['huevos', 'docena', 'dos docenas de huevos', 2, 3.5],
    ['manzanas', 'kilo', 'dos kilos de manzanas', 1.5, 3], ['aceite', 'litro', 'dos litros de aceite', 4, 9], ['café', 'paquete', 'dos paquetes de café', 2, 5],
    ['arroz', 'kilo', 'dos kilos de arroz', 1, 2], ['tomates', 'kilo', 'dos kilos de tomates', 1.5, 3], ['queso', 'cuña', 'dos cuñas de queso', 3, 6],
    ['galletas', 'paquete', 'dos paquetes de galletas', 1, 2.5], ['yogures', 'pack', 'dos packs de yogures', 1.5, 3], ['azúcar', 'kilo', 'dos kilos de azúcar', 1, 1.6],
    ['naranjas', 'kilo', 'dos kilos de naranjas', 1.2, 2.5]];
  function compra(spec, seed) {
    var r = rng(seed), enteros = !!spec.enteros, prods = shuffle(r, PRODUCTOS).slice(0, 6).map(function (p) {
      var v = p[3] + r() * (p[4] - p[3]);
      return { p: p[0], u: p[1], dos: p[2], v: enteros ? Math.max(1, Math.round(v)) : Math.round(v * 10) / 10 };
    });
    function suma(ix) { return ix.reduce(function (a, i) { return a + prods[i].v; }, 0); }
    var q = [];
    var a = shuffle(r, [0, 1, 2, 3, 4, 5]);
    q.push(['Compras ' + prods[a[0]].p + ' y ' + prods[a[1]].p + '. ¿Cuánto pagas?', suma([a[0], a[1]])]);
    var billete = enteros ? (suma([a[2], a[3]]) < 5 ? 5 : 10) : (suma([a[2], a[3]]) < 10 ? 10 : 20);
    q.push(['Compras ' + prods[a[2]].p + ' y ' + prods[a[3]].p + ' y pagas con un billete de ' + billete + ' €. ¿Cuánto te devuelven?', billete - suma([a[2], a[3]])]);
    q.push(['¿Cuánto cuestan ' + prods[a[4]].dos + '?', prods[a[4]].v * 2]);
    if (!enteros) q.push(['Compras ' + prods[a[5]].p + ', ' + prods[a[0]].p + ' y ' + prods[a[1]].p + '. ¿Cuánto pagas en total?', suma([a[5], a[0], a[1]])]);
    return dos(spec, seed, function (sol) {
      var e = enunciado('Mira los precios de la tienda y responde a las preguntas.', 52, 6.2), o = e.svg, y = e.y + 4;
      o += '<rect x="15" y="' + f(y) + '" width="180" height="' + (enteros ? 52 : 46) + '" rx="3" fill="#f6f4ee" stroke="' + TINTA + '" stroke-width=".5"/>';
      o += txt(105, y + 9, 'PRECIOS', { size: 5.4, anchor: 'middle', bold: true, fill: GRIS });
      prods.forEach(function (p, k) {
        var x = 25 + (k % 2) * 90, yy = y + 20 + Math.floor(k / 2) * (enteros ? 12 : 10);
        o += txt(x, yy, p.p.charAt(0).toUpperCase() + p.p.slice(1) + ' (' + p.u + ')', { size: enteros ? 6.2 : 5.6, bold: true }) + txt(x + 76, yy, euros(p.v), { size: enteros ? 6.6 : 5.8, bold: true, anchor: 'end' });
      });
      y += (enteros ? 52 : 46) + 12;
      var alto = (282 - y) / q.length, size = enteros ? 6.2 : 5.4;
      q.forEach(function (it, k) {
        var l = parte((k + 1) + '. ' + it[0], Math.floor(180 / (size * .5)));
        l.forEach(function (x, j) { o += txt(15, y + j * size * 1.3, x, { size: size }); });
        var ys = y + l.length * size * 1.3 + 8;
        o += txt(110, ys, 'Respuesta:', { size: size * .9, bold: true }) + '<path d="M' + (enteros ? 146 : 140) + ' ' + f(ys + .6) + 'H195" stroke="' + TINTA + '" stroke-width=".3"/>';
        if (sol) o += txt(150, ys - .8, euros(it[1]), { size: size, bold: true, fill: ROJO });
        y += alto;
      });
      return o;
    });
  }

  // Fluidez verbal: escribir palabras de una categoría o que empiecen por una letra
  function fluidez(spec, seed) {
    var r = rng(seed), items = shuffle(r, spec.pool).slice(0, spec.n || 3), lineas = spec.lineas || 8;
    var s = enunciado(spec.instr || 'Escribe todas las palabras que se te ocurran de cada grupo.', 52, 6.2), o = s.svg, y = s.y + 6;
    var alto = (282 - y) / items.length;
    items.forEach(function (it) {
      o += '<rect x="15" y="' + f(y) + '" width="180" height="10" rx="2" fill="#f1efe8"/>' + txt(19, y + 7.4, it, { size: 6, bold: true });
      var fil = Math.ceil(lineas / 2), paso = (alto - 16) / fil;
      for (var i = 0; i < lineas; i++) {
        var x = 15 + (i % 2) * 92, yy = y + 14 + (Math.floor(i / 2) + 1) * paso - 2;
        o += txt(x, yy, (i + 1) + '.', { size: 4.6, fill: GRIS }) + '<path d="M' + (x + 8) + ' ' + f(yy + .6) + 'H' + (x + 86) + '" stroke="' + GRIS + '" stroke-width=".3"/>';
      }
      y += alto;
    });
    return { svg: hoja(cabCog(spec, seed), o), sol: null };
  }

  // Orientación: preguntas sobre el día, el lugar y la persona (con o sin opciones para rodear)
  function orientacion(spec) {
    var e = enunciado(spec.instr || 'Responde a estas preguntas. Si no sabes alguna, puedes mirar un calendario o preguntar.', 52, 6.2), o = e.svg, y = e.y + 8;
    var alto = (282 - y) / spec.preguntas.length, size = spec.tam || 5.8;
    spec.preguntas.forEach(function (q) {
      o += txt(15, y, q[0], { size: size, bold: true });
      if (q[1]) {
        var x = 18;
        q[1].forEach(function (op) { var ancho = op.length * size * .52 + 10; if (x + ancho > 195) { x = 18; y += size * 1.8; } o += txt(x, y + size * 1.8, op, { size: f(size * .95) }); x += ancho; });
      } else {
        o += '<path d="M15 ' + f(y + size * 2.2) + 'H195" stroke="' + GRIS + '" stroke-width=".3"/>';
      }
      y += alto;
    });
    return { svg: hoja({ titulo: spec.titulo, nombre: spec.nombre !== false }, o), sol: null };
  }

  // Funciones ejecutivas: numerar los pasos de una tarea en orden
  function ordenar(spec, seed) {
    var r = rng(seed), listas = shuffle(r, spec.listas).slice(0, spec.n || 2).map(function (l) {
      return { t: l[0], pasos: l[1], orden: shuffle(r, l[1].map(function (_, i) { return i; })) };
    }), size = spec.tam || 5.6;
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || 'Escribe en cada recuadro el número del orden: 1 para lo primero, 2 para lo siguiente…', 52, 6.2), o = e.svg, y = e.y + 8;
      listas.forEach(function (l) {
        o += txt(15, y, l.t, { size: size * 1.1, bold: true, fill: GRIS });
        y += size * 1.6;
        l.orden.forEach(function (i) {
          o += '<rect x="15" y="' + f(y - size * 1.05) + '" width="' + f(size * 1.6) + '" height="' + f(size * 1.6) + '" rx="1.5" fill="#fff" stroke="' + TINTA + '" stroke-width=".6"/>';
          if (sol) o += txt(15 + size * .8, y + size * .12, i + 1, { size: f(size), anchor: 'middle', bold: true, fill: ROJO });
          o += txt(15 + size * 2.4, y, l.pasos[i], { size: size });
          y += size * 2.15;
        });
        y += size * 1.4;
      });
      return o;
    });
  }

  // Categorización: escribir cada palabra en su grupo
  function clasificar(spec, seed) {
    var r = rng(seed), grupos = shuffle(r, Object.keys(spec.grupos)).slice(0, spec.ngrupos || 2), por = spec.porGrupo || 4;
    var elegidas = grupos.map(function (g) { return shuffle(r, spec.grupos[g]).slice(0, por); });
    var palabras = shuffle(r, [].concat.apply([], elegidas)), size = spec.tam || 6;
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || 'Lee las palabras y escribe cada una debajo del grupo al que pertenece.', 52, 6.2), o = e.svg, y = e.y + 4;
      var cols = 3, fil = Math.ceil(palabras.length / cols), alto = size * 1.9;
      o += '<rect x="15" y="' + f(y) + '" width="180" height="' + f(fil * alto + 8) + '" rx="3" fill="#f6f4ee" stroke="' + TINTA + '" stroke-width=".4"/>';
      palabras.forEach(function (p, k) { o += txt(15 + (k % cols + .5) * 60, y + 4 + (Math.floor(k / cols) + .75) * alto, p, { size: size, anchor: 'middle', bold: true }); });
      y += fil * alto + 18;
      var w = 180 / grupos.length;
      grupos.forEach(function (g, j) {
        var x = 15 + j * w;
        o += '<rect x="' + f(x + 2) + '" y="' + f(y) + '" width="' + f(w - 4) + '" height="12" rx="2" fill="' + TINTA + '"/>' + txt(x + w / 2, y + 8.4, g.toUpperCase(), { size: 5.4, anchor: 'middle', bold: true, fill: '#fff' });
        for (var i = 0; i < por; i++) {
          var yy = y + 30 + i * 20;
          o += '<path d="M' + f(x + 6) + ' ' + f(yy) + 'H' + f(x + w - 6) + '" stroke="' + GRIS + '" stroke-width=".35"/>';
          if (sol) o += txt(x + w / 2, yy - 1.5, elegidas[j][i], { size: size, anchor: 'middle', bold: true, fill: ROJO });
        }
      });
      return o;
    });
  }

  // Praxias y atención visual: copiar un dibujo uniendo puntos
  function copiar(spec, seed) {
    var r = rng(seed), N = spec.puntos || 4, n = spec.n || 3, segs = spec.segs || N + 2, figuras = [], k;
    var M = [[0, 1], [1, 0], [0, -1], [-1, 0]].concat(spec.diagonales === false ? [] : [[1, 1], [1, -1], [-1, 1], [-1, -1]]);
    for (k = 0; k < n; k++) {
      var p = [ri(r, 0, N - 1), ri(r, 0, N - 1)], camino = [p.slice()], usadas = {};
      for (var t = 0; t < 400 && camino.length <= segs; t++) {
        var m = M[ri(r, 0, M.length - 1)], q = [p[0] + m[0], p[1] + m[1]];
        if (q[0] < 0 || q[1] < 0 || q[0] >= N || q[1] >= N) continue;
        var clave = [p.join(), q.join()].sort().join('|');
        if (usadas[clave]) continue;
        usadas[clave] = 1; camino.push(q); p = q;
      }
      figuras.push(camino);
    }
    var e = enunciado(spec.instr || 'Copia cada dibujo en la cuadrícula de puntos de la derecha.', 52, 6.2), o = e.svg, y = e.y + 6;
    var alto = (282 - y) / n, lado = Math.min(alto - 10, 80), paso = lado / (N - 1);
    figuras.forEach(function (c) {
      [24, 115].forEach(function (x0, lado2) {
        for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) o += '<circle cx="' + f(x0 + i * paso) + '" cy="' + f(y + j * paso) + '" r="' + f(Math.max(1, paso * .07)) + '" fill="' + TINTA + '"/>';
        if (!lado2) o += '<path d="M' + c.map(function (pt) { return f(x0 + pt[0] * paso) + ' ' + f(y + pt[1] * paso); }).join('L') + '" fill="none" stroke="' + TINTA + '" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>';
      });
      o += '<path d="M105 ' + f(y - 4) + 'V' + f(y + lado + 4) + '" stroke="#c9c9d2" stroke-width=".3" stroke-dasharray="1.5 1.5"/>';
      y += alto;
    });
    return { svg: hoja(cabCog(spec, seed), o), sol: null };
  }

  // Unir con una línea cada dibujo con su igual
  function iguales(spec, seed) {
    var r = rng(seed), n = spec.n || 4, elegidas = shuffle(r, spec.pool || [0, 1, 2, 3, 4, 5, 6, 7]).slice(0, n), dcha = shuffle(r, elegidas);
    for (var t = 0; t < 50 && dcha.some(function (v, i) { return v === elegidas[i]; }); t++) dcha = shuffle(r, elegidas);  // ninguno enfrente de su igual
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || 'Une con una línea cada dibujo con el que es igual.', 52, spec.tamInstr || 7), o = e.svg, y0 = e.y + 8;
      var alto = (284 - y0) / n, s = Math.min(alto * .7, spec.max || 34);
      elegidas.forEach(function (v, i) {
        var y = y0 + (i + .5) * alto, j = dcha.indexOf(v), y2 = y0 + (j + .5) * alto;
        o += forma(v, 45, y, s, Math.max(1, s * .06)) + forma(dcha[i], 165, y0 + (i + .5) * alto, s, Math.max(1, s * .06));
        o += '<circle cx="' + f(45 + s * .65) + '" cy="' + f(y) + '" r="1.6" fill="' + TINTA + '"/><circle cx="' + f(165 - s * .65) + '" cy="' + f(y0 + (i + .5) * alto) + '" r="1.6" fill="' + TINTA + '"/>';
        if (sol) o += '<path d="M' + f(45 + s * .65) + ' ' + f(y) + 'L' + f(165 - s * .65) + ' ' + f(y2) + '" stroke="' + ROJO + '" stroke-width="1"/>';
      });
      return o;
    });
  }

  // Contar dibujos y rodear el número
  function contar(spec, seed) {
    var r = rng(seed), n = spec.n || 4, max = spec.max || 5, filas = [];
    for (var i = 0; i < n; i++) filas.push({ k: ri(r, 0, 5), c: ri(r, 1, max) });
    return dos(spec, seed, function (sol) {
      var e = enunciado(spec.instr || 'Cuenta los dibujos de cada fila y rodea el número.', 52, spec.tamInstr || 7), o = e.svg, y0 = e.y + 6;
      var alto = (284 - y0) / n, s = Math.min(alto * .55, 120 / max - 3);
      filas.forEach(function (fl, i) {
        var cy = y0 + (i + .5) * alto;
        for (var j = 0; j < fl.c; j++) o += forma(fl.k, 18 + s / 2 + j * (s + 3), cy, s, Math.max(.9, s * .06));
        o += '<path d="M15 ' + f(y0 + (i + 1) * alto) + 'H195" stroke="#c9c9d2" stroke-width=".3"/>';
        for (j = 1; j <= max; j++) {
          var cx = 140 + (j - 1) * (55 / max) + 55 / max / 2;
          var tn = Math.min(16, 55 / max * .8);
          o += txt(cx, cy + tn * .36, j, { size: f(tn), anchor: 'middle', bold: true });
          if (sol && j === fl.c) o += marca(cx, cy, tn * .62);
        }
      });
      return o;
    });
  }

  // Colorear figuras grandes, con una consigna sencilla
  var COLORES = ['rojo', 'azul', 'amarillo', 'verde', 'naranja', 'morado'];
  function colorear(spec, seed) {
    var r = rng(seed), n = spec.n || 2, ks = shuffle(r, spec.pool || [0, 1, 2, 3, 4, 5, 6, 7]).slice(0, n), cols = shuffle(r, COLORES);
    var e = enunciado(spec.instr || 'Colorea cada dibujo del color que se indica.', 52, 7.2), o = e.svg, y0 = e.y + 4;
    var alto = (284 - y0) / n, s = Math.min(alto - 20, 150);
    ks.forEach(function (k, i) {
      var cy = y0 + i * alto + (alto - 14) / 2;
      o += forma(k, 105, cy, s, 1.6);
      o += txt(105, y0 + (i + 1) * alto - 4, 'El ' + FORMAS[k] + ', de color ' + cols[i] + '.', { size: 7, anchor: 'middle', bold: true }).replace('El estrella', 'La estrella').replace('El luna', 'La luna').replace('El cruz', 'La cruz');
    });
    return { svg: hoja(cabCog(spec, seed), o), sol: null };
  }

  // ---------- material para dinámicas de grupo con mayores ----------
  // Tarjetas para recortar: cada item es un texto o [texto grande, texto pequeño]
  function tarjetas(spec, seed) {
    var r = rng(seed), C = spec.cols || 2, F = spec.filas || 5, items = (spec.items || []).slice();
    if (spec.pares) {  // parejas para emparejar (principio y final de un refrán): se eligen al azar y se mezclan las mitades
      items = [];
      shuffle(r, spec.pares).slice(0, Math.floor(C * F / 2)).forEach(function (p) { items.push(p[0] + '…', '…' + p[1]); });
      items = shuffle(r, items);
    } else if (spec.mezclar) items = shuffle(r, items);
    items = items.slice(0, C * F);
    var y0 = spec.sub ? 40 : 34, w = 180 / C, h = (282 - y0) / F, o = '', size = spec.tam || 7;
    items.forEach(function (it, k) {
      var x = 15 + (k % C) * w, y = y0 + Math.floor(k / C) * h, a = Array.isArray(it) ? it[0] : it, b = Array.isArray(it) ? it[1] : '';
      o += '<rect x="' + f(x + 1.5) + '" y="' + f(y + 1.5) + '" width="' + f(w - 3) + '" height="' + f(h - 3) + '" rx="3" fill="#fff" stroke="' + GRIS + '" stroke-width=".3" stroke-dasharray="2 1.5"/>';
      var l = parte(a, Math.floor((w - 10) / (size * .52))), t = size;
      if (l.length > 3) { t = size * .8; l = parte(a, Math.floor((w - 10) / (t * .52))); }
      var alto = l.length * t * 1.2 + (b ? t * 1.3 : 0), yy = y + h / 2 - alto / 2 + t * .85;
      l.forEach(function (x2, j) { o += txt(x + w / 2, yy + j * t * 1.2, x2, { size: f(t), anchor: 'middle', bold: true }); });
      if (b) o += txt(x + w / 2, yy + l.length * t * 1.2 + t * .2, b, { size: f(t * .8), anchor: 'middle', fill: spec.colorB || GRIS, bold: true });
    });
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub, seed: spec.mezclar || spec.pares ? seed : null }, o), sol: null };
  }

  // Hoja del monitor para el bingo con sumas: cada número del 1 al 90 dicho como una suma o una resta
  function bingoSumas(spec, seed) {
    var r = rng(seed), max = spec.max || 90, o = '', cols = 5, filas = Math.ceil(max / cols), w = 180 / cols, h = (282 - 40) / filas;
    for (var n = 1; n <= max; n++) {
      var x = 15 + ((n - 1) % cols) * w, y = 40 + Math.floor((n - 1) / cols) * h + h * .7, expr;
      if (n <= 2) expr = n === 1 ? '0 + 1' : '1 + 1';
      else if (r() < .7) { var a = ri(r, 1, n - 1); expr = a + ' + ' + (n - a); }
      else { var b = ri(r, 1, 10); expr = (n + b) + ' − ' + b; }
      o += txt(x + 2, y, expr, { size: 4.2 }) + txt(x + w - 4, y, '= ' + n, { size: 4.2, anchor: 'end', bold: true, fill: ROJO });
    }
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub || 'Lee la operación en voz alta; los jugadores calculan el número y lo buscan en su cartón.', seed: seed }, o), sol: null };
  }

  // Plantilla de receta para el recetario del grupo
  function receta(spec) {
    var o = '', y = 46, ln = function (yy, x0) { return '<path d="M' + (x0 || 15) + ' ' + f(yy) + 'H195" stroke="' + GRIS + '" stroke-width=".3"/>'; };
    o += txt(15, y, 'Nombre del plato:', { size: 5.4, bold: true }) + ln(y + .8, 66); y += 12;
    o += txt(15, y, 'La receta de:', { size: 5.4, bold: true }) + ln(y + .8, 52); y += 12;
    o += txt(15, y, 'Para cuántas personas:', { size: 5.4, bold: true }) + ln(y + .8, 78); y += 16;
    o += '<rect x="15" y="' + y + '" width="180" height="10" rx="2" fill="#f1efe8"/>' + txt(19, y + 7.3, 'Ingredientes', { size: 5.6, bold: true }); y += 20;
    for (var i = 0; i < 6; i++) { o += txt(15, y, '•', { size: 5 }) + ln(y + .8, 21); y += 9; }
    y += 4;
    o += '<rect x="15" y="' + y + '" width="180" height="10" rx="2" fill="#f1efe8"/>' + txt(19, y + 7.3, 'Cómo se hace', { size: 5.6, bold: true }); y += 20;
    for (i = 1; i <= 6; i++) { o += txt(15, y, i + '.', { size: 5, bold: true }) + ln(y + .8, 23); y += 9; }
    y += 4;
    o += '<rect x="15" y="' + y + '" width="180" height="10" rx="2" fill="#f1efe8"/>' + txt(19, y + 7.3, 'El truco de la casa y un recuerdo', { size: 5.6, bold: true }); y += 18;
    for (i = 0; i < 3 && y < 272; i++) { o += ln(y); y += 10; }
    return { svg: hoja({ titulo: spec.titulo }, o), sol: null };
  }

  // Lista en grupos (canciones, temas…) para quien dirige la sesión
  function listaGrupos(spec) {
    var o = '', y = 44, size = spec.tam || 5.2;
    spec.grupos.forEach(function (g) {
      o += '<rect x="15" y="' + f(y - 6.5) + '" width="180" height="9" rx="2" fill="#f1efe8"/>' + txt(19, y, g[0], { size: 5, bold: true });
      y += size * 1.9;
      g[1].forEach(function (it, k) {
        var x = 15 + (k % 2) * 92, yy = y + Math.floor(k / 2) * size * 2.6;
        o += txt(x + 2, yy, '♪ ' + it[0], { size: size, bold: true }) + txt(x + 6, yy + size * 1.05, it[1], { size: f(size * .82), fill: GRIS });
      });
      y += Math.ceil(g[1].length / 2) * size * 2.6 + 6;
    });
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub }, o), sol: null };
  }

  // Hoja de registro de una sesión de grupo
  function sesion(spec) {
    var o = '', y = 44, ln = function (yy, x0) { return '<path d="M' + (x0 || 15) + ' ' + f(yy) + 'H195" stroke="' + GRIS + '" stroke-width=".3"/>'; };
    o += txt(15, y, 'Fecha:', { size: 4.6, bold: true }) + '<path d="M31 ' + f(y + .8) + 'H100" stroke="' + GRIS + '" stroke-width=".3"/>' + txt(108, y, 'Grupo / sala:', { size: 4.6, bold: true }) + ln(y + .8, 138); y += 12;
    o += txt(15, y, 'Orientación (día, tiempo, noticia del día):', { size: 4.6, bold: true }); y += 8; o += ln(y); y += 12;
    o += '<rect x="15" y="' + y + '" width="180" height="9" fill="' + TINTA + '"/>';
    [['Dinámica', 15], ['Qué trabaja', 80], ['Min.', 130], ['Cómo ha ido', 148]].forEach(function (c) { o += txt(c[1] + 2, y + 6.4, c[0], { size: 4, bold: true, fill: '#fff' }); });
    y += 9;
    for (var i = 0; i < 5; i++) {
      o += '<rect x="15" y="' + f(y) + '" width="180" height="16" fill="none" stroke="' + TINTA + '" stroke-width=".3"/>';
      [80, 130, 148].forEach(function (x) { o += '<path d="M' + x + ' ' + f(y) + 'v16" stroke="' + TINTA + '" stroke-width=".3"/>'; });
      y += 16;
    }
    y += 12;
    o += txt(15, y, 'Asistentes y observaciones', { size: 4.6, bold: true }); y += 4;
    o += '<rect x="15" y="' + y + '" width="180" height="9" fill="#f1efe8" stroke="' + TINTA + '" stroke-width=".3"/>';
    [['Nombre', 15], ['Participa', 75], ['Ánimo', 105], ['Observaciones', 130]].forEach(function (c) { o += txt(c[1] + 2, y + 6.4, c[0], { size: 3.8, bold: true }); });
    y += 9;
    while (y < 270) {
      o += '<rect x="15" y="' + f(y) + '" width="180" height="10" fill="none" stroke="' + TINTA + '" stroke-width=".25"/>';
      [75, 105, 130].forEach(function (x) { o += '<path d="M' + x + ' ' + f(y) + 'v10" stroke="' + TINTA + '" stroke-width=".25"/>'; });
      o += txt(78, y + 7, '☐ sí  ☐ no', { size: 3.2, fill: GRIS }) + txt(108, y + 7, '☺  ☹', { size: 4, fill: GRIS });
      y += 10;
    }
    return { svg: hoja({ titulo: spec.titulo }, o), sol: null };
  }


  // ---------- más Navidad: Adviento, etiquetas, menú, lista de regalos y amigo invisible ----------
  function lineaPunteada(x1, x2, y) { return '<path d="M' + f(x1) + ' ' + f(y) + 'H' + f(x2) + '" stroke="#8a8a90" stroke-width=".25"/>'; }
  // Calendario de Adviento: 24 casillas (desordenadas, siempre igual) o, con actividades, una propuesta para cada día
  function adviento(spec) {
    var s = '', cols = 4, filas = 6, w = 180 / cols, h = 236 / filas, y0 = 42, orden = [];
    for (var k = 1; k <= 24; k++) orden.push(k);
    if (!spec.actividades) orden = shuffle(rng(2412), orden);
    orden.forEach(function (dia, i) {
      var x = 15 + (i % cols) * w, y = y0 + Math.floor(i / cols) * h;
      s += '<rect x="' + f(x + 1.5) + '" y="' + f(y + 1.5) + '" width="' + f(w - 3) + '" height="' + f(h - 3) + '" rx="3" fill="#fff" stroke="' + (dia === 24 ? ROJO : TINTA) + '" stroke-width="' + (dia === 24 ? .8 : .4) + '"/>';
      if (spec.actividades) {
        s += txt(x + 6, y + 11, dia, { size: 8, titular: true, fill: dia === 24 ? ROJO : TINTA });
        s += dibujo(dia % 6, x + w - 9, y + 9, 8, GRIS);
        parte(spec.actividades[dia - 1], 22).slice(0, 4).forEach(function (l, j) { s += txt(x + 5, y + 20 + j * 4.6, l, { size: 3.5 }); });
      } else {
        s += dibujo(dia % 6, x + w / 2, y + h / 2 + 5, 15, '#b4b4ba');
        s += txt(x + w / 2, y + 15, dia, { size: 11, titular: true, anchor: 'middle', fill: dia === 24 ? ROJO : TINTA });
      }
    });
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub }, s), sol: null };
  }

  // Etiquetas para regalos: 12 por hoja, para recortar, con agujero para la cinta
  function etiquetas(spec) {
    var s = '', cols = 3, filas = 4, w = 180 / cols, h = 236 / filas, y0 = 38;
    for (var i = 0; i < cols * filas; i++) {
      var x = 15 + (i % cols) * w, y = y0 + Math.floor(i / cols) * h, cx = x + w / 2;
      s += '<path d="M' + f(x + 12) + ' ' + f(y + 3) + 'H' + f(x + w - 4) + 'V' + f(y + h - 3) + 'H' + f(x + 12) + 'L' + f(x + 3) + ' ' + f(y + h / 2) + 'Z" fill="none" stroke="' + TINTA + '" stroke-width=".4" stroke-dasharray="2 1.4"/>';
      s += '<circle cx="' + f(x + 10) + '" cy="' + f(y + h / 2) + '" r="1.6" fill="none" stroke="' + TINTA + '" stroke-width=".4"/>';
      s += dibujo(i % 6, cx + 4, y + 13, 11, i % 2 ? ROJO : TINTA);
      if (spec.texto) s += txt(cx + 4, y + 27, spec.texto, { size: 4.6, anchor: 'middle', titular: true });
      var yy = y + (spec.texto ? 38 : 32);
      s += txt(x + 16, yy, 'Para:', { size: 4 }) + lineaPunteada(x + 27, x + w - 8, yy);
      s += txt(x + 16, yy + 10, 'De:', { size: 4 }) + lineaPunteada(x + 25, x + w - 8, yy + 10);
    }
    return { svg: hoja({ titulo: spec.titulo, sub: 'Recorta por la línea de puntos y haz un agujero en el círculo para pasar la cinta. Mejor en cartulina.' }, s), sol: null };
  }

  // Menú para la mesa (Nochebuena, Navidad, Nochevieja…)
  function menuFiesta(spec) {
    var s = '', y = 58;
    s += dibujo(0, 105, 22, 16, ROJO) + dibujo(1, 70, 26, 13) + dibujo(1, 140, 26, 13);
    s += txt(105, 46, spec.cabecera, { size: 13, titular: true, anchor: 'middle' });
    s += txt(105, 54, 'Fecha: ......................................................', { size: 4, anchor: 'middle', fill: GRIS });
    (spec.secciones || ['Para picar', 'Primer plato', 'Segundo plato', 'Postre', 'Para brindar']).forEach(function (sec) {
      y += 16;
      s += txt(105, y, sec, { size: 7, titular: true, anchor: 'middle', fill: ROJO });
      s += '<path d="M85 ' + f(y + 2.5) + 'H125" stroke="' + ROJO + '" stroke-width=".3"/>';
      for (var j = 0; j < 2; j++) { y += 10; s += lineaPunteada(40, 170, y); }
      y += 4;
    });
    if (spec.pie) s += txt(105, Math.min(y + 14, 276), spec.pie, { size: 4.4, anchor: 'middle', fill: GRIS });
    s += '<rect x="9" y="8" width="192" height="276" rx="4" fill="none" stroke="' + TINTA + '" stroke-width=".6"/><rect x="11.5" y="10.5" width="187" height="271" rx="3" fill="none" stroke="' + ROJO + '" stroke-width=".3"/>';
    return { svg: hoja({ alt: spec.cabecera, sinPie: false }, s), sol: null };
  }

  // Lista de regalos: para quién, qué, presupuesto y si ya está comprado
  function listaRegalos(spec) {
    var s = '', y = 44, cols = [['Para quién', 15], ['Regalo', 62], ['Presupuesto', 140], ['Comprado', 172]], filas = spec.filas || 18;
    s += '<rect x="15" y="' + y + '" width="180" height="9" fill="' + TINTA + '"/>';
    cols.forEach(function (c) { s += txt(c[1] + 2, y + 6.3, c[0], { size: 4, bold: true, fill: '#fff' }); });
    y += 9;
    for (var i = 0; i < filas; i++) {
      s += '<rect x="15" y="' + f(y) + '" width="180" height="11" fill="' + (i % 2 ? '#f7f5ef' : '#fff') + '" stroke="' + TINTA + '" stroke-width=".25"/>';
      [62, 140, 172].forEach(function (x) { s += '<path d="M' + x + ' ' + f(y) + 'v11" stroke="' + TINTA + '" stroke-width=".25"/>'; });
      s += '<rect x="181" y="' + f(y + 3) + '" width="5" height="5" rx=".6" fill="none" stroke="' + TINTA + '" stroke-width=".35"/>';
      s += txt(169, y + 7.5, '€', { size: 3.6, anchor: 'end', fill: GRIS });
      y += 11;
    }
    s += txt(140, y + 9, 'Total:', { size: 4.6, bold: true, anchor: 'end' }) + '<rect x="142" y="' + f(y + 3) + '" width="30" height="9" fill="none" stroke="' + TINTA + '" stroke-width=".35"/>' + txt(169, y + 9.3, '€', { size: 3.6, anchor: 'end', fill: GRIS });
    s += txt(15, y + 21, 'Presupuesto total que me he puesto:', { size: 4.2 }) + lineaPunteada(78, 120, y + 21);
    return { svg: hoja({ titulo: spec.titulo, sub: spec.sub }, s), sol: null };
  }

  // Amigo invisible: papelitos para el sorteo y hoja de quien organiza
  function amigoInvisible(spec) {
    var s = '';
    if (spec.modo === 'organiza') {
      var y = 46;
      s += txt(15, y, 'Fecha del intercambio:', { size: 4.4 }) + lineaPunteada(58, 110, y) + txt(115, y, 'Presupuesto:', { size: 4.4 }) + lineaPunteada(139, 195, y);
      y += 10;
      s += txt(15, y, 'Lugar:', { size: 4.4 }) + lineaPunteada(28, 195, y);
      y += 10;
      s += '<rect x="15" y="' + y + '" width="180" height="9" fill="' + TINTA + '"/>';
      [['Participante', 15], ['Le regala a…', 75], ['Ideas o gustos', 128]].forEach(function (c) { s += txt(c[1] + 2, y + 6.3, c[0], { size: 4, bold: true, fill: '#fff' }); });
      y += 9;
      for (var i = 0; i < 16; i++) {
        s += '<rect x="15" y="' + f(y) + '" width="180" height="12" fill="none" stroke="' + TINTA + '" stroke-width=".25"/>';
        [75, 128].forEach(function (x) { s += '<path d="M' + x + ' ' + f(y) + 'v12" stroke="' + TINTA + '" stroke-width=".25"/>'; });
        s += txt(19, y + 8, (i + 1) + '.', { size: 3.6, fill: GRIS });
        y += 12;
      }
      s += txt(15, y + 9, 'Consejo: si haces el sorteo a mano, que nadie se saque a sí mismo; si pasa, se repite el sorteo.', { size: 3.6, fill: GRIS });
      return { svg: hoja({ titulo: spec.titulo, sub: spec.sub }, s), sol: null };
    }
    var cols = 2, filas = 5, w = 180 / cols, h = 240 / filas, y0 = 36;
    for (var k = 0; k < cols * filas; k++) {
      var x = 15 + (k % cols) * w, yy = y0 + Math.floor(k / cols) * h;
      s += '<rect x="' + f(x + 1.5) + '" y="' + f(yy + 1.5) + '" width="' + f(w - 3) + '" height="' + f(h - 3) + '" rx="3" fill="none" stroke="' + TINTA + '" stroke-width=".35" stroke-dasharray="2 1.4"/>';
      s += dibujo(2, x + 11, yy + 12, 11, ROJO);
      s += txt(x + 20, yy + 13, 'Amigo invisible', { size: 5.2, titular: true });
      s += txt(x + 6, yy + 25, 'Te ha tocado regalar a:', { size: 4 }) + lineaPunteada(x + 6, x + w - 6, yy + 34);
      s += txt(x + 6, yy + 43, 'Presupuesto:', { size: 3.6, fill: GRIS }) + lineaPunteada(x + 27, x + w - 6, yy + 43);
    }
    return { svg: hoja({ titulo: spec.titulo, sub: 'Escribe un nombre en cada papelito, recórtalos, dóblalos y que cada uno saque uno al azar.' }, s), sol: null };
  }

  var TIPOS = {
    sopa: sopa, sudoku: sudoku, laberinto: laberinto, bingo90: bingo90, bingo75: bingo75, 'bingo-numeros': bingoNumeros,
    tabla: tabla, 'tablas-todas': tablasTodas, pitagorica: pitagorica, 'mult-practica': multPractica,
    operaciones: operaciones, papel: papel,
    'sudoku-dibujos': sudokuDibujos, 'bingo-palabras': bingoPalabras, 'bingo-palabras-lista': bingoPalabrasLista,
    'laberinto-arbol': laberintoArbol, carta: carta, sobre: sobre, 'carta-respuesta': cartaRespuesta, crucigrama: crucigrama,
    'caligrafia-letras': caligrafiaLetras, 'caligrafia-frases': caligrafiaFrases, 'trazos-imprenta': trazosImprenta,
    multiplicaciones: multiplicaciones, divisiones: divisiones, mandala: mandala,
    grafomotricidad: grafomotricidad, horario: horario, 'calendario-anual': calendarioAnual, 'calendario-mes': calendarioMes, 'calendario-escolar': calendarioEscolar,
    problemas: problemas,
    cancelacion: cancelacion, refranes: refranes, series: series, compra: compra, fluidez: fluidez, orientacion: orientacion,
    ordenar: ordenar, clasificar: clasificar, copiar: copiar, iguales: iguales, contar: contar, colorear: colorear,
    tarjetas: tarjetas, 'bingo-sumas': bingoSumas, adviento: adviento, etiquetas: etiquetas, 'menu-fiesta': menuFiesta, 'lista-regalos': listaRegalos, 'amigo-invisible': amigoInvisible, receta: receta, 'lista-grupos': listaGrupos, sesion: sesion
  };
  // Tipos cuyo contenido cambia con la semilla (tienen botón «Otra distinta»)
  var ALEATORIOS = { sopa: 1, sudoku: 1, laberinto: 1, bingo90: 1, bingo75: 1, 'mult-practica': 1, operaciones: 1,
    'sudoku-dibujos': 1, 'bingo-palabras': 1, 'laberinto-arbol': 1, crucigrama: 1, 'caligrafia-frases': 1, multiplicaciones: 1, divisiones: 1, mandala: 1, problemas: 1,
    cancelacion: 1, refranes: 1, series: 1, compra: 1, fluidez: 1, ordenar: 1, clasificar: 1, copiar: 1, iguales: 1, contar: 1, colorear: 1, 'bingo-sumas': 1 };

  function render(spec, seed) {
    var fn = TIPOS[spec.tipo];
    if (!fn) throw new Error('Tipo de ficha desconocido: ' + spec.tipo);
    return fn(spec, seed >>> 0);
  }

  return { render: render, hash: hash, esAleatorio: function (spec) { return !!ALEATORIOS[spec.tipo] || (spec.tipo === 'tarjetas' && !!(spec.mezclar || spec.pares)); } };
});
