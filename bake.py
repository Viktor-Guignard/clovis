#!/usr/bin/env python3
"""Fabrique la version « soutenance » : un fichier unique, autonome, hors ligne.

presentation.html charge patch.js et cj-apply.js par balise <script src>. Ici on
remplace ces deux balises par leur contenu inline : le résultat est un seul
fichier qui applique le calque au chargement, sans réseau ni fichier voisin.

    python3 bake.py [sortie.html]
"""
import io, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'presentation.html')
OUT  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'presentation-soutenance.html')

def lire(nom):
    with io.open(os.path.join(HERE, nom), encoding='utf-8') as f:
        return f.read()

patch, applic = lire('patch.js'), lire('cj-apply.js')
cible = '<script src="patch.js"></script>\n<script src="cj-apply.js"></script>'
inline = '<script>\n%s\n</script>\n<script>\n%s\n</script>' % (patch, applic)

with io.open(SRC, encoding='utf-8', errors='surrogateescape', newline='') as f:
    html = f.read()

if cible not in html:
    sys.exit("Les balises <script src> attendues sont introuvables dans presentation.html.\n"
             "Le fichier a-t-il été modifié à la main ?")

html = html.replace(cible, inline, 1)
with io.open(OUT, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
    f.write(html)

nb = patch.count('"t":')
print("%s\n  %.1f Mo — %d modification(s) intégrée(s) — %s"
      % (OUT, os.path.getsize(OUT)/1048576.0, nb,
         datetime.datetime.now().strftime('%d/%m/%Y %H:%M')))
print("  Fichier unique : il fonctionne hors ligne, sur clé USB, sur iPad.")
