// Sopas de letras. Para añadir una temática nueva, copia una entrada de `temas`
// y cambia slug, textos y lista de palabras: la página, el PDF y el sitemap salen solos.

const temas = [
  {
    slug: 'animales', corto: 'Animales', de: 'de animales',
    palabras: ['perro', 'gato', 'caballo', 'vaca', 'oveja', 'cerdo', 'gallina', 'conejo', 'león', 'tigre', 'elefante', 'jirafa', 'cebra', 'mono', 'lobo', 'zorro', 'ciervo', 'águila', 'búho', 'delfín', 'ballena', 'tiburón', 'tortuga', 'cocodrilo', 'serpiente', 'rana', 'mariposa', 'abeja', 'hormiga', 'pingüino', 'canguro'],
    cortas: ['perro', 'gato', 'vaca', 'oveja', 'cerdo', 'león', 'tigre', 'cebra', 'mono', 'lobo', 'zorro', 'búho', 'rana', 'abeja', 'pato', 'foca'],
    entrada: 'Dos sopas de letras de animales listas para imprimir: una de 13 × 13 con 14 animales de granja, de selva y de mar, y otra más pequeña para quien está empezando a leer.',
    nota: 'La lista mezcla animales domésticos, salvajes y marinos, así que sirve también para repasar vocabulario de Conocimiento del Medio: al terminar se puede pedir que clasifiquen los animales encontrados en mamíferos, aves, reptiles, peces e insectos.'
  },
  {
    slug: 'navidad', corto: 'Navidad', de: 'de Navidad',
    palabras: ['árbol', 'estrella', 'belén', 'turrón', 'polvorón', 'villancico', 'regalo', 'reyes', 'camello', 'pastor', 'ángel', 'nieve', 'trineo', 'reno', 'campana', 'guirnalda', 'mazapán', 'nochebuena', 'pandereta', 'zambomba', 'roscón', 'uvas', 'cabalgata', 'carbón'],
    cortas: ['árbol', 'belén', 'reyes', 'nieve', 'reno', 'uvas', 'regalo', 'ángel', 'turrón', 'pastor', 'roscón', 'carbón'],
    entrada: 'Sopas de letras de Navidad con vocabulario de aquí: belén, turrón, zambomba, roscón, cabalgata. Sirven para el último día de clase antes de vacaciones o para la sobremesa de Nochebuena.',
    nota: 'Las palabras son las de una Navidad española (Reyes Magos, uvas, polvorones), no una traducción de listas en inglés llenas de «muérdago» y «elfos». Si la imprimes para una comida familiar, saca una copia por persona y cronometrad quién termina antes. Tienes más fichas para estas fechas en <a href="/navidad/">fichas de Navidad</a>.'
  },
  {
    slug: 'frutas-y-verduras', corto: 'Frutas y verduras', de: 'de frutas y verduras',
    palabras: ['manzana', 'pera', 'plátano', 'naranja', 'limón', 'fresa', 'cereza', 'sandía', 'melón', 'uva', 'piña', 'kiwi', 'melocotón', 'ciruela', 'tomate', 'lechuga', 'zanahoria', 'cebolla', 'pimiento', 'pepino', 'calabaza', 'espinaca', 'brócoli', 'berenjena', 'patata', 'ajo'],
    cortas: ['pera', 'limón', 'fresa', 'melón', 'piña', 'kiwi', 'tomate', 'pepino', 'patata', 'uvas', 'cereza', 'sandía'],
    entrada: 'Sopas de letras de frutas y verduras para imprimir, con 14 alimentos escondidos en la versión normal y 10 en la fácil. Una buena excusa para hablar de lo que hay en la frutería.',
    nota: 'Funciona bien junto a una actividad de alimentación saludable: cada palabra encontrada se clasifica después en fruta o verdura (el tomate suele dar conversación), o se rodean las que han comido esa semana.'
  },
  {
    slug: 'colegio', corto: 'El colegio', de: 'del colegio',
    palabras: ['lápiz', 'goma', 'cuaderno', 'mochila', 'pizarra', 'tiza', 'regla', 'tijeras', 'pegamento', 'estuche', 'libro', 'recreo', 'maestra', 'pupitre', 'rotulador', 'sacapuntas', 'compás', 'mapa', 'patio', 'comedor', 'biblioteca', 'deberes', 'examen'],
    cortas: ['lápiz', 'goma', 'tiza', 'regla', 'libro', 'mapa', 'patio', 'recreo', 'mochila', 'estuche', 'compás', 'examen'],
    entrada: 'Sopas de letras con material escolar y rincones del colegio: estuche, pizarra, recreo, biblioteca. Pensadas para la vuelta al cole y para los primeros días de curso.',
    nota: 'Es una ficha cómoda para la primera semana de septiembre, cuando todavía no hay libros: no necesita explicación y deja ver quién lee con soltura y quién necesita más apoyo.'
  },
  {
    slug: 'halloween', corto: 'Halloween', de: 'de Halloween',
    palabras: ['bruja', 'fantasma', 'calabaza', 'murciélago', 'araña', 'esqueleto', 'vampiro', 'momia', 'zombi', 'caramelo', 'disfraz', 'escoba', 'telaraña', 'calavera', 'monstruo', 'caldero', 'susto', 'noche', 'luna', 'búho', 'cementerio', 'hechizo'],
    cortas: ['bruja', 'araña', 'momia', 'zombi', 'susto', 'noche', 'luna', 'búho', 'escoba', 'vampiro', 'disfraz', 'caldero'],
    entrada: 'Sopas de letras de Halloween para imprimir, con brujas, murciélagos y calabazas. Dan miedo lo justo: valen para clase y para una fiesta en casa.',
    nota: 'Para una fiesta, imprime una hoja por invitado y reparte caramelos según las palabras encontradas en cinco minutos. La versión fácil evita las diagonales, así los pequeños juegan en igualdad.'
  },
  {
    slug: 'deportes', corto: 'Deportes', de: 'de deportes',
    palabras: ['fútbol', 'baloncesto', 'tenis', 'natación', 'atletismo', 'ciclismo', 'balonmano', 'voleibol', 'gimnasia', 'judo', 'kárate', 'rugby', 'golf', 'pádel', 'esquí', 'patinaje', 'remo', 'surf', 'boxeo', 'esgrima', 'hockey', 'bádminton', 'escalada'],
    cortas: ['fútbol', 'tenis', 'judo', 'rugby', 'golf', 'pádel', 'esquí', 'remo', 'surf', 'boxeo', 'hockey', 'kárate'],
    entrada: 'Sopas de letras de deportes para imprimir: de fútbol y baloncesto a esgrima y bádminton. Útiles en Educación Física los días de lluvia.',
    nota: 'Todas las palabras se escriben en la cuadrícula sin tilde, como es costumbre en los pasatiempos: «fútbol» aparece como FUTBOL y «pádel» como PADEL. En la lista de abajo sí llevan su tilde.'
  }
];

