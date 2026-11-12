// Multiplicaciones y divisiones. Los ejercicios en pantalla los corrige src/js/app.js
// (bloque «multiplicaciones y divisiones»); aquí se generan los primeros para que se vean sin JavaScript.

const R = '#c42e21';
const t = (x, y, v, o = {}) => `<text x="${x}" y="${y}" font-size="${o.s || 30}" text-anchor="${o.a || 'middle'}"${o.c ? ` fill="${o.c}"` : ''}${o.n ? '' : ' font-weight="700"'}>${v}</text>`;

const pasoMult = () => {
  // 23 × 14: columnas de centenas, decenas y unidades en x = 92, 120, 148
  const X = [92, 120, 148];
  const base = (extra) => `${t(X[1], 70, 2)}${t(X[2], 70, 3)}${t(64, 104, '×', { n: 1 })}${t(X[1], 104, 1)}${t(X[2], 104, 4)}<path d="M52 114H164" stroke="currentColor" stroke-width="2.5"/>${extra}`;
  const p1 = `${t(X[1], 40, 1, { s: 18, c: R })}${t(X[1], 146, 9, { c: R })}${t(X[2], 146, 2, { c: R })}`;
  const p2 = `${t(X[1], 146, 9)}${t(X[2], 146, 2)}${t(X[0], 180, 2, { c: R })}${t(X[1], 180, 3, { c: R })}${t(X[2], 180, '·', { c: R })}`;
  const p3 = `${t(X[1], 146, 9)}${t(X[2], 146, 2)}${t(X[0], 180, 2)}${t(X[1], 180, 3)}<path d="M52 192H164" stroke="currentColor" stroke-width="2.5"/>${t(X[0], 224, 3, { c: R })}${t(X[1], 224, 2, { c: R })}${t(X[2], 224, 2, { c: R })}`;
  const panel = (i, extra) => `<g transform="translate(${i * 220} 0)"><text x="12" y="24" font-size="15" font-weight="700" fill="${R}">Paso ${i + 1}</text>${base(extra)}</g>`;
  return `
<h2>Cómo se hace una multiplicación de dos cifras: ejemplo paso a paso</h2>
<figure class="paso-a-paso">
<svg viewBox="0 0 660 240" role="img" aria-label="Multiplicación de 23 por 14 en tres pasos: 23 por 4 igual a 92; 23 por 1 decena igual a 23, escrito un lugar a la izquierda; 92 más 230 igual a 322.">${panel(0, p1)}${panel(1, p2)}${panel(2, p3)}</svg>
<ol>
<li>Multiplica el número de arriba por las <strong>unidades</strong> de abajo: 23 × 4. Primero 3 × 4 = 12, escribes el 2 y te llevas 1; después 2 × 4 = 8, más 1 que llevabas, 9. Resultado: 92.</li>
<li>Multiplica por las <strong>decenas</strong>: 23 × 1 = 23. Como el 1 vale una decena, el resultado se escribe <strong>un lugar a la izquierda</strong>, dejando libre la columna de las unidades (hay quien pone un punto o un cero en ese hueco).</li>
<li><strong>Suma</strong> los dos resultados en columna: 92 + 230 = 322. Eso es 23 × 14.</li>
</ol>
</figure>`;
};

