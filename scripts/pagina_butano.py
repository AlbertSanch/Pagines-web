"""Genera la página «Precio de la bombona de butano hoy» y pone el precio en las calculadoras.

Lee ahorrometro/datos/butano.json, que se actualiza a mano cuando el BOE publica la revisión
(el precio es regulado: cambia el tercer martes de los meses impares). Con él:
  - crea ahorrometro/precio-bombona-butano.html (precio, próxima revisión, cuánto dura, historial);
  - pone el precio actual como valor por defecto en las calculadoras que usan el butano;
  - añade la página al sitemap.xml entre <!-- BUTANO:INICIO --> y <!-- BUTANO:FIN -->.
La cabecera y el pie se copian de precio-gasolina-hoy.html.

Uso: python scripts/pagina_butano.py
"""

import json
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "ahorrometro"
DOMINIO = "https://ahorrometro.es"
RUTA = "precio-bombona-butano"
AMAZON_TAG = "albert671-21"
KWH_POR_KG = 12.87  # poder calorífico del butano, el mismo que usa la calculadora de duración
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
# Calculadoras con el precio de la bombona: (fichero, id de la casilla)
CALCULADORAS = [("calculadoras/duracion-bombona-butano.html", "precio"),
                ("calculadoras/estufa-butano-o-electrica.html", "pButano"),
                ("calculadoras/calefaccion-mas-barata.html", "pButano")]


def num(x, dec):
    entero, _, frac = f"{x:,.{dec}f}".partition(".")
    return entero.replace(",", ".") + ("," + frac if dec else "")


def eur(x):
    return num(x, 2) + " €"


