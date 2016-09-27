% Extension forPython pour 6pad++
% Auteurs : 
  [Abdel](mailto:abdelkrim.bensaid@free.fr)
  [Yannick YOUALÉ](mailto:mailtoloco2011@gmail.com) - Cameroun
  [Cyrille](mailto:cyrille.bougot2@laposte.net)
  Contributeurs : 
  QuentinC
  Jean-François COLAS
  Mathieu Barbe
  Tous membres de la progliste (une liste de discussion francophone de programmeurs déficients visuels)
% Date de rédaction : 18/09/2016

# Présentation #

forPython est une extension pour l'éditeur de texte [6pad++](https://github.com/qtnc/6pad2) créé par QuentinC, servant à améliorer l'accessibilité du codage en langage "Python", pour les développeurs.

Son objectif est de proposer une interface accessible aux personnes déficientes visuelles.

Cette extension peut être utilisée avec les lecteurs d'écran suivants :

1. JAWS;
#. NVDA;
#. Window Eye;
#. System Access;
#. Dolphin Supernova/HAL.

**Attention**, cette extension a été créée avec 6pad++, il faudra donc l'utiliser avec cette version de 6pad uniquement.

Après son activation, forPython devrait vous ajouter certains menus et sous-menus dans votre application portable 6pad++.

Par défaut, l'extension se lance à l'ouverture de fichier python. Vous pourrez l'activer ou le désactiver manuellement en validant sur "Activer le forPython" figurant dans le menu outil de 6pad++.

Mais avant celà, il faudra tout d'abord l'installer !

# Installation de l'extension forPython #

Pour installer l'extension forPython pour 6pad++, voici la procédure :

*  Dans le répertoire où se situe l'exécutable de lancement de 6pad++, créez (s'il n'existe pas déjà) un sous-répertoire, que vous appellerez "plugins";
*  Dans ce dossier "plugins", collez l'archive "forPython.zip", puis décompressez la, en sélectionnant le choix "Extraire ici" ou "Extract here", si vous utilisez Winrar ou 7zip,
  Ceci devrait générer la création d'un nouveau répertoire dans votre dossier "plugins", nommé "forPython";
*  Une fois l'archive décompressée dans le dossier "plugins", vous pourrez vous débarrasser du fichier zip ou le déplacer ailleurs de préférence;
*  Ceci fait, remontez d'un niveau, et plus précisémment, dans le dossier où se situe l'exécutable de 6pad++, puis ouvrez le fichier nommé "6pad++.ini",
  S'il n'est pas présent, créez le, en choisissant bien l'encodage "UTF-8" ou de préférence "UTF-8 sans bom";
*  Si le fichier comporte déjà des instructions, faîtes "ctrl + fin", pour vous situer en fin de fichier, puis ajoutez une ligne, dans laquelle vous écrirez ce qui suit, sans espaces :
  "extension=plugins.forPython/init.py";
*  Faîtes alors "ctrl + s" pour sauvegarder et "Alt F4", pour quitter le fichier.# Les fonctionnalités ajoutées à l'interface de 6pad++ par le forPythonL'extension forPython est sensée ajouter au 6pad++ des fonctionnalités pour permettre principalement au déficients visuels de coder facilement en langage python deux grands groupes:

# Les fonctionnalités ajoutées à l'interface du 6pad++ par le forPython

On peut les ranger en deux grands groupes:

1. les fonctionnalités autonomes à un fichier;
#. et les fonctionnalités de gestion de projet python.

## 1. Les fonctionnalités autonomes à un fichier

Ce sont des fonctionnalités qui s'appliquent à un fichier qu'il appartienne à un projet ou non.
Elles sont les suivantes:

### La prise en charge des types de fichier python dès leur ouverture

Dans la fenêtre des options (menu outils, options ou CTRL+P), à l'onglet "général", vous pouvez contrôler la façon avec laquelle le forPython sera déclenché.
Trois possibilités sont disponibles:

1. Déclencher le forPython à l'ouverture d'un fichier python;
#. Déclencher le forPython au démarrage de 6pad++;
#. Déclencher le forPython manuellement.

Dans le même onglet, vous pouvez préciser les types de fichiers que vous voudrez faire considérer comme des fichiers python.

### La prise en charge du codage dans les diverses version du langage python installés sur l'ordinateur courant

Vous pouvez choisir l'interpréteur python avec lequel travailler dans le forPython.
Ce choix se fait parmi les version de python qui auront été détectés sur votre ordinateur.

Dans le menu outils, versions de python installées, vous pourrez visualiser, ajouter  ou sélectionner l'une de ces version de python.

Le choix d'un interpréteur le valide comme vérificateur de la syntaxe et de la complétion de code.

A noter que dans la liste des interpréteurs disponibles, se trouvera également le 6pad++ lui-même, pour lequel vous pouvez employer le forPython afin de créer ses extensions codés en langage python.

### Le déplacement dans les fichiers python

Vous pouvez utiliser le déplacement de point à point ou le déplacement hiérarchique.

#### Le déplacement de point à point

Les éléments de menus liés à ce type de déplacement sont regroupés dans le menu Affichage, déplacement.
C'est ainsi qu'on peut y trouver les déplacement:
*  A la classe ou fonction suivante (F2)
*  A la classe ou fonction précédente (SHIFT+F2)
*  A la classe suivante (CTRL+F2)
*  A la classe précédente (CTRL+SHIFT+F2)
*  A la fin de la classe ou fonction courante (ALT+F2)
A la prochaine ligne de même niveau ou inférieur (F9)
A la précédente ligne de même niveau ou inférieur (SHIFT+F9)

CTRL+L vous affiche la liste des classes et fonctions du document courant.

#### Le déplacement hiérarchique entre les blocs

Si vous utilisez un autre lecteur d'écran que JAWS, ALT+les flèches de direction vous permettent de vous déplacer de manière hiérarchique dans les bloc de code.
Sinon, utilisez les touches de F9 à F12 pour ce faire.

Les blocs sont les groupes de lignes de même indentation du langage python.

### La sélection de code python

Vous pouvez sélectionner 

*  La fonction courante (CTRL+R);
*  La classe courante (CTRL+SHIFT+R).

Ces commandes se trouvent dans le menu affichage, sélection de bloc.

### Le balisage de code python

Pour faciliter la relecture de code python au déficient visuel, le forPython peut ajouter des  balises de commentaire en fin des blocs indentés.
Du genre: # end if, # end class, # end def, etc...

Pour ce faire, utilisez la commande du menu affichage, balisage de code, ajouter les balises de fin de bloc.

Pour retirer ces balises et revenir à l'affichage classique de code python, utilisez la commande affichage, balisage de code, retirer les balises de fin de bloc.

Une commande existe également pour ajuster  l'indentation à partir des balises de fin de bloc que vous auriez tapé vous-même, mais n'utilisez cette fonctionnalité qu'avec prudence car il existe des particularité avec les else en python qui peuvent causer une indentation erronée.

Notez également que lorsque du code est sélectionné, les commandes ci-dessus agissent sur cette sélection, sinon, sur tout le document.

### Le collage intelligent de code python

Dans le menu Edition, type de collage, vous sont proposé des choix de type de comportement en cas de collage de texte.
Nous avons:

*  Collage simple de texte: le texte sera collé tel quel sans aucun formattage;
*  Collage de code python;: le texte à collé sera formatté dans ses indentation et ses retours à la lignes pour convenir au code à l'emplacement du collage;
*  Collage classique de 6pad++: le texte à collé sera formatté suivant le comportement standard de 6pad++ avant le collage.

Chaque changement de mode de collage sera  conservé est restauré au redémarrage du 6pad++.

### La recherche et remplacement avancée

Dans le menu Edition, recherche et remplacement avancé, vous est proposé l'exécution d'une boîte de dialogue vous permettant de faire des recherches multicritères prenant en compte, les onglets ouvert, les classes, fonctions et sélection.
Mais également, le sens de la recherche, le type de recherche, le respect de la cass ou non, etc.

