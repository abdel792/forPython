try:
	import pkgutil
	for i in pkgutil.walk_packages():
		f,j,k=i
		print(j)
except: pass
try:
	import sys
	for e in sys.modules: print(e)
except: pass