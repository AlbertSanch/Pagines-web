/* «¿Más o menos?»: juego diario de cuantossellaman.es. Cada día, la misma partida para todo el mundo. */
(function () {
  var RONDAS = 10;
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('juego');
  if (!raiz) return;
  function n(x) { return String(x).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function txt(s) { var e = document.createElement('span'); e.textContent = s; return e.innerHTML; }
  function leer(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sin almacenamiento: se juega igual */ } }
  // Generador de números con semilla: la misma partida para todos el mismo día
  function azar(semilla) {
    return function () {
      semilla |= 0; semilla = semilla + 0x6D2B79F5 | 0;
      var t = Math.imul(semilla ^ semilla >>> 15, 1 | semilla);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function hoyLocal() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  function isoDia(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }

  fetch('/datos/juego.json').then(function (r) { return r.json(); }).then(function (datos) {
    var p = datos.inicio.split('-'), inicio = new Date(+p[0], +p[1] - 1, +p[2]), hoy = hoyLocal();
    var numero = Math.max(1, Math.round((hoy - inicio) / 864e5) + 1), dia = isoDia(hoy);
    var r = azar(numero * 7919 + 17), lista = datos.n, cadena = [], usados = {};
    var x = lista[Math.floor(r() * lista.length)];
    cadena.push(x); usados[x[0]] = 1;
    while (cadena.length < RONDAS + 1) {
      var y = lista[Math.floor(r() * lista.length)], a = cadena[cadena.length - 1][1], ratio = Math.max(a, y[1]) / Math.min(a, y[1]);
      if (usados[y[0]] || ratio < 1.15) continue;  // sin repetir y sin cifras casi iguales
      cadena.push(y); usados[y[0]] = 1;
    }

    var partida = leer('juego-partida');
    if (!partida || partida.dia !== dia) partida = { dia: dia, res: [] };
    $('juego-numero').textContent = '#' + numero;

    function pintarRonda() {
      var i = partida.res.length;
      if (i >= RONDAS) return final();
      var a = cadena[i], b = cadena[i + 1];
      raiz.innerHTML =
        '<p class="j-progreso">Ronda ' + (i + 1) + ' de ' + RONDAS + ' <span>' + partida.res.map(function (ok) { return ok ? '🟩' : '🟥'; }).join('') + '</span></p>' +
        '<div class="j-cartas">' +
        '<div class="j-carta"><span class="j-nombre">' + txt(a[0]) + '</span><span class="j-cifra">' + n(a[1]) + '</span><small>personas en España</small></div>' +
        '<div class="j-vs">vs</div>' +
        '<div class="j-carta j-pregunta"><span class="j-nombre">' + txt(b[0]) + '</span><span class="j-cifra" id="j-cifra">?</span><small>¿más o menos personas?</small>' +
        '<div class="j-botones"><button type="button" class="btn" data-r="1">▲ Más</button><button type="button" class="btn" data-r="0">▼ Menos</button></div></div>' +
        '</div><p class="j-mensaje" id="j-mensaje" aria-live="polite"></p>';
      raiz.querySelectorAll('[data-r]').forEach(function (bt) {
        bt.addEventListener('click', function () { responder(bt.getAttribute('data-r') === '1', a, b); });
      });
    }

    function responder(mas, a, b) {
      var ok = mas === (b[1] > a[1]);
      raiz.querySelectorAll('[data-r]').forEach(function (bt) { bt.disabled = true; });
      var el = $('j-cifra'), t0 = null, dur = 700;
      function paso(t) {
        if (!t0) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        el.textContent = n(Math.round(b[1] * k));
        if (k < 1) requestAnimationFrame(paso);
      }
      requestAnimationFrame(paso);
      raiz.querySelector('.j-pregunta').classList.add(ok ? 'j-bien' : 'j-mal');
      $('j-mensaje').textContent = (ok ? '¡Bien! ' : 'Casi… ') + n(b[1]) + ' personas se llaman ' + b[0] + ': ' +
        (b[1] > a[1] ? 'más' : 'menos') + ' que ' + a[0] + '.';
      partida.res.push(ok);
      guardar('juego-partida', partida);
      setTimeout(pintarRonda, 1900);
    }

    function final() {
      var aciertos = partida.res.filter(Boolean).length, cuadros = partida.res.map(function (ok) { return ok ? '🟩' : '🟥'; }).join('');
      var racha = leer('juego-racha') || { ultimo: null, dias: 0, mejor: 0 };
      if (racha.ultimo !== dia) {
        var ayer = new Date(hoy.getTime() - 864e5);
        racha.dias = racha.ultimo === isoDia(ayer) ? racha.dias + 1 : 1;
        racha.mejor = Math.max(racha.mejor || 0, racha.dias);
        racha.ultimo = dia;
        guardar('juego-racha', racha);
      }
      var url = location.origin + '/juego/';
      var texto = '¿Más o menos? #' + numero + ' · ' + aciertos + '/' + RONDAS + '\n' + cuadros + '\n' + url;
      var frase = aciertos === RONDAS ? '¡Perfecto! Te sabes los nombres de España de memoria.' : aciertos >= 8 ? '¡Muy bien!' : aciertos >= 5 ? 'Nada mal.' : 'Los nombres engañan…';
      raiz.innerHTML =
        '<div class="j-final"><p class="j-nota">' + aciertos + '/' + RONDAS + '</p><p class="j-cuadros">' + cuadros + '</p><p>' + frase + '</p>' +
        '<p class="j-racha">🔥 Racha: ' + racha.dias + (racha.dias === 1 ? ' día' : ' días') + ' · Mejor racha: ' + racha.mejor + '</p>' +
        '<div class="compartir"><span>Compártelo:</span>' +
        '<a class="btn-c wa" href="https://wa.me/?text=' + encodeURIComponent(texto) + '" target="_blank" rel="noopener">WhatsApp</a>' +
        '<button type="button" class="btn-c" id="j-copiar">Copiar resultado</button></div>' +
        '<p class="j-manana">Vuelve mañana para el juego #' + (numero + 1) + '.</p>' +
        '<h3>Los nombres de hoy</h3><ol class="j-nombres">' + cadena.map(function (c) {
          return '<li><a href="/nombre/' + c[2] + '/">' + txt(c[0]) + '</a> <small>' + n(c[1]) + '</small></li>';
        }).join('') + '</ol></div>';
      $('j-copiar').addEventListener('click', function (e) {
        var b = e.currentTarget;
        (navigator.clipboard ? navigator.clipboard.writeText(texto) : Promise.reject()).then(function () { b.textContent = '¡Copiado!'; },
          function () { window.prompt('Copia tu resultado:', texto); });
      });
    }

    pintarRonda();
  });
})();
