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

- `editeur.html` — l'éditeur (textes, images, ajout/suppression/ordre des slides)
- `patch.js` — le calque de modifications (seul fichier réécrit à chaque enregistrement)
- `cj-apply.js` — applique le calque au chargement
- `bake.py` — fabrique `presentation-soutenance.html` : un fichier unique et autonome, hors ligne
- `clovis-project.applescript` — source de l'app « Clovis Project »

## Clovis Project (l'app à deux fenêtres)

Ouvre d'un clic les deux fenêtres Safari côte à côte sur l'écran principal :
l'éditeur du deck à gauche, Claude à droite. Dock et barre de menus pris en
compte ; sur plusieurs écrans, seul l'écran principal est utilisé. Le partage
s'adapte à la taille de l'écran — 63/37 sous 1500 pt (MacBook Air 13"),
58/42 au-delà — parce que le rail de slides occupe une largeur fixe alors que
Claude se resserre sans gêne.

### Installer sur un Mac

Ouvrir **Terminal** (⌘Espace, taper « Terminal ») et coller cette ligne :

```sh
cd ~/Desktop && curl -fsSLO https://raw.githubusercontent.com/Viktor-Guignard/clovis/main/clovis-project.applescript && osacompile -o "Clovis Project.app" clovis-project.applescript && rm clovis-project.applescript && open .
```

Elle télécharge le script, fabrique l'app sur le Bureau et ouvre le dossier.
Glisser ensuite `Clovis Project.app` dans le Dock.

Construire l'app localement évite la quarantaine Gatekeeper : elle est signée
ad-hoc et non notarisée, donc une copie reçue par mail ou AirDrop serait refusée
au lancement. Recoller la même ligne plus tard met l'app à jour.

Depuis un clone du dépôt, la version courte suffit :

```sh
osacompile -o "Clovis Project.app" clovis-project.applescript
```

Puis glisser l'app dans le Dock. Au premier lancement, macOS demande
l'autorisation de piloter Safari — c'est normal, il faut l'accorder.
Le partage se règle avec `partEditeur` en haut du script.

Viktor Guignard — M2 DADG · ESDAC Paris
