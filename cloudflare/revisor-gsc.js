// Worker de Cloudflare: lectura de Search Console para las revisiones semanales.
// Guarda la clave de una cuenta de servicio de Google (solo lectura) y reenvía las consultas
// a la API de Search Console. Solo responde a quien manda la contraseña CLAVE, y solo
// habla con las dos direcciones de la API de Search Console.
//
// Cómo publicarlo: Cloudflare → Workers & Pages → Create → Start with Hello World →
// nombre «revisor-gsc» → Deploy → Edit code → pega este archivo → Deploy.
// Después, en Settings → Variables and Secrets, añade dos secretos (tipo «Secret»):
//   GSC_KEY: el contenido completo del archivo JSON de la cuenta de servicio.
//   CLAVE:   una contraseña larga inventada (la misma que se guarda en Claude).
//
// Uso: GET/POST https://revisor-gsc.<cuenta>.workers.dev/<ruta de la API>
//   /webmasters/v3/sites                                         → www.googleapis.com
//   /webmasters/v3/sites/<web>/searchAnalytics/query (POST)      → www.googleapis.com
//   /v1/urlInspection/index:inspect (POST)                       → searchconsole.googleapis.com

const PERMISO = "https://www.googleapis.com/auth/webmasters.readonly";
let ficha = { token: null, caduca: 0 };

function b64url(datos) {
  const bytes = typeof datos === "string" ? new TextEncoder().encode(datos) : new Uint8Array(datos);
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function tokenGoogle(env) {
  if (ficha.token && Date.now() < ficha.caduca - 60000) return ficha.token;
  const cuenta = JSON.parse(env.GSC_KEY);
  const ahora = Math.floor(Date.now() / 1000);
  const cabecera = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const cuerpo = b64url(JSON.stringify({
    iss: cuenta.client_email, scope: PERMISO, aud: "https://oauth2.googleapis.com/token", iat: ahora, exp: ahora + 3600,
  }));
  const pem = cuenta.private_key.replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const clave = await crypto.subtle.importKey("pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const firma = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", clave, new TextEncoder().encode(`${cabecera}.${cuerpo}`));
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${cabecera}.${cuerpo}.${b64url(firma)}`,
  });
  const datos = await r.json();
  if (!datos.access_token) throw new Error(`Google no ha dado el token: ${JSON.stringify(datos)}`);
  ficha = { token: datos.access_token, caduca: Date.now() + datos.expires_in * 1000 };
  return ficha.token;
}

export default {
  async fetch(request, env) {
    const auth = request.headers.get("Authorization") || "";
    if (!env.CLAVE || auth !== `Bearer ${env.CLAVE}`) return new Response("No autorizado", { status: 401 });
    if (!["GET", "POST"].includes(request.method)) return new Response("Método no permitido", { status: 405 });
    const url = new URL(request.url);
    let destino;
    if (url.pathname.startsWith("/webmasters/v3/")) destino = "https://www.googleapis.com";
    else if (url.pathname.startsWith("/v1/")) destino = "https://searchconsole.googleapis.com";
    else return new Response("Ruta no permitida", { status: 404 });
    try {
      const token = await tokenGoogle(env);
      const r = await fetch(destino + url.pathname + url.search, {
        method: request.method,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: request.method === "POST" ? await request.text() : undefined,
      });
      return new Response(r.body, { status: r.status, headers: { "Content-Type": "application/json; charset=utf-8" } });
    } catch (e) {
      return new Response(JSON.stringify({ error: String(e) }), { status: 502, headers: { "Content-Type": "application/json" } });
    }
  },
};
