// Problemas de matemáticas generados con plantillas (lib/puzzles.js, PROBLEMAS).

const comoResolver = `
<h2>Cómo resolver un problema, paso a paso</h2>
<ol>
<li><strong>Leer el problema entero</strong>, dos veces si hace falta, antes de hacer ninguna cuenta.</li>
<li><strong>Subrayar los datos</strong> (los números y a qué se refieren) y <strong>rodear la pregunta</strong>.</li>
<li><strong>Pensar qué operación</strong> responde a la pregunta: si se junta o se añade, suma; si se quita, se gasta o se pregunta cuánto falta, resta; si se repite la misma cantidad varias veces, multiplicación; si se reparte o se agrupa, división.</li>
<li><strong>Hacer la operación</strong> en el recuadro.</li>
<li><strong>Escribir la solución con su unidad</strong>: no «24», sino «24 galletas». Y comprobar si tiene sentido: si a alguien le devuelven más dinero del que ha pagado, algo ha fallado.</li>
</ol>`;

const enlaces = `
<p>Si todavía cuestan las operaciones, conviene repasarlas antes por separado: <a href="/sumas-y-restas/">sumas y restas</a>, <a href="/tablas-de-multiplicar/">tablas de multiplicar</a> y <a href="/multiplicaciones-y-divisiones/">multiplicaciones y divisiones</a>.</p>`;

