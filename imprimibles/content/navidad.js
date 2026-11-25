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
    resumen: 'Cartas, bingo, mandalas, laberinto y sopa de letras',
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
<li><a href="/mandalas/navidad/">Mandalas de Navidad</a> para colorear, con copos de nieve, estrellas y regalos.</li>
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
  },
  {
    cat: 'navidad', slug: 'calendario-de-adviento', corto: 'Calendario de Adviento',
    title: 'Calendario de Adviento para imprimir (PDF gratis)',
    desc: 'Calendario de Adviento para imprimir: 24 casillas para tachar o colorear del 1 al 24 de diciembre, y otro con una actividad en familia para cada día.',
    h1: 'Calendario de Adviento para imprimir',
    entrada: 'La cuenta atrás hasta Nochebuena en papel: una hoja con 24 casillas desordenadas para buscar, tachar o colorear cada día de diciembre, y otra con una pequeña actividad en familia para cada día, del 1 al 24.',
    hojas: [
      { tipo: 'adviento', titulo: 'Calendario de Adviento', sub: 'Cada día de diciembre, busca su número, táchalo y colorea el dibujo. El 24 es Nochebuena.' },
      { tipo: 'adviento', titulo: 'Calendario de Adviento con actividades', sub: 'Una cosa que hacer juntos cada día, del 1 al 24 de diciembre.', actividades: [
        'Pon música de villancicos mientras cenáis', 'Escribe la carta a los Reyes o a Papá Noel', 'Haz un dibujo navideño para la nevera', 'Busca una estrella en el cielo antes de dormir',
        'Prepara chocolate caliente', 'Monta el belén o el árbol entre todos', 'Llama a un abuelo o a una abuela', 'Elige un juguete para regalar a quien lo necesite',
        'Cuenta un cuento de Navidad', 'Haz una guirnalda de papel', 'Aprende un villancico nuevo', 'Haz una felicitación para alguien de la familia',
        'Juega a un juego de mesa todos juntos', 'Mira una película de Navidad', 'Recorta copos de nieve de papel', 'Da las gracias por tres cosas del año',
        'Sal a ver las luces de la calle', 'Haz galletas o polvorones', 'Juega al bingo de Navidad', 'Haz una sopa de letras de Navidad',
        'Escribe qué te gustaría hacer el año que viene', 'Escucha el sorteo de la Lotería en la radio', 'Prepara la mesa para Nochebuena', '¡Es Nochebuena! A disfrutar de la cena en familia'] }
    ],
    copias: 1,
    cuerpo: `
<h2>Cómo usarlo</h2>
<p>El Adviento son los días que preceden a la Navidad, y en muchas casas se cuentan con un calendario de casillas que se abren o se tachan una cada día, del 1 al 24 de diciembre. Esta versión para imprimir es la más sencilla: cuélgala en la nevera o en la puerta de la habitación y, cada mañana, el niño busca el número del día (están desordenados a propósito), lo tacha y colorea el dibujo de esa casilla.</p>
<p>La segunda hoja cambia los dibujos por una actividad para hacer en familia cada día: cosas pequeñas, sin gastar dinero, como escribir la carta a los Reyes, montar el belén o salir a ver las luces. Si algún día no cuadra, se cambia por otro; lo importante es la costumbre de hacer algo juntos.</p>
<h2>Ideas para que dure todo el mes</h2>
<ul>
<li>Imprímelo en cartulina para que aguante 24 días en la nevera.</li>
<li>Pega encima de cada casilla un trocito de papel o un pósit para «abrirla» cada día.</li>
<li>Combínalo con el resto de <a href="/navidad/">fichas de Navidad</a>: el día del bingo, el de la sopa de letras o el de la carta a los Reyes.</li>
</ul>`,
    amazon: [['Cartulina blanca A4', 'cartulina blanca A4'], ['Pegatinas de Navidad', 'pegatinas navidad niños']]
  },
  {
    cat: 'navidad', slug: 'etiquetas-regalos', corto: 'Etiquetas para regalos',
    title: 'Etiquetas para regalos de Navidad para imprimir (PDF)',
    desc: 'Etiquetas para regalos de Navidad para imprimir y recortar: 12 por hoja, con «Para» y «De» y agujero para la cinta. En blanco o con «Feliz Navidad».',
    h1: 'Etiquetas para regalos de Navidad',
    entrada: 'Doce etiquetas por hoja con forma de etiqueta de regalo, un dibujo navideño, los huecos de «Para» y «De» y el círculo para pasar la cinta. Una hoja lleva «Feliz Navidad» y la otra solo el dibujo, para escribir lo que quieras.',
    hojas: [
      { tipo: 'etiquetas', titulo: 'Etiquetas para regalos de Navidad', texto: 'Feliz Navidad' },
      { tipo: 'etiquetas', titulo: 'Etiquetas para regalos' }
    ],
    copias: 1,
    cuerpo: `
<h2>Cómo hacerlas</h2>
<p>Imprímelas en cartulina fina (de 160 a 200 gramos) o en papel normal pegado a una cartulina de color. Recorta por la línea de puntos, haz el agujero con un perforador o con la punta de un lápiz y pasa un trozo de cinta o de cordel para atarlas al paquete.</p>
<p>Las etiquetas salen en blanco y negro para que los niños las coloreen: es una buena tarea para los días de vacaciones, y los regalos quedan mucho más personales. La hoja sin «Feliz Navidad» sirve también para Reyes, cumpleaños o el amigo invisible.</p>
<p>Para el sorteo del <a href="/navidad/amigo-invisible/">amigo invisible</a> tienes los papelitos y la hoja de quien organiza.</p>`,
    amazon: [['Cinta de regalo', 'cinta regalo navidad'], ['Perforadora de un agujero', 'perforadora un agujero']]
  },
  {
    cat: 'navidad', slug: 'menu-de-navidad', corto: 'Menú de Navidad',
    title: 'Menú de Navidad para imprimir: Nochebuena y Nochevieja',
    desc: 'Menú de Navidad para imprimir y rellenar: plantillas para la mesa de Nochebuena, Navidad y Nochevieja, con entrantes, platos, postre y brindis.',
    h1: 'Menú de Navidad para imprimir',
    entrada: 'Tres plantillas de menú para poner en la mesa: Nochebuena, comida de Navidad y Nochevieja. Escribe los platos a mano y deja una copia en cada sitio o una en el centro de la mesa.',
    hojas: [
      { tipo: 'menu-fiesta', cabecera: 'Menú de Nochebuena' },
      { tipo: 'menu-fiesta', cabecera: 'Menú de Navidad' },
      { tipo: 'menu-fiesta', cabecera: 'Menú de Nochevieja', secciones: ['Para picar', 'Primer plato', 'Segundo plato', 'Postre', 'Uvas y brindis'], pie: 'Doce uvas, doce campanadas y un deseo para cada mes.' }
    ],
    copias: 1,
    cuerpo: `
<h2>Ideas para usarlo</h2>
<p>Escribe los platos con un rotulador fino, mejor con letra grande, y pon una copia en cada plato o en el centro de la mesa. Si los niños se aburren antes de la cena, pídeles que lo decoren: coloreando las estrellas y los árboles del borde ya tienen entretenimiento para un rato.</p>
<p>En la plantilla de Nochevieja el último apartado es para las uvas y el brindis: si a alguien le toca recibir a los invitados, puede apuntar ahí quién trae las uvas peladas para los más pequeños.</p>
<p>Si quieres poner el menú en un marco o en una mesa larga, imprímelo en A3 con «Ajustar al papel». Y para repartir los regalos de esos días tienes las <a href="/navidad/etiquetas-regalos/">etiquetas para regalos</a>.</p>`,
    amazon: [['Rotuladores de punta fina', 'rotuladores punta fina negro'], ['Marcos de fotos A4', 'marco fotos A4']]
  },
  {
    cat: 'navidad', slug: 'lista-de-regalos', corto: 'Lista de regalos de Navidad',
    title: 'Lista de regalos de Navidad para imprimir (PDF)',
    desc: 'Lista de regalos de Navidad para imprimir: para quién, qué regalo, cuánto cuesta y si ya está comprado, con el total para no pasarte del presupuesto.',
    h1: 'Lista de regalos de Navidad para imprimir',
    entrada: 'Una tabla para organizar los regalos de Navidad y Reyes: para quién es, qué le vas a regalar, cuánto cuesta y una casilla para marcar cuando ya lo tienes. Abajo, el total y el presupuesto que te has puesto.',
    hojas: [
      { tipo: 'lista-regalos', titulo: 'Lista de regalos de Navidad', sub: 'Apunta cada regalo, su precio y marca la casilla cuando lo tengas.' }
    ],
    copias: 1,
    cuerpo: `
<h2>Para no pasarte del presupuesto</h2>
<p>Lo más práctico es decidir antes cuánto quieres gastar en total, apuntarlo abajo y repartirlo entre las personas de la lista. Al ir rellenando la columna de presupuesto ves enseguida si te queda margen o si toca recortar. Si compras por internet, apunta en la misma línea dónde lo has pedido para no perder la pista de los paquetes.</p>
<p>La lista tiene 18 líneas; si sois más, imprime dos copias. Para el intercambio de regalos en el trabajo o con los amigos tienes los papelitos del <a href="/navidad/amigo-invisible/">amigo invisible</a>.</p>`,
    amazon: [['Agenda 2027', 'agenda 2027'], ['Papel de regalo de Navidad', 'papel regalo navidad']]
  },
  {
    cat: 'navidad', slug: 'amigo-invisible', corto: 'Amigo invisible',
    title: 'Amigo invisible para imprimir: papelitos y hoja del sorteo',
    desc: 'Amigo invisible para imprimir: papelitos para el sorteo («te ha tocado regalar a…») y una hoja para quien organiza, con fecha, presupuesto e ideas.',
    h1: 'Amigo invisible para imprimir',
    entrada: 'Todo lo necesario para organizar el amigo invisible en papel: diez papelitos por hoja para el sorteo y una hoja para quien organiza, con la fecha, el presupuesto, el lugar y quién regala a quién.',
    hojas: [
      { tipo: 'amigo-invisible', titulo: 'Amigo invisible: papelitos para el sorteo' },
      { tipo: 'amigo-invisible', modo: 'organiza', titulo: 'Amigo invisible: hoja de quien organiza', sub: 'Apunta aquí los participantes y, si hace falta, quién regala a quién.' }
    ],
    copias: 1,
    cuerpo: `
<h2>Cómo organizar el sorteo</h2>
<ol>
<li>Acordad la fecha del intercambio y un presupuesto igual para todos, y apuntadlo en la hoja de quien organiza.</li>
<li>Escribe el nombre de cada participante en un papelito, recórtalos, dóblalos y mételos en una bolsa.</li>
<li>Cada uno saca un papel sin enseñarlo. Si alguien se saca a sí mismo, se vuelve a sortear.</li>
<li>El día del intercambio, cada uno entrega su regalo… o intenta adivinar quién era su amigo invisible.</li>
</ol>
<p>Si alguien no puede estar en el sorteo, quien organiza puede sacar su papel y decírselo en privado; por eso la hoja del organizador tiene una columna de «le regala a». Para envolver, tienes las <a href="/navidad/etiquetas-regalos/">etiquetas para regalos</a>.</p>`,
    amazon: [['Papel de regalo de Navidad', 'papel regalo navidad'], ['Bolsas de regalo', 'bolsas regalo navidad']]
  }
];
