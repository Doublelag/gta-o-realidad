"""Genera las páginas SEO a partir de public/datos.json.

    python build.py

Crea public/comparacion/<slug>/index.html (una por dato), el índice
public/comparacion/index.html, sitemap.xml y robots.txt. Los archivos
generados no se editan a mano: se regeneran con este script.
"""
import json
import re
import shutil
import unicodedata
from datetime import date
from html import escape
from pathlib import Path

BASE = "https://gta-o-realidad.comparador-hosting.workers.dev"
RAIZ = Path(__file__).parent / "public"
SALIDA = RAIZ / "comparacion"

MEDIDA = {"velocidad": "velocidad", "precio": "precio", "tamano": "tamaño", "otro": "dato"}
VERBO = {  # (pregunta con los dos nombres, ganador, adjetivo)
    "velocidad": ("¿Corre más {a} o {b}?", "corre más", "más rápido"),
    "precio": ("¿Cuesta más {a} o {b}?", "cuesta más", "más caro"),
    "tamano": ("¿Qué es más grande, {a} o {b}?", "es más grande", "más grande"),
    "otro": ("¿Qué es mayor, {a} o {b}?", "es mayor", "mayor"),
}


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"\(.*?\)", "", t.lower())
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def formatear(valor, unidad):
    if isinstance(valor, float) and not valor.is_integer():
        n = f"{valor:,.1f}"
    else:
        n = f"{int(valor):,}"
    n = n.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${n}" if unidad == "USD" else f"{n} {unidad}"


def slug_de(d):
    return f"{slug(d['gta']['nombre'])}-gta-vs-{slug(d['real']['nombre'])}-{slug(MEDIDA[d['cat']])}"


def pagina(d, relacionados):
    g, r, u = d["gta"], d["real"], d["unidad"]
    pregunta_tpl, verbo, adjetivo = VERBO.get(d["cat"], VERBO["otro"])
    a = f"{g['nombre']} ({g.get('juego', 'GTA')})"
    b = f"{r['nombre']} (real)"
    pregunta = pregunta_tpl.format(a=a, b=b)
    gana_gta = g["valor"] > r["valor"]
    mayor, menor = (g, r) if gana_gta else (r, g)
    veces = mayor["valor"] / menor["valor"] if menor["valor"] else 0
    diferencia = (f"{veces:.1f}".replace(".", ",") + " veces") if veces >= 2 else f"un {round((veces - 1) * 100)} %"
    respuesta = (
        f"{'Gana GTA' if gana_gta else 'Gana la realidad'}: {mayor['nombre']} "
        f"{verbo}. {g['nombre']}: {formatear(g['valor'], u)}. {r['nombre']}: {formatear(r['valor'], u)}. "
        f"Diferencia: {diferencia} {adjetivo}."
    )
    titulo = f"{g['nombre']} (GTA) vs {r['nombre']} real: {MEDIDA[d['cat']]}"
    url = f"{BASE}/comparacion/{slug_de(d)}/"

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": pregunta,
            "acceptedAnswer": {"@type": "Answer", "text": f"{respuesta} {d.get('dato', '')}".strip()},
        }],
    }

    video = ""
    if d.get("video"):
        video = (f'<a class="cta cta-video" href="{escape(d["video"])}" target="_blank" rel="noopener">'
                 f'🎥 {escape(d.get("videoTitulo") or "Lo explico en este vídeo")}</a>')

    fuentes = "".join(
        f'<li><a href="{escape(f)}" target="_blank" rel="noopener nofollow">{escape(re.sub(r"^https?://(www\\.)?", "", f)[:70])}</a></li>'
        for f in d.get("fuentes", [])
    )
    rel = "".join(
        f'<li><a href="/comparacion/{slug_de(x)}/">{escape(x["gta"]["nombre"])} vs {escape(x["real"]["nombre"])}</a></li>'
        for x in relacionados
    )

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(titulo)}</title>
  <meta name="description" content="{escape(respuesta)}">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="{escape(pregunta)}">
  <meta property="og:description" content="¿Aciertas? Compara {escape(g['nombre'])} con {escape(r['nombre'])} y juega a ¿GTA o Realidad?">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#14071f">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>
