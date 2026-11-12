// CSS con las tipografías incrustadas (base64). Hace falta porque Chromium no carga
// archivos locales en una página creada con setContent: sin esto, los PDF y las
// imágenes saldrían con tipografías de sustitución.
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, '../src/fonts');
const datos = (f) => 'data:font/woff2;base64,' + fs.readFileSync(path.join(dir, f)).toString('base64');
module.exports = `
@font-face{font-family:Besley;src:url(${datos('besley-800.woff2')}) format("woff2");font-weight:800}
@font-face{font-family:"Andika";src:url(${datos('andika-400.woff2')}) format("woff2");font-weight:400}
@font-face{font-family:"Andika";src:url(${datos('andika-700.woff2')}) format("woff2");font-weight:700}
@font-face{font-family:"Playwrite ES";src:url(${datos('playwrite-es-300.woff2')}) format("woff2");font-weight:300}`;
