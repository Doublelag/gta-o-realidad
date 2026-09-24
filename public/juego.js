(() => {
  const CFG = window.CONFIG || {};
  const VIDAS = CFG.vidas || 3;
  const CLAVE_RECORD = "gtaorealidad.record";

  const CATEGORIAS = {
    velocidad: "Velocidad",
    precio: "Precio",
    tamano: "Tamaño",
    otro: "Curiosidad",
  };

  const $ = (id) => document.getElementById(id);

  let datos = [];
  let mazo = [];
  let actual = null;
  let puntos = 0;
  let vidas = VIDAS;
  let historial = [];

  // --- almacenamiento (puede fallar en modo privado) ---
  function leerRecord() {
    try { return Number(localStorage.getItem(CLAVE_RECORD)) || 0; } catch { return 0; }
  }
  function guardarRecord(n) {
    try { localStorage.setItem(CLAVE_RECORD, String(n)); } catch {}
  }

  function barajar(lista) {
    const a = lista.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function formatear(valor, unidad) {
    const n = new Intl.NumberFormat("es-ES").format(valor);
    if (unidad === "USD") return `$${n}`;
    if (unidad === "EUR") return `${n} €`;
    return `${n} ${unidad}`;
  }

  function mostrar(pantalla) {
    document.querySelectorAll(".pantalla").forEach((p) => p.classList.toggle("activa", p.id === pantalla));
    window.scrollTo({ top: 0 });
  }

  function pintarVidas() {
    $("vidas").textContent = "❤️".repeat(vidas) + "🖤".repeat(VIDAS - vidas);
  }

  // --- flujo ---
  function empezar() {
    mazo = barajar(datos);
    puntos = 0;
    vidas = VIDAS;
    historial = [];
    $("puntos").textContent = "0";
    pintarVidas();
    mostrar("partida");
    siguiente();
  }

  function siguiente() {
    if (!mazo.length) return terminar(true);
    actual = mazo.pop();

    $("categoria").textContent = CATEGORIAS[actual.cat] || "Curiosidad";
    $("pregunta").textContent = actual.pregunta;
    $("gta-juego").textContent = actual.gta.juego || "GTA";
    $("gta-nombre").textContent = actual.gta.nombre;
    $("real-nombre").textContent = actual.real.nombre;
    $("gta-valor").textContent = "?";
    $("real-valor").textContent = "?";

    for (const carta of [$("carta-gta"), $("carta-real")]) {
      carta.disabled = false;
      carta.classList.remove("ganadora", "perdedora", "elegida", "fallo");
    }
    $("resultado").hidden = true;
    window.dispatchEvent(new CustomEvent("juego:ronda", { detail: actual }));
  }

  function contar(el, hasta, unidad) {
    const reducir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducir) { el.textContent = formatear(hasta, unidad); return; }
    const inicio = performance.now();
    const dur = 700;
    const paso = (t) => {
      const k = Math.min(1, (t - inicio) / dur);
      const v = k < 1 ? Math.round(hasta * (1 - Math.pow(1 - k, 3))) : hasta;
      el.textContent = formatear(v, unidad);
      if (k < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
    // Si la pestaña no está pintando, la animación se congela: asegura el valor final.
    setTimeout(() => { el.textContent = formatear(hasta, unidad); }, dur + 100);
  }

  function elegir(lado) {
    const gtaGana = actual.gta.valor > actual.real.valor;
    const acierto = (lado === "gta") === gtaGana;

    const cartaGta = $("carta-gta");
    const cartaReal = $("carta-real");
    cartaGta.disabled = cartaReal.disabled = true;

    const elegida = lado === "gta" ? cartaGta : cartaReal;
    elegida.classList.add("elegida");
    (gtaGana ? cartaGta : cartaReal).classList.add("ganadora");
    (gtaGana ? cartaReal : cartaGta).classList.add("perdedora");
    if (!acierto) elegida.classList.add("fallo");

    contar($("gta-valor"), actual.gta.valor, actual.unidad);
    contar($("real-valor"), actual.real.valor, actual.unidad);

    window.dispatchEvent(new CustomEvent("juego:resuelta", { detail: { ganador: gtaGana ? "gta" : "real" } }));

    historial.push(acierto);
    if (acierto) {
      puntos++;
      $("puntos").textContent = String(puntos);
    } else {
      vidas--;
      pintarVidas();
    }

    const veredicto = $("veredicto");
    veredicto.textContent = acierto ? "¡Correcto!" : "¡Fallo!";
    veredicto.className = "veredicto " + (acierto ? "bien" : "mal");
    $("dato").textContent = actual.dato || "";

    const video = $("enlace-video");
    video.hidden = !actual.video;
    if (actual.video) video.href = actual.video;

    $("btn-siguiente").textContent = vidas > 0 ? "Siguiente" : "Ver resultado";
    $("resultado").hidden = false;
    $("btn-siguiente").focus({ preventScroll: true });
    $("resultado").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function terminar(completo) {
    const record = Math.max(leerRecord(), puntos);
    const nuevo = puntos > 0 && puntos === record && puntos > leerRecord();
    guardarRecord(record);

    $("final-motivo").textContent = completo ? "¡Te has pasado todos los datos!" : "Sin vidas";
    $("final-puntos").textContent = String(puntos);
    $("final-record").textContent = nuevo ? "🏆 ¡Nuevo récord!" : `Tu récord: ${record}`;
    $("rejilla").textContent = historial.map((a) => (a ? "🟩" : "🟥")).join("");
    $("aviso-copia").hidden = true;
    pintarCtas();
    mostrar("final");
    window.dispatchEvent(new CustomEvent("juego:final"));
  }

  function textoCompartir() {
    return `¿GTA o Realidad? 🌴\nRacha de ${puntos}\n${historial.map((a) => (a ? "🟩" : "🟥")).join("")}\n¿Me superas? ${location.origin}${location.pathname}`;
  }

  async function compartir() {
    const texto = textoCompartir();
    if (navigator.share) {
      try { await navigator.share({ text: texto }); return; } catch (e) { if (e.name === "AbortError") return; }
    }
    try {
      await navigator.clipboard.writeText(texto);
      $("aviso-copia").hidden = false;
    } catch {
      window.prompt("Copia tu resultado:", texto);
    }
  }

  function enlace(id, url, texto) {
    const el = $(id);
    el.hidden = !url;
    if (url) el.href = url;
    if (texto) el.textContent = texto;
  }

  function pintarCtas() {
    const v = CFG.videoFinal || {};
    enlace("cta-video", v.url, v.titulo ? `🎥 ${v.titulo}` : "🎥 Mira el vídeo completo");
    enlace("cta-yt", CFG.youtube);
    enlace("cta-ig", CFG.instantGaming);
    enlace("cta-dc", CFG.discord);
  }

  // --- arranque ---
  async function cargar() {
    const r = await fetch("datos.json", { cache: "no-cache" });
    if (!r.ok) throw new Error("No se pudieron cargar los datos");
    datos = (await r.json()).filter((d) => d.gta.valor !== d.real.valor);
  }

  $("vidas-portada").textContent = String(VIDAS);
  const rec = leerRecord();
  if (rec) $("record-portada").textContent = `Tu récord: ${rec}`;

  $("btn-jugar").addEventListener("click", empezar);
  $("btn-otra").addEventListener("click", empezar);
  $("carta-gta").addEventListener("click", () => elegir("gta"));
  $("carta-real").addEventListener("click", () => elegir("real"));
  $("btn-siguiente").addEventListener("click", () => (vidas > 0 ? siguiente() : terminar(false)));
  $("btn-compartir").addEventListener("click", compartir);

  // Atajos: 1 = GTA, 2 = Real, Enter/espacio en el botón = siguiente
  document.addEventListener("keydown", (e) => {
    if (!$("partida").classList.contains("activa")) return;
    if (e.key === "1" && !$("carta-gta").disabled) elegir("gta");
    if (e.key === "2" && !$("carta-real").disabled) elegir("real");
  });

  // Para el modo directo (directo.js).
  window.Juego = {
    empezar,
    elegir: (lado) => { if (!$("carta-gta").disabled) elegir(lado); },
  };

  $("btn-jugar").disabled = true;
  cargar()
    .then(() => { $("btn-jugar").disabled = false; })
    .catch(() => { $("record-portada").textContent = "No se han podido cargar los datos. Recarga la página."; });
})();
