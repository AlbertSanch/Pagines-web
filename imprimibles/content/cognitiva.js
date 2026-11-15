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

const CANCIONES = [
  ['Boleros y coplas de siempre', [['Angelitos negros', 'Antonio Machín'], ['Toda una vida', 'Antonio Machín'], ['Soy minero', 'Antonio Molina'], ['Francisco Alegre', 'Juanita Reina'], ['Mi jaca', 'Estrellita Castro'], ['Bésame mucho', 'bolero de Consuelo Velázquez']]],
  ['Años 60', [['Tómbola', 'Marisol'], ['La chica ye-yé', 'Concha Velasco'], ['Black is black', 'Los Bravos'], ['Yo soy aquel', 'Raphael'], ['Cuando calienta el sol', 'Los Hermanos Rigual'], ['La, la, la', 'Massiel']]],
  ['Años 70', [['Un rayo de sol', 'Los Diablos'], ['Libre', 'Nino Bravo'], ['Eres tú', 'Mocedades'], ['Mediterráneo', 'Joan Manuel Serrat'], ['Mi querida España', 'Cecilia'], ['Soy rebelde', 'Jeanette']]],
  ['Años 80', [['La puerta de Alcalá', 'Ana Belén y Víctor Manuel'], ['Los pajaritos', 'María Jesús y su Acordeón'], ['Hey', 'Julio Iglesias'], ['Bailando', 'Alaska y los Pegamoides'], ['Ni tú ni nadie', 'Alaska y Dinarama'], ['Cadillac solitario', 'Loquillo y los Trogloditas']]]
];

const PRECIOS = [['Pan (barra)', '1,10 €'], ['Leche (litro)', '1,05 €'], ['Huevos (docena)', '2,60 €'], ['Manzanas (kilo)', '2,20 €'], ['Aceite (litro)', '5,90 €'],
  ['Café (paquete)', '3,40 €'], ['Arroz (kilo)', '1,50 €'], ['Galletas (paquete)', '1,80 €'], ['Queso (cuña)', '4,75 €'], ['Naranjas (kilo)', '1,95 €']];

