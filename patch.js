/* Clovis Project — calque de modifications
   Écrit par l'éditeur (editeur.html) et par Claude. Appliqué au chargement du deck.
   Ne pas éditer à la main sauf si tu sais ce que tu fais. */
window.CJ_PATCH = {
 "version": 1,
 "updated": "2026-09-11",
 "ops": [
  { "t": "title", "value": "CHONG JI 冲击 — Oral de soutenance" },

  { "t": "seltext", "sel": ".loader-ctx .lc-s",
    "html": "Clovis · 2025 — 2026" },

  { "t": "seltext", "sel": "section.slide[data-lbl=\"Couverture\"] .eyebrow",
    "html": "<span class=\"dot\"></span>Oral de soutenance · M2 DADG" },

  { "t": "seltext", "sel": "section.slide[data-lbl=\"Couverture\"] .meta",
    "html": "<span>Clovis</span><span>2025 — 2026</span>" },

  { "t": "seltext", "sel": "section.slide[data-lbl=\"Qui suis-je\"] .who-meta",
    "html": "Clovis<br>M2 DADG" },

  { "t": "seltext", "sel": "section.slide[data-lbl=\"Merci\"] .meta",
    "html": "<span>Clovis — CHONG JI</span><span>M2 DADG · 2026</span>" },

  { "t": "selattr", "sel": "section.slide[data-lbl=\"Support secondaire · Billet\"] img[alt^=\"Souche\"]",
    "name": "alt", "value": "Souche — Clovis, porte G rang 11 place 140" }
 ]
};
