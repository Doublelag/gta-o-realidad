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

## Probar en local

```bash
python -m http.server 5190 --directory public
```

## Publicar (Cloudflare)

```bash
wrangler deploy
```

Solo se sube la carpeta `public/`.