const comoSeHace = `
<h2>Cómo se resuelve</h2>
<p>Las palabras de la lista están escondidas en la cuadrícula, siempre en línea recta. En la versión normal van en horizontal, en vertical y en diagonal, pero nunca al revés; en la fácil solo de izquierda a derecha y de arriba abajo. Cuando encuentres una, rodéala y marca su casilla en la lista.</p>
<p>Un método que funciona: elige una palabra, busca su primera letra por filas y mira las ocho casillas de alrededor hasta dar con la segunda. Las palabras largas y las que tienen letras poco frecuentes (Ñ, Z, J, K) son las más rápidas de localizar.</p>`;

const paginasTema = temas.map((t) => ({
  cat: 'sopas-de-letras', slug: t.slug, corto: t.corto,
  title: `Sopa de letras ${t.de} para imprimir (PDF)`,
  desc: `Sopa de letras ${t.de} lista para imprimir, en versión normal y fácil, con solución. PDF gratis o genera otra distinta con un clic.`,
  h1: `Sopa de letras ${t.de} para imprimir`,
  entrada: t.entrada,
  hojas: [
    { tipo: 'sopa', titulo: `Sopa de letras ${t.de}`, nivel: 'medio', tam: 13, nPalabras: 14, palabras: t.palabras },
    { tipo: 'sopa', titulo: `Sopa de letras ${t.de} (fácil)`, nivel: 'facil', tam: 10, nPalabras: 10, palabras: t.cortas }
  ],
  copias: 2,
  cuerpo: `
<h2>Qué palabras hay que buscar</h2>
<p>En cada hoja se esconden palabras tomadas al azar de esta lista, así que dos fichas distintas no repiten exactamente las mismas: ${t.palabras.join(', ')}.</p>
<p>${t.nota}</p>
${comoSeHace}
<h2>Versión normal y versión fácil</h2>
<p>La hoja normal tiene 13 × 13 letras y 14 palabras, y va bien a partir de 8 años. La fácil tiene 10 × 10 letras, 10 palabras cortas y ninguna diagonal: es la adecuada para 6 y 7 años o para quien hace su primera sopa de letras. El PDF incluye dos fichas de cada una y sus cuatro soluciones.</p>`,
  amazon: [['Subrayadores de colores', 'subrayadores colores pastel'], ['Libros de sopas de letras', 'libro sopas de letras']]
}));

