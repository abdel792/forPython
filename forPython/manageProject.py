# -*- coding: utf-8 -*-
import sixpad as sp
import os
import sys
import re
import inspect
import shutil
import time
from threading import Timer

alert = sp.window.alert

lastLevel = 0

curPage = object()
curProjectPath = ""
curProjectIniFile = ""
lstProjectPath = []
# référence d'évènements à la fenêtre
po = 0
otc = 0

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

def iniRead(key, file, defaultValue = ""):
	""" lit dans un fichier ini """
	if os.path.isfile(file) == False: return defaultValue
	# lecture du fichier
	lstLine = []
	f = open(file, "r")
	lstLine = f.readlines()
	f.close() # Fermeture du fichier
	# parcours des lignes à la recherche de la bonne clée
	for ln in lstLine:
		if ln.find("=") >= 0:
			lst = ln.split("=")
			# si c'est la bonne clée
			if lst[0] == key:
				# traitement s'avérant nécessaire avant le renvoi
				lst[1] = re.sub("(\\r|\\n)", "", lst[1])
				# renvoi
				return lst[1]
			# end if
		# end if
	# end for
	return defaultValue
# end def

def iniWrite(key, value, file):
	""" écrit dans un fichier ini """
	lstLine = []
	if file == "": return False
	# si le fichier existe
	if os.path.isfile(file) == True:
		# lecture du fichier
		f = open(file, "r")
		lstLine = f.readlines()
		f.close() # Fermeture du fichier
	else: # le fichier n'existe pas encore
		# on tente de le créer
		f = open(file, "w")
		f.write("")
		f.close()
		# revérification
		if os.path.isfile(file) == False: return False
	# end if
	# parcours des lignes à la recherche de la bonne clée
	for i in range(len(lstLine)):
		ln = lstLine[i]
		if ln.find("=") >= 0:
			lst = ln.split("=")
			# si c'est la bonne clée
			if lst[0] == key:
				lst[1] = value
				lstLine[i] = "=".join(lst)
				break
			# end if
		# end if
	# end for
	# clée introuvable, création d'une nouvelle clée
	lstLine.append(key + "=" + value)
	# reconstitution du texte
	s = "\r\n".join(lstLine)
	# re-écriture dans le fichier ini
	f = open(file, "w")
	f.write(s)
	f.close()
	return True
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

def isAllReadyOpened(filePath):
	""" vérifie si un fichier est déja ouvert dans un onglet
		si oui, renvoi l'index de l'onglet.
		sinon, renvoi -1"""
	for i in range(len(sp.window.pages)):
		p = sp.window.pages[i]
		if os.path.samefile(filePath, p.file) == True:
			return i
		# end if
	# end for
	return - 1
# end def

def finditer2list(pt, s, flags = 0):
	# recherche par regexp renvoyant un objet liste d'objets match
	lst = []
	found = re.finditer(pt, s, flags)
	for e in found: lst.append(e)
	return lst
# end def

def findall2list(pt, s, flags = 0):
	# recherche par regexp renvoyant un objet liste de string trouvés
	lst = []
	found = re.findall(pt, s, flags)
	for e in found: lst.append(e)
	return lst
# end def

def closeCurrentProject():
	""" ferme le projet actuellement ouvert """
	global curProjectPath, curProjectIniFile
	for p in sp.window.pages:
		if p.file != "":
			p.save()
		# end if
		p.close()
	# end for
	# réinitialisation des paramètres du projet
	curProjectPath = ""
	curProjectIniFile = ""
# end def

