-- CHONG JI — Atelier
-- Ouvre l'établi de travail : l'éditeur du deck à gauche, Claude à droite,
-- deux vraies fenêtres Safari calées chacune sur sa moitié de l'écran principal.
--
-- Recompiler après modification :
--   osacompile -o "CHONG JI — Atelier.app" atelier.applescript

use framework "Foundation"
use framework "AppKit"
use scripting additions

set editeurURL to "https://viktor-guignard.github.io/clovis/editeur.html"
set claudeURL to "https://claude.ai/code"

-- part de l'écran donnée à l'éditeur (0.58 = 58 %) : c'est lui qui affiche les slides
set partEditeur to 0.58

-- Géométrie de l'ÉCRAN PRINCIPAL uniquement (pas l'étendue de tous les écrans),
-- zone utile : sous la barre de menus, hors Dock.
set ecran to current application's NSScreen's mainScreen()
set cadre to ecran's frame()
set utile to ecran's visibleFrame()
set hTotal to item 2 of item 2 of cadre
set xU to item 1 of item 1 of utile
set yU to item 2 of item 1 of utile
set wU to item 1 of item 2 of utile
set hU to item 2 of item 2 of utile

-- Cocoa compte depuis le bas, AppleScript depuis le haut : on convertit.
set bordGauche to xU as integer
set bordHaut to (hTotal - (yU + hU)) as integer
set bordDroit to (xU + wU) as integer
set bordBas to (bordHaut + hU) as integer
set coupure to (bordGauche + (wU * partEditeur)) as integer

tell application "Safari"
	activate

	make new document with properties {URL:editeurURL}
	delay 0.6
	set bounds of window 1 to {bordGauche, bordHaut, coupure, bordBas}

	make new document with properties {URL:claudeURL}
	delay 0.6
	set bounds of window 1 to {coupure, bordHaut, bordDroit, bordBas}
end tell
