// Fichas de estimulación cognitiva para mayores, por nivel de deterioro (lib/puzzles.js, bloque «estimulación cognitiva»).

const REFRANES = [
  ['A quien madruga', 'Dios le ayuda'], ['Más vale pájaro en mano', 'que ciento volando'], ['No por mucho madrugar', 'amanece más temprano'],
  ['En casa de herrero', 'cuchillo de palo'], ['Perro ladrador', 'poco mordedor'], ['Ojos que no ven', 'corazón que no siente'],
  ['Al pan, pan', 'y al vino, vino'], ['Dime con quién andas', 'y te diré quién eres'], ['Más vale tarde', 'que nunca'],
  ['Camarón que se duerme', 'se lo lleva la corriente'], ['A caballo regalado', 'no le mires el diente'], ['El que la sigue', 'la consigue'],
  ['Agua que no has de beber', 'déjala correr'], ['No hay mal', 'que por bien no venga'], ['Quien siembra vientos', 'recoge tempestades'],
  ['Hasta el cuarenta de mayo', 'no te quites el sayo'], ['En abril', 'aguas mil'], ['Más vale prevenir', 'que curar'],
  ['Zapatero', 'a tus zapatos'], ['A mal tiempo', 'buena cara'], ['Cada oveja', 'con su pareja'], ['Ande yo caliente', 'y ríase la gente'],
  ['Quien mucho abarca', 'poco aprieta'], ['Haz el bien', 'y no mires a quién'], ['Mucho ruido', 'y pocas nueces'],
  ['Cría cuervos', 'y te sacarán los ojos'], ['Donde las dan', 'las toman'], ['El que avisa', 'no es traidor']
];

const CATEGORIAS = ['Frutas', 'Animales', 'Nombres de mujer', 'Nombres de hombre', 'Ciudades de España', 'Cosas que hay en una cocina',
  'Prendas de ropa', 'Oficios y profesiones', 'Colores', 'Flores', 'Comidas típicas de España', 'Cosas que hay en un dormitorio',
  'Palabras que empiezan por P', 'Palabras que empiezan por M', 'Palabras que empiezan por S', 'Palabras que empiezan por C'];

const GRUPOS = {
  Frutas: ['manzana', 'pera', 'plátano', 'naranja', 'uva', 'melón', 'fresa', 'cereza'],
  Animales: ['perro', 'gato', 'caballo', 'vaca', 'gallina', 'oveja', 'burro', 'conejo'],
  Ropa: ['camisa', 'pantalón', 'falda', 'chaqueta', 'abrigo', 'bufanda', 'calcetín', 'jersey'],
  Muebles: ['mesa', 'silla', 'armario', 'cama', 'sofá', 'estantería', 'cómoda', 'mesilla'],
  Verduras: ['lechuga', 'zanahoria', 'cebolla', 'pimiento', 'calabacín', 'pepino', 'acelga', 'espinaca'],
  Herramientas: ['martillo', 'sierra', 'alicates', 'tenazas', 'destornillador', 'llave inglesa', 'metro', 'lija']
};

