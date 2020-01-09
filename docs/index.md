# Aide

## Présentation de l'outil

Geocontrib est une application web destinée à éditer de manière collaborative une base de données sous la forme de
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
d’un projet. Chaque signalement est attaché à un projet et un type de signalements particulier.

### Type de signalements

Un type de signalements correspond à une modélisation particulière (pour un contexte métier particulier) des 
signalements :
* un type de géométrie donné : point, ligne ou polygone
* des champs spécifiques déclarés par le créateur du type de signalements (ces champs s'ajoutent aux champs 
obligatoires) que l'on retrouve pour tous les types de signalements, à savoir le titre, la description et le statut du 
signalement.

Chaque type de signalements est également caractérisé par une couleur qui est utilisé pour la présentation des 
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

L'application est développée en Python à l'aide de la bibliothèque Django.
Elle alimente une base de données PostgreSQL/PostGIS.


## Interface homme-machine de l'application

### Page d'accueil de l'application

La page d'accueil de l'application contient :
* un bandeau horizontal qui contient :
  * le logo et le nom de l'application (cliquable pour revenir à la page d'accueil de l'application depuis n'importe 
  quelle autre page),
  * si aucun utilisateur n'est connecté : un bouton "Se connecter" permettant à l'utilisateur de 
  s'authentifier,
  * si un utilisateur est connecté : le nom de l'utilisateur courant et un bouton de déconnexion. Un clic sur le nom de 
  l'utilisateur renvoie vers sa page "Mon compte"
* la liste des projets existants avec une courte description et quelques indicateurs. Un clic sur un projet renvoie 
vers la page d'accueil de ce projet si l'utilisateur courant est habilité à le consulter. Dans le cas contraire un 
message d'erreur lui est présenté ;
* un bouton de création d'un nouveau projet (présent uniquement pour les utilisateurs ayant le rôle de Gestionnaire 
métier).

### Menu d'un projet

Lorsque l'utilisateur courant est entré dans un projet un menu supplémentaire apparaît dans le bandeau horizontal 
d'en-tête. Il donne accès aux principales sous-pages du projet :
* Page d'accueil du projet ;
* Page de consultation des signalements sous forme d'une carte ou d'une liste ;
* Page d'administration des fonds cartographiques (uniquement pour les administrateurs du projet et les utilisateurs 
ayant des droits supérieurs) ;
* Page d'administration des droits des utilisateurs pour ce projet (uniquement pour les administrateurs du projet et 
les utilisateurs ayant des droits supérieurs).

Ce menu identifie également le niveau d'autorisation de l'utilisateur courant par rapport au projet courant :
* Utilisateur anonyme : indique que l'utilisateur courant n'est pas connecté ;
* Utilisateur connecté : indique que l'utilisateur est connecté mais n'a pas d'autorisation spécifique sur ce projet ;
* Contributeur : indique que l'utilisateur peut saisir des signalements et écrire des commentaires ;
* Modérateur : indique que l'utilisateur peut publier des signalements ;
* Administrateur projet : indique que l'utilisateur peut créer des nouveaux types de signalements, paramétrer les fonds 
cartographiques et administrer les niveaux d'autorisation des autres utilisateurs sur ce projet.

### Page d'accueil d'un projet

La page d'accueil d'un projet contient les éléments suivants :
* Un rappel des informations descriptives du projet dans la partie haute :
  * Titre,
  * Description,
  * Illustration,
* La liste des types de signalements du projet. Un pictogramme indique le type de géométrie de chaque type de 
signalement. Un clic sur un type de signalements renvoie vers sa page de description ;
* Une cartographie des signalements existants (uniquement ceux que l'utilisateur courant est habilité à consulter). Un 
clic sur cette carte renvoie vers la page de consultation des signalements sous forme de carte ou de liste ;
* Les derniers signalements et commentaires du projet. Un clic sur un signalement ou un commentaire renvoie vers la 
page de consultation du signalement associé ;
* Les caractéristiques techniques du projet dans la partie basse :
  * Délais d'archivage et de suppression automatiques des signalements,
  * Visibilité des signalements publiés et archivés en fonction des autorisations des utilisateurs,
  * Modération du projet.

Au-delà de ces informations, cette page propose également des actions activées en fonction du rôle de l'utilisateur 
courant par rapport au projet :
* un bouton d'édition des caractéristiques du projet en haut à droite (pour les 
administrateurs du projet) ;
* un bouton d'abonnement aux évènement du projet en haut à droite (pour les utilisateurs connectés membres du projet) ;
* un bouton de création d'un nouveau type de signalements sous la liste des types de signalements (pour les 
administrateurs du projet) ;
* un bouton de création d'un nouveau signalement en face de chaque type de signalements (pour les contributeurs du 
projet).

### Page d'un type de signalements

