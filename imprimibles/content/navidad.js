// Sección de Navidad. Pasadas las fiestas (después de Reyes), se puede mover al final
// del menú cambiando el orden en content/index.js; las URL no cambian.

const palabrasBingo = ['estrella', 'árbol', 'belén', 'turrón', 'regalo', 'Reyes Magos', 'camello', 'pastor', 'ángel', 'nieve', 'trineo', 'reno', 'campana', 'vela', 'bola', 'calcetín', 'polvorón', 'villancico', 'zambomba', 'roscón', 'uvas', 'guirnalda', 'cabalgata', 'Papá Noel', 'pandereta', 'mazapán', 'chimenea', 'muñeco de nieve'];

const consejosCarta = (destinatario, cuando) => `
<h2>Cómo rellenar la carta</h2>
<p>La carta está pensada para que la complete el propio niño: su nombre y su edad arriba, una casilla para decir qué tal se ha portado, cinco renglones numerados para los regalos, tres renglones libres para contar lo que quiera y un recuadro grande para un dibujo. Al final, la despedida y la firma.</p>
<p>Los cinco huecos para regalos no son casualidad: obligan a elegir. Si la lista es más larga, se puede pedir que marquen con una estrella el que más ilusión les hace; ayuda a ${destinatario} y también a la familia.</p>
<h2>Tres versiones según la edad</h2>
<ul>
<li><strong>Con renglones</strong>, para niños que ya escriben con soltura, de 7 u 8 años en adelante.</li>
<li><strong>Con pauta de doble línea</strong>, la misma que usan en primero y segundo de primaria: las letras pequeñas van entre las dos líneas y la carta queda más ordenada.</li>
<li><strong>Para dibujar o pegar</strong>, con cuatro recuadros grandes en lugar de renglones. Es la de infantil: el niño recorta los juguetes del catálogo que llega a casa por estas fechas y los pega, o los dibuja. Un adulto puede escribir debajo el nombre de cada regalo.</li>
</ul>
<h2>El sobre</h2>
<p>La última hoja es un sobre para recortar y montar, con la dirección ya escrita. Se recorta por la línea continua y se doblan hacia atrás los laterales y la solapa de abajo, que se pega a los laterales. La carta, doblada en cuatro, entra justa; después se cierra con la solapa de arriba. Queda sitio para que el niño ponga su nombre en «De:» y dibuje el sello.</p>
<h2>Cuándo y cómo entregarla</h2>
<p>${cuando}</p>
<p>Imprímela en folio normal o en papel algo más grueso si va a llevar dibujo con rotuladores o recortes pegados. Si prefieres un sobre comprado, la carta doblada en tres cabe en uno americano.</p>`;

