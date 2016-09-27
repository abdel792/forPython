# -*- coding: utf-8 -*-

import sixpad as sp
import re
import os

# pour raccourcir l'appel à la fonction alert
alert = sp.window.alert

# pour compter le nombre de chargement de cet extension
nbLoad = 0

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

def getCurReturnUnit():
	# renvoi l'unité de retour à la ligne dans le document courant
	lst = ["\r\n", "\n", "\r"]
	return lst[sp.window.curPage.lineEnding]	
# end def

def getCurIndentUnit():
	# renvoi l'unité d'indentation dans le document courant
	i = sp.window.curPage.indentation
	if i == 0:
		return "\t"
	else:
		return " " * i
	# end if
# end def

def getReturnUnitInText(s):
	# détermine l'unité de retour à la ligne dans le texte
	nb1 = len(re.findall("\\r\\n", s))
	nb2 = len(re.findall("\\r", s))
	nb3 = len(re.findall("\\n", s))
	# comparaisons
	if nb1 == 0 and nb2 == 0 and nb3 == 0: return ""
	if nb1 > 0: return "\r\n"
	if nb2 > nb3: return "\r"
	if nb3 > nb2: return "\n"
	return ""
# end def

def getIndentUnitInText(s, lstIndent, lstCode):
	# détermine l'unité d'indentation dans un texte
	iu = ""
	# cas de moins de trois lignes
	if len(lstIndent) < 3: return getCurIndentUnit()
	# cas de plus de deux lignes
	# on essai de savoir si les indentations sont constitués de tabulation ou d'espaces
	nbSpace = 0
	nbTab = 0
	for i in range(1, len(lstIndent)):
		if re.match("^[ ]+", lstIndent[i]):
			nbSpace = nbSpace + 1
		elif re.match("^[\\t]+", lstIndent[i]):
			nbTab = nbTab + 1
		# end if
	# end for
	# si rien ne prédomine
	if nbTab == 0 and nbSpace == 0: return getCurIndentUnit()
	# si les tabulations prédomminent
	if nbTab > nbSpace: return "\t"
	# si les espaces prédominent
	# on va identifier les variations pour savoir combien en constituent un niveau d'indentation
	lst = [0, 0, 0, 0, 0, 0, 0, 0]
	lastIndent = lstIndent[1]
	for i in range(2, len(lstIndent)):
		if lstIndent[i] != lastIndent:
			variation = abs(len(lstIndent[i]) - len(lastIndent))
			lst[variation - 1] = lst[variation - 1] + 1
			lastIndent = lstIndent[i]
		# end if
	# end for
	# détermination de la variation la plus élevée
	index = - 1
	maxi = 0
	for i in range(0, 8):
		if lst[i] > maxi:
			maxi = lst[i]
			variation = i
		# end if
	# end for
	if variation == - 1: return getCurIndentUnit()
	return " " * (variation + 1)
# end def

def choosePaste1():
	# choix du collage simple
	try:
		mnu = sp.window.menus["edit"]["pasteTypes"]
		if mnu[0].checked == True: return
		# cochage et décochages
		mnu[0].checked = True
		mnu[1].checked = False
		mnu[2].checked = False
		# enregistrement du choix dans le fichier ini
		sp.setConfig("currentPasteType", "1", False)
		# rechargement des menus et raccourcis
		loadPasteTools()
	except:
		alert("Erreur dans la tentative de changement du type de collage")
	# end try
# end def

def choosePaste2():
	# choix du collage de code python
	try:
		mnu = sp.window.menus["edit"]["pasteTypes"]
		if mnu[1].checked == True: return
		# cochage et décochages
		mnu[0].checked = False
		mnu[1].checked = True
		mnu[2].checked = False
		# enregistrement du choix dans le fichier ini
		sp.setConfig("currentPasteType", "2", False)
		# rechargement des menus et raccourcis
		loadPasteTools()
	except:
		alert("Erreur dans la tentative de changement du type de collage")
	# end try
# end def

def choosePaste3():
	# choix du collage classique de 6pad++
	try:
		mnu = sp.window.menus["edit"]["pasteTypes"]
		if mnu[2].checked == True: return
		# cochage et décochages
		mnu[0].checked = False
		mnu[1].checked = False
		mnu[2].checked = True
		# enregistrement du choix dans le fichier ini
		sp.setConfig("currentPasteType", "3", False)
		# rechargement des menus et raccourcis
		loadPasteTools()
		# avertissement de la nécessité de redémarrage
		alert("Le choix du collage classique de 6pad++ a été validé.\nCependant, vous devez impérativement redémarrer 6pad++ pour que ce changement soit effectif dans le collage de texte.", "Choix validé, nécessité de redémarrage de l'application")
	except:
		alert("Erreur dans la tentative de changement du type de collage")
	# end try
# end def

def paste1():
	# collage simple
	# recueillement du texte du presse-papier
	s = sp.getClipboardText()
	# collage
	page = sp.window.curPage
	if s != "":
		page.selectedText = s
		page.selectionStart = page.selectionEnd
	# end if
# end def