def openProject(novelty = False, fldPath = ""):
	# ouvre un projet (nouveau ou existant)
	global curProjectPath, curProjectIniFile
	fldName = ""
	if novelty == False:
		if fldPath == "": fldPath = sp.window.chooseFolder("Désignez le répertoire du projet python à ouvrir")
	else:
		fldPath = sp.window.chooseFolder("Désignez l'emplacement dans lequel créer le nouveau projet python.")
	# end if
	if fldPath == None or os.path.isdir(fldPath) == False: return
	if novelty == False:
		# on retient le nom de ce dossier
		fldName = os.path.basename(fldPath)
	else: # c'est un nouveau projet
		# on demande le nom à donner au dossier
		# dont on va vérifier la validité
		pt = "^[\\w\\d_]+$"
		fldName = sp.window.prompt("Tapez le nom du repertoire devant contenir le projet.\nAttention, ce nom doit respecter les standards de nom de variable en langage python.", "Nom du repertoire du projet", fldName)
		if fldName == None or fldName == "": return
		if re.match(pt, fldName):
			fldName = fldName
		else:
			alert("Le nom tapé pour le répertoire python n'est pas valide.\nLe processus va à présent s'interrompre.", "Erreur- nom erroné")
			return
		# end if
		# complétion du chemin du repertoire du projet
		fldPath = os.path.join(fldPath, fldName)
		# on crée ce dossier
		os.mkdir(fldPath)
		# vérification
		if os.path.isdir(fldPath) == False:
			alert("Impossible de créer le répertoire " + fldName + ".\nL'action va à présent s'interrompre.", "Erreur- création de dossier")
			return
		# end if
	# end if
	projectPath = fldPath
	# on ferme le projet courant
	closeCurrentProject()
	# recensement des fichiers python dans le repertoire à ouvrir
	lstFile = []
	lstName = []
	for f in os.listdir(fldPath):
		ext = f.split(".")[-1].lower()
		# si fichier python
		if ext == "py" or ext == "pyw":
			# on retient le fichier python
			lstFile.append(os.path.join(fldPath, f))
			lstName.append(f)
		# end if
	# end for
	# si pas de fichier python dans ce dossier
	if len(lstFile) == 0:
		# on en crée un automatiquement
		# après demande à l'utilisateur
		if novelty == False:
			if sp.window.confirm("Il n'existe pas de fichier python à l'emplacement que vous avez désigné.\nVoulez-vous continuer cette action par la création automatique d'un fichier __init__.py dans le repertoire \n" + fldPath + " ?", "Fichiers python introuvables") == 0: return
		# end if
		path = os.path.join(fldPath, "__init__.py")
		if os.path.isfile(path) == False: writeFile(path, "# -*- coding: utf-8 -*-")
		lstFile.append(path)
		lstName.append("__init__.py")
	# end if
	# initialisation de paramètres
	projectName = ""
	projectStartingFile = ""
	projectType = ""
	# recherche du fichier des paramètres du projet python
	projectFile = os.path.join(fldPath, "project.pyproj")
	if os.path.isfile(projectFile) == False:
		# il n'existe pas, on va le créer
		# mais d'abord renseignement de quelques paramètres
		s = ""
		# demande de désignation du fichier de démarrage du projet
		i = sp.window.choice("Choisissez le fichier de démarrage du projet", "Fichier de démarrage", lstName)
		if i >= 0: projectStartingFile = lstName[i]
		s += "projectStartingFile=" + projectStartingFile + "\r\n"
		# demande de détermination du nom du projet
		projectName = projectStartingFile.split(".")[0]
		projectName = sp.window.prompt("Tapez le nom du projet", "Nom du projet", fldName, [fldName, projectName])
		if projectName == "" or projectName == None: projectName = fldName
		s += "projectName=" + projectName + "\r\n"
		# demande de détermination du type du projet (exe, dll, script, etc)
		projectType = "exe"
		s += "projectType=" + projectType + "\r\n"
		# création
		writeFile(projectFile, s)
	# end if
	# lecture du fichier de projet
	s = "\r\n" + readFile(projectFile, )
	projectName = finditer2list("projectName=([^\\r\\n]*)", s, re.I)[0].group(1)
	projectStartingFile = finditer2list("projectStartingFile=([^\\r\\n]*)", s, re.I)[0].group(1)
	projectType = finditer2list("projectType=([^\\r\\n]*)", s, re.I)[0].group(1)
	# ouverture des fichiers python dans les onglets
	for f in lstFile:
		p = sp.window.open(f)
	# end for
	# sélection de l'onglet du fichier de démarrage
	for p in sp.window.pages:
		if p.name == projectStartingFile:
			p.focus()
			break
		# end if
	# end for
	# assignation de variables globales
	curProjectPath = projectPath
	curProjectIniFile = projectFile
	# ajout de ce projet à la liste des projets récents
	addToRecentProjects(projectPath)
	# actualisation de la liste des projets récents
	displayRecentProjectsInMenu()
	# affichage des outils contextuels de projet
	displayContextualProjectTools(projectPath)
	# lecture du nombre d'onglets ouverts
	sayText(str(len(lstFile)) + " onglets ouverts")
# end def

def openNewProject():
	""" Crée un nouveau projet """
	openProject(True)
# end def

def openRecentProject(menuIndex):
	""" ouvre un projet récent """
	def openAProject():
		global lstProjectPath
		openProject(False, lstProjectPath[menuIndex])
	# end def
	return openAProject
	
# end def