def fecha(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def tercer_martes(anio, mes):
    d = date(anio, mes, 1)
    return d + timedelta(days=(1 - d.weekday()) % 7 + 14)


def proxima_revision(desde):
    """Tercer martes del siguiente mes impar después de la última revisión."""
    anio, mes = desde.year, desde.month + 1
    while True:
        if mes > 12:
            anio, mes = anio + 1, 1
        if mes % 2 == 1:
            return tercer_martes(anio, mes)
        mes += 1


def plantilla_base():
    base = (WEB / "precio-gasolina-hoy.html").read_text(encoding="utf-8")
    head_assets = base[base.index('  <link rel="stylesheet"'):base.index("</head>")]
    header = base[base.index("<body>"):base.index('<main class="container">')]
    i = base.index('<footer class="site-footer">')
    j = base.index("\n", base.index("assets/main.js", i)) + 1
    return head_assets, header, base[i:j]


def afiliados():
    items = [("🔥", "Estufa de butano", "estufa de butano", "Las catalíticas e infrarrojas son las más comunes; mira que tenga sensor de oxígeno."),
             ("🔧", "Regulador y manguera", "regulador butano manguera", "La manguera caduca: revisa la fecha impresa y cámbiala cuando toque."),
             ("🚨", "Detector de monóxido de carbono", "detector monoxido de carbono", "Imprescindible si usas una estufa de gas en casa.")]
    tarjetas = "\n".join(
        f'          <a class="aff-item" href="https://www.amazon.es/s?k={busqueda.replace(" ", "%20")}&amp;tag={AMAZON_TAG}" rel="sponsored nofollow noopener" target="_blank">'
        f'<span class="aff-icon">{icono}</span><b>{escape(t)}</b><span class="aff-desc">{escape(d)}</span><span class="aff-cta">Ver precio en Amazon →</span></a>'
        for icono, t, busqueda, d in items)
    return f"""      <section class="affiliate">
        <h2>Para usar el butano con seguridad</h2>
        <div class="aff-grid">
{tarjetas}
        </div>
        <p class="aff-note">Enlaces de afiliado: si compras a través de ellos, recibimos una pequeña comisión sin coste extra para ti.</p>
      </section>"""


def precio_luz():
    try:
        return float(json.loads((WEB / "datos" / "luz.json").read_text(encoding="utf-8"))["conImpuestos"]["media"])
    except Exception:
        return 0.16


def pagina(datos, base, hoy, luz):
    head_assets, header, footer = base
    e = escape
    hist = datos["historial"]
    act = hist[0]
    kg = datos["kg"]
    precio = act["precio"]
    desde = date.fromisoformat(act["desde"])
    prox = proxima_revision(desde)
    pendiente = hoy >= prox  # ya tocaba revisión y aún no está en los datos
    url = f"{DOMINIO}/{RUTA}"
    mes_txt = f"{MESES[desde.month - 1]} de {desde.year}"
    titulo = f"Precio de la bombona de butano hoy ({MESES[hoy.month - 1]} {hoy.year})"
    desc = (f"La bombona de butano de {num(kg, 1)} kg cuesta {eur(precio)} desde el {fecha(desde)}. "
            f"Próxima revisión, historial de precios y cuánto te dura una bombona.")

    if len(hist) > 1:
        ant = hist[1]["precio"]
        cambio = (precio - ant) / ant * 100
        variacion = (f"{'Sube' if cambio > 0 else 'Baja'} un {num(abs(cambio), 1)} % respecto a los {eur(ant)} anteriores"
                     if abs(cambio) >= 0.05 else f"El mismo precio que en la revisión anterior")
    else:
        variacion = ""
    estado_prox = (f"Tocaba revisión el {fecha(prox)}: actualizaremos el precio en cuanto se publique en el BOE."
                   if pendiente else f"El precio cambiará, como pronto, el {fecha(prox)}.")

    # Cuánto dura y cuánto cuesta por hora una estufa según la potencia
    filas_uso = ""
    for nombre, kw in (("Potencia baja (1 placa)", 1.4), ("Potencia media (2 placas)", 2.8), ("Potencia máxima (3 placas)", 4.2)):
        horas = kg * KWH_POR_KG / kw
        filas_uso += (f"<tr><td>{nombre}</td><td class=\"num\">{num(kw * 1000 / KWH_POR_KG, 0)} g</td><td class=\"num\">{num(horas, 0)} h</td>"
                      f"<td class=\"num\">{num(horas / 4, 0)} días</td><td class=\"num\">{eur(precio / horas)}</td></tr>")
    horas_media = kg * KWH_POR_KG / 2.8
    coste_butano, coste_radiador = precio / horas_media, 2.8 * luz
    comparacion = ("Ahora mismo el butano sale más barato que el radiador eléctrico, pero la bomba de calor gana a los dos."
                   if coste_butano < coste_radiador else
                   "Ahora mismo el radiador eléctrico sale más barato que el butano, y la bomba de calor gana a los dos.")

    filas_hist = ""
    for i, h in enumerate(hist):
        d = date.fromisoformat(h["desde"])
        if i + 1 < len(hist):
            c = (h["precio"] - hist[i + 1]["precio"]) / hist[i + 1]["precio"] * 100
            var = f'{"+" if c > 0 else ""}{num(c, 1)} %'
        else:
            var = "—"
        filas_hist += (f"<tr><td>{fecha(d)}</td><td class=\"num\"><strong>{eur(h['precio'])}</strong></td>"
                       f"<td class=\"num\">{num(h['precio'] / kg, 2)} €/kg</td><td class=\"num\">{var}</td></tr>")

    faq = [
        (f"¿Cuánto cuesta la bombona de butano hoy?",
         f"La bombona de butano de {num(kg, 1)} kg cuesta como máximo {eur(precio)} en la Península y Baleares desde el {fecha(desde)}, "
         f"con impuestos incluidos. Es el precio máximo regulado que fija el Gobierno, así que ningún distribuidor puede cobrar más por ella."),
        ("¿Cuándo cambia el precio del butano?",
         f"Cada dos meses, el tercer martes de enero, marzo, mayo, julio, septiembre y noviembre. La próxima revisión es el {fecha(prox)}. "
         "El nuevo precio se publica en el BOE el día anterior."),
        ("¿Cuánto puede subir o bajar el butano en cada revisión?",
         "Como máximo un 5 % arriba o abajo. Si según la fórmula tocaría subir o bajar más, la diferencia se aplica en las revisiones siguientes."),
        ("¿Cuánto dura una bombona de butano?",
         f"Con una estufa a potencia media (unos 2,8 kW), una bombona de {num(kg, 1)} kg dura unas {num(horas_media, 0)} horas: "
         f"unos {num(horas_media / 4, 0)} días si la enciendes 4 horas al día. A potencia baja dura el doble."),
        ("¿Por qué el butano es distinto en Canarias?",
         "Porque en Canarias no se aplica el IVA sino el IGIC, y el precio se fija con un sistema propio. El precio de esta página es el de la Península y Baleares."),
        ("¿Qué bombonas tienen el precio regulado?",
         "Las de gas licuado del petróleo de entre 8 y 20 kg, como la bombona naranja de 12,5 kg. Las bombonas más pequeñas, las de propano y las de "
         "mezcla para uso industrial o de automoción tienen precio libre."),
    ]
    ld = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": titulo, "url": url, "inLanguage": "es-ES",
         "dateModified": hoy.isoformat(), "author": {"@type": "Person", "name": "Albert Sanchez Guiu"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMINIO}/"},
            {"@type": "ListItem", "position": 2, "name": "Precio de la bombona de butano", "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]},
    ]
    faq_html = "\n".join(f"        <details>\n          <summary>{e(q)}</summary>\n          <p>{e(r)}</p>\n        </details>" for q, r in faq)
    boe = date.fromisoformat(act["boe"]) if act.get("boe") else None
    fuente = (f'Resolución de la Dirección General de Política Energética y Minas publicada en el '
              f'<a href="https://www.boe.es/boe/dias/{boe.year}/{boe.month:02d}/{boe.day:02d}/" rel="noopener">BOE del {fecha(boe)}</a>'
              if boe else "Boletín Oficial del Estado (BOE)")
    sin_imp = (f" El precio máximo antes de impuestos es de {num(act['cent_kg_sin_impuestos'], 4)} céntimos por kilo."
               if act.get("cent_kg_sin_impuestos") else "")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#1f7a55">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ahorrómetro">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{e(titulo)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://ahorrometro.es/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {json.dumps(ld, ensure_ascii=False)}
  </script>
{head_assets}  <style>
    .bt-precio {{ background: var(--primary); color: #fff; border-radius: var(--radius); padding: 26px 28px; margin: 20px 0; }}
    .bt-precio p {{ margin: 0; }}
    .bt-precio .bt-cifra {{ font-size: clamp(2.6rem, 8vw, 3.6rem); font-weight: 800; line-height: 1.1; letter-spacing: -.02em; font-variant-numeric: tabular-nums; margin: 6px 0; }}
    .bt-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 16px; }}
    .bt-stat {{ background: rgba(255,255,255,.13); border-radius: 10px; padding: 10px 14px; }}
    .bt-stat b {{ display: block; font-size: 1.05rem; font-variant-numeric: tabular-nums; }}
    .bt-stat span {{ font-size: .85rem; opacity: .85; }}
  </style>
</head>
<!-- Página generada automáticamente por scripts/pagina_butano.py a partir de datos/butano.json: no la edites a mano. -->
{header}<main class="container">
  <nav class="breadcrumbs"><a href="./">Inicio</a> › Precio de la bombona de butano</nav>
  <div class="layout">
    <article>
      <h1>Precio de la bombona de butano hoy</h1>
      <p class="lead">La bombona de butano de {num(kg, 1)} kg cuesta <strong>{eur(precio)}</strong> desde el {fecha(desde)}. Es el precio máximo oficial, con impuestos, en la Península y Baleares.</p>

      <div class="bt-precio">
        <p>Bombona de butano de {num(kg, 1)} kg · {e(mes_txt)}</p>
        <p class="bt-cifra">{eur(precio)}</p>
        <p>{e(variacion + ("." if variacion else ""))} {e(estado_prox)}</p>
        <div class="bt-stats">
          <div class="bt-stat"><b>{num(precio / kg, 2)} €/kg</b><span>precio por kilo</span></div>
          <div class="bt-stat"><b>{fecha(desde)}</b><span>en vigor desde</span></div>
          <div class="bt-stat"><b>{fecha(prox)}</b><span>próxima revisión</span></div>
        </div>
      </div>
      <p class="updated">Fuente: {fuente}.{sin_imp}</p>


      <div class="content">
        <h2>Cuánto dura una bombona y cuánto cuesta por hora</h2>
        <p>Una estufa de butano gasta más o menos gas según la potencia a la que la pongas. Con el precio actual:</p>
        <div class="table-wrap"><table class="data"><thead><tr><th>Estufa a…</th><th class="num">Gas por hora</th><th class="num">Dura</th><th class="num">4 h al día</th><th class="num">Coste por hora</th></tr></thead><tbody>{filas_uso}</tbody></table></div>
        <p>Calcula la tuya con la <a href="calculadoras/duracion-bombona-butano">calculadora de cuánto dura una bombona</a>, o compara si te sale más barato que un radiador eléctrico o una bomba de calor con la <a href="calculadoras/estufa-butano-o-electrica">calculadora de estufa de butano o eléctrica</a>.</p>

        <h2>Historial del precio del butano</h2>
        <div class="table-wrap"><table class="data"><thead><tr><th>Desde</th><th class="num">Bombona {num(kg, 1)} kg</th><th class="num">Por kilo</th><th class="num">Cambio</th></tr></thead><tbody>{filas_hist}</tbody></table></div>
        <p>Precios máximos con impuestos en la Península y Baleares.</p>

        <h2>Cómo se fija el precio del butano</h2>
        <p>El precio de la bombona de butano no es libre: lo fija el Ministerio para la Transición Ecológica cada dos meses, el tercer martes de enero, marzo, mayo, julio, septiembre y noviembre, y se publica en el BOE el día anterior. Es un precio máximo con impuestos incluidos: ningún distribuidor puede cobrar más por la bombona.</p>
        <p>La fórmula tiene en cuenta el precio internacional del butano y del propano y el cambio entre el euro y el dólar en los meses anteriores. Para evitar saltos bruscos, cada revisión puede subir o bajar el precio como máximo un 5 %; lo que quede pendiente se aplica en las revisiones siguientes.</p>
        <p class="note">En Canarias el precio es distinto, porque no se aplica el IVA sino el IGIC. Ceuta y Melilla también tienen una fiscalidad propia.</p>

        <h2>¿Compensa calentarse con butano?</h2>
        <p>A potencia media (2,8 kW), una estufa de butano cuesta unos <strong>{eur(precio / horas_media)} por hora</strong>. Con el precio medio actual de la luz ({num(luz, 3)} €/kWh), dar el mismo calor con un radiador eléctrico cuesta unos <strong>{eur(2.8 * luz)} por hora</strong>, y con una bomba de calor (el aire acondicionado en modo calor), unos <strong>{eur(2.8 / 3.5 * luz)}</strong>. {comparacion} Compáralo con tus datos en la calculadora <a href="calculadoras/calefaccion-mas-barata">¿qué calefacción es más barata?</a></p>

        <h2>Preguntas frecuentes</h2>
{faq_html}
      </div>

{afiliados()}
    </article>

    <aside class="sidebar">
      <div class="side-box">
        <h3>Calefacción</h3>
        <ul>
          <li><a href="calculadoras/duracion-bombona-butano">🔥 ¿Cuánto dura una bombona?</a></li>
          <li><a href="calculadoras/estufa-butano-o-electrica">⚖️ Estufa de butano o eléctrica</a></li>
          <li><a href="calculadoras/calefaccion-mas-barata">🏠 Calefacción más barata</a></li>
          <li><a href="calculadoras/manta-electrica-o-calefaccion">🛏️ Manta eléctrica o calefacción</a></li>
          <li><a href="precio-luz-hoy">💡 Precio de la luz hoy</a></li>
        </ul>
      </div>
    </aside>
  </div>
</main>

{footer}</body>
</html>
"""


def poner_precio_calculadoras(precio):
    for fichero, campo in CALCULADORAS:
        ruta = WEB / fichero
        texto = ruta.read_text(encoding="utf-8")
        nuevo, n = re.subn(rf'(<input id="{campo}"[^>]*?value=")[0-9.]+(")', rf"\g<1>{precio:.2f}\g<2>", texto)
        if n != 1:
            raise SystemExit(f"No encuentro la casilla {campo} en {fichero}")
        if nuevo != texto:
            ruta.write_text(nuevo, encoding="utf-8")


def sitemap(lastmod):
    ruta = WEB / "sitemap.xml"
    texto = ruta.read_text(encoding="utf-8")
    bloque = f"\n  <url><loc>{DOMINIO}/{RUTA}</loc><lastmod>{lastmod}</lastmod><priority>1.0</priority></url>\n  "
    if "<!-- BUTANO:INICIO -->" not in texto:
        texto = texto.replace("</urlset>", "  <!-- BUTANO:INICIO --><!-- BUTANO:FIN -->\n</urlset>")
    nuevo = re.sub(r"(<!-- BUTANO:INICIO -->).*?(<!-- BUTANO:FIN -->)", lambda m: m[1] + bloque + m[2], texto, flags=re.S)
    if nuevo != ruta.read_text(encoding="utf-8"):
        ruta.write_text(nuevo, encoding="utf-8")


def main():
    datos = json.loads((WEB / "datos" / "butano.json").read_text(encoding="utf-8"))
    datos["historial"].sort(key=lambda h: h["desde"], reverse=True)
    hoy = date.today()
    html = pagina(datos, plantilla_base(), hoy, precio_luz())
    ruta = WEB / f"{RUTA}.html"
    # dateModified cambia cada día: solo reescribimos si cambia algo más, para no hacer un commit diario
    viejo = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
    quitar_fecha = lambda t: re.sub(r'"dateModified": "[0-9-]+"', "", t)  # noqa: E731
    if quitar_fecha(viejo) != quitar_fecha(html):
        ruta.write_text(html, encoding="utf-8")
    act = datos["historial"][0]
    poner_precio_calculadoras(act["precio"])
    sitemap(act["desde"])
    print(f"Butano: {act['precio']} € desde {act['desde']}; próxima revisión {proxima_revision(date.fromisoformat(act['desde']))}")


if __name__ == "__main__":
    main()
