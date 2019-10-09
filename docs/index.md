# Aide

## Présentation de l'outil

Collab est une application web destinée à éditer de manière collaborative une base de données sous la forme de
contributions géolocalisées et de commentaires. En utilisant un système de commentaires, de notifications et de 
modération des contributions elle cherche à renforcer des communautés d'utilisateurs autour de projets de 
constitution ou de qualification de leurs bases de données géographiques.

Elle a été conçue pour fonctionner aussi bien sur du matériel sédentaire que sur des terminaux mobiles (dans des 
navigateurs internet modernes).


## Notions importantes

### Projet

Un projet constitue l'application de l’outil de signalement pour un contexte métier / un usage particulier.
Chaque projet est destiné à une communauté d'utilisateurs particulières, de droits d'accès spécifiques et est articulé 
autour de types de projets qui lui sont propres.

Le champ des applications possibles est vaste. Quelques exemples illustratifs :
* publier les projets de travaux sur la voirie dans le cadre de l'article L49 du code des postes et des communications 
électroniques ;
* recette d'une base de données géographiques ;
* création d'une base de données collaborative sur la localisation d'équipements ;
* recueil de commentaires sur base cartographique d'un projet d'aménagement ;
* recueil des besoins de mise à jour du PCRS (Plan de Corps de Rue Simplifié).

Chaque projet possède des caractéristiques propres qui ont un impact sur les droits des utilisateurs :
* chaque utilisateur peut posséder un rôle différent pour chaque projet : administrateur du projet, modérateur, 
contributeur ou aucun rôle particulier ;
* la visibilité des signalements publiés et archivés peut être modulée pour chaque projet ;
* la modération peut activée/désactivée pour chaque projet.

### Signalement

Un signalement est une information géolocalisée décrivant un objet géographique porté à la connaissance des usagers 
d’un projet. Chaque signalement est attaché à un projet et un type de signalement particulier.

### Type de signalement

Un type de signalement correspond à une modélisation particulière (pour un contexte métier particulier) des 
signalements :
* un type de géométrie donné : point, ligne ou polygone
* des champs spécifiques déclarés par le créateur du type de signalement (ces champs s'ajoutent aux champs obligatoires)
que l'on retrouve pour tous les types de signalement, à savoir le titre, la description et le statut du signalement.

Chaque type de signalement est également caractérisé par une couleur qui est utilisé pour la présentation des 
signalements sur les cartes.

### Statut d'un signalement

Chaque signalement possède un statut indiquant son état en terme de publication :
* brouillon : signalement non publié. Permet au créateur du signalement d'éditer progressivement sur un signalement 
avant de le publier ou de demander sa publication ;
* en attente de publication : statut d'un signalement dont l'auteur a demandé sa publication (uniquement si le projet 
est modéré) ;
* publié : donne la visibilité la plus large possible au signalement ;
* archivé : correspond à un signalement obsolète mais que l'on souhaite toutefois conservé en base.

La liste ci-dessus est donnée dans l'ordre logique du cycle de vie d'un signalement.
Modération

### Commentaire

À l’image de ce qui existe sur les outils en ligne de gestion de tickets (Github et Redmine par exemple) chaque 
signalement peut être commenté par son auteur et par les autres usagers du projet afin de permettre l’amélioration de 
la base de données de manière collaborative. Chaque commentaire peut-être être accompagné de pièces jointes.

### Pièce jointe

Il est possible d'associer un document numérique à un signalement ou à un commentaire. Typiquement, il pourra s'agir 
d'une photographie de terrain, d'une copie d'un arrêté. Tout document permettant de préciser les informations portées 
par le signalement peut être utilisé. Dans certains cas, la géolocalisation présente dans une photographie (tags EXIF) 
peut être utilisée pour positionner le signalement.

### Évènements et notifications

La modification d'un signalement, son changement de statut, l'ajout d'un commentaire sont enregistrés en base de données
pour :
* mettre à jour la liste des évènements qui apparaît dans la fiche du signalement dans la rubrique "Activité et 
commentaires" ;
* envoyés des notifications par messages électroniques aux modérateurs, administrateurs ainsi que les autres 
utilisateurs qui se sont abonnés au projet.


## Architecture

## Consulter un projet

### Consulter les signalements
### Télécharger les signalements
### Être notifié des changements

## Contribuer à un projet

### Créer un signalement
### Commenter un signalement
### Créer un lien entre deux signalements

## Administrer un projet

### Créer un nouveau projet
### Ajouter un nouveau type de signalement
### Gérer les autorisations des utilisateurs
### Créer un type de signalement
### Importer des données

## Réexploiter une couche de signalement

## Administrer l'outil

### Créer un utilisateur

### Paramétrer l'outil

## Statuts et cycle de vie des signalements

Brouillon :
* ce statut permet à son auteur de commencer à saisir un signalement et de le sauvegarder afin de le finaliser plus tard (lorsqu'il aura récolté des informations complémentaires par exemple)
* statut du signalement à sa création
* peut être rebasculé dans ce statut par son auteur, un modérateur ou un administrateur du projet
* seuls l'auteur du signalement et les super utilisateurs Django peuvent consulter un signalement avec ce statut et réaliser des actions sur un signalement avec ce statut

En attente de publication :
* ce statut n’existe pas pour un projet sans modération
* peut être basculé dans ce statut par son auteur ou un administrateur
* seuls l'auteur du signalement, les modérateurs du projet, les administrateurs du projet et les super-utilisateurs Django peuvent consulter un signalement avec ce statut

Publié :
* peut être basculé dans ce statut par un modérateur ou un administrateur du projet
* peut être rebasculé dans ce statut par son auteur uniquement lorsque le projet est sans modération
* l'utilisateur courant peut avoir accès à un signalement publié si son niveau d'autorisation est au moins aussi haut que le paramètre du projet "Visibilité des signalements publiés"

Archivé :
* peut être basculé dans ce statut par son auteur, un modérateur ou un administrateur du projet (uniquement à partir de l’état publié)
* est également basculé dans ce statut de manière automatique par l’outil lui-même lorsque la date d’archivage automatique est dépassée
* l'utilisateur courant peut avoir accès à un signalement publié si son niveau d'autorisation est au moins aussi haut que le paramètre du projet "Visibilité des signalements archivés"