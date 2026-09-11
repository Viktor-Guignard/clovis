#!/usr/bin/env python3
"""Fabrique la version figée : un fichier unique, autonome, hors ligne.

presentation.html charge trois fichiers par balise <script src> — patch.js et
cj-early.js dans l'en-tête, cj-apply.js après les slides. Ici on remplace ces
balises par leur contenu inline : le résultat est un seul fichier qui applique
le calque au chargement, sans réseau ni fichier voisin.

    python3 bake.py [sortie.html]
"""
import io, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'presentation.html')
OUT  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'presentation-figee.html')

def lire(nom):
    with io.open(os.path.join(HERE, nom), encoding='utf-8') as f:
        return f.read()

def inline(*fichiers):
    return '\n'.join('<script>\n%s\n</script>' % lire(f) for f in fichiers)

REMPLACEMENTS = [
    ('<script src="patch.js"></script>\n<script src="cj-early.js"></script>',
     inline('patch.js', 'cj-early.js')),
    ('<script src="cj-apply.js"></script>',
     inline('cj-apply.js')),
]

with io.open(SRC, encoding='utf-8', errors='surrogateescape', newline='') as f:
    html = f.read()

for cible, remplacement in REMPLACEMENTS:
    if cible not in html:
        sys.exit("Balise attendue introuvable dans presentation.html :\n  %s\n"
                 "Le fichier a-t-il été modifié à la main ?" % cible.split('\n')[0])
    html = html.replace(cible, remplacement, 1)

with io.open(OUT, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
    f.write(html)

nb = lire('patch.js').count('"t":')
print('%s\n  %.1f Mo — %d modification(s) intégrée(s) — %s'
      % (OUT, os.path.getsize(OUT) / 1048576.0, nb,
         datetime.datetime.now().strftime('%d/%m/%Y %H:%M')))
print('  Fichier unique : il fonctionne hors ligne, sur clé USB, sur iPad.')
