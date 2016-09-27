# coding:utf-8

# Importation des modules.
import sixpad as sp
import inspect
import traceback
import re
import os
import subprocess
import io

# Dictionnaire pour les regexps.
regexp={
	"regClsPython":"^[ \t]*class.*?:.*",
	"regFuncPython":"^[ \t]*def.*?:.*",
	"regClsAndFuncPython":"^[ \t]*((?:class|def).*?:.*$)"
	}

# Liste pour les versions de Python.
pythonVersionsList = ["6padPythonVersion"]

# Variables globales.
mode = 0
curPythonVersion = sp.getConfig("curPythonVersion") if sp.getConfig("curPythonVersion") else "6padPythonVersion"

# Dictionnaire pour les raccourcis-clavier des menus nécessitant une action callback.
shortcuts = {}
	# lineHeadings
shortcuts["toggleMode"] = sp.getConfig("toggleMode") if sp.getConfig("toggleMode")  else "CTRL+F8"
# Selection
shortcuts["selectCurrentFunction"] = sp.getConfig("selectCurrentFunction") if sp.getConfig("selectCurrentFunction") else "CTRL+R"
shortcuts["selectCurrentClass"] = sp.getConfig("selectCurrentClass") if sp.getConfig("selectCurrentClass") else "CTRL+SHIFT+R"
# Insertion
shortcuts["insertHeaderStatement"] = sp.getConfig("insertHeaderStatement") if sp.getConfig("insertHeaderStatement") else "CTRL+I"
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
# Modify shortcuts
shortcuts["modifyShortcuts"] = sp.getConfig("modifyShortcuts") if sp.getConfig("modifyShortcuts") else "CTRL+M"
# Running code or module
shortcuts["runAPythonCodeOrModule"] = sp.getConfig("runAPythonCodeOrModule") if sp.getConfig("runAPythonCodeOrModule") else "CTRL+F5"
# for using pip.
if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
	shortcuts["updatePip"] = sp.getConfig("updatePip") if sp.getConfig("updatePip") else "CTRL+SHIFT+P"
	shortcuts["executeAPipCommand"] = sp.getConfig("executeAPipCommand") if sp.getConfig("executeAPipCommand") else "CTRL+F11"
	# for Py2exe in python27.
	if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
		shortcuts["compileScriptWithPy2exeP27"] = sp.getConfig("compileScriptWithPy2exeP27") if sp.getConfig("compileScriptWithPy2exeP27") else "CTRL+F10"
# for installing package with setup script.
if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
	shortcuts["installPackageWithSetup"] = sp.getConfig("installPackageWithSetup") if sp.getConfig("installPackageWithSetup") else "CTRL+F12"

def modifyShortcuts():
	# On crée un dictionnaire pour la liste des options disponibles.
	functionsList = {
		"toggleMode":lineHeadings.toggleMode.label.replace("&", ""),
		"selectCurrentFunction":selection.selectCurrentFunction.label.replace("&", ""),
		"selectCurrentClass":selection.selectCurrentClass.label.replace("&", ""),
		"insertHeaderStatement":insertion.insertHeaderStatement.label.replace("&", ""),
		"deleteCurrentFunction":deletion.deleteCurrentFunction.label.replace("&", ""),
		"deleteCurrentClass":deletion.deleteCurrentClass.label.replace("&", ""),
		"deleteCurrentLine":deletion.deleteCurrentLine.label.replace("&", ""),
		"nextElement":navigation.nextElement.label.replace("&", ""),
		"previousElement":navigation.previousElement.label.replace("&", ""),
		"nextClass":navigation.nextClass.label.replace("&", ""),
		"previousClass":navigation.previousClass.label.replace("&", ""),
		"selectAClassOrFunction":navigation.selectAClassOrFunction.label.replace("&", ""),
		"modifyShortcuts":modifyAccelerators.modifyShortcuts.label.replace("&", ""),
		"runAPythonCodeOrModule":menuForPython.runAPythonCodeOrModule.label.replace("&", "")
	}
	if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
		functionsList["installPackageWithSetup"] = menuForPython.installPackageWithSetup.label.replace("&", "")
	if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
		functionsList["updatePip"] = menuForPython.pipMenu["updatePip"].label.replace("&", "")
		functionsList["executeAPipCommand"] = menuForPython.pipMenu["executeAPipCommand"].label.replace("&", "")
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
	# On affiche un prompt rappelant le choix fait par l'utilisateur.
	prompt = sp.window.prompt("Saisissez votre raccourci pour la commande %s" % choices[element].split(":")[0], "Nouveau raccourci", text = choices[element].split(":")[1])
	if not prompt:
		# On a validé sur annuler.
		return
	# On met à jour le fichier de configuration.
	sp.setConfig(list(functionsList.keys())[list(functionsList.values()).index(choices[element].split(":")[0])], prompt)
	# On informe l'utilisateur du changement.
	sp.window.alert("C'est bon, votre racourci %s a bien été attribué à la commande %s, vous devrez quitter puis relancer 6pad++ pour que vos changements prennent pleinement effet !" % (prompt, choices[element].split(":")[0]), "Confirmation")

