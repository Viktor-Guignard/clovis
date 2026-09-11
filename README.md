# CONTRE-CHAMP

**Arts martiaux et cinéma : un siècle d'influences croisées.**
Essai illustré, 208 pages — projet professionnel TS2, 2026 — 2027.

Ouvrir : https://viktor-guignard.github.io/clovis/

- `contre-champ.html` — la présentation du projet (18 slides)
- `editeur.html` — l'éditeur du deck
- `index.html` — page d'accueil

## Éditer le deck

https://viktor-guignard.github.io/clovis/editeur.html

Textes en place, remplacement d'images, ajout / duplication / suppression /
masquage / réordonnancement des slides, mise en forme (gras, italique, accent),
manipulation des blocs, rechercher-remplacer global, édition du HTML.
Un jeton GitHub à renseigner une fois par navigateur (Réglages).

`contre-champ.html` n'est jamais réécrit par l'éditeur : chaque modification
devient une « op » dans `patch.js`, appliquée au chargement. C'est ce qui permet
d'éditer à la main et de faire travailler Claude sur le même deck sans conflit,
et de révoquer une modification une par une.

- `patch.js` — le calque de modifications (seul fichier réécrit à l'enregistrement)
- `cj-early.js` — applique le calque dès l'en-tête (titre, écran de chargement)
- `cj-apply.js` — applique le calque aux slides, puis la typographie française
  (espaces insécables, apostrophes courbes)
- `bake.py` — fabrique `contre-champ-figee.html`, fichier unique et autonome
- `clovis-project.applescript` — source de l'app « Clovis Project »

## Clovis Project (l'app à deux fenêtres)

Ouvre d'un clic deux fenêtres Safari côte à côte sur l'écran principal :
l'éditeur à gauche, Claude à droite. Le partage s'adapte à l'écran — 63/37 sous
1500 pt (MacBook Air 13"), 58/42 au-delà.

### Installer sur un Mac

Ouvrir **Terminal** (⌘Espace, taper « Terminal ») et coller cette ligne :

```sh
cd ~/Desktop && curl -fsSLO https://raw.githubusercontent.com/Viktor-Guignard/clovis/main/clovis-project.applescript && osacompile -o "Clovis Project.app" clovis-project.applescript && rm clovis-project.applescript && open .
```

Glisser ensuite `Clovis Project.app` dans le Dock. Construire l'app localement
évite la quarantaine Gatekeeper : signée ad-hoc et non notarisée, une copie reçue
par mail ou AirDrop serait refusée au lancement.

## Archives

`presentation.html`, `hub-complet.html` et `appli.html` appartiennent au projet
CHONG JI, abandonné. Conservés le temps de décider de leur sort ; ils ne sont
plus liés depuis l'accueil.

Clovis — TS2 · 2026 — 2027
