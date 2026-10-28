"""Comprobaciones rápidas del proyecto (solo biblioteca estándar).

    python scripts/check.py

- public/datos.json es válido y cada comparación tiene los campos que usa el juego.
- Cada comparación tiene su página generada en public/comparacion/ (y no sobran).
- Todos los enlaces y recursos locales (href/src) de los HTML de public/ existen.
- build.py y make_og.py compilan, y los .js de public/ se pueden parsear (con Node, si está).

Sale con código 1 si algo falla.
"""
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True  # no dejar __pycache__ al importar build.py
RAIZ = Path(__file__).resolve().parent.parent
PUBLIC = RAIZ / "public"
CATEGORIAS = {"velocidad", "precio", "tamano", "otro"}

errores = []


def error(msg):
    errores.append(msg)


# --- datos.json ---------------------------------------------------------------
def es_url(v):
    return isinstance(v, str) and re.match(r"^https?://\S+$", v) is not None


def es_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def comprobar_datos():
    try:
        datos = json.loads((PUBLIC / "datos.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        error(f"datos.json no se puede leer: {e}")
        return []
    if not isinstance(datos, list) or not datos:
        error("datos.json debe ser una lista no vacía")
        return []

    ids = set()
    for i, d in enumerate(datos):
        donde = f"datos.json[{i}] ({d.get('id', '?') if isinstance(d, dict) else '?'})"
        if not isinstance(d, dict):
            error(f"{donde}: no es un objeto")
            continue
        for campo in ("id", "cat", "unidad", "pregunta", "gta", "real", "fuentes"):
            if campo not in d:
                error(f"{donde}: falta «{campo}»")
        if d.get("id") in ids:
            error(f"{donde}: id repetido")
        ids.add(d.get("id"))
        if d.get("cat") not in CATEGORIAS:
            error(f"{donde}: cat «{d.get('cat')}» no es una de {sorted(CATEGORIAS)}")
        for lado in ("gta", "real"):
            x = d.get(lado)
            if not isinstance(x, dict):
                error(f"{donde}: «{lado}» debe ser un objeto")
                continue
            if not isinstance(x.get("nombre"), str) or not x["nombre"].strip():
                error(f"{donde}: {lado}.nombre vacío")
            if not es_numero(x.get("valor")) or x["valor"] < 0:
                error(f"{donde}: {lado}.valor debe ser un número positivo")
        g, r = d.get("gta", {}), d.get("real", {})
        if isinstance(g, dict) and isinstance(r, dict) and g.get("valor") == r.get("valor"):
            error(f"{donde}: empate (el juego lo descartaría): no hay respuesta correcta")
        fuentes = d.get("fuentes", [])
        if not isinstance(fuentes, list) or not fuentes or not all(es_url(f) for f in fuentes):
            error(f"{donde}: «fuentes» debe ser una lista de URLs")
        if "video" in d and not es_url(d["video"]):
            error(f"{donde}: «video» no es una URL")
    return datos


def comprobar_paginas(datos):
    sys.path.insert(0, str(RAIZ))
    try:
        import build
    except Exception as e:  # noqa: BLE001
        error(f"build.py no se puede importar: {e}")
        return
    try:
        esperadas = {build.slug_de(d) for d in datos}
    except Exception as e:  # noqa: BLE001
        error(f"No se pudieron calcular los slugs: {e}")
        return
    if len(esperadas) != len(datos):
        error("Hay slugs repetidos en datos.json")
    carpeta = PUBLIC / "comparacion"
    hay = {p.name for p in carpeta.iterdir() if p.is_dir()} if carpeta.exists() else set()
    for s in sorted(esperadas - hay):
        error(f"Falta la página comparacion/{s}/ (ejecuta python build.py)")
    for s in sorted(hay - esperadas):
        error(f"Sobra la página comparacion/{s}/ (ejecuta python build.py)")
    if not (carpeta / "index.html").exists():
        error("Falta comparacion/index.html (ejecuta python build.py)")


# --- enlaces locales en los HTML -----------------------------------------------
class Enlaces(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for nombre, valor in attrs:
            if nombre in ("href", "src") and valor:
                self.urls.append(valor)


def comprobar_enlaces():
    for html in sorted(PUBLIC.rglob("*.html")):
        p = Enlaces()
        p.feed(html.read_text(encoding="utf-8"))
        for url in p.urls:
            u = urlparse(url)
            if u.scheme or u.netloc or url.startswith(("#", "mailto:", "data:")):
                continue
            ruta = unquote(u.path)
            if not ruta:
                continue
            destino = (PUBLIC / ruta.lstrip("/")) if ruta.startswith("/") else (html.parent / ruta)
            if destino.is_dir():
                destino = destino / "index.html"
            if not destino.exists():
                error(f"{html.relative_to(RAIZ)}: enlace roto «{url}»")


# --- código ----------------------------------------------------------------------
def comprobar_codigo():
    for py in ("build.py", "make_og.py", "scripts/check.py"):
        try:
            compile((RAIZ / py).read_text(encoding="utf-8"), py, "exec")
        except SyntaxError as e:
            error(f"{py} no compila: {e}")
    node = shutil.which("node")
    if not node:
        print("Aviso: Node no está instalado; no se comprueba la sintaxis de los .js")
        return
    for js in sorted(PUBLIC.glob("*.js")):
        r = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
        if r.returncode:
            error(f"{js.relative_to(RAIZ)} no parsea:\n{r.stderr.strip()}")


def main():
    datos = comprobar_datos()
    if datos:
        comprobar_paginas(datos)
    comprobar_enlaces()
    comprobar_codigo()
    if errores:
        print(f"{len(errores)} problema(s):")
        for e in errores:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK: {len(datos)} comparaciones, páginas, enlaces y código correctos.")


if __name__ == "__main__":
    main()
