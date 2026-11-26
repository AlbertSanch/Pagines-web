// Calendario escolar para imprimir, una página por comunidad (o por provincia donde cada una tiene el suyo).
// Datos: scripts/calendarios_escolares.py, a partir del calendario escolar oficial que usa festivosde.es
// (festivos/data/escolar.json, sacado de la orden o resolución de cada territorio).
const D = require('./datos/escolar-2026-2027.json');
const CURSO = D.curso;
const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const ABR = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];
const dia = (iso) => new Date(iso + 'T12:00:00Z');
const larga = (iso) => { const d = dia(iso); return `${DIAS[d.getUTCDay()]} ${d.getUTCDate()} de ${MESES[d.getUTCMonth()]}`; };
const corta = (iso) => { const d = dia(iso); return `${ABR[d.getUTCDay()]} ${d.getUTCDate()} ${MESES[d.getUTCMonth()].slice(0, 3)}`; };
const dm = (iso) => { const d = dia(iso); return `${d.getUTCDate()} ${MESES[d.getUTCMonth()].slice(0, 3)}`; };
const rango = (a, b) => `del ${larga(a)} al ${larga(b)}`;
const lista = (l) => l.length < 2 ? l.join('') : l.slice(0, -1).join(', ') + ' y ' + l[l.length - 1];
const CORTO = { 'Comunidad de Madrid': 'Madrid', 'Comunitat Valenciana': 'Valencia', 'Illes Balears': 'Baleares', 'Región de Murcia': 'Murcia' };
const AMAZON = [['Agendas escolares 2026-2027', 'agenda escolar 2026 2027'], ['Calendarios de pared', 'calendario pared 2027'], ['Cartulina blanca A4 para imprimir', 'cartulina blanca A4 impresora']];
const URL = (t) => `/calendarios/escolar-${CURSO}-${t.slug}/`;
const breve = (t) => CORTO[t.nombre] || t.nombre;
// días lectivos (de lunes a viernes, entre el primer y el último día, sin marcas)
const lectivos = (t) => {
  let n = 0;
  for (let d = dia(t.inicio); d <= dia(t.fin); d.setUTCDate(d.getUTCDate() + 1)) {
    const iso = d.toISOString().slice(0, 10), w = d.getUTCDay();
    if (w > 0 && w < 6 && !t.marcas[iso]) n++;
  }
  return n;
};
// días no lectivos seguidos agrupados («7 y 8 ene»)
const agrupar = (fechas) => {
  const grupos = [];
  fechas.forEach((f) => {
    const g = grupos[grupos.length - 1];
    if (g && (dia(f) - dia(g[g.length - 1])) / 864e5 === 1) g.push(f); else grupos.push([f]);
  });
  return grupos;
};

function clave(t) {
  const l = [`Empiezan las clases: ${corta(t.inicio)}`];
  t.vacaciones.forEach(([n, a, b]) => l.push(`${n}: ${dm(a)} - ${dm(b)}`));
  const nl = t.no_lectivos.filter((x) => !t.vacaciones.some(([, a, b]) => x[0] >= a && x[0] <= b)).map((x) => x[0]);
  if (nl.length) l.push('No lectivos: ' + agrupar(nl).map((g) => g.length > 2 ? `${dm(g[0])} - ${dm(g[g.length - 1])}` : g.map(dm).join(', ')).join(', '));
  l.push(`Último día de clase: ${corta(t.fin)}`);
  return l;
}

