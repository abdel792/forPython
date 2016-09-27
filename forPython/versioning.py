# -*- coding: utf-8 -*-

# extension de création d'un système de gestion de versions d'un fichier
# pour le 6pad++
# par Yannick Daniel Youalé
# mailtoloco2011@gmail.com
# mai 2016

# quelques conventions d'enregistrement des versions:
# la version sauvegardée l'est dans un fichier portant le même nom que le fichier courant, 
# mais en plus avec l'extension .save, et se trouve dans le même dossier.
# les textes des versions y sont séparées par le séparateur déclaré ci-dessous,
# et chaque versions  comporte trois informations:
# * la date et l'heure de sa sauvegarde (les 19 premiers caractères);
# * le nom donnée à la version (du caractère21 au caractère 50);
# * le texte sauvegardé (à partir du 52ème caractère jusqu'à la fin de la portion.

# importations
import sixpad as sp
import os
import time

alert = sp.window.alert

# le séparateur des enregistrements
separator = "fklru'fuYYDà'_Bç" + "tuejk"

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

def getMenuIndex(mnuName, mnuParent):
	# renvoi la position/index d'un menu par son name, relativement à son parent
	s = ""
	for i in range(mnuParent.length):
		if mnuParent[i].name == mnuName: return i
		s = s + mnuParent[i].name + ", "
	# end for
	alert(s)
	return - 1
# end def

def readFile(filePath, _mode = 'r'):
	# lit et renvoi le contenu d'un fichier texte
	s = ""
	try:
		fil = open(filePath, _mode)
		s = fil.read()
		fil.close() # Fermeture du fichier
	except: pass
	return s
# end def

def writeFile(filePath, s, _mode = 'w'):
	# Ecrit dans un fichier
	fil = open(filePath, _mode)
	fil.write(s)
	fil.close() # Fermeture du fichier
# end def

def getDisplayedText(page = None):
	# recueille le texte courant et le formatte de façon standard
	if page == None: page = sp.window.curPage
	n = page.lineCount
	rt = "\r\n" # retour à la ligne standard
	s = page.line(0)
	for i in range(1, n):
		s = s + rt + page.line(i)
	# end for
	return s
# end def

def displayText(s, page = None):
	# affiche le texte après déformattage
	if page == None: page = sp.window.curPage
	page.text = ""
	page.insert(0, s)
	return
	rt = "\n"
	lines = s.split(rt)
	# effacement du texte courant
	page.text = ""
	# insertion ligne par ligne du nouveau texte
	if len(lines) > 0:
		for i in range(0, len(lines)):
			page.insert(i, lines[i])
		# end for
	# end if
# end def

def getVersionItemName(s):
	# extrait et formatte le nom à afficher d'une version
	d = 0.0
	d = len(s) / 1024
	return s[20: 50] + " " + s[0: 19] + " " + str(d) + " ko"
# end def

def saveNewVersion(prompt = True):
	# sauvegarde d'une nouvelle version
	global separator
	path = sp.window.curPage.file
	if path == "":
		sp.window.messageBeep()
		return
	# end if
	# on demande un nom à donner à la version sauvegardée
	name = sp.window.prompt("Donner un nom de 30 caractères max à cette version", "Nom donné à la version", "Nouvelle version")
	if len(name) > 30: name = name[0: 31]
	elif len(name) < 30: name = name + (" " * (30 - len(name)))
	path = path + ".save"
	# recueillement du contenu actuel du fichier de sauvegarde
	s = readFile(path)
	# la date et l'heure de la sauvegarde
	t = time.strftime("%Y/%m/%d %H-%M-%S")
	# le texte à sauvegarder
	# txt = sp.window.curPage.text
	txt = getDisplayedText()
	# jointure
	txt = t + " " + name + " " + txt
	# ajout
	s = txt + separator + s
	# écriture
	writeFile(path, s)
	if prompt == True:
		sp.window.alert("La version a été sauvegardée avec succès.", "Sauvegarde succesfull")
		# sp.window.messageBeep(64)
	# end if
# end def

def saveInFormalVersion():
	# sauvegarde du texte courant dans une ancienne version
	global separator
	lst = []
	path = sp.window.curPage.file
	if path == "":
		sp.window.messageBeep(0)
		return
	# end if
	path = path + ".save"
	if os.path.isfile(path) == False:
		sp.window.messageBeep(0)
		return
	# end if
	# le texte du fichier de sauvegarde
	s = readFile(path)
	# vérification de la présence du séparateur
	if s.count(separator) == 0:
		sp.window.messageBeep(0)
		return
	# end if
	# décomposition dans une liste suivant séparateurs
	lst = s.split(separator)
	del lst[len(lst) - 1] # le dernier élément est toujours vide, on le supprime
	# création de la liste des dates et noms de version uniquement
	lstDate = []
	for e in lst:
		lstDate.append(getVersionItemName(e))
	# end for
	# affichage
	i = sp.window.choice("Anciennes versions du document", "Enregistrer dans une ancienne version", lstDate, 0)
	if i < 0: return
	if sp.window.confirm("Vous êtes sur le point de mettre à jour une ancienne version sauvegardée de ce document.\n Êtes-vous sûr de vouloir continuer ?", "Enregistrement dans une ancienne version") == 0: return
	s = lst[i]
	# lst[i] = s[0: 50] + " " + sp.window.curPage.text
	lst[i] = s[0: 50] + " " + getDisplayedText()
	# reconstitution et sauvegarde
	s = separator.join(lst) + separator
	writeFile(path, s)
	sp.window.messageBeep(64)
