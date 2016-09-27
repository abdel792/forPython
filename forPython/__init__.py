# coding:utf-8

# Extension forPython pour le 6pad++
# transformant cet éditeur de texte scriptable en véritable IDE de développement pour le langage python
# réalisé par:
# Abdel
# Yannick Youalé (mailtoloco2011@gmail.com) Cameroun
# Cyrille
# avec les contributions de:
# QuentinC
# Jean-François Collas
# Tous membres de la progliste (une liste de discussion francophone de programmeurs déficients visuels)
# Débuté en janvier 2016

# Importation des modules.
import sixpad as sp
import inspect
import pkgutil
import sys
import traceback
import re
import os
import shlex
import subprocess
import io

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
curPythonVersion = sp.getConfig("curPythonVersion") if sp.getConfig("curPythonVersion") else "6padPythonVersion"
okd = oku = po = 0 # Pour les événements onKeyDown, onKeyUp et pageOpened.
menuForPython = menuView = menuAccessibility = menuModifyAccelerators = menuPythonVersion = menuLineHeadings = menuSelection = menuInsertion = menuDeletion = menuExecution = menuNavigation = menuTags = menuExploration = None # Pour les menus du forPython
idTmrLineMove = 0
iLastLine = 0
sLastLine = ""
flagCheckLineMove = True
curProc = object() # Pour contrôler le processus en cours d'exécution.

# Dictionnaire pour les raccourcis-clavier des menus nécessitant une action callback.
shortcuts = {}
# for activate/deactivate the forPython extension.
shortcuts["forPythonKey"] = sp.getConfig("forPythonKey") if sp.getConfig("forPythonKey") else "CTRL+SHIFT+F3"
	# lineHeadings
shortcuts["toggleMode"] = sp.getConfig("toggleMode") if sp.getConfig("toggleMode")  else "CTRL+F8"
# Selection
shortcuts["selectCurrentFunction"] = sp.getConfig("selectCurrentFunction") if sp.getConfig("selectCurrentFunction") else "CTRL+R"
shortcuts["selectCurrentClass"] = sp.getConfig("selectCurrentClass") if sp.getConfig("selectCurrentClass") else "CTRL+SHIFT+R"
# Insertion
shortcuts["insertHeaderStatement"] = sp.getConfig("insertHeaderStatement") if sp.getConfig("insertHeaderStatement") else "CTRL+I"
shortcuts["createNewFunction"] = sp.getConfig("createNewFunction") if sp.getConfig("createNewFunction") else "CTRL+E"
shortcuts["createNewClass"] = sp.getConfig("createNewClass") if sp.getConfig("createNewClass") else "CTRL+SHIFT+C"
# Deletion
shortcuts["deleteCurrentClass"] = sp.getConfig("deleteCurrentClass") if sp.getConfig("deleteCurrentClass") else "CTRL+SHIFT+D"
shortcuts["deleteCurrentFunction"] = sp.getConfig("deleteCurrentFunction") if sp.getConfig("deleteCurrentFunction") else "CTRL+K"
shortcuts["deleteCurrentLine"] = sp.getConfig("deleteCurrentLine") if sp.getConfig("deleteCurrentLine") else "CTRL+D"
# Navigation
shortcuts["nextElement"] = sp.getConfig("nextElement") if sp.getConfig("nextElement") else "F2"
shortcuts["previousElement"] = sp.getConfig("previousElement") if sp.getConfig("previousElement") else "SHIFT+F2"
shortcuts["nextClass"] = sp.getConfig("nextClass") if sp.getConfig("nextClass") else "CTRL+F2"
shortcuts["previousClass"] = sp.getConfig("previousClass") if sp.getConfig("previousClass") else "CTRL+SHIFT+F2"
shortcuts["selectAClassOrFunction"] = sp.getConfig("selectAClassOrFunction") if sp.getConfig("selectAClassOrFunction") else "CTRL+L"
shortcuts["goToEnd"] = sp.getConfig("goToEnd") if sp.getConfig("goToEnd") else "ALT+F2"
# Modify shortcuts
shortcuts["modifyShortcuts"] = sp.getConfig("modifyShortcuts") if sp.getConfig("modifyShortcuts") else "CTRL+M"
# Running code or module
shortcuts["runAPythonCodeOrModule"] = sp.getConfig("runAPythonCodeOrModule") if sp.getConfig("runAPythonCodeOrModule") else "CTRL+F5"
# To enter a command manually.
if curPythonVersion != "6padPythonVersion":
	shortcuts["enterACommand"] = sp.getConfig("enterACommand") if sp.getConfig("enterACommand") else "CTRL+SHIFT+E"
# for using pip.
if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
	shortcuts["updatePip"] = sp.getConfig("updatePip") if sp.getConfig("updatePip") else "CTRL+SHIFT+P"
	shortcuts["executeAPipCommandFromAList"] = sp.getConfig("executeAPipCommandFromAList") if sp.getConfig("executeAPipCommandFromAList") else "CTRL+F11"
	# for Py2exe in python27.
	if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
		shortcuts["compileScriptWithPy2exeP27"] = sp.getConfig("compileScriptWithPy2exeP27") if sp.getConfig("compileScriptWithPy2exeP27") else "CTRL+F10"
# for installing package with setup script.
if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
	shortcuts["installPackageWithSetup"] = sp.getConfig("installPackageWithSetup") if sp.getConfig("installPackageWithSetup") else "CTRL+F12"
# Exploration
shortcuts["navigateRight"] = sp.getConfig("navigateRight") if sp.getConfig("navigateRight") else "F9"
shortcuts["navigateLeft"] = sp.getConfig("navigateLeft") if sp.getConfig("navigateLeft") else "SHIFT+F9"
shortcuts["nextBrother"] = sp.getConfig("nextBrother") if sp.getConfig("nextBrother") else "F11"
shortcuts["previousBrother"] = sp.getConfig("previousBrother") if sp.getConfig("previousBrother") else "SHIFT+F11"
# Tags
shortcuts["removeTags"] = sp.getConfig("removeTags") if sp.getConfig("removeTags") else "F7"
shortcuts["addTags"] = sp.getConfig("addTags") if sp.getConfig("addTags") else "ALT+F10"
shortcuts["adjustIndent"] = sp.getConfig("adjustIndent") if sp.getConfig("adjustIndent") else "ALT+F12"
# Refresh code
shortcuts["refreshCode"] = sp.getConfig("refreshCode") if sp.getConfig("refreshCode") else "Alt+F12"
# Accessibility
shortcuts["vocalSynthesis"] = sp.getConfig("vocalSynthesis") if sp.getConfig("vocalSynthesis") else "CTRL+F3"
shortcuts["sayCurrentBlocName"] = sp.getConfig("sayCurrentBlocName") if sp.getConfig("sayCurrentBlocName") else "CTRL+SHIFT+B"
shortcuts["sayCurrentIndentLevel"] = sp.getConfig("sayCurrentIndentLevel") if sp.getConfig("sayCurrentIndentLevel") else "CTRL+SHIFT+L"
# Other
shortcuts["defineKeyWord"] = sp.getConfig("defineKeyWord") if sp.getConfig("defineKeyWord") else "CTRL+J"
shortcuts["completion"] = sp.getConfig("completion") if sp.getConfig("completion") else "CTRL+SHIFT+J"
shortcuts["advancedSearch"] = sp.getConfig("advancedSearch") if sp.getConfig("advancedSearch") else "CTRL+SHIFT+H"

def activeForPythonExtension():
	sp.window.menus.tools["forPythonActivation"].checked = not sp.window.menus.tools["forPythonActivation"].checked
	if sp.window.menus.tools["forPythonActivation"].checked:
		sp.setConfig("forPythonActivation", "1")
		loadForPythonTools()
	else:
		sp.setConfig("forPythonActivation", "0")
		unloadForPythonTools()
# Pour l'activation/désactivation du forPython.
sp.window.menus.tools.add(label="Activer le forPython", action = activeForPythonExtension, accelerator = shortcuts["forPythonKey"], name = "forPythonActivation")
# définition de l'état de la case d'activation du forPython par défaut.
sp.window.menus.tools["forPythonActivation"].checked = False if not sp.getConfig("forPythonActivation") or sp.getConfig("forPythonActivation") == "0" else True