function pagina(t) {
  const nom = breve(t);
  const art = /^(Comunidad|Comunitat|Región)/.test(t.nombre) ? 'la ' : t.nombre === 'País Vasco' ? 'el ' : '';
  const de = t.es_provincia ? `de ${t.nombre} (${t.comunidad})` : art === 'el ' ? `del ${t.nombre}` : `de ${art}${t.nombre}`;
  const en = t.es_provincia ? `en la provincia de ${t.nombre}` : `en ${art}${t.nombre}`;
  const n = lectivos(t);
  const navidad = t.vacaciones.find((v) => /navidad/i.test(v[0]));
  const santa = t.vacaciones.find((v) => /santa|pascua/i.test(v[0]));
  const otrasVac = t.vacaciones.filter((v) => v !== navidad && v !== santa);
  const nl = t.no_lectivos.filter((x) => !t.vacaciones.some(([, a, b]) => x[0] >= a && x[0] <= b));
  const fest = t.festivos.filter(([f]) => f >= t.inicio && f <= t.fin && dia(f).getUTCDay() % 6 !== 0);
  const otros = D.territorios.filter((x) => x.ccaa === t.ccaa && x !== t);
  const titulos = [`Calendario escolar ${CURSO} ${nom} para imprimir`, `Calendario escolar ${CURSO} ${nom} (PDF)`, `Calendario escolar ${CURSO} ${nom}`];
  const desc = [
    `Calendario escolar ${CURSO} ${de} para imprimir en A4: inicio de curso, vacaciones de Navidad y Semana Santa y días sin clase marcados. PDF gratis.`,
    `Calendario escolar ${CURSO} ${de} para imprimir: inicio de curso, vacaciones y días sin clase marcados en una hoja A4. PDF gratis.`,
    `Calendario escolar ${CURSO} ${de} para imprimir en una hoja A4, con vacaciones y días sin clase marcados. PDF gratis.`
  ].find((x) => x.length <= 158);
  return {
    cat: 'calendarios', slug: `escolar-${CURSO}-${t.slug}`, corto: `Calendario escolar ${de}`,
    title: titulos.find((x) => x.length <= 60),
    desc,
    h1: `Calendario escolar ${CURSO} ${de} para imprimir`,
    entrada: `El curso ${CURSO} ${en} en una hoja A4, de septiembre a junio: las clases empiezan el ${larga(t.inicio)} de 2026 y terminan el ${larga(t.fin)} de 2027. Las vacaciones van en verde, los días no lectivos en naranja y los festivos con un círculo rojo. Son las fechas de ${t.etapas}.`,
    hojas: [{ tipo: 'calendario-escolar', curso: CURSO, inicio: t.inicio, fin: t.fin, marcas: t.marcas, region: t.nombre, clave: clave(t),
      nota: 'Fiestas locales no incluidas: cada municipio tiene dos más, que también son días sin clase.' }],
    copias: 1,
    amazon: AMAZON,
    cuerpo: `
<h2>Fechas del curso ${CURSO} ${en}</h2>
<ul>
<li><strong>Primer día de clase</strong>: ${larga(t.inicio)} de 2026 (${t.etapas}).${t.otras_etapas.map(([e, f]) => ` ${e}: ${larga(f)}.`).join('')}</li>
${navidad ? `<li><strong>Vacaciones de Navidad</strong>: ${rango(navidad[1], navidad[2])}, ambos incluidos.</li>` : ''}
${santa ? `<li><strong>Vacaciones de ${santa[0]}</strong>: ${rango(santa[1], santa[2])}.</li>` : ''}
${otrasVac.map(([v, a, b]) => `<li><strong>${v}</strong>: ${a === b ? larga(a) : rango(a, b)}.</li>`).join('\n')}
<li><strong>Último día de clase</strong>: ${larga(t.fin)} de 2027.</li>
</ul>
<p>Quedan unos <strong>${n} días lectivos</strong> de lunes a viernes, sin contar las fiestas locales.</p>
${nl.length ? `<h2>Días no lectivos</h2>
<p>Además de las vacaciones, no hay clase estos días:</p>
<ul>
${nl.map(([f, m]) => `<li>${larga(f)} de ${f.slice(0, 4)}${m && m !== 'Otro día no lectivo' ? `: ${m}` : ''}</li>`).join('\n')}
</ul>` : ''}
${fest.length ? `<h2>Festivos durante el curso</h2>
<p>Los festivos nacionales y autonómicos que caen entre semana durante el curso:</p>
<ul>
${fest.map(([f, m]) => `<li>${larga(f)} de ${f.slice(0, 4)}: ${m}</li>`).join('\n')}
</ul>` : ''}
<h2>Y las fiestas locales</h2>
<p>${t.locales ? t.locales + ' ' : ''}Las fiestas locales de tu municipio no salen en el calendario porque cambian de un pueblo a otro. Las puedes consultar en los <a href="https://festivosde.es/comunidad/${t.ccaa}/">festivos de ${t.comunidad} en festivosde.es</a> y apuntarlas a mano.</p>
<h2>De dónde salen las fechas</h2>
<p>Del calendario escolar oficial: ${t.url ? `<a href="${t.url}" rel="nofollow">${t.norma}</a>` : t.norma}. Si tu centro tiene días de libre disposición, el colegio los comunica a las familias a principio de curso. También tienes el <a href="https://festivosde.es/calendario-escolar/${t.ccaa}/">calendario escolar ${CURSO} de ${t.comunidad}</a> en festivosde.es, con la cuenta atrás para las vacaciones.</p>
${otros.length ? `<p>¿Otra provincia de ${t.comunidad}? ${lista(otros.map((x) => `<a href="${URL(x)}">${x.nombre}</a>`))}.</p>` : ''}
<h2>Cómo imprimirlo</h2>
<p>Está pensado para A4 vertical. Los festivos llevan un círculo y el primer y último día un recuadro, así que se distinguen también en blanco y negro. Para la nevera, imprímelo en cartulina; para la agenda escolar, al 70 %. Los calendarios de todas las comunidades están en el <a href="/calendarios/escolar-${CURSO}/">calendario escolar ${CURSO} para imprimir</a>.</p>`,
    faq: [
      [`¿Cuándo empiezan las clases ${en} en el curso ${CURSO}?`, `El ${larga(t.inicio)} de 2026 en ${t.etapas}.${t.otras_etapas.map(([e, f]) => ` En ${e}, el ${larga(f)}.`).join('')}`],
      ...(navidad ? [[`¿Cuándo son las vacaciones de Navidad?`, `${rango(navidad[1], navidad[2]).replace(/^d/, 'D')}.`]] : []),
      [`¿Cuándo acaba el curso?`, `El ${larga(t.fin)} de 2027 es el último día de clase.`]
    ]
  };
}

