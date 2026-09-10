# CHONG JI 冲击

Menu d'accès : **la présentation** (deck complet de soutenance) et **l'appli iPad du jury**
(compagnon de soutenance).

Ouvrir : https://viktor-guignard.github.io/clovis/chongji-hub/

- `index.html` — menu d'accueil (2 cartes)
- `presentation.html` — deck complet (mémoire, projet, système graphique)
- `hub-complet.html` — compagnon iPad du jury : galerie 3D, charte, mockups, billet, festival + AR
- `appli.html` — application mobile du festival (bonus, non lié depuis le menu)

## Éditer le deck

`editeur.html` — éditeur type Google Slides pour `presentation.html`, avec Claude intégré.
Ouvrir : https://viktor-guignard.github.io/clovis/editeur.html

`presentation.html` n'est jamais réécrit. Toutes les modifications sont des « ops »
enregistrées dans `patch.js`, que `cj-apply.js` applique au chargement du deck.
C'est ce qui permet à Viktor et à Claude d'éditer le même deck sans se marcher dessus,
et qui garde le dépôt léger malgré un fichier source de 81 Mo.

- `editeur.html` — l'éditeur (textes, images, ajout/suppression/ordre des slides) + panneau Claude
- `patch.js` — le calque de modifications (seul fichier réécrit à chaque enregistrement)
- `cj-apply.js` — applique le calque au chargement
- `bake.py` — fabrique `presentation-soutenance.html` : un fichier unique et autonome, hors ligne
- `atelier.applescript` — source de l'app « CHONG JI — Atelier »

## L'atelier (l'app à deux fenêtres)

Ouvre d'un clic les deux fenêtres Safari côte à côte sur l'écran principal :
l'éditeur à gauche (58 %), Claude à droite (42 %). Dock et barre de menus pris
en compte ; sur plusieurs écrans, seul l'écran principal est utilisé.

Pour l'installer sur un Mac :

```sh
osacompile -o "CHONG JI — Atelier.app" atelier.applescript
```

Puis glisser l'app dans le Dock. Au premier lancement, macOS demande
l'autorisation de piloter Safari — c'est normal, il faut l'accorder.
Le partage gauche/droite se règle avec `partEditeur` en haut du script.

Viktor Guignard — M2 DADG · ESDAC Paris
