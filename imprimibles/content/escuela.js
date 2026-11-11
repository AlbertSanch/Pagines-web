// Tablas de multiplicar, sumas y restas, y papel pautado.

const trucos = {
  1: ['Cualquier número multiplicado por 1 se queda igual. No hay nada que memorizar: 1 × 8 es 8 porque es «una vez ocho».',
    'Aunque parezca trivial, conviene que el niño la escriba una vez para fijar la idea de que multiplicar es contar grupos: un grupo de 6, un grupo de 9.'],
  2: ['Multiplicar por 2 es calcular el doble, o lo que es lo mismo, sumar el número consigo mismo: 2 × 7 = 7 + 7 = 14.',
    'Todos los resultados son pares y terminan en 0, 2, 4, 6 u 8, siempre en ese orden. Si un niño ya sabe contar de dos en dos, ya se sabe la tabla.'],
  3: ['Los resultados van de tres en tres: 3, 6, 9, 12, 15… Un buen apoyo es que las cifras de cada resultado suman 3, 6 o 9 (12 → 1 + 2 = 3; 27 → 2 + 7 = 9), lo que permite detectar errores.',
    'Si se atasca, puede calcular el doble y sumar una vez más: 3 × 6 es 6 + 6 + 6, o sea 12 + 6 = 18.'],
  4: ['La tabla del 4 es el doble del doble. Para 4 × 6, dobla 6 (12) y vuelve a doblar (24). Quien domina la tabla del 2 tiene esta casi hecha.',
    'Todos los resultados son pares, y las terminaciones se repiten cada cinco: 4, 8, 2, 6, 0.'],
  5: ['Los resultados terminan siempre en 5 o en 0, alternándose: 5, 10, 15, 20… Con un número par termina en 0; con uno impar, en 5.',
    'Otro camino: multiplica por 10 y calcula la mitad. 5 × 8 es la mitad de 80, es decir, 40. Y coincide con contar los minutos en un reloj de agujas.'],
  6: ['Al multiplicar 6 por un número par, el resultado termina en ese mismo número: 6 × 2 = 12, 6 × 4 = 24, 6 × 6 = 36, 6 × 8 = 48.',
    'También se puede pensar como la tabla del 3 doblada (6 × 7 es el doble de 3 × 7: 21 y 21, 42) o como la del 5 más una vez el número (6 × 7 = 35 + 7).'],
  7: ['Es la tabla con menos trucos y por eso tiene fama de difícil. La buena noticia es que casi toda ya se sabe por las otras tablas, porque el orden no cambia el resultado: 7 × 3 es lo mismo que 3 × 7.',
    'Si se deja para el final, solo queda un resultado realmente nuevo: 7 × 7 = 49. Los dos que más se olvidan son 7 × 8 = 56 y 7 × 9 = 63; para el primero hay una regla popular: «cinco, seis, siete, ocho», 56 = 7 × 8.'],
  8: ['Multiplicar por 8 es doblar tres veces. Para 8 × 6: 12, 24, 48.',
    'Hay un patrón en los resultados: las unidades bajan de dos en dos (8, 6, 4, 2, 0) y vuelven a empezar: 8, 16, 24, 32, 40, 48, 56, 64, 72, 80.'],
  9: ['En los resultados de la tabla del 9, las decenas suben de uno en uno y las unidades bajan de uno en uno: 09, 18, 27, 36, 45… Y las dos cifras suman siempre 9.',
    'El truco de los dedos: extiende las dos manos y dobla el dedo que ocupa el lugar del número por el que multiplicas. Para 9 × 4, dobla el cuarto dedo: quedan 3 a la izquierda y 6 a la derecha, 36.'],
  10: ['Basta añadir un cero a la derecha: 10 × 7 = 70. Es la tabla más fácil junto con la del 1.',
    'Conviene explicar por qué funciona en lugar de darlo como magia: multiplicar por 10 convierte las unidades en decenas, así que cada cifra se mueve un lugar a la izquierda.']
};