def saveProjectAs():
	""" enregistre le projet sous """
	global curProjectPath
	# si projet non actuellement désigné
	if curProjectPath == "":
		sayText("Projet non enregistré")
		sp.window.messageBeep(0)
		return
	# end if
	# si le chemin vers le projet est éronné
	if os.path.isdir(curProjectPath) == False:
		sayText("Impossible d'enregistrer le projet sous")
		sp.window.messageBeep(0)
		return
	# end if
	# demande de désignation de l'emplacement où faire une copie du projet courant
	fldPath = sp.window.chooseFolder("Désignez l'emplacement dans lequel enregistrer le projet '" + os.path.basename(curProjectPath) + "'.")
	if fldPath == None or fldPath == "": return
	# COPIE DE REPERTOIRE
	shutil.copytree(curProjectPath, os.path.join(fldPath, os.path.basename(curProjectPath)))
# end def

def executeProject():
	""" exécute le projet """
	global curProjectPath, curProjectIniFile
	# enregistrement de toutes les pages ouvertes
	for p in sp.window.pages:
		p.save()
	# end for
	# on va s'assurer que la page du fichier de lancement du projet est ouverte
	projectStartingFile = iniRead("projectStartingFile", curProjectIniFile, "")
	projectStartingFile = projectStartingFile.replace("/", "\\")
	projectStartingFile = os.path.join(curProjectPath, projectStartingFile)
	if os.path.isfile(projectStartingFile) == False:
		alert("Le fichier de démarrage du projet est introuvable.\nUtiliser  la fenêtre de propriété du projet pour la désigner à nouveau.", "Exécution impossible")
		return
	# end if
	# détermination du bon onglet
	page = None
	for p in sp.window.pages:
		if os.path.samefile(projectStartingFile, p.file) == True:
			page = p
			break
		# end if
	# end for
	# si l'onglet n'est pas ouvert, on l'ouvre
	if page == None:
		# mais en faisant attention de ne pas perdre l'onglet courant
		curPage = sp.window.curPage
		page = sp.window.open(projectStartingFile)
		curPage.focus()
	# end if
	# lancement de l'exécution en passant par forPython
	from forPython.__init__ import runAPythonCodeOrModule
	runAPythonCodeOrModule(page)
# end def

def TVOpenFile(item):
	# ouverture du fichier dans un onglet, si pas déja ouvert
	global tv
	# Détermination si la page est déjà ouverte
	i = isAllReadyOpened(item.value)
	# comparaison
	if i >= 0:
		# le fichier est ouvert dans l'onglet i
		sp.window.pages[i].focus()
	else: # le fichier n'est pas encore ouvert
		sp.window.open(item.value)
	# end if
	# on referme l'arborescence
	tv.close()
# end def

def TVOpenFolder(item):
	""" ouverture du dossier dans l'explorateur windows """
	path = item.value
	if os.path.isfile(path) == True:
		path = os.path.dirname(path)
	# end if
	# utilisation d'une fonction du forPython
	from forPython.__init__ import runFile
	runFile("explorer.exe", path)
# end def

def TVRename(item):
	# renommage de l'élément
	itemPath = item.value
	dirPath = os.path.dirname(item.value)
	name = os.path.basename(item.value)
	# si l'élément est un fichier
	if os.path.isfile(itemPath) == True:
		# demande de modification
		newName = sp.window.prompt("Renommer:", "Renommer", name)
		if newName == None or newName == "": return
		# si le fichier est ouvert dans un onglet
		i = isAllReadyOpened(itemPath)
		if i >= 0:
			# on l'enregistre et le ferme au préalable
			sp.window.pages[i].close()
		# end if # fin si le fichier est ouvert
		# détermination du nouveau chemin
		newItemPath = os.path.join(dirPath, newName)
		# renommage
		os.rename(itemPath, newItemPath)
		# si échec de renommage
		if os.path.isfile(newItemPath) == False:
			alert("Le renommage a rencontré une erreur", "Erreur de renommage")
			# on réouvre le précédent fichier si avait été ouvert
			if i >= 0:
				sp.window.open(itemPath)
			# end if
			return
		# end if # fin si renommage a échoué
		# le renommage a été un succès
		# ouverture du nouveau fichier si l'ancien avait été ouvert
		if i >= 0:
			page = sp.window.open(newItemPath)
			page.focus()
		# end if # fin si fichier avait déjà été ouvert
		# si le fichier modifié était le fichier de démarrage
		projectStartingFile = iniRead("projectStartingFile", curProjectIniFile, "")
		if name == projectStartingFile:
			projectStartingFile = newName
		elif projectStartingFile.find("/" + name) >= 0:
			projectStartingFile = projectStartingFile.replace("/" + name, "/" + newname)
		# end if
		iniWrite("projectStartingFile", projectStartingFile, curProjectIniFile)
		# on actualise les valeurs dans l'arborescence
		item.value = os.path.join(dirPath, newName)
		item.text = newName
	else: # l'élément est un dossier
		sp.window.messageBeep(0)
		return
	# end if # fin si fichier ou dossier
