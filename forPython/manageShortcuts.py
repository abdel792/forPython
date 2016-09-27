# -*- coding: utf-8 -*-
import sixpad as sp
import os
import re
import inspect
import subprocess
from threading import Timer

searchedText = ""

alert = sp.window.alert

def sayText(s, stopSpeech = False):
	""" si autorisé, fait lire un texte par la synthèse vocale """
	flag = True
	try:
		flag = sp.window.menus["accessibility"]["vocalSynthesis"].checked
	except: pass
	# si synthèse autorisée
	if flag == True:
		sp.say(s, stopSpeech)
	# end if
# end def

def delayMsg2():
	# retardement de la lecture d'un message
	global tmr, msg
	sayText(msg)
	# relance du timer 
	# tmr.run() # pas nécessaire
# end def

def delayMsg1(s, delay):
	global msg
	msg = s
	tmr = Timer(delay, delayMsg2)
	tmr.start() # lancement
# end def
def readFile(filePath, _mode = 'r'):
	# lit et renvoi le contenu d'un fichier texte
	fil = open(filePath, _mode)
	s = fil.read()
	fil.close() # Fermeture du fichier
	return s
# end def

def writeFile(filePath, s, _mode = 'w'):
	# Ecrit dans un fichier
	fil = open(filePath, _mode)
	fil.write(s)
	fil.close() # Fermeture du fichier
# end def

def getCurModuleDir():
	# renvoi le chemin vers le dossier contenant le script courant
	path = inspect.getfile(inspect.currentframe())
	return os.path.dirname(path)
# end def-

def getModuleRef(modPath):
	# renvoi le module de 6pad à partir de son chemin
	lst = modPath.split("\\")
	appPath = sp.appdir
	# quel répertoire ? (lib ou plugins ?)
	rep = ""
	if modPath.find(os.path.join(appPath, "lib")) >= 0: rep = "lib"
	elif modPath.find(os.path.join(appPath, "plugins")) >= 0: rep = "plugins"
	else: return ""
	limit = len(os.path.join(appPath, rep).split("\\"))
	lst = lst[limit:]
	return ".".join(lst)
# end def

def getValues(item):
	# renvoi les valeurs liées à l'item
	lst = []
	lst = item.value.split("|||")
	index = int(lst[0])
	label = lst[1]
	accelerator = lst[2]
	return index, label, accelerator
# end def

def onAction(dialog, item):
	# après entrer ou au double click
	try: modifyShortcut(item)
	except: sp.window.messageBeep(0)
# end def

def onSelect(dialog, item):
	# à la sélection d'un noeud
	i = 0
	return
	# on va faire dire sa position par rapport aux autres noeuds
	parent = item.parentNode
	if parent != None:
		lst = parent.childNodes
	else:
		lst = dialog.root.childNodes
	# end if
	# la position du noeud courant
	i = - 1
	for e in lst:
		i = i + 1
		if lst[i].value == item.value: break
	# end for
	# le nombre total d'éléments
	n = len(lst)
	# lecture retardée
	s = str(i + 1) + "/" + str(n)
	delayMsg1(s, 0.5)
# end def

def onExpand(dialog, item):
	# à l'expension d'un noeud
	sayText(item.text, False)
	try: sayText(str(len(item.childNodes)) + " items")
	except: pass
	return True
# end def

def onContextMenu(dialog, item):
	# au menu contextuel sur un noeud
	# constitution de la liste des éléments du menu contextuel
	lst = ["Modifier le raccourci-clavier", "Restaurer le raccourci-clavier d'origine", "Rechercher...", "Rechercher suivant", "Rechercher précédent"]
	# affichage du menu contextuel
	i = sp.window.showPopupMenu(lst)
	if i == 0:
		modifyShortcut(item)
	elif i == 1:
		reinitializeShortcut(item)
	elif i == 2:
		search()
	elif i == 3:
		searchNext()
	elif i == 4:
		searchPrior()
	# end if
	dialog.focus()
# end def

def getMenus():
	# parcours et recencement des menus principaux
	global menus, photography
	menus = []
	photography = []
	# parcours des menus principaux
	for i in range(0, sp.window.menus.length):
		m = sp.window.menus[i]
		getSubMenus(m)
	# end for
	return menus
# end def

