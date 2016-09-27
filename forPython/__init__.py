# coding:utf-8

# Importation des modules.
import sixpad as sp
import inspect
import re
import os
import subprocess

# Dictionnaire pour les regexps.
regexp={
	"regClsPython":"^[ \t]*class.*?:.*",
	"regFuncPython":"^[ \t]*def.*?:.*",
	"regClsAndFuncPython":"^[ \t]*((?:class|def).*?:.*$)"
	}

# Variables globales.
mode = 0
pythonVersion = sp.getConfig("pythonVersion") if sp.getConfig("pythonVersion") else "6padPythonVersion"

# Dictionnaire pour le chemin de l'exécutable de Python.
pythonExPaths = {"6padPythonVersion":"6pad++"}

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
shortcuts["selectAClassOrFunction"] = sp.getConfig("selectAClassOrFunction") if sp.getConfig("selectAClassOrFunction") else "CTRL+L"
# Modify shortcuts
shortcuts["modifyShortcuts"] = sp.getConfig("modifyShortcuts") if sp.getConfig("modifyShortcuts") else "CTRL+M"
# Running code or module
shortcuts["runAPythonCodeOrModule"] = sp.getConfig("runAPythonCodeOrModule") if sp.getConfig("runAPythonCodeOrModule") else "CTRL+F5"

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
		"selectAClassOrFunction":navigation.selectAClassOrFunction.label.replace("&", ""),
		"modifyShortcuts":modifyAccelerators.modifyShortcuts.label.replace("&", ""),
		"runAPythonCodeOrModule":menuForPython.runAPythonCodeOrModule.label.replace("&", "")
	}
	# On remplit notre liste de choix à partir de nos 2 dictionnaires functionsList et shortcuts.
	choices = [functionsList[k] + ":" + shortcuts[k] for k in shortcuts.keys()]
	# On affiche notre listebox.
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

def make_action(f):
	def action():
		global pythonVersion
		menuName = f
		pythonVersion = menuName
		for x in range(menuPythonVersion.length):
			if menuPythonVersion[x].name != menuName:
				menuPythonVersion[x].checked = False
			else:
				menuPythonVersion[x].checked = True
		sp.setConfig("pythonVersion", pythonVersion)
		sp.window.alert("C'est bon, %s a bien été activé !" % (menuPythonVersion[f].name), "Confirmation")
	return action

def runAPythonCodeOrModule():
	if pythonExPaths[pythonVersion] == "6pad++":
		if not sp.window.curPage.selectedText:
			sp.window.alert("Vous devez sélectionner une partie de code pour pouvoir l'exécuter avec le python embarqué avec 6pad++", "Information")
			return
		#code = compile(sp.window.curPage.selectedText, sp.window.curPage.file, "exec")
		code = sp.window.curPage.selectedText
		exec(code)
	else:
		with open(os.path.join(os.path.dirname(sp.window.curPage.file), "logfile.log"), 'w') as f:
			proc = subprocess.Popen([pythonExPaths[pythonVersion], sp.window.curPage.file], stdout = f, stderr = f)
			(stdout, stderr) = proc.communicate()
			sp.window.open(os.path.join(os.path.dirname(sp.window.curPage.file), "logfile.log"))

# menus

toolsMenu = sp.window.menus.tools
menuForPython = toolsMenu.add(label = "for &Python", submenu = True)

# en-têtes de ligne

lineHeadings = menuForPython.add(label = "Lecture des entêtes de &lignes", submenu = True)
lineHeadings.add(label = "Ne &rien dire", action = sayNothing, name = "nothing")
lineHeadings.add(label = "Dire les nu&méro de lignes", action = sayLineNumber, name = "lineNumber")
lineHeadings.add(label = "Dire les &indentations", action = sayIndentation, name = "indentation")
lineHeadings.add(label = "Dire les num&éros de lignes et les indentations", action = sayLineAndIndentation, name = "lineAndIndentation")
lineHeadings.add(label = "Dire les ni&veaux", action = sayLevel, name = "level")
lineHeadings.add(label = "Dire les numéro de li&gnes et les niveaux", action = sayLineAndLevel, name = "lineAndLevel")
lineHeadings.add(label = "&Basculer le mode de lecture des entêtes", action = toggleMode, accelerator =shortcuts["toggleMode"], name = "toggleMode")
lineHeadings.nothing.checked = True