# end def

def TVDelete(item):
	# suppression de l'élément courant
	global tv
	# demande de confirmation de la suppression
	if sp.window.confirm("Êtes-vous sur de vouloir supprimer l'élément'" + os.path.basename(item.value) + "' du projet ?", "Suppression") == 0: return
	# si fichier
	if os.path.isfile(item.value) == True:
		os.remove(item.value)
		# si le chemin représente une fenêtre actuellement ouverte
		# on va la fermer
		i = isAllReadyOpened(item.value)
		if i >= 0: sp.window.pages[i].close()
	elif os.path.isdir(item.value) == True:
		shutil.rmtree(item.value)
	# end if
	# fermeture de l'arborescence
	tv.close()
# end def

def TVCopyAbsolutePath(item):
	""" Copie du chemin absolu de l'élément sélectionné dans l'arborescence """
	sp.setClipboardText(item.value)
# end def

def TVCopyRelativePath(item):
	""" Copie du chemin relatif de l'élément sélectionné dans l'arborescence """
	global curProjectPath
	# décomposition du chemin de l'item dans une liste
	lst = item.value.split("\\")
	# on trouve la longueur limite du répertoire de base du projet
	limit = len(curProjectPath.split("\\"))
	# on prend la partie au dela de cette limite
	lst = lst[limit:]
	# on renvoi cette partie en la joignant par des barres obliques
	path = "/".join(lst)
	# on envoi dans le presse-papier
	sp.setClipboardText(path)
# end def

def TVCopyRef(item):
	""" Copie de la référence python de l'élément sélectionné dans l'arborescence """
	is6padInterpretor = (sp.getConfig("curPythonVersion", "") == "6padPythonVersion")
	ref = getModuleRef(item.value, is6padInterpretor)
	# retrait d'extension
	ref = re.sub("\\.py$", "", ref, 0, re.I)
	ref = re.sub("\\.pyw$", "", ref, 0, re.I)
	# copie dans le presse-papier
	sp.setClipboardText(ref)
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

def delayTitleChange():
	# retard sur le changement de titre de la fenêtre
	global msg
	sp.window.title = msg
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

def getModuleRef(modPath, is6padInterpretor = True):
	# renvoi la référence à un module  à partir de son chemin
	global curProjectPath
	# décomposition du chemin vers le module dans une liste
	lst = modPath.split("\\")
	rep = ""
	# si l'interpréteur sélectionné est celui du 6pad++
	if is6padInterpretor == True:
		appPath = sp.appdir
		# quel répertoire ? (lib ou plugins ?) lib ou plugins ?
		if modPath.find(os.path.join(appPath, "lib")) >= 0: rep = "lib"
		elif modPath.find(os.path.join(appPath, "plugins")) >= 0: rep = "plugins"
		else: return ""
		rep = os.path.join(appPath, rep)
	else: # l'interpréteur sélectionné n'est pas celui du 6pad++
		rep = curProjectPath
	# end if
	# on trouve la longueur limite du répertoire de base du projet
	limit = len(rep.split("\\"))
	# on prend la partie au dela
	lst = lst[limit:]
	# on renvoi cette partie en la joignant par des points
	rep = ".".join(lst)
	# on élimine l'extension python
	rep = re.sub("\\.py$", "", rep, 0, re.I)
	rep = re.sub("\\.pyw$", "", rep, 0, re.I)
	# renvoi
	return rep
# end def

def getCurrentLevel(item):
	# renvoi le niveau de l'item dans la hiérarchie de larborescence
	level = 1
	parent = item.parentNode
	while(parent != None):
		parent = parent.parentNode
		level = level + 1
	# end while
	return level
# end def

def onPageOpened(newPage):
	""" A l'ouverture d'une nouvelle page"""
	i = 0
# end def

def onTitleChange(text):
	""" lors du changement de titre """
	global curPage, msg
	# on va ajouter au titre le nom du projet
	text = sp.window.curPage.name + " - " + os.path.basename(curProjectPath) + " - 6pad++"
	# si changement d'onglet
	if curPage != sp.window.curPage:
		sayText(text, True)
		curPage = sp.window.curPage
	# end if
	# on retarde le changement du titre par un timer
	msg = text
	tmr = Timer(0.5, delayTitleChange)
	tmr.start() # lancement du timer
	# renvoi
	return text