def getSubMenus(mnu):
	# Parcours et recencement des sous-menus
	global menus, photography
	for i in range(0, mnu.length):
		m = mnu[i]
		if m.submenu == False:
			menus.append(m)
			photography.append(m.accelerator)
		# end if
		if m.length > 0 and m.label != 'Fichiers r&écents': getSubMenus(m)
	# end for
# end def

def search():
	# recherche dans la liste
	global searchedText
	s = sp.window.prompt("Tapez le texte à rechercher dans cette liste", "Texte à rechercher", searchedText)
	if s == "" or s == None: return
	searchedText = s.lower()
	searchNext()
# end def

def searchNext():
	# rechercher suivant
	global tv, searchedText
	lst = tv.root.childNodes
	pos = 0
	try: pos = int(tv.selectedItem.value)
	except: pass
	for i in range(pos + 1, len(lst)):
		s = lst[i].text.lower()
		if s.count(searchedText) > 0:
			sayText("Suivant")
			lst[i].select()
			return
		# end if
	# end for
	sp.window.messageBeep(0)
	sayText("Aucune occurence suivante")
# end def

def searchPrior():
	# rechercher précédent
	global tv, searchedText
	lst = tv.root.childNodes
	pos = 0
	try: pos = int(tv.selectedItem.value)
	except: pass
	for i in range(pos - 1, 0, - 1):
		s = lst[i].text.lower()
		if s.count(searchedText) > 0:
			sayText("Précédent")
			lst[i].select()
			return
		# end if
	# end for
	sp.window.messageBeep(0)
	sayText("Aucune occurence précédente")
# end def

def getSavedShortcuts():
	# recencement des références de raccourcis sauvegardés
	global shortcuts, iniFilePath
	separator = "|||"
	# le contenu du fichier ini
	s = readFile(iniFilePath)
	if s == "": return shortcuts
	shortcuts = [] # réinitialisation
	lines = re.findall("[^\\r\\n]+", s)
	for e in lines:
		if e.count(separator) > 0:
			lst = e.split(separator)
			label = lst[0]
			name = lst[1]
			accelerator = lst[2]
			validity = False
			# ajout à la liste globale
			shortcuts.append((label, name, accelerator, validity))
		# end if
	# end for
	return shortcuts
# end def

def saveShortcuts():
	# sauvegarde les raccourcis clavier
	# mais uniquement ceux valides (ayant été trouvés)
	global shortcuts, iniFilePath
	separator = "|||"
	# constitution du texte à sauvegarder
	s = ""
	if len(shortcuts) > 0:
		for(label, name, accelerator, validity) in shortcuts:
			if validity == True: s = s + label + separator + name + separator + accelerator + "\r\n"
		# end for
	# end if
	writeFile(iniFilePath, s)
# end def

def assignSavedShortcuts():
	# restoration et assignation des raccourcis clavier de menus
	global menus, shortcuts
	# recencement des raccourcis sauvegardés
	shortcuts = getSavedShortcuts()
	# si aucun raccourci assigné
	if len(shortcuts) == 0: return
	# parcours et comparaisons
	for m in menus:
		for i in range(0, len(shortcuts)):
			label, name, accelerator, validity = shortcuts[i]
			# astuce pour éviter un bug
			if accelerator == "": accelerator = "F15"
			if(m.name != "" and m.name == name) or(m.name == "" and m.label == label):
				try:
					m.accelerator = accelerator
					shortcuts[i] = (m.label, m.name, accelerator, True)
				except: pass
			# end if
		# end for
	# end for
# end def

def changeShortcut(index, s):
	# application du changement dans un élément de menu
	global menus, shortcuts, tv
	m = menus[index]
	if m.accelerator.lower() == s.lower(): return True
	if s == "": s = "F15"
	s = s.upper() # raccourci doit être en majuscule
	# Application du changement
	s0 = m.accelerator
	m.accelerator = s
	if s == "F15": s = ""
	# si le changement a été refusé
	if m.accelerator.lower() == s0.lower(): return False
	# modification dans la liste globale
	flag = False
	for i in range(0, len(shortcuts)):
		label, name, accelerator, validity = shortcuts[i]
		if(m.name != "" and m.name == name) or(m.name == "" and m.label == label):
			shortcuts[i] = (label, name, s, True)
			flag = True
			break
		# end if
	# end for
	if flag == False: shortcuts.append((m.label, m.name, s, True))
	# modification dans la liste visible
	text = m.label.replace("&", "") + "\t" + m.accelerator
	tv.root.childNodes[index].text = text
	return True
