// Vídeos verticales (1080x1920) tipo «¿Qué fue antes?» para TikTok, Reels y Shorts, con el aspecto del juego.
// Cada ronda enseña dos hechos de data/hechos.json, una cuenta atrás y después los años, con el más antiguo en verde.
// Sin sonido: la música se elige en TikTok. El texto queda en el centro, lejos de los botones de la derecha y de abajo.
//
// Uso: node cronologia/marketing/video_quiz.js CARPETA_DE_SALIDA [nombre]
// Necesita Playwright (con Chromium), ffmpeg y la fuente Noto Color Emoji.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const RAIZ = path.join(__dirname, '..');
const hechos = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(RAIZ, 'data/hechos.json'), 'utf8')).map((h) => [h.slug, h]));

// Cada vídeo: gancho, rondas (pares de hechos) y cierre. Los años salen de hechos.json, ya comprobados con Wikipedia.
const VIDEOS = {
  '1-sorpresas': {
    gancho: ['¿Qué fue antes?', '4 preguntas. ¿Cuántas aciertas?'],
    rondas: [['primer-vuelo-wright', 'fundacion-real-madrid'], ['bombilla-edison', 'metro-londres'],
      ['primera-llamada-movil', 'primer-correo-electronico'], ['torre-eiffel', 'coca-cola']],
    cierre: ['Cada día, 6 momentos de la historia para ordenar', 'quefueantes.es']
  },
  '2-inventos': {
    gancho: ['¿Qué se inventó antes?', 'Si aciertas las 4, eres un reloj suizo'],
    rondas: [['primer-semaforo', 'coche-benz'], ['fregona', 'disneyland'], ['primer-sms', 'primera-web'], ['futbolin', 'monopoly']],
    cierre: ['Un reto nuevo cada día, gratis', 'quefueantes.es']
  },
  '3-espana': {
    gancho: ['¿Qué pasó antes en España?', '4 preguntas. ¿Cuántas aciertas?'],
    rondas: [['museo-prado', 'constitucion-cadiz'], ['tren-barcelona-mataro', 'telegrafo-morse'], ['coca-cola', 'sagrada-familia-obras'], ['fundacion-real-madrid', 'fundacion-fc-barcelona']],
    cierre: ['Un reto nuevo cada día, gratis', 'quefueantes.es']
  },
  '4-deporte': {
    gancho: ['¿Qué fue antes?', 'Edición deporte y espectáculo'],
    rondas: [['mundial-uruguay-1930', 'primeros-oscar'], ['juegos-olimpicos-atenas-1896', 'primera-sesion-cine'], ['llegada-luna', 'massiel-eurovision'], ['curiosity-marte', 'espana-campeona-mundial-2010']],
    cierre: ['¿Cuántas has acertado? Dímelo en comentarios', 'quefueantes.es']
  },
  '5-tecnologia': {
    gancho: ['¿Qué salió antes?', 'Si aciertas las 4, eres de la generación del Walkman'],
    rondas: [['primer-iphone', 'twitter'], ['fundacion-google', 'oveja-dolly'], ['primera-web', 'game-boy'], ['pac-man', 'walkman']],
    cierre: ['Cada día, 6 momentos de la historia para ordenar', 'quefueantes.es']
  },
  '6-cine-y-tele': {
    gancho: ['¿Qué fue antes?', 'Edición cine y tele'],
    rondas: [['constitucion-1978', 'star-wars'], ['primer-eurovision', 'disneyland'], ['barbie', 'primeras-emisiones-tve'], ['telescopio-hubble', 'los-simpson']],
    cierre: ['Un reto nuevo cada día, gratis', 'quefueantes.es']
  },
  '8-en-casa': {
    gancho: ['¿Qué llegó antes a casa?', 'Inventos de todos los días'],
    rondas: [['fregona', 'microondas'], ['bombilla-edison', 'patente-telefono'], ['coca-cola', 'vaqueros-levis'], ['tamagotchi', 'playstation']],
    cierre: ['Un reto nuevo cada día, gratis', 'quefueantes.es']
  },
  '7-antiguos': {
    gancho: ['¿Qué fue antes?', 'Nivel difícil: historia antigua'],
    rondas: [['gran-piramide-guiza', 'invencion-rueda'], ['fundacion-roma', 'primeros-juegos-olimpicos-antiguos'], ['erupcion-vesubio-pompeya', 'asesinato-julio-cesar'], ['invencion-papel', 'erupcion-vesubio-pompeya']],
    cierre: ['¿Te atreves con el reto de hoy?', 'quefueantes.es']
  }
};

