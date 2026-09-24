"""Genera public/og-image.png (la tarjeta que se ve al compartir el enlace).

    python make_og.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
FONDO = (20, 7, 31)
NARANJA, ROSA, MORADO, CIAN = (255, 179, 71), (255, 61, 139), (123, 47, 247), (45, 226, 230)
FUENTES = Path("C:/Windows/Fonts")


def mezcla(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def degradado(y, alto):
    t = y / alto
    return mezcla(NARANJA, ROSA, t / .55) if t < .55 else mezcla(ROSA, MORADO, (t - .55) / .45)


def main():
    img = Image.new("RGB", (W, H), FONDO)

    # Sol de atardecer con franjas.
    sol = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(sol)
    cx, cy, r = W // 2, 470, 330
    for y in range(cy - r, cy + r):
        if (y - (cy - r)) % 34 >= 26:
            continue
        dx = int((r * r - (y - cy) ** 2) ** .5)
        d.line([(cx - dx, y), (cx + dx, y)], fill=degradado(y - (cy - r), 2 * r))
    img = Image.blend(img, sol.filter(ImageFilter.GaussianBlur(1)), .35)

    # Rejilla del suelo.
    d = ImageDraw.Draw(img)
    for y in range(470, H, 26):
        d.line([(0, y), (W, y)], fill=(70, 20, 80), width=1)

    # Título con degradado.
    impact = ImageFont.truetype(str(FUENTES / "impact.ttf"), 128)
    texto = "¿GTA O REALIDAD?"
    caja = d.textbbox((0, 0), texto, font=impact)
    tw, th = caja[2] - caja[0], caja[3] - caja[1]
    mascara = Image.new("L", (W, H))
    ImageDraw.Draw(mascara).text(((W - tw) // 2, 150 - caja[1]), texto, font=impact, fill=255)
    color = Image.new("RGB", (W, H))
    cd = ImageDraw.Draw(color)
    for y in range(150, 150 + th + 10):
        cd.line([(0, y), (W, y)], fill=degradado(y - 150, th))
    sombra = mascara.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.new("RGB", (W, H), ROSA), (0, 0), sombra.point(lambda v: v * .5))
    img.paste(color, (0, 0), mascara)

    # Subtítulo.
    sub = ImageFont.truetype(str(FUENTES / "seguibl.ttf"), 40)
    linea = "Coches, precios y edificios de GTA contra la vida real"
    lw = d.textlength(linea, font=sub)
    d.text(((W - lw) // 2, 345), linea, font=sub, fill=(253, 242, 255))

    # Pastilla «¿Cuánta racha aguantas?».
    peq = ImageFont.truetype(str(FUENTES / "seguibl.ttf"), 32)
    reto = "¿Cuánta racha aguantas?"
    rw = d.textlength(reto, font=peq)
    x0, y0 = (W - rw) // 2 - 34, 430
    d.rounded_rectangle([x0, y0, x0 + rw + 68, y0 + 64], radius=32, fill=ROSA)
    d.text((x0 + 34, y0 + 10), reto, font=peq, fill=FONDO)

    marca = ImageFont.truetype(str(FUENTES / "seguibl.ttf"), 26)
    d.text((40, H - 56), "UN JUEGO DE DOUBLELAG", font=marca, fill=CIAN)

    salida = Path(__file__).parent / "public" / "og-image.png"
    img.save(salida, optimize=True)
    print(salida, salida.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