def toggleMode():
	if mode == 0:
		sayLineNumber()
		sp.say("Dire les numéros de lignes", True)
	elif mode == 1:
		sayIndentation()
		sp.say("Dire les indentations", True)
	elif mode == 2:
		sayLineAndIndentation()
		sp.say("Dire les numéros de lignes et les indentations", True)
	elif mode == 3:
		sayLevel()
		sp.say("Dire les niveaux", True)
	elif mode == 4:
		sayLineAndLevel()
		sp.say("Dire les numéros de lignes et les niveaux", True)
	elif mode == 5:
		sayNothing()
		sp.say("Ne rien dire", True)

def onKeyUp(activePage, vk):
	# Pour les touches tab et Shift + Tab.
	if vk in [9, 1033] and activePage.position == activePage.lineSafeStartOffset(activePage.curLine) and not activePage.selectedText:
		sp.say("Niveau " + str(activePage.lineIndentLevel(activePage.curLine)) + ". " + activePage.line(activePage.curLine), True)
		return False
	# Pour la touche BackSpace.
	if vk == 8 and not activePage.selectedText and activePage.position == activePage.lineSafeStartOffset(activePage.curLine):
		# Si les paramètres d'indentation sont de 1 Tab ou de 1 espace, on donne le niveau.
		if activePage.indentation in [0, 1]:
			sp.say("Niveau " + str(activePage.lineIndentLevel(activePage.curLine)) + ". " + activePage.line(activePage.curLine), True)
		else:
			# Le niveau d'indentation est fixé sur plus d'une espace, on donne donc le nombre d'indentations.
			sp.say(getIndentation() + ". " + activePage.line(activePage.curLine), True)
		return False
	# Si la touche est FLH, FLB, CTRL+Home, CTRL+End, PGUp, PGDown, CTRL+Up, CTRL+Down.
	# On donne les informations selon le mode de lecture d'entêtes utilisé.
	if vk in [33, 34, 38, 40, 547, 548, 550, 552] and not activePage.selectedText:
		sp.say(getLineHeading(activePage.curLine), True)
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
sp.window.curPage.addEvent("keyUp", onKeyUp)

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
	newPage.addEvent("keyUp", onKeyUp)
sp.window.addEvent("pageOpened", openedPage)

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
	sp.say(getLineHeading(sp.window.curPage.curLine), True)

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
	sp.say(getLineHeading(sp.window.curPage.curLine), True)
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
	sp.say(getLineHeading(sp.window.curPage.curLine), True)

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
	sp.say(getLineHeading(sp.window.curPage.curLine), True)

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
		sp.say("Aucune fonction à sélectionner !", True)
		return
	text = sp.window.curPage.text
	if selectionFunction():
		sp.say("Fonction %s sélectionnée !" % (funcName), True)
		sp.window.curPage.text = text
	else:
		sp.say("Impossible de sélectionner la fonction %s" % (funcName), True)

