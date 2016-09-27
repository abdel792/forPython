% Cahier des charges pour l'extension forPython
%
%
1.  Corrigez les bugs des boîtes de dialogues permettant de créer une nouvelle classe, de créer une nouvelle fonction et de faire une recherche avancée;
#.  Dans le menu outils, près ou à l'intérieur  des menus de recensement des versions de python installées, créer le menu "Localiser manuellement une version de python" qui, ouvrira une boîte de dialogue ouvrir pour aller désigner l'exécutable d'une version de python qui ne serait pas trouvée par la boucle de parcours des dossiers de l'ordinateur;
#.  Dans le menu outils, créer le menu à cocher "Vérification automatique de la syntaxe des lignes modifiées", qui activera ou désactivera la vérification automatique de la syntaxe des lignes modifiées;
#.  Dans le menu outils, créer le menu à cocher "Complétion de code- ajouter automatiquement les balises de fin de bloc", qui lors de l'insertion de code, ajoutera selon cette préférence des balises end if, end def, end class, etc;;
#.  Dans le menu "accessibilité", créer le menu à cocher "Lecture du niveau d'indentation seulement si changement", dont le caractère coché n'autorisera la lecture du niveau d'indentation que lorsque le focus se déplacera sur une ligne où ce niveau est différent de celui de la ligne antérieure;
#.  Lors du repérage des versions de python installées, faire également le recensement des fichiers chm d'aide présent dans chaque dossier de python et les afficher comme élément d'un sous-menu au menu aide;
#.  Rendre visible les menus "Compiler avec py2exe" et "Exécuter une commande pip", et simplement les griser en cas d'absence des bibliothèques nécessaires;
#.  Dans le menu "fichier", créer le menu "Enregistrer tout" juste après le menu "Enregistrer sous", qui enregistrera tous les onglets à partir d'une seule commande;
#.  Dans le menu "fichier", créer le menu "Fermer tout sauf l'onglet courant";
#.  Dans le menu "affichage", créer le menu "Propriétés..." qui ouvrira un dialogue des propriétés du document courant;
    Les informations affichées seront pour le document courant:
  le type d'encodage,
  le nombre d'imports,
  le nombre de classes,
  le nombre de propriétés,
  le nombre de méthodes,
  le nombre de fonctions,
  le nombre de lignes,
  le nombre de caractères,
  le pourcentage d'évolution dans le document.
#.  Intersepter et refaire le collage de texte pour une meilleure prise en compte du collage de code indentés provenant d'ailleurs;
#.  Faire l'interdiction du caractère tabulation si on n'est pas en début de ligne;
#.  Faire l'interdiction d'un niveau d'indentation supérieur à plus d'une unité de celui de la ligne précédente;
  Émettre un beep dans ce cas.
#.  Dans le menu python/sélection, Faire des commandes pour:
  Etendre la sélection au bloc parent,
  Réduire la sélection au premier bloc enfant;.