const tablasN = Object.keys(trucos).map(Number).map((n) => ({
  cat: 'tablas-de-multiplicar', slug: `tabla-del-${n}`, corto: `Tabla del ${n}`,
  title: `Tabla del ${n} para imprimir: lámina y ejercicios (PDF)`,
  desc: `Tabla de multiplicar del ${n} para imprimir en A4: lámina para estudiar, hoja para rellenar y 30 multiplicaciones desordenadas con solución. PDF gratis.`,
  h1: `Tabla del ${n} para imprimir`,
  entrada: `Tres hojas para aprender la tabla del ${n}: la lámina con los resultados para colgar o estudiar, la misma tabla con huecos para rellenar y una ficha de 30 multiplicaciones desordenadas para comprobar que se sabe de verdad.`,
  hojas: [
    { tipo: 'tabla', n },
    { tipo: 'tabla', n, vacia: true, titulo: `Tabla del ${n} para rellenar` },
    { tipo: 'mult-practica', tablas: [n], titulo: `Practica la tabla del ${n}` }
  ],
  copias: 2,
  cuerpo: `
<h2>La tabla del ${n}</h2>
<p class="tabla-texto">${Array.from({ length: 10 }, (_, i) => `${n} × ${i + 1} = ${n * (i + 1)}`).join(' · ')}</p>
<h2>Trucos para aprender la tabla del ${n}</h2>
<p>${trucos[n][0]}</p>
<p>${trucos[n][1]}</p>
<h2>Cómo usar las tres hojas</h2>
<p>Empieza por la lámina: leedla en voz alta un par de veces y dejadla a la vista unos días. Después, la hoja para rellenar, que sigue el orden natural (× 1, × 2, × 3…) y permite apoyarse en el resultado anterior. La ficha desordenada es la prueba final: si el niño responde 7 de cada 10 sin contar con los dedos, la tabla está aprendida.</p>
<p>La ficha de práctica cambia cada vez que pulsas «Otra distinta», así que puedes repetirla varios días sin que memorice el orden de las respuestas.</p>`,
  amazon: [['Fundas para plastificar A4', 'fundas plastificar A4'], ['Rotuladores borrables de punta fina', 'rotuladores borrables punta fina']]
}));

const sr = (slug, corto, op, llevada, entrada, explicacion) => ({
  cat: 'sumas-y-restas', slug, corto,
  title: `${corto} para imprimir: fichas con solución (PDF)`,
  desc: `Fichas de ${corto.toLowerCase()} para imprimir: 20 operaciones en vertical de dos cifras y de tres cifras, con solución. PDF gratis o fichas nuevas al instante.`,
  h1: `${corto} para imprimir`,
  entrada,
  hojas: [
    { tipo: 'operaciones', op, digitos: 2, llevada, titulo: `${corto} de dos cifras` },
    { tipo: 'operaciones', op, digitos: 3, llevada, titulo: `${corto} de tres cifras` }
  ],
  copias: 2,
  cuerpo: explicacion + `
<h2>Cómo están hechas las fichas</h2>
<p>Cada hoja trae 20 operaciones colocadas en vertical, con las cifras bien alineadas en columnas y espacio debajo para el resultado. Los números se eligen al azar, pero el programa descarta las operaciones que no encajan con el tipo de ficha y las repetidas. Al pulsar «Otra distinta» obtienes veinte nuevas.</p>
<p>La solución sale en una hoja aparte con los resultados en rojo, útil para que el niño se corrija solo.</p>`
});

