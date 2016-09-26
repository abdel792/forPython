# coding:utf-8

import sixpad as sp
import re

mode = 0

shortcuts={}
	# lineHeadings
shortcuts["toggleMode"] = sp.getConfig("toggleMode") if sp.getConfig("toggleMode")  else "CTRL+F8"
# Selection
shortcuts["selectCurrentFunction"] = sp.getConfig("selectCurrentFunction") if sp.getConfig("selectCurrentFunction") else "CTRL+R"
shortcuts["selectCurrentClass"] = sp.getConfig("selectCurrentClass") if sp.getConfig("selectCurrentClass") else "CTRL+SHIFT+R"
shortcuts["selectAClassOrFunction"] = sp.getConfig("selectAClassOrFunction") if sp.getConfig("selectAClassOrFunction") else "CTRL+L"
# Deletion
shortcuts["deleteCurrentFunction"] = sp.getConfig("deleteCurrentFunction") if sp.getConfig("deleteCurrentFunction") else "CTRL+D"
shortcuts["deleteCurrentClass"] = sp.getConfig("deleteCurrentClass") if sp.getConfig("deleteCurrentClass") else "CTRL+SHIFT+D"
# Navigation
shortcuts["nextElement"] = sp.getConfig("nextElement") if sp.getConfig("nextElement") else "F2"
shortcuts["previousElement"] = sp.getConfig("previousElement") if sp.getConfig("previousElement") else "SHIFT+F2"
# Modify shortcuts
shortcuts["modifyShortcuts"] = sp.getConfig("modifyShortcuts") if sp.getConfig("modifyShortcuts") else "CTRL+M"

def modifyShortcuts():
	choices = [k + ":" + shortcuts[k] for k in shortcuts.keys()]
	element = sp.window.choice("Sélectionnez une fonction", "Liste des fonctions", choices)
	if element == -1:
		return
	prompt=sp.window.prompt("Saisissez votre raccourci pour la commande %s" % choices[element].split(":")[0], "Nouveau raccourci", text=shortcuts[choices[element].split(":")[0]])
	if not prompt:
		return
	sp.setConfig(choices[element].split(":")[0], prompt)
	sp.window.alert("C'est bon, votre racourci %s a bien été attribué à la commande %s, vous devrez quitter puis relancer 6pad++ pour que vos changements prennent pleintment effet !" % (prompt, choices[element].split(":")[0]), "Confirmation")

def toggleMode():
	if mode == 0:
		sayLineNumber()
		sp.say("Dire les numéros de lignes", True)
	elif mode == 1:
		sayLevel()
		sp.say("Dire les niveaux", True)
	elif mode == 2:
		sayLineAndLevel()
		sp.say("Dire les numéros de lignes et les niveaux", True)
	elif mode == 3:
		sayNothing()
		sp.say("Ne rien dire", True)

def onKeyUp(activePage, vk):
	#sp.say(str(vk), True)
	if vk in [8, 9, 1033] and activePage.position == activePage.lineSafeStartOffset(activePage.curLine):
		sp.say("Niveau " + str(activePage.lineIndentLevel(activePage.curLine)) + ". " + activePage.line(activePage.curLine), True)
	if vk in [33, 34, 38, 40, 547, 548, 550, 552]:
		sp.say(getLineHeading(activePage.curLine), True)

def getLineHeading(line):
	lineNumber = str(line+1) + ". "
	level = "niveau " + str(sp.window.curPage.lineIndentLevel(line)) + ". "
	lineAndLevel = lineNumber + level
	if mode == 0:
		sayLine = ""
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 1:
		sayLine = lineNumber
		sayLevel = ""
		sayLineAndLevel = ""
	elif mode == 2:
		sayLine = ""
		sayLevel = level
		sayLineAndLevel = ""
	elif mode == 3:
		sayLine = ""
		sayLevel = ""
		sayLineAndLevel = lineAndLevel
	return "%s%s%s%s" % (sayLine, sayLevel, sayLineAndLevel, sp.window.curPage.line(line))
sp.window.curPage.addEvent("keyUp", onKeyUp)

def openedPage(newPage):
	newPage.addEvent("keyUp", onKeyUp)
sp.window.addEvent("pageOpened", openedPage)

def parseElement(element):
	offset=sp.window.curPage.text.index(element)
	lineNumber=sp.window.curPage.lineOfOffset(offset)

	regClass = re.compile("^[ \t]*class.*?:.*", re.MULTILINE)
	if regClass.match(element):
		key="%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "classe", sp.window.curPage.lineIndentLevel(lineNumber))
	else:
		key="%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "fonction", sp.window.curPage.lineIndentLevel(lineNumber))
	return key

def getFunctionName():
	regFunc = re.compile("^[ \t]*def.*?:.*", re.MULTILINE)
	if regFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regFunc.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	funcName=parseElement(sp.window.curPage.line(i)).split(" ")[0]
	return funcName
def getClassName():
	regClass = re.compile("^[ \t]*class.*?:.*", re.MULTILINE)
	if regClass.match(sp.window.curPage.line(sp.window.curPage.curLine)):
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regClass.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			return None
	className=parseElement(sp.window.curPage.line(i)).split(" ")[0]
	return className

