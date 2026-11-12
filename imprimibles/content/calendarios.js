// Calendarios para imprimir. Festivos nacionales de 2027 según la Resolución de 8 de octubre de 2026
// de la Dirección General de Trabajo (BOE-A-2026-21254), los mismos datos que usa festivosde.es
// (festivos/data/festivos_2027.json): solo los que son festivo en todas las comunidades.

const ANIO = 2027;
const festivos = [
  ['01-01', 'Año Nuevo'], ['01-06', 'Epifanía del Señor'], ['03-26', 'Viernes Santo'], ['05-01', 'Fiesta del Trabajo'],
  ['10-12', 'Fiesta Nacional de España'], ['11-01', 'Todos los Santos'], ['12-06', 'Día de la Constitución'],
  ['12-08', 'Inmaculada Concepción'], ['12-25', 'Navidad']
];
const meses = (desde, hasta) => Array.from({ length: hasta - desde }, (_, i) => ({ tipo: 'calendario-mes', anio: ANIO, mes: desde + i, festivos }));

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
    copias: 1,
    cuerpo: notaFestivos + `
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
    cuerpo: `
<h2>Para qué sirve un calendario mes a mes</h2>
<p>Cada casilla mide unos 2,5 × 3,5 centímetros, sitio suficiente para dos o tres anotaciones a mano. Es el formato de los calendarios de cocina: se cuelga en la nevera o en un tablón y toda la familia apunta allí las citas médicas, las excursiones del colegio o los turnos de trabajo.</p>
<p>También funciona como planificador: imprime solo el mes en curso, apunta los plazos y las fechas importantes y tenlo a la vista junto al escritorio. Si necesitas organizar la semana con más detalle, tienes el <a href="/papel/horario-escolar/">horario semanal</a>.</p>
${notaFestivos}
<p>Si prefieres ver el año entero de un vistazo, tienes el <a href="/calendarios/">calendario ${ANIO} anual en una hoja</a>.</p>`
  }
];