const SECUENCIAS = [
  ['Hacer un café', ['Llenar la cafetera de agua', 'Poner el café molido', 'Calentar la cafetera en el fuego', 'Servir el café en la taza', 'Añadir azúcar o leche']],
  ['Hacer una tortilla de patatas', ['Pelar y cortar las patatas', 'Freír las patatas', 'Batir los huevos', 'Mezclar las patatas con el huevo', 'Cuajar la tortilla en la sartén']],
  ['Enviar una carta', ['Escribir la carta', 'Meterla en el sobre', 'Poner la dirección y el sello', 'Echarla al buzón']],
  ['Lavarse los dientes', ['Coger el cepillo', 'Poner la pasta de dientes', 'Cepillarse los dientes', 'Enjuagarse la boca']],
  ['Plantar una flor', ['Hacer un hoyo en la tierra', 'Poner la planta en el hoyo', 'Tapar con tierra', 'Regar la planta']],
  ['Vestirse para salir', ['Ponerse la ropa interior', 'Ponerse los pantalones', 'Ponerse los zapatos', 'Ponerse el abrigo']],
  ['Las estaciones del año, empezando en marzo', ['Primavera', 'Verano', 'Otoño', 'Invierno']],
  ['Las comidas del día', ['Desayuno', 'Almuerzo', 'Merienda', 'Cena']],
  ['Los días de la semana', ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']]
];
const SECUENCIAS_CORTAS = SECUENCIAS.filter((s) => s[1].length <= 4);

const ORIENTACION_LEVE = [
  ['¿Qué día de la semana es hoy?'], ['¿Qué fecha es hoy? (día, mes y año)'], ['¿En qué estación del año estamos?'],
  ['¿En qué ciudad o pueblo estamos?'], ['¿Cómo se llama el sitio donde estamos ahora?'], ['¿Qué tiempo hace hoy?'],
  ['¿Qué ha comido o desayunado hoy?'], ['¿Qué fiesta o celebración viene pronto?']
];
const ORIENTACION_MODERADO = [
  ['¿Qué día es hoy? Rodéalo:', ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']],
  ['¿En qué estación estamos? Rodéala:', ['primavera', 'verano', 'otoño', 'invierno']],
  ['¿Es de día o de noche?', ['de día', 'de noche']],
  ['¿Qué tiempo hace hoy?', ['sol', 'nubes', 'lluvia', 'frío', 'calor']],
  ['¿Cómo te llamas?'], ['¿Dónde estamos?']
];

const comoUsar = `
<h2>Cómo usar las fichas</h2>
<ul>
<li><strong>Sesiones cortas.</strong> Entre 15 y 30 minutos, una o dos fichas cada vez, mejor que una tarde entera. En el deterioro moderado y severo, a veces bastan cinco minutos.</li>
<li><strong>En el mejor momento del día.</strong> Suele ser por la mañana, después de desayunar y descansado. Con buena luz, con las gafas puestas y sin la televisión encendida.</li>
<li><strong>Acompañando, no examinando.</strong> Leed juntos el enunciado, dad pistas si se atasca y celebrad lo que salga bien. Si una ficha frustra, se deja y se cambia por otra más fácil: el objetivo es que la persona esté activa y a gusto, no que acierte todo.</li>
<li><strong>Sin corregir en rojo delante.</strong> La hoja con la solución es para quien acompaña. Si hay un error, mejor repasarlo juntos («¿miramos otra vez este?») que tacharlo.</li>
<li><strong>Con temas cercanos.</strong> Las fichas de refranes, la compra o los pasos de una receta funcionan porque tocan recuerdos y tareas de toda la vida. Aprovechad para hablar: de dónde se compraba antes el pan, quién hacía la mejor tortilla de la familia…</li>
</ul>`;

const aviso = `
<h2>Un aviso importante</h2>
<p>Estas fichas son material de apoyo para hacer en casa, en un centro de día o en una residencia. No diagnostican nada ni sustituyen la valoración y el plan de un profesional: el médico de familia, el neurólogo, el neuropsicólogo o el terapeuta ocupacional son quienes pueden decir en qué punto está cada persona y qué ejercicios le convienen. Si notas cambios en la memoria de un familiar, lo primero es consultarlo con su médico.</p>`;

const niveles = `
<ul>
<li><a href="/estimulacion-cognitiva/deterioro-leve/">Deterioro cognitivo leve</a>: para personas que hacen su vida casi con normalidad pero notan olvidos o les cuesta concentrarse. Fichas con más texto: refranes, series de números, la compra, palabras por categorías, orientación, copiar dibujos y atención.</li>
<li><a href="/estimulacion-cognitiva/deterioro-moderado/">Deterioro cognitivo moderado</a>: para quien necesita ayuda en algunas tareas del día a día. Letra más grande, menos ejercicios por hoja y respuestas para elegir en lugar de escribir.</li>
<li><a href="/estimulacion-cognitiva/deterioro-severo/">Deterioro cognitivo severo</a>: para personas que dependen de otros para casi todo. Dibujos grandes, una sola consigna sencilla: unir iguales, contar hasta tres, rodear un dibujo, colorear o repasar trazos.</li>
</ul>`;

module.exports = [
  {
    cat: 'estimulacion-cognitiva', slug: '', corto: 'Estimulación cognitiva', nav: 'Estimulación cognitiva',
    resumen: 'Fichas para mayores: deterioro leve, moderado y severo',
    title: 'Fichas de estimulación cognitiva para mayores (PDF)',
    desc: 'Fichas de estimulación cognitiva para mayores para imprimir: deterioro leve, moderado y severo. Atención, memoria, lenguaje, cálculo y orientación.',
    h1: 'Fichas de estimulación cognitiva para mayores',
    entrada: 'Fichas para trabajar la atención, la memoria, el lenguaje, el cálculo y la orientación con personas mayores, en tres niveles según el grado de deterioro cognitivo. Letra grande, mucho espacio para escribir y temas cercanos: refranes, la compra, recetas de siempre. Casi todas cambian con «Otra distinta», así que se pueden repetir sin que salgan iguales, y tienen la solución aparte para quien acompaña.',
    hojas: [
      { tipo: 'refranes', lista: REFRANES, n: 6, titulo: 'Completa los refranes' },
      { tipo: 'cancelacion', formas: true, objetivo: 4, filas: 6, cols: 6, prop: .25, titulo: 'Busca los corazones' }
    ],
    copias: 2,
    cuerpo: `
<h2>Tres niveles</h2>
${niveles}
<p>Los niveles son orientativos. Una persona con deterioro leve puede tener un mal día y agradecer una ficha del nivel moderado, y alguien con deterioro moderado puede disfrutar de los refranes si siempre le gustaron. Lo mejor es probar y quedarse con lo que le resulta un reto alcanzable.</p>
<h2>Qué se trabaja en cada ficha</h2>
<ul>
<li><strong>Atención:</strong> rodear todas las letras o dibujos iguales a un modelo.</li>
<li><strong>Memoria y lenguaje:</strong> completar refranes, escribir palabras de una categoría (frutas, ciudades, oficios) o que empiecen por una letra.</li>
<li><strong>Cálculo:</strong> series de números y cuentas de la compra con precios.</li>
<li><strong>Funciones ejecutivas:</strong> ordenar los pasos de una tarea, como hacer un café o enviar una carta.</li>
<li><strong>Orientación:</strong> el día de la semana, la estación, el lugar.</li>
<li><strong>Praxias y coordinación:</strong> copiar dibujos uniendo puntos, repasar trazos y colorear.</li>
</ul>
${comoUsar}
${aviso}`,
    faq: [
      ['¿Para qué sirven las fichas de estimulación cognitiva?', 'Para mantener activas la atención, la memoria, el lenguaje y el cálculo con ejercicios sencillos y agradables. Son una actividad más dentro del plan que marque el profesional que atiende a la persona, no un tratamiento por sí mismas.'],
      ['¿Qué nivel elijo?', 'Empieza por el que creas que encaja y observa: si la persona termina la ficha sin esfuerzo, prueba el nivel superior; si se frustra o no entiende el enunciado, baja un nivel. Lo importante es que sea un reto alcanzable.'],
      ['¿Puedo usarlas en una residencia o un centro de día?', 'Sí. Puedes imprimirlas y fotocopiarlas sin límite para casa, centros de día, residencias y talleres. Lo único que no está permitido es venderlas o republicarlas en otra web.']
    ]
  },
  {
    cat: 'estimulacion-cognitiva', slug: 'deterioro-leve', corto: 'Deterioro cognitivo leve',
    title: 'Fichas de estimulación cognitiva: deterioro leve (PDF)',
    desc: 'Fichas de estimulación cognitiva para mayores con deterioro cognitivo leve: refranes, series, la compra, categorías, orientación y atención. Con solución.',
    h1: 'Fichas de estimulación cognitiva para deterioro leve',
    entrada: 'Fichas para personas mayores con deterioro cognitivo leve, que hacen su vida con bastante autonomía pero notan olvidos o les cuesta concentrarse. Son ejercicios con algo más de texto y un reto real: completar refranes, continuar series de números, hacer las cuentas de la compra, escribir palabras de una categoría, ordenar los pasos de una receta o copiar dibujos. Casi todas cambian con «Otra distinta» y tienen solución.',
    hojas: [
      { tipo: 'refranes', lista: REFRANES, n: 7, titulo: 'Completa los refranes' },
      { tipo: 'series', n: 6, largo: 6, huecos: 2, titulo: 'Series de números' },
      { tipo: 'compra', titulo: 'Las cuentas de la compra' },
      { tipo: 'fluidez', pool: CATEGORIAS, n: 3, lineas: 10, titulo: 'Palabras por grupos' },
      { tipo: 'ordenar', listas: SECUENCIAS.filter((s) => s[1].length >= 4), n: 2, tam: 6.4, titulo: 'Ordena los pasos' },
      { tipo: 'cancelacion', objetivo: ['M', 'P'], filas: 12, cols: 12, prop: .16, titulo: 'Atención: busca las letras' },
      { tipo: 'copiar', puntos: 5, n: 3, segs: 7, titulo: 'Copia los dibujos' },
      { tipo: 'orientacion', preguntas: ORIENTACION_LEVE, titulo: 'Orientación: ¿qué día es hoy?' }
    ],
    copias: 2,
    cuerpo: `
<h2>Qué hay en estas fichas</h2>
<ul>
<li><strong>Refranes</strong> de toda la vida para completar escribiendo el final: trabajan la memoria de lo aprendido hace años y el lenguaje.</li>
<li><strong>Series de números</strong> que suben o bajan de 2 en 2, de 5 en 5 o se duplican, con dos huecos que hay que descubrir.</li>
<li><strong>La compra:</strong> una lista de precios con céntimos y cuatro preguntas (cuánto se paga, cuánto devuelven…). Es cálculo, pero también una tarea de la vida diaria.</li>
<li><strong>Palabras por grupos:</strong> escribir frutas, ciudades, oficios o palabras que empiecen por una letra. Es la llamada fluidez verbal; si cuesta, se puede hacer en voz alta y escribir quien acompaña.</li>
<li><strong>Ordenar los pasos</strong> de una tarea conocida, como hacer una tortilla de patatas o enviar una carta.</li>
<li><strong>Atención:</strong> una sopa de letras sin palabras en la que hay que rodear todas las M y las P.</li>
<li><strong>Copiar dibujos</strong> uniendo los puntos de una cuadrícula, que trabaja la percepción del espacio y la coordinación.</li>
<li><strong>Orientación:</strong> preguntas sobre el día, la fecha y el lugar, para empezar la sesión.</li>
</ul>
<p>Para variar, también encajan en este nivel las <a href="/sopas-de-letras/faciles/">sopas de letras fáciles</a>, los <a href="/sudokus/faciles/">sudokus fáciles</a> y los <a href="/crucigramas/">crucigramas</a>.</p>
${comoUsar}
<p>Si alguna ficha resulta demasiado difícil, las del <a href="/estimulacion-cognitiva/deterioro-moderado/">nivel moderado</a> tienen letra más grande y respuestas para elegir.</p>
${aviso}`,
    faq: [
      ['¿Las fichas tienen solución?', 'Sí, las que tienen una respuesta correcta (refranes, series, la compra, ordenar los pasos y atención). «Ver solución» muestra la hoja resuelta, y en el PDF van al final. Las de palabras por grupos, copiar dibujos y orientación no tienen una única respuesta.'],
      ['¿Cada cuánto hay que hacerlas?', 'Lo que recomiende el profesional que atiende a la persona. Como referencia, muchas familias hacen una o dos fichas al día, varios días por semana, en sesiones cortas. Es mejor poco y a menudo que mucho de golpe.']
    ]
  },
  {
    cat: 'estimulacion-cognitiva', slug: 'deterioro-moderado', corto: 'Deterioro cognitivo moderado',
    title: 'Fichas de estimulación cognitiva: deterioro moderado',
    desc: 'Fichas de estimulación cognitiva para mayores con deterioro cognitivo moderado: letra grande, respuestas para elegir, atención, cálculo y orientación.',
    h1: 'Fichas de estimulación cognitiva para deterioro moderado',
    entrada: 'Fichas para personas mayores con deterioro cognitivo moderado, que necesitan ayuda en algunas tareas del día a día. Tienen letra más grande, menos ejercicios por hoja y, siempre que se puede, respuestas para elegir o rodear en lugar de escribir: refranes con tres finales, la compra con euros sin céntimos, series sencillas, agrupar palabras, ordenar los días o las comidas, buscar dibujos y unir iguales.',
    hojas: [
      { tipo: 'refranes', lista: REFRANES, n: 4, opciones: true, tam: 6.4, titulo: 'Elige el final del refrán' },
      { tipo: 'cancelacion', formas: true, objetivo: 3, filas: 7, cols: 6, prop: .25, pool: [0, 1, 2, 3, 4], titulo: 'Busca las estrellas' },
      { tipo: 'series', n: 5, largo: 5, alFinal: true, pasos: [1, 2, 10], max: 10, titulo: '¿Qué número sigue?' },
      { tipo: 'compra', enteros: true, titulo: 'Vamos a la tienda' },
      { tipo: 'clasificar', grupos: GRUPOS, ngrupos: 2, porGrupo: 4, tam: 7, titulo: 'Cada palabra en su grupo' },
      { tipo: 'ordenar', listas: SECUENCIAS_CORTAS, n: 2, tam: 6.6, titulo: '¿Qué va primero?' },
      { tipo: 'iguales', n: 5, max: 26, titulo: 'Une los dibujos iguales' },
      { tipo: 'copiar', puntos: 3, n: 3, segs: 3, diagonales: false, titulo: 'Copia los dibujos' },
      { tipo: 'orientacion', preguntas: ORIENTACION_MODERADO, tam: 6.6, instr: 'Rodea la respuesta o escríbela. Puedes mirar el calendario.', titulo: '¿Qué día es hoy?' }
    ],
    copias: 2,
    cuerpo: `
<h2>Cómo están adaptadas</h2>
<ul>
<li><strong>Letra grande</strong> y una sola tarea por hoja, con el enunciado en negrita y corto.</li>
<li><strong>Respuestas para elegir.</strong> En los refranes hay tres finales y se rodea el bueno; en la orientación se rodea el día o la estación. Reconocer es más fácil que recordar sin pistas, y permite acertar a quien ya no escribe con soltura.</li>
<li><strong>Números pequeños.</strong> La compra usa euros sin céntimos y las series suben de uno en uno, de dos en dos o de diez en diez.</li>
<li><strong>Tareas conocidas.</strong> Ordenar las comidas del día, las estaciones o los pasos para lavarse los dientes.</li>
<li><strong>Dibujos grandes</strong> para buscar estrellas, unir iguales y copiar figuras sencillas en una cuadrícula de nueve puntos.</li>
</ul>
<h2>Si cuesta escribir</h2>
<p>Muchas fichas se pueden hacer de palabra: la persona dice la respuesta y quien acompaña la escribe o le señala dónde rodearla. En la de agrupar palabras, por ejemplo, se pueden recortar las palabras y colocarlas en su columna, que es más fácil que copiarlas.</p>
${comoUsar}
<p>Si este nivel se queda corto, prueba las fichas de <a href="/estimulacion-cognitiva/deterioro-leve/">deterioro leve</a>; si cuesta demasiado, las de <a href="/estimulacion-cognitiva/deterioro-severo/">deterioro severo</a> son aún más sencillas.</p>
${aviso}`,
    faq: [
      ['¿Qué hago si no entiende el enunciado?', 'Leedlo juntos en voz alta y haced el primer ejercicio con él o ella como ejemplo. Si sigue sin entenderse, la ficha es demasiado difícil en ese momento: cámbiala por una del nivel severo o por una actividad distinta, como colorear.'],
      ['¿Las fichas tienen solución?', 'Sí, las de refranes, estrellas, series, la tienda, agrupar palabras, ordenar y unir iguales. La solución es para quien acompaña; no hace falta enseñarla.']
    ]
  },
  {
    cat: 'estimulacion-cognitiva', slug: 'deterioro-severo', corto: 'Deterioro cognitivo severo',
    title: 'Fichas de estimulación cognitiva: deterioro severo (PDF)',
    desc: 'Fichas de estimulación cognitiva para mayores con deterioro cognitivo severo: dibujos grandes para unir iguales, contar, rodear, colorear y repasar trazos.',
    h1: 'Fichas de estimulación cognitiva para deterioro severo',
    entrada: 'Fichas muy sencillas para personas mayores con deterioro cognitivo severo, que dependen de otras para casi todo. Cada hoja tiene una sola consigna corta y dibujos grandes: unir dibujos iguales, contar hasta tres, rodear un dibujo, colorear figuras o repasar trazos. Más que acertar, buscan un rato de atención compartida, tranquilo y agradable.',
    hojas: [
      { tipo: 'iguales', n: 3, max: 40, nombre: false, tamInstr: 8, titulo: 'Une los iguales' },
      { tipo: 'contar', n: 3, max: 3, nombre: false, tamInstr: 8, titulo: '¿Cuántos hay?' },
      { tipo: 'cancelacion', formas: true, objetivo: 0, filas: 3, cols: 3, prop: .4, pool: [0, 1, 2], nombre: false, tamInstr: 8, titulo: 'Busca los círculos' },
      { tipo: 'colorear', n: 2, pool: [0, 1, 2, 3, 4, 5], nombre: false, titulo: 'Colorea los dibujos' },
      { tipo: 'grafomotricidad', trazos: ['horizontal', 'ondas', 'puentes', 'zigzag'], alto: 22, paso: 50, titulo: 'Repasa los trazos', sub: 'Empieza en el punto negro y sigue la línea de puntos.' }
    ],
    copias: 2,
    cuerpo: `
<h2>Cómo están pensadas</h2>
<ul>
<li><strong>Una consigna por hoja</strong>, corta y en letra muy grande: «Une los iguales», «¿Cuántos hay?».</li>
<li><strong>Pocos elementos y muy grandes:</strong> tres parejas para unir, filas de uno a tres dibujos para contar, nueve figuras para buscar los círculos.</li>
<li><strong>Formas sencillas</strong> y fáciles de reconocer: círculo, cuadrado, triángulo, estrella, corazón.</li>
<li><strong>Colorear y repasar trazos</strong>, que no tienen respuesta correcta: se trata de mover la mano y estar a gusto.</li>
</ul>
<h2>Cómo acompañar</h2>
<p>En este nivel, quien acompaña es la clave. Siéntate al lado, señala con el dedo, ofrece el lápiz o la cera y haz tú el primer ejemplo. Habla con frases cortas y una cosa cada vez («mira este círculo», «¿dónde hay otro igual?»). Si la persona no quiere seguir, no insistas: probad otro día o cambiad a algo que le guste, como mirar fotos o escuchar música.</p>
<p>Las ceras gruesas o los lápices triangulares se agarran mejor que los finos. Plastificar las hojas permite usarlas con rotuladores borrables muchas veces.</p>
${comoUsar}
<p>Si estas fichas resultan fáciles, las de <a href="/estimulacion-cognitiva/deterioro-moderado/">deterioro moderado</a> son el siguiente paso. Y los <a href="/mandalas/faciles/">mandalas fáciles</a> sirven para colorear con más detalle.</p>
${aviso}`,
    faq: [
      ['¿Qué hago si no quiere hacer la ficha?', 'Respetarlo. En el deterioro severo el objetivo es el bienestar y el contacto, no completar el ejercicio. Se puede intentar en otro momento, hacerlo juntos (tu mano guiando la suya) o cambiar a otra actividad que le guste.'],
      ['¿Sirven si ya no sabe leer?', 'Sí, la mayoría: unir iguales, contar, buscar círculos, colorear y repasar trazos se entienden mirando los dibujos y con una explicación de palabra de quien acompaña.']
    ],
    amazon: [['Ceras gruesas', 'ceras gruesas colores'], ['Lápices triangulares gruesos', 'lapices de colores triangulares gruesos'], ['Fundas para plastificar A4', 'fundas plastificar a4']]
  }
];
