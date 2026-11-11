// Sudokus, laberintos y bingo.

const reglasSudoku = `
<h2>Reglas del sudoku</h2>
<p>Hay que rellenar todas las casillas vacías de modo que cada fila, cada columna y cada caja de 3 × 3 contenga los números del 1 al 9 una sola vez. No hace falta ninguna operación matemática: los números podrían ser letras o dibujos, lo que cuenta es la lógica.</p>`;

const amazonSudoku = [['Libros de sudokus', 'libro sudokus'], ['Portaminas con goma', 'portaminas 0.7 con goma']];

const lab = (slug, corto, singular, cols, filas, edad, texto, extra) => ({
  cat: 'laberintos', slug, corto,
  title: `Laberintos ${corto.toLowerCase()} para imprimir, con solución`,
  desc: `Laberintos ${corto.toLowerCase()} para imprimir en A4 (${cols} × ${filas} casillas), ${edad}. Con solución, en PDF gratis o generados al momento.`,
  h1: `Laberintos ${corto.toLowerCase()} para imprimir`,
  entrada: texto,
  hojas: [{ tipo: 'laberinto', titulo: `Laberinto ${singular}`, cols, filas }],
  copias: 4,
  cuerpo: extra + `
<h2>Cómo imprimirlos</h2>
<p>Caben en un A4 vertical y solo usan tinta negra. El PDF trae cuatro laberintos distintos de este tamaño y, al final, sus soluciones con el camino en rojo; el número de ficha de la esquina inferior te dice qué solución corresponde a cada uno. Si necesitas más, pulsa «Otra distinta» e imprime directamente desde el navegador.</p>
<p>Todos son laberintos con un único camino entre la entrada y la salida, sin bucles: siempre tienen solución y solo una.</p>`
});

