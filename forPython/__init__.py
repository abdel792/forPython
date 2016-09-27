# -*- coding: utf-8 -*-
# Extension forPython pour le 6pad++
# transformant cet éditeur de texte scriptable en véritable IDE de développement pour le langage python
# réalisé par:
# Abdel (abdelkrim.bensaid@free.fr)
# Yannick Youalé (mailtoloco2011@gmail.com) Cameroun
# Cyrille (cyrille.bougot2@laposte.net)
# avec les contributions de:
# QuentinC
# Jean-François Collas
# Mathieu Barbe
# Tous les membres de la progliste (une liste de discussion francophone de programmeurs déficients visuels)
# Débuté en janvier 2016

# Importation des modules.
import sixpad as sp
import inspect
import pkgutil
import sys
import time
import traceback
import re
import os
import webbrowser
import shlex
import subprocess
import io
import importlib
from threading import Timer

alert = sp.window.alert

# Dictionnaire pour les regexps.
regexp={
	"regClsPython":"^[ \t]*class[^\\w\\d_].*?:.*",
	"regFuncPython":"^[ \t]*def[^\\w\\d_].*?:.*",
	"regClsAndFuncPython":"^[ \t]*((?:class|def)[^\\w\\d_].*?:.*$)"
	}

# Liste pour les versions de Python.
pythonVersionsList = ["6padPythonVersion"]

# Variables globales.
mode = 0
curPythonVersion = sp.getConfig("curPythonVersion", "6padPythonVersion")
okd = oku = po = 0 # Pour les événements onKeyDown, onKeyUp et pageOpened.
# pour les accélérateurs ajoutés
# g_key1=0
# g_key2 = 0
menuForPython = menuView = menuAccessibility = menuModifyAccelerators = menuPythonVersion = menuLineHeadings = menuSelection = menuInsertion = menuDeletion = menuExecution = menuNavigation = menuTags = menuExploration = None # Pour les menus du forPython
idTmrLineMove = 0
iLastLine = 0
sLastLine = ""
flagCheckLineMove = True
flagCheckLine = True
curProc = object() # Pour contrôler le processus en cours d'exécution.
# pour retenir le niveau d'indentation changeant
lastDifferentIndentLevel = sp.window.curPage.lineIndentLevel(sp.window.curPage.curLine)

# liste pour les fichiers d'aide liés aux versions installées de python
gLstPythonHelpFiles = []

# paramètres de configuration
gWayOfActivatingForPython = sp.getConfig("WayOfActivatingForPython", "1")
gCheckLineSyntax = (sp.getConfig("forPythonCheckLineSyntax", "1") == "1")
gGoToLineOfError = (sp.getConfig("forPythonGoToLineOfError", "1") == "1")
gShowErrorsIn = sp.getConfig("forPythonShowErrorsIn", "1")
gWriteErrorsInLogFile = (sp.getConfig("forPythonWriteErrorsInLogFile", "1") == "1")
gAddEndTagsAtCodeCompletion = (sp.getConfig("AddEndTagsAtCodeCompletion", "0") == "1")
gPythonExtensionsSupported = sp.getConfig("PythonExtensionsSupported", "py, pyw").replace(" ", "").split(",")

def activeForPythonExtension():
	# Activation/désactivation des outils de l'extension forPython
	sp.window.menus.tools["forPythonActivation"].checked = not sp.window.menus.tools["forPythonActivation"].checked
	if sp.window.menus.tools["forPythonActivation"].checked == True:
		sp.setConfig("forPythonActivation", "1")
		loadForPythonTools()
		sayText("Activation du forPython")
	else:
		sp.setConfig("forPythonActivation", "0")
		unloadForPythonTools()
		sayText("Désactivation du forPython")
	# end if
# end def

def toggleMode():
	if mode == 0:
		sayLineNumber()
		sayText("Dire les numéros de lignes", True)
	elif mode == 1:
		sayIndentation()
		sayText("Dire les indentations", True)
	elif mode == 2:
		sayLineAndIndentation()
		sayText("Dire les numéros de lignes et les indentations", True)
	elif mode == 3:
		sayLevel()
		sayText("Dire les niveaux", True)
	elif mode == 4:
		sayLineAndLevel()
		sayText("Dire les numéros de lignes et les niveaux", True)
	elif mode == 5:
		sayNothing()
		sayText("Ne rien dire", True)

def toggleVocalSynthesis():
	# active ou désactive la synthèse vocale
	global flagVocalSynthesis
	mnu = sp.window.menus["accessibility"]["vocalSynthesis"]
	mnu.checked = not(mnu.checked)
	flagVocalSynthesis = mnu.checked
# end def

def onKeyDown(page, vk):
	# sayText(str(vk))
	# si la touche est FLH, CTRL+FLH, CTRL+HOME, PGUp
	if vk in[38, 550, 548, 33]:
		# et qu'on est à la première ligne
		if page.curLine == 0: sp.window.messageBeep(0)
	# end if
	# si la touche est FLB, CTRL+FLB, CTRL+END, PGDown
	if vk in[40, 552, 547, 34]:
		# et qu'on est à la dernière ligne
		if page.curLine == page.lineCount - 1: sp.window.messageBeep(0)
	# end if
	# les commande d'exploration de blocs
	if vk == 2085: # alt+left
		navigateLeft()
		return False
	elif vk == 2087: # alt+right
		navigateRight()
		return False
	elif vk == 2086: # alt+up
		navigateUp()
		return False
	elif vk == 2088:
		navigateDown()
		return False
	# end if
	return True
# end def

def onKeyUp(page, vk):
	global lastDifferentIndentLevel
	# Pour les touches tab et Shift + Tab.
	if vk in [9, 1033] and page.position == page.lineSafeStartOffset(page.curLine) and not page.selectedText:
		sayText("Niveau " + str(page.lineIndentLevel(page.curLine)) + ". " + page.line(page.curLine), True)
		return False
	# Pour la touche BackSpace.
	if vk == 8 and not page.selectedText and page.position == page.lineSafeStartOffset(page.curLine):
		# Si les paramètres d'indentation sont de 1 Tab ou de 1 espace, on donne le niveau.
		if page.indentation in [0, 1]:
			sayText("Niveau " + str(page.lineIndentLevel(page.curLine)) + ". " + page.line(page.curLine), True)
		else:
			# Le niveau d'indentation est fixé sur plus d'une espace, on donne donc le nombre d'indentations.
			sayText(getIndentation() + ". " + page.line(page.curLine), True)
		return False
	# Si la touche est FLH, FLB, CTRL+Home, CTRL+END, PGUp, PGDown, CTRL+Up, CTRL+Down.
	# On donne les informations selon le mode de lecture d'entêtes utilisé.
	if vk in[33, 34, 38, 40, 547, 548, 550, 552] and not page.selectedText:
		if mode == 4 and menuReadIndentOnlyWhenChange.checked == True: # lecture des niveaux d'indentation
			if lastDifferentIndentLevel != page.lineIndentLevel(page.curLine):
				sayText(getLineHeading(page.curLine), True)
				lastDifferentIndentLevel = page.lineIndentLevel(page.curLine)
			else:
				sayText(page.curLineText, True)
			# end if
		else:
			sayText(getLineHeading(page.curLine), True)
		# end if
		return False
	# end if
	return True

def getLineHeading(line):
	lineNumber = str(line+1) + ". "
	indentation = getIndentation() + ". "
	lineAndIndentation = lineNumber + indentation
	level = "niveau " + str(sp.window.curPage.lineIndentLevel(line)) + ". "
	lineAndLevel = lineNumber + level
	if mode == 0:
		sayLine = ""
		sayIndentation = ""
		sayLineAndIndentation = ""
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 1:
		sayLine = lineNumber
		sayIndentation = ""
		sayLineAndIndentation = ""
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 2:
		sayLine = ""
		sayIndentation = indentation
		sayLineAndIndentation = ""
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 3:
		sayLine = ""
		sayIndentation = ""
		sayLineAndIndentation = lineAndIndentation
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 4:
		sayLine = ""
		sayIndentation = ""
		sayLineAndIndentation = ""
		sayLevel = level
		sayLineAndLevel = ""
	elif mode == 5:
		sayLine = ""
		sayIndentation = ""
		sayLineAndIndentation = ""
		sayLevel = ""
		sayLineAndLevel = lineAndLevel
	return "%s%s%s%s%s%s" % (sayLine, sayIndentation, sayLineAndIndentation, sayLevel, sayLineAndLevel, sp.window.curPage.line(line))

def getIndentation():
	iIndent = 0
	sIndent = ""
	if sp.window.curPage.line(sp.window.curPage.curLine) == "":
		return "Vide"
	if sp.window.curPage.lineStartOffset(sp.window.curPage.curLine) != sp.window.curPage.lineSafeStartOffset(sp.window.curPage.curLine):
		iFirstChar = sp.window.curPage.lineStartOffset(sp.window.curPage.curLine)
		sIndentChar = sp.window.curPage.text[iFirstChar]
		if sIndentChar == " ":
			sMarker =  " espaces"
		elif sIndentChar == "\t":
			sMarker = " tabs"
		sTemp = sp.window.curPage.line(sp.window.curPage.curLine)
		i = 100
		while len(sTemp) > 0 and i > 0:
			i -= 1
			sFirstChar = sTemp[:1]
			sTemp = sTemp[1:]
			if sFirstChar != " " and sFirstChar != "\t":
				sIndent = sIndent + "|" + str(iIndent) + sMarker
				return sIndent[1:]
			if sFirstChar == sIndentChar:
				iIndent += 1
			else:
				sIndent = sIndent + "|" + str(iIndent) + sMarker
				iIndent = 1
				sIndentChar = sFirstChar
				if sMarker == " espaces":
					sMarker = " tabs"
				else:
					sMarker = " espaces"
		if iIndent != 0:
			sIndent = sIndent + "|" + str(iIndent) + sMarker
		if i == 0:
			return ""
		return sIndent[1:]
	else:
		return ""

def openedPage(newPage):
	""" A l'ouverture d'une page """
	# ajout des évènements dans la nouvelle page
	newPage.__setattr__("okd", newPage.addEvent("keyDown", onKeyDown))
	newPage.__setattr__("oku", newPage.addEvent("keyUp", onKeyUp))
	newPage.__setattr__("opc", newPage.addEvent("close", onPageClose))
	# si fichier python
	# désactivation du if suivant
	# if isPythonFile(newPage):
		# loadForPythonTools()
	# # end if
	# ajout de l'évènement de prise de focus à la page
	try: newPage.addEvent("activated", onPageActivated)
	except: pass
	# si demande d'ajout de balise de fin de bloc au démarrage
	if sp.getConfig("AddEndTagsAtFileLoading", "0") == "1":
		addTagsInPage(newPage)
	# end if
# end def

	def onPageActivated(page):
		# à l'affichage d'une page
		sp.window.messageBeep(0)
# end def

def onPageClose(page):
	""" A la fermeture de page """
	# alert("fermeture de page")
	return True
# end def

def parseElement(element):
	offset = sp.window.curPage.text.index(element)
	lineNumber = sp.window.curPage.lineOfOffset(offset)
	regClass = re.compile(regexp["regClsPython"], re.MULTILINE)
	if regClass.match(element):
		key = "%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "classe", sp.window.curPage.lineIndentLevel(lineNumber))
	else:
		key = "%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "fonction", sp.window.curPage.lineIndentLevel(lineNumber))
	return key

def getFunctionName():
	regFunc = re.compile(regexp["regFuncPython"], re.MULTILINE)
	if regFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regFunc.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	funcName = parseElement(sp.window.curPage.line(i)).split(" ")[0]
	return funcName

def getClassName():
	regClass = re.compile(regexp["regClsPython"], re.MULTILINE)
	if regClass.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regClass.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	className = parseElement(sp.window.curPage.line(i)).split(" ")[0]
	return className

def nextElement():
	regClassAndFunc = re.compile(regexp["regClsAndFuncPython"], re.MULTILINE)
	if regClassAndFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine < sp.window.curPage.lineCount:
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i < sp.window.curPage.lineCount and not regClassAndFunc.match(sp.window.curPage.line(i)):
		i += 1
		if i == sp.window.curPage.lineCount:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sayText(getLineHeading(sp.window.curPage.curLine), True)
	sayText("line " + str(i + 1))

def previousElement():
	regClassAndFunc = re.compile(regexp["regClsAndFuncPython"], re.MULTILINE)
	if regClassAndFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine > 0:
		i = sp.window.curPage.curLine - 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regClassAndFunc.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sayText(getLineHeading(sp.window.curPage.curLine), True)
	sayText("line " + str(i + 1))

def nextClass():
	regClass = re.compile(regexp["regClsPython"], re.MULTILINE)
	if regClass.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine < sp.window.curPage.lineCount:
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i < sp.window.curPage.lineCount and not regClass.match(sp.window.curPage.line(i)):
		i += 1
		if i == sp.window.curPage.lineCount:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sayText(getLineHeading(sp.window.curPage.curLine), True)
	sayText("line " + str(i + 1))

def previousClass():
	regClass = re.compile(regexp["regClsPython"], re.MULTILINE)
	if regClass.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine > 0:
		i = sp.window.curPage.curLine - 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regClass.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sayText(getLineHeading(sp.window.curPage.curLine), True)
	sayText("line " + str(i + 1))

def selectionFunction():
	regFunc = re.compile(regexp["regFuncPython"], re.MULTILINE)
	regClassAndFunc = re.compile(regexp["regClsAndFuncPython"], re.MULTILINE)
	if regFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regFunc.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	sp.window.curPage.curLine = i
	startOffset = sp.window.curPage.lineStartOffset(i)
	endOffset = sp.window.curPage.lineEndOffset(sp.window.curPage.lineCount - 1)
	text = sp.window.curPage.substring(startOffset, endOffset)
	mySel = regClassAndFunc.findall(text)
	selectedText = text if len(mySel) < 2 else text.split(mySel[1])[0]
	sp.window.curPage.selectedText = selectedText
	return True

def selectionClass():
	regClass = re.compile(regexp["regClsPython"], re.MULTILINE)
	if regClass.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regClass.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	sp.window.curPage.curLine = i
	startOffset = sp.window.curPage.lineStartOffset(i)
	endOffset = sp.window.curPage.lineEndOffset(sp.window.curPage.lineCount - 1)
	text = sp.window.curPage.substring(startOffset, endOffset)
	mySel = regClass.findall(text)
	selectedText = text if len(mySel) < 2 else text.split(mySel[1])[0]
	sp.window.curPage.selectedText = selectedText
	return True

def selectCurrentFunction():
	""" sélectionne la fonction sous le curseur """
	page = sp.window.curPage
	curLine = page.curLine
	# on fait dresser la liste des limites des principaux  blocs
	lstBlocsLimits = getBlocsLimits(page.text)
	# on détermine si le curseur est à l'intérieur d'une fonction
	if isWithinFunction(curLine, lstBlocsLimits) == False:
		sayText("Aucune fonction sous le curseur à sélectionner !", True)
		sp.window.messageBeep(0)
		return
	# end if
	# recherche et sélection dans la liste des limites de blocs
	# en commençant par la fin
	i = len(lstBlocsLimits) - 1
	while (i >= 0):
		indent, key, name, d, f, ln = lstBlocsLimits[i]
		# si fonction def
		if key == "def":
			# si la ligne courante est dans ses limites
			if curLine >= d and curLine <= f:
				# sélection
				sayText("Sélection de la fonction " + name)
				page.selectionStart = page.lineStartOffset(d)
				page.selectionEnd = page.lineEndOffset(f)
				return
			# end if
		# end if
		i -= 1 # décrémentation
	# end while
	sp.window.messageBeep(0) # erreur
# end def

def selectCurrentFunction2():
	funcName = getFunctionName()
	if not funcName:
		sayText("Aucune fonction à sélectionner !", True)
		return
	text = sp.window.curPage.text
	if selectionFunction():
		sayText("Fonction %s sélectionnée !" % (funcName), True)
		sp.window.curPage.text = text
	else:
		sayText("Impossible de sélectionner la fonction %s" % (funcName), True)

def selectCurrentClass():
	""" sélectionne la classe sous le curseur """
	page = sp.window.curPage
	curLine = page.curLine
	# on fait dresser la liste des limites des principaux  blocs
	lstBlocsLimits = getBlocsLimits(page.text)
	# on détermine si le curseur est à l'intérieur d'une classe
	if isWithinClass(curLine, lstBlocsLimits) == False:
		sayText("Aucune classe sous le curseur à sélectionner !", True)
		sp.window.messageBeep(0)
		return
	# end if
	# recherche et sélection dans la liste des limites de blocs
	# en commençant par la fin
	i = len(lstBlocsLimits) - 1
	while (i >= 0):
		indent, key, name, d, f, ln = lstBlocsLimits[i]
		# si classe
		if key == "class":
			# si la ligne courante est dans ses limites
			if curLine >= d and curLine <= f:
				# sélection
				sayText("Sélection de la classe " + name)
				page.selectionStart = page.lineStartOffset(d)
				page.selectionEnd = page.lineEndOffset(f)
				return
			# end if
		# end if
		i -= 1 # décrémentation
	# end while
	sp.window.messageBeep(0) # erreur
# end def

def selectCurrentClass2():
	className = getClassName()
	if not className:
		sayText("Aucune classe à sélectionner !", True)
		return
	text = sp.window.curPage.text
	if selectionClass():
		sayText("Classe %s sélectionnée !" % (className), True)
		sp.window.curPage.text = text
	else:
		sayText("Impossible de sélectionner la classe %s" % (className), True)

def deleteCurrentFunction():
	funcName = getFunctionName()
	if not funcName:
		sayText("Il n'y a pas de fonction à supprimer", True)
		return
	confirmation = sp.window.confirm("Êtes vous sur de vouloir supprimer la fonction %s?" % (funcName), "Confirmation de suppression")
	if confirmation == 0:
		return
	if selectionFunction():
		sp.window.curPage.text = sp.window.curPage.text.replace(sp.window.curPage.selectedText, "")
		sp.window.curPage.save()
	else:
		sayText("Impossible de supprimer la fonction %s" % (funcName), True)

def deleteCurrentClass():
	className = getClassName()
	if not className:
		sayText("Il n'y a pas de classe à supprimer", True)
		return
	confirmation = sp.window.confirm("Êtes vous sur de vouloir supprimer la classe %s?" % (className), "Confirmation de suppression")
	if confirmation == 0:
		return
	if selectionClass():
		sp.window.curPage.text = sp.window.curPage.text.replace(sp.window.curPage.selectedText, "")
		sp.window.curPage.save()
	else:
		sayText("Impossible de supprimer la classe %s" % (className), True)

def selectAClassOrFunction():
	regClassAndFunc = re.compile(regexp["regClsAndFuncPython"], re.MULTILINE)
	choices = regClassAndFunc.findall(sp.window.curPage.text)
	if choices:
		choices = [k.strip() for k in choices]
		choicesList = [parseElement(k) for k in choices]
		i = sp.window.curPage.curLine
		while i > -1 and not regClassAndFunc.match(sp.window.curPage.line(i)):
			i -= 1
			if i == -1:
				i = sp.window.curPage.text.index(choices[0])
				i = sp.window.curPage.lineOfOffset(i)
				break
		element = sp.window.choice("Veuillez sélectionner une classe ou fonction", "Liste d'éléments", choicesList, choices.index(sp.window.curPage.line(i).strip()))
		if element == -1:
			return
		offset = sp.window.curPage.text.index(choices[element])
		lineNumber = sp.window.curPage.lineOfOffset(offset)
		sp.window.curPage.curLine = lineNumber
		sayText(getLineHeading(lineNumber), True)
	else:
		sayText("Aucune classe ou fonction trouvée !", True)

def sayNothing():
	global mode, menuLineHeadings
	mode = 0
	menuLineHeadings.nothing.checked = True
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayLineNumber ():
	global mode, menuLineHeadings
	mode = 1
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = True
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayIndentation ():
	global mode, menuLineHeadings
	mode = 2
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = True
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayLineAndIndentation ():
	global mode
	mode = 3
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = True
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayLevel ():
	global mode
	mode = 4
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = True
	menuLineHeadings.lineAndLevel.checked = False

def sayLineAndLevel ():
	global mode
	mode = 5
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = True

def deleteCurrentLine ():
	# supprime la ligne ou les lignes sélectionnées sous le curseur
	nb = 0
	iLineStart, iLineEnd, j = 0, 0, 0
	d, f = 0, 0
	# on trouve le nombre de lignes total du document
	nb = sp.window.curPage.lineOfOffset (len(sp.window.curPage.text))
	# on trouve les numéros des lignes de début et de fin
	iLineStart = sp.window.curPage.lineOfOffset (sp.window.curPage.selectionStart)
	iLineEnd = sp.window.curPage.lineOfOffset (sp.window.curPage.selectionEnd)
	# on identifie la position de début du texte à supprimer
	d = sp.window.curPage.lineStartOffset(iLineStart)
	# on identifie la position de fin du texte à supprimer
	# si la fin est la dernière ligne
	if iLineEnd == nb:
		# la position de fin est la fin de tout le texte
		f = len(sp.window.curPage.text)
	else: # ce n'est pas la dernière ligne
		# la fin est le début de la ligne suivante
		f = sp.window.curPage.lineStartOffset(iLineEnd+1)
	# end--if
	# sélection de la portion à supprimer
	sp.window.curPage.select(d, f)
	# suppression
	sp.window.curPage.selectedText = ""
	sayText("Suppression de ligne", True)
	# lecture de la nouvelle ligne courante
	sayText(sp.window.curPage.line(sp.window.curPage.curLine))
# end--def

def insertHeaderStatement():
	""" Insère une instruction d'en-tête de fichier à l'emplacement du curseur """
	sFile = os.path.join(getCurScriptFolderPath(), "data\\statements.txt")
	if os.path.isfile(sFile):
		path = open(sFile,'r')
		s = path.read() # Récupération du contenu du fichier
		path.close() # Fermeture du fichier
		lignes = s.split("\n")
		lignes.remove("") # retrait des éléments vides
		i = sp.window.choice("Veuillez sélectionner une instruction d'en-tête de fichier à insérer", "Instructions d'en-tête de fichier", lignes, 1)
		if i >= 0:
			sp.window.curPage.insert(sp.window.curPage.selectionStart, lignes[i])
	else:
		sp.window.alert("Le fichier %s est introuvable près de l'extension 'forPython' \nVeuillez l'y installer et recommencer cette action." % sFile, "Fichier introuvable")
		return

def insertImportStatement():
	""" Insère une instruction d'importation à l'emplacement du curseur """
	alert("Insertion d'une instruction import encore en construction")
# end def

def insertFileRef():
	""" Insère une référence à un fichier à l'emplacement du curseur """
	page = sp.window.curPage
	# si aucun fichier dans l'onglet courant
	if page.file == "":
		alert("Vous devez d'abord enregistrer le fichier courant avant de tenter cette action.", "Fichier non enregistré")
		return
	# end if
	# openDialog(file= €˜', title='', filters=[], initialFilter=0, multiple=False) -> 
	path = sp.window.openDialog(title = "Choisissez le fichier", file = page.file)
	if path == None or path == "": return
	# choix du type de renvoi
	lst = ["Chemin absolu", "Chemin relatif", "Référence python"]
	i = sp.window.choice("Choisissez le type de référence à insérer à l'emplacement du curseur", "Insertion", lst)
	if i == None or i < 0: return
	if i == 0: # chemin absolu
		page.selectedText = path
	elif i == 1: # chemin relatif
		lst1 = page.file.split("\\")
		limit = len(lst1) - 1
		lst2 = path.split("\\")
		lst2 = lst2[limit:]
		page.selectedText = "/".join(lst2)
	elif i == 2: # référence python
		is6padInterpretor = (sp.getConfig("curPythonVersion", "6padPythonVersion") == "6padPythonVersion")
		page.selectedText = getModuleRef(path, is6padInterpretor)
	# end if
# end def

def getCurScriptFolderPath():
	sPath = inspect.getfile(inspect.currentframe())
	sPath = os.path.dirname(sPath)
	return sPath