def modifyShortcuts():
	# On crée un dictionnaire pour la liste des options disponibles.
	functionsList = {
		"forPythonKey":sp.window.menus.tools.forPythonActivation.label.replace("&", ""),
		"toggleMode":menuLineHeadings.toggleMode.label.replace("&", ""),
		"selectCurrentFunction":menuSelection.selectCurrentFunction.label.replace("&", ""),
		"selectCurrentClass":menuSelection.selectCurrentClass.label.replace("&", ""),
		"insertHeaderStatement":menuInsertion.insertHeaderStatement.label.replace("&", ""),
		"createNewFunction":menuInsertion.createNewFunction.label.replace("&", ""),
		"createNewClass":menuInsertion.createNewClass.label.replace("&", ""),
		"deleteCurrentFunction":menuDeletion.deleteCurrentFunction.label.replace("&", ""),
		"deleteCurrentClass":menuDeletion.deleteCurrentClass.label.replace("&", ""),
		"deleteCurrentLine":menuDeletion.deleteCurrentLine.label.replace("&", ""),
		"nextElement":menuNavigation.nextElement.label.replace("&", ""),
		"previousElement":menuNavigation.previousElement.label.replace("&", ""),
		"nextClass":menuNavigation.nextClass.label.replace("&", ""),
		"previousClass":menuNavigation.previousClass.label.replace("&", ""),
		"goToEnd":menuNavigation.goToEnd.label.replace("&", ""),
		"selectAClassOrFunction":menuNavigation.selectAClassOrFunction.label.replace("&", ""),
		"modifyShortcuts":menuModifyAccelerators.modifyShortcuts.label.replace("&", ""),
		"runAPythonCodeOrModule":menuExecution.runAPythonCodeOrModule.label.replace("&", ""),
		"defineKeyWord":menuForPython.defineKeyWord.label.replace("&", ""),
		"completion":menuForPython.completion.label.replace("&", ""),
		"advancedSearch":sp.window.menus.edit.advancedSearch.label.replace("&", ""),
		"navigateLeft":sp.window.menus.view.exploration.navigateLeft.label.replace("&", ""),
		"navigateRight":sp.window.menus.view.exploration.navigateRight.label.replace("&", ""),
		"nextBrother":sp.window.menus.view.exploration.nextBrother.label.replace("&", ""),
		"previousBrother":sp.window.menus.view.exploration.previousBrother.label.replace("&", ""),
		"removeTags":sp.window.menus.view.endBlocTags.removeTags.label.replace("&", ""),
		"addTags":sp.window.menus.view.endBlocTags.addTags.label.replace("&", ""),
		"adjustIndent":sp.window.menus.view.endBlocTags.adjustIndent.label.replace("&", ""),
		"refreshCode":sp.window.menus.view.refreshCode.label.replace("&", ""),
		"vocalSynthesis":sp.window.menus.accessibility.vocalSynthesis.label.replace("&", ""),
		"sayCurrentBlocName":sp.window.menus.accessibility.sayCurrentBlocName.label.replace("&", ""),
		"sayCurrentIndentLevel":sp.window.menus.accessibility.sayCurrentIndentLevel.label.replace("&", "")
	}
	if curPythonVersion != "6padPythonVersion":
		functionsList["enterACommand"] = menuForPython.enterACommand.label.replace("&", "")
	if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
		functionsList["installPackageWithSetup"] = menuForPython.installPackageWithSetup.label.replace("&", "")
	if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
		functionsList["updatePip"] = menuForPython.pipMenu["updatePip"].label.replace("&", "")
		functionsList["executeAPipCommandFromAList"] = menuForPython.pipMenu["executeAPipCommandFromAList"].label.replace("&", "")
		# On vérifie pour l'ajout de la compilation avec Py2exe pour Python 27.
		if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
			functionsList["compileScriptWithPy2exeP27"] = menuForPython["compileScriptWithPy2exeP27"].label.replace("&", "")
	# On remplit notre liste de choix à partir de nos 2 dictionnaires functionsList et shortcuts.
	choices = [functionsList[k] + ":" + shortcuts[k] for k in shortcuts.keys()]
	# On affiche notre listBox.
	element = sp.window.choice("Sélectionnez une fonction", "Liste des fonctions", choices)
	if element == -1:
		# On a validé sur annulé ou échappe.
		return
	while 1:
		# On affiche un prompt invitant l'utilisateur à saisir son nouveau raccourci.
		prompt = sp.window.prompt("Saisissez votre raccourci pour la commande %s" % choices[element].split(":")[0], "Nouveau raccourci", text = choices[element].split(":")[1])
		if not prompt:
			# On a validé sur annuler.
			return
		# On vérifie si la clé ne serait pas déjà utilisée.
		verify = [x for x in list(shortcuts.values()) if x.lower() == prompt.lower()]
		if len(verify) > 0:
			sp.window.alert("Le raccourci %s est déjà attribué à la commande %s, veuillez choisir un autre raccourci." % (prompt, functionsList[list(shortcuts.keys())[list(shortcuts.values()).index(prompt)]]))
			continue
		else:
			break
	# On met à jour le fichier de configuration.
	sp.setConfig(list(functionsList.keys())[list(functionsList.values()).index(choices[element].split(":")[0])], prompt)
	# On informe l'utilisateur du changement.
	sp.window.alert("C'est bon, votre racourci %s a bien été attribué à la commande %s, vous devrez quitter puis relancer 6pad++ pour que vos changements prennent pleinement effet !" % (prompt, choices[element].split(":")[0]), "Confirmation")

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
	# sp.say(str(vk))
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
	if vk in [33, 34, 38, 40, 547, 548, 550, 552] and not page.selectedText:
		sayText(getLineHeading(page.curLine), True)
		return False
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
	if isPythonFile():
		loadForPythonTools()
	# end if

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

def sayNothing ():
	global mode
	mode = 0
	menuLineHeadings.nothing.checked = True
	menuLineHeadings.lineNumber.checked = False
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayLineNumber ():
	global mode
	mode = 1
	menuLineHeadings.nothing.checked = False
	menuLineHeadings.lineNumber.checked = True
	menuLineHeadings.indentation.checked = False
	menuLineHeadings.lineAndIndentation.checked = False
	menuLineHeadings.level.checked = False
	menuLineHeadings.lineAndLevel.checked = False

def sayIndentation ():
	global mode
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
	# propose une instruction d'en-tête de fichier à insérer
	sFile = os.path.join(getCurScriptFolderPath(), "statements.txt")
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
			shortcuts["enterACommand"] = sp.getConfig("enterACommand") if sp.getConfig("enterACommand") else "CTRL+SHIFT+E"
			menuForPython.add(label = "En&trer une commande manuellement", index = idx, action = enterACommand, name = "enterACommand", accelerator=shortcuts["enterACommand"])
		# On vérifie qu'on est bien avec une version 2 ou supérieure de Python.
		if int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
			if menuForPython.installPackageWithSetup == None:
				shortcuts["installPackageWithSetup"] = sp.getConfig("installPackageWithSetup") if sp.getConfig("installPackageWithSetup") else "CTRL+F12"
				menuForPython.add(label = "Ins&taller un package avec un script setup.py", index = idx, action = installPackageFromSetupScript, name = "installPackageWithSetup", accelerator = shortcuts["installPackageWithSetup"])
		else:
			# La version de Python utilisée est inférieure à la version 2.
			# On supprime donc les menus et clés de dictionnaire dont on aura pas besoin.
			if "updatePip" in shortcuts.keys():
				del shortcuts["updatePip"]
			if "executeAPipCommandFromAList" in shortcuts.keys():
				del shortcuts["executeAPipCommandFromAList"]
			if "compileScriptWithPy2exeP27" in shortcuts.keys():
				del shortcuts["compileScriptWithPy2exeP27"]
			if "installPackageWithSetup" in shortcuts.keys():
				del shortcuts["installPackageWithSetup"]
			menuForPython.remove(name = "installPackageWithSetup")
			menuForPython.remove(name = "compileScriptWithPy2exeP27")
			menuForPython.remove(name = "pipMenu")
		#idx = -3 if menuForPython.enterACommand == None else -4
		# On vérifie si l'on peut ajouter le sous-menu des commandes PIP.
		if os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
			if menuForPython.pipMenu == None:
				shortcuts["updatePip"] = sp.getConfig("updatePip") if sp.getConfig("updatePip") else "CTRL+SHIFT+P"
				shortcuts["executeAPipCommandFromAList"] = sp.getConfig("executeAPipCommandFromAList") if sp.getConfig("executeAPipCommandFromAList") else "CTRL+F11"
				pipMenu = menuForPython.add(label = "Commandes &PIP", index = 7, submenu = True, name = "pipMenu")
				pipMenu.add(label = "Me&ttre à jour pip", action = updatePip, name = "updatePip", accelerator = shortcuts["updatePip"])
				pipMenu.add(label = "E&xécuter une commande PIP à partir d'une liste", action = executeAPipCommandFromAList, name = "executeAPipCommandFromAList", accelerator = shortcuts["executeAPipCommandFromAList"])
			# On vérifie si l'on est avec Python 27 pour l'ajout de la compilation avec Py2exe compatible Python 27.
			if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
				if menuForPython.compileScriptWithPy2exeP27 == None:
					shortcuts["compileScriptWithPy2exeP27"] = sp.getConfig("compileScriptWithPy2exeP27") if sp.getConfig("compileScriptWithPy2exeP27") else "CTRL+F10"
					menuForPython.add(label = "C&ompiler avec Py2exe pour Python 27", index = idx, action = compileScriptWithPy2exeP27, name = "compileScriptWithPy2exeP27", accelerator = shortcuts["compileScriptWithPy2exeP27"])
			else:
				# On tourne avec une version 3 de Python, on supprime la clé de dictionnaire spécifique à la compilation avec Py2exe P27.
				if "compileScriptWithPy2exeP27" in shortcuts.keys():
					del shortcuts["compileScriptWithPy2exeP27"]
				menuForPython.remove(name = "compileScriptWithPy2exeP27")
	else:
		# On utilise le Python embarqué avec 6pad++.
		# On supprime donc les menus et clés de dictionnaire inutiles.
		if "updatePip" in shortcuts.keys():
			del shortcuts["updatePip"]
		if "executeAPipCommandFromAList" in shortcuts.keys():
			del shortcuts["executeAPipCommandFromAList"]
		if "compileScriptWithPy2exeP27" in shortcuts.keys():
			del shortcuts["compileScriptWithPy2exeP27"]
		if "enterACommand" in shortcuts.keys():
			del shortcuts["enterACommand"]
		if "installPackageWithSetup" in shortcuts.keys():
			del shortcuts["installPackageWithSetup"]
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