module.exports = [
  {
    cat: 'problemas-de-matematicas', slug: '', corto: 'Problemas', nav: 'Problemas',
    resumen: 'Problemas de primaria por cursos, con solución',
    title: 'Problemas de matemáticas para primaria para imprimir',
    desc: 'Problemas de matemáticas para primaria para imprimir, con solución: de sumas y restas, de multiplicar y dividir y de dos operaciones. Distintos cada vez.',
    h1: 'Problemas de matemáticas para primaria',
    entrada: 'Problemas de matemáticas con situaciones del día a día (cromos, autobuses, excursiones, la compra) para resolver en papel y con la solución aparte. Los enunciados se generan a partir de plantillas, así que con «Otra distinta» salen problemas nuevos con otros números y otros nombres.',
    hojas: [
      { tipo: 'problemas', nivel: 'sumas', n: 6, titulo: 'Problemas de sumas y restas' },
      { tipo: 'problemas', nivel: 'mult', n: 6, titulo: 'Problemas de multiplicar y dividir' }
    ],
    copias: 2,
    cuerpo: `
<h2>Por cursos</h2>
<ul>
<li><a href="/problemas-de-matematicas/sumas-y-restas/">Problemas de sumas y restas</a>, para primero y segundo de primaria.</li>
<li><a href="/problemas-de-matematicas/multiplicacion-y-division/">Problemas de multiplicación y división</a>, para tercero y cuarto.</li>
<li><a href="/problemas-de-matematicas/dos-operaciones/">Problemas de dos operaciones</a>, para cuarto y quinto, en los que hay que encadenar varias cuentas.</li>
</ul>
${comoResolver}
<h2>Por qué cuestan tanto los problemas</h2>
<p>Un niño puede hacer bien una resta y no saber cuándo hay que restar. El problema obliga a dos cosas a la vez: entender lo que se cuenta y traducirlo a una operación. Por eso conviene leerlos en voz alta, sobre todo en los primeros cursos, y preguntar «¿qué nos piden?» antes de cualquier cuenta.</p>
<p>Las palabras clave ayudan («más», «en total», «quedan», «cada uno», «repartir»), pero no siempre funcionan: «Lucía tiene 3 años menos que su hermano» lleva un «menos» y aun así puede pedir una suma si la pregunta es la edad del hermano. Lo que funciona de verdad es imaginar la situación.</p>
${enlaces}`,
    faq: [
      ['¿Los problemas tienen solución?', 'Sí. «Ver solución» muestra la hoja resuelta con las operaciones paso a paso y la respuesta con su unidad. En el PDF, las soluciones van al final.'],
      ['¿Se repiten los problemas?', 'Cada hoja combina al azar entre ocho y diez tipos de problema por nivel, con nombres y números distintos cada vez. Puede repetirse el tipo de situación, pero no los datos.']
    ]
  },
  {
    cat: 'problemas-de-matematicas', slug: 'sumas-y-restas', corto: 'Sumas y restas (1.º y 2.º)',
    title: 'Problemas de sumas y restas para imprimir (1.º y 2.º)',
    desc: 'Problemas de sumas y restas para primero y segundo de primaria, con números hasta 100 y solución. Seis problemas por hoja, distintos cada vez. PDF gratis.',
    h1: 'Problemas de sumas y restas',
    entrada: 'Problemas de una sola operación, sumar o restar, con números hasta el cien: cromos, lápices, el autobús, la biblioteca. Para primero y segundo de primaria. Seis por hoja, con sitio para la cuenta y la solución.',
    hojas: [{ tipo: 'problemas', nivel: 'sumas', n: 6, titulo: 'Problemas de sumas y restas' }],
    copias: 4,
    cuerpo: `
<h2>Suma o resta: cómo distinguirlas</h2>
<p>En estos problemas siempre hay una sola operación, y la duda es cuál. Una pregunta sencilla ayuda: <em>¿al final hay más o menos que al principio?</em> Si llegan niños al patio o regalan cromos, hay más: se suma. Si se bajan del autobús, se gastan euros o falta algo por leer, hay menos o se pregunta la diferencia: se resta.</p>
<p>Para los más pequeños funciona mucho dibujar el problema: unos palitos para los cromos que tiene, otros para los que le regalan, y contar. Cuando el dibujo se vuelve pesado (por ejemplo, con 46 páginas), es el momento de pasar a la operación.</p>
${comoResolver}
<p>Cuando estos salgan solos, el siguiente paso son los <a href="/problemas-de-matematicas/multiplicacion-y-division/">problemas de multiplicación y división</a>.</p>`
  },
  {
    cat: 'problemas-de-matematicas', slug: 'multiplicacion-y-division', corto: 'Multiplicación y división (3.º y 4.º)',
    title: 'Problemas de multiplicación y división para imprimir',
    desc: 'Problemas de multiplicación y división para tercero y cuarto de primaria, con solución: repartos, grupos, precios y repartos con resto. PDF gratis.',
    h1: 'Problemas de multiplicación y división',
    entrada: 'Problemas de una operación para tercero y cuarto de primaria: cajas de galletas, filas de un autobús, repartos de caramelos y equipos en los que sobran alumnos. Seis por hoja, con solución.',
    hojas: [{ tipo: 'problemas', nivel: 'mult', n: 6, titulo: 'Problemas de multiplicar y dividir' }],
    copias: 4,
    cuerpo: `
<h2>Multiplicar o dividir</h2>
<p><strong>Se multiplica</strong> cuando se repite la misma cantidad varias veces: 6 paquetes de 8 galletas, 7 días por semana durante 5 semanas, una entrada de 7 euros para 4 amigos.</p>
<p><strong>Se divide</strong> cuando se reparte en partes iguales («¿cuántos le tocan a cada uno?») o cuando se agrupa («¿cuántas cajas hacen falta?», «¿cuántos equipos se forman?»).</p>
<h2>Los problemas con resto</h2>
<p>Algunos problemas de división tienen resto y la pregunta es qué hacer con él. En el de los equipos, el resto son alumnos que se quedan sin equipo completo. En otros, como el de los autobuses de la excursión, el resto obliga a sumar uno más: si sobran personas, hace falta otro autobús. Pensar qué significa el resto en cada caso es una de las cosas más útiles que enseñan estos problemas.</p>
${comoResolver}
<p>Para practicar las operaciones por separado tienes las <a href="/multiplicaciones-y-divisiones/divisiones-de-una-cifra/">divisiones de una cifra</a> y las <a href="/multiplicaciones-y-divisiones/multiplicaciones-por-una-cifra/">multiplicaciones por una cifra</a>.</p>`
  },
  {
    cat: 'problemas-de-matematicas', slug: 'dos-operaciones', corto: 'Dos operaciones (4.º y 5.º)',
    title: 'Problemas de dos operaciones para imprimir (4.º y 5.º)',
    desc: 'Problemas de dos o más operaciones para cuarto y quinto de primaria, con la solución paso a paso: compras, granjas, excursiones y repartos. PDF gratis.',
    h1: 'Problemas de dos operaciones',
    entrada: 'Problemas en los que hay que encadenar dos o tres cuentas para llegar a la respuesta: el cambio de una compra, las patas de los animales de una granja, los autobuses que hacen falta para una excursión. Para cuarto y quinto de primaria, con la solución paso a paso.',
    hojas: [{ tipo: 'problemas', nivel: 'mixto', n: 5, titulo: 'Problemas de dos operaciones' }],
    copias: 4,
    cuerpo: `
<h2>Cómo plantearlos</h2>
<p>La clave está en no buscar «la» operación, sino preguntarse <em>qué necesito saber antes</em>. Para saber cuánto te devuelven, primero necesitas saber cuánto cuesta la compra. Para saber cuántas páginas quedan, primero necesitas saber cuántas ha leído en total. Cada «antes» es una operación.</p>
<p>Ayuda escribir cada paso con una frase corta delante: «Lo que cuestan los cuadernos: 4 × 3 = 12 euros». «Lo que me devuelven: 20 − 12 = 8 euros». Así se ve qué representa cada número y es más fácil encontrar el error si lo hay.</p>
<h2>Cómo están hechas las soluciones</h2>
<p>La hoja de soluciones no da solo el resultado: muestra cada operación en orden, separadas por punto y coma. Si el resultado final no coincide, se puede comparar paso a paso y ver en cuál se ha equivocado.</p>
${comoResolver}
${enlaces}`
  }
];