module.exports = [
  {
    cat: 'sopas-de-letras', slug: '', corto: 'Sopas de letras', nav: 'Sopas de letras',
    title: 'Sopas de letras para imprimir gratis en PDF',
    desc: 'Sopas de letras para imprimir en A4, con solución. Elige tema o dificultad, descarga el PDF o genera una sopa nueva cada vez que quieras.',
    h1: 'Sopas de letras para imprimir',
    resumen: 'Por temas y por dificultad, con solución',
    entrada: 'Cada sopa de letras de esta página se genera por ordenador, así que no hay dos iguales: imprime la que ves, descarga el PDF con cuatro fichas o pulsa «Otra distinta» hasta dar con una que te guste. Todas caben en un A4 y llevan su solución.',
    hojas: [{
      tipo: 'sopa', titulo: 'Sopa de letras: la casa', nivel: 'medio', tam: 14, nPalabras: 16,
      palabras: ['ventana', 'puerta', 'cocina', 'salón', 'pasillo', 'terraza', 'escalera', 'tejado', 'chimenea', 'armario', 'espejo', 'lámpara', 'alfombra', 'cortina', 'sofá', 'mesa', 'silla', 'cama', 'almohada', 'nevera', 'horno', 'bañera', 'grifo', 'buzón', 'timbre', 'garaje', 'jardín', 'balcón']
    }],
    copias: 4,
    cuerpo: `
<h2>Cómo elegir la dificultad</h2>
<p>La dificultad de una sopa de letras depende de tres cosas: el tamaño de la cuadrícula, cuántas palabras hay y en qué direcciones pueden ir. Aquí están ordenadas así:</p>
<ul>
<li><strong>Fáciles</strong>: cuadrícula de 8 × 8 o 10 × 10, palabras cortas, solo en horizontal y vertical. Para primeros lectores, de 5 a 7 años.</li>
<li><strong>Normales</strong>: 13 × 13 o 14 × 14, con diagonales pero sin palabras al revés. A partir de 8 años y para adultos que quieren algo relajado.</li>
<li><strong>Difíciles</strong>: 18 × 18, más de 20 palabras y las ocho direcciones posibles, también de derecha a izquierda y de abajo arriba.</li>
</ul>
${comoSeHace}
<h2>Por qué en la cuadrícula no hay tildes</h2>
<p>Es la convención de casi todos los pasatiempos en español: las letras se escriben en mayúscula y sin tilde, para que «CAMIÓN» no delate su posición con una Ó. La Ñ sí se mantiene porque es una letra distinta, no una N con adorno. En la lista de palabras de cada ficha verás la ortografía correcta.</p>
<h2>Consejos para imprimir</h2>
<p>Las fichas están pensadas para A4 en vertical y en blanco y negro; no gastan tinta de color. Si tu impresora recorta los bordes, activa «Ajustar a la página». Para letra más grande (personas mayores o con baja visión) elige las sopas fáciles: al tener menos casillas, cada letra mide casi el doble.</p>`,
    faq: [
      ['¿Las sopas de letras tienen solución?', 'Sí. Pulsa «Ver solución» para mostrarla en pantalla e imprimirla junto a la ficha. El PDF descargable lleva las soluciones en las últimas páginas, cada una con el mismo número de ficha que su sopa.'],
      ['¿Puedo usarlas en clase o en un taller?', 'Sí, puedes imprimir y fotocopiar las fichas libremente para uso personal, en el aula, en residencias o en talleres. Lo único que no está permitido es revenderlas o republicarlas en otra web.'],
      ['¿Puede salir una palabra repetida por casualidad?', 'No. Después de rellenar los huecos con letras al azar, el generador repasa la cuadrícula y deshace cualquier copia accidental de una palabra de la lista, para que cada una aparezca una sola vez.']
    ],
    amazon: [['Libros de sopas de letras en letra grande', 'sopas de letras letra grande'], ['Subrayadores de colores', 'subrayadores colores pastel']]
  },
  ...paginasTema,
  {
    cat: 'sopas-de-letras', slug: 'faciles', corto: 'Fáciles para niños',
    title: 'Sopas de letras fáciles para niños, para imprimir',
    desc: 'Sopas de letras fáciles para niños de 5 a 7 años: cuadrícula pequeña, letra grande y palabras cortas sin diagonales. Con solución y PDF gratis.',
    h1: 'Sopas de letras fáciles para niños',
    entrada: 'Sopas de letras de 8 × 8 con letra muy grande y ocho palabras cortas que solo van de izquierda a derecha o de arriba abajo. Son las adecuadas para niños que acaban de aprender a leer.',
    hojas: [
      { tipo: 'sopa', titulo: 'Sopa de letras fácil: animales', nivel: 'facil', tam: 8, nPalabras: 8, palabras: ['perro', 'gato', 'vaca', 'oveja', 'pato', 'león', 'mono', 'lobo', 'rana', 'búho', 'foca', 'tigre', 'cebra', 'zorro'] },
      { tipo: 'sopa', titulo: 'Sopa de letras fácil: colores', nivel: 'facil', tam: 8, nPalabras: 8, palabras: ['rojo', 'azul', 'verde', 'rosa', 'gris', 'negro', 'blanco', 'marrón', 'lila', 'dorado', 'morado', 'naranja'] }
    ],
    copias: 2,
    cuerpo: `
<h2>Qué las hace fáciles</h2>
<p>Una cuadrícula de 8 × 8 tiene 64 letras; una normal de 13 × 13 tiene 169. Con tan pocas casillas, cada letra mide más de dos centímetros en el papel y el niño puede recorrer las filas con el dedo. Además, las palabras se leen siempre en el sentido natural de la lectura: ninguna va al revés ni en diagonal.</p>
<p>Las palabras tienen entre cuatro y siete letras y pertenecen a vocabulario que un niño de primero de primaria ya conoce: animales y colores.</p>
<h2>Cómo acompañar a un niño que empieza</h2>
<p>Lee con él la lista antes de empezar. Proponle buscar primero la letra inicial de una palabra y comprobar después la letra de al lado y la de abajo. Si se atasca, dile en qué fila o columna está la palabra en lugar de señalársela: el objetivo es que practique el rastreo visual, que es la misma destreza que usa al leer una línea de texto.</p>
<p>Cuando estas le resulten sencillas, el siguiente paso son las <a href="/sopas-de-letras/animales/">sopas por temas</a>, que traen una versión de 10 × 10 y otra de 13 × 13 con diagonales.</p>`
  },
  {
    cat: 'sopas-de-letras', slug: 'dificiles', corto: 'Difíciles',
    title: 'Sopas de letras difíciles para imprimir (18 × 18)',
    desc: 'Sopas de letras difíciles para adultos: 18 × 18 letras, 24 palabras y ocho direcciones, también al revés. Con solución, en PDF o recién generada.',
    h1: 'Sopas de letras difíciles para imprimir',
    entrada: 'Una cuadrícula de 18 × 18, 24 ciudades españolas escondidas y las ocho direcciones permitidas: horizontal, vertical y diagonal, del derecho y del revés. Para quien encuentra las sopas normales demasiado rápidas.',
    hojas: [{
      tipo: 'sopa', titulo: 'Sopa de letras difícil: ciudades', nivel: 'dificil', tam: 18, nPalabras: 24, nombre: false,
      palabras: ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 'Málaga', 'Murcia', 'Bilbao', 'Alicante', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón', 'Granada', 'Oviedo', 'Pamplona', 'Almería', 'Burgos', 'Santander', 'Castellón', 'Albacete', 'Logroño', 'Badajoz', 'Salamanca', 'Huelva', 'Lleida', 'Tarragona', 'León', 'Cádiz', 'Jaén', 'Ourense', 'Girona', 'Lugo', 'Cáceres', 'Toledo', 'Segovia', 'Zamora', 'Teruel', 'Cuenca', 'Ávila']
    }],
    copias: 4,
    cuerpo: `
<h2>Por qué cuestan más</h2>
<p>En una sopa normal solo hay que leer en cuatro direcciones. Aquí son ocho, y las palabras escritas de derecha a izquierda o de abajo arriba no se reconocen de un vistazo: hay que deletrearlas. A eso se suman 324 letras en la cuadrícula y palabras que se cruzan compartiendo letras.</p>
<h2>Técnica para sopas grandes</h2>
<p>Empieza por las palabras con letras raras. En esta lista, la Z de Zaragoza, Badajoz o Cádiz, la Ñ de Logroño y la J de Gijón o Jaén aparecen pocas veces en la cuadrícula, así que basta localizarlas y mirar alrededor. Deja para el final las palabras cortas con letras comunes, como León o Lugo, que son las que más se camuflan.</p>
<p>Otra opción es barrer la cuadrícula fila a fila buscando parejas de letras características («LL», «RR», «GR») en lugar de palabras enteras.</p>
<h2>Las palabras de esta sopa</h2>
<p>Cada ficha esconde 24 ciudades elegidas al azar entre cuarenta capitales y ciudades grandes de España, por lo que al pulsar «Otra distinta» cambian tanto las posiciones como la lista. Como en todos los pasatiempos, en la cuadrícula se escriben sin tilde.</p>`
  }
];