module.exports = [
  // ---------------- TABLAS ----------------
  {
    cat: 'tablas-de-multiplicar', slug: '', corto: 'Tablas de multiplicar', nav: 'Tablas de multiplicar',
    title: 'Tablas de multiplicar para imprimir (del 1 al 10)',
    desc: 'Tablas de multiplicar del 1 al 10 para imprimir en una hoja A4, en PDF gratis. También cada tabla por separado, para rellenar y con ejercicios.',
    h1: 'Tablas de multiplicar para imprimir',
    resumen: 'Del 1 al 10, láminas y ejercicios',
    entrada: 'Las diez tablas de multiplicar en una sola hoja A4, limpia y en blanco y negro, para pegar en la carpeta o en la pared. Debajo tienes cada tabla por separado con sus ejercicios, la tabla pitagórica y las versiones en blanco para rellenar.',
    hojas: [{ tipo: 'tablas-todas' }, { tipo: 'mult-practica', tablas: [2, 3, 4, 5, 6, 7, 8, 9], titulo: 'Repaso de las tablas' }],
    copias: 2,
    cuerpo: `
<h2>En qué orden aprender las tablas</h2>
<p>No hace falta ir del 1 al 10. Muchos maestros siguen un orden que va de lo fácil a lo difícil y aprovecha lo ya aprendido:</p>
<ol>
<li><strong>Tablas del 1 y del 10</strong>: no requieren memoria, solo entender la regla.</li>
<li><strong>Tablas del 2 y del 5</strong>: dobles y resultados terminados en 0 o 5.</li>
<li><strong>Tabla del 4</strong>: el doble de la del 2.</li>
<li><strong>Tablas del 3 y del 6</strong>: la del 6 es el doble de la del 3.</li>
<li><strong>Tabla del 9</strong>: tiene patrones muy claros y el truco de los dedos.</li>
<li><strong>Tablas del 8 y del 7</strong>: las últimas, cuando ya casi todo está aprendido.</li>
</ol>
<h2>En realidad hay que memorizar muy poco</h2>
<p>Las diez tablas suman 100 multiplicaciones, pero el orden de los factores no altera el producto: 6 × 8 y 8 × 6 son el mismo dato. Si quitamos las repetidas y las tablas del 1 y del 10, quedan 36 resultados. Y si el niño ya domina las del 2 y del 5, quedan 21. Contado así impresiona mucho menos, y es bueno decírselo.</p>
<h2>Cómo practicar sin aburrirse</h2>
<p>Cinco minutos al día funcionan mejor que una hora el domingo. Cuelga la lámina en un sitio de paso, pregunta dos o tres multiplicaciones sueltas en el desayuno y usa la ficha de repaso una vez por semana para ver cuáles fallan. Las que fallan son las únicas que merece la pena repetir.</p>
<p>Plastificar la hoja para rellenar y usar un rotulador borrable permite repetirla sin gastar papel.</p>`,
    faq: [
      ['¿A qué edad se aprenden las tablas de multiplicar?', 'En España se introducen normalmente en segundo de primaria (7-8 años) y se consolidan en tercero. Lo importante es que antes el niño entienda la multiplicación como suma repetida.'],
      ['¿Las tablas llegan hasta el 10 o hasta el 12?', 'En los colegios españoles se estudian del 1 al 10, y así están estas hojas. Las tablas del 11 y del 12 son habituales en países anglosajones.'],
      ['¿Qué es la tabla pitagórica?', 'Es un cuadro de doble entrada con los números del 1 al 10 en la primera fila y en la primera columna; cada casilla contiene el producto de su fila por su columna. Reúne las diez tablas en un solo cuadro.']
    ],
    amazon: [['Fundas para plastificar A4', 'fundas plastificar A4'], ['Rotuladores borrables de punta fina', 'rotuladores borrables punta fina']]
  },
  ...tablasN,
  {
    cat: 'tablas-de-multiplicar', slug: 'tabla-pitagorica', corto: 'Tabla pitagórica',
    title: 'Tabla pitagórica para imprimir (completa y en blanco)',
    desc: 'Tabla pitagórica del 1 al 10 para imprimir en A4: una hoja completa para consultar y otra en blanco para rellenar, con solución. PDF gratis.',
    h1: 'Tabla pitagórica para imprimir',
    entrada: 'La tabla pitagórica reúne todas las tablas de multiplicar en un cuadro de 10 × 10. Aquí la tienes completa, para consultar, y vacía, para que el alumno la rellene.',
    hojas: [{ tipo: 'pitagorica' }, { tipo: 'pitagorica', vacia: true, titulo: 'Tabla pitagórica en blanco' }],
    copias: 1,
    cuerpo: `
<h2>Cómo se lee</h2>
<p>Para saber cuánto es 6 × 8, busca el 6 en la primera columna y el 8 en la primera fila. Sigue la fila del 6 hacia la derecha y la columna del 8 hacia abajo: se cruzan en el 48.</p>
<h2>Lo que enseña la tabla</h2>
<p><strong>La propiedad conmutativa se ve.</strong> La tabla es simétrica respecto a la diagonal que va de arriba a la izquierda hacia abajo a la derecha: el 6 × 8 y el 8 × 6 ocupan casillas espejo con el mismo número.</p>
<p><strong>La diagonal son los cuadrados.</strong> 1, 4, 9, 16, 25, 36, 49, 64, 81 y 100 son los resultados de multiplicar cada número por sí mismo.</p>
<p><strong>También sirve para dividir.</strong> Para calcular 56 : 7, recorre la fila del 7 hasta encontrar el 56 y mira en qué columna está: la del 8.</p>
<h2>Ideas para la tabla en blanco</h2>
<p>No hace falta rellenarla en orden. Se puede empezar por las filas fáciles (1, 10, 2 y 5), copiar después sus columnas gemelas y dejar para el final el bloque central del 6 al 9, que es donde están las multiplicaciones que más cuestan. También funciona cronometrar el tiempo y tratar de mejorarlo cada semana.</p>`
  },
  {
    cat: 'tablas-de-multiplicar', slug: 'para-rellenar', corto: 'Tablas para rellenar',
    title: 'Tablas de multiplicar para rellenar e imprimir (PDF)',
    desc: 'Tablas de multiplicar en blanco para rellenar: las diez tablas del 1 al 10 sin resultados en una hoja A4, con solución. PDF gratis para imprimir.',
    h1: 'Tablas de multiplicar para rellenar',
    entrada: 'Las tablas del 1 al 10 con los resultados en blanco, en una sola hoja. Sirven como control rápido: en diez minutos se ve qué tablas están aprendidas y cuáles no.',
    hojas: [{ tipo: 'tablas-todas', vacia: true, titulo: 'Tablas de multiplicar para rellenar' }],
    copias: 1,
    cuerpo: `
<h2>Cómo aprovechar la hoja</h2>
<p>Si el alumno está empezando, pídele solo las tablas que ya ha trabajado y tacha el resto. Si está repasando, que la complete entera y anote el tiempo. Al corregir con la hoja de soluciones, rodea los fallos: suelen concentrarse en muy pocas multiplicaciones (6 × 7, 7 × 8, 8 × 9, 6 × 8), y son esas las que conviene practicar.</p>
<p>Para practicar una sola tabla con las multiplicaciones desordenadas, entra en la página de cada una, por ejemplo la <a href="/tablas-de-multiplicar/tabla-del-7/">tabla del 7</a> o la <a href="/tablas-de-multiplicar/tabla-del-8/">tabla del 8</a>. Y si prefieres el formato de cuadro, tienes la <a href="/tablas-de-multiplicar/tabla-pitagorica/">tabla pitagórica en blanco</a>.</p>
<h2>Para reutilizarla</h2>
<p>Métela en una funda de plástico transparente y escribe encima con rotulador borrable. Se limpia con un pañuelo y sirve para toda la semana.</p>`,
    amazon: [['Fundas para plastificar A4', 'fundas plastificar A4'], ['Rotuladores borrables de punta fina', 'rotuladores borrables punta fina']]
  },

  // ---------------- SUMAS Y RESTAS ----------------
  {
    cat: 'sumas-y-restas', slug: '', corto: 'Sumas y restas', nav: 'Sumas y restas',
    title: 'Fichas de sumas y restas para imprimir (PDF gratis)',
    desc: 'Fichas de sumas y restas para imprimir, con y sin llevada, de dos y tres cifras. 20 operaciones por hoja con solución. PDF gratis para primaria.',
    h1: 'Fichas de sumas y restas para imprimir',
    resumen: 'Con y sin llevada, de dos y tres cifras',
    entrada: 'Fichas de cálculo para primero, segundo y tercero de primaria: veinte operaciones en vertical por hoja, con su solución. Esta primera mezcla sumas y restas sin llevada; más abajo las tienes separadas por tipo.',
    hojas: [{ tipo: 'operaciones', op: 'mixta', digitos: 2, llevada: false, titulo: 'Sumas y restas sin llevada' }],
    copias: 4,
    cuerpo: `
<h2>Por dónde empezar</h2>
<p>El orden habitual en el colegio es este, y conviene no saltarse pasos:</p>
<ol>
<li><a href="/sumas-y-restas/sumas-sin-llevada/">Sumas sin llevada</a>: cada columna suma 9 o menos.</li>
<li><a href="/sumas-y-restas/restas-sin-llevada/">Restas sin llevada</a>: cada cifra de arriba es mayor o igual que la de abajo.</li>
<li><a href="/sumas-y-restas/sumas-con-llevada/">Sumas con llevada</a>: alguna columna pasa de 9 y hay que «llevarse una».</li>
<li><a href="/sumas-y-restas/restas-con-llevada/">Restas con llevada</a>: la más difícil de las cuatro.</li>
</ol>
<h2>Qué significa «llevada»</h2>
<p>En una suma, cuando las unidades suman 10 o más, se escribe solo la cifra de las unidades y la decena se añade a la columna siguiente. En 47 + 38, siete y ocho son quince: se escribe el 5 y «me llevo una», que se suma a las decenas. En la resta ocurre lo contrario: si arriba hay menos unidades que abajo, hay que tomar una decena prestada.</p>
<h2>Cuántas hacer</h2>
<p>Una ficha de veinte operaciones al día es más que suficiente; con niños que empiezan, media ficha. Importa más la regularidad que la cantidad. Si falla más de cinco de veinte, conviene volver al paso anterior en lugar de insistir.</p>`,
    faq: [
      ['¿Para qué curso son estas fichas?', 'Las de dos cifras sin llevada, para primero de primaria; las de llevada, para segundo; las de tres cifras, para segundo y tercero. Es una orientación: cada colegio lleva su ritmo.'],
      ['¿Por qué las operaciones van en vertical?', 'Porque el algoritmo que se enseña en primaria trabaja por columnas: unidades con unidades y decenas con decenas. Colocarlas bien alineadas es parte de lo que se aprende.']
    ]
  },
  sr('sumas-sin-llevada', 'Sumas sin llevada', 'suma', false,
    'Sumas en vertical en las que ninguna columna pasa de 9, así que no hay que llevarse nada. Son las primeras sumas «de verdad» que se hacen en primero de primaria.',
    `<h2>Qué se trabaja</h2>
<p>El objetivo es aprender el procedimiento: empezar por la derecha, sumar las unidades, escribir el resultado debajo y pasar a las decenas. Como ninguna columna supera el 9, el niño se concentra en el orden y en la colocación sin la dificultad añadida de la llevada.</p>
<p>Si todavía cuenta con los dedos, no pasa nada: la rapidez llega con la práctica. Cuando resuelva una ficha entera con uno o dos fallos como mucho, puede pasar a las <a href="/sumas-y-restas/sumas-con-llevada/">sumas con llevada</a>.</p>`),
  sr('sumas-con-llevada', 'Sumas con llevada', 'suma', true,
    'Sumas en vertical en las que al menos una columna suma 10 o más. Es el paso que más cuesta en segundo de primaria y el que más práctica necesita.',
    `<h2>Cómo explicar la llevada</h2>
<p>Tomemos 47 + 38. Unidades: 7 + 8 = 15. Quince son una decena y cinco unidades, así que debajo se escribe el 5 y la decena se anota, pequeña, encima de la columna de las decenas. Después se suman las decenas contando la que nos hemos llevado: 1 + 4 + 3 = 8. Resultado: 85.</p>
<p>Ayuda mucho que el niño escriba siempre la llevada encima, aunque crea que la recuerda: el fallo más común es olvidarla al sumar la columna siguiente. En las sumas de tres cifras puede haber llevada en las unidades, en las decenas o en las dos.</p>`),
  sr('restas-sin-llevada', 'Restas sin llevada', 'resta', false,
    'Restas en vertical en las que cada cifra de arriba es mayor o igual que la de abajo. No hay que pedir prestado: se resta columna a columna.',
    `<h2>Qué se trabaja</h2>
<p>Igual que en la suma, se empieza por las unidades. La diferencia es que aquí el orden importa: siempre se resta la cifra de abajo a la de arriba. En 68 − 25, ocho menos cinco son tres y seis menos dos son cuatro: 43.</p>
<p>Un buen hábito desde el principio es comprobar la resta con una suma: el resultado más el número de abajo tiene que dar el de arriba (43 + 25 = 68). Cuando estas fichas salgan bien, el siguiente paso son las <a href="/sumas-y-restas/restas-con-llevada/">restas con llevada</a>.</p>`),
  sr('restas-con-llevada', 'Restas con llevada', 'resta', true,
    'Restas en vertical en las que alguna cifra de arriba es menor que la de abajo y hay que «pedir prestado». Es la operación más difícil del primer ciclo de primaria.',
    `<h2>Dos formas de explicarla</h2>
<p>Tomemos 52 − 27. De 2 no se pueden quitar 7.</p>
<p><strong>Pidiendo prestado.</strong> Se toma una decena del 5, que se queda en 4, y las unidades pasan a ser 12. Ahora 12 − 7 = 5 y 4 − 2 = 2. Resultado: 25. Es el método que mejor se entiende, porque se ve qué pasa con las decenas.</p>
<p><strong>Llevándose una.</strong> Es el método tradicional en España: «del 7 al 12 van 5 y me llevo una»; esa una se suma al 2 de abajo, que pasa a ser 3, y «del 3 al 5 van 2». Resultado: 25. Es más rápido, pero conviene enseñarlo después de entender el primero.</p>
<p>Lo importante es usar en casa el mismo método que en clase. Si no sabes cuál es, pregunta al tutor antes de explicar otro.</p>`),

  // ---------------- PAPEL ----------------
  {
    cat: 'papel', slug: '', corto: 'Papel para imprimir', nav: 'Papel',
    title: 'Papel para imprimir: milimetrado, cuadriculado, pautado',
    desc: 'Hojas de papel para imprimir en A4: milimetrado, cuadriculado de 4 y 5 mm, pautado, pentagramas y punteado. PDF gratis a tamaño real.',
    h1: 'Papel para imprimir',
    resumen: 'Milimetrado, cuadrícula, pauta, pentagramas y puntos',
    entrada: 'Cuando se acaba el cuaderno o hace falta una sola hoja de papel milimetrado, no merece la pena comprar un bloc entero. Estas plantillas en A4 están dibujadas a tamaño real: si imprimes al 100 %, un milímetro en la hoja es un milímetro de verdad.',
    hojas: [{ tipo: 'papel', clase: 'cuadriculado', paso: 5, alt: 'Papel cuadriculado de 5 mm' }],
    copias: 1,
    cuerpo: `
<h2>Lo más importante: imprimir al 100 %</h2>
<p>Los programas de impresión suelen activar por defecto «Ajustar a la página», que encoge la hoja entre un 3 y un 6 %. Para un pasatiempo da igual, pero en un papel milimetrado significa que diez centímetros medirán nueve y medio. Antes de imprimir, busca la opción <strong>Escala: 100 %</strong> o <strong>Tamaño real</strong> y desactiva cualquier ajuste automático.</p>
<p>Para comprobarlo, mide con una regla después de imprimir: en el milimetrado, entre dos líneas gruesas tiene que haber exactamente un centímetro.</p>
<h2>Qué papel usar para cada cosa</h2>
<ul>
<li><a href="/papel/milimetrado/">Milimetrado</a>: gráficas de matemáticas y física, dibujo técnico, patrones a escala.</li>
<li><a href="/papel/cuadriculado/">Cuadriculado</a>: operaciones, cuentas en columna, dibujos de simetría y juegos de papel y lápiz.</li>
<li><a href="/papel/pautado/">Pautado</a>: caligrafía y primeros cursos de primaria.</li>
<li><a href="/papel/pentagramas/">Pentagramas</a>: lenguaje musical y composición.</li>
<li><a href="/papel/puntos/">Punteado</a>: agendas tipo bullet journal, bocetos y diagramas.</li>
</ul>
<h2>Papel y tinta</h2>
<p>Con folio normal de 80 gramos basta. Si vas a escribir con pluma o rotulador, un papel de 90 o 100 gramos evita que la tinta traspase. Las líneas son finas y de color suave para que no compitan con lo que escribas; si tu impresora es en blanco y negro, saldrán en gris claro.</p>`,
    faq: [
      ['¿Por qué las líneas no llegan al borde del papel?', 'Casi ninguna impresora doméstica imprime hasta el borde: deja entre 3 y 5 mm sin tinta. Las plantillas tienen un margen de 10 mm para que la cuadrícula salga completa en cualquier impresora.'],
      ['¿Puedo imprimir por las dos caras?', 'Sí. Activa la impresión a doble cara en tu impresora o imprime una cara, da la vuelta al papel y vuelve a imprimir.']
    ],
    amazon: [['Papel A4 de 100 gramos', 'papel A4 100 g 500 hojas']]
  },
  {
    cat: 'papel', slug: 'milimetrado', corto: 'Papel milimetrado',
    title: 'Papel milimetrado para imprimir en A4 (PDF gratis)',
    desc: 'Papel milimetrado A4 para imprimir a tamaño real: líneas cada 1 mm, reforzadas cada 5 mm y cada centímetro. PDF gratis en naranja clásico y en gris.',
    h1: 'Papel milimetrado para imprimir',
    entrada: 'Una hoja de papel milimetrado en A4 con una zona útil de 19 × 27 cm, líneas cada milímetro y refuerzos cada medio centímetro y cada centímetro. Disponible en el naranja de toda la vida y en gris, para impresoras en blanco y negro.',
    hojas: [
      { tipo: 'papel', clase: 'milimetrado', alt: 'Papel milimetrado naranja' },
      { tipo: 'papel', clase: 'milimetrado', color: '#6f7480', alt: 'Papel milimetrado gris' }
    ],
    copias: 1,
    cuerpo: `
<h2>Imprime al 100 % o no será milimetrado</h2>
<p>Es el único requisito y el error más frecuente. En el cuadro de impresión, elige <strong>Escala 100 %</strong> o <strong>Tamaño real</strong> y desmarca «Ajustar a la página». Luego compruébalo con una regla: entre dos líneas gruesas debe haber 10 mm exactos, y la cuadrícula completa mide 190 mm de ancho por 270 mm de alto.</p>
<h2>Cómo es la cuadrícula</h2>
<p>Tiene tres grosores de línea, igual que el papel milimetrado de papelería. Las más finas marcan cada milímetro; las intermedias, cada 5 mm; las gruesas, cada centímetro. Eso da 19 centímetros en horizontal y 27 en vertical, suficientes para la mayoría de las gráficas de secundaria y bachillerato.</p>
<h2>Para qué se usa</h2>
<p>Para representar funciones y datos experimentales con precisión, para dibujar a escala (un plano a 1:100 convierte cada centímetro en un metro), para trazar patrones de costura o punto de cruz y para cualquier dibujo en el que haga falta medir sin regla.</p>
<p>Si solo necesitas cuadritos para hacer cuentas, te servirá mejor el <a href="/papel/cuadriculado/">papel cuadriculado</a>, que gasta menos tinta.</p>`,
    amazon: [['Papel A4 de 100 gramos', 'papel A4 100 g 500 hojas'], ['Portaminas de 0,5 mm', 'portaminas 0.5']]
  },
  {
    cat: 'papel', slug: 'cuadriculado', corto: 'Papel cuadriculado',
    title: 'Papel cuadriculado para imprimir: 4 mm y 5 mm (PDF)',
    desc: 'Hojas cuadriculadas para imprimir en A4, con cuadrícula de 4 mm (cuaderno escolar) y de 5 mm. PDF gratis a tamaño real, en azul grisáceo suave.',
    h1: 'Papel cuadriculado para imprimir',
    entrada: 'Hojas de cuadros en A4 con las dos medidas más usadas: la cuadrícula de 4 mm de los cuadernos escolares españoles y la de 5 mm de los blocs de notas.',
    hojas: [
      { tipo: 'papel', clase: 'cuadriculado', paso: 4, alt: 'Papel cuadriculado de 4 mm' },
      { tipo: 'papel', clase: 'cuadriculado', paso: 5, alt: 'Papel cuadriculado de 5 mm' }
    ],
    copias: 1,
    cuerpo: `
<h2>¿4 mm o 5 mm?</h2>
<p>La cuadrícula de <strong>4 mm</strong> es la del cuaderno escolar de toda la vida y la que piden casi todos los colegios a partir de tercero de primaria. Si la hoja es para deberes o para sustituir una página de cuaderno, elige esta.</p>
<p>La de <strong>5 mm</strong> es la habitual en blocs, libretas de notas y cuadernos técnicos. Tiene la ventaja de que dos cuadros hacen un centímetro, lo que facilita dibujar a escala y hacer gráficas sencillas.</p>
<p>Para los más pequeños, que escriben números grandes, hay cuadernos de 6 y 8 mm. Si necesitas esa medida, imprime la hoja de 4 mm al 150 % o al 200 %.</p>
<h2>Para qué sirve una hoja de cuadros</h2>
<p>Para colocar operaciones en columna (una cifra por cuadro), dibujar figuras simétricas, hacer ampliaciones y reducciones, diseñar pixel art o plantillas de abalorios y jugar a los barcos, al tres en raya o a los puntitos.</p>
<p>Como en todas las plantillas de papel, imprime con <strong>escala 100 %</strong> para que los cuadros midan lo que deben.</p>`
  },
  {
    cat: 'papel', slug: 'pautado', corto: 'Papel pautado',
    title: 'Papel pautado para imprimir: pauta de 3,5 mm y rayado',
    desc: 'Hojas pautadas para imprimir en A4: doble línea de 3,5 mm para caligrafía y rayado horizontal de 8 mm con margen. PDF gratis a tamaño real.',
    h1: 'Papel pautado para imprimir',
    entrada: 'Dos hojas para escribir: una con pauta de doble línea de 3,5 mm, la que se usa para aprender a escribir, y otra con rayado horizontal de 8 mm y margen rojo, como un cuaderno de una raya.',
    hojas: [
      { tipo: 'papel', clase: 'pautado', pauta: 3.5, alt: 'Papel pautado con pauta de 3,5 mm' },
      { tipo: 'papel', clase: 'rayado', paso: 8, alt: 'Papel rayado de 8 mm con margen' }
    ],
    copias: 1,
    cuerpo: `
<h2>Qué es la pauta</h2>
<p>En el papel pautado cada renglón son dos líneas paralelas. El cuerpo de las letras minúsculas (a, e, o, m) se escribe entre las dos; los palos altos de la b, la d o la l suben por encima, y los rabos de la g, la p o la q bajan por debajo. La separación entre las dos líneas es la «medida de la pauta».</p>
<p>La de <strong>3,5 mm</strong> es la más extendida en primero y segundo de primaria. Para niños que empiezan, en infantil, se usan pautas más anchas, de 5 mm; puedes conseguirla imprimiendo esta hoja al 140 %. Hacia tercero se pasa a 2,5 mm (imprime al 70 %) y después a la raya sencilla.</p>
<h2>La hoja rayada</h2>
<p>El rayado de 8 mm es el de los cuadernos «de una raya» para adultos y para los últimos cursos de primaria. Lleva un margen vertical a la izquierda, a 28 mm del borde, que deja sitio para taladrar la hoja y archivarla.</p>
<h2>Consejo para caligrafía</h2>
<p>Si la hoja es para practicar letra, escribe tú la primera palabra de cada renglón como modelo, con rotulador fino, antes de fotocopiarla. El niño copia mejor un trazo real que una tipografía de ordenador.</p>`
  },
  {
    cat: 'papel', slug: 'pentagramas', corto: 'Pentagramas',
    title: 'Pentagramas para imprimir: papel pautado de música',
    desc: 'Hoja de pentagramas en blanco para imprimir en A4: diez pentagramas por página con buena separación para escribir notas y letra. PDF gratis.',
    h1: 'Pentagramas para imprimir',
    entrada: 'Papel de música en blanco, con diez pentagramas por hoja en A4 vertical y espacio entre ellos para líneas adicionales, matices o la letra de una canción. También una versión de seis pentagramas más grandes para quien empieza.',
    hojas: [
      { tipo: 'papel', clase: 'pentagrama', n: 10, sep: 2, alt: 'Hoja con diez pentagramas' },
      { tipo: 'papel', clase: 'pentagrama', n: 6, sep: 3, alt: 'Hoja con seis pentagramas grandes' }
    ],
    copias: 1,
    cuerpo: `
<h2>Dos tamaños</h2>
<p>La hoja de <strong>diez pentagramas</strong> tiene las líneas separadas 2 mm, de modo que cada pentagrama mide 8 mm de alto: es el tamaño de los cuadernos de música de conservatorio y de escuela de música.</p>
<p>La de <strong>seis pentagramas</strong> separa las líneas 3 mm (12 mm de alto por pentagrama). Va mejor para niños que empiezan lenguaje musical en primaria, porque las cabezas de las notas se dibujan más grandes y es más fácil acertar con la línea o el espacio.</p>
<h2>Para qué se usa</h2>
<p>Para dictados y ejercicios de lenguaje musical, para copiar una partitura, para anotar una melodía o para armonía a cuatro voces. Los pentagramas vienen sin clave ni compás: así sirven igual para clave de sol, de fa o de do, y para unirlos de dos en dos con una llave si escribes para piano.</p>
<h2>Con qué escribir</h2>
<p>Lápiz blando (2B) si vas a corregir, o un rotulador calibrado de 0,5 mm para pasar a limpio. En papel de 90 o 100 gramos la tinta no traspasa y se puede usar la hoja por las dos caras.</p>`,
    amazon: [['Cuadernos de música pautados', 'cuaderno musica pentagramas'], ['Lápices 2B', 'lapices 2B']]
  },
  {
    cat: 'papel', slug: 'puntos', corto: 'Papel punteado',
    title: 'Papel punteado para imprimir: hoja de puntos de 5 mm',
    desc: 'Hoja de puntos para imprimir en A4, con retícula de 5 mm como la de los cuadernos bullet journal. PDF gratis a tamaño real, en gris suave.',
    h1: 'Papel punteado para imprimir',
    entrada: 'Una hoja A4 con puntos cada 5 mm, la retícula de los cuadernos punteados. Guía la escritura y el dibujo como una cuadrícula, pero casi desaparece cuando la página está llena.',
    hojas: [{ tipo: 'papel', clase: 'puntos', paso: 5, alt: 'Papel punteado de 5 mm' }],
    copias: 1,
    cuerpo: `
<h2>Por qué puntos en lugar de cuadros</h2>
<p>La retícula de puntos da las mismas referencias que una cuadrícula, horizontales y verticales, con mucha menos tinta en el papel. Permite escribir recto, dibujar tablas y cajas sin regla y hacer bocetos a escala, y al terminar lo que se ve es tu contenido, no las líneas.</p>
<h2>Usos habituales</h2>
<p>Planificadores y agendas hechas a mano (el método bullet journal usa este papel), caligrafía y lettering, esquemas y diagramas, diseño de interfaces en papel y juegos como el de unir puntos para formar cuadrados.</p>
<p>La separación de 5 mm coincide con la de la mayoría de cuadernos punteados que se venden, así que estas hojas se pueden intercalar en uno de anillas sin que cambie la retícula. Imprime con <strong>escala 100 %</strong> para conservar la medida.</p>
<h2>Si lo vas a encuadernar</h2>
<p>Imprime a doble cara en papel de 100 gramos para que los rotuladores no traspasen. Para tamaño A5, imprime dos páginas por hoja y corta por la mitad: la retícula quedará a unos 3,5 mm.</p>`,
    amazon: [['Papel A4 de 100 gramos', 'papel A4 100 g 500 hojas'], ['Rotuladores calibrados', 'rotuladores calibrados punta fina']]
  }
];