</head>
<body>
  <div class="sol" aria-hidden="true"></div>
  <main id="app" class="pagina">
    <nav class="migas"><a href="/">¿GTA o Realidad?</a> › <a href="/comparacion/">Comparaciones</a></nav>
    <p class="categoria">{escape(MEDIDA[d['cat']].capitalize())}</p>
    <h1 class="pregunta">{escape(pregunta)}</h1>
    <p class="sub">Piénsalo antes de mirar. Luego pon a prueba tu racha con el resto de datos.</p>

    <details class="revelar">
      <summary class="btn btn-principal">Ver la respuesta</summary>
      <div class="duelo">
        <div class="carta carta-gta {'ganadora' if gana_gta else 'perdedora'}">
          <span class="origen">{escape(g.get('juego', 'GTA'))}</span>
          <span class="nombre">{escape(g['nombre'])}</span>
          <span class="valor">{formatear(g['valor'], u)}</span>
        </div>
        <span class="vs">VS</span>
        <div class="carta carta-real {'perdedora' if gana_gta else 'ganadora'}">
          <span class="origen">Vida real</span>
          <span class="nombre">{escape(r['nombre'])}</span>
          <span class="valor">{formatear(r['valor'], u)}</span>
        </div>
      </div>
      <p class="veredicto {'gana-gta' if gana_gta else 'gana-real'}">{'Gana GTA' if gana_gta else 'Gana la realidad'}</p>
      <p class="dato">{escape(respuesta)} {escape(d.get('dato', ''))}</p>
    </details>

    <div class="ctas">
      <a class="cta cta-jugar" href="/">🎮 Jugar a ¿GTA o Realidad? ¿Cuánta racha aguantas?</a>
      {video}
    </div>

    <section class="bloque">
      <h2>Fuentes</h2>
      <ul class="fuentes">{fuentes}</ul>
    </section>

    <section class="bloque">
      <h2>Más comparaciones</h2>
      <ul class="relacionados">{rel}</ul>
    </section>
  </main>
  <footer class="pie">
    Proyecto fan de <a href="https://www.youtube.com/@DoublelagGTA6" target="_blank" rel="noopener">Doublelag</a>. Sin relación con Rockstar Games ni Take-Two.
  </footer>
</body>
</html>
"""


def indice(datos):
    grupos = {}
    for d in datos:
        grupos.setdefault(d["cat"], []).append(d)
    secciones = ""
    for cat, lista in grupos.items():
        items = "".join(
            f'<li><a href="/comparacion/{slug_de(d)}/">{escape(d["gta"]["nombre"])} <span>vs</span> {escape(d["real"]["nombre"])}</a></li>'
            for d in sorted(lista, key=lambda x: x["gta"]["nombre"])
        )
        secciones += f'<section class="bloque"><h2>{escape(MEDIDA[cat].capitalize())}</h2><ul class="relacionados">{items}</ul></section>'
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GTA vs la vida real: todas las comparaciones</title>
  <meta name="description" content="Velocidad, precio y tamaño de coches, aviones y edificios de GTA V comparados con los reales en los que se basan. {len(datos)} comparaciones con fuentes.">
  <link rel="canonical" href="{BASE}/comparacion/">
  <meta property="og:image" content="{BASE}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#14071f">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <div class="sol" aria-hidden="true"></div>
  <main id="app" class="pagina">
    <nav class="migas"><a href="/">¿GTA o Realidad?</a> › Comparaciones</nav>
    <h1 class="pregunta">GTA vs la vida real</h1>
    <p class="sub">{len(datos)} comparaciones con sus fuentes. ¿Te las sabes? <a href="/">Juega y compruébalo</a>.</p>
    {secciones}
  </main>
  <footer class="pie">
    Proyecto fan de <a href="https://www.youtube.com/@DoublelagGTA6" target="_blank" rel="noopener">Doublelag</a>. Sin relación con Rockstar Games ni Take-Two.
  </footer>
</body>
</html>
"""


def main():
    datos = json.loads((RAIZ / "datos.json").read_text(encoding="utf-8"))
    slugs = [slug_de(d) for d in datos]
    repetidos = {s for s in slugs if slugs.count(s) > 1}
    if repetidos:
        raise SystemExit(f"Slugs repetidos: {repetidos}")

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)

    for d in datos:
        misma = [x for x in datos if x is not d and x["cat"] == d["cat"]]
        otra = [x for x in datos if x is not d and x["cat"] != d["cat"]]
        # Los de la misma categoría primero, rotando para repartir enlaces.
        i = datos.index(d)
        relacionados = (misma[i % max(len(misma), 1):] + misma)[:5] + otra[i % max(len(otra), 1):][:1]
        carpeta = SALIDA / slug_de(d)
        carpeta.mkdir()
        (carpeta / "index.html").write_text(pagina(d, relacionados), encoding="utf-8")

    (SALIDA / "index.html").write_text(indice(datos), encoding="utf-8")

    hoy = date.today().isoformat()
    urls = [f"{BASE}/", f"{BASE}/comparacion/"] + [f"{BASE}/comparacion/{s}/" for s in slugs]
    (RAIZ / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{hoy}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (RAIZ / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(datos)} páginas + índice + sitemap")


if __name__ == "__main__":
    main()
