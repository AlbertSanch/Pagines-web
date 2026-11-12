// Datos estructurados (Schema.org) de cada página, calculados en un solo sitio.
const abs = (site, u) => site.url + u;

module.exports = {
  migas: (d) => {
    if (d.p) {
      const hub = d.secciones.find((s) => s.cat === d.p.cat);
      const m = [{ nombre: 'Inicio', url: '/' }, { nombre: hub.nombre, url: hub.url }];
      if (!d.p.esHub) m.push({ nombre: d.p.corto, url: d.p.url });
      return m;
    }
    if (d.page.url === '/' || !d.title) return null;
    return [{ nombre: 'Inicio', url: '/' }, { nombre: d.titulo || d.title, url: d.page.url }];
  },
  jsonld: (d) => {
    const site = d.site, out = [];
    if (!d.page || !d.page.url) return out;
    if (d.page.url === '/') {
      out.push({
        '@context': 'https://schema.org', '@type': 'WebSite', name: site.nombre, url: site.url + '/',
        inLanguage: 'es-ES', description: d.description,
        publisher: { '@type': 'Organization', name: site.nombre, url: site.url + '/', logo: abs(site, '/icono-512.png') }
      });
    }
    if (d.migas) {
      out.push({
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        itemListElement: d.migas.map((m, i) => ({ '@type': 'ListItem', position: i + 1, name: m.nombre, item: abs(site, m.url) }))
      });
    }
    if (d.p) {
      const p = d.p;
      const obra = {
        '@context': 'https://schema.org', '@type': p.esHub ? ['CollectionPage', 'LearningResource'] : 'LearningResource',
        name: p.h1, description: p.desc, url: abs(site, p.url), inLanguage: 'es-ES',
        isAccessibleForFree: true, learningResourceType: 'Ficha para imprimir',
        dateModified: (d.fechas[p.url] || {}).fecha || site.compilado,
        publisher: { '@type': 'Organization', name: site.nombre, url: site.url + '/' }
      };
      if (p.imagen) obra.image = p.hojas.filter((h) => h.hayImg).map((h) => abs(site, h.img));
      if (p.pdf) obra.encoding = { '@type': 'MediaObject', encodingFormat: 'application/pdf', contentUrl: abs(site, p.pdf) };
      if (p.esHub) {
        const hub = d.secciones.find((s) => s.cat === p.cat);
        obra.hasPart = hub.hijas.map((h) => ({ '@type': 'LearningResource', name: h.h1, url: abs(site, h.url) }));
      }
      out.push(obra);
      if (p.faq && p.faq.length) {
        out.push({
          '@context': 'https://schema.org', '@type': 'FAQPage',
          mainEntity: p.faq.map((f) => ({ '@type': 'Question', name: f[0], acceptedAnswer: { '@type': 'Answer', text: f[1] } }))
        });
      }
    }
    return out;
  }
};