Ce type de recherche vous est recommandé pour les éventuelles refactorisation dans le code python.

### L'insertion/génération de code python

Dans le menu python, insertion, vous sont proposés des moyens de générer du code python rapidement.
A savoir:

* Insérer une instruction d'en-tête de fichier
* insérer un import
* insérer une nouvelle fonction
* insérer une nouvelle classe
* insérer une référence à un fichier

### L'exécution de code

Dans le menu python, exécution, vous sont regroupés les commandes d'exécutions que sont:

* exécuter le module qui permet d'exécuter le module entier ou la partie du module couramment sélectionnée.
* exécuter le projet: qui n'apparaît que lorsqu'un projet est ouvert.

### La complétion de mots clé ou complétion de code

La complétion de code est une fonctionnalité qui évite à l'utilisateur de faire des aller et retour dans la documentation.
Elle se déclenche par le raccourci CTRL+J ou menu python, complétion de code.
Elle affiche une liste de mots clé que vous pouvez choisir pour compléter le mot dont vous avez tapé les premières lettres sous le curseur

Les propositions sont contextuelles. C'est-à-dire qu'elles s'adaptent à ce qu'il ya ou n'y a pas sous le curseur.
C'est ainsi que:

* lorsque le curseur est après le mot clé import, il vous est uniquement proposé un ensemble de modules et de classe disponibles dans l'interpréteur actuellement sélectionné.
* lorsque le curseur est après un point ou directement sur les lettres après un point, il vous est proposé la liste des membres de la classe ou l'objet dont le nom se trouve avant le point;
* lorsque le curseur est au début d'une expression ou après un caractère neutre il vous est proposé une liste comportant les mots clés du langage python, les noms des classes, fonctions et variables déjà créés dans le document courant, les membres des imports déjà réalisés dans le document courant, etc...

### La définition de mot clé

Tout comme la complétion de code, elle évite de faire des aller et retour dans la documentation.
C'est une fonctionnalité qui affiche l'aide documentaire pour le mot clé sous le curseur dans la fenêtre console du 6pad++.
Elle se déclenche par le raccourci CTRL+I, ou menu python, définition de mot clé.
Vous pourrez ainsi afficher l'aide pour:

* les nom de modules;
* les noms de classes;
* les membres de classes;
* les noms de fonctions;
* les noms de variables.

### La compilation de code ou création d'exécutable

Avant de lancer cette commande, vous devez au préalable sélectionner un interpréteur dans lequel vous avez installé le module py2exe.
Elle se trouve dans le menu python, Créer un exécutable avec py2exe.

Lorsqu'elle est exécutée un traitement sera effectué qui aboutira à un message dans la fenêtre console de 6pad++.
En cas de succès, il sera créé à la racine du projet ou dans le dossier contenant le fichier à partir duquel l'exécution a été lancé un sous-dossier nommé "dist" qui contiendra l'exécutable et toutes les dll associées.

### L'exécution de commandes pip

Vous devez avoir pip installé dans la version de python que vous utilisez.
Dans le menu python, exécuter une commande.

### Les aménagements d'accéssibilité

Le forPython cré un menu Accessibilité sur la barre de menu du 6pad++.

Comme commande, ce menu contient:

* Activer la synthèse vocale: pour activer ou désactiver la synthèse vocale. Utile pour des mal-voyant ou des voyant ne voulant pas ou n'ayant pas de synthèse vocale.
* Activer la lecture du niveau d'indentation seulement si changement: qui lorsque activé fait dire automatiquement le niveau d'indentation de la nouvelle ligne si celui-ci est différent du niveau d'indentation de l'avant dernière ligne sur laquelle on était.
* lire le nom du bloc courant: qui est une commande de repérage
* lire le nom de l'interpréteur courant
* lire le niveau d'indentation courant

