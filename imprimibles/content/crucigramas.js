// Crucigramas. Cada banco es una lista de [respuesta, pista]; en cada hoja salen unas 12-14
// palabras elegidas al azar. La respuesta se escribe con su ortografía (tildes incluidas):
// en la cuadrícula se quitan solas.

const variado = [
  ['Madrid', 'Capital de España'],
  ['Ebro', 'Río que pasa por Zaragoza'],
  ['Teide', 'Pico más alto de España, en Tenerife'],
  ['Cervantes', 'Autor de «Don Quijote de la Mancha»'],
  ['paella', 'Plato de arroz típico de Valencia'],
  ['Pirineos', 'Cordillera que separa España de Francia'],
  ['Guernica', 'Cuadro de Picasso que se expone en el Museo Reina Sofía'],
  ['Sevilla', 'Ciudad de la Giralda y la Torre del Oro'],
  ['Goya', 'Pintor de «Los fusilamientos del 3 de mayo»'],
  ['flamenco', 'Arte andaluz de cante, toque y baile'],
  ['tortilla', 'Se hace con huevo y patata, con cebolla o sin ella'],
  ['Mercurio', 'Planeta más cercano al Sol'],
  ['oxígeno', 'Gas que respiramos, de símbolo O'],
  ['piano', 'Instrumento de teclas blancas y negras'],
  ['ajedrez', 'Juego de reyes, damas, alfiles y peones'],
  ['euro', 'Moneda que circula en España desde 2002'],
  ['Atlántico', 'Océano que baña Galicia y Canarias'],
  ['Alhambra', 'Conjunto de palacios nazaríes de Granada'],
  ['Quijote', 'Caballero que confundió molinos con gigantes'],
  ['Lorca', 'Poeta granadino, autor de «Romancero gitano»'],
  ['Prado', 'Museo de Madrid donde cuelgan «Las meninas»'],
  ['Velázquez', 'Pintor de «Las meninas»'],
  ['naranja', 'Cítrico típico de los huertos valencianos'],
  ['gazpacho', 'Sopa fría andaluza de tomate'],
  ['Duero', 'Río que pasa por Zamora y desemboca en Oporto'],
  ['Canarias', 'Archipiélago de Tenerife, Gran Canaria y Lanzarote'],
  ['Gaudí', 'Arquitecto de la Sagrada Familia'],
  ['Baleares', 'Islas de Mallorca, Menorca, Ibiza y Formentera'],
  ['luna', 'Satélite natural de la Tierra'],
  ['olivo', 'Árbol del que se obtiene el aceite']
];

const ninos = [
  ['sol', 'Estrella que nos da luz y calor durante el día'],
  ['luna', 'Brilla en el cielo por la noche y cambia de forma'],
  ['libro', 'Tiene páginas y se lee'],
  ['perro', 'Animal que ladra'],
  ['gato', 'Animal que maúlla'],
  ['agua', 'La bebemos cuando tenemos sed'],
  ['árbol', 'Tiene tronco, ramas y hojas'],
  ['escuela', 'Lugar al que vamos a aprender'],
  ['pelota', 'Juguete redondo que bota'],
  ['manzana', 'Fruta redonda que puede ser roja, verde o amarilla'],
  ['leche', 'Bebida blanca que nos da la vaca'],
  ['cama', 'Mueble en el que dormimos'],
  ['lápiz', 'Sirve para escribir y se borra con goma'],
  ['nariz', 'Parte de la cara con la que olemos'],
  ['zapato', 'Lo llevamos en el pie para caminar'],
  ['reloj', 'Nos dice qué hora es'],
  ['nube', 'Está en el cielo y de ella cae la lluvia'],
  ['flor', 'Parte bonita y perfumada de una planta'],
  ['pan', 'Se compra en la panadería'],
  ['tren', 'Viaja por las vías'],
  ['barco', 'Navega por el mar'],
  ['avión', 'Vuela por el cielo y lleva pasajeros'],
  ['invierno', 'Estación del año en la que hace más frío'],
  ['verano', 'Estación de las vacaciones largas y la playa'],
  ['mesa', 'Mueble en el que comemos'],
  ['abuela', 'La madre de tu madre o de tu padre'],
  ['diente', 'Lo usamos para masticar; los de leche se caen'],
  ['arcoíris', 'Arco de colores que sale cuando llueve y hace sol'],
  ['helado', 'Postre frío que apetece en verano'],
  ['mochila', 'Bolsa que llevamos a la espalda al cole']
];