const pasoDiv = () => {
  // 157 : 4 en casita
  const X = [50, 76, 102];
  const casa = `${t(X[0], 70, 1)}${t(X[1], 70, 5)}${t(X[2], 70, 7)}<path d="M118 44V80H180" fill="none" stroke="currentColor" stroke-width="2.5"/>${t(132, 70, 4, { a: 'start' })}`;
  const p1 = `${t(132, 108, 3, { a: 'start', c: R })}${t(X[1], 108, 3, { c: R })}<path d="M38 46H90" stroke="${R}" stroke-width="2" stroke-dasharray="4 3"/>`;
  const p2 = `${t(132, 108, 3, { a: 'start' })}${t(X[1], 108, 3)}${t(X[2], 108, 7, { c: R })}${t(150, 108, 9, { a: 'start', c: R })}${t(X[2], 144, 1, { c: R })}`;
  const p3 = `${t(132, 108, 39, { a: 'start', c: R })}${t(X[1], 108, 3)}${t(X[2], 108, 7)}${t(X[2], 144, 1, { c: R })}<text x="12" y="186" font-size="15" fill="${R}" font-weight="700">cociente 39</text><text x="12" y="208" font-size="15" fill="${R}" font-weight="700">resto 1</text>`;
  const panel = (i, extra) => `<g transform="translate(${i * 220} 0)"><text x="12" y="24" font-size="15" font-weight="700" fill="${R}">Paso ${i + 1}</text>${casa}${extra}</g>`;
  return `
<h2>Cómo se hace una división de una cifra: ejemplo paso a paso</h2>
<figure class="paso-a-paso">
<svg viewBox="0 0 660 220" role="img" aria-label="División de 157 entre 4 en tres pasos: 15 entre 4 cabe a 3 y sobran 3; se baja el 7 y 37 entre 4 cabe a 9 y sobra 1; cociente 39 y resto 1.">${panel(0, p1)}${panel(1, p2)}${panel(2, p3)}</svg>
<ol>
<li>El 1 es menor que 4, así que se toman <strong>dos cifras</strong>: 15. ¿Cuántas veces cabe el 4 en 15? Tres veces (4 × 3 = 12). Escribe el 3 en el cociente y debajo del 15 lo que sobra: 15 − 12 = 3.</li>
<li><strong>Baja</strong> la siguiente cifra, el 7, al lado del 3: queda 37. El 4 cabe 9 veces en 37 (4 × 9 = 36). Escribe el 9 en el cociente y debajo lo que sobra: 37 − 36 = 1.</li>
<li>Ya no quedan cifras por bajar. El <strong>cociente</strong> es 39 y el <strong>resto</strong>, 1. Para comprobarlo: 4 × 39 + 1 = 157.</li>
</ol>
</figure>`;
};

// Ejercicio en pantalla: genera las primeras operaciones con una semilla fija
const azarFijo = (semilla) => { let x = semilla; return () => (x = (x * 1103515245 + 12345) % 2147483648) / 2147483648; };
const entre = (az, a, b) => a + Math.floor(az() * (b - a + 1));

const practicaMult = (a, b, titulo) => {
  const az = azarFijo(a * 131 + b * 17), ops = [], id = `m${a}${b}`;
  while (ops.length < 6) {
    const x = entre(az, 10 ** (a - 1), 10 ** a - 1), y = b === 1 ? entre(az, 2, 9) : entre(az, 12, 98);
    if (x % 10 === 0 || (b > 1 && (y % 10 < 2 || Math.floor(y / 10) < 2))) continue;
    ops.push([x, y]);
  }
  return `
<section class="practica practica-md" data-tipo="mult" data-a="${a}" data-b="${b}" aria-labelledby="${id}-t">
<h2 id="${id}-t">${titulo}</h2>
<p>Haz las operaciones en un papel, escribe el resultado y pulsa «Corregir».</p>
<form>
<ol class="ops-lista">
${ops.map(([x, y], i) => `<li><div class="op" aria-hidden="true"><span>${x}</span><span class="op-b"><span class="op-signo">×</span>${y}</span></div><label class="solo-lector" for="${id}-${i}">${x} por ${y}</label><input id="${id}-${i}" type="text" inputmode="numeric" autocomplete="off" maxlength="5" data-r="${x * y}"><span class="marca" aria-live="polite"></span></li>`).join('\n')}
</ol>
<p class="practica-botones"><button type="submit" class="boton boton-tinta">Corregir</button> <button type="button" class="boton" data-otras>Otras 6</button></p>
<p class="practica-resultado" aria-live="polite"></p>
</form>
</section>`;
};