def nextElement():
	regClassAndFunc = re.compile("^[ \t]*((?:class|def).*?:.*$)", re.MULTILINE)
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
	regClassAndFunc = re.compile("^[ \t]*((?:class|def).*?:.*$)", re.MULTILINE)
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
	regFunc = re.compile("^[ \t]*def.*?:.*", re.MULTILINE)
	regClassAndFunc = re.compile("^[ \t]*((?:class|def).*?:.*$)", re.MULTILINE)
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
	selectedText=text if len(mySel) < 2 else text.split(mySel[1])[0]
	sp.window.curPage.selectedText = selectedText
	return True

def selectionClass():
	regClass = re.compile("^[ \t]*class.*?:.*", re.MULTILINE)
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
	selectedText=text if len(mySel) < 2 else text.split(mySel[1])[0]
	sp.window.curPage.selectedText = selectedText
	return True

def selectCurrentFunction():
	funcName = getFunctionName()
	if not funcName:
		sp.say("Aucune fonction à sélectionner !", True)
		return
	text=sp.window.curPage.text
	if selectionFunction():
		sp.say("C'est bon, la fonction %s a bien été sélectionnée !" % (funcName), True)
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
		sp.say("C'est bon, la classe %s a bien été sélectionnée !" % (className), True)
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
	regClassAndFunc = re.compile("^[ \t]*((?:class|def).*?:.*$)", re.MULTILINE)
	choices=regClassAndFunc.findall(sp.window.curPage.text)
	if choices:
		choices=[k.strip() for k in choices]
		choicesList=[parseElement(k) for k in choices]
		i = sp.window.curPage.curLine
		while i > -1 and not regClassAndFunc.match(sp.window.curPage.line(i)):
			i -= 1
			if i == -1:
				i = sp.window.curPage.text.index(choices[0])
				i = sp.window.curPage.lineOfOffset(i)
				break
		element=sp.window.choice("Veuillez sélectionner une classe ou fonction", "Liste d'éléments", choicesList, choices.index(sp.window.curPage.line(i).strip()))
		if element == -1:
			return
		offset=sp.window.curPage.text.index(choices[element])
		lineNumber=sp.window.curPage.lineOfOffset(offset)
		sp.window.curPage.curLine = lineNumber
		sp.say(getLineHeading(lineNumber), True)
	else:
		sp.say("Aucune classe ou fonction trouvée !", True)

def sayNothing ():
	global mode
	mode=0
	lineHeadings.nothing.checked=True
	lineHeadings.lineNumber.checked=False
	lineHeadings.level.checked=False
	lineHeadings.lineAndLevel.checked=False

def sayLineNumber ():
	global mode
	mode=1
	lineHeadings.nothing.checked=False
	lineHeadings.lineNumber.checked=True
	lineHeadings.level.checked=False
	lineHeadings.lineAndLevel.checked=False

def sayLevel ():
	global mode
	mode=2
	lineHeadings.nothing.checked=False
	lineHeadings.lineNumber.checked=False
	lineHeadings.level.checked=True
	lineHeadings.lineAndLevel.checked=False
def sayLineAndLevel ():
	global mode
	mode=3
	lineHeadings.nothing.checked=False
	lineHeadings.lineNumber.checked=False
	lineHeadings.level.checked=False
	lineHeadings.lineAndLevel.checked=True

# menus

toolsMenu = sp.window.menus[-2]
menuForPython = toolsMenu.add(label="for &Python", submenu=True)
lineHeadings = menuForPython.add(label="Lecture des entêtes de &lignes", submenu=True)
lineHeadings.add(label="Ne &rien dire", action=sayNothing, name="nothing")
lineHeadings.add(label="Dire les nu&méro de lignes", action=sayLineNumber, name="lineNumber")
lineHeadings.add(label="Dire les ni&veaux", action=sayLevel, name="level")
lineHeadings.add(label="Dire les numéro de li&gnes et les niveaux", action=sayLineAndLevel, name="lineAndLevel")
lineHeadings.add(label = "&Basculer le mode de lecture des entêtes", action = toggleMode, accelerator =shortcuts["toggleMode"])
lineHeadings.nothing.checked=True

# Sélection

selection = menuForPython.add(label="&Sélections", submenu=True)
selection.add(label="Sélectionner la &classe courante", action=selectCurrentClass, accelerator=shortcuts["selectCurrentClass"])
selection.add(label="Sélectionner la &fonction courante", action=selectCurrentFunction, accelerator=shortcuts["selectCurrentFunction"])
selection.add(label="Sélectionner une c&lasse ou fonction", action=selectAClassOrFunction, accelerator=shortcuts["selectAClassOrFunction"])

# Suppressions

deletion = menuForPython.add(label="S&uppressions", submenu=True)
deletion.add(label="Ssupprimmer la &classe courante", action=deleteCurrentClass, accelerator=shortcuts["deleteCurrentClass"])
deletion.add(label="Supprimer la &fonction courante", action=deleteCurrentFunction, accelerator=shortcuts["deleteCurrentFunction"])

# Navigation

navigation = menuForPython.add(label="&Navigation", submenu=True)
navigation.add(label="Se déplacer vers l'élément &suivant", action=nextElement, accelerator=shortcuts["nextElement"])
navigation.add(label="Se déplacer vers l'élément &précédent", action=previousElement, accelerator=shortcuts["previousElement"])

# Modify shortcuts

modifyAccelerators = menuForPython.add(label="&Modifier les raccourcis claviers", submenu=True)
modifyAccelerators.add(label="Modifier les raccourcis-claviers des commandes", action=modifyShortcuts, accelerator=shortcuts["modifyShortcuts"])