def selectCurrentClass():
	className = getClassName()
	if not className:
		sp.say("Aucune classe à sélectionner !", True)
		return
	text = sp.window.curPage.text
	if selectionClass():
		sp.say("Classe %s sélectionnée !" % (className), True)
		sp.window.curPage.text = text
	else:
		sp.say("Impossible de sélectionner la classe %s" % (className), True)

def deleteCurrentFunction():
	funcName = getFunctionName()
	if not funcName:
		sp.say("Il n'y a pas de fonction à supprimer", True)
		return
	confirmation = sp.window.confirm("Êtes vous sur de vouloir supprimer la fonction %s?" % (funcName), "Confirmation de suppression")
	if confirmation == 0:
		return
	if selectionFunction():
		sp.window.curPage.text = sp.window.curPage.text.replace(sp.window.curPage.selectedText, "")
		sp.window.curPage.save()
	else:
		sp.say("Impossible de supprimer la fonction %s" % (funcName), True)

def deleteCurrentClass():
	className = getClassName()
	if not className:
		sp.say("Il n'y a pas de classe à supprimer", True)
		return
	confirmation = sp.window.confirm("Êtes vous sur de vouloir supprimer la classe %s?" % (className), "Confirmation de suppression")
	if confirmation == 0:
		return
	if selectionClass():
		sp.window.curPage.text = sp.window.curPage.text.replace(sp.window.curPage.selectedText, "")
		sp.window.curPage.save()
	else:
		sp.say("Impossible de supprimer la classe %s" % (className), True)

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
		sp.say(getLineHeading(lineNumber), True)
	else:
		sp.say("Aucune classe ou fonction trouvée !", True)

def sayNothing ():
	global mode
	mode = 0
	lineHeadings.nothing.checked = True
	lineHeadings.lineNumber.checked = False
	lineHeadings.indentation.checked = False
	lineHeadings.lineAndIndentation.checked = False
	lineHeadings.level.checked = False
	lineHeadings.lineAndLevel.checked = False

def sayLineNumber ():
	global mode
	mode = 1
	lineHeadings.nothing.checked = False
	lineHeadings.lineNumber.checked = True
	lineHeadings.indentation.checked = False
	lineHeadings.lineAndIndentation.checked = False
	lineHeadings.level.checked = False
	lineHeadings.lineAndLevel.checked = False

def sayIndentation ():
	global mode
	mode = 2
	lineHeadings.nothing.checked = False
	lineHeadings.lineNumber.checked = False
	lineHeadings.indentation.checked = True
	lineHeadings.lineAndIndentation.checked = False
	lineHeadings.level.checked = False
	lineHeadings.lineAndLevel.checked = False
def sayLineAndIndentation ():
	global mode
	mode = 3
	lineHeadings.nothing.checked = False
	lineHeadings.lineNumber.checked = False
	lineHeadings.indentation.checked = False
	lineHeadings.lineAndIndentation.checked = True
	lineHeadings.level.checked = False
	lineHeadings.lineAndLevel.checked = False


def sayLevel ():
	global mode
	mode = 4
	lineHeadings.nothing.checked = False
	lineHeadings.lineNumber.checked = False
	lineHeadings.indentation.checked = False
	lineHeadings.lineAndIndentation.checked = False
	lineHeadings.level.checked = True
	lineHeadings.lineAndLevel.checked = False
def sayLineAndLevel ():
	global mode
	mode = 5
	lineHeadings.nothing.checked = False
	lineHeadings.lineNumber.checked = False
	lineHeadings.indentation.checked = False
	lineHeadings.lineAndIndentation.checked = False
	lineHeadings.level.checked = False
	lineHeadings.lineAndLevel.checked = True

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
	sp.say("Suppression de ligne", True)
	# lecture de la nouvelle ligne courante
	sp.say(sp.window.curPage.line(sp.window.curPage.curLine))
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