module.exports = [
  // ---------------- SUDOKUS ----------------
  {
    cat: 'sudokus', slug: '', corto: 'Sudokus', nav: 'Sudokus',
    title: 'Sudokus para imprimir gratis en PDF (4 por hoja)',
    desc: 'Sudokus para imprimir en A4, cuatro por hoja y con solución. Fáciles, medios, difíciles y para niños. Descarga el PDF o genera sudokus nuevos.',
    h1: 'Sudokus para imprimir',
    resumen: 'Fáciles, medios, difíciles y para niños',
    entrada: 'Cuatro sudokus por hoja, en A4 y con casillas lo bastante grandes para escribir candidatos a lápiz. Todos tienen solución única, comprobada por el programa que los genera, y puedes pedir una hoja nueva tantas veces como quieras.',
    hojas: [{ tipo: 'sudoku', n: 9, nivel: 'medio', titulo: 'Sudokus de nivel medio' }],
    copias: 4,
    cuerpo: `
${reglasSudoku}
<h2>Qué nivel elegir</h2>
<p>La dificultad se regula aquí por el número de casillas que vienen ya rellenas. Es una medida sencilla y honesta, aunque no perfecta: dos sudokus con las mismas pistas pueden exigir técnicas distintas.</p>
<ul>
<li><strong>Fáciles</strong>: unas 38 pistas de 81. Se resuelven buscando la única casilla posible para cada número.</li>
<li><strong>Medios</strong>: unas 31 pistas. Conviene anotar candidatos en pequeño.</li>
<li><strong>Difíciles</strong>: entre 26 y 28 pistas. Requieren paciencia y técnicas como las parejas.</li>
<li><strong>Para niños</strong>: cuadrículas de 4 × 4 y 6 × 6, con números del 1 al 4 o del 1 al 6.</li>
</ul>
<h2>Cómo empezar un sudoku</h2>
<p>Busca el número que más veces aparece ya en el tablero y recorre las cajas donde falta: las filas y columnas que ya lo contienen descartan casillas, y a menudo solo queda un hueco posible. Repite con el siguiente número. Cuando ese método deje de dar resultados, escribe en pequeño los candidatos de las casillas que tengan solo dos o tres opciones y busca las que se quedan con una.</p>
<p>Usa lápiz y ten una goma a mano. Si llegas a una contradicción (dos números iguales en una fila), el error casi siempre viene de una casilla rellenada por intuición.</p>
<h2>Solución única</h2>
<p>Un sudoku bien hecho solo admite una solución. Al generar cada rejilla, el programa quita números de uno en uno y comprueba tras cada retirada que el sudoku sigue teniendo una única solución; si no, devuelve el número a su sitio. Por eso nunca tendrás que adivinar.</p>`,
    faq: [
      ['¿Cuántos sudokus hay en cada hoja?', 'Cuatro por A4. Con ese tamaño cada casilla mide casi un centímetro, suficiente para escribir el número y los candidatos. El PDF trae cuatro hojas (16 sudokus) y sus soluciones.'],
      ['¿Dónde está la solución?', 'Pulsa «Ver solución» y aparecerá otra hoja con las cuatro rejillas resueltas; los números que había que averiguar salen en rojo. En el PDF, las soluciones van al final.'],
      ['¿Se repiten los sudokus?', 'En la práctica, no. Cada vez que pulsas «Otra distinta» se generan cuatro rejillas nuevas a partir de un número de ficha al azar entre más de cuatro mil millones.']
    ],
    amazon: amazonSudoku
  },
  {
    cat: 'sudokus', slug: 'faciles', corto: 'Fáciles',
    title: 'Sudokus fáciles para imprimir, con solución (PDF)',
    desc: 'Sudokus fáciles para imprimir: 9 × 9 con unas 38 pistas, cuatro por hoja y con solución. Ideales para principiantes. PDF gratis con 16 sudokus.',
    h1: 'Sudokus fáciles para imprimir',
    entrada: 'Sudokus de 9 × 9 con cerca de la mitad de las casillas ya rellenas. Se resuelven sin anotar candidatos, solo descartando, así que son los adecuados para aprender o para un rato sin complicaciones.',
    hojas: [{ tipo: 'sudoku', n: 9, nivel: 'facil', titulo: 'Sudokus fáciles' }],
    copias: 4,
    cuerpo: `
${reglasSudoku}
<h2>El método para resolverlos</h2>
<p>En un sudoku fácil basta una sola técnica, que suele llamarse «único oculto». Elige un número, por ejemplo el 5, y mira una caja de 3 × 3 donde falte. Tacha mentalmente las filas y columnas que ya tienen un 5: si en la caja solo queda una casilla libre, ahí va. Hazlo con los nueve números y vuelve a empezar; cada casilla que rellenas abre otras.</p>
<p>Cuando una fila, columna o caja tenga ocho números puestos, el noveno es inmediato. Conviene revisar esos casos de vez en cuando.</p>
<h2>Para quién son</h2>
<p>Para principiantes de cualquier edad, a partir de unos 9 o 10 años. Si a un niño le resultan largos, prueba antes los <a href="/sudokus/para-ninos/">sudokus de 4 × 4 y 6 × 6</a>. Si se te quedan cortos, pasa a los de <a href="/sudokus/medios/">nivel medio</a>.</p>`,
    amazon: amazonSudoku
  },
  {
    cat: 'sudokus', slug: 'medios', corto: 'Nivel medio',
    title: 'Sudokus de nivel medio para imprimir, con solución',
    desc: 'Sudokus de nivel medio para imprimir: 9 × 9 con unas 31 pistas, cuatro por hoja y solución incluida. PDF gratis con 16 sudokus o genera más.',
    h1: 'Sudokus de nivel medio para imprimir',
    entrada: 'Con unas 31 casillas de partida, estos sudokus ya no salen solo descartando: en algún momento tendrás que anotar candidatos. Es el nivel habitual de los pasatiempos de periódico.',
    hojas: [{ tipo: 'sudoku', n: 9, nivel: 'medio', titulo: 'Sudokus de nivel medio' }],
    copias: 4,
    cuerpo: `
${reglasSudoku}
<h2>Qué cambia respecto a los fáciles</h2>
<p>Los primeros números se colocan igual, buscando la única casilla posible para cada cifra dentro de una caja. La diferencia llega a mitad de partida, cuando ese recurso se agota. Entonces toca escribir en pequeño, en la esquina de cada casilla vacía, los números que todavía podrían ir en ella.</p>
<p>Con los candidatos anotados aparecen dos situaciones útiles. La primera, una casilla con un solo candidato: se rellena. La segunda, un número que dentro de una fila, columna o caja solo figura como candidato en una casilla: también se rellena, aunque esa casilla tenga más candidatos apuntados.</p>
<h2>Un consejo sobre las anotaciones</h2>
<p>No anotes todo el tablero de golpe. Empieza por las filas, columnas y cajas más llenas, donde quedan dos o tres huecos, y borra candidatos cada vez que coloques un número. Las casillas de estas hojas miden unos 9 mm, espacio suficiente para tres o cuatro cifras pequeñas.</p>`,
    amazon: amazonSudoku
  },
  {
    cat: 'sudokus', slug: 'dificiles', corto: 'Difíciles',
    title: 'Sudokus difíciles para imprimir, con solución (PDF)',
    desc: 'Sudokus difíciles para imprimir: 9 × 9 con solo 26-28 pistas, solución única garantizada, cuatro por hoja. PDF gratis con 16 sudokus y soluciones.',
    h1: 'Sudokus difíciles para imprimir',
    entrada: 'Entre 26 y 28 pistas de 81. El programa retira números mientras el sudoku conserve una única solución, de modo que cada rejilla queda cerca del mínimo que admite su disposición.',
    hojas: [{ tipo: 'sudoku', n: 9, nivel: 'dificil', titulo: 'Sudokus difíciles' }],
    copias: 4,
    cuerpo: `
${reglasSudoku}
<h2>Técnicas que vas a necesitar</h2>
<p><strong>Parejas desnudas.</strong> Si en una fila, columna o caja hay dos casillas cuyos únicos candidatos son los mismos dos números (por ejemplo 3 y 7), esos dos números irán ahí en algún orden, y puedes borrarlos como candidatos del resto de esa fila, columna o caja.</p>
<p><strong>Candidatos alineados.</strong> Si dentro de una caja un número solo puede ir en casillas de una misma fila, ese número queda descartado en el resto de esa fila fuera de la caja. Vale igual para columnas.</p>
<p><strong>Parejas ocultas.</strong> Si dos números solo aparecen como candidatos en las mismas dos casillas de una unidad, esas casillas no pueden contener nada más, y se borran sus demás candidatos.</p>
<h2>Sobre el nivel real</h2>
<p>La dificultad está medida por el número de pistas, no por las técnicas necesarias. La mayoría de estas rejillas se resuelven con las tres técnicas de arriba, pero alguna puede resultar más llevadera de lo esperado y otra pedir algo más. Lo que sí está garantizado es que la solución es única y que se puede comprobar al final.</p>`,
    amazon: amazonSudoku
  },
  {
    cat: 'sudokus', slug: 'para-ninos', corto: 'Para niños (4 × 4 y 6 × 6)',
    title: 'Sudokus para niños para imprimir: 4 × 4 y 6 × 6',
    desc: 'Sudokus para niños listos para imprimir: 4 × 4 desde 5 años y 6 × 6 desde 7, con casillas grandes y solución. PDF gratis o genera hojas nuevas.',
    h1: 'Sudokus para niños para imprimir',
    entrada: 'Dos tamaños pensados para primaria: el 4 × 4, con números del 1 al 4, y el 6 × 6, con números del 1 al 6. Las reglas son las mismas que en el sudoku de adultos, pero cada rejilla se termina en pocos minutos.',
    hojas: [
      { tipo: 'sudoku', n: 4, nivel: 'facil', titulo: 'Sudokus 4 × 4 para niños' },
      { tipo: 'sudoku', n: 6, nivel: 'facil', titulo: 'Sudokus 6 × 6 para niños' }
    ],
    copias: 2,
    cuerpo: `
<h2>Cómo explicárselo a un niño</h2>
<p>En el de 4 × 4 basta una frase: «en cada fila, en cada columna y en cada cuadrado gordo tienen que estar el 1, el 2, el 3 y el 4, sin repetir ninguno». Empezad juntos por una fila a la que solo le falte un número y preguntad cuál no está todavía.</p>
<p>En el de 6 × 6 las cajas son rectángulos de dos filas por tres columnas. La idea es idéntica, con los números del 1 al 6.</p>
<h2>A qué edad</h2>
<p>Como orientación: el 4 × 4 se puede proponer desde los 5 o 6 años, en cuanto reconocen las cifras; el 6 × 6, desde los 7 u 8. Cuando resuelvan el 6 × 6 sin ayuda, ya pueden intentar un <a href="/sudokus/faciles/">sudoku fácil de 9 × 9</a>.</p>
<h2>Qué se trabaja</h2>
<p>El sudoku no es cálculo: es razonamiento por descarte. El niño practica mantener varias condiciones a la vez (fila, columna y caja), comprobar antes de escribir y corregir cuando algo no encaja. Por eso conviene que use lápiz y que la goma no se viva como un fracaso.</p>`
  },

  // ---------------- LABERINTOS ----------------
  {
    cat: 'laberintos', slug: '', corto: 'Laberintos', nav: 'Laberintos',
    title: 'Laberintos para imprimir gratis, con solución',
    desc: 'Laberintos para imprimir en A4: fáciles para niños pequeños, medios y difíciles. Con solución, en PDF gratis o recién generados, siempre distintos.',
    h1: 'Laberintos para imprimir',
    resumen: 'Tres tamaños, de infantil a adultos',
    entrada: 'Laberintos de pasillos rectos que ocupan toda la hoja, con la entrada arriba a la izquierda y la salida abajo a la derecha. Cada uno tiene un único camino correcto y se genera en el momento, así que nunca repetirás el mismo.',
    hojas: [{ tipo: 'laberinto', titulo: 'Laberinto', cols: 18, filas: 22 }],
    copias: 4,
    cuerpo: `
<h2>Tres tamaños</h2>
<ul>
<li><strong>Fáciles</strong>: 10 × 12 casillas, con pasillos de casi dos centímetros de ancho. Para infantil y primero de primaria.</li>
<li><strong>Medios</strong>: 18 × 22 casillas, pasillos de un centímetro. De 7 a 10 años.</li>
<li><strong>Difíciles</strong>: 30 × 37 casillas, más de mil cien en total. Para mayores de 10 años y adultos.</li>
</ul>
<h2>Cómo están hechos</h2>
<p>Son laberintos «perfectos»: entre dos puntos cualesquiera existe un camino y solo uno, sin bucles ni zonas aisladas. Eso significa que la salida siempre es alcanzable y que la solución es única. El programa excava los pasillos avanzando al azar y retrocediendo cuando no puede seguir, un método que produce recorridos largos y sinuosos con pocos callejones cortos.</p>
<h2>Trucos para resolverlos</h2>
<p>El más conocido es el de la mano en la pared: si apoyas una mano en una pared y no la despegas nunca, acabas llegando a la salida. En estos laberintos funciona siempre, aunque rara vez da el camino más corto. Otro recurso es empezar por la salida y avanzar hacia la entrada: a veces el final tiene menos bifurcaciones que el principio.</p>
<p>Con niños pequeños, propón que primero recorran el camino con el dedo y solo después lo marquen con lápiz o rotulador.</p>`,
    faq: [
      ['¿Para qué sirven los laberintos en infantil?', 'Trabajan el trazo y el control del lápiz dentro de un pasillo, que es una preparación directa para la escritura, además de la planificación: mirar adónde lleva un camino antes de dibujarlo.'],
      ['¿Tienen solución?', 'Sí. «Ver solución» añade una hoja con el recorrido correcto en rojo, y el PDF la incluye al final.']
    ],
    amazon: [['Rotuladores de punta fina', 'rotuladores punta fina colores'], ['Libros de laberintos para niños', 'libro laberintos niños']]
  },
  lab('faciles', 'Fáciles', 'fácil', 10, 12, 'para niños de 4 a 6 años',
    'Laberintos de 10 × 12 casillas con pasillos de 18 mm de ancho, pensados para manos pequeñas: cabe de sobra un lápiz grueso o una cera, y el camino se resuelve en un par de minutos.',
    `<h2>Para qué edad</h2>
<p>De 4 a 6 años, como orientación. A esa edad el reto no es solo encontrar el camino, sino trazarlo sin salirse: los pasillos anchos permiten hacerlo con ceras, rotuladores gruesos o incluso con el dedo mojado en pintura. Antes de dibujar, pide al niño que siga el recorrido con el dedo; así separa las dos tareas, pensar y trazar.</p>
<p>Cuando los resuelva a la primera, pasa a los <a href="/laberintos/medios/">laberintos medios</a>, con pasillos de un centímetro.</p>`),
  lab('medios', 'Medios', 'medio', 18, 22, 'para niños de 7 a 10 años',
    'Laberintos de 18 × 22 casillas, con pasillos de un centímetro. Tienen suficientes bifurcaciones para obligar a pensar, pero se terminan sin frustración en cinco o diez minutos.',
    `<h2>Para qué edad</h2>
<p>De 7 a 10 años aproximadamente. Con casi 400 casillas ya no se ve la solución de un vistazo: hay que explorar, equivocarse y volver atrás. Es buen momento para enseñar a marcar con un punto los callejones ya descartados, en lugar de borrarlo todo y empezar de nuevo.</p>
<p>Si se quedan pequeños, los <a href="/laberintos/dificiles/">laberintos difíciles</a> triplican el número de casillas; si resultan largos, vuelve a los <a href="/laberintos/faciles/">fáciles</a>.</p>`),
  lab('dificiles', 'Difíciles', 'difícil', 30, 37, 'para mayores y adultos',
    'Laberintos de 30 × 37 casillas, 1.110 en total, con pasillos de 6 mm. El camino correcto suele recorrer buena parte de la hoja y hay callejones largos que parecen prometedores.',
    `<h2>Cómo abordarlos</h2>
<p>Con más de mil casillas, ir probando a ciegas lleva mucho tiempo. Ayuda trabajar desde los dos extremos: avanza un tramo desde la entrada, otro desde la salida, y busca dónde pueden encontrarse. Otra técnica es rellenar con lápiz los callejones sin salida que veas claros; a medida que los cierras, el camino bueno va quedando a la vista.</p>
<p>Usa un lápiz fino o un portaminas: los pasillos miden 6 mm y un rotulador grueso tapa las paredes.</p>`),

  // ---------------- BINGO ----------------
  {
    cat: 'bingo', slug: '', corto: 'Bingo', nav: 'Bingo',
    title: 'Cartones de bingo para imprimir gratis (90 bolas)',
    desc: 'Cartones de bingo de 90 bolas para imprimir, seis por hoja A4 y todos distintos. Descarga el PDF con 24 cartones o genera los que necesites.',
    h1: 'Cartones de bingo para imprimir',
    resumen: 'Cartones de 90 y 75 bolas y números para recortar',
    entrada: 'Seis cartones de bingo tradicional por hoja, con el formato que se usa en España: tres filas, nueve columnas y quince números. Cada vez que pulsas «Otra distinta» salen seis cartones nuevos, así que puedes imprimir tantos como jugadores tengas.',
    hojas: [{ tipo: 'bingo90', titulo: 'Cartones de bingo' }],
    copias: 4,
    cuerpo: `
<h2>Cómo es un cartón de bingo de 90 bolas</h2>
<p>Cada cartón tiene 27 casillas en tres filas y nueve columnas. En cada fila hay cinco números y cuatro huecos, de modo que el cartón suma quince números. Las columnas van por decenas: en la primera están los números del 1 al 9, en la segunda del 10 al 19, y así hasta la novena, que va del 80 al 90. Dentro de cada columna, los números están ordenados de menor a mayor.</p>
<p>Los cartones de esta página cumplen todas esas reglas y ninguna columna queda vacía.</p>
<h2>Cómo se juega</h2>
<ol>
<li>Cada jugador recibe uno o varios cartones y algo para marcar: un rotulador, garbanzos, botones o fichas.</li>
<li>Una persona saca los números de uno en uno, del bombo o de una bolsa, y los canta en voz alta.</li>
<li>Quien completa primero los cinco números de una fila canta <strong>línea</strong>.</li>
<li>Quien tacha primero los quince números de su cartón canta <strong>bingo</strong> y gana.</li>
</ol>
<p>Antes de dar un premio, comprueba el cartón con los números que han salido; para eso conviene ir dejándolos ordenados sobre la mesa.</p>
<h2>Si no tienes bombo</h2>
<p>Imprime la hoja de <a href="/bingo/numeros-para-recortar/">números del 1 al 90 para recortar</a>, dobla los papeles y mételos en una bolsa. También sirve cualquier aplicación gratuita de «bombo de bingo» en el móvil.</p>
<h2>Cuántos cartones imprimir</h2>
<p>Uno o dos por jugador es lo habitual. Con pocos jugadores, repartir dos o tres cartones a cada uno acorta la partida. Para reutilizarlos, plastifica las hojas o mételas en fundas de plástico y marca con rotulador borrable; si prefieres usar garbanzos o fichas, no hace falta nada más.</p>`,
    faq: [
      ['¿Pueden salir dos cartones iguales?', 'Es prácticamente imposible. Cada cartón se genera al azar entre millones de combinaciones, y dos jugadores solo empatarían de verdad con cartones idénticos. Lo que sí es normal es que varios cartones compartan algunos números, igual que en el bingo de verdad.'],
      ['¿Sirven para un bingo benéfico o de fiesta de pueblo?', 'Para jugar entre familia, amigos, en clase o en una residencia, sí. Un bingo con dinero y abierto al público es un juego regulado que necesita autorización de la comunidad autónoma; para eso consulta la normativa de la tuya.'],
      ['¿Cómo recorto los cartones?', 'Entre cartón y cartón hay una línea discontinua. Con una regla y un cúter salen los seis en tres cortes; con tijeras, corta primero la hoja por la mitad.']
    ],
    amazon: [['Bombo de bingo con bolas', 'bombo bingo con bolas'], ['Fichas para marcar cartones', 'fichas bingo transparentes'], ['Fundas para plastificar A4', 'fundas plastificar A4']]
  },
  {
    cat: 'bingo', slug: 'cartones-75-bolas', corto: 'Cartones de 75 bolas',
    title: 'Cartones de bingo de 75 bolas para imprimir (5 × 5)',
    desc: 'Cartones de bingo americano de 75 bolas para imprimir: 5 × 5 con casilla libre central, cuatro por hoja A4. PDF gratis con 16 cartones distintos.',
    h1: 'Cartones de bingo de 75 bolas',
    entrada: 'El bingo de 75 bolas, o bingo americano, usa cartones cuadrados de 5 × 5 con las letras B-I-N-G-O arriba y una casilla libre en el centro. Aquí tienes cuatro por hoja, todos distintos.',
    hojas: [{ tipo: 'bingo75', titulo: 'Bingo de 75 bolas' }],
    copias: 4,
    cuerpo: `
<h2>Cómo es el cartón</h2>
<p>Cada columna tiene su propio rango de números: la B va del 1 al 15, la I del 16 al 30, la N del 31 al 45, la G del 46 al 60 y la O del 61 al 75. El cartón tiene 24 números y una casilla central marcada como «libre», que cuenta como tachada desde el principio.</p>
<h2>En qué se diferencia del bingo de 90</h2>
<p>En el bingo tradicional español se canta línea y bingo. En el de 75 bolas se puede ganar con más figuras, que se acuerdan antes de empezar: una línea horizontal, vertical o diagonal, las cuatro esquinas, una X, un marco o el cartón lleno. Los números se cantan con su letra («B-7», «G-52»), lo que ayuda a encontrarlos rápido.</p>
<p>Al tener menos bolas y cartones más pequeños, las partidas son más cortas. Es el formato habitual en los bingos de clase de inglés.</p>
<h2>Qué necesitas para jugar</h2>
<p>Un juego de bolas o papeles numerados del 1 al 75 y fichas para marcar. Si no tienes bombo de 75 bolas, numera 75 papeles o usa una aplicación de sorteo. Los <a href="/bingo/">cartones de 90 bolas</a> no sirven para este juego, porque sus columnas van por decenas.</p>`,
    amazon: [['Bombo de bingo con bolas', 'bombo bingo 75 bolas'], ['Fichas para marcar cartones', 'fichas bingo transparentes']]
  },
  {
    cat: 'bingo', slug: 'numeros-para-recortar', corto: 'Números para recortar',
    title: 'Números de bingo del 1 al 90 para imprimir y recortar',
    desc: 'Hoja con los números de bingo del 1 al 90 para imprimir y recortar. Sustituye al bombo: recorta, dobla, mete en una bolsa y empieza a cantar.',
    h1: 'Números de bingo del 1 al 90 para recortar',
    entrada: 'Si tienes cartones pero no bombo, esta hoja lo resuelve: noventa casillas numeradas con línea de corte. Recórtalas, dóblalas y sácalas de una bolsa o de un bol.',
    hojas: [{ tipo: 'bingo-numeros', titulo: 'Números del 1 al 90' }],
    copias: 1,
    cuerpo: `
<h2>Cómo prepararlos</h2>
<p>Imprime la hoja en papel normal o, mejor, en cartulina de 160 a 200 gramos para que los números duren más y no se transparenten. Cada casilla mide 18 × 18 mm. Con cúter y regla se recortan en una veintena de cortes rectos; con tijeras, corta primero las tiras horizontales y luego cada número.</p>
<p>El 6 y el 9 llevan una raya debajo para saber cuál es cuál cuando salgan del revés.</p>
<h2>Dos usos de la misma hoja</h2>
<p>Imprime dos copias. Una se recorta para sacar los números; la otra se deja entera sobre la mesa como tablero de control, y sobre ella se va colocando cada número cantado. Así comprobar una línea o un bingo es cuestión de segundos.</p>
<p>Para jugar necesitarás también los <a href="/bingo/">cartones de bingo de 90 bolas</a>.</p>`,
    amazon: [['Cartulina blanca A4', 'cartulina blanca A4 180g'], ['Bombo de bingo con bolas', 'bombo bingo con bolas']]
  }
];
