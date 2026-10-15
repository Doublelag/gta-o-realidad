// Banners de Instant Gaming (patrocinador).
//
// Su script dibuja un banner responsive dentro de cada hueco que le declares,
// con el enlace de afiliado ya puesto. Dos reglas suyas que hay que respetar:
//
//   1. La config tiene que existir ANTES de que cargue su loader. Por eso este
//      archivo va sin defer y el loader con defer.
//   2. Cada hueco necesita su propio identificador en `banners`. Por eso aqui
//      se recorren los <div class="pub-ig"> de la pagina y se les pone una
//      clase numerada al vuelo: asi se pueden poner los huecos que hagan falta
//      en el HTML sin tocar este archivo.
//
// El igr es el codigo de afiliado: sin el, los clics no cuentan.
(function () {
  var huecos = Array.prototype.slice.call(document.querySelectorAll(".pub-ig"));

  window.igBannerConfig = {
    lang: "es",
    igr: "Doublelag",
    banners: huecos.map(function (hueco, i) {
      var clase = "pub-ig-" + (i + 1);
      hueco.classList.add(clase);
      return clase;
    }),
  };

  // Cada hueco lleva encima la etiqueta "Publicidad". Si el banner no llega
  // (bloqueador, script caido, sin conexion) esa etiqueta se quedaria sola
  // presidiendo un rectangulo vacio, asi que el bloque nace oculto y solo se
  // enciende cuando de verdad hay algo dentro.
  function encender(hueco) {
    var bloque = hueco.closest(".pub");
    if (bloque) bloque.classList.add("pub-ok");
  }

  huecos.forEach(function (hueco) {
    if (hueco.children.length) return encender(hueco);
    var ojo = new MutationObserver(function () {
      if (!hueco.children.length) return;
      ojo.disconnect();
      encender(hueco);
    });
    ojo.observe(hueco, { childList: true });
    // Su script tarda lo que tarde, pero no se vigila para siempre.
    setTimeout(function () { ojo.disconnect(); }, 15000);
  });
})();
