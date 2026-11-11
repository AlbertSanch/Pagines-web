// Configuración general. Todo lo que hay que rellenar antes de publicar está aquí.
module.exports = {
  nombre: 'imprimibles.es',
  url: 'https://imprimibles.es',
  lema: 'Pasatiempos y fichas para imprimir',
  compilado: new Date().toISOString().slice(0, 10),
  anio: new Date().getFullYear(),

  // --- Monetización (vacío = desactivado; no se reserva hueco ni se carga nada) ---
  adsenseId: process.env.ADSENSE_ID || 'ca-pub-8810566450749484',        // p. ej. 'ca-pub-1234567890123456'
  adsSlots: { contenido: '', lateral: '', final: '' }, // id de cada bloque creado en AdSense
  amazonTag: process.env.AMAZON_TAG || '',          // p. ej. 'imprimibles-21'

  // --- Analítica sin cookies (opcional): token de Cloudflare Web Analytics ---
  cfBeacon: '',

  // --- Datos legales (obligatorios para el aviso legal) ---
  legal: {
    titular: 'Albert Sanchez Guiu',
    nif: '48167483D',
    domicilio: 'La Roca del Vallès (Barcelona), España',
    email: 'contacto.ahorrometro@gmail.com'
  }
};