const FPS = 30, GANCHO = 2.2, RONDA = 4.6, CIERRE = 3.4;
const fuentes = (n, w) => `@font-face{font-family:${n};font-weight:${w};src:url(file://${RAIZ}/plantilla/fuentes/${n.toLowerCase()}-${w}-latin.woff2) format('woff2');unicode-range:U+0000-00FF}`
  + `@font-face{font-family:${n};font-weight:${w};src:url(file://${RAIZ}/plantilla/fuentes/${n.toLowerCase()}-${w}-latin-ext.woff2) format('woff2')}`;

function html(v) {
  const tic = fs.readFileSync(path.join(RAIZ, 'plantilla/tic.svg'), 'utf8');
  const horizonte = fs.readFileSync(path.join(RAIZ, 'plantilla/horizonte.svg'), 'utf8');
  const datos = {
    gancho: v.gancho, cierre: v.cierre,
    rondas: v.rondas.map((par) => par.map((s) => {
      const h = hechos[s];
      if (!h) throw new Error('No existe el hecho ' + s);
      return { e: h.emoji, t: h.tarjeta, a: h.anio, y: h.anio_texto || String(h.anio) };
    }))
  };
  return `<!doctype html><meta charset="utf-8"><style>
${fuentes('Fredoka', 600)}${fuentes('Fredoka', 700)}${fuentes('Nunito', 800)}${fuentes('Nunito', 900)}
:root{--oro:#ffcf6b;--crema:#fff6ea;--tinta:#3a1d47;--sil:#3a1d47;--verde:#2fb47c;--rojo:#e5484d}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;overflow:hidden}
body{font-family:Nunito,'Noto Color Emoji',sans-serif;font-weight:800;color:#fff;
 background:linear-gradient(180deg,#2b1748 0%,#5b2a66 46%,#c8634c 82%,#f2a65a 100%);position:relative}
.sol{position:absolute;left:50%;top:1250px;width:1100px;height:1100px;margin-left:-550px;border-radius:50%;
 background:radial-gradient(circle,rgba(255,214,140,.95) 0%,rgba(255,170,90,.55) 32%,rgba(255,150,80,0) 68%)}
.horizonte{position:absolute;left:-380px;bottom:40px;width:1840px;height:auto;color:var(--sil)}.horizonte .sil{fill:var(--sil)}.horizonte .humo{opacity:.45}
.suelo{position:absolute;left:0;right:0;bottom:0;height:60px;background:var(--sil)}
.tic{position:absolute;left:50%;bottom:70px;width:170px;margin-left:-85px}.tic .cejas-triste,.tic .boca-triste{display:none}
.marca{position:absolute;top:150px;left:0;right:0;text-align:center;font:700 64px Fredoka,sans-serif;color:var(--oro)}
.capa{position:absolute;left:80px;right:140px;top:420px;display:flex;flex-direction:column;align-items:stretch;gap:44px}
.grande{font:700 118px/1.05 Fredoka,sans-serif;color:var(--oro);text-align:center;text-shadow:0 6px 0 rgba(0,0,0,.18)}
.sub{font-size:60px;text-align:center;line-height:1.25}
.num{font-size:44px;text-align:center;color:var(--oro);letter-spacing:.06em}
.tarjeta{background:var(--crema);color:var(--tinta);border-radius:44px;padding:52px 44px;display:flex;align-items:center;gap:30px;
 box-shadow:0 12px 0 rgba(0,0,0,.18);border:6px solid transparent;position:relative}
.tarjeta .em{font-size:112px;line-height:1;font-family:'Noto Color Emoji'}
.tarjeta .tx{font-size:60px;line-height:1.15;flex:1}
.tarjeta .ano{position:absolute;right:28px;top:-34px;background:var(--tinta);color:#fff;font:700 50px Fredoka,sans-serif;border-radius:999px;padding:6px 26px}
.tarjeta.gana{border-color:var(--verde);background:#e6f8ef}
.tarjeta.gana::after{content:'ANTES ✓';position:absolute;left:28px;top:-34px;background:var(--verde);color:#fff;font:700 44px Fredoka,sans-serif;border-radius:999px;padding:8px 26px}
.o{font:700 90px/1 Fredoka,sans-serif;text-align:center;color:var(--oro);margin:-10px 0}
.barra{height:22px;border-radius:11px;background:rgba(255,255,255,.18);overflow:hidden}.barra i{display:block;height:100%;background:var(--oro);border-radius:11px}
.web{align-self:center;background:var(--oro);color:var(--tinta);font:700 78px Fredoka,sans-serif;border-radius:999px;padding:18px 54px}
</style><body><div class="sol"></div>${horizonte}<div class="suelo"></div><div class="tic">${tic}</div>
<div class="marca">¿Qué fue antes?</div><div class="capa" id="capa"></div>
<script>
const D=${JSON.stringify(datos)}, GANCHO=${GANCHO}, RONDA=${RONDA}, CIERRE=${CIERRE};
const esc=(s)=>String(s).replace(/[&<>"]/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]);
const suave=(x)=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const entra=(t,d)=>{const k=suave((t-d)/.35);return 'opacity:'+k+';transform:translateY('+((1-k)*60)+'px)'};
function tarjeta(c,t,d,revela,gana){return '<div class="tarjeta'+(revela&&gana?' gana':'')+'" style="'+entra(t,d)+'"><span class="em">'+c.e+'</span><span class="tx">'+esc(c.t)+'</span>'+(revela?'<b class="ano">'+esc(c.y)+'</b>':'')+'</div>'}
window.pintar=function(t){
  const capa=document.getElementById('capa');let h='';
  if(t<GANCHO){h='<div class="grande" style="'+entra(t,0)+'">'+esc(D.gancho[0])+'</div><div class="sub" style="'+entra(t,.5)+'">'+esc(D.gancho[1])+'</div>';}
  else if(t<GANCHO+RONDA*D.rondas.length){
    const r=Math.floor((t-GANCHO)/RONDA),tt=(t-GANCHO)-r*RONDA,[a,b]=D.rondas[r],revela=tt>=3.0,cuenta=Math.max(0,Math.min(1,(tt-.6)/2.4));
    h='<div class="num" style="'+entra(tt,0)+'">PREGUNTA '+(r+1)+' DE '+D.rondas.length+'</div>'+tarjeta(a,tt,.1,revela,a.a<b.a)+'<div class="o" style="'+entra(tt,.25)+'">¿o?</div>'+tarjeta(b,tt,.4,revela,b.a<a.a)
      +'<div class="barra" style="'+entra(tt,.5)+';visibility:'+(revela?'hidden':'visible')+'"><i style="width:'+((1-cuenta)*100)+'%"></i></div>';
  } else {const tt=t-GANCHO-RONDA*D.rondas.length;h='<div class="sub" style="'+entra(tt,0)+'">'+esc(D.cierre[0])+'</div><div class="web" style="'+entra(tt,.5)+'">'+esc(D.cierre[1])+'</div>';}
  capa.innerHTML=h;
};
window.duracion=GANCHO+RONDA*D.rondas.length+CIERRE;
</script>`;
}

(async () => {
  const salida = path.resolve(process.argv[2] || '.');
  fs.mkdirSync(salida, { recursive: true });
  const nombres = process.argv[3] ? [process.argv[3]] : Object.keys(VIDEOS);
  const nav = await chromium.launch();
  for (const n of nombres) {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'qfa-'));
    const pag = await nav.newPage({ viewport: { width: 1080, height: 1920 } });
    fs.writeFileSync(path.join(tmp, 'v.html'), html(VIDEOS[n]));
    await pag.goto('file://' + path.join(tmp, 'v.html'));
    await pag.evaluate(() => document.fonts.ready);
    const dur = await pag.evaluate(() => window.duracion);
    const total = Math.round(dur * FPS);
    for (let i = 0; i < total; i++) {
      await pag.evaluate((t) => window.pintar(t), i / FPS);
      await pag.screenshot({ path: path.join(tmp, String(i).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 90 });
    }
    await pag.close();
    const mp4 = path.join(salida, 'quefueantes-' + n + '.mp4');
    execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', path.join(tmp, '%05d.jpg'),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', mp4]);
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log(mp4, Math.round(dur) + ' s');
  }
  await nav.close();
})();
