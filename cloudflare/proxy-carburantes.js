// Worker de Cloudflare: intermediario para descargar los precios del Ministerio.
// El servidor del Ministerio corta las conexiones desde GitHub Actions, así que el
// proceso automático pide los datos a este Worker y el Worker se los pide al Ministerio.
// Solo reenvía esa dirección concreta: no sirve como proxy para otras webs.
//
// Cómo publicarlo: Cloudflare → Workers & Pages → Create → Start with Hello World →
// nombre «proxy-carburantes» → Deploy → Edit code → pega este archivo → Deploy.

const MINISTERIO =
  "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/";

export default {
  async fetch(request) {
    if (request.method !== "GET") {
      return new Response("Método no permitido", { status: 405 });
    }
    let respuesta;
    try {
      respuesta = await fetch(MINISTERIO, {
        headers: { Accept: "application/json", "User-Agent": "ahorrometro.es (proxy de precios)" },
        cf: { cacheTtl: 900, cacheEverything: true }, // como mucho una descarga real cada 15 min
      });
    } catch (e) {
      return new Response("Error al conectar con el Ministerio: " + e.message, { status: 502 });
    }
    return new Response(respuesta.body, {
      status: respuesta.status,
      headers: {
        "Content-Type": respuesta.headers.get("Content-Type") || "application/json",
        "Cache-Control": "no-store",
      },
    });
  },
};
