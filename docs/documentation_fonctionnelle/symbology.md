# Symbologie

L'administrateur du projet a la possibilité d'associer une symbologie à chaque type de signalement. Pour cela, lorsqu'il a créé un type de signalements, il a à sa disposition un bouton pinceau sur la page d'accueil du projet. S'il clique dessus, il est renvoyé vers un formulaire de personnalisation de la symbologie.

## Symbologie par défaut

Pour tous les types de signalements, l'administrateur a la possibilité de choisir une symbologie par défaut. Il peut choisir la couleur dans laquelle les signalements seront affichés sur les cartes. Si le type de signalement est un polygone, il est aussi possible de faire varier l'opacité du remplissage de la géométrie (0% pour un fond transparent et 100% pour un fond complètement opaque).

## Symbologie en fonction d'un champ personnalisé

Le formulaire d'édition de la symbologie permet de faire varier la symbologie en fonction de la valeur d'un champ personnalisé. Il est ainsi possible de paramétrer la symbologie en fonction de :

- une chaîne de caractères : la couleur et l'opacité (dans le cas d'un polygone) varient en fonction de deux options : si la chaîne est renseignée ou si la chaîne est vide. Dans ce cas, la symbologie par défaut ne sera jamais affichée.
- un booléen : la couleur et l'opacité (dans le cas d'un polygone) varient en fonction de deux options : si la case est cochée ou si la case est décochée. Dans ce cas, la symbologie par défaut ne sera jamais affichée.
- une liste de valeurs : la couleur et l'opacité (dans le cas d'un polygone) varient en fonction des options proposées dans la liste. On peut ainsi choisir une couleur pour chaque option de la liste. Dans le cas où aucune option de la liste n'est affichée, la symbologie par défaut sera affichée.

Pour savegarder les modifications, il faut cliquer sur le bouton "Sauvegarder la symbologie du type de signalement".
---

[Retour à l'accueil](<index.md>)