def make_action(i, f, exFile=None):
	def action():
		global curPythonVersion
		menuName = f
		curPythonVersion = "6padPythonVersion" if not exFile else exFile
		for x in range(pythonVersion.length):
			if x != i:
				pythonVersion[x].checked = False
			else:
				pythonVersion[x].checked = True
		sp.setConfig("curPythonVersion", curPythonVersion)
		sp.window.alert("C'est bon, %s a bien été activé !" % (curPythonVersion), "Confirmation")
		# On vérifie la condition pour ajouter un sous-menu permettant d'installer un package avec un script setup.
		if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
			if menuForPython.installPackageWithSetup == None:
				shortcuts["installPackageWithSetup"] = sp.getConfig("installPackageWithSetup") if sp.getConfig("installPackageWithSetup") else "CTRL+F12"
				installPackage = menuForPython.add(label = "Ins&taller un package avec un script setup.py", action = installPackageFromSetupScript, name = "installPackageWithSetup", accelerator = shortcuts["installPackageWithSetup"])
		else:
			if "installPackageWithSetup" in shortcuts.keys():
				del shortcuts["installPackageWithSetup"]
			menuForPython.remove(name = "installPackageWithSetup")
		# On vérifie la présence du sous-menu permettant de mettre à jour pip.
		if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
			if menuForPython.pipMenu == None:
				shortcuts["updatePip"] = sp.getConfig("updatePip") if sp.getConfig("updatePip") else "CTRL+SHIFT+P"
				shortcuts["executeAPipCommand"] = sp.getConfig("executeAPipCommand") if sp.getConfig("executeAPipCommand") else "CTRL+F11"
				pipMenu = menuForPython.add(label = "Commandes &PIP", index = -2, submenu = True, name = "pipMenu")
				pipMenu.add(label = "Me&ttre à jour pip", action = updatePip, name = "updatePip", accelerator = shortcuts["updatePip"])
				pipMenu.add(label = "E&xécuter une commande PIP", action = executeAPipCommand, name = "executeAPipCommand", accelerator = shortcuts["executeAPipCommand"])
			# On vérifie si l'on est avec Python 27 pour l'ajout de la compilation avec Py2exe compatible Python 27.
			if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
				if menuForPython.compileScriptWithPy2exeP27 == None:
					shortcuts["compileScriptWithPy2exeP27"] = sp.getConfig("compileScriptWithPy2exeP27") if sp.getConfig("compileScriptWithPy2exeP27") else "CTRL+F10"
					menuForPython.add(label = "C&ompiler avec Py2exe pour Python 27", action = compileScriptWithPy2exeP27, index = -2, name = "compileScriptWithPy2exeP27", accelerator = shortcuts["compileScriptWithPy2exeP27"])
			if int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 2:
				# On tourne avec une version 3 de Python, on supprime la clé de dictionnaire spécifique à la compilation avec Py2exe P27.
				if "compileScriptWithPy2exeP27" in shortcuts.keys():
					del shortcuts["compileScriptWithPy2exeP27"]
		else:
			if "updatePip" in shortcuts.keys():
				del shortcuts["updatePip"]
			if "executeAPipCommand" in shortcuts.keys():
				del shortcuts["executeAPipCommand"]
			if "compileScriptWithPy2exeP27" in shortcuts.keys():
				del shortcuts["compileScriptWithPy2exeP27"]
			menuForPython.remove(name = "compileScriptWithPy2exeP27")
			menuForPython.remove(name = "pipMenu")
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
def executeAPipCommand():
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
			if not os.path.exists(os.path.join(curPythonVersion, "lib", "site-packages", "py2exe")):
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
	if re.match(".+error", contains, re.I|re.S) and re.match(".+file", contains, re.I|re.S) and re.match(".+line", contains, re.I|re.S):
		# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
		goToLineError(contains)

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
			if re.match(".+error", contains, re.I|re.S) and re.match(".+file", contains, re.I|re.S) and re.match(".+line", contains, re.I|re.S):
				# On affiche une alerte, invitant l'utilisateur à atteindre directement la ligne concernée.
				goToLineError(contains)
		else:
			# On utilise une autre version de Python, indépendante de 6pad++.
			# On crée la ligne de commande qui sera exécutée dans la fonction writeToFileAndScreen, grâce à subprocess.Popen.
			cmd=[curPythonVersion, curPage.file]
			# On exécute notre code.
			executeCommand(cmd)