const animales = [
  ['león', 'Lo llaman el rey de la selva'],
  ['jirafa', 'El animal con el cuello más largo'],
  ['elefante', 'Tiene trompa y unas orejas enormes'],
  ['canguro', 'Salta y lleva a su cría en una bolsa'],
  ['pingüino', 'Ave que no vuela y vive donde hace mucho frío'],
  ['delfín', 'Mamífero marino muy listo que salta entre las olas'],
  ['ballena', 'El animal más grande del planeta'],
  ['tortuga', 'Es muy lenta y se esconde en su caparazón'],
  ['caracol', 'Deja un rastro de baba y saca los cuernos'],
  ['murciélago', 'Mamífero que vuela de noche y duerme boca abajo'],
  ['búho', 'Ave nocturna de ojos grandes'],
  ['abeja', 'Insecto que fabrica miel'],
  ['hormiga', 'Insecto pequeño que vive en un hormiguero'],
  ['mariposa', 'Antes de volar fue oruga'],
  ['rana', 'Croa, salta y de pequeña es renacuajo'],
  ['serpiente', 'Reptil sin patas que se arrastra'],
  ['cocodrilo', 'Reptil de grandes mandíbulas que vive en los ríos'],
  ['camello', 'Tiene dos jorobas y aguanta mucho sin beber'],
  ['cebra', 'Parece un caballo con rayas blancas y negras'],
  ['oso', 'Animal grande y peludo que hiberna en invierno'],
  ['lobo', 'Aúlla a la luna y vive en manada'],
  ['zorro', 'Tiene la cola larga y peluda y fama de astuto'],
  ['águila', 'Ave rapaz de vista muy aguda'],
  ['pulpo', 'Tiene ocho brazos con ventosas'],
  ['tiburón', 'Pez grande con varias filas de dientes'],
  ['gallina', 'Ave de granja que pone huevos'],
  ['vaca', 'Nos da leche y hace «mu»'],
  ['oveja', 'Con su lana se hacen jerséis'],
  ['caballo', 'Se puede montar y relincha'],
  ['conejo', 'Tiene orejas largas y le encanta la zanahoria'],
  ['ardilla', 'Roedor de cola peluda que guarda frutos secos'],
  ['flamenco', 'Ave rosa que descansa sobre una sola pata']
];

const navidad = [
  ['belén', 'Se monta con el portal, la mula y el buey'],
  ['turrón', 'Dulce de almendra; lo hay duro y blando'],
  ['polvorón', 'Dulce navideño que se deshace en la boca'],
  ['villancico', 'Canción de Navidad'],
  ['zambomba', 'Instrumento que suena al frotar una caña'],
  ['pandereta', 'Instrumento con sonajas que acompaña los villancicos'],
  ['roscón', 'Dulce del día de Reyes con sorpresa dentro'],
  ['uvas', 'Nos comemos doce en Nochevieja'],
  ['campanadas', 'Suenan a medianoche del 31 de diciembre'],
  ['Nochebuena', 'La noche del 24 de diciembre'],
  ['Nochevieja', 'La última noche del año'],
  ['Reyes', 'Melchor, Gaspar y Baltasar'],
  ['camello', 'Animal en el que viajan los Reyes Magos'],
  ['estrella', 'Guio a los Reyes y se pone en lo alto del árbol'],
  ['cabalgata', 'Desfile de los Reyes Magos el 5 de enero'],
  ['pastor', 'En el belén, cuida de las ovejas'],
  ['regalo', 'Se envuelve en papel bonito'],
  ['trineo', 'Vehículo de Papá Noel'],
  ['reno', 'Animal que tira del trineo de Papá Noel'],
  ['nieve', 'Cae del cielo cuando hace mucho frío y es blanca'],
  ['chimenea', 'Por ella entra Papá Noel'],
  ['mazapán', 'Dulce de almendra y azúcar, típico de Toledo'],
  ['guirnalda', 'Tira de adornos que se cuelga en el árbol'],
  ['carbón', 'Lo traen los Reyes a quien se ha portado mal'],
  ['carta', 'Se escribe a los Reyes para pedir regalos'],
  ['paje', 'Ayudante de los Reyes Magos que recoge las cartas']
];