const practicaDiv = (titulo) => {
  const az = azarFijo(4157), ops = [], id = 'dv';
  while (ops.length < 6) {
    const d = entre(az, 2, 9), D = entre(az, 20, 999);
    if (D < d * 10) continue;
    ops.push([D, d]);
  }
  return `
<section class="practica practica-md" data-tipo="div" aria-labelledby="${id}-t">
<h2 id="${id}-t">${titulo}</h2>
<p>Haz la división en un papel y escribe el cociente (debajo del divisor) y el resto (debajo del dividendo). Después pulsa «Corregir».</p>
<form>
<ol class="ops-lista divs-lista">
${ops.map(([D, d], i) => `<li><div class="casita"><span class="dvd" aria-hidden="true">${D}</span><span class="dvs" aria-hidden="true">${d}</span><label class="solo-lector" for="${id}-${i}r">Resto de ${D} entre ${d}</label><input class="res" id="${id}-${i}r" type="text" inputmode="numeric" autocomplete="off" maxlength="2" data-r="${D % d}"><label class="solo-lector" for="${id}-${i}c">Cociente de ${D} entre ${d}</label><input class="coc" id="${id}-${i}c" type="text" inputmode="numeric" autocomplete="off" maxlength="3" data-r="${Math.floor(D / d)}"></div><span class="marca" aria-live="polite"></span></li>`).join('\n')}
</ol>
<p class="practica-botones"><button type="submit" class="boton boton-tinta">Corregir</button> <button type="button" class="boton" data-otras>Otras 6</button></p>
<p class="practica-resultado" aria-live="polite"></p>
</form>
</section>`;
};

