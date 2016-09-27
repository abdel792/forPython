@echo off
pandoc -s --toc -N --ascii -c style.css -f markdown -t html -o readme.html readme.md
pandoc -s --ascii -c style.css -f markdown -t html -o change.html change.md
pandoc -s --ascii -c style.css -f markdown -t html -o cahier-des-charges.html cahier-des-charges.md