def writeToFileAndScreen(cmd, logfile):
	# Permet d'exécuter le module encours avec subprocess.Popen, puis de diriger la sortie vers la console, ainsi que vers le fichier logfile.log.
	# Cette fonction ne s'applique que lorsque le curPythonVersion est différent du Python embarqué avec 6pad++.
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

def executeCommand(cmd):
	# On ouvre le fichier de log.
	f = open(os.path.join(sp.appdir, "logfile.log"), "w+")
	# On récupère le retour de writeToFileAndScreen.
	contains=writeToFileAndScreen(cmd, f)
	# On referme le fichier de log.
	f.close()
	# On vérifie s'il y a une erreur.
	if re.match(".+Error", contains, re.S) and re.match(".+File", contains, re.S) and re.match(".+line", contains, re.S):
		# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
		goToLineError(contains)

def addPythonVersionsSubMenus():
	# On initialise l'index des sous-menus qui seront créés dans la boucle.
	i = 0
	# On crée une liste des dossier susceptibles de contenir un répertoire de Python.
	pathsList = []
	# On vérifie si le Python ainsi que la plateforme Windows sont récents.
	# Car Python 35 s'installe dans un répertoire particulier.
	if os.path.isdir(os.path.join(os.environ.get("USERPROFILE"), "Appdata\\Local\\Programs\\python")):
		# On ajoute le chemin à la liste pathsList.
		pathsList.append(os.path.join(os.environ.get("USERPROFILE"), "Appdata\\Local\\Programs\\python"))
	vol="CDEFGHIJ"
	for k in range(len(vol)):
		pathsList.extend (["%s:\\" % vol[k],
		"%s:\\Programs" % vol[k],
		"%s:\\Program Files" % vol[k],
		"%s:\\Program Files (x86)" % vol[k]]
		)
	# On trie notre liste.
	pathsList.sort()
	for p in pathsList:
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

def runAPythonCodeOrModule():
	# Permet d'exécuter le module en cours d'exploration.
	# On crée une variable pour la page courante.
	curPage = sp.window.curPage
	# On affecte une variable path vers le fichier courant.
	path = curPage.file
	# On vérifie si le fichier est bien sauvegardé.
	if not path:
		# On regarde s'il comporte quand même du code.
		if not curPage.text:
			# Il n'y en a pas, on informe l'utilisateur et on sort.
			sp.window.alert("Le module courant n'est pas sauvegardé et il est vide, impossible donc d'exécuter le code", "Aucun contenu à exécuter")
			return
		# Il y a bien du code, on sauvegarde cela dans un module temporaire.
		tmp = os.path.join(sp.appdir, "tmp.py")
		tmpFile = open(tmp, "w")
		# On y insère le contenu de notre fichier non sauvegardé.
		tmpFile.write(curPage.text)
		# On referme ce fichier.
		tmpFile.close()
		#On ouvre ce fichier temporaire et on le définit comme étant le module courant.
		sp.window.open(tmp)
		# On informe l'utilisateur que son nouveau module a bien été sauvegardé et on l'invite à refaire son raccourci pour exécuter son code.
		sp.window.alert("Votre nouveau module a bien été sauvegardé dans le fichier %s, veuillez cliquer sur OK pour refermer cette présente alerte, puis réexécuter votre raccourci %s pour exécuter son code" % (tmp, shortcuts["runAPythonCodeOrModule"]), "Confirmation de sauvegarde")
		return
	else:
		# Le fichier est bien sauvegardé.
		# On regarde s'il comporte quand même du code.
		if not curPage.text:
			# Il n'y en a pas, on informe l'utilisateur et on sort.
			sp.window.alert("Le module courant est vide, impossible donc d'exécuter le code", "Aucun contenu à exécuter")
			return
		# Le module est bien sauvegardé et prêt à l'exécution.
		# On regarde si on tourne avec le Python embarqé avec 6pad++.
		if curPythonVersion== "6padPythonVersion":
			# On pointe vers le fichier courant en lecture.
			curFile = open(path, "r")
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
				execute6padModule(path)
			except:
				# Il y a des erreurs.
				lines = traceback.format_exception(etype = sys.exc_info()[0], value = sys.exc_info()[1], tb = sys.exc_info()[2])
				# On remplit notre variable out en y introduisant le contenu de la sortie standard.
				print (''.join(line for line in lines))
			finally:
				# On restaure la sortie standard sys.stdout.
				sys.stdout = oldOutput
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
		else:
			# On utilise une autre version de Python, indépendante de 6pad++.
			# On crée la ligne de commande qui sera exécutée dans la fonction writeToFileAndScreen, grâce à subprocess.Popen.
			cmd=[curPythonVersion, curPage.file]
			# On exécute notre code.
			executeCommand(cmd)

# xxxxxxxxxx

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
	# renvoi l'expression sous le curseur
	# ainsi que ses positions de début et de fin
	s = sp.window.curPage.text
	if s == "": return "", 0, 0
	# recueillement de la position du curseur
	l = sp.window.curPage.position
	iStart = l
	iEnd = l
	flag = False
	# recherche vers la droite
	expression = ""
	i = l
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
	i = l - 1
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
	lst = getBlocsLimits(s)
	i = sp.window.curPage.curLine
	lst2 = []
	for (curLevel, curKey, curName, d, f, e) in lst:
		if i>=d and i<=f:
			if curKey == "def" or curKey == "class":
				lst2.append(curKey+" "+curName)
			# end if
		# end if
	# end for
	lst2.reverse()
	return "/".join(lst2)
# end def

def getCurClassName(lstBlocsLimits, line):
	# renvoi le nom de la classe à l'emplacement du curseur
	i = len(lstBlocsLimits)
	while(i > 0):
		i = i - 1
		level, key, name, d, f, sLine = lstBlocsLimits[i]
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
# end def-