module.exports = [
  {
    cat: 'multiplicaciones-y-divisiones', slug: '', corto: 'Multiplicar y dividir', nav: 'Multiplicar y dividir',
    resumen: 'Por una y dos cifras, y divisiones en casita',
    title: 'Multiplicaciones y divisiones para imprimir (PDF)',
    desc: 'Fichas de multiplicaciones por una y dos cifras y divisiones de una cifra para imprimir, con solución y ejercicios para practicar en pantalla. PDF gratis.',
    h1: 'Multiplicaciones y divisiones para imprimir',
    entrada: 'Fichas de multiplicaciones y divisiones en vertical para tercero, cuarto y quinto de primaria, con su solución. Cada página explica el método con un ejemplo paso a paso y trae un ejercicio para practicar en pantalla.',
    antes: practicaMult(2, 1, 'Practica multiplicaciones aquí'),
    hojas: [{ tipo: 'multiplicaciones', a: 2, b: 1, titulo: 'Multiplicaciones por una cifra' }],
    copias: 4,
    cuerpo: `
<h2>En qué orden se aprenden</h2>
<ol>
<li><a href="/tablas-de-multiplicar/">Tablas de multiplicar</a>: sin ellas no se puede avanzar.</li>
<li><a href="/multiplicaciones-y-divisiones/multiplicaciones-por-una-cifra/">Multiplicaciones por una cifra</a>, primero de dos cifras arriba (34 × 6) y luego de tres (247 × 8).</li>
<li><a href="/multiplicaciones-y-divisiones/divisiones-de-una-cifra/">Divisiones de una cifra</a>, que son la operación inversa y se apoyan en las mismas tablas.</li>
<li><a href="/multiplicaciones-y-divisiones/multiplicaciones-de-dos-cifras/">Multiplicaciones de dos cifras</a>, que combinan multiplicar, colocar bien en columnas y sumar.</li>
</ol>
<p>Como orientación, las multiplicaciones por una cifra y las primeras divisiones se trabajan en tercero de primaria; las multiplicaciones de dos cifras y las divisiones con dividendo de tres cifras, en cuarto.</p>
<h2>Cómo usar las fichas</h2>
<p>Cada ficha trae 20 multiplicaciones por una cifra o 12 operaciones más largas, en vertical y con espacio para las cuentas. La solución sale en hoja aparte; en las multiplicaciones de dos cifras incluye también los dos productos parciales, para que se vea dónde está el error si lo hay.</p>
<p>Si el niño falla mucho, casi nunca es un problema de método: suele ser una tabla que no tiene bien aprendida. Apunta las multiplicaciones que falla y repasa esa tabla concreta.</p>`,
    faq: [
      ['¿En qué curso se aprende a dividir?', 'En España las divisiones de una cifra se introducen normalmente en tercero de primaria y se consolidan en cuarto, cuando se pasa a dividendos de tres y cuatro cifras. Las divisiones de dos cifras llegan en quinto.'],
      ['¿Por qué se llama «en casita» a la división?', 'Por la forma de la caja que encierra al divisor: una línea vertical y otra horizontal debajo del divisor, como un tejado. Es la disposición que se usa en España y en buena parte de Latinoamérica.']
    ]
  },
  {
    cat: 'multiplicaciones-y-divisiones', slug: 'multiplicaciones-por-una-cifra', corto: 'Multiplicaciones por una cifra',
    title: 'Multiplicaciones por una cifra: fichas y ejercicios',
    desc: 'Multiplicaciones por una cifra para imprimir: 20 por hoja, de dos y tres cifras arriba, con solución. Y un ejercicio para practicar en pantalla.',
    h1: 'Multiplicaciones por una cifra',
    entrada: 'Multiplicaciones en vertical en las que el número de abajo tiene una sola cifra: primero con dos cifras arriba (34 × 6) y después con tres (247 × 8). Veinte por hoja, con solución, y un ejercicio para practicar aquí mismo.',
    antes: practicaMult(2, 1, 'Practica multiplicaciones por una cifra'),
    hojas: [
      { tipo: 'multiplicaciones', a: 2, b: 1, titulo: 'Multiplicaciones por una cifra' },
      { tipo: 'multiplicaciones', a: 3, b: 1, titulo: 'Multiplicaciones de tres cifras por una' }
    ],
    copias: 2,
    cuerpo: `
<h2>Cómo se hacen</h2>
<p>Se multiplica la cifra de abajo por cada cifra de arriba, empezando por la derecha. En 47 × 6: primero 7 × 6 = 42, se escribe el 2 y «me llevo 4»; después 4 × 6 = 24, más las 4 que llevaba, 28. Resultado: 282.</p>
<p>El error más común es olvidar sumar lo que se lleva, o sumarlo antes de multiplicar (4 + 4 = 8, × 6 = 48, que está mal). El orden es siempre: primero multiplicar, después sumar la llevada.</p>
<h2>Qué tablas hacen falta</h2>
<p>Todas, porque el número de abajo va del 2 al 9. Si el niño todavía duda con alguna, la ficha de práctica de cada tabla (por ejemplo, la <a href="/tablas-de-multiplicar/tabla-del-7/">tabla del 7</a> o la <a href="/tablas-de-multiplicar/tabla-del-8/">del 8</a>) ayuda a afianzarla antes de seguir.</p>
<p>Cuando estas salgan bien, el siguiente paso son las <a href="/multiplicaciones-y-divisiones/multiplicaciones-de-dos-cifras/">multiplicaciones de dos cifras</a>.</p>`
  },
  {
    cat: 'multiplicaciones-y-divisiones', slug: 'multiplicaciones-de-dos-cifras', corto: 'Multiplicaciones de dos cifras',
    title: 'Multiplicaciones de dos cifras: cómo se hacen y fichas',
    desc: 'Multiplicaciones de dos cifras explicadas paso a paso y fichas para imprimir con solución, incluidos los productos parciales. Y ejercicio en pantalla.',
    h1: 'Multiplicaciones de dos cifras',
    entrada: 'Multiplicaciones en las que el número de abajo tiene dos cifras, como 23 × 14. Aquí tienes el método explicado paso a paso, un ejercicio para practicar en pantalla y fichas para imprimir con la solución completa, productos parciales incluidos.',
    antes: pasoMult() + practicaMult(2, 2, 'Practica multiplicaciones de dos cifras'),
    hojas: [
      { tipo: 'multiplicaciones', a: 2, b: 2, titulo: 'Multiplicaciones de dos cifras' },
      { tipo: 'multiplicaciones', a: 3, b: 2, titulo: 'Multiplicaciones de tres cifras por dos' }
    ],
    copias: 2,
    cuerpo: `
<h2>El hueco de la derecha</h2>
<p>Lo que más cuesta de estas multiplicaciones es entender por qué el segundo resultado se escribe un lugar a la izquierda. La razón es que la cifra de las decenas no vale 1, vale 10: en 23 × 14 no multiplicamos 23 × 1, sino 23 × 10 = 230. Ese hueco a la derecha es el cero de 230, que no se escribe pero ocupa su sitio.</p>
<p>Por eso algunos maestros enseñan a poner un cero, un punto o una rayita en ese hueco: así no se olvida desplazar. Cualquiera de las tres formas es correcta; lo importante es usar la misma que en clase.</p>
<h2>Errores frecuentes</h2>
<ul>
<li><strong>No desplazar el segundo producto.</strong> El resultado sale mucho más pequeño de lo esperado.</li>
<li><strong>Mezclar las llevadas.</strong> Las que te llevas al multiplicar por las unidades no sirven para la fila de las decenas: hay que borrarlas o tacharlas antes de empezar la segunda fila.</li>
<li><strong>Equivocarse al sumar.</strong> La suma final también puede tener llevadas; conviene hacerla con la misma calma.</li>
</ul>
<p>Para comprobar si un resultado tiene sentido, redondea: 23 × 14 es más o menos 20 × 15 = 300, así que 322 es razonable y 115 no.</p>
<p>Las soluciones de las fichas muestran los dos productos parciales y el total, para que el niño vea en qué paso se ha equivocado.</p>`
  },
  {
    cat: 'multiplicaciones-y-divisiones', slug: 'divisiones-de-una-cifra', corto: 'Divisiones de una cifra',
    title: 'Divisiones de una cifra: cómo se hacen y fichas',
    desc: 'Divisiones de una cifra explicadas paso a paso, en casita como se hacen en España, y fichas para imprimir con cociente y resto. Con ejercicio en pantalla.',
    h1: 'Divisiones de una cifra',
    entrada: 'Divisiones en las que el divisor tiene una sola cifra, colocadas «en casita» como se hacen en los colegios españoles. Aquí tienes un ejemplo resuelto paso a paso, un ejercicio con corrección al momento y fichas para imprimir con dividendos de dos y tres cifras.',
    antes: pasoDiv() + practicaDiv('Practica divisiones aquí'),
    hojas: [
      { tipo: 'divisiones', dividendo: 2, titulo: 'Divisiones con dividendo de dos cifras' },
      { tipo: 'divisiones', dividendo: 3, titulo: 'Divisiones con dividendo de tres cifras' }
    ],
    copias: 2,
    cuerpo: `
<h2>Las partes de una división</h2>
<p>El <strong>dividendo</strong> es el número que se reparte (157); el <strong>divisor</strong>, entre cuántos se reparte (4); el <strong>cociente</strong>, cuánto le toca a cada uno (39), y el <strong>resto</strong>, lo que sobra (1). El resto siempre tiene que ser menor que el divisor: si sobran 5 al dividir entre 4, es que el cociente se ha quedado corto.</p>
<p>La prueba de la división sirve para comprobar cualquier resultado: divisor × cociente + resto = dividendo. Si no da, hay un error.</p>
<h2>Restar escribiendo o de cabeza</h2>
<p>En el ejemplo de arriba, la resta de cada paso (15 − 12, 37 − 36) se hace de cabeza y solo se escribe lo que sobra. Es la forma habitual en España a partir de cuarto. En tercero, muchos colegios escriben la resta completa debajo del dividendo hasta que el niño se suelta. Las fichas dejan espacio para las dos formas.</p>
<h2>Qué fichas elegir</h2>
<p>La primera hoja tiene dividendos de dos cifras (como 78 : 3), para empezar. La segunda, de tres cifras (como 157 : 4), en las que hay que bajar cifras más veces y a veces el cociente lleva un cero en medio (como 412 : 4 = 103), que es donde más se equivocan. Hay divisiones exactas y con resto, mezcladas.</p>
<p>Antes de dividir con soltura hacen falta las <a href="/tablas-de-multiplicar/">tablas de multiplicar</a>: dividir 37 entre 4 es preguntarse qué número de la tabla del 4 se acerca más a 37 sin pasarse.</p>`,
    faq: [
      ['¿Qué pasa si el primer número es menor que el divisor?', 'Se toman dos cifras del dividendo en lugar de una. En 157 : 4, como 1 es menor que 4, se empieza dividiendo 15. En el cociente no se escribe nada por ese primer 1.'],
      ['¿Cuándo sale un cero en el cociente?', 'Cuando, al bajar una cifra, el número que queda es menor que el divisor. Por ejemplo, en 412 : 4, después de 4 : 4 = 1 se baja el 1, y 1 : 4 no cabe: se escribe un 0 en el cociente y se baja la siguiente cifra.']
    ]
  }
];