La page de description d'un type de signalement (accessible via la page d'accueil de son projet) présente les 
informations suivantes :
* Les caractéristiques du type de signalements :
  * Son titre,
  * Son type de géométrie,
  * Les champs personnalisés.
* Les derniers signalements créés pour ce type. Un clic sur un signalement renvoie vers la  page de consultation du 
signalement associé.

Au-delà de ces informations, cette page propose également des actions spécifiques :
* Voir tous les signalements : renvoie vers la page de consultation des signalements du projet ;
* Ajouter un signalement : création d'un signalement de ce type. Cette fonction n'est active que pour les contributeurs 
et les utilisateurs avec un niveau d'autorisation supérieur ;
* Import de signalement : création de signalements par l'import d'un fichier GeoJSON conforme au modèle de données
spécifique du type de signalements. Cette fonction n'est active que pour les contributeurs et les utilisateurs avec un
 niveau d'autorisation supérieur ;
* Export des signalements : enregistrement des signalements du type de signalements courant sous la forme d'un fichier 
GeoJSON. Seuls les signalements dont le statut est "publié" sont exportés.

### Page de consultation des signalements

La page de consultation des signalements d'un projet propose 2 vues (par l'intermédiaire des pictogrammes en haut de la 
page) :
* une vue cartographique :
  * présentation de l'ensemble des signalement visibles de l'utilisateur (dépend de ses autorisations par rapport au 
  projet). L'administrateur du projet peut consulter les signalements archivés alors que ce n'est pas systématiquement 
  le cas pour les autres types d'utilisateurs,
  * possibilité de zoomer et de se déplacer dans la carte,
  * consultation des caractéristiques principales d'un signalement dans une petite infobulle à l'aide d'un simple clic,
  * dans cette info-bulle, le clic sur le titre renvoie vers la fiche détaillée du signalement,
  * toujours dans cette info-bulle, le clic sur le type de signalements renvoie vers la fiche détaillée du signalement.
* une vue tabulaire paginée :
  * tri par ordre chronologique inverse (les signalements les plus récents sont affichés en premier),
  * présentation des caractéristiques principales : statut (représenté par un pictogramme), type de signalements, titre, 
  et date de dernière modification,
  * le clic sur le titre renvoie vers la fiche détaillée du signalement,
  * le clic sur le type de signalements renvoie vers la fiche détaillée du signalement.

Chacune d'entre elles propose un bloc "Filtres" permettant à l'utilisateur de réduire le nombre de signalements à ceux 
qu'il recherche :
* filtre sur le type de signalements ;
* filtre sur le statut des signalements ;
* filtre textuel recherchant la chaîne de caractères saisie par l'utilisateur dans le titre des signalements

### Page de consultation d'un signalement

La page de consultation d'un signalement présente les informations suivantes :
* L'ensemble des attributs du signalement ;
* Les dates d'archivage et de suppression automatiques (si de tels délais ont été configurés au niveau du projet) ;
* la localisation sur une carte ;
* Les liaisons avec d'autres signalements (les liaisons sont de quatre types : doublon, remplace, est remplacé par, 
dépend de) ;
* Les pièces jointes du signalement ;
* Le fil d'activité et les commentaires du signalement.

Cette page propose également des actions activées en fonction des autorisations de l'utilisateur :
* Modifier le signalement via un pictogramme en haut à droite de la page (uniquement pour son auteur) ;
* Supprimer le signalement via un pictogramme en haut à droite de la page (uniquement pour son auteur) ;
* Ajouter un commentaire (uniquement pour les contributeurs).

### Page d'administration des fonds cartographiques

La page d'administration des fonds cartographiques est un formulaire permettant aux adminitrateurs du projet de :
* Déclarer l'ensemble des couches de données qui seront utilisées dans les différentes interfaces cartographiques du 
projet. Ces couches servent uniquement de fonds de carte afin d'aider à la localisation des signalements créés dans 
l'application.
* Ces couches peuvent être de deux types : WMS ou TMS ;
* Elles peuvent être réordonnées à l'aide du champ `Position` ;
* Si aucune couche n'est configurée, une couche configurée par défaut au niveau de l'application est alors affichée 
dans les interfaces cartographiques.

cf. [Fonds cartographiques](basemaps.md) pour des informations détaillées sur la configuration d'une couche.

### Page d'administration des droits des utilisateurs

La page d'administration des droits des utilisateurs est un formulaire permettant de modifier le niveau 
d'autorisation de chaque utilisateur de l'application pour le projet courant.

4 niveaux d'autorisation sont gérés au niveau du projet :
* Utilisateur connecté : aucun privilège particulier n'est accordé à l'utilisateur ;
* Contributeur ;
* Modérateur ;
* Administrateur du projet.

cf. [Utilisateurs et autorisations](users.md) pour des informations détaillées sur ces différents niveaux 
d'autorisation.