# end def

def onPageActivated(page):
	""" A la prise de focus d'une page """
	# on va mettre le nom du projet dans le titre de la fenêtre
	sp.window.messageBeep(0)
	name = sp.window.title
	name = name + " [" + os.path.basename(curProjectPath) + "]"
	sp.window.title = name
# end def

def onCheck(dialog, item):
	# au cochage ou décochage
	i = 0
# end def

def onSelect(dialog, item):
	# à la sélection d'un noeud
	global lastLevel
	# lecture de son niveau si changement de noeud
	level = getCurrentLevel(item)
	if level != lastLevel:
		#  désactivé sayText("Niveau " + str(level))
		lastLevel = level
	# end if
	# désactivé sayText(s)
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
	# constitution de la liste de base des éléments du menu contextuel
	lst = ["Renommer", "Supprimer", "Copier le chemin absolu", "Copier le chemin relatif", "Copier la référence python"]
	# selon si dossier ou fichier python
	if os.path.isdir(item.value):
		lst.insert(0, "Ouvrir dans l'explorateur Windows")
		# affichage du menu contextuel
		i = sp.window.showPopupMenu(lst)
		if i == -1:
			return
		# end if
	elif os.path.isfile(item.value):
		lst.insert(0, "Afficher le code")
		# affichage du menu contextuel
		i = sp.window.showPopupMenu(lst)
		if i == -1:
			return
		elif i == 0:
			if os.path.isfile(item.value) == True:
				TVOpenFile(item)
			elif os.path.isdir(item.value) == True:
				TVOpenFolder(item)
			# end if
		elif i == 1:
			TVRename(item)
		elif i == 2:
			TVDelete(item)
		elif i == 3:
			TVCopyAbsolutePath(item)
		elif i == 4:
			TVCopyRelativePath(item)
		elif i == 5:
			TVCopyRef(item)
		# end if
	else:
		return
	# end if
# end def

def loadTV(tv, rootPath):
	# chargement de l'arborescence
	# à partir du dossier racine du projet
	if os.path.isdir(rootPath):
		item = tv.root.appendChild(os.path.basename(rootPath), rootPath)
		browseFolders(item)
	# end if
	# ajout d'évènements
	tv.addEvent("expand", onExpand)
	tv.addEvent("contextMenu", onContextMenu)
	tv.addEvent("check", onCheck)
	tv.addEvent("select", onSelect)
# end def

def browseFolders(item):
	# parcours des sous-éléments d'un dossier
	# dans l'optique de les ajouter à l'arborescence
	f = ""
	pt = "(.+)\\.(py|pyw|pyx)$"
	found = os.listdir(item.value)
	if found == None or len(found) == 0: return
	# premièrement, recherche des sous-dossiers
	for f in found:
		try:
			if os.path.isdir(os.path.join(item.value, f)):
				subItem = item.appendChild(f, os.path.join(item.value, f))
				browseFolders(subItem)
			# end if
		except: pass
	# end for
	# puis, recherche des fichiers python du dossier courant
	for f in found:
		if re.match(pt, f, re.I):
			subItem = item.appendChild(f, os.path.join(item.value, f))
			# si l'item représente le document courant, on le sélectionne
			try:
				if os.path.samefile(sp.window.curPage.file, subItem.value):
					subItem.select()
				# end if
			except: pass
		# end if
	# end for
# end def

def projectClose():
	""" ferme le projet courant """
	closeCurrentProject()
	# masque les outils spécifiques aux projets
	hideContextualProjectTools()
	# ouvre une fenêtre vierge
	page = sp.window.new()
	page.focus()
# end def

def projectAddModule():
	""" ajout d'un nouveau module au projet """
	global curProjectPath
	# le chemin par défaut du fichier à créer
	filePath = os.path.join(curProjectPath, "module1.py")
	# on crée la liste des extensions autorisées
	lstExtension = [("Python file (*.py)", "*.py"), ("Python file (*.pyw)", "*.pyw"), ("Text file (*.txt)", "*.txt")]
	# on affiche le dialogue enregistrer sous
	filePath, i = sp.window.saveDialog(file = filePath, title = "Créer un nouveau module", filters = lstExtension)
	if filePath == None or filePath == "": return
	# si le fichier existe déjà
	if os.path.isfile(filePath) == True:
		alert("Un fichier porte déjà ce nom. Vous ne pouvez le remplacer.\nVeuillez recommencer l'action et choisir un nom disponible.", "Impossible d'écraser le fichier")
		return
	# end if
	# création du fichier
	writeFile(filePath, "# -*- coding: utf-8 -*-")
	# ouverture du fichier dans un nouvel onglet
	page = sp.window.open(filePath)
	page.focus()