const DINAMICAS = `
<h2>Antes de empezar</h2>
<ul>
<li><strong>Grupos de 6 a 12 personas</strong>, sentadas en círculo o en U para que todas se vean.</li>
<li><strong>Sesiones de 45 a 60 minutos</strong> con dos o tres dinámicas, alternando las de estar sentado con las de moverse.</li>
<li><strong>Siempre la misma entrada y la misma salida:</strong> al llegar, el saludo y en la pizarra la fecha, el día de la semana y el tiempo que hace (orientación); al terminar, algo agradable, como cantar una canción entre todos.</li>
<li><strong>Nadie falla en público.</strong> Si alguien no recuerda, se le dan pistas o le ayuda el grupo. Lo importante es participar.</li>
<li><strong>Mezclar niveles con roles:</strong> quien está mejor puede apuntar en la pizarra, hacer de tendero o leer las preguntas.</li>
</ul>

<h2>Memoria y recuerdos</h2>
<h3>1. El baúl de los recuerdos</h3>
<p>Una caja con objetos antiguos: un molinillo de café, una plancha de hierro, una peseta, una radio de transistores, un dedal, una cartilla escolar. Se saca uno y el grupo cuenta qué es, para qué servía y qué recuerdos le trae. <strong>Más fácil:</strong> objetos muy conocidos y preguntas de sí o no. <strong>Más difícil:</strong> guardar los objetos y, al final de la sesión, recordar entre todos los cinco que salieron.</p>
<h3>2. Me voy de viaje y en la maleta llevo…</h3>
<p>El primero dice «me voy de viaje y en la maleta llevo un sombrero»; el segundo repite y añade, «…un sombrero y una toalla»; y así por turnos. <strong>Más fácil:</strong> meter objetos de verdad en una maleta, que se ven. <strong>Más difícil:</strong> que vayan por orden alfabético (abanico, bañador, cepillo…).</p>
<h3>3. La radio de antes</h3>
<p>Suenan 15 segundos de una canción de toda la vida y el grupo adivina el título y el cantante, y canta el estribillo. La música despierta recuerdos incluso en personas con deterioro avanzado, y suele ser la sesión favorita. En las hojas de abajo tienes una lista de canciones por épocas.</p>
<h3>4. Mi pueblo en el mapa</h3>
<p>Un mapa grande de España en la pared. Cada persona pone una chincheta o una pegatina en su pueblo y cuenta algo de él: la fiesta, la comida típica, a qué se dedicaba la gente. Trabaja la orientación en el espacio y la memoria de la propia vida.</p>

<h2>Lenguaje</h2>
<h3>5. Refranes para emparejar</h3>
<p>Se reparten las tarjetas de refranes de esta página, partidas por la mitad: unos tienen el principio («A quien madruga…») y otros el final («…Dios le ayuda»). Quien tiene un principio lo lee en voz alta y el grupo busca quién tiene el final. Después se comenta qué quiere decir. <strong>Más fácil:</strong> el monitor dice el principio y el grupo lo completa de memoria.</p>
<h3>6. Palabras encadenadas</h3>
<p>Cada palabra empieza por la última sílaba de la anterior: casa, sapo, pollo, llave… <strong>Más fácil:</strong> decir por turnos palabras que empiecen por una letra («nombres que empiecen por M»).</p>
<h3>7. El supermercado de la A a la Z</h3>
<p>Por turnos, cada uno dice algo que se compra en el supermercado con la letra que toca: aceite, bacalao, cebollas, dátiles… <strong>Más fácil:</strong> sin letras, solo «cosas que se compran en la frutería».</p>

<h2>Atención y cálculo</h2>
<h3>8. Bingo con sumas</h3>
<p>Se juega con cartones normales de bingo, pero el monitor no canta «el 24», sino «el 20 más 4», y cada jugador tiene que hacer la cuenta antes de buscarlo. La hoja del monitor de esta página trae una suma o una resta para cada número del 1 al 90. Los cartones están en <a href="/bingo/">bingo para imprimir</a>; para quien no lee números, mejor el bingo de dibujos.</p>
<h3>9. La tienda</h3>
<p>Una mesa con productos (o envases vacíos, o fotos) y sus tarjetas de precios, que también están en esta página, y monedas y billetes de juguete. Por turnos, unos venden y otros compran: hay que pagar, dar la vuelta y comprobarla. Trabaja el cálculo con una tarea de la vida diaria y es de las dinámicas que más gustan, porque es «de verdad».</p>
<h3>10. Palmada en el número</h3>
<p>El monitor lee números en voz alta, despacio, y el grupo da una palmada cuando sale el elegido (por ejemplo, el 7). <strong>Más difícil:</strong> palmada en los pares y golpe en la mesa en los impares.</p>

<h2>Creatividad y trabajo en equipo</h2>
<h3>11. El mural de la estación</h3>
<p>Un papel continuo grande en el que el grupo hace el mural de la estación del año: recortes de revistas, hojas secas en otoño, flores en primavera, dibujos y frases. Trabaja la orientación en el tiempo, la motricidad fina y la cooperación, y alegra la sala durante semanas.</p>
<h3>12. Recetas de toda la vida</h3>
<p>El grupo dicta entre todos la receta de un plato (tortilla, cocido, torrijas, rosquillas) y el monitor la escribe en grande: los ingredientes, los pasos en orden y los trucos de cada casa. Con la plantilla de esta página, al cabo de unas sesiones sale un recetario del grupo para que cada uno se lleve una copia.</p>
<h3>13. Teatro de anuncios y escenas</h3>
<p>Representar anuncios antiguos de la televisión que el grupo recuerde, o escenas de la vida diaria: en la consulta del médico, en el mercado, en la estación. Trabaja la memoria, la expresión y la risa, que también cuenta.</p>

<h2>Movimiento y cerebro</h2>
<h3>14. Gimnasia de órdenes</h3>
<p>Sentados en círculo, el monitor da órdenes sencillas: manos arriba, toca la rodilla derecha, dos palmadas, mira a la izquierda. <strong>Más difícil:</strong> «Simón dice»: solo se obedece si la orden empieza por «Simón dice».</p>
<h3>15. Pásala con nombre</h3>
<p>Una pelota blanda pasa de mano en mano y quien la recibe dice su nombre y una fruta (o un color, o una ciudad). En la segunda ronda, hay que decir el nombre de quien te la pasa. Trabaja la atención, la memoria de nombres y la coordinación, y es un buen comienzo de sesión.</p>
`;

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
</ul>
<p>Y para talleres y centros, <a href="/estimulacion-cognitiva/dinamicas-grupales/">quince dinámicas de grupo</a> con su material para imprimir.</p>`;

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
    cat: 'estimulacion-cognitiva', slug: 'dinamicas-grupales', corto: 'Dinámicas en grupo',
    title: 'Dinámicas de estimulación cognitiva para grupos de mayores',
    desc: '15 dinámicas de grupo para trabajar la memoria, el lenguaje y la atención con mayores, con tarjetas de refranes, bingo con sumas y plantillas para imprimir.',
    h1: 'Dinámicas de estimulación cognitiva para grupos de mayores',
    entrada: 'Quince dinámicas para hacer en grupo en un centro de día, una residencia o un taller de memoria: recuerdos con objetos antiguos, música de siempre, refranes, la tienda, el bingo con sumas, recetas de toda la vida y juegos de movimiento. Cada una explica cómo hacerla más fácil o más difícil, y abajo tienes el material listo para imprimir: tarjetas de refranes para emparejar, la hoja del bingo con sumas, precios para la tienda, la plantilla del recetario, canciones por épocas y una hoja para registrar cada sesión.',
    hojas: [
      { tipo: 'tarjetas', pares: REFRANES, cols: 2, filas: 5, tam: 6.6, titulo: 'Refranes para emparejar', sub: 'Recorta las tarjetas, repártelas y buscad entre todos las dos mitades de cada refrán.' },
      { tipo: 'bingo-sumas', titulo: 'Bingo con sumas: hoja del monitor' },
      { tipo: 'tarjetas', items: PRECIOS, cols: 2, filas: 5, tam: 7.4, colorB: '#d5392b', titulo: 'Precios para la tienda', sub: 'Recorta las tarjetas y ponlas junto a cada producto, su envase o su foto. Precios de ejemplo.' },
      { tipo: 'receta', titulo: 'Recetas de toda la vida' },
      { tipo: 'lista-grupos', grupos: CANCIONES, titulo: 'Canciones para cantar en grupo', sub: 'Pon unos segundos de cada una: el grupo adivina el título y sigue el estribillo.' },
      { tipo: 'sesion', titulo: 'Registro de la sesión' }
    ],
    copias: 2,
    cuerpo: `${DINAMICAS}
