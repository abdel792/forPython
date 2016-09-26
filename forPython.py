import re
sp=sixpad
regFunc = re.compile("^[ \t]*def.*?:*")
regClass = re.compile("^[ \t]*class.*?:*")
def nextClass():
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
	sp.say(sp.window.curPage.line(sp.window.curPage.curLine), True)
sixpad.window.addAccelerator("F7", nextClass)
def previousClass():
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
	sp.say(sp.window.curPage.line(sp.window.curPage.curLine), True)
sixpad.window.addAccelerator("SHIFT+F7", previousClass)

def nextFunction():
	if regFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine < sp.window.curPage.lineCount:
		i = sp.window.curPage.curLine + 1
	else:
		i = sp.window.curPage.curLine
	while i < sp.window.curPage.lineCount and not regFunc.match(sp.window.curPage.line(i)):
		i += 1
		if i == sp.window.curPage.lineCount:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sp.say(sp.window.curPage.line(sp.window.curPage.curLine), True)
sixpad.window.addAccelerator("F2", nextFunction)

def previousFunction():
	if regFunc.match(sp.window.curPage.line(sp.window.curPage.curLine)) and sp.window.curPage.curLine > 0:
		i = sp.window.curPage.curLine - 1
	else:
		i = sp.window.curPage.curLine
	while i > -1 and not regFunc.match(sp.window.curPage.line(i)):
		i -= 1
		if i == -1:
			sp.window.messageBeep(0)
			break
	sp.window.curPage.curLine = i
	sp.say(sp.window.curPage.line(sp.window.curPage.curLine), True)
sixpad.window.addAccelerator("SHIFT+F2", previousFunction)