# end def

def projectDeleteCurrentModule():
	""" suppression du module courant """
	page = sp.window.curPage
	filePath = page.file
	if filePath == "":
		sp.window.messageBeep(0)
		return
	# end if
	# demande de confirmation
	if sp.window.confirm("Êtes-vous sûr de vouloir supprimer le module '" + page.name + "' du projet '" + os.path.basename(curProjectPath) + "' ?", "Suppression de module du projet") == 0: return
	# enregistrement et fermeture
	page.save()
	page.close()
	# suppression du fichier
	os.remove(filePath)
	# vérification
	# désactivé
	# if os.path.isfile(filePath) == True:
		# alert("La suppression du fichier a rencontré une erreur")
	# # end if
# end def

def projectSaveParams():
	""" fixe les paramètres de sauvegarde du projet en cours """
	# pour l'instant, uniquement le chemin du dossier de sauvegarde
	global curProjectPath, curProjectIniFile
	# on retrouve le chemin actuel du dossier de sauvegarde
	projectSavePath = iniRead("projectSavePath", curProjectIniFile, "")
	# on demande de désigner ou rectifier le dossier de sauvegarde
	projectSavePath = sp.window.chooseFolder(folder = projectSavePath, title = "Désignez le dossier dans lequel sera sauvegardé le projet '" + os.path.basename(curProjectPath) + "'")
	if projectSavePath == None or projectSavePath == "": return
	# alert("projectSavePath=" + projectSavePath)
	# alert("curProjectIniFile=" + curProjectIniFile)
	# détermination du type de sauvegarde
	projectSaveType = iniRead("projectSaveType", curProjectIniFile, "1")
	lst = ["sauvegarde complète", "Sauvegarde incrémentielle"]
	i = sp.window.choice("Choisissez le type de sauvegarde pour ce projet", "Type de sauvegarde", lst, int(projectSaveType) - 1)
	if i >= 0: projectSaveType = str(i + 1)
	# enregistrement des paramètres
	iniWrite("projectSavePath", projectSavePath, curProjectIniFile)
	iniWrite("projectSaveType", projectSaveType, curProjectIniFile)
# end def

def projectSaveStart():
	""" lancement de la sauvegarde du projet """
	global curProjectPath, curProjectIniFile
	# vérification de l'existence du dossier du projet
	if os.path.isdir(curProjectPath) == False:
		sayText("Impossible de sauvegarder le projet")
		sp.window.messageBeep(0)
		return
	# end if
	# identification du dossier pour les sauvegardes
	projectSavePath = iniRead("projectSavePath", curProjectIniFile, "")
	if os.path.isdir(projectSavePath) == False:
		alert("Impossible de lancer la sauvegarde car le répertoire de sauvegarde est introuvable.\nSi vous ne l'avez pas encore fait, veuillez le désigner.\n" + projectSavePath, "Erreur- Sauvegarde impossible")
		return
	# end if
	# détermination du type de sauvegarde
	projectSaveType = iniRead("projectSaveType", curProjectIniFile, "1")
	# détermination du chemin vers le dossier de destination
	# il doit porter le même nom que le dossier d'origine
	destPath = os.path.join(projectSavePath, os.path.basename(curProjectPath))
	# si type de sauvegarde = sauvegarde complète
	if projectSaveType == "1":
		# si le dossier de destination avait déjà été créé, on le supprime
		if os.path.isdir(destPath) == True:
			try:
				shutil.rmtree(destPath)
			except:
				sp.window.warning("La suppression préalable de l'ancienne version de la sauvegarde a rencontré une erreur.\nVeuillez vous assurer qu'un fichier  n'est pas utilisé dans ce dossier.", "Erreur- sauvegarde impossible")
				return
			# end try
		# end if
	else: #  type de sauvegarde = sauvegarde incrémentielle
		# on va ajouter la date et l'heure au nom du dossier de destination
		t = time.strftime("%Y-%m-%d %H-%M-%S")
		destPath = destPath + " " + t
	# end if # fin si type de sauvegarde
	# copie des fichiers
	sayText("Veuillez patienter")
	try:
		shutil.copytree(curProjectPath, destPath, symlinks = True, ignore_dangling_symlinks = True)
		# shutil.copytree(curProjectPath, destPath, symlinks = True)
		alert("Fin de la copie.\nLe projet '" + os.path.basename(curProjectPath) + "' a été correctement sauvegardé dans :\n" + projectSavePath, "Projet sauvegardé !")
	except:
		sp.window.warning("La sauvegarde du projet a rencontré une erreur lors de la copie des fichiers dans:\n" + projectSavePath, "Erreur- sauvegarde interrompue")
	# end try
