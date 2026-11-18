// Calendarios para imprimir. Festivos nacionales de 2027 según la Resolución de 8 de octubre de 2026
// de la Dirección General de Trabajo (BOE-A-2026-21254), los mismos datos que usa festivosde.es
// (festivos/data/festivos_2027.json): solo los que son festivo en todas las comunidades.

const ANIO = 2027;
// Festivos de cada comunidad: los prepara scripts/calendarios_ccaa.py a partir de festivos/data/festivos_2027.json
const DATOS = require('./datos/festivos-2027.json');
const festivos = DATOS.nacional;
const meses = (desde, hasta, fest = festivos) => Array.from({ length: hasta - desde }, (_, i) => ({ tipo: 'calendario-mes', anio: ANIO, mes: desde + i, festivos: fest }));
const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const fecha = (k) => { const m = Number(k.slice(0, 2)) - 1, d = Number(k.slice(3)); return `${DIAS[new Date(Date.UTC(ANIO, m, d)).getUTCDay()]} ${d} de ${MESES[m]}`; };
const CORTO = { madrid: 'Madrid', murcia: 'Murcia', baleares: 'Baleares' };
const AMAZON = [['Calendarios de pared 2027', 'calendario pared 2027'], ['Agendas 2027', 'agenda 2027'], ['Cartulina blanca A4 para imprimir', 'cartulina blanca A4 impresora']];
const lista = (l) => l.length < 2 ? l.join('') : l.slice(0, -1).join(', ') + ' y ' + l[l.length - 1];

const notaFestivos = `
<h2>Los festivos que vienen marcados</h2>
<p>En rojo están los domingos y los nueve festivos nacionales que en ${ANIO} son fiesta en todas las comunidades autónomas: 1 de enero (Año Nuevo), 6 de enero (Reyes), 26 de marzo (Viernes Santo), 1 de mayo (Fiesta del Trabajo), 12 de octubre (Fiesta Nacional), 1 de noviembre (Todos los Santos), 6 de diciembre (Constitución), 8 de diciembre (Inmaculada) y 25 de diciembre (Navidad). Están tomados de la resolución de fiestas laborales para ${ANIO} publicada en el BOE el 13 de octubre de 2026.</p>
<p>No están marcados el Jueves Santo (25 de marzo), que es festivo en casi todas las comunidades pero no en todas, ni el 15 de agosto, que en ${ANIO} cae en domingo y algunas comunidades trasladan al lunes 16. Tampoco los festivos autonómicos ni los dos locales de cada municipio. Para el calendario completo de tu localidad, con todos sus festivos, tienes el <a href="https://festivosde.es/calendario-laboral-para-imprimir/">calendario laboral ${ANIO} para imprimir de festivosde.es</a>, donde eliges tu municipio.</p>`;