def getModuleRef(path):
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
		lstPt.append("'{3,5}[\w\W]+?'{3,5}")
		# string avec triples quotes en guillemets
		lstPt.append("\"{3, 5} [ \\w \\W] + ? \"{3,5}")
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
	#  renvoi les positions de tous les triples quotes dans un objet liste
	l = []
	lst = []
	tripleQuote = ""
	flag = True
	polarity = True
	flagBalance = True
	# recherche de toutes les lignes qui ont au moins un triple quotes
	found = finditer2list("([\\r\\n]+)[^\\r\\n]*?('''|\" \"\") [^ \\r \\n] * ", s)
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
			o = - 1
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
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(s)
	# l'unité d'indentation du fichier courant
	iu = getCurIndentUnit()
	# l'unité de retour à la ligne du fichier courant
	rt = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lstLines = s.split(rt)
	# préparation du parcour des blocs recencés
	s = ""
	i = 0
	for(level, key, name, d, f, sLine) in lstBlocsLimits:
		if key == "class":
			# si classe avec héritage
			pt = "class[ \\t]+[\\w\\d_]+[ \\t]*\\([ \\t]*([\\w\\d_\\.]+)[ \\t]*\\)[ \\t]*\\:"
			if re.match(pt, sLine):
				s = s + ("\t" * level.count(iu)) + key + " " + name + "():\n"				
			else: # pas d'héritage à la classe
				s = s + ("\t" * level.count(iu)) + key + " " + name + "():\n"
			# end if
			# sur la ligne suivante, on recherche une éventuelle description documentaire de la classe
			s3 = rt.join(lstLines[d + 1:])
			pt = "^[ \\t]*('''.+?'''|\"\"\.+?\"\"\")"
			if re.match(pt, s3):
				s3 = finditer2list(pt, s3) [0].group(1)
				s = s + ("\t" * level.count(iu)) + "\t" + s3 + "\n"
			# end if			
			# on circonscrit le texte qui contient la classe
			classText = rt.join(lstLines[d: f])
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
			if re.match(pt, rt.join(lstLines[d:]), re.L):
				# on extrait la ligne
				s2 = finditer2list(pt, rt.join(lstLines[d:]), re.L) [0].group(1)
				# retrait de caractères indésirables de la chaîne
				s2 = re.sub("(\\\\[ \\t]*)*[\\r\\n]+", "", s2)
				s = s + ("\t" * level.count(iu)) + s2 + "\n"
			else: # fonction simple
				s = s + ("\t" * level.count(iu)) + key + " " + name + "():\n"
			# end if			
			# on recherche un éventuel commentaire documentaire à la fonction
			s3 = rt.join(lstLines[d: f])
			pt = "^.+?\\)[ \\t]*\\:[ \\t]*(\\#[^\\r\\n]*)*[\\r\\n]+[ \\t]*('''.+?'''|\"\"\".+?\"\"\")"
			if re.match(pt, s3):
				s3 = finditer2list(pt, s3) [0].group(2)
				s = s + ("\t" * level.count(iu)) + "\t" + s3 + "\n"
			# end if			
			# pour toute fonction, on ajoute un return
			s = s + ("\t" * level.count(iu)) + "\treturn 0\n"
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
	lst = []
	inTripleQuote = False
	rt = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lines = s.split(rt)
	# ajout d'une ligne supplémentaire pour marquer la fin
	lines.append("fin")
	n = len(lines)
	for i in range(0, n):
		curLine = lines[i]
		# si ligne vide ou de commentaire
		if re.match("^[ \\t]*\\#[^\\r\\n]*", curLine, re.I) or re.match("^[ \\t]*$", curLine):
			continue
		# end if
		# gestion des triples quotes
		if inTripleQuote == False:
			if curLine.count("'''") > 0 or curLine.count("\"\"\"") > 0:
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
			curLevel = finditer2list(pt, curLine, re.I)[0].group(1)
			curKey = finditer2list(pt, curLine, re.I)[0].group(2)
			curName = finditer2list(pt, curLine, re.I)[0].group(3)
			d = i
			# on recherche la fin de ce bloc
			for j in range(i+1, n):
				line = lines[j]
				# si ligne vide ou de commentaire
				if re.match("^[ \\t]*\\#[^\\r\\n]*", line, re.I) or re.match("^[ \\t]*$", line):
					continue
				# end if
				# gestion des triples quotes
				if inTripleQuote == False:
					if line.count("'''") > 0 or line.count("\"\"\"") > 0:
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
				level = finditer2list("^[ \\t]*", line)[0].group(0)
				# si le niveau est inférieur
				if level <= curLevel:
					f = j-1
					lst.append((curLevel, curKey, curName, d, f, curLine))
					break
				# end if
			# end for
			inTripleQuote = False
			curTripleQuote = ""
		# end if
	# end for
	# retrait de la ligne superflux préalablement ajoutée
	del lines[len(lines)-1]
	# renvoi
	return lst
# end defdef getBlocsLimits2(s):
	# retrouve les lignes de début et fin des blocks principaux def et class
	rt = getCurReturnUnit()
	# Transfert des lignes dans un tableau
	lines = s.split(rt)
	# on va indexer toutes les lignes
	i = -1
	for e in lines:
		i = i+1
		lines[i] = lines[i] + " ## " + str(i)
	# end for
	# reconstitution du texte aux lignes indexées
	s = rt.join(lines)
	# retrait de tous les string
	lstString = removeStringsFromCode(s)
	# élimination des lignes vide ou avec uniquement des string
	pt = "[\\r\\n]+[ \\t]*tag___yyd[a-zA-Z\\d_]+[ \\t]*(tag___yyd[^\\r\\n]+)*"
	s = re.sub(pt, "", s, 0, re.I)
	# on remplace les renvois de code à la ligne par des génériques
	pt = "\\[ \\t]+(tag___yyd[a-zA-Z\\d_]+[\\r\\n]+)"
	s = re.sub(pt, "___renvoi_a__la___ligne\\1", s)
	# retransformation en liste
	lines = s.split(rt)
	# on ajoute une ligne de fin à indentation 0
	lines.append("fin")
	lst = []
	key = ""
	curKey = ""
	curLevel = 0
	d = 0
	f = 0
	pt1 = "^([ \\t]*)(class|def)[ \\t]+([a-zA-Z\\d_]+)"
	# parcours
	i = - 1
	for e in lines:
		i = i + 1
		if re.match(pt1, e):
			if isDirectLine(e) == True: # cas improbable, mais à prendre en compte
				continue
			# end if
			found = finditer2list(pt1, e)
			curIndent = found[0].group(1)
			curLevel = len(curIndent)
			curKey = found[0].group(2)
			curName = found[0].group(3)
			d = i
			# recherche de la fin du block
			for j in range(i + 1, len(lines)):
				sLine = lines[j]
				level = len(findall2list("^[ \\t]*", lines[j]) [0])
				if level <= curLevel:
					# fin du block
					f = j - 1
					lst.append((curLevel, curKey, curName, d, f, e))
					curKey = "" # réinitialisation
					break
				# end if
			# end for
			if curKey != "": lines.append(curIndent + "# end " + curKey)
		# end if
	# end for
	if curKey != "":
		f = j
		lst.append(curLevel, curKey, curName, d, f, e)
	# end if
	return lst
# end def

def getBlocHeader(s):
	# renvoi la ou les premières lignes déclarant un bloc def ou class
	rt = getCurReturnUnit()
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

def getRelatedCode(lstBlocsLimits = None):
	# Restriction et renvoi du code uniquement relatif à la ligne courante
	s = sp.window.curPage.text
	if lstBlocsLimits == None: lstBlocsLimits = getBlocsLimits(s)
	rt = getCurReturnUnit()
	# décomposition des lignes dans une liste
	lines = s.split(rt)
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
				s = s + lines[j] + rt
			# end for
			# 2. on recueille le texte après le bloc enfant
			for j in range(f2 + 1, f + 1):
				s = s + lines[j] + rt
			# end for
		else: # il n'y a pas de bloc enfant
			# on recueille le texte jusqu'à la ligne courante
			for j in range(d, l):
				s = s + lines[j] + rt
			# end for
		# end if
	# end for
	# Elimination des lignes vides
	s = re.sub("(" + rt + "){2,}", rt, s)
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
	return re.sub("[\\r\\n]+[ \\t]*#[ \\t]*end[ \\t]*(class|def|while|for|if|try|with)[^\\r\\n]*", "", s)
# end def

def removeTagsInPage():
	# sur la page courante
	iLine = sp.window.curPage.curLine
	if sp.window.curPage.selectedText != "":
		sp.window.curPage.selectedText = removeTags(sp.window.curPage.selectedText)
	else:
		sp.window.curPage.text = removeTags(sp.window.curPage.text)
	# end if
	sp.window.curPage.curLine = iLine
# end def

