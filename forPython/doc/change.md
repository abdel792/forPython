% Changements et historique des modifications pour l'extension forPython
.
.

# 21-01-2016 #

*  Navigation parmi les fonctions d'un module par F2 et Shift+F2.
*  Navigation parmi les classes d'un module par F7 et Shift+F7.
*  Affichage de la liste des éléments (class et def) du code par Ctrl+L.

# 22-01-2016 #

*  Désormais, dans la liste d'éléments, le nom de la fonction ou classe est dit en premier, suivi de classe ou fonction, suivi du niveau.

# 23-01-2016 #

*  Avec CTRL+F8, on bascule désormais entre le mode "Dire les numéros de lignes", "Dire les niveaux", "Dire les numéros de lignes et les niveaux", et "Ne rien dire", qui est le choix par défaut.
  Ces fonctionnalités sont regroupées dans le menu "Lecture des en-têtes de lignes".

# 25-01-2016 #

*  Positionnement sur l'élément le plus proche du curseur lors de l'affichage de la liste des éléments.

# 28-01-2016 #

*  Désormais, toutes les commandes ainsi que leurs raccourcis claviers ont été intégrées dans un menu, "for Python", situé entre le menu "Format et le menu Outils.
*  Possibilité de sélectionner la fonction courante avec CTRL+R, la classe courante avec CTRL+SHIFT+R, supprimer la fonction courante avec CTRL+D, supprimer la classe courante avec CTRL+SHIFT+D.
  Ces fonctionnalités ont été regroupées dans les menus "Sélection" et "Suppression".

# 29-01-2016 #

*  Déplacement du menu "for Python" dans le menu Outils de 6pad++.

# 04-02-2016 #

*  Vocalisation des changements de niveaux avec tab, shift+tab, ou backSpace, lorsqu'on est en début de ligne.
*  Désormais, en réalisant le raccourci clavier "CTRL+M", chacune et chacun pourra modifier les raccourcis-claviers des différentes commandes, selon les préférences.

# 07-02-2016 #

*  Désormais, vous disposez d'un nouveau mode de lecture des entêtes de lignes, il s'agit de la lecture des indentations, ainsi que la lecture des numéros de lignes et des indentations.
*  Désormais, dans la liste des fonctions dont on va souhaiter modifier les raccourcis-clavier, la liste recueille maintenant les noms de chaque item en français, en allant les rechercher dans les labels des menus correspondant.
*  La fonction getCurScriptFolderPath a bien été corrigée et devrait fonctionner quel que soit le contexte du répertoire où figurera l'extension forPython.

# 08-02-2016 #

*  Prise en compte du niveau d'indentation, lors de l'utilisation de la touche backSpace lorsqu'on est en début de ligne.
*  Correction d'une petite erreur concernant la lecture des entêtes de lignes dans l'événement keyUp.

# 15-02-2016 #

*  Listage des versions de python installées sur l'ordinateur courant dans un sous-menu du menu forPython.
*  Le sous-menu forPython comporte désormais une commande exécuter, activable grâce au raccourci clavier CTRL+F5, qui exécutera, selon la version de Python choisie dans le menu, la version de Python qui sera cochée et l'associera au module en cours d'implémentation.
    Il conviendra alors de sélectionner dans le module en cours d'exploration, la partie du code que l'on souhaite voir s'exécuter, avant de lancer le raccourci CTRL+F5, la sortie sera dirigée vers la console.
*  Si on coche une version installée sur le PC, la sélection du code à exécuter ne sera pas indispensable, ce sera tout le module en cours d'exploration ou d'implémentation qui sera exécuté, et la sortie redirigée vers un fichier logFile.log, qui sera ouvert automatiquement.
*  Les regexps servant à atteindre les classes et fonctions ont été réunies dans un dictionnaire, qui pourra être enrichi par d'autres regexps, au cas où on souhaiterais exploiter d'autres langages de programmation, différents du Python.
*  La fonction événementielle onKeyUp a été mise à jour.

# 17-02-2016 #

*  Correction d'un bug et amélioration de la reconnaissance de répertoire des pythons installés.
*  Création d'une variable globale pour la conservation du chemin de l'exécutable de python sélectionné.

# 23-02-2016 #

*  Lorsqu'une erreur est détectée dans le module en cours d'exécution, une alerte s'affiche, donnant à l'utilisateur la ligne où se situe l'erreur, et l'invitant à valider sur OK pour l'atteindre directement dans le module concerné.
  Cette alerte invite également l'utilisateur à consulter la console, ainsi que le fichier logfile.log, pour plus de détails sur l'erreur trouvée.
*  Si le fichier en cours n'est pas sauvegardé lors de son exécution, l'utilisateur sera invité à valider sur OK pour sauvegarder son module dans un fichier tmp.py, figurant dans le même répertoire que l'exécutable de 6pad++.
  Il devra ensuite relancer son raccourci pour ré exécuter son module.