# end def

def projectFileExplorer():
	""" affiche l'explorateur des fichiers du projet """
	global curProjectPath, tv
	# le chemin du projet
	rootPath = curProjectPath
	if rootPath == "": rootPath = os.path.dirname(sp.window.curPage.file)
	# affichage
	tv = qc.TreeViewDialog.open(title = "Explorateur de projet", hint = "Gérer les fichier python du projet", modal = False, multiple = False, okButtonText = "", cancelButtonText = "Fermer")
	# chargement
	loadTV(tv, rootPath)
# end def

def projectClassExplorer():
	""" ouvre l'explorateur de classes du projet """
	i = 0
# end def

def projectProperties():
	# affichage des propriétés du projet
	global curProjectIniFile, curProjectPath
	s = ""
	# le nom du projet
	projectName = iniRead("projectName", curProjectIniFile, "Inconnu")
	s += "Nom du projet : " + projectName + "\r\n"
	# le type du projet
	projectType = iniRead("projectType", curProjectIniFile, "Inconnu")
	s += "Type de projet : " + projectType + "\r\n"
	#  le fichier de démarrage
	projectStartingFile = iniRead("projectStartingFile", curProjectIniFile, "Inconnu")
	s += "Fichier de démarrage : " + projectStartingFile + "\r\n"
	# l'emplacement du projet
	projectPath = curProjectPath
	s += "Emplacement du projet : " + projectPath + "\r\n"
	# affichage
	sp.window.messageBox(s, "Propriétés du projet " + projectName, 1)
# end def

def addToRecentProjects(projectPath):
	""" enregistre le projet récent """
	# recherche des fichiers récents dans le fichier de configuration
	s = sp.getConfig("recentPythonProjects", "")
	lst = s.split("|") # transfert dans une liste
	# on retire une éventuelle présence de ce chemin déjà présent dans la liste des chemins
	try: lst.remove(projectPath)
	except: pass
	# on ajoute le nouvel élément au début
	lst.insert(0, projectPath)
	# si la liste a plus de 15 éléments, on la réduit
	if len(lst) > 15:
		lst = lst[0:14]
	# end if
	# reconstitution et écriture dans le fichier de configuration
	s = "|".join(lst)
	sp.setConfig("recentPythonProjects", s)
# end def

def displayRecentProjectsInMenu():
	""" peuple le menu projet récents """
	global menuRecentProjects, lstProjectPath
	mnu = menuRecentProjects # simplification
	# vidage de la liste des chemins de projet
	lstProjectPath = []
	# vidage du menu
	i = mnu.length - 1
	while (i >= 0):
		mnu[i].remove()
		i -= 1
	# end while
	# recherche des fichiers récents dans le fichier de configuration
	s = sp.getConfig("recentPythonProjects", "")
	lst = s.split("|") # transfert dans liste
	# création des menus à la volée
	j = -1
	for i in range(len(lst)):
		if os.path.isdir(lst[i]) == True:
			j += 1
			mnu.add(label = os.path.basename(lst[i]) + " de " + os.path.dirname(lst[i]), action = openRecentProject(j))
			# ajout à la liste globale
			lstProjectPath.append(lst[i])
		# end if
		# contrôle de la limite (10 éléments maximum)
		if j >= 9: break
	# end for
# end def

