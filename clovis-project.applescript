-- Clovis Project
-- Ouvre l'établi : l'éditeur du deck à gauche, Claude à droite,
-- deux vraies fenêtres Safari calées sur l'écran principal.
--
-- Recompiler après modification :
--   osacompile -o "Clovis Project.app" clovis-project.applescript

use framework "Foundation"
use framework "AppKit"
use scripting additions

set editeurURL to "https://viktor-guignard.github.io/clovis/editeur.html"
set claudeURL to "https://claude.ai/code"

-- Géométrie de l'ÉCRAN PRINCIPAL seulement (pas l'étendue de tous les écrans),
-- zone utile : sous la barre de menus, hors Dock.
set ecran to current application's NSScreen's mainScreen()
set cadre to ecran's frame()
set utile to ecran's visibleFrame()
set hTotal to item 2 of item 2 of cadre
set xU to item 1 of item 1 of utile
set yU to item 2 of item 1 of utile
set wU to item 1 of item 2 of utile
set hU to item 2 of item 2 of utile

-- Part donnée à l'éditeur. Sur un petit écran (MacBook Air 13"), il lui en faut
-- davantage : son rail de slides occupe une largeur fixe, alors que Claude,
-- qui n'est qu'une colonne de texte, se resserre sans gêne.
if wU < 1500 then
	set partEditeur to 0.63
else
	set partEditeur to 0.58
end if

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
