# ¿GTA o Realidad?

Juego web de «más o menos»: coches, precios y edificios de GTA contra sus
equivalentes reales. Elige cuál es mayor, mantén la racha y compártela.

Proyecto de [Doublelag](https://www.youtube.com/@DoublelagGTA6). Hecho por fans,
sin relación con Rockstar Games ni Take-Two.

## Cómo funciona

- HTML, CSS y JavaScript sin dependencias ni paso de compilación.
- `public/datos.json`: las comparaciones. Cada una con su fuente.
- `public/config.js`: enlaces (canal, Discord, Instant Gaming, vídeo recomendado)
  y número de vidas. Se cambian sin tocar el juego.
- Récord guardado en el navegador del jugador (`localStorage`).
- Compartir la racha con el menú nativo del móvil o copiándola al portapapeles.

## Modo directo (chat de Twitch)

Abre el juego con `?directo=tucanal` (o actívalo en la portada) y úsalo como
fuente de navegador en OBS. El chat vota con `!1` (GTA) o `!2` (real); al
acabar la cuenta atrás gana la mayoría, se revela y pasa sola a la siguiente.
Al final sale el top 5 del chat. Lee el chat en modo anónimo: no hace falta
token ni cuenta.

Tiempos en `config.js`: `segundosVoto` (20 por defecto) y `segundosAvance` (8).
Para probar sin directo: añade `&prueba` a la URL y usa `simularChat(...)` en la consola.

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
  "fuentes": ["https://..."]
}
```

`cat`: `velocidad`, `precio`, `tamano` u `otro`. `unidad`: `km/h`, `USD`, `EUR`, `m`, `km²`…

## Páginas SEO

`python build.py` genera una página por comparación en `public/comparacion/`,
más el índice, `sitemap.xml` y `robots.txt`. Cada página tiene la pregunta,
la respuesta oculta tras un botón, el dato, las fuentes, el vídeo relacionado y
datos estructurados FAQ. Vuelve a ejecutarlo cada vez que cambie `datos.json`.
No edites a mano lo generado.

## Probar en local

```bash
python -m http.server 5190 --directory public
```

## Publicar (Cloudflare)

```bash
wrangler deploy
```

Solo se sube la carpeta `public/`.