On y trouve également les menu de lecture de l'en-tête de ligne.
Ce sont des menus qui active ou désactivent des lectures particulières lorsqu'on se déplace de ligne en ligne dans le document.
Il représentent des modes entre lesquels on peut basculer par le raccourci CTRL+SHIFT+L.
Il s'agit des modes suivants:

Ne rien dire
Dire les numéros de ligne
Dire les indentations
Dire les numéros de ligne et les indentations
dire les niveaux
Dire les numéros de ligne et les niveaux

### La personnalisation de raccourcis clavier

Dans le menu outils, Raccourcis clavier se trouvent des commandes de personnalisation des raccourcis clavier de menu.

En validant sur le menu "Gestion des raccourcis clavier" ou par le raccourci CTRL+M, vous ferez afficher une boîte de dialogue dans laquelle vous seront listés tous les raccourcis clavier liés aux menus de l'interface du 6pad++.

Par le menu contextuel déclenché sur un élément de la liste, vous pourrez:

* modifier un raccourcis clavier
* Restaurer le raccourcis clavier d'origine;
* rechercher dans la liste des raccourcis clavier.

### La gestion de versions multiples à un document

Le forPython vous permet de garder une version à un document et de le restaurer si besoin est.

Dans le menu fichier, versions de document, vous avez un ensemble de commandes vous servant à gérer les versions au document courant.
A savoir:

* sauvegarder une nouvelle version
* sauvegarder le texte courant dans une ancienne version
* remplacer le texte courant par celui d'une ancienne version
* afficher le texte d'une ancienne version dans un nouvel onglet
* supprimer une ancienne version sauvegardée.

### L'aide au codeur

Le forPython regroupe un ensemble de fichier d'aide au codeur dans le menu aide.
A savoir:

* L'aide de l'extension forPython: où vous sont donnés des directives quant à l'emploi de cette extension.
* l'aide du langage python: qui regroupe les fichiers chm trouvés dans tous les interpréteurs reconnus sur l'ordinateur de l'utilisateur.

## Les fonctionnalités de gestion de projet python

Le forPython se déclenche lors de l'ouverture des fichiers python isolés, mais peut également ouvrir des projets python et offrir des moyens de les monitorer.

### Louverture de projets python

Le forPython peut ouvrir:

* de nouveau projets python (menu fichier, nouveau, projet)
* un projet en désignant son dossier (menu fichier, ouvrir un projet)
* un projet récent (menu fichier, projets récents)

A l'ouverture d'un projet, si c'est la première fois, il sera demandé de déterminer:

* le nom du projet;
* le type de projet
* le fichier de démarrage du projet.

Un fichier project.pyproj est créé à la racine du dossier du projet contenant ces informations qui sont sensé être utilisées plus tard, lors des exécution et des compilations par exemple.

Lorsqu'un projet python est ouvert: 

* son nom apparaît sur la barre de titre de 6pad++;
* il apparaît le menu "projet" sur la barre des menus de 6pad++;
* tous les modules python trouvés dans son dossier sont ouvert dans des onglets différents.

### La sauvegarde de projet python

Vous pouvez en quelques clicks sauvegarder l'ensemble du projet python ouvert.
Dans le menu projet, sauvegarde du projet se trouvent deux commandes:

* paramètres de sauvegarde du projet: qui vous servira à déterminer les conditions des sauvegardes;
* lancer la sauvegarde du projet: qui vous servira à exécuter la sauvegarde.

Notez également que dans le menu fichier, enregistrer le projet sous, vous pouvez créer une copie du projet vers un emplacement que vous désignerez.

### L'exécution et la compilation de projet

Lorsqu'un projet est ouvert, apparaissent des éléménts de menu liés à l'exécution et la compilation de projet dans le menu python.

### L'exploration et la gestion des fichiers d'un projet python

Vous pouvez explorer les fichiers principaux dans un projet python en faisant CTRL+T ou menu projet, Explorateur de projet.

Dans l'arborescence qui s'ouvre, utilisez le menu contextuel pour découvrir les possibilités qui vous sont offertes pour chaque élément de cette arborescence.


