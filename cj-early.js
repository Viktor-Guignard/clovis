/* Clovis Project — application anticipée du calque.
   Chargé dans <head>, donc avant le moindre pixel.

   Le deck pèse 81 Mo : entre le premier affichage et la fin de l'analyse du
   document, il s'écoule plusieurs secondes. Les ops par sélecteur (titre,
   écran de chargement) doivent donc s'appliquer dès que leur cible paraît,
   sans attendre cj-apply.js qui, lui, vit après les slides.

   On observe le document et on traite chaque cible à son apparition : le
   rappel d'un MutationObserver est une micro-tâche, il s'exécute avant le
   rendu suivant. Aucun texte périmé n'atteint l'écran. */
(function () {
  if (/[?&]preview=1/.test(location.search)) return;   // l'éditeur pilote lui-même
  var P = window.CJ_PATCH;
  if (!P || !P.ops || !P.ops.length) return;

  // Attention : affecter document.title avant que <title> ne soit analysé en
  // crée un second dans <head> — HTML invalide. On attend l'élément réel.
  var attente = P.ops.filter(function (o) {
    return o.t === 'seltext' || o.t === 'selattr' || o.t === 'title';
  });
  if (!attente.length) return;

  function essayer() {
    attente = attente.filter(function (o) {
      var n;
      try { n = document.querySelector(o.t === 'title' ? 'head > title' : o.sel); }
      catch (e) { return false; }
      if (!n) return true;                                  // pas encore là
      if (o.t === 'title')        n.textContent = o.value;
      else if (o.t === 'seltext') n.innerHTML   = o.html;
      else                        n.setAttribute(o.name, o.value);
      return false;
    });
    return attente.length === 0;
  }

  if (essayer()) return;
  var obs = new MutationObserver(function () { if (essayer()) obs.disconnect(); });
  obs.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', function () { essayer(); obs.disconnect(); });
})();