def manageMenus():
	global menuForPython
	# On définit l'index des menus à ajouter.
	idx = -2 if menuForPython[-1].name == "runAPythonCodeOrModule" else -1
	# On vérifie qu'on est bien avec un Python indépendant du 6pad++.
	if curPythonVersion != "6padPythonVersion":
		if menuForPython.enterACommand == None:
			menuForPython.add(label = "En&trer une commande manuellement", index = idx, action = enterACommand, name = "enterACommand")
		# On vérifie qu'on est bien avec une version 2 ou supérieure de Python.
		if int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
			if menuForPython.installPackageWithSetup == None:
				menuForPython.add(label = "Ins&taller un package avec un script setup.py", index = idx, action = installPackageFromSetupScript, name = "installPackageWithSetup")
		else:
			# La version de Python utilisée est inférieure à la version 2.
			# On supprime donc les menus et clés de dictionnaire dont on aura pas besoin.
			menuForPython.remove(name = "installPackageWithSetup")
			menuForPython.remove(name = "compileScriptWithPy2exeP27")
			menuForPython.remove(name = "pipMenu")
		#idx = -3 if menuForPython.enterACommand == None else -4
		# On vérifie si l'on peut ajouter le sous-menu des commandes PIP.
		if os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
			if menuForPython.pipMenu == None:
				pipMenu = menuForPython.add(label = "Commandes &PIP", index = 7, submenu = True, name = "pipMenu")
				pipMenu.add(label = "Me&ttre à jour pip", action = updatePip, name = "updatePip")
				pipMenu.add(label = "E&xécuter une commande PIP à partir d'une liste", action = executeAPipCommandFromAList, name = "executeAPipCommandFromAList")
			# On vérifie si l'on est avec Python 27 pour l'ajout de la compilation avec Py2exe compatible Python 27.
			if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
				if menuForPython.compileScriptWithPy2exeP27 == None:
					menuForPython.add(label = "C&ompiler avec Py2exe pour Python 27", index = idx, action = compileScriptWithPy2exeP27, name = "compileScriptWithPy2exeP27")
			else:
				menuForPython.remove(name = "compileScriptWithPy2exeP27")
	else:
		# On utilise le Python embarqué avec 6pad++.
		# On supprime donc les menus et clés de dictionnaire inutiles.
		menuForPython.remove(name = "installPackageWithSetup")
		menuForPython.remove(name = "compileScriptWithPy2exeP27")
		menuForPython.remove(name = "pipMenu")
		menuForPython.remove(name = "enterACommand")

def make_action(i, f, exFile=None):
	def action():
		global curPythonVersion
		menuName = f
		curPythonVersion = "6padPythonVersion" if not exFile else exFile
		for x in range(menuPythonVersion.length):
			if x != i:
				menuPythonVersion[x].checked = False
			else:
				menuPythonVersion[x].checked = True
		sp.setConfig("curPythonVersion", curPythonVersion)
		sp.window.alert("C'est bon, %s a bien été activé !" % (curPythonVersion), "Confirmation")
		manageMenus()
	return action

def runHelpFile(path):
	# au click dans le menu aide
	# exécute un fichier d'aide
	os.popen('"' + path + '"')
# end def

def writeToFileAndScreen(cmd, logfile, curDirectory = ""):
	# Permet d'exécuter le module encours avec subprocess.Popen, puis de diriger la sortie vers la console, ainsi que vers le fichier logfile.log.
	# Cette fonction ne s'applique que lorsque le curPythonVersion est différent du Python embarqué avec 6pad++.
	
	# changement du repertoire de travail
	# pour éviter les erreurs de fichiers non trouvés
	if curDirectory == "": curDirectory = os.path.dirname(sp.window.curPage.file)
	os.chdir(curDirectory)
	
	# Les 2 lignes de code suivantes permettent d'éviter l'ouverture de la console lors de l'exécution.
	# La valeur de la variable startupinfo sera alors affectée au paramètre startupinfo de la classe Popen.
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	# On fait en sorte que le stdout comprenne le stderr pour faciliter l'analyse des erreurs.
	# Le paramètre universal_newlines de subprocess.Popen et fixé sur True afin d'obtenir les données directement en unicode, ce qui devrait nous permettre d'éviter de les décoder.
	proc = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines=True, shell = True, startupinfo = startupinfo)
	# On crée une liste qui sera convertie plus bas en string et retournée par la fonction, en vue d'analyser les éventuels messages d'erreur.
	l = []
	# On itère sur le proc.stdout.
	for line in proc.stdout:
		# On écrit dans le fichier de log, ligne par ligne.
		if line:
			logfile.write(line)
			# On dirige vers la console, ligne par ligne.
			if sys.stdout:
				sys.stdout.write(line)
			# On ajoute chaque ligne dans la liste sous la forme d'élément de liste.
			l.append(line)
	proc.wait()
	# On retourne la liste créée sous la forme d'une string.
	return "\r\n".join(l)

def goToLineError(errorMessage):
	# Permet de retrouver la ligne d'erreur et de l'atteindre.
	# On initialise les erreurs à rechercher.
	f = l = f1 = l1 = ""
	# On crée une regexp qui va capturer 2 partie du messages d'erreur.
	# 1. La partie concernant Le fichier comportant l'erreur et son chemin.
	# 2. La ligne où se trouve l'erreur, qui nous aidera pour l'atteindre.
	# Cette regex va retourner une liste de tuples correspondant à chaque item trouvé.
	find=re.findall("(?<=file \")([^\"]+)\", line (\d+)", errorMessage, re.I|re.M)
	# On crée une variable pour stocker la page courante.
	page = sp.window.curPage
	# On crée une liste de tous les onglets ouverts.
	mod = [p.file for p in sp.window.pages]
	# On itère à partir de la fin parmi les éléments de la liste pour trouver le module en cours.
	# La recherche se fera parmi tous les modules ouverts dans 6pad++.
	# On inverse la liste de lignes d'erreurs trouvées pour commencer à partir de la dernière.
	find.reverse()
	# On crée une expression pour chercher la correspondance de l'erreur trouvée avec les modules ouverts.
	for item1, item2 in find:
		if item1 in mod:
			# On affecte les variables f et l au tuple trouvé.
			f, l = item1, item2
			# On stoppe l'itération pour ne récupérer que la première erreur à partir de la fin.
			break
	if not f and not l:
		f1, l1 = find[0]
		# Le module comportant l'erreur n'est pas disponible.
		sp.window.alert("Le module comportant l'erreur est %s, à la ligne %s, c'est un module qu'il nous est impossible d'ouvrir.\nPour plus de détails, veuillez consulter la console ou le fichier logfile.log figurant dans le même répertoire que l'exécutable de 6pad++." % (f1, l1), "Erreur")
		return
	# On vérifie si f est bien le module actuellement ouvert.
	if f and l and f != page.file:
		# Le module actuellement ouvert n'est pas celui comportant l'erreur.
		# On l'ouvre et le définit comme étant le module courant.
		sp.window.open(f)
		# On réaffecte page à la page courante.
		page = sp.window.curPage
	# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
	sp.window.alert("Erreur détectée à la ligne %s, dans le fichier %s, veuillez valider sur OK pour atteindre la ligne concernée.\nPour plus de détails, veuillez consulter la console, ou le fichier logfile.log, figurant dans le même répertoire que l'exécutable de 6pad++" % (l, f), "Erreur")
	# On pointe sur la ligne concernée, dans le fichier comportant l'erreur.
	page.curLine = int(l) - 1

def execute6padModule(filepath):
	globals={
		"__file__":filepath,
		"__name__":"__main__"
	}
	with open(filepath, "r") as fd:
		exec(compile(fd.read(), filepath, "exec"), globals)

def updatePip():
	# On vérifie si pip est bien disponible.
	if not os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts\\pip.exe")):
		# Pip n'est pas installé dans notre version de Python.
		sp.window.alert("Pip n'est pas installé dans votre version de Python\nVeuillez utiliser une version de Python où pip est déja présent", "Erreur")
		return
	# pip est bien présent, on exécute la commande de mise à jour.
	cmd = [curPythonVersion, '-m', 'pip', 'install', '-U', 'pip']
	executeCommand(cmd)

def enterACommand():
	# Initialisation de la séquence de commandes à exécuter avec le module subprocess.
	cmd = []
	# Ajout du chemin de notre version de Python dans la séquence.
	cmd.append(curPythonVersion)
	prompt = sp.window.prompt("Veuillez entrer votre commande à exécuter.\nEntrez uniquement tout ce qui suit le nom de l'exécutable.\nPar exemple : \"-V\" pour connaitre votre version de Python, \"-h\" pour de l'aide, etc.\nLe résultat devrait alors s'afficher dans la console et dans le fichier logfile.log.", "Commande à exécuter")
	if not prompt:
		# On a validé sur annuler ou échappe.
		return
	# C'est bon, on peut exécuter notre commande.
	# Mais avant cela, on transforme la chaîne saisie par l'utilisateur en une séquence bien reconnue par subprocess.
	userCMD = shlex.split(prompt)
	cmd.extend(userCMD)
	# C'est bon, on exécute la commande.
	executeCommand(cmd)

def executeAPipCommandFromAList():
	# Création d'un dictionnaire comportant certaines commandes.
	commands = {}
	# Ajout de la commande d'installation de wxPython_Phoenix, pour les versions 3 de Python.
	if int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 2:
		commands["Installer wx.Python_Phoenix pour une version 3 de Python"] = [os.path.join(os.path.dirname(curPythonVersion), "Scripts\\pip.exe"), "install", "--upgrade", "--trusted-host", "wxpython.org", "--pre", "-f", "http://wxpython.org/Phoenix/snapshot-builds/", "wxPython_Phoenix"]
	# Ajout de la commande pour installer Py2exe, dans les version supérieures à Python 32.
	if int(curPythonVersion.split("\\")[-2].split("ython")[1][:2]) > 32:
		commands["Installer Py2exe pour une version 33 ou plus de Python"] = [curPythonVersion, "-m", "pip", "install", "-U", "py2exe"]
	# Création de notre liste de choix.
	choices = list(commands.keys())
	userChoice = sp.window.choice("Veuillez sélectionner une commande PIP à exécuter dans la liste", "Liste de commandes PIP disponibles", choices)
	if userChoice == -1:
		# On a validé sur annuler ou echappe.
		return
	# On exécute la commande PIP choisie par l'utilisateur.
	executeCommand(commands[choices[userChoice]])

def installPackageFromSetupScript():
	# On vérifie si les conditions sont bien réunies.
	if os.path.basename(sp.window.curPage.file) == "setup.py":
		# C'est bien un script setup.py, on vérifie quand même s'il n'est pas lié plutôt à py2exe.
		verify = [True for match in ["import py2exe", "from py2exe"] if match in sp.window.curPage.text]
		if not True in verify:
			# C'est bon, on peut exécuter notre commande.
			cmd = [curPythonVersion, sp.window.curPage.file, "install"]
			executeCommand(cmd)
		else:
			# C'est apparemment un script pour une compilation avec py2exe.
			sp.window.alert("Ce script est plutôt destiné à être compilé avec py2exe, veuillez l'exécuter avec le menu approprié", "Erreur")
	else:
		# Ce script n'est pas un script d'installation de package.
		sp.window.alert("Le module courant n'est pas un script d'installation, veuillez ouvrir un script setup.py d'installation de package pour utiliser cette action", "Erreur")

def compileScriptWithPy2exeP27():
	# On vérifie si les conditions sont bien réunies.
	if os.path.basename(sp.window.curPage.file) == "setup.py":
		# C'est bien un script setup.py, on vérifie maintenant qu'il est bien lié à py2exe.
		verify = [True for match in ["import py2exe", "from py2exe"] if match in sp.window.curPage.text]
		if True in verify:
			# C'est bon, on peut exécuter notre commande.
			# Mais avant cela, on vérifie quand même si Py2exe est bien installé.
			if not os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "lib", "site-packages", "py2exe")):
				# Py2exe n'est pas installé, on sort.
				sp.window.alert("Py2exe n'est pas installé dans votre version Python27, veuillez l'installer pour pouvoir exécuter cette action", "Erreur")
				return
			#Py2exe est bien installé, on peut continuer.
			cmd = [curPythonVersion, sp.window.curPage.file, "py2exe"]
			executeCommand(cmd)
		else:
			# Ce n'est apparemment pas un script pour compilation avec py2exe du python 27.
			sp.window.alert("Ce script n'est pas un setup pour Py2exe, veuillez l'exécuter avec le menu approprié", "Erreur")
	else:
		# Ce script n'est pas du tout un setup.
		sp.window.alert("Le module courant n'est pas un script de compilation avec Py2exe, veuillez ouvrir un script setup.py de compilation avec Py2exe pour utiliser cette action", "Erreur")

def executeCommand(cmd, curDirectory = ""):
	# On ouvre le fichier de log.
	f = open(os.path.join(sp.appdir, "logfile.log"), "w+")
	# On récupère le retour de writeToFileAndScreen.
	contains = writeToFileAndScreen(cmd, f, curDirectory)
	# On referme le fichier de log.
	f.close()
	# On vérifie s'il y a une erreur.
	if re.match(".+Error", contains, re.S) and re.match(".+File", contains, re.S) and re.match(".+line", contains, re.S):
		# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
		goToLineError(contains)

def addPythonVersionsSubMenus():
	# recensement des versions de python disponible dans le menu "versions de python"
	# On initialise l'index des sous-menus qui seront créés dans la boucle.
	i = 0
	# On crée une liste des dossier susceptibles de contenir un répertoire de Python.
	lstPath = []
	# On vérifie si le Python ainsi que la plateforme Windows sont récents.
	# Car Python 35 s'installe dans un répertoire particulier.
	if os.path.isdir(os.path.join(os.environ.get("USERPROFILE"), "Appdata\\Local\\Programs\\python")):
		# On ajoute le chemin à la liste lstPath.
		lstPath.append(os.path.join(os.environ.get("USERPROFILE"), "Appdata\\Local\\Programs\\python"))
	# end if
	# parcours de répertoires à la recherche d'installations de python
	vol = "CDEFGHIJ"
	for k in range(len(vol)):
		lstPath.extend (["%s:\\" % vol[k],
		"%s:\\Programs" % vol[k],
		"%s:\\Program Files" % vol[k],
		"%s:\\Program Files (x86)" % vol[k]]
		)
	# end for
	# On trie notre liste.
	lstPath.sort()
	for p in lstPath:
		# Si le répertoire existe vraiment.
		if os.path.isdir(p):
			for f in os.listdir(p):
				# S'il contient bien un dossier d'une éventuelle version de Python.
				if re.match("^python\d\.?\d", f, re.I):
					# On vérifie la présence de l'exécutable.
					if os.path.isfile(os.path.join(p, f, "python.exe")):
						# L'exécutable existe bien, on affecte son chemin à la variable exFile.
						exFile = os.path.join(p, f, "python.exe")
						# On incrémente l'index des sous-menus qui seront créés plus bas.
						i += 1
						# On crée le sous-menu correspondant.
						menuPythonVersion.add(label = "%s - %s" % (f, str(os.path.join(p, f))), action = make_action(i, f, exFile), name = f)
						# On remplit la liste pythonVersionsList déclarée en début de module.
						pythonVersionsList.append(exFile)
						# on tente d'ajouter les fichier d'aide qui lui sont liés au menu aide
						addPythonHelpFilesToMenu(os.path.join(p, f))
					# end if
				# end if
			# end for
		# end if si le repertoire existe vraiment
	# end for parcours des repertoires
	# on trouve et intègre les versions ajoutées manuellement conservés dans le fichier ini
	lstPath = sp.getConfigAsList("pythonVersionAddedManually")
	if len(lstPath) > 0:
		for p in lstPath:
			try:
				if os.path.isfile(p) == True:
					fldPath = os.path.dirname(p)
					fldName = os.path.basename(fldPath)
					# On incrémente l'index des sous-menus qui seront créés plus bas.
					i += 1
					# On crée le sous-menu correspondant.
					menuPythonVersion.add(label = "%s - %s" % (fldName, fldPath), action = make_action(i, fldName, p), name = fldName)
					# On remplit la liste pythonVersionsList déclarée en début de module.
					pythonVersionsList.append(p)
				# end if
			except: continue
		# end for
	# end if
	# ajout du menu pour désigner d'autres répertoires
	menuPythonVersion.add(label = "Localiser une version supplémentaire...", action = addPythonVersionManually, name = "addPythonVersionManually")
# end def

def addPythonVersionManually():
	# ajout manuel d'une version supplémentaire du python à prendre en compte
	global menuPythonVersion, pythonVersionsList
	fldPath = sp.window.chooseFolder("Désignez le répertoire de la version de python à ajouter")
	if os.path.isdir(fldPath) == False: return
	fldName = os.path.basename(fldPath)
	# vérification de la présence de l'éxécutable de l'interpréteur python
	exePath = os.path.join(fldPath, "python.exe")
	if os.path.isfile(exePath) == False:
		alert("Le fichier exécutable de l'interpréteur python est introuvable dans ce répertoire", "Exécutable introuvable")
		return
	# end if
	# recherche si ce chemin n'a pas déjà été recensé
	for p in pythonVersionsList:
		try:
			if os.path.samefile(p, exePath) == True:
				alert("Cet interpréteur python a déjà été recensé\n'" + exePath + "'", "Interpréteur python déjà recensé")
				return
			# end if
		except: continue
	# end for
	# identification de la position du nouveau menu à insérer
	i = len(pythonVersionsList)
	# On crée le sous-menu correspondant.
	menuPythonVersion.add(label = "%s - %s" % (fldName, fldPath), action = make_action(i, fldName, exePath), name = fldName, index = i)
	# On remplit la liste pythonVersionsList déclarée en début de module.
	pythonVersionsList.append(exePath)
	# on inscrit le chemin dans le fichier ini de configuration
	sp.setConfig(key = "pythonVersionAddedManually", value = exePath, multiple = True)
# end def

def addPythonHelpFilesToMenu(path):
	""" trouve les fichiers d'aide dans le dossier installé de python
	et les ajoute au menu aide."""
	if os.path.isdir(path) == False: return
	# recherche dans le dossier Doc
	path = os.path.join(path, "Doc")
	if os.path.isdir(path) == False: return
	for f in os.listdir(path):
		# si fichier chm
		if f[len(f) - 4:] == ".chm":
			# assurance de l'existence du menu des fichiers d'aide sur le langage
			if sp.window.menus["help"]["pythonHelpFiles"] == None: sp.window.menus["help"].add(name = "pythonHelpFiles", submenu = True, label = "Aide du langage python")
			mnu = sp.window.menus["help"]["pythonHelpFiles"]
			mnu.add(label = f + " de " + path, action = lambda:runHelpFile(os.path.join(path, f)))
			# ajout à la liste virtuelle
			gLstPythonHelpFiles.append(os.path.join(path, f))
		# end if
	# end for
# end def

def runAPythonCodeOrModule(curPage = None):
	# Permet d'exécuter le module désigné ou en cours d'exploration.
	# On crée si ce n'est déjà fait une variable pour la page courante
	if curPage == None: curPage = sp.window.curPage
	# on vérifie si cette page contient du code
	if not curPage.text:
		# Il n'y en a pas, on en informe l'utilisateur et on sort.
		sp.window.alert("Le module est vide, impossible donc d'exécuter le code", "Aucun contenu à exécuter")
		return
	# end if
	# On affecte une variable filePath pour garder le chemin vers le fichier courant.
	filePath = curPage.file
	# On vérifie si le fichier est bien sauvegardé.
	if not filePath:
		# le fichier n'est pas enregistré
		# on va exécuter son code via un module temporaire.
		filePath = os.path.join(sp.appdir, "tmp.py")
		# On y insère le contenu de notre fichier non sauvegardé.
		writeFile(filePath, curPage.text)
	# end if
	# Le module (temporaire ou pas) est bien sauvegardé et prêt à l'exécution.
	# vérification si l'interpréteur actuellement choisi est celui du 6pad++.
	if curPythonVersion== "6padPythonVersion":
		# On pointe vers le fichier courant en lecture.
		curFile = open(filePath, "r")
		# On définit le code à exécuter, qui n'est autre que tout le contenu du module courant.
		curFileCode = curFile.read()
		# On referme le fichier ouvert par open.
		curFile.close()
		# On sauvegarde la sortie standard sys.stdout.
		oldOutput = sys.stdout
		# On redirige la sortie standard vers StringIO().
		out = io.StringIO()
		sys.stdout = out
		try:
			# On execute le code.
			execute6padModule(filePath)
		except:
			# Il y a des erreurs.
			lines = traceback.format_exception(etype = sys.exc_info()[0], value = sys.exc_info()[1], tb = sys.exc_info()[2])
			# On remplit notre variable out en y introduisant le contenu de la sortie standard.
			print (''.join(line for line in lines))
		finally:
			# On restaure la sortie standard sys.stdout.
			sys.stdout = oldOutput
		# end try
		# On affecte notre variable contains au contenu de la redirection.
		contains = out.getvalue()
		# On ouvre le fichier de log en écriture.
		f = open(os.path.join(sp.appdir, "logfile.log"), "w+")
		# On enregistre dans le fichier logfile.log.
		f.write(contains)
		# On referme le fichier de log.
		f.close()
		# On affiche quand-même le contenu dans la console.
		print(contains)
		# On vérifie s'il y a une erreur.
		if re.match(".+Error", contains, re.S) and re.match(".+File", contains, re.S) and re.match(".+line", contains, re.S):
			# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
			goToLineError(contains)
		# end if
	else: # l'interpréteur actuellement choisi est celui d'un python classique
		# On crée la ligne de commande qui sera exécutée dans la fonction writeToFileAndScreen, grâce à subprocess.Popen.
		cmd = [curPythonVersion, filePath]
		# On exécute notre code.
		executeCommand(cmd, os.path.dirname(filePath))
	# end if
# end def

# xxxxxxxxxx

