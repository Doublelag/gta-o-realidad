# ¿GTA o Realidad?

**¿Corre más el Pegassi Infernus de GTA V o el Lamborghini Murciélago en el que se basa?**
Un juego web de «más o menos» que enfrenta coches, motos, aviones, precios y lugares de GTA
con sus equivalentes reales. Elige cuál es mayor, mantén la racha y compártela… o deja que juegue
el chat de tu directo de Twitch.

Proyecto de [Doublelag](https://www.youtube.com/@DoublelagGTA6). Hecho por fans,
sin relación con Rockstar Games ni Take-Two.

> 📸 CAPTURA AQUÍ — portada del juego y una ronda en marcha (GTA vs vida real).

Web publicada: <https://gta-o-realidad.comparador-hosting.workers.dev/>

## Características

- **Juego de racha con vidas**: cada ronda muestra un elemento de GTA y su versión real;
  aciertas cuál tiene más velocidad, precio o tamaño. Por defecto hay 3 vidas.
- **Datos con fuentes**: cada comparación de `public/datos.json` incluye las URLs de donde
  sale el dato, una frase que explica la diferencia y, si existe, el vídeo del canal donde se trata.
- **Récord local** guardado en el navegador (`localStorage`), con tolerancia a modo privado.
- **Compartir la racha** con el menú nativo del móvil o copiándola al portapapeles
  (con una rejilla de 🟩/🟥 al estilo Wordle).
- **Modo directo para Twitch**: el chat vota con `!1` / `!2`, hay cuenta atrás,
  avance automático y top 5 del chat al final. Pensado para usarse como fuente de navegador en OBS.
- **Páginas SEO por comparación** generadas a partir de los datos, con la respuesta oculta tras
  un botón, fuentes, comparaciones relacionadas y datos estructurados `FAQPage`.
- **Tarjeta para redes** (`og:image`) generada por script.
- Controles con teclado (`1` = GTA, `2` = vida real) y respeto a `prefers-reduced-motion`.

## Tecnología

- **HTML, CSS y JavaScript sin dependencias ni paso de compilación** para el juego (`public/`).
- **Python 3.11+** (solo biblioteca estándar) para generar las páginas SEO, el `sitemap.xml`
  y el `robots.txt` (`build.py`).
- **Pillow** solo para regenerar la imagen para compartir (`make_og.py`).
- **Chat de Twitch** por WebSocket IRC en modo anónimo (solo lectura, sin token ni cuenta).
- **Cloudflare Workers** con archivos estáticos (`wrangler.jsonc`) para publicar.
- **GitHub Actions** para comprobar los datos, las páginas generadas y los enlaces en cada push.

## Probar en local

No hace falta instalar nada: basta con servir la carpeta `public/`.

```bash
python -m http.server 5190 --directory public
```

Y abre <http://localhost:5190>. (Abrir `index.html` con doble clic no vale: el juego carga
`datos.json` con `fetch`, que necesita un servidor.)

### Modo directo (chat de Twitch)

Abre el juego con `?directo=tucanal` (o actívalo en la portada) y úsalo como
fuente de navegador en OBS. El chat vota con `!1` (GTA) o `!2` (real); al
acabar la cuenta atrás gana la mayoría, se revela y pasa sola a la siguiente.
Al final sale el top 5 del chat. Lee el chat en modo anónimo: no hace falta
token ni cuenta.

Tiempos en `config.js`: `segundosVoto` (20 por defecto) y `segundosAvance` (8).
Para probar sin directo: añade `&prueba` a la URL y usa `simularChat(...)` en la consola, por ejemplo:

```js
simularChat(":pepe!pepe@x PRIVMSG #tucanal :!1")
```

## Generar las páginas

```bash
python build.py      # páginas SEO, índice, sitemap.xml y robots.txt
python scripts/check.py   # comprobaciones (las mismas que corre GitHub Actions)
```

`build.py` genera una página por comparación en `public/comparacion/`,
más el índice, `sitemap.xml` y `robots.txt`. Vuelve a ejecutarlo cada vez que cambie
`datos.json`. No edites a mano lo generado.

