// Mandalas para colorear, generados por geometría (lib/puzzles.js, función mandala).

const comoColorear = `
<h2>Ideas para colorear un mandala</h2>
<ul>
<li><strong>Por anillos.</strong> Usa el mismo color en todas las piezas de un mismo anillo: la simetría se mantiene y el resultado queda ordenado aunque elijas colores al azar.</li>
<li><strong>Del centro hacia fuera</strong> o al revés. Empezar por el centro ayuda a no apoyar la mano sobre lo ya coloreado si usas rotuladores.</li>
<li><strong>Con una paleta corta.</strong> Tres o cuatro colores de la misma gama (azules y verdes, o rojos, naranjas y amarillos) dan un acabado más armonioso que doce colores distintos.</li>
<li><strong>Dejando blancos.</strong> No hace falta colorearlo todo: dejar un anillo sin pintar da descanso a la vista.</li>
</ul>
<h2>Con qué colorear</h2>
<p>Los lápices de colores son lo más versátil y permiten degradados. Los rotuladores de punta fina van bien en los mandalas difíciles, con piezas pequeñas; en papel de 80 gramos pueden traspasar, así que conviene imprimir en papel de 100 o 120 gramos o poner una hoja debajo. Las ceras gruesas, solo para los mandalas fáciles.</p>`;

const amazon = [['Lápices de colores', 'lapices de colores 48'], ['Rotuladores de punta fina', 'rotuladores punta fina 0.4 colores'], ['Papel A4 de 120 gramos', 'papel a4 120 gramos']];

