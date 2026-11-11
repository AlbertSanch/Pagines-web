// Caligrafía: letra ligada (Playwrite España) y letra de imprenta para infantil.
// `hojas` se ven en la página; `pdfExtra` solo van en el PDF (para no alargar la página).

const abc = 'a b c d e f g h i j k l m n ñ o p q r s t u v w x y z'.split(' ');
const ABC = abc.map((l) => l.toUpperCase());
const grupos = (lista, n) => Array.from({ length: Math.ceil(lista.length / n) }, (_, i) => lista.slice(i * n, i * n + n));

const frases = [
  'Mi mamá me mima.', 'El sol sale por la mañana.', 'Me gusta leer cuentos.', 'La casa tiene un jardín.',
  'Hoy es un día muy bonito.', 'El perro juega con la pelota.', 'Más vale tarde que nunca.',
  'A quien madruga, Dios le ayuda.', 'Mi abuela hace pan.', 'Los pájaros cantan.', 'El gato duerme al sol.',
  'Me lavo los dientes.', 'Vamos al parque.', 'Tengo una mochila azul.', 'La luna brilla de noche.',
  'En verano vamos a la playa.', 'Las hojas caen en otoño.', 'Mi amigo se llama Pablo.',
  'Me gustan las fresas.', 'El tren llega a las tres.', 'Poco a poco se va lejos.', 'Ayudo a poner la mesa.'
];

const pauta = `
<h2>La pauta</h2>
<p>Cada renglón tiene cuatro líneas. Entre las dos azules va el cuerpo de las letras pequeñas (a, e, o, m, n); la línea de puntos de arriba marca hasta dónde suben los palos de la b, la d, la l o la h, y la de abajo, hasta dónde bajan la g, la j, la p, la q o la y. Las mayúsculas llegan también a la línea de arriba.</p>
<p>Es la misma idea que la pauta de doble línea de los cuadernos de primaria, con las líneas de ayuda para que el niño vea dónde termina cada trazo.</p>`;

const letraLigada = `
<h2>Qué letra se usa</h2>
<p>Las fichas usan Playwrite España, una letra de escritura enlazada diseñada para enseñar a escribir en los colegios españoles: redonda, vertical y con las uniones entre letras que se enseñan en primaria. Si en el colegio de tu hijo usan otro modelo (más inclinado o con más bucles, como el de algunos cuadernillos), el trazo de cada letra puede variar un poco; lo importante es que copie siempre el mismo modelo.</p>`;