const ingles = [
  ['cat', 'Gato'], ['dog', 'Perro'], ['house', 'Casa'], ['book', 'Libro'], ['apple', 'Manzana'],
  ['water', 'Agua'], ['school', 'Colegio'], ['teacher', 'Profesor o profesora'], ['friend', 'Amigo'],
  ['red', 'Rojo'], ['green', 'Verde'], ['yellow', 'Amarillo'], ['blue', 'Azul'], ['Monday', 'Lunes'],
  ['Sunday', 'Domingo'], ['summer', 'Verano'], ['winter', 'Invierno'], ['mother', 'Madre'],
  ['father', 'Padre'], ['brother', 'Hermano'], ['sister', 'Hermana'], ['chair', 'Silla'],
  ['table', 'Mesa'], ['pencil', 'Lápiz'], ['orange', 'Naranja (la fruta y el color)'], ['bird', 'Pájaro'],
  ['fish', 'Pez'], ['horse', 'Caballo'], ['milk', 'Leche'], ['bread', 'Pan'], ['happy', 'Feliz'],
  ['seven', 'Siete'], ['twelve', 'Doce']
];

const inglesIngles = [
  ['dog', 'A pet that barks'], ['cat', 'A pet that says «meow»'], ['cow', 'A farm animal that gives us milk'],
  ['elephant', 'A big grey animal with a trunk'], ['giraffe', 'The animal with the longest neck'],
  ['banana', 'A long yellow fruit'], ['apple', 'A red or green fruit that grows on trees'],
  ['bread', 'You use it to make a sandwich'], ['breakfast', 'The first meal of the day'],
  ['teacher', 'The person who teaches you at school'], ['library', 'A place where you can borrow books'],
  ['kitchen', 'The room where you cook'], ['bedroom', 'The room where you sleep'],
  ['Monday', 'The day after Sunday'], ['Friday', 'The last school day of the week'],
  ['December', 'The month of Christmas'], ['summer', 'The hottest season of the year'],
  ['winter', 'The coldest season of the year'], ['umbrella', 'You open it when it rains'],
  ['doctor', 'You visit this person when you are ill'], ['airport', 'A place where planes take off and land'],
  ['grandmother', 'Your mother\'s mother'], ['brother', 'A boy who has the same parents as you'],
  ['twelve', 'Ten plus two'], ['hundred', 'Ten times ten'], ['yellow', 'The colour of the sun and of lemons'],
  ['purple', 'Red and blue make this colour'], ['moon', 'You can see it in the sky at night'],
  ['clock', 'It tells you the time'], ['football', 'A team sport with a ball and two goals'],
  ['happy', 'The opposite of sad'], ['tall', 'The opposite of short']
];

const comoSeHace = `
<h2>Cómo se resuelve</h2>
<p>Cada palabra empieza en la casilla con su número. Las <strong>horizontales</strong> se escriben de izquierda a derecha y las <strong>verticales</strong>, de arriba abajo. El número entre paréntesis al final de cada pista dice cuántas letras tiene la palabra. Como en todos los pasatiempos, se escribe en mayúsculas y sin tildes; la Ñ sí se respeta.</p>
<p>Empieza por las pistas que sepas seguro: cada palabra que colocas deja letras en las que se apoyan las palabras que la cruzan. Si una se resiste, mira cuántas letras tiene y qué letras ya te han dejado las otras.</p>`;

const solucion = `
<h2>Con solución</h2>
<p>«Ver solución» muestra la cuadrícula resuelta con las letras en rojo, para imprimirla junto a la ficha o corregir después. El PDF trae cuatro crucigramas distintos y, al final, sus soluciones, cada una con el mismo número de ficha.</p>`;