<h2>Fichas para trabajar de forma individual</h2>
<p>Entre dinámica y dinámica, o para quien prefiere trabajar solo, están las fichas por niveles: <a href="/estimulacion-cognitiva/deterioro-leve/">deterioro leve</a>, <a href="/estimulacion-cognitiva/deterioro-moderado/">deterioro moderado</a> y <a href="/estimulacion-cognitiva/deterioro-severo/">deterioro severo</a>.</p>
${aviso}`,
    faq: [
      ['¿Cuántas personas son ideales para una dinámica?', 'Entre seis y doce. Con menos, se pierde el ambiente de grupo; con más, cuesta que todos participen y oigan bien. Si el grupo es grande, se puede partir en dos con un monitor cada uno.'],
      ['¿Sirven para grupos con distintos niveles de deterioro?', 'Sí. Cada dinámica tiene una versión más fácil y otra más difícil, y se pueden repartir papeles según lo que pueda hacer cada persona: unos cantan, otros apuntan, otros reparten las tarjetas. Las de música y recuerdos suelen funcionar con todo el grupo.'],
      ['¿Puedo usar el material en mi centro?', 'Sí. Puedes imprimirlo y fotocopiarlo sin límite para residencias, centros de día, asociaciones y talleres. Lo único que no está permitido es venderlo o republicarlo en otra web.']
    ],
    amazon: [['Pelotas blandas de espuma', 'pelotas espuma blandas'], ['Bombo de bingo con bolas', 'bombo bingo bolas'], ['Billetes y monedas de juguete', 'billetes monedas juguete euros']]
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