def addTags(s = ""):
	# ajoute des balises de fin de block au code en paramètre
	s = removeTags(s) # préalable
	# détermination des type d'indentation et de retour à la ligne
	rt = getCurReturnUnit()
	iu = getCurIndentUnit()
	# recueillement de toutes les lignes non vides
	lines = findall2list("[^\\r\\n]+", s, re.M) 
	lines.append("")
	lines.append("")
	# recueillement de tous les triples quotes
	lstTripleQuote = getTripleQuotePos(s)
	tripleQuote = ""
	lst = []
	# initialisation de variables
	polarity = False
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	# parcours ligne par ligne
	i = 0
	n = len(lines)
	while(i < n):
		e = lines[i]
		# si ligne d'influence de l'indentation pour les lignes suivantes
		pt = "^([ \\t]*)(" + pt1 + ")[^a-zA-Z\\d_]"
		if re.match(pt, e, re.I):
			# recueillement de certaines infos sur cette ligne
			found = finditer2list(pt, e, re.I)
			curIndent = found[0].group(1)
			curLevel = curIndent.count(iu)
			curKey = found[0].group(2)
			# si ligne d'exécution d'instruction après le deux points
			if isDirectLine(e) == True:
				# on va rechercher une éventuelle ligne de relance qui la suivraient directement
				flag = False
				pt = "^([ \\t]*)(" + pt2 + ")[^a-zA-Z\\d_]"
				for k in range(i + 1, n):
					if re.match(pt, lines[k], re.I):
						found2 = finditer2list(pt, lines[k], re.I)
						indent = found2[0].group(1)
						level = indent.count(iu)
						if curLevel != level: break
						if isDirectLine(lines[k]) == False:
							flag = True # ligne d'influence de l'indentation trouvée
							break
						# end if
					else: # ce n'est pas une ligne de relance
						break
					# end if
				# end for
				if flag == False: # pas de ligne de relance trouvée
					i = i + 1
					continue
				# end if
			# end if
			# continuation du traitement de la ligne d'augmentation de l'indentation
			suplement = "" # pour les cas particulier des class et def
			if curKey == "def" or curKey == "class": supplement = rt + curIndent # pour créer des lignes de séparation
			else: supplement = ""
			# recherche de la fin du block pour y positionner la balise
			tripleQuote = ""
			inTripleQuote = False
			for j in range((i + 1), (len(lines))):
				sLine = lines[j]
				if inTripleQuote == True: # des triples guillemets ont été préalablement ouvert
					if sLine.count(tripleQuote) >= 1:
						inTripleQuote = False # fermeture
						tripleQuote = ""
					# end if
					j = j + 1
					continue
				else: # inTripleQuote==False
					# si dans la ligne il y a au moins un triple quote
					if sLine.count("'''") > 0 or sLine.count("\" \"\"") > 0:
						inTripleQuote, polarity, tripleQuote, lst = getTripleQuoteInfos(sLine)
						# si ouverture de triple quote sur la ligne
						if polarity == True:
							# si  la ligne commence immédiatement par un triple quotes
							if re.match("^[ \\t]*(\" \"\" | ''')", sLine):
								j = j + 1
								continue
							# end if
						# end if
					# end if
				# end if
				level = findall2list("^[ \\t]*", lines[j])[0].count(iu)
				if level <= curLevel:
					# il ne faut pas que ce soit une ligne de relance
					# et qu'elle soit de même niveau
					pt = "^([ \\t]*)(" + pt2 + ")[^a-zA-Z\\d_]"
					if re.match(pt, sLine, re.I) and curLevel == level:
						j = j + 1
						continue
					# end if
					# insertion de la ligne commentaire marquant la fin du block
					lines.insert(j, curIndent + "# end " + curKey + supplement)
					curKey = "" # réinitialisation
					n = n + 1
					break
				# end if
			# end for
			if curKey != "":
				lines.append(curIndent + "# end " + curKey + supplement)
			# end if
		# end if
		i = i + 1
	# end while
	# retrait des deux lignes préalablement ajoutées
	del lines[len(lines) - 1]
	del lines[len(lines) - 1]
	s = rt.join(lines)	
	return s
# end def

def addTagsInPage():
	# sur la page courante
	page = sp.window.curPage
	if page.selectedText == "":
		page.text = addTags(page.text)
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
	rt = getCurReturnUnit()
	# repérage du type d'indentation
	iu = getCurIndentUnit()
	lst2 = []
	# ensuite, décomposition des lignes dans une liste
	lines = s.split(rt)
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
	s = rt.join(lines)
	if selection == False:
		sp.window.curPage.text = s
	else:
		# sp.window.curPage.replace(iStart, iEnd, s)
		sp.window.curPage.selectedText = s
	# end if
# end def

def adjustIndentsByTags2(s, selection = False, iStart=0, iEnd=0):
	# ajuste les indentation à partir des balises commentaires de fin de block
	#
	# élimination de toutes les indentations
	s = re.sub("^[ \\t]+", "", s, 0, re.M)
	# reécriture des balises de block pour meilleure conformité
	s = re.sub("^[#]*[ \\t]*end[ \\t]*(" + pt1 + ")", "# end \\1", s, 0, re.I + re.M)
	# décomposition des lignes dans une liste
	rt = getCurReturnUnit()
	iu = getCurIndentUnit()
	lines = s.split(rt)
	# des variables à utiliser
	flagRebounce = False
	lstKey = []
	level = 0
	level = findall2list("^[ \\t]*", s)[0].count(iu)
	inTripleQuote = False
	pt1 = "class|def|if|for|while|try|with"
	pt2 = "elif|else|except|finally"
	tripleQuote = ""
	i = - 1
	n = len(lines)
	# parcours ligne par ligne
	for e in lines:
		i = i + 1
		if inTripleQuote == False:
			if re.match("^[ \\t]*(" + pt1 + ")[^a-zA-Z\\d_]", e, re.I):
				# xxx c'est une ligne d'initialisation d'indentation pour les lignes suivantes
				indent = iu * level
				lines[i] = indent + lines[i]
				if isDirectLine(e) == False:
					level = level + 1
					flagRebounce = False
				else: # c'est une ligne d'exécution directe
					flagRebounce = True
				# end if
			elif re.match("^(" + pt2 + ")[^a-zA-Z\\d_]", e, re.I):
				#  xxx c'est une ligne de relance de l'indentation
				if flagRebounce == False:
					indent = iu * (level - 1)
				else: # flagRebounce==True
					indent = iu * level
				# end if
				lines[i] = indent + lines[i]
				if isDirectLine(e) == False:
					flagRebounce = False
					level = level + 1
				else: # c'est une ligne d'exécution directe
					flagRebounce = True
				# end if
			elif re.match("^[#][ \\t]*end[ \\t]*(" + pt1 + ")", e, re.I):
				# xxx c'est une balise de fin de block
				# vérification que la clée correspond
				key = finditer2list("[#][ \\t]*end[ \\t]*(" + pt1 + ")", e, re.I) [0].group(1)
				if key == lstKey[len(lstKey) - 1]:
					level = level - 1
					indent = iu * level
					lines[i] = indent + lines[i]
					del lstKey[len(lstKey) - 1]
				else: # non correspondance de clées
					if selection == True: i = i + sp.window.curPage.curLine - 1
					sp.window.alert("'end " + key + "' sans '" + key + "' à la ligne " + str(i + 1))
					return
				# end if
				flagRebounce = False
			else: # xxx c'est une ligne quelconque
				indent = iu * level
				lines[i] = indent + lines[i]
				flagRebounce = False
			# end if
		else: # inTripleQuote==True
			i = i
		# end if
	# end for
	s = rt.join(lines)
	sp.window.curPage.text = s
# end def

def AdjustIndentsByTagsInPage():
	# sur la page courante
	page = sp.window.curPage
	iLine = page.curLine
	if len(sp.window.curPage.selectedText) > 0:
		s = page.text
		d = page.lineStartOffset(page.lineOfOffset(page.selectionStart))
		f = page.lineEndOffset(page.lineOfOffset(page.selectionEnd))
		s = s[d: f - 1]
		adjustIndentsByTags(s, True, d, f)
	else:
		adjustIndentsByTags(page.text)
	# end if
	page.position = page.lineSafeStartOffset(page.curLine)
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
	# séparation des opérateurs des autres caractères par  des espaces
	pt = r"[ ]*(\+=|-=|\*=|/=|<=|>=|==|!=|\|=|=|\||\+|-|\*|/|<|>|%)[ ]*"
	s = re.sub(pt, " \\1 ", s)
	# les englobeurs ouvrants doivent être
	# séparés des autres caractères par un espace à gauche
	pt = r"([\(\[\{]+)[ ]*"
	s = re.sub(pt, " \\1", s)
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
	# les espaces trop grands
	pt = r"[ ]{2,}"
	s = re.sub(pt, " ", s)
	# élimination des espaces et tabulations en fin de ligne
	pt = r"([^ \t]+)[ \t]+$"
	s = re.sub(pt, "\\1", s, 0, re.M)
	# élimination des espaces entre les englobants fermants et ouvrants
	pt = "(\\)|\\]|\\}|\\.)[ \\t]+(\\(|\\[|\\{)"
	s = re.sub(pt, "\\1\\2", s)
	# restauration des string à partir des génériques
	i = 0
	for e in lstString:
		i = i + 1
		s = s.replace(tag + str(i) + "_", e.group(0), 1)
	# end for
	return s
# end def

def refreshCodeInPage():
	# ajuste le code dans la page courante
	iLine = sp.window.curPage.curLine
	if sp.window.curPage.selectedText != "":
		sp.window.curPage.selectedText = refreshCode(sp.window.curPage.selectedText)
	else:
		sp.window.curPage.text = refreshCode(sp.window.curPage.text)
	# end if
	sp.window.curPage.curLine = iLine
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
				sayText("erreur")
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
			sp.window.messageBeep(1)
		# end if
	# end if
# end def

