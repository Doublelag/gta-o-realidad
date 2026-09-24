// Modo directo: el chat de Twitch vota con !1 (GTA) o !2 (real).
// Se conecta al chat en modo anónimo (solo lectura), sin tokens.
(() => {
  const CFG = window.CONFIG || {};
  const SEGUNDOS = CFG.segundosVoto || 20;
  const AVANCE = CFG.segundosAvance || 8;

  const $ = (id) => document.getElementById(id);

  let canal = "";
  let ws = null;
  let reintento = 0;
  let abierta = false;
  let votos = new Map();    // usuario -> "gta" | "real" (vale el último voto)
  let marcador = new Map(); // usuario -> { nombre, aciertos }
  let reloj = null;
  let avance = null;

  const estado = document.createElement("span");
  estado.className = "estado-directo";
  estado.hidden = true;
  document.querySelector(".marcador").insertBefore(estado, document.querySelector(".racha"));

  // --- conexión al chat ---
  function conectar(nombre) {
    canal = nombre.toLowerCase().replace(/^#/, "").trim();
    if (!/^[a-z0-9_]{3,25}$/.test(canal)) return false;
    if (ws) { ws.onclose = null; ws.close(); }

    ws = new WebSocket("wss://irc-ws.chat.twitch.tv:443");
    ws.onopen = () => {
      ws.send("CAP REQ :twitch.tv/tags");
      ws.send("PASS SCHMOOPIIE");
      ws.send(`NICK justinfan${Math.floor(Math.random() * 90000) + 10000}`);
      ws.send(`JOIN #${canal}`);
      reintento = 0;
      pintarEstado(true);
    };
    ws.onmessage = (e) => e.data.split("\r\n").forEach(linea);
    ws.onclose = () => {
      pintarEstado(false);
      reintento = Math.min(reintento + 1, 5);
      setTimeout(() => conectar(canal), reintento * 2000);
    };
    return true;
  }

  function pintarEstado(ok) {
    estado.hidden = false;
    estado.textContent = ok ? `🔴 #${canal}` : "⚠️ Reconectando…";
    estado.classList.toggle("caido", !ok);
  }

  function linea(l) {
    if (!l) return;
    if (l.startsWith("PING")) { ws.send("PONG :tmi.twitch.tv"); return; }
    const m = l.match(/^(?:@(\S+) )?:(\w+)!\S+ PRIVMSG #\w+ :(.*)$/);
    if (!m) return;
    const tags = Object.fromEntries((m[1] || "").split(";").map((t) => t.split("=")));
    votar(m[2], tags["display-name"] || m[2], m[3].trim().toLowerCase());
  }

  function votar(usuario, nombre, texto) {
    if (!abierta) return;
    let lado = null;
    if (texto === "!1" || texto === "1" || texto === "!gta") lado = "gta";
    if (texto === "!2" || texto === "2" || texto === "!real") lado = "real";
    if (!lado) return;
    votos.set(usuario, lado);
    if (!marcador.has(usuario)) marcador.set(usuario, { nombre, aciertos: 0 });
    pintarVotos();
  }

  // --- votación ---
  function contar() {
    let gta = 0, real = 0;
    for (const v of votos.values()) v === "gta" ? gta++ : real++;
    return { gta, real };
  }

  function pintarVotos() {
    const { gta, real } = contar();
    const total = gta + real || 1;
    $("votos-gta").textContent = gta;
    $("votos-real").textContent = real;
    $("barra-gta").style.width = `${(gta / total) * 100}%`;
    $("barra-real").style.width = `${(real / total) * 100}%`;
  }

  function arrancarReloj() {
    clearInterval(reloj);
    let quedan = SEGUNDOS;
    $("reloj").textContent = quedan;
    reloj = setInterval(() => {
      quedan--;
      if (quedan > 0) { $("reloj").textContent = quedan; return; }
      const { gta, real } = contar();
      if (gta + real === 0) {
        // Nadie ha votado: se vuelve a empezar la cuenta.
        quedan = SEGUNDOS;
        $("reloj").textContent = "…";
        return;
      }
      clearInterval(reloj);
      const lado = gta === real ? (Math.random() < 0.5 ? "gta" : "real") : gta > real ? "gta" : "real";
      window.Juego.elegir(lado);
    }, 1000);
  }

  window.addEventListener("juego:ronda", () => {
    if (!canal) return;
    clearTimeout(avance);
    votos = new Map();
    abierta = true;
    pintarVotos();
    $("votacion").hidden = false;
    arrancarReloj();
  });

  window.addEventListener("juego:resuelta", (e) => {
    if (!canal) return;
    abierta = false;
    clearInterval(reloj);
    $("reloj").textContent = "✓";
    const ganador = e.detail.ganador;
    for (const [usuario, lado] of votos) {
      if (lado === ganador) marcador.get(usuario).aciertos++;
    }
    // Pasa sola a la siguiente para no tener que tocar nada en directo.
    avance = setTimeout(() => $("btn-siguiente").click(), AVANCE * 1000);
  });

  window.addEventListener("juego:final", () => {
    if (!canal) return;
    clearTimeout(avance);
    const top = [...marcador.values()]
      .filter((j) => j.aciertos > 0)
      .sort((a, b) => b.aciertos - a.aciertos)
      .slice(0, 5);
    const lista = $("lista-top");
    lista.replaceChildren(...top.map((j) => {
      const li = document.createElement("li");
      li.textContent = `${j.nombre} · ${j.aciertos}`;
      return li;
    }));
    $("top-chat").hidden = top.length === 0;
  });

  // Reiniciar el marcador del chat en cada partida nueva.
  for (const id of ["btn-jugar", "btn-otra"]) {
    $(id).addEventListener("click", () => { marcador = new Map(); $("top-chat").hidden = true; }, true);
  }

  // --- configuración ---
  function activar(nombre) {
    if (!conectar(nombre)) return false;
    const url = new URL(location.href);
    url.searchParams.set("directo", canal);
    history.replaceState(null, "", url);
    $("url-obs").textContent = url.href;
    document.body.classList.add("modo-directo");
    return true;
  }

  $("form-directo").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = $("canal-twitch");
    if (!activar(input.value)) { input.setCustomValidity("Nombre de canal no válido"); input.reportValidity(); return; }
    input.setCustomValidity("");
    $("form-directo").closest("details").open = false;
  });
  $("canal-twitch").addEventListener("input", (e) => e.target.setCustomValidity(""));

  // Con ?prueba se pueden simular mensajes del chat desde la consola.
  if (new URLSearchParams(location.search).has("prueba")) window.simularChat = linea;

  const inicial = new URLSearchParams(location.search).get("directo");
  if (inicial) {
    $("canal-twitch").value = inicial;
    activar(inicial);
  }
})();