module.exports = [
  {
    cat: 'caligrafia', slug: '', corto: 'Caligrafía', nav: 'Caligrafía',
    resumen: 'Letra ligada, mayúsculas y números para repasar',
    title: 'Fichas de caligrafía para imprimir: letra ligada (PDF)',
    desc: 'Fichas de caligrafía para imprimir: frases para repasar y copiar en letra ligada, con pauta de primaria. Abecedario, mayúsculas y números. PDF gratis.',
    h1: 'Fichas de caligrafía para imprimir',
    entrada: 'Frases cortas en letra ligada para repasar en gris y copiar después en la pauta de debajo. Cada hoja trae cuatro frases elegidas al azar; con «Otra distinta» salen otras. Más abajo tienes el abecedario completo, las mayúsculas para infantil y los números.',
    hojas: [{ tipo: 'caligrafia-frases', frases }],
    copias: 4,
    cuerpo: `
<h2>Cómo usar las fichas</h2>
<p>Cada frase aparece primero en gris: el niño la repasa con lápiz siguiendo el trazo, sin levantarlo dentro de cada palabra. Después la copia dos veces en los renglones vacíos de debajo. Repasar primero y copiar después es el orden de los cuadernillos de caligrafía de toda la vida: la mano aprende el movimiento antes de tener que hacerlo sola.</p>
<p>Una ficha al día es suficiente. Diez minutos con atención valen más que media hora con prisa, y la letra mejora con la regularidad, no con la cantidad.</p>
${pauta}
${letraLigada}
<h2>Por dónde empezar</h2>
<ul>
<li>Si todavía no escribe en ligada, empieza por el <a href="/caligrafia/abecedario/">abecedario en letra ligada</a>, letra a letra.</li>
<li>En infantil, antes de la ligada, se suele aprender la <a href="/caligrafia/letras-mayusculas/">letra de imprenta en mayúsculas</a>.</li>
<li>Para los números, tienes los <a href="/caligrafia/numeros/">números del 0 al 9 para repasar</a>.</li>
</ul>
<p>Si solo necesitas la hoja con pauta, sin modelos, la tienes en <a href="/papel/pautado/">papel pautado</a>.</p>`,
    faq: [
      ['¿Con qué lápiz se hace la caligrafía?', 'Con un lápiz de dureza media (HB) bien afilado, o un triangular si al niño le cuesta sujetarlo. El rotulador no conviene: no deja corregir y tapa la pauta.'],
      ['¿A qué edad se empieza la letra ligada?', 'Depende del colegio: algunos la introducen en infantil, a los 5 años, y otros en primero de primaria. Antes conviene que el niño domine los trazos básicos y la letra de imprenta.']
    ],
    amazon: [['Lápices triangulares para niños', 'lapices triangulares niños'], ['Cuadernillos de caligrafía', 'cuadernillo caligrafia']]
  },
  {
    cat: 'caligrafia', slug: 'abecedario', corto: 'Abecedario en letra ligada',
    title: 'Abecedario en letra ligada para imprimir y repasar',
    desc: 'Abecedario en letra ligada para repasar e imprimir: las 27 letras, en minúscula y mayúscula, con pauta escolar y renglones para copiar. PDF gratis.',
    h1: 'Abecedario en letra ligada para repasar',
    entrada: 'Las 27 letras del abecedario en letra ligada, en minúscula y en mayúscula, tres letras por hoja: una fila para repasar el modelo en gris y otra vacía para escribirla solo. El PDF trae el abecedario completo, de la a a la z, con la ñ.',
    hojas: grupos(abc, 3).slice(0, 2).map((g) => ({ tipo: 'caligrafia-letras', letras: g })),
    pdfExtra: grupos(abc, 3).slice(2).map((g) => ({ tipo: 'caligrafia-letras', letras: g })),
    copias: 1,
    cuerpo: `
<h2>Cómo está organizado</h2>
<p>Cada letra ocupa cuatro renglones: la minúscula para repasar, un renglón vacío para escribirla, la mayúscula para repasar y otro renglón vacío. La primera letra de cada fila está en negro: es el modelo, el que hay que mirar antes de empezar. Las grises se repasan una a una, de izquierda a derecha.</p>
<p>En pantalla ves las dos primeras hojas (de la a a la f); el PDF tiene las nueve, hasta la z.</p>
<h2>En qué orden trabajarlas</h2>
<p>No hace falta seguir el orden alfabético. Muchos maestros agrupan las letras por la forma del trazo: primero las que empiezan con un óvalo (a, o, c, d, g, q), después las de puente (m, n, ñ, h), las de lazo hacia arriba (l, b, h, k, f) y las de lazo hacia abajo (g, j, y, z). Practicar juntas las letras parecidas ayuda a fijar el movimiento.</p>
${pauta}
${letraLigada}
<p>Cuando domine las letras sueltas, pasa a las <a href="/caligrafia/">frases para copiar</a>.</p>`
  },
  {
    cat: 'caligrafia', slug: 'letras-mayusculas', corto: 'Mayúsculas de imprenta (infantil)',
    title: 'Letras mayúsculas para repasar: fichas de infantil (PDF)',
    desc: 'Fichas para repasar las letras mayúsculas de imprenta, para infantil: letras grandes en gris con línea de guía, de la A a la Z con la Ñ. PDF gratis.',
    h1: 'Letras mayúsculas para repasar',
    entrada: 'Las mayúsculas de imprenta, la «letra de palo» con la que se empieza a escribir en infantil, en tamaño grande: la letra modelo en negro y seis copias en gris para repasar, con una línea de guía a media altura.',
    hojas: grupos(ABC, 7).slice(0, 1).map((g) => ({ tipo: 'trazos-imprenta', letras: g, titulo: 'Letras mayúsculas: ' + g[0] + ' a ' + g[g.length - 1] })),
    pdfExtra: grupos(ABC, 7).slice(1).map((g) => ({ tipo: 'trazos-imprenta', letras: g, titulo: 'Letras mayúsculas: ' + g[0] + ' a ' + g[g.length - 1] })),
    copias: 1,
    cuerpo: `
<h2>Para qué edad</h2>
<p>Para el segundo y tercer curso de infantil (4 y 5 años), que es cuando la mayoría de colegios trabajan la letra de imprenta en mayúsculas. Las letras miden 14 mm de alto, el doble que en una ficha de primaria, para que la mano todavía torpe pueda seguir el trazo.</p>
<h2>Cómo repasar una letra</h2>
<p>Cada mayúscula se hace con trazos rectos y curvos que empiezan arriba. Antes de repasar, conviene que el niño haga la letra en el aire con el dedo, o con el dedo sobre el modelo negro, diciendo en voz alta el recorrido: «la A: palo inclinado, palo inclinado y rayita en medio». Después repasa las grises sin prisa.</p>
<p>La línea de puntos a media altura indica dónde van las rayitas de la A, la E, la F o la H, y dónde se juntan las curvas de la B, la P o la R.</p>
<p>En pantalla ves la primera hoja (de la A a la G); el PDF trae las cuatro, hasta la Z. Cuando las mayúsculas salgan solas, el siguiente paso es el <a href="/caligrafia/abecedario/">abecedario en letra ligada</a>.</p>`,
    amazon: [['Lápices triangulares para niños', 'lapices triangulares niños']]
  },
  {
    cat: 'caligrafia', slug: 'numeros', corto: 'Números para repasar',
    title: 'Números para repasar e imprimir: del 0 al 9 (PDF)',
    desc: 'Fichas para repasar los números del 0 al 9: cifras grandes en gris para seguir con el lápiz, con línea de guía. Para infantil y primero. PDF gratis.',
    h1: 'Números para repasar del 0 al 9',
    entrada: 'Las diez cifras en tamaño grande para aprender a escribirlas: el número modelo en negro y seis copias en gris para repasar con el lápiz. Dos hojas, del 0 al 4 y del 5 al 9.',
    hojas: [
      { tipo: 'trazos-imprenta', letras: ['0', '1', '2', '3', '4'], titulo: 'Números para repasar: 0 a 4', alto: 22, paso: 46, repeticiones: 5, sub: 'Empieza por el número negro y repasa los grises siguiendo la forma.' },
      { tipo: 'trazos-imprenta', letras: ['5', '6', '7', '8', '9'], titulo: 'Números para repasar: 5 a 9', alto: 22, paso: 46, repeticiones: 5, sub: 'Empieza por el número negro y repasa los grises siguiendo la forma.' }
    ],
    copias: 1,
    cuerpo: `
<h2>Los números que más cuestan</h2>
<p>Casi todos los niños escriben alguna vez el 3, el 7 o el 9 del revés, como en un espejo. Es normal hasta los 6 o 7 años y se corrige con práctica, no con regañinas. Repasar el modelo muchas veces fija el sentido del trazo: el 3 y el 9 empiezan curvando hacia la derecha; el 7, con la raya de arriba de izquierda a derecha.</p>
<p>El 8 suele ser el último en salir bien. Un truco es hacerlo como una «S» que vuelve a subir para cerrarse, sin levantar el lápiz.</p>
<h2>Después de repasar</h2>
<p>Cuando escriba los números sin el modelo, puede pasar a las <a href="/sumas-y-restas/sumas-sin-llevada/">primeras sumas</a> o al <a href="/sudokus/para-ninos/">sudoku de 4 × 4</a>, que también usa cifras y le hará escribirlas muchas veces sin darse cuenta.</p>`
  }
];