def paste2():
	# collage de code python
	s = ""
	rt = ""
	iu = ""
	# recueillement du texte du presse-papier
	s = sp.getClipboardText()
	# identification du type de retour à la ligne dans ce texte
	rt = getReturnUnitInText(s)
	if rt == "": rt = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lstLine = s.split(rt)
	n = len(lstLine)
	# recueillement de toutes les indentations dans une liste
	lstIndent = []
	for i in range(0, n): lstIndent.append(re.findall("^[ \\t]*", lstLine[i])[0])
	# recueillement des lignes sans indentation dans une liste
	lstCode = []
	for i in range(0, n): lstCode.append(lstLine[i][len(lstIndent[i]):])
	# identification de l'unité d'indentation dans le texte à coller
	iu = getIndentUnitInText(s, lstIndent, lstCode)
	# Résolution de l'incertitude entre la première et la seconde ligne
	# la première étant possiblement incomplète.
	if n > 1: # si plus d'une ligne à coller
		lst = ["La première ligne du texte à coller est d'indentation égale à celle de sa seconde ligne", "La première ligne du texte à coller est d'indentation supérieure à celle de sa seconde ligne"]
		if lstIndent[1] != "": lst.append("La première ligne du texte à coller est d'indentation inférieure à celle de sa seconde ligne")
		# affichage
		msg = "Vous tentez de coller plusieurs lignes de code python dans ce document.\nEt pour éviter toute ambiguïté, vous devez indiquer quelle est le niveau d'indentation de la première ligne à coller par rapport à la seconde.\nCes lignes sont:\n"
		msg = msg + lstIndent[0] + lstLine[0] + "\n" + lstIndent[1] + lstLine[1]
		i = sp.window.choice(msg, "Collage de plusieurs lignes", lst)
		if i < 0 or i == None:
			return False
		elif i == 0: # de même niveau
			lstIndent[0] = lstIndent[1]
		elif i == 1: # supérieur à la seconde
			lstIndent[0] = lstIndent[1] + iu
		elif i == 2: # inférieur à la seconde
			lstIndent[0] = iu * (int(len(lstIndent[1]) / len(iu)) - 1)
		# end if
	# end if
	# convertion des indentations au type du document courant
	ciu = sp.window.curPage.indentString
	if ciu != iu:
		for i in range(0, n): lstIndent[i] = lstIndent[i].replace(iu, ciu)
	# end if
	# par mesure de simplification, créons  la liste des niveaux d'indentation courant
	lstLevel = []
	gap = 0
	for i in range(0, n):
		j = 0
		j = int(len(lstIndent[i]) / len(ciu))
		lstLevel.append(j)
	# end for
	# recueillement d'informations sur l'emplacement courant
	curIndent = re.findall("^[ \\t]*", sp.window.curPage.curLineText)[0]
	curLevel = sp.window.curPage.lineIndentLevel(sp.window.curPage.curLine)
	# crt = getCurReturnUnit()
	crt = "\r\n"
	# ajustement des niveaux d'indentation du texte à coller à partir de ces informations
	gap = lstLevel[0] - curLevel
	for i in range(0, n): lstLevel[i] = lstLevel[i] - gap
	# réassignement des lignes
	lstLevel[0] = 0 # la première ligne doit être sans indentation
	for i in range(0, n): lstLine[i] = (ciu * lstLevel[i]) + lstCode[i]
	# reconstitution du texte
	s = crt.join(lstLine)
	# insertion comme sélection courante
	sp.window.curPage.selectedText = s
	sp.window.curPage.selectionStart = sp.window.curPage.selectionEnd
# end def

def paste3():
	# collage classique de 6pad++
	alert("Impossibilité de revenir au type de collage classique de 6pad++ sans rechargement.\nVous devez impérativement redémarrer 6pad++ pour que le type de collage de texte classique soit restauré.", "Impossibilité de collage")
# end def

def loadPasteTools():
	# chargement ou rechargement des menus et raccourcis clavier
	global nbLoad, menuPasteType
	nbLoad = nbLoad + 1
	pasteType = sp.getConfig("currentPasteType", "3")
	if pasteType == "1":
		pasteAction = paste1
	elif pasteType == "2":
		pasteAction = paste2
	elif pasteType == "3":
		pasteAction = paste3
	# end if
	# remplacement du menu coller
	mnu = sp.window.menus["edit"]
	try:
		# recherche de la position du menu couper
		# et insertion des menus du choix du type de collage
		for i in range(0, mnu.length):
			if mnu[i].name == "paste":
				# Si les menus du choix du type de collage n'ont pas encore été créés
				if mnu["pasteTypes"] == None:
					# ils n'existent pas, on les crée
					menuPasteType = mnu.add(label = "Types de collage", name = "pasteTypes", submenu = True, index = i + 1)
					menuPasteType.add(label = "Collage &simple de texte", action = choosePaste1)
					menuPasteType.add(label = "Collage de code &python", action = choosePaste2)
					menuPasteType.add(label = "Collage &classique de 6pad++", action = choosePaste3)
					# cochage du bon menu
					menuPasteType[int(pasteType) - 1].checked = True
				# end if
				# sous certaines conditions, élimination du menu coller
				if not(nbLoad == 1 and pasteType == "3"):
					mnu[i].remove()
					# création d'une autre version de ce menu
					mnu.add(label = "Coller", name = "paste", action = pasteAction, accelerator = "CTRL+V", index = i)
				# end if
				break
			# end if
		# end for
	except: pass
	# sous certaines conditions, modification du raccourci sans menu
	if not(nbLoad == 1 and pasteType == "3"):
		i = sp.window.findAcceleratorByKey("CTRL+V")
		if i > 0:
			try: sp.window.RemoveAccelerator(i)
			except: pass
			# alert(sp.window.findAcceleratorByID(i))
			# réassignation du raccourci
			sp.window.addAccelerator("CTRL+V", pasteAction)
		# end if
	# end if
# end def

def unloadPasteTools():
	# déchargement des menus et raccourcis clavier
	global nbLoad, menuPasteType
	nbLoad = 0
	menuPasteType.remove()
# end def

# Si vous voulez utiliser ce module de manière autonome, 
# veuillez décommenter la ligne suivante
# loadPasteTools()