# end def

def modifyShortcut(item):
	# modification d'un raccourci liés à un élément de menu
	global menus, shortcuts
	i = int(item.value)
	index = i
	m = menus[i]
	# affichage du prompt de modification
	s = sp.window.prompt("Raccourci:", "Modifier le raccourci", m.accelerator)
	if s == None: return
	s = s.replace(" ", "") # élimination d'éventuels caractères d'espacement
	# si raccourci non vide
	if s != "":
		# Vérification que le raccourci clavier n'est pas déjà utilisé
		s = s.lower()
		for i in range(0, len(menus)):
			if s == menus[i].accelerator.lower() and menus[i] != m:
				# demande de confirmation de remplacement
				if sp.window.confirm("Le raccourci " + menus[i].accelerator + " est déjà utilisé par le menu " + menus[i].label.replace("&", "") + "\nVoulez-vous le remplacer ?", "Raccourci déjà utilisé") < 1: return
				# on va non seulement remplacer celui-ci mais d'éventuels autre avec le même raccourci
				for j in range(i, len(menus)):
					if s == menus[j].accelerator.lower() and menus[j] != m:
						changeShortcut(j, "")
					# end if
				# end for
				break
			# end if
		# end for
	# end if
	if changeShortcut(index, s) == False:
		alert("La modification du raccourci-clavier a rencontré une erreur\nIl est possible que le raccourci tapé ne soit pas valide.\nVeuillez recommencer en faisant attention de n'y insérer aucun caractère d'espacement.", "Erreur de modification")
		return
	# end if
	saveShortcuts() # enregistrement des changements
# end def

def reinitializeShortcut(item):
	# réinitialise un raccourci clavier
	global menus, photography, tv
	# on retrouve le vrai index dans la liste des index conservée
	i = int(item.value)
	# restoration du raccourcis tel que photographié au départ
	s = photography[i]
	if s == "": s = "F15"
	s0 = menus[i].accelerator
	menus[i].accelerator = s
	if s == "F15": s = ""
	# si il n'y a pas eu de changement
	if s0 == menus[i].accelerator:
		alert("Echec de réinitialisation du raccourci-clavier lié à cet élément de menu", "Erreur de réinitialisation")
		return
	# end if
	# retrait de ce raccourci de la liste des configurations gardée en mémoire
	for j in range(0, len(shortcuts)):
		label, name, accelerator, validity = shortcuts[j]
		if menus[i].name == name or(menus[i].name == "" and menus[i].label == label):
			del shortcuts[j]
			break
		# end if
	# end for
	# modification dans la liste visible
	text = menus[i].label.replace("&", "") + "\t" + menus[i].accelerator
	item.text = text
	# élimination de ce raccourci chez tous les autres qui pourraient le posséder
	for j in range(0, len(menus)):
		if menus[j] != menus[i]:
			if menus[j].accelerator == menus[i].accelerator:
				changeShortcut(j, "")
			# end if
		# end if
	# end for
	# sauvegarde des changements
	saveShortcuts()
# end def

def reinitializeShortcuts():
	# réinitialise tous les raccourcis clavier
	global shortcuts, iniFilePath, menus, photography
	if sp.window.confirm("Êtes-vous sûr de vouloir réinitialiser la configuration des raccourcis clavier ?", "Réinitialiser les raccourcis clavier") == 0: return
	writeFile(iniFilePath, "")
	shortcuts = []
	# parcours et restoration à partir des photographies
	for i in range(0, len(menus)):
		menus[i].accelerator = photography[i]
	# end for
	alert("Les raccourcis clavier de menus ont bien été réinitialiser.", "Succès de réinitialisation")
# end def

def manageMenuShortcuts():
	# affiche l'interface de gestion des raccourcis
	global menus, tv
	tv = qc.TreeViewDialog.open(title = "Gestion des raccourcis-clavier", hint = "Gérez les raccourcis-clavier de menus.", modal = False, multiple = False, okButtonText = "", cancelButtonText = "Fermer")
	# remplissage
	i = - 1
	for m in menus:
		i = i + 1
		text = m.label.replace("&", "") + "\t" + m.accelerator
		value = str(i)
		tv.root.appendChild(text, value)
	# end for
	# ajout d'évènements
	tv.addEvent("action", onAction)
	tv.addEvent("expand", onExpand)
	tv.addEvent("contextMenu", onContextMenu)
	tv.addEvent("select", onSelect)