def displayContextualProjectTools(projectPath):
	# charge et affiche les outils contextuels d'un projet à ouvrir
	global curProjectPath, curProjectIniFile, curPage
	# enregistrement du chemin du projet
	curProjectPath = projectPath
	# vérification que ces outils n'ont pas déjà été affichés
	if sp.window.menus["project"] != None: return
	# ajout d'évènement à la fenêtre
	po = sp.window.addEvent("pageOpened", onPageOpened)
	otc = sp.window.addEvent("title", onTitleChange)
	try: curPage = sp.window.curPage
	except: pass
	# création du menu projet
	i = getMenuIndex("forPython", sp.window.menus)
	if i < 0: i = 4
	mnu = sp.window.menus.add(label = "Proj&et", name = "project", submenu = True, index = i + 1)
	# menu d'ajout de module
	m = mnu.add(label = "Ajouter un module python", name = "projectAddModule", action = projectAddModule)
	# m.enabled = False
	# menu d'ajout d'interface graphique
	# m = mnu.add(label = "Ajouter une interface graphique", name = "projectAddGraphicInterface")
	# m.enabled = False
	# menu d'ajout de fichier de base de données
	# m = mnu.add(label = "Ajouter un fichier de base de données", name = "projectAddDatabaseFile")
	# m.enabled = False
	# menu de suppression du projet
	m = mnu.add(label = "Supprimer le module courant du projet", name = "projectDeleteCurrentModule", action = projectDeleteCurrentModule)
	# m.enabled = False
	# menu des paramètres de sauvegarde du projet
	m = mnu.add(label = "Sauvegarde du projet", name = "projectSave", submenu = True)
	m.add(label = "Paramètres de sauvegarde du projet", action = projectSaveParams, name = "projectSaveParams")
	m.add(label = "Lancer la sauvegarde du projet", action = projectSaveStart, name = "projectSaveStart")
	# menu d'exploration des fichiers du projet
	mnu.add(label = "Explorateur de projet python", action = projectFileExplorer, name = "projectFileExplorer", accelerator = "CTRL+T")
	# menu d'exploration des classes du projet
	# m = mnu.add(label = "Explorateur de classes python", action = projectClassExplorer, name = "projectExplorer")
	# m.enabled = False
	# menu des propriétés du projet
	m = mnu.add(label = "Propriétés du projet python", name = "projectProperties", action = projectProperties)
	# m.enabled = False
	# dans le menu fichier
	mnu = sp.window.menus.file
	# menu enregistrer le projet sous après l'item enregistrer sous
	i = getMenuIndex("saveAs", mnu)
	mnu.add(label = "Enregistrer le projet python sous...", name = "saveProjectAs", action = saveProjectAs, index = i + 1)
	# menu fermer le projet après l'item fermer
	i = getMenuIndex("close", mnu)
	mnu.add(label = "Fermer le projet python", action = projectClose, name = "closePythonProject", index = i + 1)
	# dans le menu python
	if sp.window.menus["forPython"]["execution"] != None:
		mnu = sp.window.menus["forPython"]["execution"]
		# ajout du menu exécuter le projet
		m = mnu.add(label = "Exécuter le projet", name = "executeProject", action = executeProject)
		# m.enabled = False
	# end if
# end def

def hideContextualProjectTools():
	# masque les outils contextuel liés à un projet ouvert
	mnu = sp.window.menus
	# masque le menu projet de premier niveau
	if mnu["project"] != None: mnu["project"].remove()
	# dans le menu fichier
	if mnu.file["saveProjectAs"] != None: mnu.file["saveProjectAs"].remove()
	if mnu.file["closePythonProject"] != None: mnu.file["closePythonProject"].remove()
	# dans le menu python
	try: sp.window.menus["forPython"]["execution"]["executeProject"].remove()
	except: pass
	# retrait d'évènements à l'objet window
	try: sp.window.removeEvent("pageOpened", po)
	except: pass
	try: sp.window.removeEvent("title", otc)
	except: pass
	# retraits d'évènements aux objets pages
	for page in sp.window.pages:
		try: page.removeEvent(page.__setattr__("opa"))
		except: pass
	# end for
# end def

def loadManageProjectTools():
	# charge les outils liés au manageProject
	global menuRecentProjects
	# création des menu visible en tout temps
	# dans le menu fichier
	mnu = sp.window.menus["file"]
	# menu projet python dans nouveau
	mnu[0].add(label = "Projet python", name = "newPythonProject", action = openNewProject)
	# on modifie le label pour être synchrone
	mnu[0][0].label = "Fichier"
	# menu ouvrir un projet
	i = getMenuIndex("open", mnu)
	mnu.add(label = "Ouvrir un projet python", name = "openPythonProject", index = i + 1, action = openProject)
	# les menus des projets récents
	i = getMenuIndex("close", mnu)
	menuRecentProjects = mnu.add(label = "Projets récents", name = "recentPythonProjects", index = i, submenu = True)
	displayRecentProjectsInMenu()
# end def

def unloadManageProjectTools():
	# retrait des outils liés au manageProject
	mnu = sp.window.menus
	# les outils contextuels
	hideContextualProjectTools()
	# dans le menu fichier
	if mnu.file[0]["newPythonProject"] != None: mnu.file[0]["newPythonProject"].remove()
	if mnu.file["openPythonProject"] != None: mnu.file["openPythonProject"].remove()
	if mnu.file["recentPythonProjects"] != None: mnu.file["recentPythonProjects"].remove()
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
