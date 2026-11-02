/* cuantosdiasfaltan.es: «¿A qué hora juega…?» en directo. La página trae el próximo partido de la última comprobación
   (cada mañana); al abrirla, esto lo consulta otra vez en ESPN para enseñar la hora recién publicada, si se juega ya y
   cómo va. Si ESPN no responde, se queda lo de la página. */
(function () {
  var caja = document.getElementById("vivo");
  if (!caja || !window.fetch || !window.Intl) return;
  var ESPN = "https://site.api.espn.com/apis/site/v2/sports";
  var RONDAS = { "Round 1": "primera ronda", "Round 2": "segunda ronda", "Round 3": "tercera ronda", "Round 4": "cuarta ronda",
    "Round of 16": "octavos de final", "Quarterfinal": "cuartos de final", "Semifinal": "semifinales", "Final": "final", "Round Robin": "fase de grupos" };

  function esc(t) { return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function fmt(fecha, zona, opciones) { return new Intl.DateTimeFormat("es-ES", Object.assign({ timeZone: zona }, opciones)).format(fecha); }
  function hora(fecha, zona) { return fmt(fecha, zona, { hour: "2-digit", minute: "2-digit" }); }
  function dia(fecha) {
    var hoy = fmt(new Date(), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" });
    var manana = fmt(new Date(Date.now() + 864e5), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" });
    var d = fmt(fecha, "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" });
    if (d === hoy) return "hoy";
    if (d === manana) return "mañana";
    return "el " + fmt(fecha, "Europe/Madrid", { weekday: "long" }) + " " + fmt(fecha, "Europe/Madrid", { day: "numeric", month: "long" });
  }
  function cuando(utc, valida) {
    var f = new Date(utc);
    return dia(f) + (valida ? " a las <strong>" + hora(f, "Europe/Madrid") + "</strong> en España (" + hora(f, "Atlantic/Canary") + " en Canarias)" : " (hora aún por confirmar)");
  }
  var frase = document.getElementById("vivo-frase");
  function pinta(html) { if (frase) frase.innerHTML = html + ' <small class="vivo-nota">Comprobado ahora mismo.</small>'; }
  function esHoy(utc) {
    return fmt(new Date(utc), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" }) === fmt(new Date(), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" });
  }

  function tenis(id) {
    fetch(ESPN + "/tennis/atp/scoreboard?lang=es&region=es").then(function (r) { return r.json(); }).then(function (d) {
      var lista = [];
      (d.events || []).forEach(function (ev) {
        (ev.groupings || []).forEach(function (g) {
          (g.competitions || []).forEach(function (c) {
            if (!c.type || c.type.slug !== "mens-singles") return;
            var yo = (c.competitors || []).filter(function (x) { return x.id === id; })[0];
            if (!yo) return;
            var otro = (c.competitors || []).filter(function (x) { return x !== yo; })[0] || {};
            var rival = (otro.athlete || {}).displayName || "";
            if (rival === "Bye") return;
            lista.push({ torneo: ev.name, c: c, yo: yo, otro: otro, rival: rival === "TBD" ? "" : rival });
          });
        });
      });
      var enJuego = lista.filter(function (p) { return p.c.status.type.state === "in"; })[0];
      var pend = lista.filter(function (p) { return p.c.status.type.state === "pre"; }).sort(function (a, b) { return a.c.date < b.c.date ? -1 : 1; })[0];
      var hoy = fmt(new Date(), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" });
      var acabado = lista.filter(function (p) { return p.c.status.type.state === "post" && fmt(new Date(p.c.date), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" }) === hoy; })[0];
      function sets(p) { return (p.yo.linescores || []).map(function (l, i) { return l.value + "-" + (((p.otro.linescores || [])[i] || {}).value || 0); }).join(" "); }
      function ronda(p) { var r = (p.c.round || {}).displayName || ""; return RONDAS[r] || r.toLowerCase(); }
      if (enJuego) pinta('<span class="vivo-ya">🔴 <strong>Está jugando ahora</strong></span> contra ' + esc(enJuego.rival) + ", en la " + esc(ronda(enJuego)) + " del " + esc(enJuego.torneo) + ": " + esc(sets(enJuego)) + ".");
      else if (acabado && !pend) pinta("<strong>Hoy " + (acabado.yo.winner ? "ha ganado" : "ha perdido") + "</strong> contra " + esc(acabado.rival) + " (" + esc(sets(acabado)) + "), en la " + esc(ronda(acabado)) + " del " + esc(acabado.torneo) + ".");
      else if (pend) pinta((esHoy(pend.c.date) ? "<strong>Hoy juega</strong>, " : "<strong>Hoy no juega.</strong> Su próximo partido es ") + cuando(pend.c.date, pend.c.timeValid)
        + (pend.rival ? ", contra <strong>" + esc(pend.rival) + "</strong>" : ", contra un rival aún por decidir") + ", en la " + esc(ronda(pend)) + " del " + esc(pend.torneo) + ".");
    }).catch(function () {});
  }

  function equipo(id) {
    fetch(ESPN + "/soccer/all/teams/" + id + "/schedule?fixture=true&lang=es&region=es").then(function (r) { return r.json(); }).then(function (d) {
      var ev = (d.events || []).filter(function (e) { var s = e.competitions[0].status.type.state; return s === "pre" || s === "in"; })
        .sort(function (a, b) { return a.date < b.date ? -1 : 1; })[0];
      if (!ev) return;
      var c = ev.competitions[0];
      var local = c.competitors.filter(function (x) { return x.homeAway === "home"; })[0];
      var fuera = c.competitors.filter(function (x) { return x.homeAway === "away"; })[0];
      function goles(x) { return x.score && typeof x.score === "object" ? x.score.displayValue : (x.score || "0"); }
      var liga = (ev.league || {}).name || "";
      if (c.status.type.state === "in") pinta('<span class="vivo-ya">🔴 <strong>Está jugando ahora</strong></span>: ' + esc(local.team.displayName) + " " + esc(goles(local)) + "-" + esc(goles(fuera)) + " " + esc(fuera.team.displayName) + " (" + esc(liga) + ").");
      else pinta((esHoy(ev.date) ? "<strong>Hoy juega</strong>: " : "<strong>Hoy no juega.</strong> Su próximo partido es ") + "<strong>" + esc(local.team.displayName) + " - " + esc(fuera.team.displayName) + "</strong> (" + esc(liga) + "), " + cuando(ev.date, c.timeValid) + ".");
    }).catch(function () {});
  }

  function tenisHoy() {
    // la sección del día de quien mira (la página se genera por la mañana: pasada la medianoche ya vale la de «mañana»)
    var hoy = fmt(new Date(), "Europe/Madrid", { year: "numeric", month: "2-digit", day: "2-digit" }).split("/").reverse().join("-");
    var dias = document.querySelectorAll(".tenis-dia");
    var hay = false;
    for (var i = 0; i < dias.length; i++) if (dias[i].dataset.dia === hoy) hay = true;
    if (hay) for (var j = 0; j < dias.length; j++) {
      dias[j].hidden = dias[j].dataset.dia !== hoy;
      var h2 = dias[j].querySelector("h2");
      if (h2 && dias[j].dataset.dia === hoy) h2.textContent = h2.textContent.replace(/^Mañana/, "Hoy");
    }
    function acabado(a, b) { return (Math.max(a, b) >= 6 && Math.abs(a - b) >= 2) || (Math.max(a, b) === 7 && Math.min(a, b) >= 5); }
    ["atp", "wta"].forEach(function (gira) {
      fetch(ESPN + "/tennis/" + gira + "/scoreboard?lang=es&region=es").then(function (r) { return r.json(); }).then(function (d) {
        (d.events || []).forEach(function (ev) {
          (ev.groupings || []).forEach(function (g) {
            (g.competitions || []).forEach(function (c) {
              var filas = document.querySelectorAll('tr[data-id="' + c.id + '"] .t-hora');
              if (!filas.length) return;
              var a = c.competitors[0] || {}, b = c.competitors[1] || {};
              var sets = (a.linescores || []).map(function (l, k) { return [l.value, ((b.linescores || [])[k] || {}).value || 0]; });
              var texto = sets.map(function (x) { return x[0] + "-" + x[1]; }).join(" ");
              var estado = c.status.type.state, html;
              if (estado === "in") html = '<span class="vivo-ya">🔴 ' + esc(texto || "En juego") + "</span>";
              else if (estado === "post") html = esc(texto + (sets.length && !acabado(sets[sets.length - 1][0], sets[sets.length - 1][1]) ? " (abandono)" : "")) || "Terminado";
              else html = c.timeValid ? hora(new Date(c.date), "Europe/Madrid") : "Por confirmar";
              for (var k = 0; k < filas.length; k++) filas[k].innerHTML = html;
            });
          });
        });
      }).catch(function () {});
    });
  }

  if (caja.dataset.tipo === "tenis") tenis(caja.dataset.id);
  else if (caja.dataset.tipo === "tenis-hoy") tenisHoy();
  else if (caja.dataset.tipo === "equipo") equipo(caja.dataset.id);
})();