const pagina = (slug, corto, title, desc, h1, entrada, banco, n, cuerpo, extra = {}) => Object.assign({
  cat: 'crucigramas', slug, corto, title, desc, h1, entrada,
  hojas: [{ tipo: 'crucigrama', titulo: h1.replace(/ para imprimir$/, ''), palabras: banco, n }],
  copias: 4,
  cuerpo: cuerpo + comoSeHace + solucion
}, extra);

module.exports = [
  pagina('', 'Crucigramas',
    'Crucigramas para imprimir gratis, con solución (PDF)',
    'Crucigramas para imprimir en A4 con solución: de cultura general, para niños, de animales, de Navidad y en inglés. PDF gratis o nuevos al momento.',
    'Crucigramas para imprimir',
    'Crucigramas de palabras cruzadas en A4, con las pistas debajo y la solución aparte. Este primero es de cultura general sobre España; más abajo los tienes para niños, de animales, de Navidad y en inglés. Cada vez que pulsas «Otra distinta», el programa coloca otras palabras en otra disposición.',
    variado, 14, `
<h2>Qué tipo de crucigrama es</h2>
<p>Son crucigramas de palabras cruzadas sin casillas negras: solo se dibujan las casillas que llevan letra, y las palabras se cruzan compartiendo una letra. Es el formato habitual en los cuadernos escolares y en los pasatiempos para ejercitar la memoria, porque se ve enseguida cuánto mide cada palabra y por dónde se cruza con las demás.</p>
<p>El de esta página mezcla geografía, arte, literatura y cocina de España: el Teide, el Guernica, Cervantes, el gazpacho. En cada hoja salen catorce palabras elegidas al azar entre treinta, así que dos fichas seguidas casi nunca coinciden.</p>
<h2>Para quién es</h2>
<p>Para adultos y adolescentes que quieren un rato de pasatiempo, y para mayores que buscan ejercitar la memoria: las pistas tratan de cultura general conocida, no de palabras rebuscadas de crucigrama de periódico. Para los más pequeños están los <a href="/crucigramas/para-ninos/">crucigramas para niños</a>, con vocabulario de primaria.</p>`,
    { nav: 'Crucigramas', resumen: 'Cultura general, niños, animales, Navidad e inglés', amazon: [['Libros de crucigramas', 'libro crucigramas'], ['Portaminas con goma', 'portaminas 0.7 con goma']] }),
  pagina('para-ninos', 'Para niños',
    'Crucigramas para niños para imprimir, con solución',
    'Crucigramas para niños de primaria para imprimir: pistas sencillas, palabras de su vocabulario y casillas grandes. Con solución, en PDF gratis.',
    'Crucigramas para niños para imprimir',
    'Crucigramas con pistas que un niño de primaria entiende solo: «animal que ladra», «tiene páginas y se lee», «lo llevamos en el pie para caminar». Doce palabras por hoja y casillas grandes para escribir con letra de niño.',
    ninos, 12, `
<h2>Para qué edad</h2>
<p>A partir de unos 7 años, cuando ya leen las pistas sin ayuda y escriben en mayúsculas con soltura. Con niños de 6 se pueden hacer juntos: el adulto lee la pista en voz alta y el niño piensa la palabra y la escribe. Las palabras son de vocabulario cotidiano y ninguna tiene más de ocho letras.</p>
<h2>Qué se trabaja</h2>
<p>Comprensión lectora, porque hay que entender la definición; ortografía, porque una letra equivocada no deja encajar la palabra que la cruza; y vocabulario, al relacionar una descripción con la palabra exacta. Es además una buena forma de que se acostumbren a contar letras y a comprobar su propio trabajo.</p>`),
  pagina('animales', 'Animales',
    'Crucigrama de animales para imprimir, con solución',
    'Crucigrama de animales para imprimir: pistas como «tiene trompa y orejas enormes» o «salta y lleva a su cría en una bolsa». Con solución, PDF gratis.',
    'Crucigrama de animales para imprimir',
    'Un crucigrama con animales de granja, de la selva, del mar y del bosque, con pistas que hablan de cómo son y qué hacen: el que lleva a su cría en una bolsa, el que duerme boca abajo, el que tiene ocho brazos con ventosas.',
    animales, 12, `
<h2>Los animales del crucigrama</h2>
<p>En cada hoja salen doce animales elegidos al azar entre más de treinta: del león, la jirafa o el canguro al pulpo, el murciélago y el flamenco. Las pistas no son solo adivinanzas: cada una cuenta un rasgo real del animal, así que el crucigrama sirve también para repasar Ciencias de la Naturaleza.</p>
<p>Una actividad para después: con la solución delante, clasificar los animales en mamíferos, aves, reptiles, peces, anfibios e insectos. La rana, el delfín y el murciélago suelen dar conversación.</p>
<p>Si te gustan los animales, también tienes la <a href="/sopas-de-letras/animales/">sopa de letras de animales</a>.</p>`),
  pagina('navidad', 'Navidad',
    'Crucigrama de Navidad para imprimir, con solución',
    'Crucigrama de Navidad para imprimir con vocabulario de aquí: belén, turrón, zambomba, cabalgata, roscón. Con solución y en PDF gratis.',
    'Crucigrama de Navidad para imprimir',
    'Un crucigrama con la Navidad española: el belén, la zambomba, las campanadas, el roscón y la cabalgata de Reyes. Para el último día de clase antes de vacaciones o para la sobremesa.',
    navidad, 12, `
<h2>Vocabulario de la Navidad de aquí</h2>
<p>Las palabras son las de una Navidad española, no una traducción de listas en inglés: Nochebuena y Nochevieja, polvorón y mazapán, paje y cabalgata, villancico y pandereta. Cada hoja toma doce de un banco de veintiséis.</p>
<p>Si buscas más fichas para estas fechas, en <a href="/navidad/">fichas de Navidad</a> están la carta a los Reyes Magos, el bingo de Navidad, el laberinto con forma de árbol y la <a href="/sopas-de-letras/navidad/">sopa de letras de Navidad</a>.</p>`),
  pagina('en-ingles', 'En inglés',
    'Crucigrama en inglés para imprimir, con solución (PDF)',
    'Crucigramas en inglés en dos niveles: pistas en español para primaria y pistas en inglés para secundaria. Vocabulario básico, con solución. PDF gratis.',
    'Crucigrama en inglés para imprimir',
    'Dos crucigramas para repasar vocabulario de inglés. En el primero la pista está en español («Perro», «Amarillo», «Lunes») y hay que escribir la palabra en inglés: es el de primaria. En el segundo, todo está en inglés («A pet that barks», «The first meal of the day»): para los últimos cursos de primaria y secundaria.',
    ingles, 12, `
<h2>Dos niveles</h2>
<p><strong>Pistas en español.</strong> Es un ejercicio de traducción directa con el vocabulario de los primeros cursos de primaria: colores, familia, animales, días de la semana, números y el colegio. Sirve a partir de tercero, cuando ya escriben en inglés con algo de soltura.</p>
<p><strong>Pistas en inglés.</strong> Aquí hay que entender una definición sencilla en inglés y encontrar la palabra: «The room where you sleep», «Ten times ten», «The opposite of sad». Obliga a leer y a pensar en inglés, sin pasar por el español. Va bien desde quinto o sexto de primaria y en los primeros cursos de la ESO.</p>
<h2>Cómo se usan en clase de inglés</h2>
<p>El crucigrama obliga a escribir cada palabra letra a letra, y eso fija la ortografía mejor que una lista de vocabulario: si el alumno escribe «YELOW», la palabra que cruza no encaja y se da cuenta solo. Funciona como repaso al final de una unidad, como tarea para casa o como actividad para los cinco últimos minutos de clase.</p>
<p>Las palabras se escriben en mayúsculas, así que «Monday» aparece como MONDAY. Conviene recordar que en inglés los días de la semana y los meses se escriben siempre con mayúscula inicial.</p>`,
    { hojas: [
      { tipo: 'crucigrama', titulo: 'Crucigrama en inglés', sub: 'Escribe en inglés cada palabra, una letra por casilla. Entre paréntesis, el número de letras.', palabras: ingles, n: 12 },
      { tipo: 'crucigrama', ingles: true, titulo: 'English crossword', sub: 'Write each word in the grid, one letter per square. Brackets show the number of letters.', palabras: inglesIngles, n: 12 }
    ], copias: 2 })
];