# end def

def exportShortcutsConfig():
	""" exportation des configuration de raccourci clavier """
	global iniFilePath
	# demande de l'emplacement de sauvegarde
	savePath = sp.window.saveDialog(file = os.path.basename(iniFilePath), title = "Désigner l'emplacement ou exporter les configurations de raccourcis clavier")
	if savePath == None or savePath == "": return
	# sauvegarde
	try:
		writeFile(savePath, readFile(iniFilePath))
	except:
		alert("La sauvegarde des configurations de raccourcis clavier a rencontré une erreur")
	# end try
# end def

def importShortcutsConfig():
	""" importation des configuration de raccourci clavier """
	global iniFilePath
	# demande de l'emplacement de sauvegarde
	savePath = sp.window.openDialog(title = "Désigner le fichier dans lequel ont été sauvegardées les configurations de raccourci clavier")
	if savePath == None or savePath == "": return
	# restauration
	try:
		if sp.window.confirm("Vous êtes sur le point de restaurer vos configurations de raccourcis clavier à partir du fichier '" + savePath + "'.\nVoulez-vous continuer ?", "Restauration des raccourci clavier") >= 1:
			writeFile(iniFilePath, readFile(savePath))
		# end if
	except:
		alert("La sauvegarde des configurations de raccourcis clavier a rencontré une erreur")
	# end try
# end def

def loadManageShortcutsTools():
	# Création des éléments globaux
	global menus, shortcuts, photography, iniFilePath
	menus = []
	shortcuts = []
	photography = []
	# chemin du fichier contenant les paramètres personnalisés des raccourcis
	iniFilePath = os.path.join(sp.appdir, "manageShortcuts.ini")
	formalIniFilePath = os.path.join(getCurModuleDir(), "manageShortcuts.ini")
	# si les paramètres se trouvent à l'ancien emplacement
	if os.path.isfile(iniFilePath) == False and os.path.isfile(formalIniFilePath) == True:
		# on les transvase
		writeFile(iniFilePath, readFile(formalIniFilePath))
	# end if
	# création des éléments de menus propres à la gestion des raccourci clavier
	# dans le menu outils
	menuTools = sp.window.menus["tools"]
	global menuModifyShortcuts
	if menuTools["shortcuts"] != None:
		menuModifyShortcuts = menuTools["shortcuts"]
	else:
		i = menuTools.length - 1
		menuModifyShortcuts = menuTools.add(label = "&Raccourcis claviers", submenu = True, name = "shortcuts", index = i)
		menuModifyShortcuts.add(label = "Gestion des ra&ccourcis-clavier de menus...", action = manageMenuShortcuts, name = "manageMenuShortcuts")
		menuModifyShortcuts.add(label = "&Exporter les configurations de raccourcis-clavier", action = exportShortcutsConfig, name = "exportShortcutsConfig")
		menuModifyShortcuts.add(label = "&Importer les configurations de raccourcis-clavier", action = importShortcutsConfig, name = "importShortcutsConfig")
		menuModifyShortcuts.add(label = "Restaurer tous les r&accourcis-clavier d'origine", action = reinitializeShortcuts, name = "reinitializeShortcuts")
	# end if
	
	# recencement et photographie de l'ensemble des menus
	menus = getMenus()
	# assignation des raccourcis sauvegardés
	assignSavedShortcuts()
# end def

def unloadManageShortcutsTools():
	# élimination des outils spécifiques du manageShortcuts
	global menuModifyShortcuts
	try: menuModifyShortcuts.remove()
	except: pass
# end def

# importation du control arborescence
try:
	import qc6paddlgs as qc
except:
	try:
		modName = getModuleRef(getCurModuleDir()) + "." + "qc6paddlgs"
		exec("import " + modName + " as qc")
	except:
		sp.window.alert("Le fichier qc6paddlg.pyd est introuvable.\nVeuillez le copier à la racine du dossier plugins pour que ce module puisse fonctionner correctement.", "Erreur dans le module manageShortcuts")
	# end try
# end try

# si vous voulez ce module indépendant du forPython,
# veuillez décommenter la ligne suivante.
# loadManageShortcutsTools()