def curPosCompletion():
	# simule l'intellicence pour le python à l'emplacement du curseur
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
	# somme-nous à une position d'importation de module ?
	flagModuleOnly = isImportationArea()
	# quelques autres initialisations
	flagPoint = False
	flag6pad = False
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
	# y a-t-il un nom à une classe courante ?
	curClassName = getCurClassName(lstBlocsLimits, sp.window.curPage.curLine)
	# détermination si l'interpréteur choisi est celui du 6pad
	if curPythonVersion == "6padPythonVersion": flag6pad = True
	# identification d'une éventuelle expression sous le curseur
	expression, iStart, iEnd = getCurExpression()
	# xxx s'il n'y a pas de point dans l'expression
	if expression.find(".") <= - 1:
		flagPoint = False
		curKey = expression
		if flagModuleOnly == False:
			# on circonscrit le code relatif à la ligne sous le curseur
			sCode = getRelatedCode(lstBlocsLimits)
			# de ce code, on extrait tous les imports
			lstImports = extractImportsFromCode(sCode)
			# de ce code, on extrait toutes les déclarations de variables
			lstVars = extractVarsFromCode(sCode)
			# du code entier, on extrait les déclarations de classes et fonctions
			# lstClassDef = extractClassDefFromCode(s)
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
					elif re.match("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+([a-zA-Z\\d_\\.]+)", e, re.I): # from x import x
						s2 = finditer2list("^[ \\t]*from[ \\t]+([^ \\t]+)[ \\t]+import[ \\t]+\([a-zA-Z\\d_\\.]+)", e) [0].group(2)
						if s2.find(".") < 0: lst.append(s2)
					# end if
				# end for
			else: # l'interpréteur est une version de python classique
				# pour trouver les mots clés et d'éventuelles sous-fonctions des imports,
				# on va passer par un fichier intermédiaire dont le sample se trouve à la racine du dossier forPython
				if os.path.isfile(getCurModuleDir() + "\\sampleCompletion.txt") == False:
					sp.window.alert("Un fichier sample d'exécution de code intermédiaire est introuvable", "Erreur- fichier manquant")
					return
				# end if
				s2 = readFile(getCurModuleDir() + "\\sampleCompletion.txt")
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
		else: # flagModuleOnly==True
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
		if len(curKey) > 0: iStart = iEnd - (len(curKey) - 1)
		else:
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
			sp.window.messageBeep(1)
			return
		# end if
	# end if
	# on ajoute les listes en attente
	lst = lst + lstVars + lstClassDef + lstModules
	if len(lst) == 0:
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
	# extrait les assignations de variables du texte
	lst = []
	# pour les déclarations uniques sur une ligne
	pt = "[\\r\\n]+[ \\t]*([a-zA-Z][a-zA-Z\\d_]*)[ \\t]*=[^=]"
	found = finditer2list(pt, s, re.I)
	for e in found:
		lst.append(e.group(1))
	# end for
	# pour les déclarations multiples sur une ligne
	pt = "([\\r\\n]+[ \\t]*|[ \\t]*,[ \\t]*)([a-zA-Z][a-zA-Z\\d_]*)([ \\t]*=|[ \\t]*,)"
	found = finditer2list(pt, s, re.I)
	for e in found:
		lst.append(e.group(2))
	# end for
	# lst.sort()
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
	# supprime les doublons dans la liste en paramètre
	# cette liste doit être ordonnée/triée au préalable
	n = len(lst)
	i = n - 1
	while(i > 0):
		if i > 1:
			if lst[i] == lst[i - 2]:
				del lst[i]
				continue
			# end if
		# end if
		if lst[i] == lst[i - 1]: del lst[i]
		i = i - 1
	# end while
	return lst
# end def

def createNewClass():
	# crée une nouvelle classse
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\com.ini"
	pathFrm = getCurModuleDir() + "\\frmCreateClass.hta"
	# infos d'indentation et de retours à la ligne
	rt = getCurReturnUnit()
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
	os.system(pathFrm)
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
	s = "class " + className + "():" + rt
	# si une description à la classe
	if classDescription != "":
		classDescription = classDescription.replace(separator, indent + iu + rt)
		s = s + indent + iu + "'''" + classDescription + "'''" + rt
	# end if
		s = s + indent + iu + rt
	# si des variables globales
	if classGlobals != "":
		lst = classGlobals.split(separator)
		for e in lst:
			if e.count("=") == 0:
				s = s + indent + iu + e + " = 0" + rt
			else:
				s = s + indent + iu + e + rt
			# end if
		# end for
		s = s + indent + iu + rt
	# end if	
	# si fonction d'initialisation
	if funcInitialize == "1":
		s = s + indent + iu + "def __init__(self):" + rt + indent + iu + iu + "a = 0" + rt
		s = s + indent + iu + "# end def" + rt
		s = s + indent + iu + rt
	# end if
	# si fonction de termination
	if funcTerminate == "1":
		s = s + indent + iu + "def __del__(self):" + rt + indent + iu + iu + "a = 0" + rt
		s = s + indent + iu + "# end def" + rt
		s = s + indent + iu + rt
	# end if
	# si des propriétés 
	if classProperties != "":
		lst = classProperties.split(separator)
		for e in lst:
			s = s + indent + iu + "@property" + rt + indent + iu + "def " + e + "(self):" + rt + indent + iu + iu + "return 0" + rt
			s = s + indent + iu + "# end def" + rt
			s = s + indent + iu + "@" + e + ".setter" + rt + indent + iu + "def " + e + "(self, newValue):" + rt + indent + iu + iu + "a = newValue" + rt
			s = s + indent + iu + "# end def" + rt
			s = s + indent + iu + rt
		# end for
	# end if	
	# si des méthodes
	if classMethods != "":
		lst = classMethods.split(separator)
		for e in lst:
			s = s + indent + iu + "def " + e + "(self):" + rt + indent + iu + iu + "a = 0" + rt
			s = s + indent + iu + "# end def" + rt
			s = s + indent + iu + rt
		# end for
		s = s + indent + iu + rt
	# end if	
	# cloture de la classe
	s = s + indent + "# end class" + rt
	# insertion
	sp.window.curPage.insert(sp.window.curPage.lineSafeStartOffset(iLine), s)
	sp.window.curPage.curLine = iLine
# end def

def createNewFunction():
	# crée une nouvelle fonction
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\com.ini"
	pathFrm = getCurModuleDir() + "\\frmCreateFunction.hta"
	# infos d'indentation et de retours à la ligne
	rt = getCurReturnUnit()
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
	os.system(pathFrm)
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
	funcDescription = funcDescription.replace(separator, indent + iu + rt)
	lst = []
	if funcSelf == "1": lst.append("self")
	if funcParams != "": lst = lst + funcParams.split(separator)
	#
	if funcType == "def":
		s = "def " + funcName + "(" + ", ".join(lst) + "):" + rt
		if funcDescription != "": s = s + indent + iu + "''' " + funcDescription + " '''" + rt
		s = s + indent + iu + "a = 0" + rt
		s = s + indent + "# end def" + rt
	elif funcType == "property":
		s = s + indent + "@property" + rt + indent + "def " + funcName + "(self):" + rt
		if funcDescription != "": s = s + indent + iu + "''' " + funcDescription + " '''" + rt
		s = s + indent + iu + "return 0" + rt
		s = s + indent + "# end def" + rt
		s = s + indent + iu + "@" + funcName + ".setter" + rt + indent + "def " + funcName + "(self, newValue):" + rt + indent + iu + "a = newValue" + rt
		s = s + indent + "# end def" + rt
	# end if
	# insertion
	sp.window.curPage.insert(sp.window.curPage.lineSafeStartOffset(iLine), s)
	sp.window.curPage.curLine = iLine
# end def

def isPythonFile(page = None):
	# ""dÃ©termine si la page en paramÃ¨tre contient un fichier python
	if page == None: page = sp.window.curPage
	sFile = page.file
	iLength = len(sFile)
	if sFile[iLength - 3:].lower() == ".py" or sFile[iLength - 4:].lower() == ".pyw":
		return True
	else:
		return False
	# end if
# end def

def isLineCommented(sLine):
	# détermine s'il y a un commentaire commençant sur la ligne
	lst = getStringsPos(sLine)
	if len(lst) == 0: return False
	d, f = lst[len(lst) - 1]
	if sLine[d] == "#": return True
	return False
# end def

def isWithinTripleQuotes(page, pos, lst = None):
	# La position se trouve-t-elle dans des triples quotes ?
	s = page.text
	if lst == None: lst = getTripleQuotePos(s)
	if len(lst) == 0: return False
	for d, f in lst:
		if d <= pos and pos <= f: return True
	# end for
	return False
# end def

def isImportationArea():
	# détermine si on se trouve sur une ligne d'import, à la position d'un mot clé
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

def isModuleExist(moduleName):
	# vérifie si un module existe
	try: 
		__import__(moduleName)
	except ImportError: 
		return False 
	else: 
		return True
	# end try
# end def

def isSyntaxValid(code):
	# vérifie la syntaxe d'un bout de code
	s = "try:\r\n\texec(\" "+code+" \")\r\nexcept SyntaxError:\r\n\traise"
	sp.window.alert(s)
	exec(s)
# end def

def onPageOpened(newPage):
	# Ã  l'ouverture d'une nouvelle page
	if isPythonFile(newPage) == True:
		CreatePythonTools()
	else:
		removePythonTools()
	# end if
	sayText("Nouvelle page ouverte")
# end def