# menus

toolsMenu = sp.window.menus.tools
menuForPython = toolsMenu.add(label = "for &Python", submenu = True, name = "forPython")

# en-têtes de ligne

lineHeadings = menuForPython.add(label = "Lecture des entêtes de &lignes", submenu = True, name = "lineHeadings")
lineHeadings.add(label = "Ne &rien dire", action = sayNothing, name = "nothing")
lineHeadings.add(label = "Dire les nu&méro de lignes", action = sayLineNumber, name = "lineNumber")
lineHeadings.add(label = "Dire les &indentations", action = sayIndentation, name = "indentation")
lineHeadings.add(label = "Dire les num&éros de lignes et les indentations", action = sayLineAndIndentation, name = "lineAndIndentation")
lineHeadings.add(label = "Dire les ni&veaux", action = sayLevel, name = "level")
lineHeadings.add(label = "Dire les numéro de li&gnes et les niveaux", action = sayLineAndLevel, name = "lineAndLevel")
lineHeadings.add(label = "&Basculer le mode de lecture des entêtes", action = toggleMode, accelerator =shortcuts["toggleMode"], name = "toggleMode")
lineHeadings.nothing.checked = True

# Sélection

selection = menuForPython.add(label = "&Sélections", submenu = True, name = "selection")
selection.add(label = "Sélectionner la &classe courante", action = selectCurrentClass, accelerator = shortcuts["selectCurrentClass"], name = "selectCurrentClass")
selection.add(label = "Sélectionner la &fonction courante", action = selectCurrentFunction, accelerator = shortcuts["selectCurrentFunction"], name = "selectCurrentFunction")

# insertion

insertion = menuForPython.add(label = "&Insertion", submenu = True, name = "insertion")
insertion.add(label = "&Insérer une instruction d'en-tête de fichier", action = insertHeaderStatement , accelerator = shortcuts["insertHeaderStatement"], name = "insertHeaderStatement")

# Suppressions

deletion = menuForPython.add(label = "S&uppressions", submenu = True, name = "deletion")
deletion.add(label = "Ssupprimmer la &classe courante", action = deleteCurrentClass, accelerator = shortcuts["deleteCurrentClass"], name = "deleteCurrentClass")
deletion.add(label = "Supprimer la &fonction courante", action = deleteCurrentFunction, accelerator = shortcuts["deleteCurrentFunction"], name = "deleteCurrentFunction")
deletion.add(label = "Supprimer la ligne courante", action = deleteCurrentLine, accelerator = shortcuts["deleteCurrentLine"], name = "deleteCurrentLine")

# Navigation

navigation = menuForPython.add(label = "&Navigation", submenu = True, name = "navigation")
navigation.add(label = "Se déplacer vers l'élément &suivant", action = nextElement, accelerator = shortcuts["nextElement"], name = "nextElement")
navigation.add(label = "Se déplacer vers l'élément &précédent", action = previousElement, accelerator = shortcuts["previousElement"], name = "previousElement")
navigation.add(label = "Se déplacer vers la &classe suivante", action = nextClass, accelerator = shortcuts["nextClass"], name = "nextClass")
navigation.add(label = "Se déplacer vers la classe p&récédente", action = previousClass, accelerator = shortcuts["previousClass"], name = "previousClass")
navigation.add(label = "Liste des c&lasses et fonctions", action = selectAClassOrFunction, accelerator = shortcuts["selectAClassOrFunction"], name = "selectAClassOrFunction")

# Modify shortcuts