def runCompiler():
	""" Execute the code compiler if available """
	global curPythonVersion
	# le fichier courant est-il enregistré ?
	if sp.window.curPage.file == "":
		alert("Le document courant n'est pas enregistré.\nL'action de compilation va être annulée.")
		return
	# end if
	# quelle est l'interpréteur courant ?
	if curPythonVersion == "6padPythonVersion":
		alert("Vous ne pouvez compiler pour le 6pad++\nCela ne peut être possible que pour les autres interpréteurs de python installés sur votre ordinateur.\nDès lors, veuillez choisir dans le menu outils l'une des autres version de python installés sur cet ordinateur avant de retenter cette action.", "Compilation impossible")
		return
	# end if
	# le chemin vers l'interpréteur est-il valide ?
	pythonExePath = curPythonVersion
	if os.path.isfile(pythonExePath) == False:
		alert("Le chemin vers lexécutable de l'interpréteur python est introuvable\nL'action de compilation va être annulée")
		return
	# end if
	# on recueille le code modèle
	s = readFile(os.path.join(getCurScriptFolderPath(), "data\\sampleCompiler.txt"))
	if s == "":
		alert("Le code modèle est introuvable\nL'action de compilation va être annulée")
		return
	# end if
	# le nom du ou des fichiers à compiler
	pythonScriptName = sp.window.curPage.name
	# on l'insère dans le code à exécuter
	s = s.replace("\\scriptName\\", '"' + pythonScriptName + '"')
	# on insère le chemin pour la localisation du script
	s = s.replace("\\scriptFolder\\", os.path.dirname(sp.window.curPage.file))
	# on crée le fichier setup de la compilation
	pythonScriptPath = os.path.join(os.path.dirname(sp.window.curPage.file), "setup.py")
	# écriture du code de compilation dans ce fichier
	writeFile(pythonScriptPath, s)
	# exécution de la compilation
	# annonce
	sayText("Compilation")
	sayText("Veuillez patienter")
	# création de l'objet de retour
	file2 = ""
	# instruction qui envéront toute écriture dans la console vers le fichier créé.
	sys.stdout = file2
	sys.stderr = file2
	# variable à utiliser
	variable1 = ''
	variable2 = ''
	# changement du repertoire de travail
	# pour éviter les erreurs de fichiers non trouvés
	os.chdir(os.path.dirname(sp.window.curPage.file))
	# exécution
	si = subprocess.STARTUPINFO()
	si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	# exécution
	curProc = subprocess.Popen([pythonExePath, pythonScriptPath, "py2exe"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = si, universal_newlines = True)
	sResultConsole, sResultError = curProc.communicate()
	# try: sResultConsole = sResultConsole.decode()
	# except: sResultConsole=decode2(sResultConsole)
	if sResultConsole != "":
		sp.console.print(sResultConsole)
	# end if fin si texte de retour
# end def

def decode2(s):
	# décodage alternatif de texte renvoyé
	s = str(s)
	s = re.sub("^[ \\t]*[>]+[ \\t]+[a-z*]('|\") ([ \\w \\W] +) (' | \")[ \\t]*$", "\\2", s, 0, re.I)
	s = re.sub(r"\\r\\n", "\r\n", s)
	return s
# end def

def removeStringsFromCode(s):
	# retire  les chaînes string et les commentaires dans le code en paramètre
	lstString = []
	# pattern pour trouver tous les strings et commentaires
	pt = getStringPattern()
	# recherche
	lstString = finditer2list(pt, s)
	# remplacement des strings et commentaires par des génériques
	i = 0
	iStart = 0
	iEnd = 0
	s2 = s
	s = ""
	tag = "tag___yyd"
	for e in lstString:
		i = i + 1
		d, f = e.span(0)
		iEnd = d - 1
		s = s + s2[iStart: iEnd + 1] + tag + str(i) + "_"
		iStart = f
	# end for
	# ajout de la dernière portion
	try: s = s + s2[f:]
	except: pass
	# renvoi du texte et de la liste conservée des strings et commentaires
	return s, lstString
# end def

def restoreStringsInCode(s, lstString):
	# restoration des chaînes strings et commentaires dans le code en paramètre
	tag = "tag___yyd"
	i = 0
	for e in lstString:
		i = i + 1
		s = s.replace(tag + str(i) + "_", e.group(0), 1)
	# end for
	return s
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

def readFile(filePath, _mode = 'r'):
	# lit et renvoi le contenu d'un fichier texte
	fil = open(filePath, _mode)
	s = fil.read()
	fil.close() # Fermeture du fichier
	return s
# end def

def writeFile(filePath, s, _mode = 'w'):
	# Ecriture dans un fichier
	fil = open(filePath, _mode)
	fil.write(s)
	fil.close() # Fermeture du fichier
# end def

def getCurReturnUnit():
	# renvoi le caractère de retour à la ligne courant
	lst = ["\r\n", "\n", "\r"]
	return lst[sp.window.curPage.lineEnding]	
# end def

def getCurIndentUnit():
	# renvoi l'unité d'indentation du fichier courant
	i = sp.window.curPage.indentation
	if i == 0:
		return "\t"
	else:
		return " " * i
	# end if
# end def

def getCurExpression():
	""" retrieve the key word/expression under the cursor 
	as well as its position of start and end """
	s = sp.window.curPage.text
	if s == "": return "", 0, 0
	# recueillement de la position du curseur
	pos = sp.window.curPage.position
	iStart = pos
	iEnd = pos
	flag = False
	# recherche vers la droite
	expression = ""
	i = pos
	while(i < len(s)):
		sChar = s[i]
		if re.match("[a-zA-Z_\\d]", sChar, re.I):
			expression = expression + sChar
			iEnd = i
			flag = True
		else:
			break
		# end if
		i = i + 1 # incrémentation
	# end while
	# recherche vers la gauche
	# on incluera les points dans les caractères recherchés
	# ainsi que les englobants de crochets, accolades,  et parenthèses
	i = pos - 1
	while(i >= 0):
		sChar = s[i]
		if re.match("[a-zA-Z_\\d\\.]", sChar, re.I):
			expression = sChar + expression
			iStart = i
			if flag == False:
				iEnd = iStart
				flag = True
			# end if
		elif(sChar == ")" or sChar == "]" or sChar == "}") and s[i + 1] == ".":
			if sChar == ")": limit = "("
			if sChar == "]": limit = "["
			if sChar == "}": limit = "{"
			start = sChar
			balance = 1
			quote = ""
			inQuote = False
			# on inclus le caractère
			expression = sChar + expression
			iStart = i
			# on va également inclure le texte à gauche jusqu'à la limite
			i = i - 1
			while(i >= 0):
				sChar = s[i]
				if inQuote == True:
					if sChar == quote:
						if s[i - 1] != "\\": inQuote = False
					# end if
				else: # pas dans des quotes
					if sChar == "'" or sChar == '"':
						quote = sChar
						inQuote = True
					elif sChar == start:
						balance = balance + 1
					elif sChar == limit:
						balance = balance - 1
						if balance == 0:
							expression = sChar + expression
							iStart = i
							break
						# end if
					# end if
				# end if inQuote
				expression = sChar + expression
				iStart = i
				i = i - 1
			# end while
		else:
			break
		# end if
		iStart = i
		i = i - 1 # décrémentation
	# end while 
	# if iEnd>iStart: iEnd=iEnd+1
	return expression, iStart, iEnd
# end def

def getCurBlocName():
	# renvoi le nom du bloc (class ou def) dans lequel est positionné le curseur
	# dans le texte courant
	s = sp.window.curPage.text
	lstBlocsLimits = getBlocsLimits(s)
	i = sp.window.curPage.curLine
	lst = []
	for (curLevel, curKey, curName, d, f, e) in lstBlocsLimits:
		if i>=d and i<=f:
			if curKey == "def" or curKey == "class":
				lst.append(curKey+" "+curName)
			# end if
		# end if
	# end for
	lst.reverse()
	return "/".join(lst)
# end def

def getCurClassName(lstBlocsLimits, line):
	# renvoi le nom de la classe à l'emplacement du curseur
	i = len(lstBlocsLimits)
	while(i > 0):
		i = i - 1 # décrémentation
		indent, key, name, d, f, ln = lstBlocsLimits[i]
		if line >= d and line <= f:
			if key == "class":
				return name
			# end if
		# end if
	# end while	
	return ""
# end def

def getCurModuleDir():
	# renvoi le chemin vers le dossier contenant le script courant
	path = inspect.getfile(inspect.currentframe())
	return os.path.dirname(path)
# end def

def getCurInterpretorName():
	""" renvoi le nom de l'interpréteur actuellement choisi """
	if curPythonVersion == "6padPythonVersion":
		return "6pad++"
	elif curPythonVersion != "": # interpréteur classique
		v = os.path.dirname(curPythonVersion)
		return os.path.basename(v)
	# end if
	return ""
# end def

def getModuleRef(modPath, is6padInterpretor = True):
	# renvoi la référence à un module  à partir de son chemin
	curPath = os.path.dirname(sp.window.curPage.file)
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
		rep = curPath
	# end if
	# on trouve la longueur limite du répertoire de base du projet
	limit = len(rep.split("\\"))
	# on prend la partie au dela
	lst = lst[limit:]
	# on transforme en texte en la joignant par des points
	rep = ".".join(lst)
	# on élimine l'extension python
	rep = re.sub("\\.py$", "", rep, 0, re.I)
	rep = re.sub("\\.pyw$", "", rep, 0, re.I)
	# renvoi
	return rep
# end def

def getModuleRef2(modPath):
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

def getModuleRef2(path):
	# renvoi le module de 6pad à partir de son chemin
	s = sp.appdir
	l = path.split("\\")
	if path.find(os.path.join(s, "lib")) >= 0:
		s2 = os.path.join(s, "lib")
		l2 = s2.split("\\")
		l = l[len(l2):]
	elif path.find(os.path.join(s, "plugins")) >= 0:
		s2 = os.path.join(s, "plugins")
		l2 = s2.split("\\")
		l = l[len(l2):]
	else:
		return ""
	# end if
	path = ".".join(l)
	l = path.split(".")
	del l[- 1]
	path = ".".join(l)
	return path
# end def

def getStringsPos(s):
	# renvoi les limites des chaînes string et commentaires déclarées dans le texte en paramètre.
	# suppose que la syntaxe du texte est correcte.
	lst = []
	k = - 1
	prev = ""
	quote = ""
	inQuote = False
	litteral = False
	d, f = 0, 0
	i = 0
	n = len(s)
	while(i < n):
		e = s[i]
		if inQuote == False:
			if e == "'" or e == '"':
				quote = e
				inQuote = True
				if i > 0 and s[i - 1] == "r": literal = True
				else: literral = False
				d = i
			elif e == "#": # début de commentaire
				# on prend jusqu'à la fin de la ligne ou du texte
				d = i
				for k in range(i, n):
					if s[k] == "\r" or s[k] == "\n":
						k = k - 1
						break
					# end if
				# end for
				i = k # avancement
				f = k
				lst.append((d, f))
			# end if
		else: # inQuote==True
			if e == quote:
				if prev == "\\" and litteral == True:
					prev = e
					i = i + 1
					continue
				elif prev == "\\" and litteral == False:
					k = i - 1
					s2 = ""
					while(k >= 0):
						if s[k] == "\\": s2 = s2 + "\\"
						else: break
						k = k - 1
					# end while
					# ici, si le nombre d'antislashes comptés est un multiple de 2
					if len(s2) % 2 == 0:
						inQuote = False
						quote = ""
						f = i
						lst.append((d, f))
					# end if
				else: # simple fermeture de guillemets
					inQuote = False
					quote = ""
					f = i
					lst.append((d, f))
				# end if fin test plusieurs possibilités pour le quote
			# end if fin si quote
		# end if fin si inQuote ou pas
		prev = e
		i = i + 1
	# end while
	return lst
# end def

def getStringPattern(patternType=0):
	# retourne le pattern de regexp pour trouver les string
	lstPt = []
	if patternType == 0 or patternType == 1:
		# recencement des chaînes string
		# string avec triples quotes en appostrophes
		lstPt.append("[']{3,5}[\w\W]+?[']{3,}")
		# string avec triples quotes en guillemets
		lstPt.append("\"{3,}[\\w\\W]+?\"{3,}")
	# end if
	if patternType == 0 or patternType == 2:
		# string avec appostrophes
		lstPt.append("r'.*?'")
		lstPt.append(r"'.*?((?<!\\\\\\\\\\)|(?<!\\\\\\)|(?<!\\))'")
		# string avec guillemets
		lstPt.append('r".*?"')
		lstPt.append(r'".*?((?<!\\\\\\\\\\)|(?<!\\\\\\)|(?<!\\))"')
	# end if
	if patternType == 0 or patternType == 3:
		# commentaire uniligne
		lstPt.append("\\#[^\\r\\n]*")
	# end if
	# concaténation
	return "(" + "|".join(lstPt) + ")"
# end def

def getTripleQuotePos(s):
	"""  renvoi les positions de tous les triples quotes dans un objet liste """
	lst = []
	pt = "([\"]{3,}|[']{3,})"
	found = finditer2list(pt, s)
	if len(found) == 0: return lst
	# recherche et suppression des triples quotes au nombre de caractère éroné
	i = len(found) - 1
	while (i >= 0):
		e = found[i]
		nb = len(e.group(0))
		if nb != 3 and nb != 5:
			del found[i]
		# end if
		i -= 1
	# end while
	nb = len(found)
	if nb == 0: return lst
	# parcours
	i = 0
	lastTQEnd = 0 # position de fin du précédent triple quote
	while (i < nb):
		trip = found[i]
		# on retient la position de début du triple quote
		d = trip.start(0)
		# on essai de déterminer si le triple quote n'est pas dans une chaîne string
		# la limite de vérification est le précédent triple quote ou retour à la ligne
		flagString = False
		ln = ""
		k = d - 1
		while (k > lastTQEnd):
			sChar = s[k]
			ln = sChar + ln
			if re.match("[\\r\\n]", sChar): # retour à la ligne
				break
			elif re.match("[\" | ']", sChar): # caractère de string
				flagString = True
			# end if
			k -= 1
		# end while
		#  si un caractère de string a été détecté dans la zone de vérification
		if flagString == True:
			# on va vérifier dans cette zone si les chaînes string sont équilibrées ou pas
			flag, lstString = isStringBalanced(ln)
			# si les chaînes string ne sont pas équilibrée, on saute ce triple quote
			# il est probablement englobé par des guillemets ou appostrophes
			if flag == False:
				i += 1
				continue
			# end if
		# end if
		# le triple quote est valide
		# détermination du type de caractère duquel il est constitué
		quoteType = s[d]
		# recherche du triple quote de fin équivalant
		flagEnd = False
		for j in range(i + 1, nb):
			# si triple quote de même type que celui de l'ouverture
			if s[found[j].start(0)] == quoteType:
				# on détermine la position de fin
				f = found[j].start(0) + len(found[j].group(0))
				lastTQEnd = f
				i = j # déplacement du compteur
				flagEnd = True
				break
			# end if
		# end for
		# si une fin de quote n'a pas été trouvée, la fin est la fin du document
		if flagEnd == False:
			f = len(s) - 1
			i = nb # déplacement du compteur
		# end if
		# ajout à la liste des limites
		lst.append((d, f))
		i += 1 # incrémentation
	# end while
	# renvoi de la liste des limites
	return lst
# end def

def getTripleQuotePos2(s):
	#  renvoi les positions de tous les triples quotes dans un objet liste
	l = []
	lst = []
	tripleQuote = ""
	flag = True
	polarity = True
	flagBalance = True
	# recherche de toutes les lignes qui ont au moins un triple quotes
	found = finditer2list("([\\r\\n]+)[^\\r\\n]*?('''|\" \"\")[^ \\r \\n] * ", s)
	# parcours
	i = 0
	n = len(found)
	while(i < n):
		e = found[i]
		sLine = e.group(0)
		start = e.start(0)
		flag, polarity, tripleQuote, l = getTripleQuoteInfos(sLine)
		# si au moins un triple quotes valide
		if flag == True:
			# on ajuste les valeurs de la sous-liste des positions
			o = -1
			for(d, f) in l:
				o = o + 1
				d = start + d
				if f > - 1: f = start + f
				l[o] = (d, f)
			# end for
			# on ajoute la sous liste des positions à la liste principale
			lst = lst + l
			# si tous les triples quotes ne se referment pas sur la même ligne
			# ca veut dire qu'on doit rechercher la position de fin du dernier triple quotes commencé sur cette ligne
			if polarity == True:
				flagBalance = False
				j = i + 1
				while(j < n):
					sLine2 = found[j].group(0)
					start = found[j].start(0)
					if sLine2.find(tripleQuote) >= 0:
						d, f = lst[len(lst) - 1]
						f = start + sLine2.find(tripleQuote) + 3
						lst[len(lst) - 1] = (d, f)
						flagBalance = True
						i = j # avancement 
						break
					# end if
					j = j + 1
				# end while
			# end if
		# end if
		i = i + 1
	# end while
	# si il manque une fermeture de triple quote
	if flagBalance == False:
		# on va marquer la fin du texte comme position de fin
		d, f = lst[n - 1]
		f = len(s) - 1
		lst[n - 1] = (d, f)
	# end if
	# renvoi de la liste des positions recencées
	return lst
# end def

def getTripleQuoteInfos(sLine):
	#  renvoi des infos sur les triples quotes dans cette ligne
	# où commencent et où s'arrêtent-elles ?
	sLine = "  " + sLine + "  "
	flag = False
	flagQuote = False
	flagTripleQuote = False
	flagLitteral = False
	quote = ""
	tripleQuote = ""
	i = 2
	lst = []
	d, f = 0, 0
	# parcours
	while i < len(sLine):
		e = sLine[i]
		if flagQuote == False:
			if e == "'" or e == '"':
				if sLine[i + 1] == e and sLine[i + 2] != e:
					i = i + 2
					continue
				elif sLine[i + 1] == e and sLine[i + 2] == e:
					tripleQuote = e
					if flagTripleQuote == False: 
						flagTripleQuote = True
						flag = True
						d = i - 2
					elif flagTripleQuote == True: 
						flagTripleQuote = False
						f = i
						# ajout des limites à la liste des triples quotes repérés
						lst.append((d, f))
					# end if
				else:
					flagQuote = True
					quote = e
					flagLitteral = (sLine[i - 1] == "r")
				# end if				
			# end if
		else: # flagQuote==True
			if e == quote:
				if flagLitteral == False:
					if sLine[i - 1] == "\\" and sLine[i - 2] != "\\":
						i = i + 1
						continue
					else:
						flagQuote = False
						quote = ""
					# end if
				else: # flagLitteral==True
					if sLine[i - 1] == "\\":
						i = i + 1
						continue
					else:
						flagQuote = False
						quote = ""
					# end if					
				# end if
			# end if
		# end if		
		i = i + 1
	# end while
	# on force la fermeture même si polarité positive
	if flagTripleQuote == True:
		f = - 1
		lst.append((d, f))
	else:
		tripleQuote = ""
	# end if
	# on retourne: 
	# si True ou False des triples quotes ont été trouvés
	# la polarité de flagTripleQuote, 
	# le dernier type de triples quotes non refermé
	# le tableau des positions de triples quotes
	return flag, flagTripleQuote, tripleQuote + tripleQuote + tripleQuote, lst
# end def

def getBlocsStructure(lstBlocsLimits=None):
	# crée une structure des principaux blocs du code
	s = sp.window.curPage.text
	# on génère la liste de toutes les importations dans le texte/code
	lstImport = extractImportsFromCode(s)
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(s)
	# l'unité d'indentation du fichier courant
	iu = getCurIndentUnit()
	# l'unité de retour à la ligne du fichier courant
	ru = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lstLines = s.split(ru)
	# préparation du parcour des blocs recencés
	s = ""
	i = 0
	for(level, key, name, d, f, ln) in lstBlocsLimits:
		if key == "class":
			# si classe avec héritage
			pt = "class[ \\t]+[\\w\\d_]+[ \\t]*\\([ \\t]*([\\w\\d_\\.]+)"
			if re.match(pt, ln):
				# on trouve l'expression d'héritage
				heritFull = finditer2list(pt, ln)[0].group(1)
				# s'il y a un import lié à cet héritage
				heritShort = ""
				if heritFull.find(".") >= 0:
					# l'expression d'héritage contient un point
					# on va garder seulement la première partie
					heritShort = heritFull.split(".")[0]
				else:
					heritShort = heritFull
				# end if
				# recherche de cette expression dans les importations préalablement recensées
				for impo in lstImport:
					# désactivé if re.match("[^a-zA-Z\\d_]" + heritShort + "[^a-zA-Z\\d_]", impo + "'"):
					if impo.find(" " + heritShort) >= 0 or impo.find("," + heritShort) >= 0:
						# on doit ajouter l'importation au texte renvoyé
						# pas grave si importation multiple
						s = s + ("\t" * level.count(iu)) + impo + "\n"
					# end if
				# end for
				# on ajoute la déclaration de la classe au texte à renvoyer
				s = s + ("\t" * level.count(iu)) + key + " " + name + "(" + heritFull + "):\n"
			else: # pas d'héritage à la classe
				s = s + ("\t" * level.count(iu)) + key + " " + name + "():\n"
			# end if
			# sur la ligne suivante, on recherche une éventuelle description documentaire de la classe
			s3 = ru.join(lstLines[d + 1:])
			pt = "^[ \\t]*('''.+?'''|\"\"\.+?\"\"\")"
			if re.match(pt, s3):
				s3 = finditer2list(pt, s3) [0].group(1)
				s = s + ("\t" * level.count(iu)) + "\t" + s3 + "\n"
			# end if			
			# on circonscrit le texte qui contient la classe
			classText = ru.join(lstLines[d: f])
			# on va rechercher tous les attributs de la classe dans son texte préalablement circonscrit
			lst = []
			lstAttributs = finditer2list("^" + level + iu + "([_]*[\\w][\\w\\d_]*)[ \\t]*\\=", classText, re.M)
			for e in lstAttributs:
				lst.append(e.group(1))
			# end for			
			# on recherche également les attribut implicites à la classe déclarés dans les def
			lstAttributs = finditer2list("^[ \\t]+self\\.([\\w\\d_]+)[ \\t]*\\=", classText, re.M)
			for e in lstAttributs:
				lst.append(e.group(1))
			# end for			
			# on élimine les doublons de la liste des attributs ainsi constituée
			lst = cleanList(lst)
			# on complète le texte résultat avec les attributs triés
			for e in lst:
				s = s + level + iu + e + " = 0\n"
			# end for			
		elif key == "def":
			pt = "^[ \\t]*(def[ \\t]+[\\w\\d_]+[ \\t]*\\(.*?\\)[ \\t]*\\:)"
			if re.match(pt, ru.join(lstLines[d:]), re.L):
				# on extrait la ligne
				s2 = finditer2list(pt, ru.join(lstLines[d:]), re.L) [0].group(1)
				# retrait de caractères indésirables de la chaîne
				s2 = re.sub("(\\\\[ \\t]*)*[\\r\\n]+", "", s2)
				s = s + ("\t" * level.count(iu)) + s2 + "\n"
			else: # fonction simple
				s = s + ("\t" * level.count(iu)) + key + " " + name + "():\n"
			# end if			
			# on recherche un éventuel commentaire documentaire à la fonction
			s3 = ru.join(lstLines[d: f])
			pt = "^.+?\\)[ \\t]*\\:[ \\t]*(\\#[^\\r\\n]*)*[\\r\\n]+[ \\t]*('''.+?'''|\"\"\".+?\"\"\")"
			if re.match(pt, s3):
				s3 = finditer2list(pt, s3) [0].group(2)
				s = s + ("\t" * level.count(iu)) + "\t" + s3 + "\n"
			# end if			
			# pour toute fonction, on ajoute un return
			# ou plutôt une déclaration simple
			# pour éviter le vide
			# désactivé s = s + ("\t" * level.count(iu)) + "\treturn 0\n"
			s = s + ("\t" * level.count(iu)) + "\ta = 0\n"
		# end if
	# end for
	# englobage dans un bloc try
	if s.count("class") > 0 or s.count("def") > 0:
		# s = "try:\n\t" + re.sub("\n", "\n\t", s) + "\nexcept: pass\n"
		i = 0
	# end if
	return s # renvoi final
# end def

def getBlocsLimits(s):
	# retrouve les lignes de début et fin des blocks principaux def et class
	lst = []
	inTripleQuote = False
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# décomposition des lignes dans une liste
	lines = s.split(ru)
	# ajout d'une ligne supplémentaire pour marquer la fin
	lines.append("fin")
	n = len(lines)
	for i in range(0, n):
		curLine = lines[i]
		# si ligne vide ou de commentaire
		if re.match("^[ \\t]*\\#", curLine) or re.match("^[ \\t\\r\\n]*$", curLine):
			continue
		# end if
		# gestion des triples quotes
		if inTripleQuote == False:
			if curLine.count("'''") > 0 or curLine.count("\" \"\"") > 0:
				flag, flagTripleQuote, tripleQuote, lstTripleQuote = getTripleQuoteInfos(curLine)
				if flagTripleQuote == True:
					inTripleQuote = True
					curTripleQuote = tripleQuote
				# end if
			# end if
		else: # inTripleQuote == True
			if curLine.count(curTripleQuote) > 0:
				inTripleQuote = False
				curTripleQuote = ""
				continue
			else: # ligne à ne pas prendre en compte
				continue
			# end if
		# end if
		# si ligne d'influence de l'indentation
		pt = "^([ \\t]*)(class|def)[ \\t]+([a-zA-Z\\d_]+)"
		if re.match(pt, curLine):
			curKey = finditer2list(pt, curLine, re.I)[0].group(2)
			curName = finditer2list(pt, curLine, re.I)[0].group(3)
			curIndent = re.findall("^[ \\t]*", curLine)[0]
			curLevel = len(curIndent)
			d = i # ligne de début
			# on recherche la fin de ce bloc
			for j in range(i + 1, n):
				line = lines[j]
				# si ligne vide ou de commentaire
				if re.match("^[ \\t]*\\#", line) or re.match("^[ \\t\\r\\n]*$", line):
					continue
				# end if
				# gestion des triples quotes
				if inTripleQuote == False:
					if line.count("'''") > 0 or line.count("\" \"\"") > 0:
						flag, flagTripleQuote, tripleQuote, lstTripleQuote = getTripleQuoteInfos(line)
						if flagTripleQuote == True:
							inTripleQuote = True
							curTripleQuote = tripleQuote
						# end if
					# end if
				else: # inTripleQuote == True
					if line.count(curTripleQuote) > 0:
						inTripleQuote = False
						curTripleQuote = ""
						continue
					else: # ligne à ne pas prendre en compte
						continue
					# end if
				# end if
				# est-ce la ligne de fin ?
				level = len(finditer2list("^[ \\t]*", line)[0].group(0))
				# si le niveau est inférieur ou égal
				if level <= curLevel:
					# on vérifie si les dernières lignes  sont des commentaires ou des lignes vides
					k = j
					while(re.match("^[ \\t]*\\#", lines[k - 1]) or re.match("^[ \\t\\r\\n]*$", lines[k - 1])):
						k = k - 1
						# si balise de fin de bloc correspondante
						if re.match("^[ \\t]*(\\#[ ]+)?end[ ]+" + curKey, lines[k]) and re.findall("^[ \\t]*", lines[k])[0] == curIndent:
							j = k + 1
							k = j
							break
						# end if
					# end while
					if k != j:
						# on recherche la vraie position de fin
						for j in range(k, j + 1):
							indent = re.findall("^[ \\t]*", lines[j])[0]
							if len(indent) < len(curIndent + iu): break
						# end for
					# end if
					f = j - 1
					lst.append((curIndent, curKey, curName, d, f, curLine))
					break
				# end if
			# end for
			inTripleQuote = False
			curTripleQuote = ""
		# end if
	# end for
	# retrait de la ligne superflux préalablement ajoutée
	del lines[len(lines) - 1]
	# renvoi
	return lst
# end def

def getBlocHeader(s):
	# renvoi la ou les premières lignes déclarant un bloc def ou class
	ru = getCurReturnUnit()
	pt = "[ \\t]*(class|def)[ \\t]+[_]*[a-zA-Z][a-zA-Z\\d_]*("
	# avec deux points cloturant immédiatement
	pt = pt + "[ \\t]*\\:|"
	# avec des parenthèses ouvrantes et fermantes
	pt = pt + "[ \\t]*\\(.*?\\)[ \\t]*\\:"
	# cloture de la parenthèse
	pt = pt + ")"
	# recherche
	return findall2list(pt, s, re.L) [0]
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

def getRelatedCode(lstBlocsLimits = None):
	# Restriction et renvoi du code uniquement relatif à la ligne courante
	s = sp.window.curPage.text
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(s)
	ru = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lines = s.split(ru)
	l = sp.window.curPage.curLine # numéro de la ligne courante
	# effacement des lignes non impliquées
	for(level, key, name, d, f, sLine) in lstBlocsLimits:
		if l < d or l > f:
			for i in range(d, f + 1):
				lines[i] = ""
			# end for
		# end if
	# end for
	# recencement de la hiérarchie des blocs impliqués
	lstInvolved = [(0, len(lines) - 1)]
	for(level, key, name, d, f, sLine) in lstBlocsLimits:
		if l >= d and l <= f:
			lstInvolved.append((d, f))
		# end if
	# end for
	# parcours des blocs impliqués
	s = ""
	for i in range(0, len(lstInvolved)):
		d, f = lstInvolved[i]
		# s'il existe un bloc enfant à ce bloc
		if i < len(lstInvolved) - 1:
			d2, f2 = lstInvolved[i + 1]
			# 1. on recueille le texte jusqu'au début du bloc enfant
			for j in range(d, d2):
				s = s + lines[j] + ru
			# end for
			# 2. on recueille le texte après le bloc enfant
			for j in range(f2 + 1, f + 1):
				s = s + lines[j] + ru
			# end for
		else: # il n'y a pas de bloc enfant
			# on recueille le texte jusqu'à la ligne courante
			for j in range(d, l):
				s = s + lines[j] + ru
			# end for
		# end if
	# end for
	# Elimination des lignes vides
	s = re.sub("(" + ru + "){2,}", ru, s)
	# renvoi
	return s
# end def

def getNierestExpression(lst, expression):
	# renvoi la position de l'expression la plus proche contenue dans la liste ordonnée de manière croissante
	if expression == "": return 0
	#  élimination de la cass
	lst2 = []
	for e in lst:
		lst2.append(e.lower())
	# end for
	expression = expression.lower()
	s = ""
	pos = 0
	selec = 0
	flag = False
	# pour chaque lettres de l'expression
	n = len(expression)
	for i in range(0, n):
		s = expression[0: i + 1].lower()
		for j in range(pos, len(lst2)):
			if lst2[j].startswith(s):
				selec = j
				if i >= n: return selec
				pos = j
				break
			else:
				if i >= n: return selec
			# end if
		# end for
	# end for
	return selec
# end def

def removeTags(s = ""):
	# retire les commentaires de fin de block à un texte
	# D'abord le cas particulier des lignes
	# avec balise plus commentaire.
	# on va retirer la balise de fin mais garder le commentaire
	# en mettant un marqueur pour signifier que ce commentaire est sur la même ligne que la balise de fin
	# le marqueur est un double # (##)
	s= re.sub("([\\r\\n]+[ \\t]*)\\#[ \\t]*end[ \\t]+(class|def|while|for|if|try|with)([ \\t]*\\#+[ \\t]*)*([^\\r\\n]+)", "\\1## \\4", s)
	# Puis, retrait des lignes de balises de fin sans commentaires en plus
	s= re.sub("[\\r\\n]+[ \\t]*\\#[ \\t]*end[ \\t]+(class|def|while|for|if|try|with)[^\\r\\n]*", "", s)
	# renvoi
	return s
# end def

def removeTagsInPage(page = None):
	# sur la page courante si aucune page
	if page == None: page = sp.window.curPage
	iLine = page.curLine
	if page.selectedText != "":
		page.selectedText = removeTags(page.selectedText)
	else:
		page.text = removeTags(page.text)
	# end if
	page.curLine = iLine
	sayText("Retrait des balises de fin de bloc")
# end def

def addTags(s = "", blAdjustIndents = False):
	# ajoute des balises de fin de block au code en paramètre
	s = removeTags(s) # préalable
	# retrait de tous les strings
	lstString = []
	s, lstString = removeStringsFromCode(s)
	# détermination des type d'indentation et de retour à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# décomposition des lignes dans un tableau
	lines = s.split(ru)
	# ajout d'une ligne supplémentaire marquant la limite
	lines.append("a")
	# initialisation de variables
	tag = "tag___yyd"
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	curKey = ""
	curIndent = ""
	curLevel = 0
	supplement = ""
	flagRebounce = False
	# parcours ligne par ligne
	i = 0
	n = len(lines)
	while(i < n):
		ln = lines[i]
		# si est une ligne de départ de l'indentation
		pt = "^([ \\t]*)(" + pt1 + ")[^\\w\\d_]+"
		if re.match(pt, ln):
			# on recense ses informations
			curKey = finditer2list(pt, ln)[0].group(2)
			curIndent = finditer2list(pt, ln)[0].group(1)
			curLevel = int(len(curIndent) / len(iu))
			# retrait d'éventuels commentaire/strings
			ln = re.sub(tag + "\\d+_", "", ln)
			# si pas de deux points cloturant sur cette ligne d'influence de l'indentation
			# on recherche ces deux points sur les lignes suivantes
			if ln.count(":") == 0:
				k = 0
				while (i + k < len(lines)):
					k = k + 1
					# si ligne vide, de commentaire ou de relance
					if re.match("^[ \\t\\r\\n]*$", lines[i + k]) or re.match("^[ \\t]*" + tag + "\\d+_[\\r\\n]*$", lines[i + k]) or re.match("^[ \\t]*(" + pt1 + "|" + pt2 + ")[^\\w\\d_]", lines[i + k]):
						break
					# end if
					# inclusion de cette ligne à l'instruction
					ln = ln + " " + lines[i + k]
					ln = re.sub(tag + "\\d+_", "", ln)
					# selon si contient un deux points ou pas
					if ln.count(":") > 0:
						# on est arrivé à la fin
						i = i + k
						break
					# end if
				# end while
			# end if
			flagContinue = False
			# si est une ligne d'exécution directe d'instruction
			if isDirectLine(ln):
				#  les lignes suivantes immédiates relancent-elles également l'indentation ?
				for k in range(i + 1, n):
					ln3 = lines[k]
					# retrait d'éventuelle marque de commentaire/string
					ln3 = re.sub(tag + "\\d+_", "", ln3)
					# si ligne de relance de même niveau
					if re.match("^[ \\t]*(" + pt2 + ")", ln3) and finditer2list("^[ \\t]*", ln3) == curIndent:
						if isDirectLine(ln3):
							continue
						else:
							i = k
							break
						# end if
					else:
						flagContinue = True
						break
					# end if
				# end for
			# end if
			if flagContinue == True:
				i = i + 1
				continue
			# end if
			# Recherche de la fin du bloc,
			# dans l'optique d'y placer un commentaire d'indication de la fin de ce bloc.
			# et d'ajuster les indentations si autorisé
			j = i + 1
			while(j < n):
				ln2 = lines[j]
				indent = finditer2list("^[ \\t]*", ln2)[0].group(0)
				level = int(len(indent) / len(iu))
				# si indentation inférieure ou de même niveau
				if level <= curLevel:
					# si indentation de même niveau
					if level == curLevel:
						#  si est une ligne de relance de l'indentation
						if re.match("^[ \\t]*(" + pt2 + ")[^\\w\\d_]", ln2):
							# si ligne directe d'exécution d'instruction
							if isDirectLine(ln2):
								# les lignes suivantes immédiates relancent-elles également l'indentation ?
								flagContinue = False
								for k in range(j + 1, len(lines)):
									ln3 = lines[k]
									# retrait d'éventuelle marque de commentaire/string
									ln3 = re.sub(tag + "\\d+_", "", ln3)
									# si ligne de relance de même niveau
									if re.match("^[ \\t]*(" + pt2 + ")", ln3) and finditer2list("^[ \\t]*", ln3) == curIndent:
										if isDirectLine(ln3):
											continue
										else:
											j = k - 1
											break
										# end if
									else:
										flagContinue = True
										break
									# end if
								# end for
							# end if
							if flagContinue == True:
								curKey = ""
								curIndent = ""
								curLevel = 0
								break
							# end if
							j = j + 1
							continue
						# end if
					# end if
					# si ligne de commentaire/string
					# ou ligne vide
					if re.match("^[ \\t]*" + tag, ln2) or re.match("^[ \\t\\r\\n]*$", ln2):
						j = j + 1
						continue
					# end if
					# si les lignes précédentes sont  de type vide ou commenté, on remonte la position du compteur
					k = j
					while(re.match("^[ \\t]*" + tag, lines[k - 1]) or re.match("^[ \\t\\r\\n]*$", lines[k - 1])):
						k = k - 1
					# end while
					if k != j:
						# à partir de la ligne k, on recherche la fin réelle
						for j in range(k, j + 1):
							indent = finditer2list("^[ \\t]*", lines[j])[0].group(0)
							if len(indent) < len(curIndent + iu): break
						# end for
					# end if
					# détermination si on doit ajouter une ligne vide
					if(curKey == "class" or curKey == "def") and not re.match("^[ \\t\\r\\n]*$", lines[j]) and not re.match("^[ \\t]*\\#[ \\t]*end[ \\t]+def", lines[j]):
						supplement = ru + curIndent
					else:
						supplement = ""
					# end if
					# si ligne avec marqueur pour indiquer
					# un commentaire sur la même ligne que la balise de fin de bloc
					ln4 = lines[j]
					indent = finditer2list("^[ \\t]*", ln4)[0].group(0)
					if (len(indent) == len(curIndent)) and re.match("^[ \\t]*" + tag + "\\d+_[\\r\\n]*$", ln4) :
						# les commentaires ayant été remplacés par des génériques
						# on va retrouver la vrai valeur du commentaire sur cette ligne
						try:
							id = int(finditer2list("^[ \\t]*"+tag+"(\\d+)_[\\r\\n]*$", ln4)[0].group(1))
							ln4 = indent + lstString[id-1].group(0)
						except: pass
					# end if
					# si la ligne possède un marqueur
					if indent == curIndent and re.match("^[ \\t]*\\#{2}", ln4):
						# on ajoute la balise au début de cette ligne
						lines[j] = curIndent+"# end "+curKey+" # "+re.sub("^[ \\t]*\\#+[ \\t]*", "", ln4)
						# on annule un éventuel ajout de ligne vide
						supplement = ""
					else: # n'est pas une ligne avec marqueur
						# insertion de la ligne commentaire balise de fin de bloc
						lines.insert(j, curIndent + "# end " + curKey)
						n = n + 1
					# end if
					if supplement != "":
						lines.insert(j + 1, curIndent)
						n = n + 1
					# end if
					# réinitialisations
					curKey = ""
					curIndent = ""
					curLevel = 0
					supplement = ""
					iString = 0
					break
				# end if fin si level inférieur ou égal
				j = j + 1
			# end while fin boucle de recherche de fin du bloc
		# end if fin si ligne d'influence de l'indentation
		i = i + 1
	# end while
	k = 0
	# si autorisation d'ajustement des indentations
	if blAdjustIndents == True:
		# on part de la dernière ligne vers le début
		for i in range(len(lines) - 1, -1, -1):
			# s'il s'agit d'une ligne de balise de fin de bloc
			if re.match("^[ \\t]*\\# end (" + pt1 + ")", lines[i]):
				# on retient son indentation
				curIndent = re.findall("^[ \\t]*", lines[i])[0]
				# on retient son mot clé
				curKey = finditer2list("end (" + pt1 + ")", lines[i])[0].group(1)
				# on va remonter vers sa ligne déclencheuse
				for j in range(i - 1, -1, -1):
					ln = lines[j]
					# si ligne déclencheuse, on s'arrête
					if re.match("^" + curIndent + curKey + "[^\\w\\d_]", ln):
						curIndent = ""
						curKey = ""
						break
					# end if
					# sinon, s'il s'agit d'une ligne vide ou de commentaire
					if re.match("^[ \\t\\r\\n]*$", ln) or re.match("^[ \\t]*" + tag + "\\d+" + "_[\\r\\n]*$", ln):
						# si cette ligne est d'indentation inférieure ou égale à celle de la ligne déclencheuse
						indent = re.findall("^[ \\t]*", ln)[0]
						if len(indent) <= len(curIndent):
							# on augmente son niveau d'indentation
							lines[j] = curIndent + iu + re.sub("^[ \\t]*", "", ln)
							k = k + 1
						# end if
					# end if"
				# end for
			# end if
		# end for
	# end if
	del lines[len(lines) - 1] # retrait de la ligne supplémentaire
	# s = ru.join(lines) # reconstitution du texte
	s = "\r\n".join(lines) # reconstitution du texte
	# restauration des strings et commentaires
	s = restoreStringsInCode(s, lstString)
	# renvoi
	return s
# end def

def addTagsInPage(page = None):
	# sur la page courante si aucune page
	if page == None: page = sp.window.curPage
	# s'il n'y a pas de texte sélectionné
	if page.selectedText == "":
		# en vue d'un repositionnement ultérieur, on va insérer un marqueur sur une ligne qui sera toujours présente
		tag = "# Aszzrzsjflzj12AsdfLKjo2399ZsMhfozpU"
		iLine = page.curLine
		while (re.match("^[ \\t]*\\#[ \\t]+end[ \\t]+()", page.line(iLine))):
			iLine = iLine - 1
			if iLine < 0:
				iLine = 0
				break
			# end if
		# end while
		page.curLine = iLine
		page.curLineText = page.line(iLine) + tag
		# ajout des balises de fin de bloc à ce texte
		s = page.text
		s = addTags(s)
		## on identifie la position du marqueur
		i = s.find(tag)
		# on retire le marqueur
		s = s.replace(tag, "")
		# re-affichage du texte traité
		page.text = s
		# repositionnement suivant le marqueur placé plus haut
		page.curLine = page.lineOfOffset(i)
	else: # du texte est sélectionné
		iLine = page.lineOfOffset(page.selectionStart)
		# on trouve les véritables début et fins de ligne de la portion impliquée
		d = page.lineStartOffset(page.lineOfOffset(page.selectionStart))
		f = page.lineEndOffset(page.lineOfOffset(page.selectionEnd))
		s = page.text
		# remplacement de la portion concernée
		page.replace(d, f, addTags(s[d: f - 1]))
		# repositionnement
		page.curLine = iLine
	# end if
	sayText("Ajout des balises de fin de bloc")
# end def

def adjustIndents(s):
	# correction des indentations suivant les limites des blocs principaux
	# le principe est que les lignes enfants d'un bloc doivent toutes être de niveau d'indentation supérieur
	k = 0
	# l'unité d'indentation du fichier courant
	iu = getCurIndentUnit()
	# l'unité de retour à la ligne du fichier courant
	ru = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lstLines = s.split(ru)
	# acquisition des limites des blocs principaux
	lstLimits = getBlocsLimits(s)
	# parcours et ajustements
	for (curIndent, curKey, curName, d, f, e) in lstLimits:
		for i in range(d + 1, f + 1):
			ln = lstLines[i]
			indent = re.findall("^[ \\t]*", ln)[0]
			# si dernière ligne du bloc
			if i == f:
				# si c'est la balise correspondante de fin de bloc
				# on la saute
				if re.match("^" + curIndent + "\\# end " + curKey, ln): continue
			# end if
			# si indentation  trop faible
			if len(indent) <= len(curIndent):
				# ajustement
				lstLines[i] = re.sub("^[ \\t]*", curIndent + iu, ln)
				k = k + 1 # compteur des occurences
			# end if
		# end for
	# end for
	alert(str(k) + " changements effectués")
	# reconstitution et renvoi du texte
	return ru.join(lstLines)
# end def

def adjustIndentsByTags(s, selection = False, iStart = 0, iEnd = 0):
	# ajuste les indentation à partir des balises commentaires de fin de block
	if selection == True:
		level = len(findall2list("^[ \\t]*", s) [0])
	# end if
	# retrait de toutes les indentations
	s = re.sub("(^|[\\r\\n]+)[ \\t]+", "\\1", s)
	# reécriture des balises de fin de block, pour notamment éviter les cas où on aurait oublié le #
	s = re.sub("(\\r\\n]+)[#]*[ \\t]*end[ \\t]*(class|def|if|for|try|while|with)", "\\1# end \\2", s, 0, re.I)
	# repérage du type de retours à la ligne
	ru = getCurReturnUnit()
	# repérage du type d'indentation
	iu = getCurIndentUnit()
	lst2 = []
	# ensuite, décomposition des lignes dans une liste
	lines = s.split(ru)
	lst = []
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	flagRebounce = False
	# parcours des lignes de la fin vers le début
	if selection == False: level = 0
	
	n = len(lines)
	i = n - 1
	while(i >= 0):
		sLine = lines[i]
		# vérification
		if re.match("^#[ \\t]*end[ \\t]*(" + pt1 + ")", sLine):
			# xxx c'est un commentaire de fin de block
			flagRebounce = False
			indent = iu * level
			lines[i] = indent + lines[i]
			key = finditer2list("^[ \\t]*#[ \\t]*end[ \\t]*(" + pt1 + ")", sLine) [0].group(1)
			lst.append(key)
			lst2.append(i)
			level = level + 1
		elif re.match("^(" + pt1 + ")[^a-zA-Z_\\d]", sLine):
			# xxx c'est une instruction de début de block
			# si n'est pas une ligne d'exécution directe après le deux points
			flag = isDirectLine(sLine)
			if flag == False: # la ligne n'exécute rien après le deux points
				flagRebounce = False
				# on vérifie si correspond à la fermeture
				key1 = finditer2list("^(" + pt1 + ")[^a-zA-Z_\\d]", sLine) [0].group(1)
				key2 = ""
				if len(lst) > 0: key2 = lst[len(lst) - 1]
				if key1.lower() == key2.lower():
					level = level - 1
					del lst[len(lst) - 1]
					del lst2[len(lst2) - 1]
					indent = iu * level
					lines[i] = indent + lines[i]
				else: # les mots clés ne correspondent pas
					if selection == True: i = i + sp.window.curPage.curLine - 1
					sp.window.alert("A la ligne " + str(i + 1) + "\r\n" + sLine, "'" + key1 + "' sans 'end " + key1 + "'")
					return
				# end if
			else: # c'est une ligne d'exécution directe d'instruction après le deux points
				if flagRebounce == True:
					flagRebounce = False
					# vérification que les mots clés correspondent
					key1 = finditer2list("^(" + pt1 + ")[^a-zA-Z_\\d]", sLine) [0].group(1)
					key2 = ""
					if len(lst) > 0: key2 = lst[len(lst) - 1]
					if key1.lower() == key2.lower():
						level = level - 1
						del lst[len(lst) - 1]
						del lst2[len(lst2) - 1]
						indent = iu * level
						lines[i] = indent + lines[i]
					# end if
				# end if
				indent = iu * level
				lines[i] = indent + lines[i]
			# end if
		elif re.match("^(" + pt2 + ")[^a-zA-Z_\\d]", sLine):
			# xxx c'est une ligne de relance d'indentation
			if isDirectLine(sLine) == False: # pas une ligne d'exécution directe
				# on diminue le niveau d'indentation uniquement pour cette ligne
				indent = iu * (level - 1)
				lines[i] = indent + lines[i]
				flagRebounce = True
			else: # c'est une ligne d'exécution directe
				if flagRebounce == True: level = level - 1 # modif temporaire
				indent = iu * level
				lines[i] = indent + lines[i]
				if flagRebounce == True: level = level + 1 # restauration
				i = i
			# end if
		else: # xxx c'est une ligne quelconque
			indent = iu * level
			lines[i] = indent + lines[i]
			flagRebounce = False
		# end if
		i = i - 1
	# end while
	if len(lst) > 0:
		key = lst[len(lst) - 1]
		i = lst2[len(lst) - 1]
		if selection == True: iLine = i + sp.window.curPage.curLine - 1
		sp.window.alert("A la ligne " + str(iLine + 1) + "\r\n" + lines[i], "'end " + key + "' sans '" + key + "'")
		return
	# end if
	# s = ru.join(lines)
	s = "\r\n".join(lines)
	if selection == False:
		sp.window.curPage.text = s
	else:
		# sp.window.curPage.replace(iStart, iEnd, s)
		sp.window.curPage.selectedText = s
	# end if
# end def

def AdjustIndentsByTagsInPage(page = None):
	# sur la page courante
	if page == None: page = sp.window.curPage
	iLine = page.curLine
	if len(page.selectedText) > 0:
		s = page.text
		d = page.lineStartOffset(page.lineOfOffset(page.selectionStart))
		f = page.lineEndOffset(page.lineOfOffset(page.selectionEnd))
		s = s[d: f - 1]
		adjustIndentsByTags(s, True, d, f)
	else:
		adjustIndentsByTags(page.text)
	# end if
	page.position = page.lineSafeStartOffset(page.curLine)
	sayText("Ajustement des indentations par les balises")
# end def

def refreshCode(s):
	# ajuste le code
	lstPt = []
	lstString = []
	# recencement des chaînes string
	# string avec triples quotes en appostrophes
	lstPt.append("'{3,5}[\w\W]+?'{3,5}")
	# string avec triples quotes en guillemets
	lstPt.append("\"{3, 5} [ \\w \\W] + ? \"{3,5}")
	# string avec appostrophes
	lstPt.append("r'.*?'")
	lstPt.append(r"'.*?((?<!\\\\\\\\\\)|(?<!\\\\\\)|(?<!\\))'")
	# string avec guillemets
	lstPt.append('r".*?"')
	lstPt.append(r'".*?((?<!\\\\\\\\\\)|(?<!\\\\\\)|(?<!\\))"')
	# commentaire uniligne
	lstPt.append("\\#[^\\r\\n]*")
	# concaténation
	pt = "(" + "|".join(lstPt) + ")"
	# recherche
	lstString = finditer2list(pt, s, 0)
	# remplacement des strings et commentaires par des génériques
	i = 0
	iStart = 0
	iEnd = 0
	d = 0
	f = 0
	s2 = s
	s = ""
	tag = "mmtag_yyd"
	for e in lstString:
		i = i + 1
		d, f = e.span(0)
		iEnd = d - 1
		s = s + s2[iStart: iEnd + 1] + tag + str(i) + "_"
		iStart = f
	# end for
	# ajout de la dernière portion
	try: s = s + s2[f:]
	except: pass
	# ajout de retour à la ligne au début
	# pour faciliter les traitements
	s = "\r\n" + s
	# séparation des opérateurs des autres caractères par  des espaces
	pt = r"[ ]*(\+=|-=|\*=|/=|<=|>=|==|!=|\|=|=|\||\+|-|\*|/|<|>|%)[ ]*"
	s = re.sub(pt, " \\1 ", s)
	# cas d'un nombre isolé précédé dun opérateur moins
	pt = "([\\(\\{\\[/\\|\\+\\*\\-,<>\\=\\:][ ]+\\-)[ ]+(\\d)"
	s = re.sub(pt, "\\1\\2", s)
	# les englobeurs ouvrants doivent être
	# séparés des autres caractères par un espace à gauche
	pt = r"([^\r\n])[ \t]*([\(\[\{]+)[ ]*"
	s = re.sub(pt, "\\1 \\2", s)
	# ceux desquels On doit retirer les espaces avant
	pt = r"([_]*[a-zA-Z][a-zA-Z_\d]*)[ ]+([\(\[\{]+)"
	s = re.sub(pt, "\\1\\2", s)
	# les englobeurs fermants
	pt = r"[ ]*([\)\]\}:]+)"
	s = re.sub(pt, "\\1", s)
	# ceux qui doivent avoir un espace avant, mais pas après
	pt = r"[ ]*([\\]+)[ ]*"
	s = re.sub(pt, " \\1", s)
	# ceux qui doivent avoir un espace après, mais pas avant
	pt = r"[ ]*([,])[ ]*"
	s = re.sub(pt, "\\1 ", s)
	# ceux qui doivent avoir un espace avant
	pt = "([^\\r\\n]([^\\w\\d_ \\t]+))((and|or)[^\\w\\d_])"
	s = re.sub(pt, "\\1 \\3", s)
	# ceux qui doivent avoir un espace après
	pt = "([^\\w\\d_](and|or|for|if|while))([^\\w\\d_ \\t])"
	s = re.sub(pt, "\\1 \\3", s)
	# les espaces trop grands
	# mais qui ne sont pas en début de ligne
	pt = r"([^\r\n ])[ ]{2,}"
	s = re.sub(pt, "\\1 ", s)
	# élimination des espaces et tabulations en fin de ligne
	pt = r"([^ \t]+)[ \t]+$"
	s = re.sub(pt, "\\1", s, 0, re.M)
	# élimination des espaces entre les englobants fermants et ouvrants
	pt = "(\\)|\\]|\\}|\\.)[ \\t]+(\\(|\\[|\\{)"
	s = re.sub(pt, "\\1\\2", s)
	# retrait du retour à la ligne de facilitation
	# ajouté plus haut
	s = re.sub("^\r\n", "", s)
	# restauration des string à partir des génériques
	i = 0
	for e in lstString:
		i = i + 1
		s = s.replace(tag + str(i) + "_", e.group(0), 1)
	# end for
	return s
# end def

def refreshCodeInPage(page = None):
	# ajuste le code dans la page courante
	if page == None: page = sp.window.curPage
	iLine = page.curLine
	if page.selectedText != "":
		page.selectedText = refreshCode(page.selectedText)
	else:
		page.text = refreshCode(page.text)
	# end if
	page.curLine = iLine
	sayText("Raffraîchissement de code")
# end def

def curPosHelp():
	# affiche de l'aide pour le mot clé sous le curseur
	# vérification qu'une version du python a bien Ã©tÃ© choisie
	if curPythonVersion == "":
		sp.window.alert("Vous n'avez choisi aucune version de python installée sur votre ordinateur.\nVeuillez le faire par le menu 'outils' et retenter cette action.", "Erreur- version de python")
		return
	# end if
	sPythonPath = curPythonVersion
	sPythonScript = sp.window.curPage.file
	sPythonScript = os.path.dirname(sPythonScript)
	if os.path.isdir(sPythonScript) == False: sPythonScript = getCurModuleDir()
	sPythonScript = sPythonScript + "\\pe_tmp.py"
	# recueillement du texte du document
	s = sp.window.curPage.text
	# quelques initialisations
	flagPoint = False
	flag6pad = False
	iStart = sp.window.curPage.position
	iEnd = iStart
	curKey = ""
	lst = []
	lstVars = []
	lstImports = []
	lstClassDef = []
	# repérage des blocs principaux du code
	lstBlocsLimits = getBlocsLimits(s)
	# y a-t-il un nom à une classe courante ?
	curClassName = getCurClassName(lstBlocsLimits, sp.window.curPage.curLine)
	# détermination si l'interpréteur choisi est celui du 6pad
	if curPythonVersion == "6padPythonVersion": flag6pad = True
	# identification d'une éventuelle expression sous le curseur
	expression, iStart, iEnd = getCurExpression()
	# vérification que l'expression est valide
	if expression.count(".") > 0:
		lst = expression.split(".")
		# si la dernière partie de l'expression est vide, alors toute l'expression est vide
		if lst[len(lst)-1] == "": expression = ""
		lst = []
	# end if
	if expression == "":
		sp.window.messageBeep(0)
		return
	# end if
	# traitement
	if flagPoint == True or flagPoint == False:
		# on circonscrit le code relatif à la ligne sous le curseur
		sCode = getRelatedCode(lstBlocsLimits)
		# décomposition des branches de l'expression dans une liste
		lstKey = expression.split(".")
		curKey = lstKey[len(lstKey) - 1]
		if len(curKey) > 0: iStart = iEnd - (len(curKey) - 1)
		else: iStart = iEnd
		# recherche de toutes les déclarations liées à l'expression dans le code restraint
		s = ""
		s = extractDeclarationsFromCode(sCode, expression)
		s = s + "\nhelp(" + ".".join(lstKey) + ")"
		# si un nom de classe courante a été détecté, on remplace tous les self par ce nom
		if curClassName != "": s = re.sub("([^a-zA-Z\\d_])self([^a-zA-Z\\d_])", "\\1" + curClassName + "\\2", s)
		# englobage dans un bloc try
		s = "\t" + re.sub("([\\r\\n]+)", "\\1\t", s)
		s = "try:\n" + s + "\nexcept: pass"
		# on y intègre la structure des blocs principaux
		s = getBlocsStructure(lstBlocsLimits) + "\n" + s
		# on précise le type d'encodage
		s = "# -*- coding: utf-8 -*-\n" + s
		if flag6pad == False:
			writeFile(sPythonScript, s)
		else: # c'est le 6pad++ qui exécute
			try: exec(s)
			except:
				sayText("Echec avec l'interpréteur " + getCurInterpretorName())
				sp.window.messageBeep(1)
				return
			# end try
		# end if
	# end if
	if flag6pad == False:
		si = subprocess.STARTUPINFO()	
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		# exécution
		curProc = subprocess.Popen([sPythonPath, sPythonScript], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = si, universal_newlines = True)
		sResultConsole, sResultError = curProc.communicate()
		try: sResultConsole = sResultConsole.decode()
		except:
			sResultConsole = decode2(sResultConsole)
		# end try
		# suppression du fichier temporaire
		os.remove(sPythonScript)
		if sResultConsole != "":
			print(sResultConsole)
		else:
			sayText("Echec avec l'interpréteur " + getCurInterpretorName())
			sp.window.messageBeep(1)
		# end if
	# end if
# end def

def curPosCompletion():
	# simule l'intellicence pour le python à l'emplacement du curseur
	# vérification qu'une version du python a bien été choisie
	if curPythonVersion == "":
		sp.window.alert("Vous n'avez choisi aucune version de python installée sur votre ordinateur.\nVeuillez le faire par le menu 'outils' et retenter cette action.", "Erreur- version de python")
		return
	# end if
	# on trouve le chemin vers l'interpréteur de python actuellement choisi
	sPythonPath = curPythonVersion
	# on détermine le chemin vers le script intermédiaire à exécuter
	sPythonScript = sp.window.curPage.file
	sPythonScript = os.path.dirname(sPythonScript)
	if os.path.isdir(sPythonScript) == False: sPythonScript = getCurModuleDir()
	sPythonScript = sPythonScript + "\\pe_tmp.py"
	# recueillement du texte du document
	s = sp.window.curPage.text
	# somme-nous à une position d'importation de module ?
	flagModuleOnly = isImportationArea()
	# quelques autres initialisations
	flagPoint = False # y a-t-il un point dans l'expression ?
	flag6pad = False # l'interpréteur est-il le 6pad++ ?
	iStart = sp.window.curPage.position
	iEnd = iStart
	curKey = ""
	lst = []
	lstVars = []
	lstImports = []
	lstClassDef = []
	lstModules = []
	# repérage des limites des principaux blocs
	lstBlocsLimits = getBlocsLimits(s)
	# y a-t-il un nom identifiable de classe courante ?
	curClassName = getCurClassName(lstBlocsLimits, sp.window.curPage.curLine)
	# détermination si l'interpréteur choisi est celui du 6pad
	if curPythonVersion == "6padPythonVersion": flag6pad = True
	# détermination d'une éventuelle expression clée sous le curseur
	expression, iStart, iEnd = getCurExpression()
	# xxx s'il n'y a pas de point dans l'expression
	if expression.find(".") <= - 1:
		flagPoint = False
		curKey = expression
		# si on doit tout proposer
		if flagModuleOnly == False:
			# on circonscrit le code relatif à la ligne sous le curseur
			sCode = getRelatedCode(lstBlocsLimits)
			# de ce code, on extrait tous les imports
			lstImports = extractImportsFromCode(sCode)
			# de ce code, on extrait toutes les déclarations de variables
			lstVars = extractVarsFromCode(sCode)
			# du code entier, on extrait les déclarations de classes et fonctions
			# désactivé lstClassDef = extractClassDefFromCode(s)
			# si l'interpréteur choisi est le 6pad++
			if flag6pad == True:
				# on recherche les sous-éléments du module __builtins__
				try: lst = lst + dir(__builtins__)
				except: pass
				# on recherche les mots clés du langage
				try:
					import keyword
					lst = lst + keyword.kwlist
				except: pass
				# selon les imports détectés
				for e in lstImports:
					if re.match(".+?[ \\t]+as[ \\t]+([a-zA-Z\\d_]+)", e, re.I): # from x import x as x
						s2 = finditer2list(".+?[ \\t]+as[ \\t]+([a-zA-Z\\d_]+)", e, re.I)[0].group(1)
						lst.append(s2)
					# end if
					if re.match("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+\\*", e, re.I): # from x import *
						s2 = finditer2list("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+\\*", e) [0].group(1)
						try:
							mo = __import__(s2)
							lst = lst + dir(mo)
						except: pass
					elif re.match("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+([\\w\\d_\\.]+)", e, re.I): # from x import x
						s2 = finditer2list("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+([\\w\\d_\\.]+)", e)[0].group(2)
						if s2.find(".") < 0: lst.append(s2)
					# end if
				# end for
				# on va ajouter les class et les def de premier niveau
				for i in range(len(lstBlocsLimits)):
					indent, key, name, d, f, ln = lstBlocsLimits[i]
					if key == "class":
						lst.append(name)
					elif key == "def" and indent == "":
						lst.append(name)
					# end if
				# end for
			else: # l'interpréteur est une version de python classique
				# pour trouver les mots clés et d'éventuelles sous-fonctions des imports,
				# on va passer par un fichier intermédiaire dont le sample se trouve à la racine du dossier forPython
				if os.path.isfile(getCurModuleDir() + "\\data\\sampleCompletion.txt") == False:
					alert("Un fichier sample d'exécution de code intermédiaire est introuvable", "Erreur- fichier manquant")
					return
				# end if
				s2 = readFile(getCurModuleDir() + "\\data\\sampleCompletion.txt")
				# construction de texte à exécuter
				s = ""
				e = ""
				for e in lstImports:
					s = s + "try: " + e + "\n\texcept: pass\n\t"
				# end for
				# ajout des imports nécessaires
				s = s2.replace("[imports]", s)
				# ajout de la structure des class et def
				s = s.replace("[structure]", getBlocsStructure(lstBlocsLimits))
				# écriture et exécution
				writeFile(sPythonScript, s)
			# end if
		else: # flagModuleOnly==True # on doit seulement proposer des modules à importer
			if flag6pad == False:
				# constitution du texte à exécuter
				s = "try:\n\timport pkgutil\n\tfor i in pkgutil.walk_packages():\n\t\tf,j,k=i\n\t\tprint(j)\nexcept: pass"
				s = s + "\ntry:\n\timport sys\n\tfor e in sys.modules: print(e)\nexcept: pass"
				# écriture dans le fichier à exécuter
				writeFile(sPythonScript, s)
				# on charge cependant la liste avec les modules détectés dans le même dossier
				lst = listModulesInCurDir(flag6pad = False)
			else: # flag6pad==True
				lst = listModules()
				# on ajoute les modules trouvés dans le même dossier
				lst = lst + listModulesInCurDir(flag6pad = True)
			# end if
		# end if
	else: # xxx au moins un point est présent dans l'expression
		flagPoint = True
		# on circonscrit le code relatif à la ligne sous le curseur
		sCode = getRelatedCode(lstBlocsLimits)
		# décomposition des branches de l'expression dans une liste
		lstKey = expression.split(".")
		curKey = lstKey[len(lstKey) - 1]
		if len(curKey) > 1: iStart = iEnd - (len(curKey) - 1)
		elif len(curKey) == 1:
			iStart = iEnd
			iEnd = iEnd + 1
		else: # longueur == 0
			iStart = iEnd + 1
			iEnd = iEnd + 1
		# end if
		# recherche de toutes les déclarations liées à l'expression dans le code restraint
		s = ""
		s = extractDeclarationsFromCode(sCode, expression)
		if s != "":
			lst = findall2list("[^\\r\\n]+", s)
			s = ""
			for e in lst:
				s = s + "\ntry:\n\t" + e + "\nexcept: pass"
			# end for
		# end if
		del lstKey[len(lstKey) - 1]
		if flag6pad == False:
			s = s + "\ntry:\n\tlst=dir(" + ".".join(lstKey) + ")\n\tfor e in lst: print(e)\nexcept: pass"
			# remplacement des self par le nom de la classe courante
			if curClassName != "": s = re.sub("([^a-zA-Z\\d_])self([^a-zA-Z\\d_])", "\\1" + curClassName + "\\2", s)
			# ajout des structures de code du code courant
			s = getBlocsStructure(lstBlocsLimits) + "\n" + s
			# précision du type d'encodage
			s = "# -*- coding: utf-8 -*-\n" + s
			# écriture
			writeFile(sPythonScript, s)
		else: # c'est le 6pad++ qui exécute
			lst = []
			# remplacement de self par le nom de la classe courante
			if curClassName != "": s = re.sub("([^a-zA-Z\\d_])self([^a-zA-Z\\d_])", "\\1" + curClassName + "\\2", s)
			# ajout de la structure des principaux blocs
			s = getBlocsStructure(lstBlocsLimits) + "\n" + s
			# précision du type d'encodage
			s = "# -*- coding: utf-8 -*-\n" + s
			# tentative d'exécution
			try: exec(s)
			except: pass
			try: lst = eval("dir(" + ".".join(lstKey) + ")")
			except: pass
			if len(lst) == 0:
				sayText("Echec avec l'interpréteur " + getCurInterpretorName())
				sp.window.messageBeep(1)
				return
			# end if
		# end if
	# end if
	if flag6pad == False:
		si = subprocess.STARTUPINFO()	
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		# exécution
		curProc = subprocess.Popen([sPythonPath, sPythonScript], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = si, universal_newlines = True)
		sResultConsole, sResultError = curProc.communicate()
		try: sResultConsole = sResultConsole.decode()
		except: sResultConsole = decode2(sResultConsole)
		# suppression du fichier temporaire
		os.remove(sPythonScript)
		if sResultConsole != "":
			lst = findall2list("[^\\r\\n]+", sResultConsole)
		else: # rien n'a été retourné
			sayText("Echec avec l'interpréteur " + getCurInterpretorName())
			sp.window.messageBeep(1)
			return
		# end if
	# end if
	# on ajoute les listes en attente
	lst = lst + lstVars + lstClassDef + lstModules
	if len(lst) == 0:
		sayText("Echec avec l'interpréteur " + getCurInterpretorName())
		sp.window.messageBeep(1)
		return
	# end if
	lst = sortList(lst)
	# doit-on enlever les doublons ?
	# attention, il y a une petite astuce.
	if flagPoint == True or flagModuleOnly == True: flagPoint = True
	else: lst = cleanList(lst)
	# détermination de l'item qui sera sélectionné
	selec = 0
	selec = getNierestExpression(lst, curKey)
	# proposition dans une liste de choix
	i = sp.window.choice("", "Complétion de code", lst, selec)
	if i >= 0:
		if iEnd > iStart: iEnd = iEnd + 1
		sp.window.curPage.replace(iStart, iEnd, lst[i])
		sp.window.curPage.position = iStart + len(lst[i])
	# end if
# end def

def listModules():
	# liste les modules appelables dans le scripting pour 6pad++
	lst = []
	try:
		import pkgutil
		for i in pkgutil.walk_packages():
			f, j, k = i
			lst.append(j)
		# end for
	except: pass
	try:
		import sys
		for e in sys.modules: lst.append(e)
	except: pass
	return lst
# end def

def listModulesInCurDir(flag6pad = False):
	# repertorie récursivement les modules potentiels présents dans le même dossier que le module courant
	lst = []
	path = getCurModuleDir()
	base = ""
	if flag6pad == True: base = getModuleRef(path)
	lst = lst + searchModules(path, base)
	return lst
# end def

def extractDeclarationsFromCode(s, expression):
	# extrait et renvoi toutes les déclarations liées à l'expression dans le texte
	code = s
	s = ""
	# décomposition des branches de l'expression dans une liste
	lstKey = expression.split(".")
	# premièrement, on repère les imports sans précision
	s = re.sub("^[ \\t]+", "", code, 0, re.M)
	lst = findall2list("^from[ \\t]+[a-zA-Z\\d_]+[ \\t]+import[ \\t]+\\*", s, re.M)
	if len(lst) > 0:
		s = "\n".join(lst) + "\n"
	else:
		s = ""
	# end if
	# on va rechercher toutes les autres déclarations grace à une fonction récursive
	s = s + searchDeclarations(code, lstKey[0])
	return s
# end def

def extractImportsFromCode(s):
	# extrait et renvoi les imports du texte dans une liste
	lst = []
	pt = "^[ \\t]*(import[ \\t]+[^\\r\\n]+|from[ \\t]+[^\\r\\n]+)"
	found = re.finditer(pt, s, re.I + re.M)
	for e in found:
		lst.append(e.group(1))
	# end for
	# lst=cleanList(lst)
	return lst
# end def

def extractVarsFromCode(s):
	# extrait du code les noms de variable qui reçoivent une valeur
	lst = []
	# pour les assignation unique sur une ligne 
	pt = "[\\r\\n]+[ \\t]*([a-zA-Z][a-zA-Z\\d_]*)[ \\t]*=[^=]"
	found = finditer2list(pt, s, re.I)
	for e in found:
		lst.append(e.group(1))
	# end for
	# pour les assignations multiples sur une ligne
	pt = "([\\r\\n]+[ \\t]*|[ \\t]*,[ \\t]*)([a-zA-Z][a-zA-Z\\d_]*)([ \\t]*=|[ \\t]*,)"
	found = finditer2list(pt, s, re.I)
	for e in found:
		lst.append(e.group(2))
	# end for
	# pour les assignations ou simples déclarations de paramètres dans les en-têtes de fonction
	pt = "[\\r\\n]+[ \\t]*def[ \\t]+[\\w\\d_]+[ \\t]*\\([^\\r\\n]{3,}"
	found = re.findall(pt, s)
	pt = "[,|\\(][ \\t]*([\\w\\d_]+)[ \\t]*"
	for e in found:
		found2 = finditer2list(pt, e)
		for e2 in found2:
			lst.append(e2.group(1))
		# end for
	# end for
	# tri par ordre alphabétique de la liste des variables trouvées 
	# lst.sort()
	# élimination de doublons
	# lst=cleanList(lst)
	return lst
# end def

def extractClassDefFromCode(s):
	# extrait les déclarations de classes et fonctions du texte
	lst = []
	pt = "[\\r\\n]+[ \\t]*(class|def)[ \\t]+([a-zA-Z\\d_]+)"
	found = finditer2list(pt, s, re.I)
	for e in found: lst.append(e.group(2))
	return lst
# end def

def runFile(filePath, params):
		# execute un fichier en lui passant un paramètre
		return subprocess.Popen([filePath, params], 0, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True, universal_newlines = True)
# end def

def runPythonFile(pythonExePath, pythonScriptPath, displayInConsole=False):
	# exécute le code python et fait éventuellement apparaître le renvoi # dans la fenêtre console.
	global curProc
	i = 0
	# sResultConsole = ""
	# sResultError = ""
	# vérification si chemin vers exécutable python existe
	if os.path.isfile(pythonExePath) == False:
		sp.window.alert("Aucun interpréteur python n'a été assigné ou le chemin de l'interpréteur actuel est éronné.\nVeuillez choisir un interpréteur valide.", "Erreur- interpréteur introuvable")
		return ""
	# end if ' fin si exÃ©cutable python n'a pas Ã©tÃ© repÃ©rÃ©
	
	# création de l'objet de retour
	file2 = ""
	# instruction qui envéront toute écriture dans la console vers le fichier créé.
	sys.stdout = file2
	sys.stderr = file2
	# variable à utiliser
	variable1 = ''
	variable2 = ''
	
	# changement du repertoire de travail
	# pour éviter les erreurs de fichiers non trouvés
	os.chdir(os.path.dirname(pythonScriptPath))
	
	si = subprocess.STARTUPINFO()
	si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	# exécution
	curProc = subprocess.Popen([pythonExePath, pythonScriptPath], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = si, universal_newlines = True)
	# curProc=subprocess.Popen([pythonExePath, pythonScriptPath], 0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
	sResultConsole, sResultError = curProc.communicate()
	# try: sResultConsole = sResultConsole.decode()
	# except: sResultConsole=decode2(sResultConsole)
	if sResultConsole != "":
		if displayInConsole == True:
			sp.console.print(sResultConsole)
		# end if fin si autorisation affichage dans pseudo console
	# end if fin si texte de retour
	# renvoi
	return sResultConsole
# End def

def runHTAApplication(path, flag = ""):
	# exécution de formulaire/application HTA
	if flag == "": flag = sp.getConfig("OpenHTAFilesWith", "1")
	# selon la valeur de flag
	if flag == "1":
		# avec subprocess.Popen,.
		# permet d'éviter l'ouverture de la console lors de l'exécution.
		# La valeur de la variable startupinfo sera alors affectée au paramètre startupinfo de la méthode check_call.
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		proc = subprocess.check_call(["mshta.exe", path], startupinfo = startupinfo)
	elif flag == "2":
		# avec os.system
		# ouvrira une fenêtre console
		# est modale
		# est succeptible de ne pas fonctionner avec des droit d'administration réduit
		# mais est le plus rapide
		os.system(path)
	elif flag == "3":
		# avec os.system et MSHTA
		# ouvrira une fenêtre console en arrière-plan
		# est modale
		# est rapide
		os.system('mshta.exe ""' + path + '""')
	elif flag == "4":
		# avec subprocess.Popen
		# permet d'éviter l'ouverture de la console lors de l'exécution.
		# La valeur de la variable startupinfo sera alors affectée au paramètre startupinfo de la classe Popen.
		# mais la fenêtre n'est pas modale
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		proc = subprocess.Popen(["mshta.exe", path], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, startupinfo = startupinfo)
	# end if
# end def

def sortList(lst):
	# trie la liste de str sans se soucier de la cass
	e = ""
	# astuce pour  réduire la cass sans perdre les repères
	i = - 1
	for e in lst:
		i = i + 1
		# on va doubler l'expression
		# la première partie sera en minuscule et servira à la comparaison
		# la seconde partie gardera la cass d'origine et sera restaurée à la fin des traitements.
		lst[i] = e.lower() + e
	# end for
	# tri proprement dit
	lst.sort()
	# restauration
	i = - 1
	for e in lst:
		i = i + 1
		lst[i] = e[int(len(e) / 2):]
	# end for
	return lst
# end def

def cleanList(lst):
	# supprime les doublons de la liste en paramètre
	# cette liste doit être ordonnée/triée au préalable
	n = len(lst)
	i = n - 1
	while(i > 0):
		if i > 0 and lst[i] == lst[i - 1]:
			del lst[i]
			i = i - 1
		# end if
		if i > 1 and lst[i] == lst[i - 2]:
			del lst[i]
			i = i - 1
			continue
		# end if
		
		i = i - 1
	# end while
	return lst
# end def

def createNewClass():
	# crée une nouvelle classse
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\data\\com.ini"
	pathFrm = getCurModuleDir() + "\\data\\frmCreateClass.hta"
	# infos d'indentation et de retours à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# vérification de la ligne courante
	iLine = sp.window.curPage.curLine
	sLine = sp.window.curPage.line(iLine)
	# si ligne non vide, alors erreur. La ligne doit être vide.
	if re.match("^[ \\t]*[^\\r\\n]+$", sLine):
		sp.window.alert("Vous ne pouvez pas créer une nouvelle classe sur une ligne non vide.", "Impossible de créer la classe à cet emplacement")
		return
	# end if
	indent = findall2list("^[ \\t]*", sLine)[0]
	if indent != "":
		if sp.window.confirm("Êtes-vous sûr de vouloir créer la nouvelle classe au niveau " + str(indent.count(iu)) + " ?") == 0:
			return
		# end if
	# end if
	# initialisation du fichier intermédiaire
	writeFile(pathIni, "")
	# exécution de la fenêtre HTA
	runHTAApplication(pathFrm)
	# traitement du résultat
	s = readFile(pathIni)
	if s == "": return
	className = finditer2list("className=([^\\r\\n]*)", s, re.I)[0].group(1)
	classDescription = finditer2list("description=([^\\r\\n]*)", s, re.I)[0].group(1)
	funcInitialize = finditer2list("funcInitialize=([^\\r\\n]*)", s, re.I)[0].group(1)
	funcTerminate = finditer2list("funcTerminate=([^\\r\\n]*)", s, re.I)[0].group(1)
	classGlobals = finditer2list("globals=([^\\r\\n]*)", s, re.I)[0].group(1)
	classProperties = finditer2list("properties=([^\\r\\n]*)", s, re.I)[0].group(1)
	classMethods = finditer2list("methods=([^\\r\\n]*)", s, re.I)[0].group(1)
	# génération progressive du texte
	s = ""
	# déclaration de la classe
	s = "class " + className + "():" + ru
	# si une description à la classe
	if classDescription != "":
		classDescription = classDescription.replace(separator, indent + iu + ru)
		s = s + indent + iu + "'''" + classDescription + "'''" + ru
	# end if
		s = s + indent + iu + ru
	# si des variables globales
	if classGlobals != "":
		lst = classGlobals.split(separator)
		for e in lst:
			if e.count("=") == 0:
				s = s + indent + iu + e + " = 0" + ru
			else:
				s = s + indent + iu + e + ru
			# end if
		# end for
		s = s + indent + iu + ru
	# end if	
	# si fonction d'initialisation
	if funcInitialize == "1":
		s = s + indent + iu + "def __init__(self):" + ru + indent + iu + iu + "a = 0" + ru
		s = s + indent + iu + "# end def" + ru
		s = s + indent + iu + ru
	# end if
	# si fonction de termination
	if funcTerminate == "1":
		s = s + indent + iu + "def __del__(self):" + ru + indent + iu + iu + "a = 0" + ru
		s = s + indent + iu + "# end def" + ru
		s = s + indent + iu + ru
	# end if
	# si des propriétés 
	if classProperties != "":
		lst = classProperties.split(separator)
		for e in lst:
			s = s + indent + iu + "@property" + ru + indent + iu + "def " + e + "(self):" + ru + indent + iu + iu + "return 0" + ru
			s = s + indent + iu + "# end def" + ru
			s = s + indent + iu + "@" + e + ".setter" + ru + indent + iu + "def " + e + "(self, newValue):" + ru + indent + iu + iu + "a = newValue" + ru
			s = s + indent + iu + "# end def" + ru
			s = s + indent + iu + ru
		# end for
	# end if	
	# si des méthodes
	if classMethods != "":
		lst = classMethods.split(separator)
		for e in lst:
			s = s + indent + iu + "def " + e + "(self):" + ru + indent + iu + iu + "a = 0" + ru
			s = s + indent + iu + "# end def" + ru
			s = s + indent + iu + ru
		# end for
		s = s + indent + iu + ru
	# end if	
	# cloture de la classe
	s = s + indent + "# end class" + ru
	# insertion
	sp.window.curPage.insert(sp.window.curPage.lineSafeStartOffset(iLine), s)
	sp.window.curPage.curLine = iLine
# end def

def createNewFunction():
	# crée une nouvelle fonction
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\data\\com.ini"
	pathFrm = getCurModuleDir() + "\\data\\frmCreateFunction.hta"
	# infos d'indentation et de retours à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# vérification de la ligne courante
	iLine = sp.window.curPage.curLine
	sLine = sp.window.curPage.line(iLine)
	# si ligne non vide, alors erreur. La ligne doit être vide.
	if re.match("^[ \\t]*[^\\r\\n]+$", sLine):
		sp.window.alert("Vous ne pouvez pas créer une nouvelle classe sur une ligne non vide.", "Impossible de créer la classe à cet emplacement")
		return
	# end if
	indent = findall2list("^[ \\t]*", sLine)[0]
	if indent != "":
		if sp.window.confirm("Êtes-vous sûr de vouloir créer la nouvelle classe au niveau " + str(indent.count(iu)) + " ?") == 0:
			return
		# end if
	# end if
	# initialisation du fichier intermédiaire
	writeFile(pathIni, "")
	# exécution de la fenêtre HTA
	runHTAApplication(pathFrm)
	# traitement du résultat
	s = readFile(pathIni)
	if s == "": return
	# recueillement des valeurs
	funcName = finditer2list("funcName=([^\\r\\n]*)", s, re.I)[0].group(1)
	funcType = finditer2list("funcType=([^\\r\\n]*)", s, re.I) [0].group(1)
	funcSelf = finditer2list("self=([^\\r\\n]*)", s, re.I)[0].group(1)
	funcParams = finditer2list("params=([^\\r\\n]*)", s, re.I)[0].group(1)
	funcDescription = finditer2list("description=([^\\r\\n]*)", s, re.I)[0].group(1)
	# génération progressive du code de la fonction
	s = ""
	# préparations
	funcDescription = funcDescription.replace(separator, indent + iu + ru)
	lst = []
	if funcSelf == "1": lst.append("self")
	if funcParams != "": lst = lst + funcParams.split(separator)
	#
	if funcType == "def":
		s = "def " + funcName + "(" + ", ".join(lst) + "):" + ru
		if funcDescription != "": s = s + indent + iu + "''' " + funcDescription + " '''" + ru
		s = s + indent + iu + "a = 0" + ru
		s = s + indent + "# end def" + ru
	elif funcType == "property":
		s = s + indent + "@property" + ru + indent + "def " + funcName + "(self):" + ru
		if funcDescription != "": s = s + indent + iu + "''' " + funcDescription + " '''" + ru
		s = s + indent + iu + "return 0" + ru
		s = s + indent + "# end def" + ru
		s = s + indent + iu + "@" + funcName + ".setter" + ru + indent + "def " + funcName + "(self, newValue):" + ru + indent + iu + "a = newValue" + ru
		s = s + indent + "# end def" + ru
	# end if
	# insertion
	sp.window.curPage.insert(sp.window.curPage.lineSafeStartOffset(iLine), s)
	sp.window.curPage.curLine = iLine
# end def

def setOptions():
	# affiche la fenêtre de fixation des options de forPython
	global gWayOfActivatingForPython, gCheckLineSyntax, gGoToLineOfError, gShowErrorsIn, gWriteErrorsInLogFile, gAddEndTagsAtCodeCompletion
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\data\\com.ini"
	pathFrm = getCurModuleDir() + "\\data\\frmOptions.hta"
	# infos d'indentation et de retours à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# constitution des infos à envoyer au formulaire HTA
	s = "\r\n"
	# la manière d'activer le forPython
	s += "WayOfActivatingForPython=" + sp.getConfig("WayOfActivatingForPython", "1") + "\r\n"
	# liste des extensions de fichier python supportés
	s += "PythonExtensionsSupported=" + sp.getConfig("PythonExtensionsSupported", "py, pyw") + "\r\n"
	# si proposition du 6pad++ pour ouvrir les fichiers python
	s += "Propose6padToOpenPythonFiles=" + sp.getConfig("Propose6padToOpenPythonFiles", "py, pyw") + "\r\n"
	# si vérification automatique de la syntaxe des lignes modifiées
	s += "forPythonCheckLineSyntax=" + sp.getConfig("forPythonCheckLineSyntax", "1") + "\r\n"
	# si déplacement automatique à la ligne de l'erreur d'exécution
	s += "forPythonGoToLineOfError=" + sp.getConfig("forPythonGoToLineOfError", "1") + "\r\n"
	# dans quoi afficher les erreurs d'exécution
	s += "forPythonShowErrorsIn=" + sp.getConfig("forPythonShowErrorsIn", "1") + "\r\n"
	# si écriture des erreurs dans un fichier log
	s += "forPythonWriteErrorsInLogFile=" + sp.getConfig("forPythonWriteErrorsInLogFile", "0") + "\r\n"
	# si activation du module des collages alternatifs
	s += "forPythonActivatePasteManager=" + sp.getConfig("forPythonActivatePasteManager", "1") + "\r\n"
	# si activation du module de gestion de version de document
	s += "forPythonActivateVersioningManager=" + sp.getConfig("forPythonActivateVersioningManager", "1") + "\r\n"
	# si activation du module de gestion des raccourcis clavier
	s += "forPythonActivateShortcutsManager=" + sp.getConfig("forPythonActivateShortcutsManager", "1") + "\r\n"
	# si ajout de balises de fin de bloc au chargement du document
	s += "AddEndTagsAtFileLoading=" + sp.getConfig("AddEndTagsAtFileLoading", "0") + "\r\n"
	# si ajout des balises de fin de bloc à la complétion de code
	s += "AddEndTagsAtCodeCompletion=" + sp.getConfig("AddEndTagsAtCodeCompletion", "0") + "\r\n"
	# type d'ouverture des fichiers HTA
	s += "OpenHTAFilesWith=" + sp.getConfig("OpenHTAFilesWith", "1") + "\r\n"
	# si activation de la sauvegarde automatique
	s += "forPythonActivateAutomaticSave=" + sp.getConfig("forPythonActivateAutomaticSave", "1") + "\r\n"
	# l'interval de la sauvegarde automatique
	s += "forPythonAutomaticSaveInterval=" + sp.getConfig("forPythonAutomaticSaveInterval", "1") + "\r\n"
	# si masquage des fichiers de sauvegarde
	s += "forPythonHideSaveFiles=" + sp.getConfig("forPythonHideSaveFiles", "0") + "\r\n"
	# initialisation du fichier intermédiaire
	writeFile(pathIni, s)
	# exécution de la fenêtre HTA
	runHTAApplication(pathFrm)
	# traitement du résultat
	s = readFile(pathIni)
	if s == "": return
	# prise en compte des valeurs
	# et enregistrement dans le fichier ini
	transferConfig(s, "WayOfActivatingForPython", "WayOfActivatingForPython")
	gWayOfActivatingForPython = sp.getConfig("WayOfActivatingForPython", "1")
	transferConfig(s, "PythonExtensionsSupported", "PythonExtensionsSupported")
	gPythonExtensionsSupported = sp.getConfig("PythonExtensionsSupported", "py, pyw").replace(" ", "").split(",")
	transferConfig(s, "Propose6padToOpenPythonFiles", "Propose6padToOpenPythonFiles")
	transferConfig(s, "forPythonCheckLineSyntax", "forPythonCheckLineSyntax")
	gCheckLineSyntax = (sp.getConfig("forPythonCheckLineSyntax", "1") == "1")
	transferConfig(s, "forPythonGoToLineOfError", "forPythonGoToLineOfError")
	gGoToLineOfError = (sp.getConfig("forPythonGoToLineOfError", "1") == "1")
	transferConfig(s, "forPythonShowErrorsIn", "forPythonShowErrorsIn")
	gShowErrorsIn = sp.getConfig("forPythonShowErrorsIn", "1")
	transferConfig(s, "forPythonWriteErrorsInLogFile", "forPythonWriteErrorsInLogFile")
	gWriteErrorsInLogFile = (sp.getConfig("forPythonWriteErrorsInLogFile", "1") == "1")
	transferConfig(s, "forPythonActivatePasteManager", "forPythonActivatePasteManager")
	if sp.getConfig("forPythonActivatePasteManager", "1") == "1":
		loadPasteTools()
	else:
		unloadPasteTools()
	# end if
	transferConfig(s, "forPythonActivateVersioningManager", "forPythonActivateVersioningManager")
	if sp.getConfig("forPythonActivateVersioningManager", "1") == "1":
		loadVersioningTools()
	else:
		unloadVersioningTools()
	# end if
	transferConfig(s, "forPythonActivateShortcutsManager", "forPythonActivateShortcutsManager")
	if sp.getConfig("forPythonActivateVersioningManager", "1") == "1":
		loadManageShortcutsTools()
	else:
		unloadManageShortcutsTools()
	# end if
	transferConfig(s, "AddEndTagsAtFileLoading", "AddEndTagsAtFileLoading")
	transferConfig(s, "AddEndTagsAtCodeCompletion", "AddEndTagsAtCodeCompletion")
	gAddEndTagsAtCodeCompletion = (sp.getConfig("AddEndTagsAtCodeCompletion", "0") == "1")
	transferConfig(s, "OpenHTAFilesWith", "OpenHTAFilesWith")
	transferConfig(s, "forPythonActivateAutomaticSave", "forPythonActivateAutomaticSave")
	transferConfig(s, "forPythonAutomaticSaveInterval", "forPythonAutomaticSaveInterval")
	transferConfig(s, "forPythonHideSaveFiles", "forPythonHideSaveFiles")
# end def

def transferConfig(s, configNameSource, configNameTarget, multiple = False):
	# transfert la valeur d'un paramètre vers le fichier ini de 6pad++
	# utile à la fonction immédiatement plus haut
	v = ""
	if s.find(configNameSource + "=") > -1:
		v = str(finditer2list("[\\r\\n]+" + configNameSource + "\\=([^\\r\\n]*)", s, re.I)[0].group(1))
		sp.setConfig(configNameTarget, v, multiple)
		# alert(configNameSource+"="+str(v)+"\r\n"+s)
	else:
		# alert("échec " + configNameSource + "\r\n" + s)
		i=0
	# end if
# end def

def isPythonFile(page = None):
	# détermine si la page en paramètre contient un fichier python
	if page == None: page = sp.window.curPage
	if page == None: return False
	sFile = page.file
	iLength = len(sFile)
	for i in range(len(gPythonExtensionsSupported)):
		if sFile[iLength - len(gPythonExtensionsSupported[i])-1:].lower() == "."+gPythonExtensionsSupported[i].lower():
			return True
		# end if
	# end for
	return False
# end def

def isLineCommented(ln):
	""" check if a comment is in this line """
	lst = getStringsPos(ln)
	if len(lst) == 0: return False
	d, f = lst[len(lst) - 1]
	if ln[d] == "#": return True
	return False
# end def

def isWithinTripleQuotes(page, pos, lstTrippleQuotes = None):
	""" check if cursor is within tripple quotes area """
	s = page.text
	if lstTrippleQuotes == None: lstTrippleQuotes = getTripleQuotePos(s)
	if len(lstTrippleQuotes) == 0: return False
	for d, f in lstTrippleQuotes:
		if d <= pos and pos <= f: return True
	# end for
	return False
# end def

def isWithinClass(iLine, lstBlocsLimits = None):
	""" check if cursor is within a class """
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	for (level, key, name, d, f, sLine) in lstBlocsLimits:
		if key == "class":
			if iLine >= d and iLine <= f: return True
		# end if
	# end for
	return False
# end def

def isWithinFunction(iLine, lstBlocsLimits = None):
	""" check if cursor is within a function """
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	for (level, key, name, d, f, sLine) in lstBlocsLimits:
		if key == "def":
			if iLine >= d and iLine <= f: return True
		# end if
	# end for
	return False
# end def

def isImportationArea():
	""" check if current line is a line of import, and cursor on a key word """
	page = sp.window.curPage
	iLine = page.curLine
	pos = page.position
	sLine = page.line(iLine)
	start = page.lineStartOffset(iLine)
	sLine = sLine[0: (pos - start)]
	if re.match("^[ \\t]*(import[ \\t]+[a-zA-Z_\\d_]*|from[ \\t]+[a-zA-Z\\d_]*)$", sLine, re.I):
		# import x ou from x
		return True
	elif re.match(".*?__import__[ \\t]*\\([ \\t]*[a-zA-Z\\d_\\.]*", sLine, re.I):
		# __import(x
		return True
	else:
		return False
	# end if
# end def

def isDirectLine(sLine):
	""" check if a line exec many statements """
	# vérifie si la ligne exécute plusieurs instructions au lieu d'une seule après un ':'
	d, f = 0, 0
	# D'abord, Transfert dans une liste classique
	l = []
	for e in sLine: l.append(e)
	# si potentiellement présence de strings ou partie de commentaire
	# on va les masquer par des caractères neutres
	if sLine.find("'") >= 0 or sLine.find('"') >= 0:
		lst = getStringsPos(sLine)
		for(d, f) in lst:
			if l[d] == "#": masc = " "
			else: masc = "a"
			for i in range(d, f + 1):
				l[i] = masc
			# end for
		# end for
	# end if
	# si présence de crochets,
	# on les masque également
	ibrac = 0
	flag = False
	for i in range(0, len(l)):
		e = l[i]
		if e == "[":
			ibrac = ibrac + 1
			flag = True
		elif e == "]":
			l[i] = "b"
			ibrac = ibrac - 1
			if ibrac == 0: flag = False
		# end if
		if flag == True: l[i] = "b"
	# end for
	sLine = "".join(l)
	# test
	if re.match("^.+?:[ \\t]*[a-zA-Z_]", sLine):
		return True
	else:
		return False
	# end if
# end def

def isStringBalanced(s):
	# vérification de l'équilibre des guillemets et appostrophes
	# on en profitera pour faire certains repérages
	flag = False
	char = ""
	prev = ""
	stringList = []
	d = - 1
	f = - 1
	commentStart = - 1
	litteral = False
	i = - 1
	for e in s:
		i = i + 1
		if flag == False:
			if e == "#": # caractère dièze
				commentStart = i
				break
			elif e == '"': # caractère guillemet
				char = '"'
				d = i
				flag = True
				if s[i - 1] == "r": litteral = True
				else: litteral = False
			elif e == "'": # caractère appostrophe
				char = "'"
				d = i
				flag = True
				if s[i - 1]: litteral = True
				else: litteral = False
			# end if
		else: # flag==True
			if e == char:
				if prev == "\\" and litteral == True: 
					prev = e
					continue
				elif prev == "\\" and litteral == False: 
					k = i - 1
					s3 = ""
					while(k >= 0):
						if s[k] == "\\": s3 = s3 + "\\"
						k = k - 1
					# end while
					# le nombre d'antislash doit être impaire
					if len(s3) % 2 != 0:
						prev = e
						continue
					# end if
				# end if
				f = i
				stringList.append((d, f))
				flag = False # fermeture du guillemet
			# end if
		# end if
		prev = e
	# end for
	# renvoi  du tuple constitué de:
	#  vrai si  les strings sont équilibrés
	# et la liste des positions de strings trouvés
	return not flag, stringList
# end def

def isModuleExist(moduleName):
	""" check if a module exist """
	try: 
		__import__(moduleName)
	except ImportError: 
		return False 
	else: 
		return True
	# end try
# end def

def isSyntaxValid(code):
	""" check if the syntax of a code is valid """
	s = "try:\r\n\texec(\" "+code+" \")\r\nexcept SyntaxError:\r\n\traise"
	sp.window.alert(s)
	exec(s)
# end def

def onPageOpened(newPage):
	""" event when a new page opens """
	if isPythonFile(newPage) == True:
		CreatePythonTools()
	else:
		removePythonTools()
	# end if
	sayText("Nouvelle page ouverte")
# end def

def tmrLineMove():
	""" triggered to check if the ligne has changed """
	global iLastLine, sLastLine
	global flagCheckLineMove, flagCheckLine
	if sp.window.curPage == None: return
	if flagCheckLine == False: return
	if flagCheckLineMove == False: return
	iLine = sp.window.curPage.curLine
	# s'il y a eu  changement de ligne
	if iLine != iLastLine:
		# si la ligne a Ã©tÃ© modifiÃ©e entre temps
		sLine = sp.window.curPage.line(iLastLine)
		if sLine != sLastLine:
			flagCheckLineMove = False # suspension
			if checkLine(sp.window.curPage, iLastLine) == False:
				sLastLine = sp.window.curPage.line(iLastLine)
				sp.window.curPage.position = sp.window.curPage.lineSafeStartOffset(iLastLine)
				flagCheckLineMove = True # relance
				return
			# end if
			flagCheckLineMove = True # relance
		# end if
		iLastLine = iLine
		sLastLine = sp.window.curPage.line(iLine)
	# end if
# end def

def checkLine(page, line):
	""" check a line syntax validity """
	# si autorisé
	if gCheckLineSyntax == False: return True
	ru = getCurReturnUnit()
	curLine = page.curLine
	s = page.line(line)
	s2 = s # sauvegarde
	# si ligne vide, alors forcément valide
	if re.match("^[ \\t]*$", s): return True
	# si ligne de commentaire, alors forcément valide
	if re.match("^[ \\t]*\\#", s):
		# si balise de fin de bloc identifiée
		pt = "^([ \\t]*)\\#[ \\t]*end[ \\t]*(class|def|while|for|if|try|with)[ \\t]*([^\\r\\n]*)"
		if re.match(pt, s, re.I):
			# Re-écriture de la ligne pour s'assurer du bon formattage
			indent = finditer2list(pt, s, re.I)[0].group(1)
			key = finditer2list(pt, s, re.I)[0].group(2).lower()
			supplement = finditer2list(pt, s, re.I)[0].group(3)
			s = indent + "# end " + key + " " + supplement
			s = s.rstrip()
			page.replace(page.lineStartOffset(line), page.lineEndOffset(line), s)
			page.position = page.lineSafeStartOffset(curLine)
		# end if
		return True
	# end if
	# si potentielle ligne  de fin de bloc sans le caractère # diez au début
	pt = "^[ \\t]*end[ \\t]*(class|def|while|for|if|try|with)"
	if re.match(pt, s, re.I):
		# prise en compte de plusieurs cas possibles
		pt1 = "^[ \\t]*end[ \\t]+(class|def|while|for|if|try|with)[ \\t]*([^\\r\\n]*)"
		pt2 = "^[ \\t]*end(class|def|while|for|if|try|with)[ \\t\\r\\n]*$"
		pt3 = "^[ \\t]*end(class|def|while|for|if|try|with)[ \\t]+\\#[^\\r\\n]*"
		if re.match(pt1, s, re.I) or re.match(pt2, s, re.I) or re.match(pt3, s, re.I):
			# Re-écriture de la ligne pour s'assurer du bon formattage
			indent = finditer2list("^[ \\t]*", s, re.I)[0].group(0)
			key = finditer2list("^[ \\t]*end[ \\t]*(class|def|while|for|if|try|with)", s, re.I)[0].group(1).lower()
			supplement = finditer2list("^[ \\t]*end[ \\t]*(class|def|while|for|if|try|with)[ \\t]*([^\\r\\n]*)", s, re.I)[0].group(2)
			s = indent + "# end " + key + " " + supplement
			s = s.rstrip()
			page.replace(page.lineStartOffset(line), page.lineEndOffset(line), s)
			page.position = page.lineSafeStartOffset(curLine)
			return True
		# end if
	# end if
	# si sur la ligne il y a des triples quotes d'un nombre de caractère incorrect
	# on va les réduire à trois
	if re.match("([\\" + '"' + "]{4,}|[']{4,})", s):
		# cas des appostrophes
		s = re.sub("[']{4,}", "'''", s)
		# cas des guillemets
		s = re.sub("[\\" + '"' + "]{4,}", "\" \"\"", s)
		# re-écriture
		page.replace(page.lineStartOffset(line), page.lineEndOffset(line), s)
		page.position = page.lineSafeStartOffset(curLine)
	# end if
	
	# si le début ou la fin de la ligne est à l'intérieur de triples quotes, alors elle est forcément valide
	lstTripleQuote = getTripleQuotePos(page.text)
	if isWithinTripleQuotes(page, page.lineStartOffset(line), lstTripleQuote) or isWithinTripleQuotes(page, page.lineEndOffset(line), lstTripleQuote):
		return True
	# end if
	# Vérification qu'on ne doit pas mélanger les types d'indentation en début de ligne
	lst = finditer2list("^[ \\t]+", s)
	if len(lst) > 0:
		indent = lst[0].group(0)
		if indent.count(" ") > 0 and indent.count("\t") > 0:
			sp.window.alert("Deux types d'indentation ont été détectés au début de la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur d'indentation")
			return False
		# end if
	# end if
	# retrait de l'indentation
	s = re.sub("^[ \\t]+", "", s)
	# si les lignes précédentes se terminent par une virgule ou un antislash, on les inclus
	i = line-1
	while(i >= 0):
		s3 = page.line(i) # ligne précédente
		if isLineCommented(s3) == True: break
		if re.match("(,|\\\\)[ \\t]*$", s3):
			s = s3 + ru + s
		else:
			break
		# end if
		i = i-1
	# end while
	# vérification de l'équilibre des guillemets et appostrophes
	# on en profitera pour faire certains repérages
	flag = False
	char = ""
	prev = ""
	stringList = []
	d = - 1
	f = - 1
	commentStart = - 1
	litteral = False
	i = - 1
	for e in s:
		i = i + 1
		if flag == False:
			if e == "#": # caractère dièze
				commentStart = i
				break
			elif e == '"': # caractère guillemet
				char = '"'
				d = i
				flag = True
				if s[i - 1] == "r": litteral = True
				else: litteral = False
			elif e == "'": # caractère appostrophe
				char = "'"
				d = i
				flag = True
				if s[i - 1]: litteral = True
				else: litteral = False
			# end if
		else: # flag==True
			if e == char:
				if prev == "\\" and litteral == True: 
					prev = e
					continue
				elif prev == "\\" and litteral == False: 
					k = i - 1
					s3 = ""
					while(k >= 0):
						if s[k] == "\\": s3 = s3 + "\\"
						k = k - 1
					# end while
					# le nombre d'antislash doit être impaire
					if len(s3) % 2 != 0:
						prev = e
						continue
					# end if
				# end if
				f = i
				stringList.append((d, f))
				flag = False # fermeture du guillemet
			# end if
		# end if
		prev = e
	# end for
	if flag == True: # quotation non refermée
		sp.window.alert("Une chaîne string a été ouverte par le caractère (" + char + " et n'a pas été refermé à la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur de chaîne string sans fermeture")
		return False
	# end if
	# Retrait d'une éventuelle partie commentaire
	if commentStart >= 0: s = s[0:commentStart]
	# Remplacement des déclarations de string par des pseudo variables
	lst = []
	e = ""
	for e in s: lst.append(e)
	for d, f in stringList:
		for i in range(d, f + 1): lst[i] = "a" # remplacement par des a
	# end for
	s = "".join(lst)
	#  si la ligne se termine par une virgule ou un antislash
	if re.match("(,|\\\\)[ \\t]*$", s):
		s = s
	else: # pas de virgule ou d'antislash à la fin de la ligne
		# Vérification de l'équilibre des accolades
		if s.find("{") >= 0 or s.find("}") >= 0:
			if s.count("{") != s.count("}"):
				sp.window.alert("Il y a un déséquilibre des accolades '{}' à la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur- déséquilibre des accolades")
				return False 
			# end if
		# end if
		# Vérification de l'équilibre des parenthèses
		if s.find("(") or s.find(")"):
			if s.count("(") != s.count(")"):
				sp.window.alert("Il y a un déséquilibre des parenthèses '()' à la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur- déséquilibre des parenthèses")
				return False
			# end if
		# end if
		# vérification de l'équilibre des crochets
		if s.find("[") >= 0 or s.find("]") >= 0:
			if s.count("[") != s.count("]"):
				sp.window.alert("Il y a un déséquilibre des crochets '[]' à la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur- déséquilibre des crochets")
				return False
			# end if
		# end if
	# end if
	# vérification si il doit y avoir un deux point à la fin de la ligne 
	if re.match("^[ \\t]*(class|def|while|for|if|with|elif|else|try|except|finally)(:|[ \\t\\(]+|$)", s, re.I):
		# on masque préalablement les éventuels deux points dans les crochets
		s = re.sub("\\[[^\\]]+\\]", "", s)
		if s.find(":") <= 0:
			sp.window.alert("Il manque le caractère deux points ':' à la fin de la ligne " + str(line + 1) + ":\r\n '" + s2 + "'", "Erreur- absence des deux points")
			return False
		# end if
	# end if
	# re-écritures et ajustement du code de la ligne
	s = s2
	s = refreshCode(s)
	# ré-insertion de la ligne re-écrite dans la page	
	page.replace(page.lineStartOffset(line), page.lineEndOffset(line), s)
	page.position = page.lineSafeStartOffset(curLine)
	# renvoi final
	return True # ligne valide
# end def

def goToEndOfElement():
	""" go to the end of current class or function """
	lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	curLine = sp.window.curPage.curLine
	curKey = ""
	# recherche du bloc courant et de sa dernière ligne
	line = -1
	for i in range(len(lstBlocsLimits)):
		level, key, name, d, f, sLine = lstBlocsLimits[i]
		if curLine>=d and curLine<=f:
			line = f
			curKey = key
		# end if
	# end for
	if line > -1:
		sayText("Fin du bloc " + curKey)
		sp.window.curPage.curLine = line
		# lecture du numéro de la ligne
		sayText("line " + str(line + 1))
	else:
		sp.window.messageBeep(0)
	# end if
# end def

def searchAdvanced():
	""" open a dialog that is another more advanced way of searching """
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\data\\com.ini"
	pathFrm = getCurModuleDir() + "\\data\\frmSearch.hta"
	# infos d'indentation et de retours à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# on retrouve les paramètres enregistrés
	lst = sp.getConfig("lastSearchParams", (separator * 11)).split(separator)
	# détermination d'une éventuelle expression sous le curseur
	expression, d, f = getCurExpression()
	# constitution du texte intermédiaire
	try:
		s = ""
		# le texte à rechercher
		if lst[1] == "1" and expression != "": s = s + "textToSearch=" + expression + "\r\n"
		else: s = s + "textToSearch=" + lst[0] + "\r\n"
		# le type de recherche
		if lst[1] != "": s = s + "searchType=" + lst[1] + "\r\n"
		# la direction de la recherche
		if lst[2] != "": s = s + "searchDirection=" + lst[2] + "\r\n"
		# la zone de recherche
		if lst[3] != "": s = s + "searchZone=" + lst[3] + "\r\n"
		# le respect de la cass
		if lst[4] != "": s = s + "respectCase=" + lst[4] + "\r\n"
		# mot seul uniquement
		if lst[5] != "": s = s + "allWordOnly=" + lst[5] + "\r\n"
	except: pass
	# écriture des paramètres dans le fichier intermédiaire
	writeFile(pathIni, s)
	if expression.count(".") > 0: expression = expression.split(".")[- 1]
	# exécution de la fenêtre HTA
	runHTAApplication(pathFrm)
	# traitement du résultat
	s = readFile(pathIni)
	if s == "": return
	# recueillement des valeurs
	textToSearch = finditer2list("textToSearch=([^\\r\\n]*)", s, re.I)[0].group(1)
	textToSearch2 = textToSearch
	searchType = finditer2list("searchType=([^\\r\\n]*)", s, re.I)[0].group(1)
	searchDirection = finditer2list("searchDirection=([^\\r\\n]*)", s, re.I)[0].group(1)
	searchZone = finditer2list("searchZone=([^\\r\\n]*)", s, re.I)[0].group(1)
	respectCase = finditer2list("respectCase=([^\\r\\n]*)", s, re.I)[0].group(1)
	allWordOnly = finditer2list("allWordOnly=([^\\r\\n]*)", s, re.I)[0].group(1)
	# traitement des paramètres renvoyés
	#  si pas expression régulière
	if searchType == "1":
		# on insère des caractères d'échappement pour certains caractères du texte à remplacer
		textToSearch = re.sub("([\\W])", "\\\\1", textToSearch)
	# end if
	# si mot entier uniquement
	if allWordOnly == "1":
		textToSearch = "([^\\w\\d_]+)" + textToSearch + "([^\\w\\d_]+)"
	# end if
	# selon la zone déterminée
	s = ""
	l = sp.window.curPage.curLine
	lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	lines = sp.window.curPage.text.split(ru)
	if searchZone == "1": # le document courant
		s = sp.window.curPage.text
	elif searchZone == "2": # la classe courante
		for(level, key, name, d, f, sLine) in lstBlocsLimits:
			if key == "class":
				if l >= d and l <= f:
					# recueillement des lignes de la classe en question
					s = ru.join(lines[d: f + 1])
					break
				# end if
			# end if
		# end for
		if s == "":
			sp.window.alert("Aucune classe n'a été détectée sous le curseur. action impossible", "Action impossible")
			return
		# end if
	elif searchZone == "3": # la fonction courante
		i = len(lstBlocsLimits)
		while(i > 0):
			i = i - 1
			level, key, name, d, f, sLine = lstBlocsLimits[i]
			if key == "def":
				if l >= d and l <= f:
					s = ru.join(lines[d: f + 1])
					break
				# end if
			# end if
		# end while
		if s == "":
			sp.window.alert("Aucune fonction n'a été détectée sous le curseur. action impossible", "Action impossible")
			return
		# end if
	elif searchZone == "4": # le texte sélectionné
		s = sp.window.curPage.selectedText
	# end if
	# recherche
	if respectCase == "1":
		i = 0
	else:
		i = 0
	# end if
	# enregistrement des paramètres dans le fichier ini
	sp.setConfig("lastSearchParams", textToSearch2 + separator + searchType + separator + searchDirection + separator + respectCase + separator + allWordOnly)
# end def

def searchAndReplaceAdvanced():
	""" open a dialog that is another more advanced way of searching and replacing """
	s = ""
	separator = ",,,"
	# infos sur la position et les limites de blocs
	l = sp.window.curPage.curLine
	lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\data\\com.ini"
	pathFrm = getCurModuleDir() + "\\data\\frmReplace.hta"
	# infos d'indentation et de retours à la ligne
	ru = getCurReturnUnit()
	iu = getCurIndentUnit()
	# on retrouve les paramètres enregistrés
	lst = sp.getConfig("lastReplacementParams", (separator * 11)).split(separator)
	# détermination d'une éventuelle expression sous le curseur
	expression, d, f = getCurExpression()
	# constitution du texte intermédiaire
	try:
		s = ""
		# le texte à remplacer
		if lst[2] == "1" and expression != "": s = s + "textToReplace=" + expression + "\r\n"
		else: s = s + "textToReplace=" + lst[0] + "\r\n"
		# le texte de remplacement
		s = s + "replaceBy=" + lst[1] + "\r\n"
		# le type de recherche
		if lst[2] != "": s = s + "searchType=" + lst[2] + "\r\n"
		# la direction de la recherche
		if lst[3] != "": s = s + "searchDirection=" + lst[3] + "\r\n"
		# la zone de recherche
		if lst[4] != "": s = s + "searchZone=" + lst[4] + "\r\n"
		# si respect de la cass
		if lst[5] != "": s = s + "respectCase=" + lst[5] + "\r\n"
		# si mot seul uniquement
		if lst[6] != "": s = s + "allWordOnly=" + lst[6] + "\r\n"
	except: pass
	# si texte sélectionné
	s = s + "IsSelectedText=" + str(sp.window.curPage.selectedText != "") + "\r\n"
	# si  curseur actuel à l'intérieur d'une classe
	s = s + "IsInClass=" + str(isWithinClass(l, lstBlocsLimits)) + "\r\n"
	# si  curseur actuel à l'intérieur d'une fonction
	s = s + "IsInFunction=" + str(isWithinFunction(l, lstBlocsLimits)) + "\r\n"
	# écriture des paramètres dans le fichier intermédiaire
	writeFile(pathIni, s)
	if expression.count(".") > 0: expression = expression.split(".")[- 1]
	# exécution de la fenêtre HTA
	runHTAApplication(pathFrm)
	# traitement du résultat
	s = readFile(pathIni)
	if s == "": return
	# recueillement des valeurs
	textToReplace = finditer2list("textToReplace=([^\\r\\n]*)", s, re.I)[0].group(1)
	textToReplace2 = textToReplace
	replaceBy = finditer2list("replaceBy=([^\\r\\n]*)", s, re.I)[0].group(1)
	replaceBy2 = replaceBy
	searchType = finditer2list("searchType=([^\\r\\n]*)", s, re.I)[0].group(1)
	searchDirection = finditer2list("searchDirection=([^\\r\\n]*)", s, re.I)[0].group(1)
	searchZone = finditer2list("searchZone=([^\\r\\n]*)", s, re.I)[0].group(1)
	respectCase = finditer2list("respectCase=([^\\r\\n]*)", s, re.I)[0].group(1)
	allWordOnly = finditer2list("allWordOnly=([^\\r\\n]*)", s, re.I)[0].group(1)
	# traitement des paramètres renvoyés
	#  si pas expression régulière
	if searchType == "1":
			# on insère des caractères d'échappement pour certains caractères du texte à remplacer
		textToReplace = re.sub("([\\W])", "\\\\1", textToReplace)
		# on insère des caractères d'échappement pour certains caractères du texte de remplacement
		replaceBy = re.sub("([\\W])", "\\\\1", replaceBy)
	# end if
	# si mot entier uniquement
	if allWordOnly == "1":
		textToReplace = "([^\\w\\d_])" + textToReplace + "([^\\w\\d_])"
		replaceBy = "\\1" + replaceBy + "\\" + str(textToReplace.count("("))
	# end if
	# selon la zone de remplacement déterminée
	s = ""
	lines = sp.window.curPage.text.split(ru)
	lstPage = []
	if searchZone == "1": # le document courant
		s = sp.window.curPage.text
	elif searchZone == "2": # la classe courante
		for(level, key, name, d, f, sLine) in lstBlocsLimits:
			if key == "class":
				if l >= d and l <= f:
					# recueillement des lignes de la classe en question
					s = ru.join(lines[d: f + 1])
					break
				# end if
			# end if
		# end for
		if s == "":
			sp.window.alert("Aucune classe n'a été détectée sous le curseur. action impossible", "Action impossible")
			return
		# end if
	elif searchZone == "3": # la fonction courante
		i = len(lstBlocsLimits)
		while(i > 0):
			i = i - 1
			level, key, name, d, f, sLine = lstBlocsLimits[i]
			if key == "def":
				if l >= d and l <= f:
					s = ru.join(lines[d: f + 1])
					break
				# end if
			# end if
		# end while
		if s == "":
			sp.window.alert("Aucune fonction n'a été détectée sous le curseur. action impossible", "Action impossible")
			return
		# end if
	elif searchZone == "4": # le texte sélectionné
		s = sp.window.curPage.selectedText
	elif searchZone == "5": # tous les onglets ouverts
		for p in sp.window.pages:
			lstPage.append(p.text)
		# end for
	# end if
	# création de la liste de texte à remplacer
	lst = []
	if len(lstPage) > 0:
		for s in lstPage: lst.append(s)
	else: # pas de remplacement sur plusieurs onglets
		lst.append(s)
	# end if
	# remplacements
	# et décompte du nombre de remplacement dans la foulée
	nb = 0
	for i in range(len(lst)):
		s = lst[i]
		if respectCase == "1":
			nb = nb + len(re.findall(textToReplace, s))
			s = re.sub(textToReplace, replaceBy, s)
		else:
			nb = nb + len(re.findall(textToReplace, s, re.IGNORECASE))
			s = re.sub(textToReplace, replaceBy, s, 0, re.IGNORECASE)
		# end if
		lst[i] = s
	# end for
	# enregistrement des paramètres dans le fichier ini
	sp.setConfig("lastReplacementParams", textToReplace2 + separator + replaceBy2 + separator + searchType + separator + searchDirection + separator + searchZone + separator + respectCase + separator + allWordOnly)
	# si aucun changement effectué
	if nb == 0:
		sp.window.alert("Aucune occurence du texte recherché n'a été trouvé et remplacée.", "Aucun remplacement effectué")
		return
	else: # des occurences ont été remplacées
		# message d'avertissement et de confirmation
		if sp.window.confirm(str(nb) + " remplacement effectués dans " + str(len(lst)) + " documents.\r\nÊtes-vous sûrs de vouloir les conserver ?") == 0: return
		# selon la zone de remplacement, on restore le texte
		s = lst[0]
		if searchZone == "1": # le document courant
			sp.window.curPage.text = s
		elif searchZone == "2": # la classe courante
			sp.window.curPage.replace(sp.window.curPage.lineStartOffset(d), sp.window.curPage.lineEndOffset(f), s)
		elif searchZone == "3": # la fonction courante
			sp.window.curPage.replace(sp.window.curPage.lineStartOffset(d), sp.window.curPage.lineEndOffset(f), s)
		elif searchZone == "4": # le texte sélectionné
			sp.window.curPage.selectedText = s
		elif searchZone == "5": # tous les onglets ouverts
			i = -1
			for p in sp.window.pages:
				i = i + 1
				p.text = lst[i]
			# end for
		# end if
	# end if
# end def

def searchModules(path, base):
	""" search of modules in a sub folder """
	# et les renvoi dans une liste
	lstMod = []
	pt = "(.+)\\.(py|pyw)$"
	found = os.listdir(path)	
	for f in found:
		# si est un dossier
		if os.path.isdir(path + "\\" + f):
			if base == "": subBase = f
			else: subBase = base + "." + f
			lstMod = lstMod + searchModules(path + "\\" + f, subBase)
		else: # c'est un fichier
			if re.match(pt, f, re.I):
				if base != "": subBase = base + "."
				else: subBase = base
				lstMod.append(subBase + re.sub(pt, "\\1", f, 0, re.I))
			# end if
		# end if
	# end for
	return lstMod
# end def

def searchDeclarations(s, key):
	""" recursive search of declarations """
	lstDeclar = []
	s = "\r\n" + s + "\r\n"
	pt = "([\\r\\n]+|:)[ \\t]*"
	pt += "(" + key + "[ \\t]*\=[^\\r\\n]+|"
	pt += ".+?[ \\t]+as[ \\t]+" + key + "[^\\w\\d_]?[^\\r\\n]*|"
	pt += "from[ \\t]+" + key + "[ \\t]+import[^\\r\\n]+|"
	pt += "from[ \\t]+[^ \\t\\r\\n]+[ \\t]+import.*?[^\\w\\d_]" + key + "[^\\w\\d_]?[^\\r\\n]*|"
	pt += "from[ \\t]+[^ \\t]+import[ \\t]+\*|"
	pt += "import[ \\t]+(" + key + "|.*?[^\\w\\d_]" + key + ")[^\\w\\d_]?[^\\r\\n]*)"
	found = finditer2list(pt, s, re.I)
	# parcours
	for e in found:
		# si ligne d'assignation avec un =
		pt2 = "^([\\r\\n]+|:)[ \\t]*" + key + "[ \\t]*=([a-zA-Z_][a-zA-Z\\d_]*)"
		if re.match(pt2, e.group(0), re.I):
			key2 = finditer2list(pt2, e.group(0), re.I) [0].group(1)
			try: lstDeclar.append(searchDeclarations(s[0: e.start(0)], key2))
			except: pass
		# end if
		lstDeclar.append(e.group(2))
	# end for
	s2 = "\n".join(lstDeclar)
	return s2
# end def

def sayCurBlocName():
	""" say the current main bloc name """
	# dit le nom de la classe ou fonction courante
	name = getCurBlocName()
	if name == "":
		sp.window.messageBeep(0)
	else:
		name = name.replace("/", " de ")
		sayText(name)
	# end if
	page = sp.window.curPage
	# on fait dire le niveau d'indentation
	sayText("Niveau " + str(page.lineIndentLevel(page.curLine)))
	# on fait dire le numéro de la ligne courante
	sayText("Line " + str(page.curLine))
	# on fait dire le nom de l'interpréteur courant
	interpretor = getCurInterpretorName()
	if interpretor != "":
		sayText("Interpréteur courant = " + interpretor)
	# end if
# end def

def sayCurInterpretorName():
	""" say the current interpretor name """
	sayText("Interpréteur courant = " + getCurInterpretorName())
# end def

def sayCurIndentLevel():
	""" say the current indent level """
	page = sp.window.curPage
	sayText("Niveau " + str(page.lineIndentLevel(page.curLine)) +". ")
# end def

def sayText(s, stopSpeech = False):
	""" say text with vocal synthesis if autorized """
	global flagVocalSynthesis
	if flagVocalSynthesis == True: sp.say(s, stopSpeech)
# end def

def navigateDown():
	""" move to the next brotherly bloc of code """
	page = sp.window.curPage
	l = page.curLine
	curLevel = page.lineIndentLevel(page.curLine)
	# regexp à utiliser
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	pt = "^([ \\t]*)(" + pt1 + "|" + pt2 + ")[^\\w\\d_]"
	# parcours à la recherche du bloc frère suivant de même niveau
	n = page.lineCount
	for i in range(l + 1, n):
		line = page.line(i)
		# si ligne d'influence de l'indentation
		if re.match(pt, line):
			# comparaison de niveaux d'indentation
			level = page.lineIndentLevel(i)
			if level == curLevel: # niveaux identiques
				page.position = page.lineSafeStartOffset(i)
				sayText(line)
				sayText("Ligne " + str(i + 1) + ", niveau " + str(level))
				return
			elif level > curLevel:
				continue
			elif level < curLevel:
				sp.window.messageBeep(0)
				return
			# end if
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def navigateUp():
	""" move to the previous brotherly bloc of code """
	page = sp.window.curPage
	l = page.curLine
	curLevel = page.lineIndentLevel(page.curLine)
	# regexp à utiliser
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	pt = "^([ \\t]*)(" + pt1 + "|" + pt2 + ")[^\\w\\d_]"
	# parcours à la recherche du bloc frère précédent de même niveau
	for i in range(l - 1, 0, - 1):
		line = page.line(i)
		# si ligne d'influence de l'indentation
		if re.match(pt, line):
			# comparaison de niveaux d'indentation
			level = page.lineIndentLevel(i)
			if level == curLevel: # niveaux identiques
				page.position = page.lineSafeStartOffset(i)
				sayText(line)
				sayText("Ligne " + str(i + 1) + ", niveau " + str(level))
				return
			elif level > curLevel:
				continue
			elif level < curLevel:
				sp.window.messageBeep(0)
				return
			# end if
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def navigateRight():
	""" move to the first child bloc of code """
	page = sp.window.curPage
	l = page.curLine
	curLevel = page.lineIndentLevel(page.curLine)
	# regexp à utiliser
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	pt = "^([ \\t]*)(" + pt1 + "|" + pt2 + ")[^\\w\\d_]"
	# parcours à la recherche du bloc enfant
	n = page.lineCount
	for i in range(l + 1, n):
		line = page.line(i)
		# si ligne d'influence de l'indentation
		if re.match(pt, line):
			# comparaison de niveaux d'indentation
			level = page.lineIndentLevel(i)
			if level == curLevel + 1:
				page.position = page.lineSafeStartOffset(i)
				sayText(line)
				sayText("Ligne " + str(i + 1) + ", niveau " + str(level))
				return
			else:
				sp.window.messageBeep(0)
				return
			# end if
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def navigateLeft():
	""" move to the parent bloc of code """
	page = sp.window.curPage
	l = page.curLine
	curLevel = page.lineIndentLevel(page.curLine)
	# regexp à utiliser
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	pt = "^([ \\t]*)(" + pt1 + "|" + pt2 + ")[^\\w\\d_]"
	# parcours à la recherche du bloc parent
	for i in range(l - 1, 0, - 1):
		line = page.line(i)
		# si ligne d'influence de l'indentation
		if re.match(pt, line):
			# comparaison de niveaux d'indentation
			level = page.lineIndentLevel(i)
			if level == curLevel - 1:
				page.position = page.lineSafeStartOffset(i)
				sayText(line)
				sayText("Ligne " + str(i + 1) + ", niveau " + str(level))
				return
			elif level >= curLevel:
				continue
			else:
				sp.window.messageBeep(0)
				return
			# end if
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def nextLineWithSameLevel():
	""" move to the next line with same or lower level """
	page = sp.window.curPage
	l = page.curLine
	n = page.lineCount
	curIndent = finditer2list("^[ \\t]*", page.line(l))[0].group(0)
	for i in range(l + 1, n):
		indent = finditer2list("^[ \\t]*", page.line(i))[0].group(0)
		if len(indent) <= len(curIndent):
			page.curLine = i
			sayText(page.line(i))
			sayText("line " + str(i + 1))
			return
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def previousLineWithSameLevel():
	""" move to the previous line with same or lower level """
	page = sp.window.curPage
	l = page.curLine
	curIndent = finditer2list("^[ \\t]*", page.line(l))[0].group(0)
	for i in range(l - 1, 0, - 1):
		indent = finditer2list("^[ \\t]*", page.line(i))[0].group(0)
		if len(indent) <= len(curIndent):
			page.curLine = i
			sayText(page.line(i))
			sayText("line " + str(i + 1))
			return
		# end if
	# end for
	sp.window.messageBeep(0)
# end def

def forPythonUsersHelp():
	""" open the forPython user help file """
	webbrowser.open(os.path.join(getCurScriptFolderPath(), "doc", "readme.html"))
# end def

def forPythonChange():
	""" open the forPython changelog file """
	webbrowser.open(os.path.join(getCurScriptFolderPath(), "doc", "changelog.html"))
# end def

def forPythonSpecifications():
	""" open the forPython specification file """
	webbrowser.open(os.path.join(getCurScriptFolderPath(), "doc", "roadmape.html"))
# end def

def readIndentOnlyWhenChange():
	""" activate or deactivate the reading  of indents if change """
	global menuReadIndentOnlyWhenChange, lastDifferentIndentLevel
	menuReadIndentOnlyWhenChange.checked = not(menuReadIndentOnlyWhenChange.checked)
	if menuReadIndentOnlyWhenChange.checked == True:
		sayLevel()
		sayText("Activation de la lecture du niveau d'indentation si changement")
	else:
		sayNothing()
		sayText("Désactivation de la lecture du niveau d'indentation si changement")
	# end if
	lastDifferentIndentLevel = sp.window.curPage.lineIndentLevel(sp.window.curPage.curLine)
# end def

def showCurDocumentProperties():
	""" display the dialog of current document properties """
	s = ""
	# détermination des nombres de classes et fonctions
	nbClass = 0
	nbFunc = 0
	lst = getBlocsLimits(sp.window.curPage.text)
	for(curLevel, curKey, curName, d, f, e) in lst:
		if curKey == "class": nbClass += 1
		if curKey == "def": nbFunc += 1
	# end for
	s = s + "\r\n" + "Nb de classes = " + str(nbClass)
	s = s + "\r\n" + "Nb de fonctions = " + str(nbFunc)
	# le nombre de lignes
	s = s + "\r\n" + "Nombre de lignes = " + str(sp.window.curPage.lineCount)
	# le nombre de caractères
	s = s + "\r\n" + "Nombre de caractères = " + str(sp.window.curPage.textLength)
	# recherche des infos de formattage du document
	try: mnu = sp.window.menus["format"]
	except: pass
	try:
		lst = [0, 1, 2]
		for i in lst:
			for j in range(mnu[i].length):
				if mnu[i][j].checked == True:
					s = s + "\r\n" + mnu[i].label.replace("&", "") + " = " + mnu[i][j].label
				# end if
			# end for
		# end for
	except: pass
	# l'emplacement du fichier
	s = s + "\r\nEmplacement = " + sp.window.curPage.file
	# affichage
	sp.window.messageBox(s, "Propriétés du document", 0)
# end def

def saveAllPages():
	""" save modifications in all opened pages """
	for p in sp.window.pages:
		p.save()
	# end for
# end def

def testeur():
	""" function to make testings """
	alert(getCurInterpretorName())
	return
	runFile("explorer.exe", os.path.dirname(sp.window.curPage.file))
	return
	alert(str(sp.window.curPage.__getattribute__("okd")))
	return
	alert(getModuleRef(getCurModuleDir()))
	return
	s = sp.window.curPage.text
	lstString = []
	# pattern pour trouver les strings et commentaires
	pt = getStringPattern(1)
	pt = sp.window.prompt("tapez la regexp", "tapez la regexp")
	# recherche
	lstString = finditer2list(pt, s)
	if len(lstString) > 0:
		alert(str(lstString))
	else:
		alert("Aucune chaîne trouvée")
	# end if
# end def

def checkForPythonTools():
	""" vérifie si nécessité d'afficher les outils du forPython """
	global gWayOfActivatingForPython
	# Création si nécessaire du menu Pour l'activation/désactivation du forPython.
	if sp.window.menus.tools["forPythonActivation"] == None:
		sp.window.menus.tools.add(label = "Activer le forPython", action = activeForPythonExtension, name = "forPythonActivation")
	# end if
	# on trouve la manière d'activer le forPython
	gWayOfActivatingForPython = sp.getConfig("WayOfActivatingForPython", "1")
	# définition de l'état de la case d'activation du forPython 
	if (gWayOfActivatingForPython == "1" and isPythonFile()==True) or gWayOfActivatingForPython == "2":
		sp.window.menus.tools["forPythonActivation"].checked = True
	# end if
	
	# Vérification de l'état d'activation du forPython à l'ouverture de 6pad++.
	if sp.window.menus.tools["forPythonActivation"].checked == True:
		loadForPythonTools()
	# end if
	
	# si demande d'ajout de balise de fin de bloc au démarrage
	if sp.getConfig("AddEndTagsAtFileLoading", "0") == "1":
		addTagsInPage()
# end def

def loadForPythonTools():
	""" loading of menus, events and shortcuts related to the forPython """
	global menuForPython, menuView, menuAccessibility, menuModifyAccelerators, menuPythonVersion, menuLineHeadings, menuSelection, menuInsertion, menuDeletion, menuExecution, menuNavigation, menuTags, menuExploration, menuReadIndentOnlyWhenChange, menuPythonHelpFiles
	global idTmrLineMove, flagCheckLine, flagVocalSynthesis
	global g_key1, g_key2
	# Vérification de la pré-existence du menu forPython.
	# il nous sert de repère pour savoir si les aménagement on déja été chargés ou pas.
	# Si c'est le cas, on ne le refait plus.
	if sp.window.menus['forPython'] != None: return
	
	# création et ajout d'éléments au menu fichier
	i = getMenuIndex("save", sp.window.menus["file"]) + 1
	menuSaveAllPages = sp.window.menus["file"].add(label = "Enregistrer tout", name = "saveAllPages", action = saveAllPages, index = i)
	
	# Création et ajout d'élément au menu python/forPython
	menuForPython = sp.window.menus.add(label="Python", action=None, index=-3, submenu=True, name="forPython")
	# les menus d'insertion
	menuInsertion = menuForPython.add(label = "&Insertion", submenu = True, name = "insertion")
	menuInsertion.add(label = "Insérer une &instruction d'en-tête de fichier...", action = insertHeaderStatement, name = "insertHeaderStatement")
	menuInsertion.add(label = "Insérer une instruction &import", action = insertImportStatement, name = "insertImportStatement")
	menuInsertion.add(label = "Insérer une nouvelle &fonction...", action = createNewFunction, name = "createNewFunction", accelerator = "CTRL+E")
	menuInsertion.add(label = "Insérer une nouvelle &classe...", action = createNewClass, name = "createNewClass", accelerator = "CTRL+SHIFT+E")
	menuInsertion.add(label = "Insérer une référence à un fichier", action = insertFileRef, name = "insertFileRef")
	# les menus d'exécution
	menuExecution = menuForPython.add(label = "&Exécution", submenu = True, name = "execution")
	menuExecution.add(label = "&Exécuter le module", action = runAPythonCodeOrModule, name = "runAPythonCodeOrModule", accelerator = "CTRL+F5")
	# éléments de menu supplémentaires au forPython
	menuForPython.add(label = "Créer un exécutable avec py2exe", action = runCompiler, name = "runCompiler")
	menuForPython.add(label = "Définition mot clé", action = curPosHelp, name = "defineKeyWord", accelerator = "CTRL+I")
	menuForPython.add(label = "Complétion de code", action = curPosCompletion, name = "completion", accelerator = "CTRL+J")
	# ajout d'éléments au menu Edition
	menuEdition = sp.window.menus['edit']
	# les menus de sélection de blocs
	i = getMenuIndex("selectAll", menuEdition)
	menuSelection = menuEdition.add(label = "&Sélection de blocks", submenu = True, name = "selection", index = i + 1)
	menuSelection.add(label = "Sélectionner la &fonction courante", action = selectCurrentFunction, name = "selectCurrentFunction", accelerator = "CTRL+R")
	menuSelection.add(label = "Sélectionner la &classe courante", action = selectCurrentClass, name = "selectCurrentClass", accelerator = "CTRL+SHIFT+R")
	# le rechercher avancé
	i = getMenuIndex("find", menuEdition)
	menuEdition.add(label = "Recherche avancée...", action = searchAdvanced, index = i + 1, name = "advancedSearch", accelerator = "CTRL+SHIFT+F")
	# le rechercher et remplacer avancée
	i = getMenuIndex("replace", menuEdition)
	menuEdition.add(label = "Rechercher et remplacer avancé...", action = searchAndReplaceAdvanced, index = i + 1, name = "advancedSearchAndReplace", accelerator = "CTRL+SHIFT+H")
	# les menus de suppressions
	menuDeletion = menuEdition.add(label = "S&uppressions", submenu = True, name = "deletion")
	menuDeletion.add(label = "Ssupprimmer la &classe courante", action = deleteCurrentClass, name = "deleteCurrentClass")
	menuDeletion.add(label = "Supprimer la &fonction courante", action = deleteCurrentFunction, name = "deleteCurrentFunction")
	menuDeletion.add(label = "Supprimer la ligne courante", action = deleteCurrentLine, name = "deleteCurrentLine", accelerator = "CTRL+D")
	# Création et ajout d'éléments au menu affichage
	if sp.window.menus["view"] == None:
		menuView = sp.window.menus.add(label = "&Affichage", action = None, index = 2, submenu = True, name = "view")
	else:
		menuView = sp.window.menus["view"]
	# end if
	# les menus de navigation
	menuNavigation = menuView.add(label = "&Déplacements", submenu = True, name = "navigation")
	menuNavigation.add(label = "Se déplacer vers la classe ou fonction &suivante", action = nextElement, name = "nextElement", accelerator = "F2")
	menuNavigation.add(label = "Se déplacer vers la classe ou fonction &précédente", action = previousElement, name = "previousElement", accelerator = "SHIFT+F2")
	menuNavigation.add(label = "Se déplacer vers la &classe suivante", action = nextClass, name = "nextClass", accelerator = "CTRL+F2")
	menuNavigation.add(label = "Se déplacer vers la classe p&récédente", action = previousClass, name = "previousClass", accelerator = "CTRL+SHIFT+F2")
	menuNavigation.add(label = "Se déplacer à la fin de la classe ou fonction courante", action = goToEndOfElement, name = "goToEnd", accelerator = "ALT+F2")
	menuNavigation.add(label = "Se déplacer à la prochaine ligne de même niveau ou inférieur", action = nextLineWithSameLevel, accelerator = "F9")
	menuNavigation.add(label = "Se déplacer à la précédente ligne de même niveau ou inférieur", action = previousLineWithSameLevel, accelerator = "SHIFT+F9")
	menuNavigation.add(label = "Liste des c&lasses et fonctions", action = selectAClassOrFunction, name = "selectAClassOrFunction", accelerator = "CTRL+L")
	# les menus d'exploration du code
	menuExploration = menuView.add(label = "&Exploration", submenu = True, name = "exploration")
	menuExploration.add(label = "Aller au bloc &parent", action = navigateLeft, name = "navigateLeft")
	menuExploration.add(label = "Aller au premier bloc &enfant", action = navigateRight, name = "navigateRight")
	menuExploration.add(label = "Aller au bloc frère &suivant", action = navigateDown, name = "nextBrother")
	menuExploration.add(label = "Aller au bloc frère précéde&nt", action = navigateUp, name = "previousBrother")
	
	# les menus des balises de fin de bloc
	menuTags = menuView.add(label = "Balisage de code", submenu = True, name = "endBlocTags")
	menuTags.add(label = "Ajouter les balises de fin de block", action = addTagsInPage, name = "addTags")
	menuTags.add(label = "Retirer les balises de fin de bloc", action = removeTagsInPage, name = "removeTags")
	menuTags.add(label = "Ajuster l'indentation aux balises de fin de block", action = AdjustIndentsByTagsInPage, name = "adjustIndent")
	# pour raffraîchir la syntaxe du code
	menuView.add(label = "Raffraîchir le code", action = refreshCodeInPage, name = "refreshCode")
	# pour afficher les propriétés du document
	menuView.add(label = "Propriétés du document...", action = showCurDocumentProperties, name = "showCurDocumentProperties", accelerator = "ALT+F1")
	
	# Ajout d'éléments au menu outils	
	menuTools = sp.window.menus.tools
	# python versions.
	menuPythonVersion = menuTools.add(label = "&Versions de Python installées", submenu = True, name = "pythonVersion")
	menuPythonVersion.add(label = "6&pad++ Python version", action = make_action(0, "6padPythonVersion"), name = "6padPythonVersion")
	# setOptions
	menuTools.add(label = "&Options...", name = "options", action = setOptions, index = -1, accelerator = "CTRL+P")
	# au menu aide
	menuHelp = sp.window.menus.help
	# ajout des menu d'aide au forPython
	menuForPythonHLP = menuHelp.add(label = "Aide de l'extension forPython", submenu = True, name = "forPythonHelp")
	menuForPythonHLP.add(label = "Aide des &utilisateurs", action = forPythonUsersHelp, name = "forPythonUsersHelp")
	menuForPythonHLP.add(label = "Historique des &changements", action = forPythonChange, name = "forPythonChange")
	menuForPythonHLP.add(label = "Cah&ier des charges", action = forPythonSpecifications, name = "forPythonSpecifications")
	# for managing additional menus.
	manageMenus()
	
	addPythonVersionsSubMenus()
	menuPythonVersion[pythonVersionsList.index(curPythonVersion)].checked = True
	
	# Création et ajout d'éléments au menu accessibilité
	if sp.window.menus["accessibility"] == None:
		menuAccessibility = sp.window.menus.add(label = "Access&ibilité", name = "accessibility", action = None, index = -3, submenu = True)
	else:
		menuAccessibility = sp.window.menus["accessibility"]
	# end if
	# l'activation ou non de la synthèse vocale
	mnu = menuAccessibility.add(label = "Activer la synthèse vocale", name = "vocalSynthesis", action = toggleVocalSynthesis)
	mnu.checked = True
	flagVocalSynthesis = mnu.checked
	# les modes de lecture des en-têtes de ligne
	menuLineHeadings = menuAccessibility.add(label = "Lecture des entêtes de &lignes", submenu = True, name = "lineHeadings")
	menuLineHeadings.add(label = "Ne &rien dire", action = sayNothing, name = "nothing")
	menuLineHeadings.add(label = "Dire les nu&méro de lignes", action = sayLineNumber, name = "lineNumber")
	menuLineHeadings.add(label = "Dire les &indentations", action = sayIndentation, name = "indentation")
	menuLineHeadings.add(label = "Dire les num&éros de lignes et les indentations", action = sayLineAndIndentation, name = "lineAndIndentation")
	menuLineHeadings.add(label = "Dire les ni&veaux", action = sayLevel, name = "level")
	menuLineHeadings.add(label = "Dire les numéro de li&gnes et les niveaux", action = sayLineAndLevel, name = "lineAndLevel")
	menuLineHeadings.add(label = "&Basculer le mode de lecture des entêtes de ligne", action = toggleMode, name = "toggleMode", accelerator = "CTRL+SHIFT+L")
	menuLineHeadings.nothing.checked = True
	# lecture du nom du bloc courant
	menuAccessibility.add(label = "Lire le nom du bloc courant", action = sayCurBlocName, name = "sayCurrentBlocName", accelerator = "CTRL+SHIFT+B")
	# lecture du nom de l'interpréteur courant
	menuAccessibility.add(label = "Lire le nom de l'interpréteur courant", action = sayCurInterpretorName, name = "sayCurrentInterpretorName")
	# lecture du niveau d'indentation courant
	menuAccessibility.add(label = "Lire le niveau d'&indentation courant", action = sayCurIndentLevel, name = "sayCurrentIndentLevel")
	# lecture de l'indentation seulement si changement
	menuReadIndentOnlyWhenChange = menuAccessibility.add(label = "Activer la lecture du niveau d'&indentation seulement si changement", accelerator = "CTRL+SHIFT+F1", action = readIndentOnlyWhenChange)
	
	# Ajout d'évènements aux pages ouvertes
	# on conservera la référence de l'évènement en créant un attribut dans chaque instance de la classe page
	for page in sp.window.pages:
		page.__setattr__("okd", page.addEvent("keyDown", onKeyDown))
		page.__setattr__("oku", page.addEvent("keyUp", onKeyUp))
		page.__setattr__("opc", page.addEvent("close", onPageClose))
	# end for
	try:
		# ajout d'un raccourci pour recharger les scripts
		sp.window.addAccelerator("F5", reloadForPythonTools, False)
		# ajout d'un raccourci pour les tests
		sp.window.addAccelerator("SHIFT+F1", testeur, False)
	except: pass
	# Ajout d'évènement à la fenêtre
	po=sp.window.addEvent("pageOpened", openedPage)
	# création du timer de vérification de changement de ligne
	flagCheckLine = True
	if idTmrLineMove == 0: idTmrLineMove = sp.window.setInterval(tmrLineMove, 400)
	# déclenchement de la gestion des raccourcis clavier
	# appel des outils des modules complémentaires
	loadVersioningTools()
	loadPasteTools()
	loadManageProjectTools()
	loadManageShortcutsTools()
	# messages d'accueil
	sayText("Chargement du forPython")
	sayCurInterpretorName()
# end def

def reloadForPythonTools():
	""" rechargement du module forPython """
	# on élimine les outils de forPython
	unloadForPythonTools()
	# on ré-importe manageProject
	# exec("importlib.reload(forPython.manageProject)")
	modRef = sys.modules["forPython.manageProject"]
	importlib.reload(modRef)
	# on ré-importe forPython
	# exec("importlib.reload(forPython.__init__)")
	modRef = sys.modules["forPython.__init__"]
	importlib.reload(modRef)
	# on recharge les outils du forPython
	loadForPythonTools()
	# message de fin
	alert("Le module forPython a été rechargé")
# end def

def unloadForPythonTools():
	""" unloading of menus, events and shortcuts related to the forPython """
	global menuSelection, flagCheckLine
	global g_key1, g_key2
	# Vérification et suppression du menu forPython.
	if sp.window.menus["forPython"] != None: sp.window.menus.remove('forPython')
	# retrait au menu fichier
	if sp.window.menus["file"]["saveAllPages"] != None: sp.window.menus["file"]["saveAllPages"].remove()
	# retrait des menus de sélection
	if menuSelection != None: menuSelection.remove()
	# dans le menu édition
	menuEdition = sp.window.menus.edit
	# Vérification et suppression du menu recherche avancée 
	if menuEdition["advancedSearch"] != None: menuEdition.remove("advancedSearch")
	# Vérification et suppression du menu de recherche et remplacement avancé 
	if menuEdition["advancedSearchAndReplace"] != None: menuEdition.remove("advancedSearchAndReplace")
	# vérification et suppression du menu Affichage.
	if sp.window.menus["view"] != None:
		sp.window.menus.remove("view")
	# Vérification et suppression des éléments du menu outils	
	menuTools = sp.window.menus.tools
	# python versions.
	if menuTools["pythonVersion"] != None:
		menuTools.remove("pythonVersion")
	# modifyAccelerators.
	if menuTools["modifyAccelerators"] != None:
		menuTools.remove("modifyAccelerators")
		# options
		if menuTools["options"] != None: menuTools.remove("options")
	# Vérification et suppression du menu accessibilité.
	if sp.window.menus["accessibility"] != None:
		sp.window.menus.remove("accessibility")
	# Vérification et suppression des items d'aide pour l'extension forPython dans le menu aide.
	menuHelp = sp.window.menus.help
	if menuHelp["forPythonHelp"] != None: menuHelp.remove("forPythonHelp")
	if menuHelp["pythonHelpFiles"] != None: menuHelp.remove("pythonHelpFiles")
	# Suppression des évènements aux pages ouvertes
	# NB: les références aux évènements ont été stockées dans chaque instance de la classe page
	for page in sp.window.pages:
		page.removeEvent("keyDown", page.__getattribute__("okd"))
		page.removeEvent("keyUp", page.__getattribute__("oku"))
		page.removeEvent("close", page.__getattribute__("opc"))
	# end for
	# Suppression d'évènement à la fenêtre
	sp.window.removeEvent("pageOpened", po)
	# arrêt du timer de vérification de changement de ligne
	# sp.window.clearInterval(idTmrLineMove)
	flagCheckLine = False
	# déchargement des outils des modules complémentaires
	unloadVersioningTools()
	unloadPasteTools
	unloadManageProjectTools()
	unloadManageShortcutsTools()
	# élimination de raccourcis/accélérateurs
	try:
		i = sp.window.findAccelerator("F5")
		if i > 0: sp.window.RemoveAccelerator(i)
		i = sp.window.findAccelerator("SHIFT+F1")
		if i > 0: sp.window.RemoveAccelerator(i)
	except: pass
	sayText("Déchargement du forPython")
# end def

# importation des modules complémentaires se trouvant dans le même dossier
modRef = getModuleRef(getCurModuleDir())
if modRef != "":
	# manageProject.py pour gérer les fichier de projet
	try:
		exec("from " + modRef + ".manageProject import loadManageProjectTools")
		exec("from " + modRef + ".manageProject import unloadManageProjectTools")
	except: pass
	# manageShortcuts.py pour gérer les raccourcis clavier de menus
	try:
		exec("from " + modRef + ".manageShortcuts import loadManageShortcutsTools")
		exec("from " + modRef + ".manageShortcuts import unloadManageShortcutsTools")
	except: pass
	# paste.py pour  choisir la façon de coller le texte
	try:
		exec("from " + modRef + ".paste import loadPasteTools")
		exec("from " + modRef + ".paste import unloadPasteTools")
	except: pass
	# versioning.py pour gérer les versions au document courant
	try:
		exec("from " + modRef + ".versioning import loadVersioningTools")
		exec("from " + modRef + ".versioning import unloadVersioningTools")
	except: pass
# end if

# vérification si nécessité d'afficher les outils du forPython
checkForPythonTools()