`scripts/check.py` comprueba que `datos.json` es válido (campos, categorías, valores numéricos,
sin empates, fuentes con URL), que cada comparación tiene su página generada, que todos los enlaces
y recursos locales de los HTML existen y que el código Python y JavaScript parsea.

La imagen para compartir (`public/og-image.png`) se regenera con `python make_og.py`. Necesita
Pillow (`pip install pillow`) y usa las fuentes Impact y Segoe UI Black de Windows
(`C:/Windows/Fonts`); en otro sistema hay que cambiar la ruta `FUENTES` del script.

## Añadir un dato

```json
{
  "id": "infernus",
  "cat": "velocidad",
  "unidad": "km/h",
  "pregunta": "¿Cuál corre más?",
  "gta": { "nombre": "Pegassi Infernus", "juego": "GTA V", "valor": 0 },
  "real": { "nombre": "Lamborghini Murciélago", "valor": 0 },
  "dato": "Frase corta que explica la diferencia.",
  "video": "https://youtu.be/... (opcional: vídeo donde se explica)",
  "videoTitulo": "Título del vídeo (opcional)",
  "fuentes": ["https://..."]
}
```

`cat`: `velocidad`, `precio`, `tamano` u `otro`. `unidad`: `km/h`, `USD`, `EUR`, `m`, `km²`…

Después: `python build.py` y `python scripts/check.py`.

## Configuración

`public/config.js` reúne los enlaces (canal, Discord, Instant Gaming, vídeo recomendado al
terminar), el número de vidas y los tiempos del modo directo. Se cambian sin tocar el juego;
deja un enlace en `""` para que su botón no aparezca.

Los huecos de publicidad del patrocinador (Instant Gaming) los gestiona `public/banner-ig.js`:
nacen ocultos y solo se muestran si el banner llega a cargar.

## Publicar (Cloudflare)

El sitio se publica como un Worker de Cloudflare que solo sirve archivos estáticos
(no hay código de servidor). `wrangler.jsonc` indica que se sube únicamente la carpeta
`public/` y activa `html_handling: "auto-trailing-slash"`, para que
`/comparacion/<slug>/` sirva su `index.html`.

```bash
npm install -g wrangler   # o usa npx wrangler
wrangler login            # una vez, con tu cuenta de Cloudflare
python build.py           # si han cambiado los datos
wrangler deploy
```

El resultado queda en `https://gta-o-realidad.<tu-subdominio>.workers.dev`. Si cambias de dominio,
actualiza `BASE` en `build.py` (URLs canónicas y sitemap) y la `og:image` de `public/index.html`.

## Estructura

```
.
├── public/                 # Lo que se publica
│   ├── index.html          # El juego
│   ├── juego.js            # Lógica de la partida (rondas, vidas, récord, compartir)
│   ├── directo.js          # Modo directo con el chat de Twitch
│   ├── config.js           # Enlaces, vidas y tiempos
│   ├── banner-ig.js        # Huecos de publicidad del patrocinador
│   ├── datos.json          # Las comparaciones y sus fuentes
│   ├── styles.css
│   ├── favicon.svg
│   ├── og-image.png        # Generada por make_og.py
│   ├── comparacion/        # Generado por build.py (una carpeta por comparación + índice)
│   ├── sitemap.xml         # Generado por build.py
│   └── robots.txt          # Generado por build.py
├── build.py                # Genera las páginas SEO
├── make_og.py              # Genera la imagen para compartir
├── scripts/check.py        # Comprobaciones de datos, páginas y enlaces
├── .github/workflows/      # CI: ejecuta scripts/check.py
└── wrangler.jsonc          # Configuración de Cloudflare
```

## Cómo se hizo

Este proyecto está hecho con IA, en modo *vibe coding*: Doublelag pone la idea, los datos que
quiere contar y el criterio de diseño, y el código se escribe conversando con
[Claude Code](https://claude.com/claude-code), el asistente de programación de Anthropic.
El juego, el modo directo de Twitch, el generador de páginas SEO, la imagen para compartir y las
comprobaciones automáticas salieron de esas conversaciones.
Los datos de cada comparación llevan sus fuentes para poder verificarlos.
