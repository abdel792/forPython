# coding:utf-8

import re
sp=sixpad

regFunc = re.compile("^[ \t]*def.*?:.*")
regClass = re.compile("^[ \t]*class.*?:.*")
regClassAndFunc = re.compile("^[ \t]*((?:class|def).*?:.*$)", re.MULTILINE)
mode = 0

def toggleMode():
	global mode
	if mode == 0:
		mode = 1
		sp.say("Dire les numéros de lignes", True)
	elif mode == 1:
		mode = 2
		sp.say("Dire les niveaux", True)
	elif mode == 2:
		mode = 3
		sp.say("Dire les numéros de lignes et les niveaux", True)
	elif mode == 3:
		mode = 0
		sp.say("Ne rien dire", True)
sp.window.addAccelerator("CTRL+F8", toggleMode)

def onKeyDown(activePage, vk):
	if vk == 38 and not activePage.selectedText:
		lineNumber = activePage.curLine - 1
		if lineNumber < 0:
			lineNumber = 0
		activePage.curLine = lineNumber 
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	if vk == 40 and not activePage.selectedText:
		lineNumber = activePage.curLine + 1
		if lineNumber == activePage.lineCount:
			lineNumber = activePage.lineCount - 1
		activePage.curLine = lineNumber
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	if vk == 547 and not activePage.selectedText:
		activePage.curLine = activePage.lineCount - 1
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	if vk == 548 and not activePage.selectedText:
		activePage.curLine = 0
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	if vk == 33 and not activePage.selectedText:
		lineNumber = activePage.curLine - 16
		if lineNumber < 0:
			lineNumber = 0
		activePage.curLine = lineNumber
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	if vk == 34 and not activePage.selectedText:
		lineNumber = activePage.curLine + 16
		if lineNumber >= activePage.lineCount:
			lineNumber = activePage.lineCount - 1
		activePage.curLine = lineNumber 
		sp.say(getLineHeading(activePage.curLine), True)
		return False
	return True

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
sp.window.curPage.addEvent("keyDown", onKeyDown)

def openedPage(newPage):
	newPage.addEvent("keyDown", onKeyDown)
sp.window.addEvent("pageOpened", openedPage)

def parseElement(element):
	offset=sp.window.curPage.text.index(element)
	lineNumber=sp.window.curPage.lineOfOffset(offset)
	if regClass.match(element):
		key="%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "classe", sp.window.curPage.lineIndentLevel(lineNumber))
	else:
		key="%s %s, niveau %d" % (element.split(" ")[1].split("(")[0], "fonction", sp.window.curPage.lineIndentLevel(lineNumber))
	return key

def nextElement():
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
sp.window.addAccelerator("F2", nextElement)

def previousElement():
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
sp.window.addAccelerator("SHIFT+F2", previousElement)

def selectAClassOrFunction():
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
sp.window.addAccelerator("CTRL+L", selectAClassOrFunction)