# Sélection

selection = menuForPython.add(label = "&Sélections", submenu = True)
selection.add(label = "Sélectionner la &classe courante", action = selectCurrentClass, accelerator = shortcuts["selectCurrentClass"], name = "selectCurrentClass")
selection.add(label = "Sélectionner la &fonction courante", action = selectCurrentFunction, accelerator = shortcuts["selectCurrentFunction"], name = "selectCurrentFunction")

# insertion

insertion = menuForPython.add(label = "&Insertion", submenu = True)
insertion.add(label = "&Insérer une instruction d'en-tête de fichier", action = insertHeaderStatement , accelerator = shortcuts["insertHeaderStatement"], name = "insertHeaderStatement")

# Suppressions

deletion = menuForPython.add(label = "S&uppressions", submenu = True)
deletion.add(label = "Ssupprimmer la &classe courante", action = deleteCurrentClass, accelerator = shortcuts["deleteCurrentClass"], name = "deleteCurrentClass")
deletion.add(label = "Supprimer la &fonction courante", action = deleteCurrentFunction, accelerator = shortcuts["deleteCurrentFunction"], name = "deleteCurrentFunction")
deletion.add(label = "Supprimer la ligne courante", action = deleteCurrentLine, accelerator = shortcuts["deleteCurrentLine"], name = "deleteCurrentLine")

# Navigation

navigation = menuForPython.add(label = "&Navigation", submenu = True)
navigation.add(label = "Se déplacer vers l'élément &suivant", action = nextElement, accelerator = shortcuts["nextElement"], name = "nextElement")
navigation.add(label = "Se déplacer vers l'élément &précédent", action = previousElement, accelerator = shortcuts["previousElement"], name = "previousElement")
navigation.add(label = "Liste des c&lasses et fonctions", action = selectAClassOrFunction, accelerator = shortcuts["selectAClassOrFunction"], name = "selectAClassOrFunction")

# Modify shortcuts

modifyAccelerators = menuForPython.add(label = "&Modifier les raccourcis claviers", submenu = True)
modifyAccelerators.add(label = "Modifier les ra&ccourcis-clavier des commandes", action = modifyShortcuts, accelerator = shortcuts["modifyShortcuts"], name = "modifyShortcuts")

# For python versions.
menuPythonVersion = menuForPython.add(label = "Activer une &version de Python installée", submenu = True)
menuPythonVersion.add(label = "6&pad++ Python version", action = make_action("6padPythonVersion"), name = "6padPythonVersion")

# for running code or module.
menuForPython.add(label = "&Exécuter du code python ou un module", action = runAPythonCodeOrModule, name = "runAPythonCodeOrModule", accelerator = shortcuts["runAPythonCodeOrModule"])

def addPythonVersionsSubMenus():
	# On crée une liste des dossier susceptibles de contenir un répertoire de Python.
	pathsList = ["C:",
	"C:/Programs",
	"C:/Program Files",
	"C:/Program Files (x86)",
	"D:",
	"D:/Programs",
	"D:/Program Files",
	"D:/Program Files (x86)",
	"E:"
	"E:/Programs",
	"E:/Program Files"
	"E:/Program Files (x86)"
	]
	for p in pathsList:
		# Si le répertoire existe vraiment.
		if os.path.isdir(p):
			for f in os.listdir(p):
				# S'il contient bien un dossier d'une éventuelle version de Python.
				if re.match("^python\d\.?\d", f, re.IGNORECASE):
					# On vérifie la présence de l'exécutable.
					if os.path.isfile(os.path.join(p, f, "python.exe")):
						# L'exécutable existe bien, on affecte son chemin à la variable exFile.
						exFile = os.path.join(p, f, "python.exe")
						# On crée le sous-menu correspondant.
						menuPythonVersion.add(label = "%s - %s" % (f, os.path.dirname(exFile)), action = make_action(f), name = f)
						# On remplit le dictionnaire pythonExPaths.
						pythonExPaths[f] = exFile

addPythonVersionsSubMenus()
menuPythonVersion[pythonVersion].checked = True