module.exports = [
  {
    cat: 'navidad', slug: '', corto: 'Navidad', nav: 'Navidad',
    title: 'Fichas de Navidad para imprimir gratis (PDF)',
    desc: 'Fichas de Navidad para imprimir: carta a los Reyes Magos y a Papá Noel, bingo, laberinto con forma de árbol, sudoku con dibujos y sopa de letras.',
    h1: 'Fichas de Navidad para imprimir',
    resumen: 'Cartas, bingo, laberinto, sudoku y sopa de letras',
    entrada: 'Todo lo que hace falta para las últimas semanas de clase y para las tardes de vacaciones: la carta a los Reyes Magos y a Papá Noel, un bingo con palabras navideñas, un laberinto con forma de árbol, sudokus con dibujos y una sopa de letras con el vocabulario de la Navidad de aquí.',
    hojas: [{ tipo: 'laberinto-arbol', titulo: 'Laberinto de Navidad', cols: 19, filas: 25 }],
    copias: 2,
    cuerpo: `
<h2>Qué hay en esta sección</h2>
<ul>
<li><a href="/navidad/carta-reyes-magos/">Carta a los Reyes Magos</a> y <a href="/navidad/carta-papa-noel/">carta a Papá Noel</a>, con renglones, con pauta o para pegar los recortes del catálogo, y con su sobre.</li>
<li><a href="/navidad/carta-de-los-reyes-a-los-ninos/">Carta de los Reyes Magos a los niños</a>, la respuesta que dejan junto a los regalos.</li>
<li><a href="/navidad/bingo/">Bingo de Navidad</a> con palabras en lugar de números, para jugar en clase o en la sobremesa.</li>
<li><a href="/navidad/laberinto/">Laberinto con forma de árbol de Navidad</a>, en versión fácil y difícil.</li>
<li><a href="/navidad/sudoku/">Sudokus de Navidad con dibujos</a>, para niños que todavía no han hecho ninguno.</li>
<li><a href="/sopas-de-letras/navidad/">Sopa de letras de Navidad</a> y <a href="/crucigramas/navidad/">crucigrama de Navidad</a>, con turrón, zambomba, roscón y cabalgata.</li>
</ul>
<h2>Ideas para el último día de clase</h2>
<p>El último día antes de las vacaciones suele ser difícil de llenar: los niños están nerviosos y no es momento de empezar nada nuevo. Una propuesta que funciona en primaria: empezar con la sopa de letras o el laberinto mientras se reparte la merienda, seguir con una partida de bingo para toda la clase y terminar con la carta a los Reyes, que se llevan a casa en la mochila.</p>
<p>Para infantil, el sudoku de 4 × 4 con dibujos y el laberinto fácil son los más adecuados; después pueden colorear la hoja, porque todos los dibujos son de línea y sin relleno.</p>
<h2>En casa, en vacaciones</h2>
<p>Las fichas se pueden generar de nuevo tantas veces como quieras con «Otra distinta», así que sirven para varios días sin repetir. Si hay primos de edades distintas, imprime el laberinto fácil para los pequeños y el difícil para los mayores: todos tienen la misma forma de árbol y nadie se siente con «la ficha de bebés».</p>
<p>Todas las hojas están pensadas para imprimir en blanco y negro en A4, sin fondos ni manchas de color que gasten tinta.</p>`,
    faq: [
      ['¿Cuándo se escribe la carta a los Reyes Magos?', 'La mayoría de las familias la escriben en diciembre, después del puente de la Constitución, y la entregan antes de la cabalgata del 5 de enero, a los pajes reales o en los buzones que ponen muchos ayuntamientos y centros comerciales.'],
      ['¿Las fichas de Navidad son gratis?', 'Sí. Puedes imprimirlas y fotocopiarlas sin límite para casa, el colegio, la catequesis o una residencia. Solo pedimos que no se revendan ni se publiquen en otras webs.']
    ]
  },
  {
    cat: 'navidad', slug: 'carta-reyes-magos', corto: 'Carta a los Reyes Magos',
    title: 'Carta a los Reyes Magos para imprimir y rellenar (PDF)',
    desc: 'Carta a los Reyes Magos para imprimir y rellenar, con renglones, con pauta o para pegar los recortes del catálogo. Incluye sobre para montar. PDF gratis.',
    h1: 'Carta a los Reyes Magos para imprimir',
    entrada: 'Tres cartas para rellenar a mano y un sobre para mandarlas: con renglones para los que ya escriben, con pauta para los que están aprendiendo y con cuatro recuadros grandes para dibujar los regalos o pegar los recortes del catálogo de juguetes. Todo en un PDF.',
    hojas: [
      { tipo: 'carta', para: 'reyes' },
      { tipo: 'carta', para: 'reyes', pauta: true },
      { tipo: 'carta', para: 'reyes', modo: 'dibujar' },
      { tipo: 'sobre', para: 'reyes' }
    ],
    copias: 1,
    cuerpo: consejosCarta('Sus Majestades',
      'La tradición es entregarla en mano a un paje real o a los propios Reyes en alguna de sus visitas de diciembre, o echarla en uno de los buzones reales que instalan muchos ayuntamientos. El último día para que llegue a tiempo es el 5 de enero, el día de la cabalgata, aunque cuanto antes se envíe, mejor: los Reyes tienen mucho trabajo esos días.') + `
<h2>Si hay varios hermanos</h2>
<p>Imprime una carta para cada uno. Escribir la suya propia, aunque sea con letra de primero de primaria, forma parte de la ilusión. Si tienen edades muy distintas, el mayor puede usar la hoja con renglones y el pequeño la de pauta.</p>
<p>¿En tu casa también viene Papá Noel? Tienes la <a href="/navidad/carta-papa-noel/">carta a Papá Noel</a> con el mismo formato. Y para la mañana del 6 de enero, la <a href="/navidad/carta-de-los-reyes-a-los-ninos/">carta de respuesta de los Reyes Magos</a>, para dejar junto a los regalos.</p>`,
    amazon: [['Sobres de colores', 'sobres de colores navidad'], ['Rotuladores para niños', 'rotuladores lavables niños']]
  },
  {
    cat: 'navidad', slug: 'carta-papa-noel', corto: 'Carta a Papá Noel',
    title: 'Carta a Papá Noel para imprimir y rellenar (PDF)',
    desc: 'Carta a Papá Noel para imprimir y rellenar, con renglones, con pauta o para pegar los recortes del catálogo de juguetes. Incluye sobre. PDF gratis.',
    h1: 'Carta a Papá Noel para imprimir',
    entrada: 'La carta para Papá Noel en tres versiones, lista para que los niños la rellenen: con renglones, con pauta de doble línea y con recuadros para dibujar los regalos o pegar los recortes del catálogo. Y un sobre «Para Papá Noel, Polo Norte» para recortar y montar.',
    hojas: [
      { tipo: 'carta', para: 'papanoel' },
      { tipo: 'carta', para: 'papanoel', pauta: true },
      { tipo: 'carta', para: 'papanoel', modo: 'dibujar' },
      { tipo: 'sobre', para: 'papanoel' }
    ],
    copias: 1,
    cuerpo: consejosCarta('Papá Noel',
      'Papá Noel reparte los regalos la noche del 24 al 25 de diciembre, así que la carta tiene que salir con tiempo: lo ideal es escribirla a principios de diciembre. Muchas familias la dejan junto al árbol o la chimenea, con un vaso de leche y unas galletas, o la echan en los buzones de Navidad de su ciudad.') + `
<h2>Papá Noel y los Reyes Magos</h2>
<p>En muchas casas vienen los dos: Papá Noel trae algo el día de Navidad y los Reyes, el 6 de enero. Si es vuestro caso, una costumbre que ayuda a no duplicar es repartir la lista: un par de cosas en esta carta y el resto en la <a href="/navidad/carta-reyes-magos/">carta a los Reyes Magos</a>.</p>`,
    amazon: [['Sobres de colores', 'sobres de colores navidad'], ['Rotuladores para niños', 'rotuladores lavables niños']]
  },
  {
    cat: 'navidad', slug: 'carta-de-los-reyes-a-los-ninos', corto: 'Carta de los Reyes a los niños',
    title: 'Carta de los Reyes Magos a los niños para imprimir',
    desc: 'Carta de respuesta de los Reyes Magos para dejar junto a los regalos, con hueco para el nombre y lo que ha hecho bien. Versión con carbón dulce. PDF gratis.',
    h1: 'Carta de los Reyes Magos a los niños',
    entrada: 'La respuesta de Melchor, Gaspar y Baltasar a la carta de tu hijo, para dejarla junto a los regalos la mañana del 6 de enero. Ya viene redactada: solo hay que escribir su nombre, en qué se ha esforzado este año y en qué puede mejorar. Hay una segunda versión que acompaña al carbón dulce.',
    hojas: [
      { tipo: 'carta-respuesta' },
      { tipo: 'carta-respuesta', variante: 'carbon' }
    ],
    copias: 1,
    cuerpo: `
<h2>Cómo personalizarla</h2>
<p>La carta tiene tres huecos. En el primero va el nombre del niño. En el segundo, dos o tres cosas concretas en las que se ha esforzado este año: «en leer cada noche», «en ayudar a poner la mesa», «en cuidar de tu hermana». Cuanto más concretas, más le sorprenderá que los Reyes lo sepan. En el tercero, una sola cosa que puede mejorar, dicha con cariño.</p>
<p>Para que no reconozca la letra de casa, puede escribirla otro familiar, o rellenarla con letras mayúsculas y un rotulador dorado o plateado. Las firmas de Melchor, Gaspar y Baltasar quedan más creíbles con tres bolígrafos distintos.</p>
<h2>La versión del carbón dulce</h2>
<p>La segunda hoja cambia un párrafo: explica que los Reyes dejan un trocito de carbón dulce junto a los regalos, «no como castigo, sino como recordatorio de que el año que viene puedes hacerlo todavía mejor». Funciona para el niño que ha tenido un año con altibajos sin convertir la mañana de Reyes en un mal trago.</p>
<h2>Dónde dejarla</h2>
<p>Encima de los regalos, junto a los zapatos o al lado del vaso de agua vacío de los camellos. Muchas familias la meten en el mismo <a href="/navidad/carta-reyes-magos/">sobre de la carta a los Reyes</a>, como si la hubieran contestado en ella. Después suele acabar guardada en una caja de recuerdos: imprímela en papel algo más grueso si quieres que dure.</p>`,
    amazon: [['Rotuladores dorados y plateados', 'rotuladores dorados plateados'], ['Carbón dulce de Reyes', 'carbon dulce reyes']]
  },
  {
    cat: 'navidad', slug: 'bingo', corto: 'Bingo de Navidad',
    title: 'Bingo de Navidad para imprimir, con palabras (PDF)',
    desc: 'Bingo de Navidad para imprimir: cartones con palabras navideñas en lugar de números y la lista para cantarlo. Para clase o para la sobremesa.',
    h1: 'Bingo de Navidad para imprimir',
    entrada: 'Un bingo en el que, en vez de números, salen palabras de Navidad: turrón, camello, zambomba, villancico. Dos cartones grandes por hoja, todos distintos, y una hoja con las 28 palabras para recortar y cantar.',
    hojas: [
      { tipo: 'bingo-palabras', titulo: 'Bingo de Navidad', cabecera: 'BINGO DE NAVIDAD', palabras: palabrasBingo },
      { tipo: 'bingo-palabras-lista', titulo: 'Bingo de Navidad: palabras para cantar', palabras: palabrasBingo }
    ],
    copias: 4,
    cuerpo: `
<h2>Cómo se juega</h2>
<ol>
<li>Reparte un cartón a cada jugador. Cada cartón tiene 16 de las 28 palabras posibles, elegidas al azar.</li>
<li>Recorta las palabras de la hoja de lista, dóblalas y mételas en una bolsa o un gorro de Papá Noel.</li>
<li>Saca una palabra cada vez y léela en voz alta. Quien la tenga, la tacha o pone un garbanzo encima.</li>
<li>El primero que complete una fila de cuatro canta <strong>línea</strong>; el primero que tache el cartón entero canta <strong>bingo</strong>.</li>
</ol>
<p>Una partida completa dura entre diez y quince minutos, lo justo para una sesión de clase o para después de la comida de Navidad.</p>
<h2>Por qué con palabras</h2>
<p>En infantil y primeros cursos de primaria, el bingo de palabras es lectura disfrazada de juego: hay que reconocer la palabra cantada entre dieciséis, muchas veces antes de que la diga el compañero. Para los más pequeños, quien canta puede enseñar el papel además de leerlo, y así lo buscan por la forma de las letras.</p>
<p>Las palabras están en mayúsculas, que es como leen al principio los niños de infantil.</p>
<h2>Cuántos cartones imprimir</h2>
<p>Cada hoja trae dos cartones; el PDF tiene cuatro hojas, es decir, ocho cartones distintos. Para una clase de 25, pulsa «Otra distinta» e imprime varias hojas más: cada vez salen cartones nuevos. Como solo hay 28 palabras posibles y cada cartón tiene 16, en clases grandes es normal que dos niños canten línea a la vez; lo más justo es dar el premio a los dos.</p>
<p>Si prefieres el bingo de toda la vida, con números del 1 al 90, tienes los <a href="/bingo/">cartones de bingo tradicionales</a>.</p>`,
    amazon: [['Fichas para marcar cartones', 'fichas bingo transparentes'], ['Gorro de Papá Noel', 'gorro papa noel']]
  },
  {
    cat: 'navidad', slug: 'laberinto', corto: 'Laberinto de Navidad',
    title: 'Laberinto de Navidad para imprimir: árbol de Navidad',
    desc: 'Laberinto de Navidad con forma de árbol para imprimir: entra por la estrella y llega al regalo. Versión fácil y difícil, con solución. PDF gratis.',
    h1: 'Laberinto de Navidad para imprimir',
    entrada: 'Un laberinto con forma de árbol de Navidad: se entra por la estrella de la punta y hay que bajar hasta el regalo que espera junto al tronco. Hay una versión fácil, con pasillos anchos, y otra difícil para mayores.',
    hojas: [
      { tipo: 'laberinto-arbol', titulo: 'Laberinto de Navidad (fácil)', cols: 13, filas: 17 },
      { tipo: 'laberinto-arbol', titulo: 'Laberinto de Navidad (difícil)', cols: 25, filas: 33 }
    ],
    copias: 2,
    cuerpo: `
<h2>Dos niveles con la misma forma</h2>
<p>El laberinto <strong>fácil</strong> tiene pasillos de más de un centímetro de ancho y pocas bifurcaciones: es para niños de 4 a 6 años, que pueden recorrerlo con un rotulador grueso. El <strong>difícil</strong> tiene casi el triple de casillas y pasillos de 6 mm, con callejones largos que obligan a volver atrás; va bien a partir de 8 años y también entretiene a los adultos.</p>
<p>Como los dos tienen la misma silueta de árbol, se pueden repartir a la vez entre hermanos o en una clase con niveles distintos.</p>
<h2>Cómo están hechos</h2>
<p>El programa traza los pasillos solo dentro de la silueta del árbol y garantiza que hay un único camino entre la estrella y el regalo, sin bucles ni zonas cerradas. Cada vez que pulsas «Otra distinta» sale un laberinto nuevo con la misma forma.</p>
<h2>Después del laberinto, a colorear</h2>
<p>La estrella y el regalo están dibujados solo con línea, y el árbol queda en blanco: cuando terminen el recorrido pueden pintar el árbol de verde, añadir bolas y guirnaldas y colorear el regalo. Así la misma hoja da para un buen rato.</p>
<p>Si buscas laberintos sin temática, en la sección de <a href="/laberintos/">laberintos para imprimir</a> hay tres tamaños más.</p>`
  },
  {
    cat: 'navidad', slug: 'sudoku', corto: 'Sudoku de Navidad',
    title: 'Sudoku de Navidad para niños, con dibujos (PDF)',
    desc: 'Sudokus de Navidad para niños con dibujos en vez de números: estrellas, árboles, regalos y campanas. 4 × 4 desde 5 años y 6 × 6 desde 7. Con solución.',
    h1: 'Sudoku de Navidad para niños',
    entrada: 'Sudokus en los que, en lugar de números, hay que colocar estrellas, árboles, regalos y campanas. El de 4 × 4 es perfecto para un primer sudoku; el de 6 × 6 añade bolas y velas para los que ya saben jugar.',
    hojas: [
      { tipo: 'sudoku-dibujos', n: 4, nivel: 'facil', titulo: 'Sudoku de Navidad' },
      { tipo: 'sudoku-dibujos', n: 6, nivel: 'facil', titulo: 'Sudoku de Navidad 6 × 6' }
    ],
    copias: 2,
    cuerpo: `
<h2>Por qué con dibujos</h2>
<p>El sudoku no tiene nada que ver con las matemáticas: es lógica pura, y los números son solo símbolos. Con dibujos se ve más claro. Un niño de cinco años que aún no maneja bien las cifras entiende enseguida que «en cada fila tiene que haber una estrella, un árbol, un regalo y una campana».</p>
<h2>Cómo se juega</h2>
<p>En el de 4 × 4, cada fila, cada columna y cada caja de 2 × 2 debe tener los cuatro dibujos sin repetir ninguno. Hay que dibujar los que faltan en las casillas vacías. Los dibujos son sencillos a propósito: una estrella, un triángulo con tronco, un cuadrado con lazo y una campana se hacen en unos segundos.</p>
<p>En el de 6 × 6 entran también la bola y la vela, y las cajas son rectángulos de dos filas por tres columnas.</p>
<h2>Un truco para los más pequeños</h2>
<p>Si dibujar les cuesta, que pongan solo la inicial (E, Á, R, C) o un punto de color distinto para cada dibujo: un rotulador amarillo para las estrellas, verde para los árboles y así. Cuando terminen, pueden colorear la hoja entera.</p>
<p>Cuando dominen estos, el siguiente paso son los <a href="/sudokus/para-ninos/">sudokus para niños con números</a>, de 4 × 4 y 6 × 6.</p>`,
    amazon: [['Lápices de colores', 'lapices de colores niños']]
  }
];