const ccaa = [...new Set(D.territorios.map((t) => t.comunidad))];
const hub = {
  cat: 'calendarios', slug: `escolar-${CURSO}`, corto: `Calendario escolar ${CURSO}`,
  title: `Calendario escolar ${CURSO} para imprimir (PDF gratis)`,
  desc: `Calendario escolar ${CURSO} para imprimir de cada comunidad: inicio de curso, vacaciones de Navidad y Semana Santa y días sin clase. PDF gratis en A4.`,
  h1: `Calendario escolar ${CURSO} para imprimir`,
  entrada: `Elige tu comunidad (o tu provincia) y descarga su calendario escolar ${CURSO} en una hoja A4, de septiembre a junio, con las vacaciones, los días no lectivos y los festivos ya marcados. Aquí abajo tienes también uno en blanco, con solo los festivos nacionales, para rellenar con las fechas de tu colegio.`,
  hojas: [{ tipo: 'calendario-escolar', curso: CURSO, marcas: Object.fromEntries(D.nacionales.filter(([f]) => dia(f).getUTCDay() % 6 !== 0).map(([f, n]) => [f, ['fest', n]])),
    clave: ['Empiezan las clases:', '', 'Navidad:', '', 'Semana Santa:', '', 'Último día:'], nota: 'Solo festivos nacionales. Apunta las vacaciones y los días no lectivos de tu colegio.' }],
  copias: 1,
  amazon: AMAZON,
  cuerpo: `
<h2>Calendario escolar ${CURSO} por comunidades</h2>
<ul>
${ccaa.map((c) => { const ts = D.territorios.filter((t) => t.comunidad === c); return ts.length === 1 && !ts[0].es_provincia ? `<li><a href="${URL(ts[0])}">${c}</a>: del ${dm(ts[0].inicio)} al ${dm(ts[0].fin)}</li>` : `<li>${c}: ${lista(ts.map((t) => `<a href="${URL(t)}">${t.nombre}</a>`))}</li>`; }).join('\n')}
</ul>
<p>En Andalucía, Aragón y Castilla-La Mancha cada provincia aprueba su propio calendario, por eso hay uno por provincia. Todavía faltan ${lista(D.pendientes)}: los añadiremos cuando tengamos las fechas oficiales completas. Mientras, las tienes en el <a href="https://festivosde.es/calendario-escolar/">calendario escolar ${CURSO} de festivosde.es</a>.</p>
<h2>Qué trae cada calendario</h2>
<p>Los diez meses del curso en una sola hoja, con la semana empezando en lunes. Las vacaciones de Navidad y Semana Santa van en verde, los días no lectivos en naranja, los festivos con un círculo rojo y el primer y último día de clase con un recuadro. En los dos huecos de abajo, la leyenda y las fechas clave escritas. Las fechas son las de Infantil y Primaria; en la página de cada comunidad se indica si ESO y Bachillerato empiezan otro día.</p>
<p>Las fiestas locales no van marcadas, porque cada municipio tiene las suyas. Puedes buscar las de tu pueblo en <a href="https://festivosde.es/">festivosde.es</a> y apuntarlas a mano.</p>
<p>Si quieres organizar también la semana, tienes el <a href="/papel/horario-escolar/">horario escolar para imprimir</a>, y para el año natural, el <a href="/calendarios/">calendario 2027</a>.</p>`,
  faq: [
    [`¿Cuándo empieza el curso ${CURSO}?`, `Entre el ${dia(D.territorios.map((t) => t.inicio).sort()[0]).getUTCDate()} y el ${dia(D.territorios.map((t) => t.inicio).sort().pop()).getUTCDate()} de septiembre de 2026, según la comunidad.`],
    ['¿Por qué no salen las fiestas locales?', 'Porque las fija cada ayuntamiento y cambian de un municipio a otro. Son días sin clase, así que conviene apuntarlas a mano.']
  ]
};

module.exports = [hub, ...D.territorios.map(pagina)];
