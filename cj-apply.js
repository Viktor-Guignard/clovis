/* CHONG JI — applique window.CJ_PATCH aux slides.
   Doit tourner APRÈS les <section class="slide">, AVANT le script de navigation. */
(function () {
  /* Deux sources possibles :
     - ?preview=1 (l'éditeur) : l'état en cours, y compris non enregistré, passé par sessionStorage
     - sinon (le deck public) : le calque enregistré dans patch.js */
  var ops = null, stamp = '';
  if (/[?&]preview=1/.test(location.search)) {
    try { ops = JSON.parse(sessionStorage.getItem('cj_preview_ops') || 'null'); } catch (e) {}
    ops = ops || []; stamp = ' (aperçu éditeur)';
  } else {
    var P = window.CJ_PATCH;
    ops = (P && P.ops) || [];
    stamp = (P && P.updated) ? ' — ' + P.updated : '';
  }
  if (!ops.length) return;
  var main = document.querySelector('main') || document.body;

  function esc(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : String(s).replace(/["\\]/g, '\\$&'); }
  function slideOf(lbl) { return main.querySelector('section.slide[data-lbl="' + esc(lbl) + '"]'); }
  function nodeAt(root, path) {
    if (!root) return null;
    if (!path) return root;
    var parts = String(path).split('-'), n = root, i;
    for (i = 0; i < parts.length; i++) {
      n = n.children[+parts[i]];
      if (!n) return null;
    }
    return n;
  }

  var handlers = {
    text: function (op) { var n = nodeAt(slideOf(op.slide), op.path); if (n) n.innerHTML = op.html; },
    attr: function (op) { var n = nodeAt(slideOf(op.slide), op.path); if (n) n.setAttribute(op.name, op.value); },
    img:  function (op) { var n = nodeAt(slideOf(op.slide), op.path); if (n) n.setAttribute('src', op.src); },
    lbl:  function (op) { var s = slideOf(op.slide); if (s) { s.dataset.lbl = op.value; } },
    skip: function (op) { var s = slideOf(op.slide); if (s) s.classList.toggle('skip', !!op.on); },
    del:  function (op) { var s = slideOf(op.slide); if (s) s.remove(); },
    add:  function (op) {
      var t = document.createElement('template');
      t.innerHTML = op.html.trim();
      var s = t.content.firstElementChild;
      if (!s) return;
      var ref = op.after ? slideOf(op.after) : null;
      if (ref) ref.after(s); else main.appendChild(s);
    },
    order: function (op) {
      op.slides.forEach(function (lbl) { var s = slideOf(lbl); if (s) main.appendChild(s); });
    },

    /* Ops par sélecteur : portée au document entier, pas seulement aux slides.
       Indispensables pour le <title>, l'écran de chargement et les attributs. */
    seltext: function (op) { var n = document.querySelector(op.sel); if (n) n.innerHTML = op.html; },
    selattr: function (op) { var n = document.querySelector(op.sel); if (n) n.setAttribute(op.name, op.value); },
    title:   function (op) { var t = document.querySelector('head > title'); if (t) t.textContent = op.value; else document.title = op.value; }
  };

  ops.forEach(function (op) {
    try { if (handlers[op.t]) handlers[op.t](op); }
    catch (e) { console.warn('[CJ_PATCH] op ignorée', op, e); }
  });
  console.log('[CJ_PATCH] ' + ops.length + ' modification(s) appliquée(s)' + stamp);
})();