module.exports = [
  {
    cat: 'calendarios', slug: '', corto: 'Calendarios', nav: 'Calendarios',
    resumen: 'Calendario 2027 anual y mensual',
    title: `Calendario ${ANIO} para imprimir con festivos (PDF gratis)`,
    desc: `Calendario ${ANIO} para imprimir en una hoja A4, con los festivos nacionales marcados y la semana empezando en lunes. También mensual, mes a mes. PDF gratis.`,
    h1: `Calendario ${ANIO} para imprimir`,
    entrada: `Los doce meses de ${ANIO} en una sola hoja A4, con la semana empezando en lunes, los domingos en rojo y los festivos nacionales marcados con un círculo. Debajo, la lista de festivos. Si prefieres un mes por hoja con espacio para apuntar, tienes el <a href="/calendarios/mensual-${ANIO}/">calendario mensual ${ANIO}</a>.`,
    hojas: [{ tipo: 'calendario-anual', anio: ANIO, festivos }],
    excel: `/pdf/calendario-${ANIO}.xlsx`,
    copias: 1,
    amazon: AMAZON,
    cuerpo: notaFestivos + `
<h2>Calendario 2027 de tu comunidad</h2>
<p>Este calendario lleva los festivos que son fiesta en toda España. Si quieres también los de tu comunidad autónoma, tienes uno para cada una, con sus festivos marcados y en PDF y Excel: ${Object.entries(DATOS.comunidades).map(([k, c]) => `<a href="/calendarios/${ANIO}-${k}/">${c.nombre}</a>`).join(', ')}.</p>
<h2>Cómo imprimirlo</h2>
<p>Está pensado para A4 vertical y se imprime bien en blanco y negro: los festivos llevan un círculo además del color, así que se distinguen igual en una impresora sin tinta roja. Si lo quieres más grande para la pared, imprímelo en A3 eligiendo «Ajustar al papel»; las proporciones se mantienen.</p>
<p>Para la nevera o un tablón, imprime en cartulina de 160 a 200 gramos. Para la agenda, imprime al 70 % y quedará del tamaño de una hoja A5.</p>
<h2>Algunas fechas de ${ANIO}</h2>
<ul>
<li>La Semana Santa cae a finales de marzo: el Jueves Santo es el 25 y el Viernes Santo, el 26; el Domingo de Resurrección, el 28 de marzo.</li>
<li>El 15 de agosto es domingo, así que en muchas comunidades no habrá festivo entre semana ese mes.</li>
<li>El puente de diciembre cae de lunes a miércoles: el 6 (lunes) y el 8 (miércoles) son festivos, y el martes 7 queda en medio. En festivosde.es tienes los <a href="https://festivosde.es/puentes-2027/">puentes de ${ANIO}</a> con más detalle.</li>
</ul>
<h2>¿Buscas el calendario escolar?</h2>
<p>Las fechas de inicio de curso y vacaciones cambian en cada comunidad. Las tienes en el <a href="https://festivosde.es/calendario-escolar/">calendario escolar 2026-2027 por comunidades</a> de festivosde.es.</p>`,
    faq: [
      [`¿En qué día de la semana empieza ${ANIO}?`, `El 1 de enero de ${ANIO} es viernes. El año no es bisiesto: febrero tiene 28 días.`],
      ['¿Por qué la semana empieza en lunes?', 'Porque es lo habitual en España y en la mayoría de Europa, según la norma ISO 8601. Los calendarios que empiezan en domingo son de tradición estadounidense.']
    ]
  },
  {
    cat: 'calendarios', slug: `mensual-${ANIO}`, corto: `Calendario mensual ${ANIO}`,
    title: `Calendario mensual ${ANIO} para imprimir (PDF)`,
    desc: `Calendario mensual ${ANIO} para imprimir: un mes por hoja A4 con casillas grandes para apuntar y los festivos nacionales marcados. Los 12 meses en PDF.`,
    h1: `Calendario mensual ${ANIO} para imprimir`,
    entrada: `Un mes por hoja, con casillas grandes para apuntar citas, cumpleaños o tareas, la semana empezando en lunes y los festivos nacionales marcados con su nombre. En pantalla ves enero y febrero; el PDF trae los doce meses de ${ANIO}.`,
    hojas: meses(0, 2),
    pdfExtra: meses(2, 12),
    copias: 1,
    amazon: AMAZON,
    cuerpo: `
<h2>Para qué sirve un calendario mes a mes</h2>
<p>Cada casilla mide unos 2,5 × 3,5 centímetros, sitio suficiente para dos o tres anotaciones a mano. Es el formato de los calendarios de cocina: se cuelga en la nevera o en un tablón y toda la familia apunta allí las citas médicas, las excursiones del colegio o los turnos de trabajo.</p>
<p>También funciona como planificador: imprime solo el mes en curso, apunta los plazos y las fechas importantes y tenlo a la vista junto al escritorio. Si necesitas organizar la semana con más detalle, tienes el <a href="/papel/horario-escolar/">horario semanal</a>.</p>
${notaFestivos}
<p>Si prefieres ver el año entero de un vistazo, tienes el <a href="/calendarios/">calendario ${ANIO} anual en una hoja</a>.</p>`
  },
  {
    cat: 'calendarios', slug: `${ANIO}-con-semanas`, corto: `Calendario ${ANIO} con números de semana`,
    title: `Calendario ${ANIO} con semanas numeradas para imprimir (PDF)`,
    desc: `Calendario ${ANIO} con el número de semana (ISO 8601) junto a cada fila, para la oficina o la planificación. Una hoja A4 con los festivos nacionales. PDF gratis.`,
    h1: `Calendario ${ANIO} con números de semana`,
    entrada: `El año ${ANIO} en una hoja A4 con el número de cada semana en la columna gris de la izquierda, como en los calendarios de oficina. Los festivos nacionales van marcados en rojo con un círculo.`,
    hojas: [{ tipo: 'calendario-anual', anio: ANIO, festivos, semanas: true }],
    copias: 1,
    amazon: AMAZON,
    cuerpo: `
<h2>Cómo se cuentan las semanas</h2>
<p>Las semanas siguen la norma ISO 8601, la que se usa en España y en casi toda Europa: empiezan en lunes y la semana 1 es la que contiene el primer jueves del año. Por eso ${ANIO} no empieza en la semana 1: el viernes 1 de enero, el sábado 2 y el domingo 3 pertenecen todavía a la semana 53 de 2026, y la semana 1 de ${ANIO} empieza el lunes 4 de enero.</p>
<p>${ANIO} tiene 52 semanas. La última, la semana 52, va del lunes 27 al domingo 2 de enero de 2028. Algunas fechas de referencia: la Semana Santa cae en la semana 12 (Viernes Santo, 26 de marzo), el 15 de agosto en la semana 32 y la Navidad en la semana 51.</p>
<h2>Para qué se usa</h2>
<p>En muchas empresas se habla de semanas en lugar de fechas: entregas «en la semana 23», turnos, vacaciones o planificación de proyectos. Tener el número a la vista ahorra cuentas. Si necesitas un mes por hoja con sitio para apuntar, tienes el <a href="/calendarios/mensual-${ANIO}/">calendario mensual ${ANIO}</a>.</p>
${notaFestivos}`,
    faq: [
      [`¿Cuántas semanas tiene ${ANIO}?`, `52. Un año tiene 53 semanas ISO solo si empieza en jueves, o en miércoles cuando es bisiesto; ${ANIO} empieza en viernes y no es bisiesto.`],
      [`¿En qué semana estamos?`, 'Busca el día de hoy en el calendario: el número gris de su fila es la semana. Recuerda que la semana empieza en lunes.']
    ]
  },
  ...Object.entries(DATOS.comunidades).map(([clave, c]) => {
    const propios = c.festivos.filter((x) => x[2] === 'propio');
    const tiene = (k) => c.festivos.some((x) => x[0] === k);
    const n = c.festivos.length;
    const semanaSanta = tiene('03-25') && tiene('03-29') ? 'el Jueves Santo (25 de marzo), el Viernes Santo (26) y el Lunes de Pascua (29)'
      : tiene('03-25') ? 'el Jueves Santo (25 de marzo) y el Viernes Santo (26)'
      : tiene('03-29') ? 'el Viernes Santo (26 de marzo) y el Lunes de Pascua (29); el Jueves Santo es laborable'
      : 'solo el Viernes Santo (26 de marzo)';
    const agosto = tiene('08-16') ? 'El 15 de agosto cae en domingo y aquí se traslada al lunes 16, que es festivo.'
      : c.festivos.some((x) => /15 de agosto/.test(x[1])) ? `El 15 de agosto cae en domingo y aquí se compensa con otro día: ${lista(c.festivos.filter((x) => /15 de agosto/.test(x[1])).map((x) => 'el ' + fecha(x[0])))}.`
      : 'El 15 de agosto cae en domingo y aquí no se traslada a otro día.';
    const notas = (c.notas || []).map((t) => `<p>${t.replace(/^En la Comunidad Autónoma de [^,]+, /, 'Además, ')}</p>`).join('');
    const fest = c.festivos.map((x) => [x[0], x[1]]);
    const de = c.con_articulo.startsWith('el ') ? 'del ' + c.con_articulo.slice(3) : 'de ' + c.con_articulo;
    const en = 'en ' + c.con_articulo;
    const breve = CORTO[clave] || c.nombre;
    const titulo = `Calendario ${ANIO} ${breve} para imprimir (PDF y Excel)`;
    return {
      cat: 'calendarios', slug: `${ANIO}-${clave}`, corto: `Calendario ${ANIO} ${de}`,
      title: titulo.length <= 60 ? titulo : `Calendario ${ANIO} ${breve} para imprimir (PDF)`,
      desc: `Calendario ${ANIO} ${de} para imprimir con sus ${n} festivos nacionales y autonómicos. Anual en A4, mes a mes en PDF y en Excel. Gratis.`,
      h1: `Calendario ${ANIO} ${de} para imprimir`,
      entrada: `El año ${ANIO} en una hoja A4 con los ${n} festivos de ${c.con_articulo} marcados en rojo: los nacionales y los propios de la comunidad. El PDF trae además los doce meses, uno por hoja, con casillas para apuntar. También lo tienes en Excel para editarlo.`,
      hojas: [{ tipo: 'calendario-anual', anio: ANIO, festivos: fest, region: c.nombre, leyenda: `Festivos ${ANIO} ${en}` }],
      pdfExtra: meses(0, 12, fest),
      excel: `/pdf/calendario-${ANIO}-${clave}.xlsx`,
      copias: 1,
      amazon: AMAZON,
    amazon: AMAZON,
      cuerpo: `
<h2>Los ${n} festivos de ${ANIO} ${en}</h2>
<ul>
${c.festivos.map((x) => `<li><strong>${fecha(x[0])}</strong>: ${x[1]}${x[2] === 'propio' ? ' <em>(solo en algunas comunidades)</em>' : ''}</li>`).join('\n')}
</ul>
<p>Los marcados como «solo en algunas comunidades» son los que cambian de una comunidad a otra: ${propios.length ? lista(propios.map((x) => x[1])) : 'ninguno'}. El resto son fiesta en toda España. La lista sale de la resolución de fiestas laborales para ${ANIO} publicada en el BOE el 13 de octubre de 2026 (<a href="${DATOS.boe.url}" rel="nofollow">${DATOS.boe.id}</a>).</p>
<h2>Semana Santa y agosto</h2>
<p>En ${ANIO} la Semana Santa cae a finales de marzo. ${en.charAt(0).toUpperCase() + en.slice(1)} son festivos ${semanaSanta}. ${agosto}</p>
${notas}
<h2>Y los festivos locales</h2>
<p>Cada municipio tiene además dos fiestas locales propias, que no salen en este calendario porque cambian de un pueblo a otro. Las tienes, municipio a municipio, en los <a href="https://festivosde.es/comunidad/${clave}/">festivos ${de} en festivosde.es</a>, donde también puedes imprimir el calendario laboral con tus fiestas locales ya marcadas.</p>
<h2>Cómo imprimirlo</h2>
<p>El calendario anual está pensado para A4 vertical y se lee bien en blanco y negro, porque los festivos llevan un círculo además del color. Para la pared, imprímelo en A3 con «Ajustar al papel». El Excel trae una hoja con el año entero y otra por cada mes, con los festivos ya escritos, para que añadas cumpleaños, turnos o vacaciones antes de imprimir.</p>
<p>¿Buscas otra comunidad? Tienes el <a href="/calendarios/">calendario ${ANIO} con los festivos nacionales</a> y, desde allí, el de cada comunidad autónoma.</p>`,
      faq: [
        [`¿Cuántos festivos hay ${en} en ${ANIO}?`, `${n} entre nacionales y autonómicos, más las dos fiestas locales de cada municipio.`],
        [`¿Se puede editar el calendario?`, `Sí: descarga el Excel, que tiene el año completo y una hoja por mes con los festivos ${de} ya marcados. Puedes escribir en las casillas y luego imprimirlo.`]
      ]
    };
  })
];
