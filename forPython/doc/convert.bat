@echo off
pandoc -s --toc -N --ascii -c style.css -f markdown -t html -o readme.html readme.md
pandoc -s --ascii -c style.css -f markdown -t html -o changelog.html changelog.md
pandoc -s --ascii -c style.css -f markdown -t html -o roadmape.html roadmape.md
pause