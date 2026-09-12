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
    /* Deux canaux, et c'est nécessaire : sessionStorage sert l'aperçu dans
       l'iframe, mais un onglet ouvert avec rel="noopener" n'en hérite PAS —
       le diaporama lisait un état vide et affichait le deck d'origine. Le
       localStorage, lui, est partagé par tous les onglets de l'origine. */
    try { ops = JSON.parse(sessionStorage.getItem('cj_preview_ops') || 'null'); } catch (e) {}
    if (!ops) { try { ops = JSON.parse(localStorage.getItem('cj_preview_ops') || 'null'); } catch (e) {} }
    ops = ops || []; stamp = ' (aperçu éditeur)';
    /* JSON.parse('{}') passe le test ci-dessus mais n'a pas de forEach : le
       TypeError avortait l'IIFE entière — plus de typographie, CJ_APPLIED vide,
       et l'éditeur en concluait qu'aucune op n'était morte. */
    if (!Array.isArray(ops)) ops = [];
  } else {
    var P = window.CJ_PATCH;
    ops = (P && P.ops) || [];
    if (!Array.isArray(ops)) ops = [];
    stamp = (P && P.updated) ? ' — ' + P.updated : '';
  }
  window.CJ_APPLIED = [];

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
      /* Se replier en fin de deck quand la slide de référence n'existe plus
         plaçait la nouvelle slide en 53e position au lieu de la 5e — et le
         rapport disait « appliquée ». La fin de deck ne vaut que pour un add
         sans référence. */
      if (o.after) { var ref = slideOf(o.after); if (!ref) return false; ref.after(s); }
      else main.appendChild(s);
      return true;
    },
    order: function (o) {
      /* On résout TOUT avant de toucher au DOM. Réordonner puis lever laissait le
         deck à moitié remanié — les slides listées à la fin, les autres en tête —
         et rien ne le défaisait. */
      var trouvees = [], absentes = [];
      o.slides.forEach(function (l) { var s = slideOf(l); if (s) trouvees.push(s); else absentes.push(l); });
      if (absentes.length) throw new Error('ordre non appliqué, slides introuvables : ' + absentes.join(', '));
      /* Et une slide ajoutée à la source après coup n'est pas dans o.slides :
         elle resterait en tête du deck. Un ordre partiel n'est pas un ordre. */
      var total = main.querySelectorAll('section.slide').length;
      if (trouvees.length !== total)
        throw new Error('ordre non appliqué : ' + (total - trouvees.length) + ' slide(s) hors de la liste');
      /* « Couverture » porte class="slide active" en dur dans le deck, et le
         goSlide(0) d'ouverture ne retire la classe qu'à slides[0]. Après un
         réordonnancement, slides[0] n'est plus la couverture : deux sections
         restaient actives, superposées, et les premières slides devenaient
         invisibles derrière. On repart d'une ardoise nette — goSlide(0), appelé
         juste après par le script de navigation, en réactivera une. */
      main.querySelectorAll('section.slide.active').forEach(function (x) { x.classList.remove('active'); });
      trouvees.forEach(function (s) { main.appendChild(s); });
      return true;
    },

    /* Ops par sélecteur : portée au document entier, pas seulement aux slides.
       Indispensables pour le <title>, l'écran de chargement et les attributs. */
    seltext: function (o) { var n = document.querySelector(o.sel); if (!n) return false; n.innerHTML = o.html; return true; },
    selattr: function (o) { var n = document.querySelector(o.sel); if (!n) return false; n.setAttribute(o.name, o.value); return true; },
    title:   function (o) { var t = document.querySelector('head > title'); if (t) t.textContent = o.value; else document.title = o.value; return true; }
  };

  /* ---------- typographie française ----------
     Le deck a déjà un script anti-veuve (il soude le dernier mot d'un titre),
     mais rien pour la ponctuation. Or en français le deux-points, le
     point-virgule, le point d'exclamation, le point d'interrogation et les
     guillemets prennent une espace INSÉCABLE : sans elle, la ponctuation peut
     se retrouver seule en début de ligne. Sur un diplôme de design graphique,
     ça se voit.

     Fait ici plutôt que dans le fichier source : presentation.html pèse 81 Mo,
     chaque réécriture en ajoute un exemplaire à l'historique Git. */
  function typographie() {
    var IGNORE = { SCRIPT:1, STYLE:1, TEXTAREA:1, CODE:1, PRE:1, KBD:1, NOSCRIPT:1, SAMP:1, VAR:1, OPTION:1 };
    // Racine = body et non main : le libellé du pied de page vit hors de main et
    // n'était jamais typographié — apostrophe droite au pied, courbe dans la slide.
    var racine = document.body || main;
    var marche = document.createTreeWalker(racine, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        for (var p = n.parentNode; p && p !== racine; p = p.parentNode) {
          // nodeName d'un élément SVG est en minuscules : on écarte tout l'arbre
          if (IGNORE[p.nodeName] || p.nodeName === 'svg' || p.ownerSVGElement) return NodeFilter.FILTER_REJECT;
          /* Ceinture et bretelles : les passes différées ne tournent plus dans
             l'aperçu (voir plus bas), et celles qui restent précèdent l'armement
             des blocs. Si l'ordre changeait, réécrire le nodeValue d'un bloc en
             cours d'édition ramènerait le curseur en tête de paragraphe. */
          if (p.isContentEditable) return NodeFilter.FILTER_REJECT;
        }
        return /[ ][:;!?»]|«[ ]|[A-Za-zÀ-ÿ]'[A-Za-zÀ-ÿ]/.test(n.nodeValue)
          ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var n, touches = 0;
    while ((n = marche.nextNode())) {
      n.nodeValue = n.nodeValue
        .replace(/ ([:;!?»])/g, '\u00A0$1')                        // insécable avant
        .replace(/« /g, '«\u00A0')                                  // et après l'ouvrant
        // lookahead : sans lui, « n'y'a » n'était converti qu'à moitié par passe
        .replace(/([A-Za-zÀ-ÿ])'(?=[A-Za-zÀ-ÿ])/g, '$1\u2019');     // apostrophe courbe
      touches++;
    }
    return touches;
  }
  var agies = 0;
  ops.forEach(function (op, i) {
    var ok = false, err = null;
    /* H[op.t] trouvait « constructor », « toString »… sur le prototype : l'op
       était déclarée appliquée sans que rien ne se passe. */
    var f = Object.prototype.hasOwnProperty.call(H, op.t) ? H[op.t] : null;
    try { ok = f ? !!f(op) : false; }
    catch (e) { err = String(e && e.message || e); }
    if (ok) agies++;
    window.CJ_APPLIED[i] = { t: op.t, ok: ok, err: err };
    if (!ok) console.warn('[CJ_PATCH] op ' + (i + 1) + ' (' + op.t + ') sans effet' + (err ? ' : ' + err : ''), op);
  });
  if (ops.length) console.log('[CJ_PATCH] ' + agies + '/' + ops.length + ' modification(s) appliquée(s)' + stamp);

  /* En dernier, toujours : les textes réécrits par le calque méritent la même
     typographie que les autres, et un calque vide ne doit pas la priver.

     Rejouée ensuite : plusieurs slides construisent leur contenu en JavaScript
     (listes de logos, personas, légendes) après le passage de ce script. La
     passe est idempotente — une espace déjà insécable le reste — donc la
     rejouer ne coûte qu'un parcours de texte. */
  function passe(quand) {
    try {
      var t = typographie();
      if (t) console.log('[CJ_TYPO] ' + t + ' bloc(s) ajustés (' + quand + ')');
    } catch (e) { console.warn('[CJ_TYPO] passe typographique ignorée', e); }
  }
  passe('au chargement');
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', function () { passe('DOM prêt'); });
  /* Les relances servent au deck public, dont certaines parties se construisent
     en JavaScript après ce script. Dans l'aperçu, l'éditeur arme contenteditable
     au même moment : une passe qui tombe pendant la frappe déplace le curseur.
     On s'en abstient là où l'on écrit. */
  if (!/[?&]preview=1/.test(location.search)) {
    addEventListener('load', function () {
      [0, 600, 1800].forEach(function (d) { setTimeout(function () { passe('+' + d + 'ms'); }, d); });
    });
  }
})();