*  Amélioration du rapport des tracebacks (retours d'erreurs).

# 25-02-2016 #

*  Amélioration de la fonction d'identification de la ligne d'erreur.

# 06-03-2016 #

*  Amélioration pour prise en compte de l'installation de python 3.5 sur l'ordinateur courant.

# 07-03-2016 #

*  Désormais, le déplacement parmi les classes suivantes et précédentes est possible, avec CTRL+F2 et CTRL+SHIFT+F2.
*  Les accelerators des items de menu se réfèrent désormais également à un dictionnaire, car la fonction modifyShortcuts a besoin aussi de connaître ses accelerators, pour permettre de proposer aux utilisateurs de les modifier au besoin.

# 10-03-2016 #

*  Implémentation de l'ajout d'un nouveau sous-menu dans le menu "for Python", qui permet de mettre à jour le module pip, après vérification de sa réelle disponibilité.

# 15-03-2016 #

*  Compilation avec Py2exe pour Python27 CTRL+F10.
  Son affichage est conditionné à la version de Python que vous utilisez.
*  Exécution de commandes PIP CTRL+F11.
  Son affichage est conditionné à la version de Python que vous utilisez.
  Cette commande permettant d'exécuter une commande PIP à partir d'une liste, nous donne accès à la possibilité d'installer wxPython_Phoenix pour Python 3 ainsi que Py2exe pour Python 3.3 et plus.
*  Possibilité d'installation d'un package avec un script setup.py CTRL+F12.

# 16-03-2016 #

*  Ajout de la commande permettant d'entrer une commande à exécuter, grâce au raccourci CTRL+SHIFT+E.
  L'utilisateur devra alors saisir uniquement tout ce qui suivra le chemin de l'exécutable de Python, dans sa commande, car celui-ci sera déjà pris en compte, selon la version de Python utilisée.
  Le résultat s'affichera alors dans la console, ainsi que dans le fichier logfile.log.
  Par exemple, pour connaître sa version de Python, -V devrait l'afficher dans la console, si on utilise une version 2 ou supérieure de Python.
  C'est surtout l'option -h qui est intéressante, car elle affiche l'aide de toutes les options disponibles, si on l'écrit toute seule.
  On peut aussi l'utiliser pour obtenir l'aide sur une commande pip, par exemple .
  -m pip install -.
  Devrait nous afficher l'aide sur la commande install.

# 25-04-2016 #

*  Contextualisation du déploiement du forPython uniquement aux fichiers python à l'extension .py et .pyw.
*  Réorganisation des menu avec notamment les créations des menus "affichage", "python" et "accessibilité" dans l'interface de 6pad++.
*  Ré-écriture et formalisation des noms des menus principaux dans le code.
*  Renommage du fichier log.txt en changes.txt.
*  Ajout de l'activation et de la désactivation de la synthèse vocale dans le menu accessibilité.
*  Correction d'un bug dans la regexp se déclenchant lors du déplacement d'élément en élément.
*  Ajout de beep à l'atteinte des limites haut et bas du document courant.
*  Ajout de commandes d'exploration des blocs de code par alt+left, alt+up, alt+right, et alt+down.
*  Ajout d'une fonctionnalité de rafraîchissement et reformatage de code (menu affichage).
*  Ajout d'une fonctionnalité de définition de mot clé sous le curseur (menu python).
*  Ajout d'une fonctionnalité de complétion de code sous le curseur (menu python).
*  Ajout de menu d'insertion de balises de fin de bloc à la basic au code sélectionné ou non (menu affichage).
*  Ajout d'un rechercher et remplacer avancé (menu édition).
*  Ajout de l'insertion du code d'une fonction par une fenêtre intermédiaire (menu python).
*  Ajout de l'insertion du code d'une classe par une fenêtre intermédiaire (menu python).
*  Ajout de la vérification automatique de la syntaxe de la ligne venant d'être modifiée.

# 01-05-2016 #

*  Ajout d'un item dans le menu outils permettant d'activer/désactiver l'extension forPython.

# 02-05-2016 #

*  Ajout de tous les menus supplémentaires dans le dictionnaire pour faciliter la modification des racourcis-clavier.

# 03-05-2016 #

*  Ajout de la vérification du nouveau raccourci-clavier choisi lors du changement de raccourcis-clavier avec CTRL+M.

# 04-05-2016 #

*  Ajustement des raccourcis-clavier permettant de naviguer parmi les blocs.

# 05-05-2016 #

*  Première ébauche d'écriture d'un fichier d'aide pour l'extension forPython, au format md.
*  Renommage du fichier change.txt en change.md pour faciliter sa conversion en HTML.
*  Ajout du fichier cahier-des-charges.md incluant les améliorations devant être ajoutées au forPython.

# 07-05-2016 #

*  Amélioration de la qualité des boîtes de dialogues en HTA permettant de créer une nouvelle fonction, créer une nouvelle classe et faire une recherche avancée.
  C'est désormais le module subprocess qui se charge d'exécuter les applications HTA grâce à mshta.exe,
  Cependant, des améliorations doivent encore être apportées à ces boîtes de dialogues;
*  Ajout de 2 nouveaux sous-menus dans le menu aide pour le récapitulatif des changements et le cahier des charges de l'extension forPython.
*  Ajout d'un dossier "doc" dans le répertoire forPython, pour permettre aux contributeurs d'enrichir la documentation.