module.exports = [
  {
    cat: 'mandalas', slug: '', corto: 'Mandalas', nav: 'Mandalas',
    resumen: 'Para colorear: fáciles, medios y difíciles',
    title: 'Mandalas para colorear e imprimir gratis (PDF)',
    desc: 'Mandalas para colorear e imprimir en A4: fáciles para niños, medios y difíciles para adultos. Cada uno es distinto: genera tantos como quieras. PDF gratis.',
    h1: 'Mandalas para colorear',
    entrada: 'Mandalas en A4 para imprimir y colorear, dibujados solo con línea negra para que el color lo pongas tú. Cada mandala lo genera un programa a partir de pétalos, hojas, arcos y círculos en anillos, así que con «Otra distinta» sale uno nuevo cada vez. Hay tres niveles, de los grandes y sencillos para niños a los de piezas pequeñas para adultos.',
    hojas: [{ tipo: 'mandala', nivel: 'medio', titulo: 'Mandala para colorear' }],
    copias: 4,
    cuerpo: `
<h2>Tres niveles</h2>
<ul>
<li><a href="/mandalas/faciles/">Mandalas fáciles</a>: tres o cuatro anillos, piezas grandes y trazo grueso. Para niños de infantil y primaria, o para colorear con ceras.</li>
<li><strong>Mandalas medios</strong> (los de esta página): cinco o seis anillos con algún detalle interior. Para niños mayores y para adultos que quieren terminar uno en una tarde.</li>
<li><a href="/mandalas/dificiles/">Mandalas difíciles</a>: ocho o nueve anillos, hasta dieciocho repeticiones por vuelta y trazo fino. Para adultos con paciencia y lápices bien afilados.</li>
</ul>
<p>Y para estas fechas, <a href="/mandalas/navidad/">mandalas de Navidad</a> con copos de nieve, estrellas y árboles.</p>
<h2>Qué es un mandala</h2>
<p>La palabra viene del sánscrito y significa «círculo». En el budismo y el hinduismo, los mandalas son representaciones del universo que se dibujan con gran detalle, a veces con arena de colores. Los que se colorean como pasatiempo toman de ellos la forma: un centro y anillos concéntricos en los que el mismo motivo se repite alrededor, como en un caleidoscopio.</p>
<p>Mucha gente los colorea para desconectar un rato: el dibujo ya está hecho, no hay que decidir formas, y la repetición de las piezas hace que la mano trabaje casi sola. En clase son una buena actividad tranquila después del recreo.</p>
${comoColorear}`,
    faq: [
      ['¿Se repiten los mandalas?', 'No. Cada mandala se genera combinando al azar el número de repeticiones, el ancho de los anillos y el motivo de cada uno (pétalos, hojas, arcos, círculos, zigzag o gotas). Con «Otra distinta» obtienes uno nuevo, y el PDF trae cuatro diferentes.'],
      ['¿Puedo usarlos en clase o en un taller?', 'Sí. Puedes imprimirlos y fotocopiarlos sin límite para casa, el aula, residencias o talleres. Lo único que no está permitido es venderlos o republicarlos en otra web.']
    ],
    amazon
  },
  {
    cat: 'mandalas', slug: 'navidad', corto: 'De Navidad',
    title: 'Mandalas de Navidad para colorear e imprimir (PDF)',
    desc: 'Mandalas de Navidad para colorear: copos de nieve, estrellas, árboles, regalos y campanas. Versión fácil para niños y otra más detallada. PDF gratis.',
    h1: 'Mandalas de Navidad para colorear',
    entrada: 'Mandalas con motivos navideños para colorear en estas fechas: copos de nieve, estrellas, árboles, regalos, campanas, bolas y velas, repetidos en anillos alrededor de un copo central. Hay una versión fácil, con piezas grandes, y otra más detallada para mayores. Cada vez que pulsas «Otra distinta» sale un mandala nuevo.',
    hojas: [
      { tipo: 'mandala', navidad: true, nivel: 'facil', titulo: 'Mandala de Navidad' },
      { tipo: 'mandala', navidad: true, nivel: 'medio', titulo: 'Mandala de Navidad' }
    ],
    copias: 2,
    cuerpo: `
<h2>Ideas para colorearlos</h2>
<p>Los colores clásicos de la Navidad funcionan muy bien en un mandala: rojo, verde y dorado, con algún toque de blanco (dejando piezas sin colorear). Otra opción es un mandala «de invierno» solo con azules, grises y plata, que hace destacar los copos de nieve.</p>
<p>Si usas rotuladores metálicos o purpurina en gel en las estrellas y las bolas, el mandala sirve de adorno: recórtalo por el círculo exterior, pégalo sobre una cartulina y cuélgalo en la ventana o en el árbol.</p>
<h2>Para clase o para casa</h2>
<p>Los mandalas de Navidad son una actividad tranquila para las últimas semanas antes de las vacaciones, cuando cuesta concentrarse en otra cosa. El fácil tiene cuatro anillos y piezas grandes, adecuado para infantil y los primeros cursos de primaria; el detallado, seis anillos con motivos pequeños, para niños mayores y adultos.</p>
<p>Si quieres más fichas para estas fechas, en <a href="/navidad/">fichas de Navidad</a> tienes la carta a los Reyes Magos, el bingo, el laberinto con forma de árbol y la sopa de letras.</p>`,
    amazon
  },
  {
    cat: 'mandalas', slug: 'faciles', corto: 'Fáciles para niños',
    title: 'Mandalas fáciles para colorear: para niños (PDF)',
    desc: 'Mandalas fáciles para colorear e imprimir: piezas grandes, pocos anillos y trazo grueso, pensados para niños de infantil y primaria. PDF gratis.',
    h1: 'Mandalas fáciles para colorear',
    entrada: 'Mandalas con tres o cuatro anillos, piezas grandes y una línea gruesa que se ve bien y ayuda a no salirse. Pensados para niños de 4 a 8 años y para colorear con ceras, lápices gruesos o rotuladores.',
    hojas: [{ tipo: 'mandala', nivel: 'facil', titulo: 'Mandala fácil' }],
    copias: 4,
    cuerpo: `
<h2>Por qué funcionan con niños pequeños</h2>
<p>Un mandala es simétrico: lo que el niño hace en una pieza lo repite en la de al lado. Esa repetición le da seguridad («ahora toca otra igual») y le obliga a fijarse en la forma de cada pieza para no saltarse ninguna. Además, colorear dentro de un contorno es un buen ejercicio de control del lápiz, la misma destreza que necesitará para escribir.</p>
<p>En estos mandalas las piezas son grandes y cerradas, el trazo es grueso y no hay detalles dentro de las piezas, para que un niño de infantil pueda terminarlo sin frustrarse.</p>
<h2>Un juego para colorear en pareja</h2>
<p>Dos niños, un mandala y dos colores cada uno: por turnos, cada uno elige un anillo y lo colorea entero. Al final comparan cómo ha quedado. Es una forma sencilla de practicar el respeto de turnos y de hablar de colores.</p>
<p>Cuando se les queden cortos, prueba con los <a href="/mandalas/">mandalas de nivel medio</a>. Y si buscas otros pasatiempos para su edad, tienes los <a href="/laberintos/faciles/">laberintos fáciles</a> y el <a href="/sudokus/para-ninos/">sudoku de 4 × 4</a>.</p>
${comoColorear}`,
    amazon
  },
  {
    cat: 'mandalas', slug: 'dificiles', corto: 'Difíciles para adultos',
    title: 'Mandalas difíciles para colorear: para adultos (PDF)',
    desc: 'Mandalas difíciles para colorear e imprimir: ocho o nueve anillos, piezas pequeñas y trazo fino, para adultos. Cada uno distinto. PDF gratis.',
    h1: 'Mandalas difíciles para colorear',
    entrada: 'Mandalas con ocho o nueve anillos, entre doce y dieciocho repeticiones por vuelta y detalles dentro de las piezas. El trazo es fino para que no se coma las piezas pequeñas. Para adultos y adolescentes que quieren un mandala que dé para varias sesiones.',
    hojas: [{ tipo: 'mandala', nivel: 'dificil', titulo: 'Mandala difícil' }],
    copias: 4,
    cuerpo: `
<h2>Cómo abordar un mandala con tantas piezas</h2>
<p>Con cientos de piezas, decidir el color de cada una agota. Funciona mejor fijar un plan antes de empezar: elige una paleta de cuatro o cinco colores y asigna uno a cada anillo, alternando claros y oscuros para que los anillos se distingan. Dentro de un mismo anillo, las piezas con detalle interior (un pétalo dentro de otro, una hoja con nervadura) admiten un segundo tono más claro o más oscuro del mismo color.</p>
<p>Si quieres un efecto de profundidad, colorea el borde de cada pieza más oscuro y el centro más claro, con lápices de colores y presión suave. Lleva su tiempo, pero es lo que hace que un mandala parezca tener relieve.</p>
<h2>Qué material usar</h2>
<p>Lápices de colores con la punta bien afilada o rotuladores de 0,3 o 0,4 mm. Los rotuladores gruesos se salen en las piezas pequeñas. Imprime en papel de 100 o 120 gramos si vas a usar rotulador, para que no traspase ni se arrugue la hoja.</p>
<p>Si prefieres algo más relajado, los <a href="/mandalas/">mandalas de nivel medio</a> se terminan en una tarde.</p>`,
    amazon
  }
];