def tmrLineMove():
	# vérificateur de changement de ligne
	global iLastLine
	global sLastLine
	global flagCheckLineMove
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
	# teste la validité d'une ligne
	rt = getCurReturnUnit()
	curLine = page.curLine
	s = page.line(line)
	s2 = s # sauvegarde
	# si ligne vide, alors forcément valide
	if re.match("^[ \\t]*$", s): return True
	# si ligne de commentaire, alors forcément valide
	if re.match("^[ \\t]*\#", s): return True
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
			s = s3 + rt + s
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
	# se rend à la fin du bloc courant
	lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	curLine = sp.window.curPage.curLine
	# recherche du bloc courant et de sa dernière ligne
	line = -1
	for i in range(len(lstBlocsLimits)):
		level, key, name, d, f, sLine = lstBlocsLimits[i]
		if curLine>=d and curLine<=f:
			line = f
		# end if
	# end for
	if line > -1:
		sayText("Fin du bloc")
		sp.window.curPage.curLine = line
	else:
		sp.window.messageBeep(0)
	# end if
# end def

def searchAndReplaceAdvanced():
	# rechercher et remplacer alternatif
	s = ""
	separator = ",,,"
	# les chemins vers les fichiers à utiliser
	pathIni = getCurModuleDir() + "\\com.ini"
	pathFrm = getCurModuleDir() + "\\frmReplace.hta"
	# infos d'indentation et de retours à la ligne
	rt = getCurReturnUnit()
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
		# le respect de la cass
		if lst[5] != "": s = s + "respectCase=" + lst[5] + "\r\n"
		# mot seul uniquement
		if lst[6] != "": s = s + "allWordOnly=" + lst[6] + "\r\n"
	except: pass
	# écriture des paramètres dans le fichier intermédiaire
	writeFile(pathIni, s)
	if expression.count(".") > 0: expression = expression.split(".")[- 1]
	# exécution de la fenêtre HTA
	os.system(pathFrm)
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
		textToReplace = "([^\\w\\d_]+)" + textToReplace + "([^\\w\\d_]+)"
		replaceBy = "\\1" + replaceBy + "\\2"
	# end if
	# selon la zone déterminée
	s = ""
	l = sp.window.curPage.curLine
	lstBlocsLimits = getBlocsLimits(sp.window.curPage.text)
	lines = sp.window.curPage.text.split(rt)
	if searchZone == "1": # le document courant
		s = sp.window.curPage.text
	elif searchZone == "2": # la classe courante
		for(level, key, name, d, f, sLine) in lstBlocsLimits:
			if key == "class":
				if l >= d and l <= f:
					# recueillement des lignes de la classe en question
					s = rt.join(lines[d: f + 1])
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
					s = rt.join(lines[d: f + 1])
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
	# remplacements
	# et décompte du nombre de remplacement dans la foulée
	nb = 0
	if respectCase == "1":
		nb = len(re.findall(textToReplace, s))
		s = re.sub(textToReplace, replaceBy, s)
	else:
		nb = len(re.findall(textToReplace, s, re.IGNORECASE))
		s = re.sub(textToReplace, replaceBy, s, 0, re.IGNORECASE)
	# end if
	# enregistrement des paramètres dans le fichier ini
	sp.setConfig("lastReplacementParams", textToReplace2 + separator + replaceBy2 + separator + searchType + separator + searchDirection + separator + respectCase + separator + allWordOnly)
	# si aucun changement effectué
	if nb == 0:
		sp.window.alert("Aucune occurence du texte recherché n'a été trouvé et remplacée.", "Aucun remplacement effectué")
		return
	else: # des occurences ont été remplacées
		# message d'avertissement et de confirmation
		if sp.window.confirm(str(nb) + " remplacement effectués.\r\nÊtes-vous sûrs de vouloir les conserver ?") == 0: return
		# selon la zone de remplacement, on restore le texte
		if searchZone == "1": # le document courant
			sp.window.curPage.text = s
		elif searchZone == "2": # la classe courante
			sp.window.curPage.replace(sp.window.curPage.lineStartOffset(d), sp.window.curPage.lineEndOffset(f), s)
		elif searchZone == "3": # la fonction courante
			sp.window.curPage.replace(sp.window.curPage.lineStartOffset(d), sp.window.curPage.lineEndOffset(f), s)
		elif searchZone == "4": # le texte sélectionné
			sp.window.curPage.selectedText = s
		# end if
	# end if
# end def

def searchModules(path, base):
	# recherche des modules dans un sous-dossier
	# et les renvoi dans une liste
	lst = []
	pt = "(.+)\\.(py|pyw)$"
	found = os.listdir(path)	
	for f in found:
		# si est un dossier
		if os.path.isdir(path + "\\" + f):
			if base == "": subBase = f
			else: subBase = base + "." + f
			lst = lst + searchModules(path + "\\" + f, subBase)
		else: # c'est un fichier
			if re.match(pt, f, re.I):
				if base != "": subBase = base + "."
				else: subBase = base
				lst.append(subBase + re.sub(pt, "\\1", f, 0, re.I))
			# end if
		# end if
	# end for
	return lst
# end def

def searchDeclarations(code, key):
	# rechercher recurssivement les déclarations
	lst = []
	code = "\r\n" + code + "\r\n"
	pt = "([\\r\\n]+|:)[ \\t]*"
	pt = pt + "(" + key + "[ \\t]*\=[^\\r\\n]+|"
	pt = pt + ".+?[ \\t]+as[ \\t]+" + key + "[^\\w\\d_]?[^\\r\\n]*|"
	pt = pt + "from[ \\t]+" + key + "[ \\t]+import[^\\r\\n]+|"
	pt = pt + "from[ \\t]+[^ \\t\\r\\n]+[ \\t]+import.*?[^\\w\\d_]" + key + "[^\\w\\d_]?[^\\r\\n]*|"
	pt = pt + "from[ \\t]+[^ \\t]+import[ \\t]+\*|"
	pt = pt + "import[ \\t]+(" + key + "|.*?[^\\w\\d_]" + key + ")[^\\w\\d_]?[^\\r\\n]*)"
	found = finditer2list(pt, code, re.I)
	# parcours
	for e in found:
		# si ligne d'assignation avec un =
		pt2 = "^([\\r\\n]+|:)[ \\t]*" + key + "[ \\t]*=([a-zA-Z_][a-zA-Z\\d_]*)"
		if re.match(pt2, e.group(0), re.I):
			key2 = finditer2list(pt2, e.group(0), re.I) [0].group(1)
			try: lst.append(searchDeclarations(code[0: e.start(0)], key2))
			except: pass
		# end if
		lst.append(e.group(2))
	# end for
	s = "\n".join(lst)
	return s
# end def

def sayCurBlocName():
	# dit le nom de la classe courante
	name = getCurBlocName()
	if name == "":
		sp.window.messageBeep(0)
	else:
		name = name.replace("/", " de ")
		sayText(name)
	# end if
# end def

def sayCurIndentLevel():
	# dit le niveau d'indentation courant
	activePage = sp.window.curPage
	sayText("Niveau " + str(activePage.lineIndentLevel(activePage.curLine)) + ". " + activePage.line(activePage.curLine), True)
# end def

def sayText(s, stopSpeech = False):
	# lecture de texte avec contrôle si autorisation
	if flagVocalSynthesis == True: sp.say(s, stopSpeech)
# end def

def navigateDown():
	# recherche du bloc frère suivant
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
	# recherche du bloc frère précédent
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
	# recherche du bloc enfant
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
	# recherche du bloc parent
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