# end def

def restoreVersion():
	# Restauration d'une version sauvegardée à la place du texte courant
	global separator
	lst = []
	path = sp.window.curPage.file
	if path == "":
		sp.window.messageBeep(0)
		return
	# end if
	path = path + ".save"
	if os.path.isfile(path) == False:
		sp.window.messageBeep(0)
		return
	# end if
	# le texte du fichier de sauvegarde
	s = readFile(path)
	# vérification de la présence du séparateur
	if s.count(separator) == 0:
		sp.window.messageBeep(0)
		return
	# end if
	# décomposition dans une liste suivant séparateurs
	lst = s.split(separator)
	del lst[len(lst) - 1] # le dernier élément est toujours vide, on le supprime
	# création de la liste des dates et noms de version uniquement
	lstDate = []
	for e in lst:
		lstDate.append(getVersionItemName(e))
	# end for
	# affichage
	i = sp.window.choice("Anciennes versions du document", "Versions", lstDate, 0)
	if i < 0: return
	if sp.window.confirm("Vous êtes sur le point de restaurer une ancienne version de ce document.\n Voulez-vous en même temps sauvegarder la version actuelle ?", "Restauration de version") == 1:
		saveNewVersion(prompt = False)
	# end if
	s = lst[i][51:]
	# sp.window.curPage.text = s
	displayText(s)
# end def

def openVersionInNewPage():
	# ouvre une ancienne version dans un nouvel onglet
	global separator
	lst = []
	path = sp.window.curPage.file
	if path == "":
		sp.window.messageBeep(0)
		return
	# end if
	path = path + ".save"
	if os.path.isfile(path) == False:
		sp.window.messageBeep(0)
		return
	# end if
	# le texte du fichier de sauvegarde
	s = readFile(path)
	# vérification de la présence du séparateur
	if s.count(separator) == 0:
		sp.window.messageBeep(0)
		return
	# end if
	# décomposition dans une liste suivant séparateurs
	lst = s.split(separator)
	del lst[len(lst) - 1] # le dernier élément est toujours vide, on le supprime
	# création de la liste des dates et noms de version uniquement
	lstDate = []
	for e in lst:
		lstDate.append(getVersionItemName(e))
	# end for
	# affichage
	i = sp.window.choice("Anciennes versions du document", "Ouvrir une version dans un nouvel onglet", lstDate, 0)
	if i < 0: return
	s = lst[i][51:]
	# création du nouvel onglet
	page = sp.window.new()
	# page.text = s
	displayText(s, page)
	page.focus()
# end def

def deleteVersion():
	# Suppression d'une version sauvegardées
	global separator
	lst = []
	path = sp.window.curPage.file
	if path == "":
		sp.window.messageBeep(0)
		return
	# end if
	path = path + ".save"
	if os.path.isfile(path) == False:
		sp.window.messageBeep(0)
		return
	# end if
	# le texte du fichier de sauvegarde
	s = readFile(path)
	# vérification de la présence du séparateur
	if s.count(separator) == 0:
		sp.window.messageBeep(0)
		return
	# end if
	# décomposition dans une liste suivant séparateurs
	lst = s.split(separator)
	del lst[len(lst) - 1] # le dernier élément est toujours vide, on le supprime
	# création de la liste des dates et noms de version uniquement
	lstDate = []
	for e in lst:
		lstDate.append(getVersionItemName(e))
	# end for
	# affichage
	i = sp.window.choice("Anciennes versions du document", "Suppression d'une ancienne version", lstDate, 0)
	if i < 0: return
	if sp.window.confirm("Vous êtes sur le point de supprimée une ancienne version sauvegardée de ce document.\n Êtes-vous sûr de vouloir continuer ?", "Suppression de version") == 0: return
	del lst[i]
	# reconstitution et sauvegarde
	s = separator.join(lst) + separator
	writeFile(path, s)
	sp.window.messageBeep(64)
# end def

def loadVersioningTools():
	# création des éléments de menu
	global menuVersioning
	mnu = sp.window.menus["file"]
	i = getMenuIndex("saveAs", sp.window.menus["file"]) + 1
	if mnu["versioning"]: mnu["versioning"].remove()
	mnu = mnu.add(label = "&Versions du document", submenu = True, name = "versioning", index = i)
	menuVersioning = mnu
	mnu.add(label = "Sauvegarder une nouvelle version", action = saveNewVersion)
	mnu.add(label = "Sauvegarder le texte courant dans une ancienne version", action = saveInFormalVersion)
	mnu.add(label = "Remplacer le texte courant par celui d'une ancienne version", action = restoreVersion)
	mnu.add(label = "Afficher le texte d'une ancienne version dans un nouvel onglet", action = openVersionInNewPage)
	mnu.add(label = "Supprimer une version sauvegardée", action = deleteVersion)
# end def

def unloadVersioningTools():
	# retrait des éléments de menu
	global menuVersioning
	try: menuVersioning.remove()
	except: pass
# end def

# si vous voulez utiliser ce module de manière autonome,
# veuillez décommenter la ligne suivante
# loadVersioningTools()