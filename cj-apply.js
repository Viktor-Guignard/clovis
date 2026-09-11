/* Clovis Project — applique le calque aux slides.
   Doit tourner APRÈS les <section class="slide">, AVANT le script de navigation
   du deck : sinon une suppression ou un réordonnancement désynchronise le
   sommaire et le compteur.

   Chaque op rend compte de son sort dans window.CJ_APPLIED : l'éditeur s'en
   sert pour signaler les modifications qui ne s'appliquent plus à rien —
   sans quoi elles resteraient dans le calque, invisibles et inertes. */
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
  window.CJ_APPLIED = [];
  if (!ops.length) return;

  var main = document.querySelector('main') || document.body;

  function esc(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : String(s).replace(/["\\]/g, '\\$&'); }
  function slideOf(l) { return main.querySelector('section.slide[data-lbl="' + esc(l) + '"]'); }
  function nodeAt(root, path) {
    if (!root) return null;
    if (!path) return root;
    var parts = String(path).split('-'), n = root, i;
    for (i = 0; i < parts.length; i++) { n = n.children[+parts[i]]; if (!n) return null; }
    return n;
  }

  /* chaque gestionnaire renvoie true s'il a effectivement agi */
  var H = {
    text: function (o) { var n = nodeAt(slideOf(o.slide), o.path); if (!n) return false; n.innerHTML = o.html; return true; },
    attr: function (o) { var n = nodeAt(slideOf(o.slide), o.path); if (!n) return false; n.setAttribute(o.name, o.value); return true; },
    img:  function (o) { var n = nodeAt(slideOf(o.slide), o.path); if (!n) return false; n.setAttribute('src', o.src); return true; },
    lbl:  function (o) { var s = slideOf(o.slide); if (!s) return false; s.dataset.lbl = o.value; return true; },
    skip: function (o) { var s = slideOf(o.slide); if (!s) return false; s.classList.toggle('skip', !!o.on); return true; },
    del:  function (o) { var s = slideOf(o.slide); if (!s) return false; s.remove(); return true; },
    add:  function (o) {
      var t = document.createElement('template');
      t.innerHTML = String(o.html).trim();
      var s = t.content.firstElementChild;
      if (!s) return false;
      var ref = o.after ? slideOf(o.after) : null;
      if (ref) ref.after(s); else main.appendChild(s);
      return true;
    },
    order: function (o) {
      var n = 0;
      o.slides.forEach(function (l) { var s = slideOf(l); if (s) { main.appendChild(s); n++; } });
      return n > 0;
    },

    /* Ops par sélecteur : portée au document entier, pas seulement aux slides.
       Indispensables pour le <title>, l'écran de chargement et les attributs. */
    seltext: function (o) { var n = document.querySelector(o.sel); if (!n) return false; n.innerHTML = o.html; return true; },
    selattr: function (o) { var n = document.querySelector(o.sel); if (!n) return false; n.setAttribute(o.name, o.value); return true; },
    title:   function (o) { var t = document.querySelector('head > title'); if (t) t.textContent = o.value; else document.title = o.value; return true; }
  };

  var agies = 0;
  ops.forEach(function (op, i) {
    var ok = false, err = null;
    try { ok = H[op.t] ? !!H[op.t](op) : false; }
    catch (e) { err = String(e && e.message || e); }
    if (ok) agies++;
    window.CJ_APPLIED[i] = { t: op.t, ok: ok, err: err };
    if (!ok) console.warn('[CJ_PATCH] op ' + (i + 1) + ' (' + op.t + ') sans effet' + (err ? ' : ' + err : ''), op);
  });
  console.log('[CJ_PATCH] ' + agies + '/' + ops.length + ' modification(s) appliquée(s)' + stamp);
})();