modifyAccelerators = menuForPython.add(label = "&Modifier les raccourcis claviers", submenu = True, name = "modifyAccelerators")
modifyAccelerators.add(label = "Modifier les ra&ccourcis-clavier des commandes", action = modifyShortcuts, accelerator = shortcuts["modifyShortcuts"], name = "modifyShortcuts")

# For python versions.
pythonVersion = menuForPython.add(label = "Activer une &version de Python installée", submenu = True, name = "pythonVersion")
pythonVersion.add(label = "6&pad++ Python version", action = make_action(0, "6padPythonVersion"), name = "6padPythonVersion")

# On vérifie la présence du sous-menu permettant de mettre à jour pip.
if curPythonVersion != "6padPythonVersion" and os.path.exists(os.path.join(os.path.dirname(curPythonVersion), "scripts", "pip.exe")):
	if menuForPython.pipMenu == None:
		shortcuts["updatePip"] = sp.getConfig("updatePip") if sp.getConfig("updatePip") else "CTRL+SHIFT+P"
		shortcuts["executeAPipCommand"] = sp.getConfig("executeAPipCommand") if sp.getConfig("executeAPipCommand") else "CTRL+F11"
		pipMenu = menuForPython.add(label = "Commandes &PIP", submenu = True, name = "pipMenu")
		pipMenu.add(label = "Me&ttre à jour pip", action = updatePip, name = "updatePip", accelerator = shortcuts["updatePip"])
		pipMenu.add(label = "E&xécuter une commande PIP", action = executeAPipCommand, name = "executeAPipCommand", accelerator = shortcuts["executeAPipCommand"])
	# On vérifie si l'on est avec Python 27 pour l'ajout de la compilation avec Py2exe compatible Python 27.
	if re.match("python27", curPythonVersion.split("\\")[-2], re.I):
		if menuForPython.compileScriptWithPy2exeP27 == None:
			shortcuts["compileScriptWithPy2exeP27"] = sp.getConfig("compileScriptWithPy2exeP27") if sp.getConfig("compileScriptWithPy2exeP27") else "CTRL+F10"
			menuForPython.add(label = "C&ompiler avec Py2exe pour Python 27", action = compileScriptWithPy2exeP27, name = "compileScriptWithPy2exeP27", accelerator = shortcuts["compileScriptWithPy2exeP27"])
	if int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 2:
		# On tourne avec une version 3 de Python, on supprime la clé de dictionnaire spécifique à la compilation avec Py2exe P27.
		if "compileScriptWithPy2exeP27" in shortcuts.keys():
			del shortcuts["compileScriptWithPy2exeP27"]
else:
	if "updatePip" in shortcuts.keys():
		del shortcuts["updatePip"]
	if "executeAPipCommand" in shortcuts.keys():
		del shortcuts["executeAPipCommand"]
	if "compileScriptWithPy2exeP27" in shortcuts.keys():
		del shortcuts["compileScriptWithPy2exeP27"]
	menuForPython.remove(name = "compileScriptWithPy2exeP27")
	menuForPython.remove(name = "pipMenu")

# for installing setup package.
if curPythonVersion != "6padPythonVersion" and int(curPythonVersion.split("\\")[-2].split("ython")[1][0]) > 1:
	installPackage = menuForPython.add(label = "Ins&taller un package avec un script setup.py", action = installPackageFromSetupScript, name = "installPackageWithSetup", accelerator = shortcuts["installPackageWithSetup"])

# for running code or module.
menuForPython.add(label = "&Exécuter du code python ou un module", action = runAPythonCodeOrModule, name = "runAPythonCodeOrModule", accelerator = shortcuts["runAPythonCodeOrModule"])

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
						pythonVersion.add(label = "%s - %s" % (f, str(os.path.join(p, f))), action = make_action(i, f, exFile), name = f)
						# On remplit la liste pythonVersionsList déclarée en début de module.
						pythonVersionsList.append(exFile)

addPythonVersionsSubMenus()
pythonVersion[pythonVersionsList.index(curPythonVersion)].checked = True