def loadForPythonTools():
	# Chargement des menus, évènements et raccourcis propres à l'extension forPython
	global menuForPython, menuView, menuAccessibility, menuModifyAccelerators, menuPythonVersion, menuLineHeadings, menuSelection, menuInsertion, menuDeletion, menuExecution, menuNavigation, menuTags, menuExploration
	global idTmrLineMove, flagVocalSynthesis
	# Vérification de la pré-existence du menu forPython.
	# il nous sert de repère pour savoir si les aménagement on déja été chargés ou pas.
	# Si c'est le cas, on ne le refait plus.
	if sp.window.menus['forPython'] != None: return
	
	# Création et ajout d'élément au menu python/forPython
	menuForPython = sp.window.menus.add(label="Python", action=None, index=-3, submenu=True, name="forPython")
	# les menus de sélection
	menuSelection = menuForPython.add(label = "&Sélections", submenu = True, name = "selection")
	menuSelection.add(label = "Sélectionner la &classe courante", action = selectCurrentClass, accelerator = shortcuts["selectCurrentClass"], name = "selectCurrentClass")
	menuSelection.add(label = "Sélectionner la &fonction courante", action = selectCurrentFunction, accelerator = shortcuts["selectCurrentFunction"], name = "selectCurrentFunction")
	# les menus d'insertion
	menuInsertion = menuForPython.add(label = "&Insertion", submenu = True, name = "insertion")
	menuInsertion.add(label = "Insérer une &instruction d'en-tête de fichier...", action = insertHeaderStatement, accelerator = shortcuts["insertHeaderStatement"], name = "insertHeaderStatement")
	menuInsertion.add(label = "Insérer une nouvelle &fonction...", accelerator = shortcuts["createNewFunction"], action = createNewFunction, name = "createNewFunction")
	menuInsertion.add(label = "Insérer une nouvelle &classe...", accelerator = shortcuts["createNewClass"], action = createNewClass, name = "createNewClass")
	# les menus de suppressions
	menuDeletion = menuForPython.add(label = "S&uppressions", submenu = True, name = "deletion")
	menuDeletion.add(label = "Ssupprimmer la &classe courante", action = deleteCurrentClass, accelerator = shortcuts["deleteCurrentClass"], name = "deleteCurrentClass")
	menuDeletion.add(label = "Supprimer la &fonction courante", action = deleteCurrentFunction, accelerator = shortcuts["deleteCurrentFunction"], name = "deleteCurrentFunction")
	menuDeletion.add(label = "Supprimer la ligne courante", action = deleteCurrentLine, accelerator = shortcuts["deleteCurrentLine"], name = "deleteCurrentLine")
	# les menus d'exécution
	menuExecution = menuForPython.add(label = "&Exécution", submenu = True, name = "execution")
	menuExecution.add(label = "&Exécuter du code python ou un module", action = runAPythonCodeOrModule, name = "runAPythonCodeOrModule", accelerator = shortcuts["runAPythonCodeOrModule"])
	# éléments de menu supplémentaires
	menuForPython.add(label = "Définition mot clé", accelerator = shortcuts["defineKeyWord"], action = curPosHelp, name = "defineKeyWord")
	menuForPython.add(label = "Complétion de code", accelerator = shortcuts["completion"], action = curPosCompletion, name="completion")
	
	# ajout d'éléments au menu Edition
	menuEdition = sp.window.menus['edit']
	menuEdition.add(label = "Rechercher et remplacer avancé...", action = searchAndReplaceAdvanced, index = -1, accelerator = shortcuts["advancedSearch"], name = "advancedSearch")
	
	# Création et ajout d'éléments au menu affichage
	if sp.window.menus["view"] == None:
		menuView = sp.window.menus.add(label = "&Affichage", action = None, index = 2, submenu = True, name = "view")
	else:
		menuView = sp.window.menus["view"]
	# end if
	# les menus de navigation
	menuNavigation = menuView.add(label = "&Navigation", submenu = True, name = "navigation")
	menuNavigation.add(label = "Se déplacer vers l'élément &suivant", action = nextElement, accelerator = shortcuts["nextElement"], name = "nextElement")
	menuNavigation.add(label = "Se déplacer vers l'élément &précédent", action = previousElement, accelerator = shortcuts["previousElement"], name = "previousElement")
	menuNavigation.add(label = "Se déplacer vers la &classe suivante", action = nextClass, accelerator = shortcuts["nextClass"], name = "nextClass")
	menuNavigation.add(label = "Se déplacer vers la classe p&récédente", action = previousClass, accelerator = shortcuts["previousClass"], name = "previousClass")
	menuNavigation.add(label = "Se déplacer à la fin de l'élément courant", accelerator = shortcuts["goToEnd"], action = goToEndOfElement, name = "goToEnd")
	menuNavigation.add(label = "Liste des c&lasses et fonctions", action = selectAClassOrFunction, accelerator = shortcuts["selectAClassOrFunction"], name = "selectAClassOrFunction")
	# les menus d'exploration du code
	menuExploration = menuView.add(label = "&Exploration", submenu = True, name = "exploration")
	menuExploration.add(label = "Aller au bloc &parent", action = navigateLeft, accelerator = shortcuts["navigateLeft"], name = "navigateLeft")
	menuExploration.add(label = "Aller au premier bloc &enfant", action = navigateRight, accelerator = shortcuts["navigateRight"], name = "navigateRight")
	menuExploration.add(label = "Aller au bloc frère &suivant", action = navigateDown, accelerator = shortcuts["nextBrother"], name = "nextBrother")
	menuExploration.add(label = "Aller au bloc frère précéde&nt", action = navigateUp, accelerator = shortcuts["previousBrother"], name = "previousBrother")
	
	# les menus des balises de fin de bloc
	menuTags = menuView.add(label = "Balises de fin de bloc", submenu = True, name = "endBlocTags")
	menuTags.add(label = "Retirer les balises de fin de bloc", action = removeTagsInPage, accelerator = shortcuts["removeTags"], name = "removeTags")
	menuTags.add(label = "Ajouter/raffraîchir les balises de fin de block", action = addTagsInPage, accelerator = shortcuts["addTags"], name = "addTags")
	menuTags.add(label = "Ajuster l'indentation aux balises de fin de block", action = AdjustIndentsByTagsInPage, accelerator = shortcuts["adjustIndent"], name = "adjustIndent")
	# pour raffraîchir le code
	menuView.add(label = "Raffraîchir le code", action = refreshCodeInPage, accelerator = shortcuts["refreshCode"], name = "refreshCode")
	
	# Ajout d'éléments au menu outils	
	menuTools = sp.window.menus.tools
	# python versions.
	menuPythonVersion = menuTools.add(label = "&Versions de Python installées", submenu = True, name = "pythonVersion")
	menuPythonVersion.add(label = "6&pad++ Python version", action = make_action(0, "6padPythonVersion"), name = "6padPythonVersion")
	# for managing additional menus.
	manageMenus()
	# Modify shortcuts
	menuModifyAccelerators = menuTools.add(label = "&Raccourcis claviers", submenu = True, name = "modifyAccelerators")
	menuModifyAccelerators.add(label = "Modifier les ra&ccourcis-clavier des commandes", action = modifyShortcuts, accelerator = shortcuts["modifyShortcuts"], name = "modifyShortcuts")
#	
	addPythonVersionsSubMenus()
	menuPythonVersion[pythonVersionsList.index(curPythonVersion)].checked = True
	
	# Création et ajout d'éléments au menu accessibilité
	if sp.window.menus["accessibility"] == None:
		menuAccessibility = sp.window.menus.add(label = "Accessibilité", name = "accessibility", action = None, index = - 3, submenu = True)
	else:
		menuAccessibility = sp.window.menus["accessibility"]
	# end if
	# l'activation ou non de la synthèse vocale
	mnu = menuAccessibility.add(label = "Synthèse vocale", name = "vocalSynthesis", accelerator = shortcuts["vocalSynthesis"], action = toggleVocalSynthesis)
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
	menuLineHeadings.add(label = "&Basculer le mode de lecture des entêtes de ligne", action = toggleMode, accelerator = shortcuts["toggleMode"], name = "toggleMode")
	menuLineHeadings.nothing.checked = True
	# lecture du nom du bloc courant
	menuAccessibility.add(label = "Lecture du nom du bloc courant", accelerator = shortcuts["sayCurrentBlocName"], action = sayCurBlocName, name = "sayCurrentBlocName")
	# lecture du niveau d'indentation courant
	menuAccessibility.add(label = "Lecture du niveau d'&indentation courant", accelerator = shortcuts["sayCurrentIndentLevel"], action = sayCurIndentLevel, name = "sayCurrentIndentLevel")
	
	# Ajout d'évènements
	okd=sp.window.curPage.addEvent("keyDown", onKeyDown)
	oku=sp.window.curPage.addEvent("keyUp", onKeyUp)
	po=sp.window.addEvent("pageOpened", openedPage)
	# création du timer de vérification de changement de ligne
	idTmrLineMove = sp.window.setInterval(tmrLineMove, 400)
# end def


def unloadForPythonTools():
	# déchargement des menus, évènements et raccourcis propres à l'extension forPython
	# Vérification et suppression du menu forPython.
	if sp.window.menus["forPython"] != None:
		sp.window.menus.remove('forPython')
	# Vérification de l'item de recherche avancée dans le menu édition:
	menuEdit = sp.window.menus.edit
	if menuEdit["advancedSearch"] != None:
		menuEdit.remove("advancedSearch")
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
	# Vérification et suppression du menu accessibilité.
	if sp.window.menus["accessibility"] != None:
		sp.window.menus.remove("accessibility")
	# Suppression des évènements
	sp.window.curPage.removeEvent("keyDown", okd)
	sp.window.curPage.removeEvent("keyUp", oku)
	sp.window.removeEvent("pageOpened", po)
	# suppression du timer de vérification de changement de ligne
	sp.window.clearInterval(idTmrLineMove)
# end def
# Vérification de l'état d'activation du forPython à l'ouverture de 6pad++.
if sp.window.menus.tools["forPythonActivation"].checked:
	loadForPythonTools()
else:
	unloadForPythonTools()