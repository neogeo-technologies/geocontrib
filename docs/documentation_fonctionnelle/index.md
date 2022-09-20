# Documentation de GéoContrib

## GéoContrib : outil de constitution de bases de données collaboratives

GéoContrib est une application web qui permet à ses utilisateurs de construire ou d'enrichir des bases de données géographiques de façon collaborative. Un système de commentaires permet aux communautés de contributeurs d'interagir sur la donnée et des modérateurs peuvent être choisis pour gérer les contributions.
L'application est conçue pour être utilisée tant sur du matériel sédentaire que sur des terminaux mobiles via le navigateur de son appareil.

Créée en 2019 par Neogeo Technologies sous l'impulsion de la région des Hauts des France, l'application GéoContrib se veut être un outil simple et accessible à tous, géomaticien ou non. 

Les usages de GéoContrib sont très multiples. En effet, l'application peut être utilisée à des fins de création d'une base de données collaborative sur un thème métier spécifique avec un aspect de localisation comme par exemple des relevés de qualité de l'air, de température, etc. ... Les commentaires peuvent aussi être utilisés pour récueillir des avis sur des projets d'aménagement. Enfin, un usage fréquent de GéoContrib est la qualification de bases de données telles que l'occupation du sol.

## Notions importantes

Afin de pouvoir utiliser au mieux GéoContrib, certaines notions sont importante à comprendre.

### Authentification

GeoContrib possède sa propre base utilisateurs, administrable depuis Django par la page "Utilisateurs" grâce à laquelle des utilisateurs peuvent être ajoutés.
L'application GeoContrib peut être couplée avec une plateforme de données Georchestra ou IDGO. Dans ce cas, l'authentification des utilisateurs se fait depuis la plateforme de données, et non plus depuis GeoContrib.

Pour plus de détails sur l'authentification des utilisateurs dans le cadre d'une installation GeoContrib / Georchestra : [GeoContrib et plateforme Georchestra](../../plugin_georchestra/README.md).
Pour plus de détails sur l'authentification des utilisateurs dans le cadre d'une installation GeoContrib / IDGO : [GeoContrib et plateforme IDGO](geocontrib_IDGO.md).

### Projet

Un projet constitue l'application de l’outil de signalement pour un contexte métier / un usage particulier.
Chaque projet est destiné à une communauté d'utilisateurs particulière, a des droits d'accès spécifiques et est articulé autour de types de signalements qui lui sont propres.

Le champ des applications possibles est vaste. Quelques exemples illustratifs :

* publier les projets de travaux sur la voirie dans le cadre de l'article L49 du code des postes et des communications électroniques ;
* recette d'une base de données géographiques ;
* création d'une base de données collaborative sur la localisation d'équipements ;
* recueil de commentaires sur base cartographique d'un projet d'aménagement ;
* recueil des besoins de mise à jour du PCRS (Plan de Corps de Rue Simplifié).

Chaque projet possède des caractéristiques propres qui ont un impact sur les droits des utilisateurs :

* chaque utilisateur peut posséder un rôle différent pour chaque projet : administrateur du projet, modérateur, super-contributeur, contributeur ou aucun rôle particulier ;
* la visibilité des signalements publiés et archivés peut être modulée pour chaque projet ;
* la modération peut activée/désactivée pour chaque projet.

### Signalement

Un signalement est une information géolocalisée décrivant un objet géographique porté à la connaissance des usagers d’un projet. Chaque signalement est attaché à un projet et un type de signalements particulier. Il peut s'agir d'un point, d'un linéaire ou d'une forme polygonale.
Les contributeurs créent des signalements pour collaborer dans un projet.

### Type de signalements

Un type de signalements correspond à une modélisation particulière (pour un contexte métier particulier) de signalements :
* **un nom**
* **un type de géométrie** donné : point, ligne ou polygone
* **des champs personnalisés** déclarés par le créateur du type de signalements (ces champs s'ajoutent aux champs
obligatoires) que l'on retrouve pour tous les types de signalements, à savoir le titre, la description et le statut du signalement. Les champs personnalisés peuvent être de type : booléen, décimal, entier, chaîne de caractères, liste de valeurs, liste de valeurs pré-enregistrées (Cf. [Liste de valeurs pré-enregistrées](list_of_saved_values.md)), texte multiligne ou date. L'administrateur a la possibilité de rendre obligatoire la saisie des champs personnalisés pour les contributeurs via une case à cocher.

Lorsque le type de signalements est créé, il est possible de lui attribuer une symbologie colorée en cliquant sur l'icône en forme de pinceau sur l'accueil du projet. Ainsi, on peut attribuer une couleur à tous les signalements appartenant à un type ou faire varier la couleur des signalement d'un même type selon les valeurs d'un champ personnalisé de type liste de valeurs. Cf. [Symbologie](symbology.md)

Le modèle de données d'un type de signalements peut être modifié tant qu'aucun signalement n'y est associé. En revanche, il est possible pour l'administrateur de modifier la symbologie d'un type de signalements à tout moment.

### Statut d'un signalement

Chaque signalement possède un statut indiquant son état en terme de publication :
* **brouillon** : signalement non publié. Permet au créateur du signalement d'éditer progressivement un signalement avant de le publier ou de demander sa publication à un modérateur ;
* **en attente de publication** : statut d'un signalement dont l'auteur a demandé sa publication (uniquement si le projet est modéré) ;
* **publié** : donne la visibilité la plus large possible au signalement ;
* **archivé** : correspond à un signalement obsolète mais que l'on souhaite toutefois conserver en base.

La liste ci-dessus est donnée dans l'ordre logique du cycle de vie d'un signalement.

### Commentaire

À l’image de ce qui existe sur les outils en ligne de gestion de tickets (Github et Redmine par exemple) chaque signalement peut être commenté par son auteur et par les autres usagers du projet afin de permettre l’amélioration de la base de données de manière collaborative. Chaque commentaire peut être accompagné de pièces jointes (les formats acceptés sont : PDF, PNG et JPEG). 

### Pièce jointe

Il est possible d'associer un document numérique à un signalement ou à un commentaire (les formats acceptés sont : PDF, PNG et JPEG). Typiquement, il pourra s'agir d'une photographie de terrain, d'une copie d'un arrêté ou tout document permettant de préciser les informations portées par le signalement. Dans certains cas, la géolocalisation présente dans une photographie (tags EXIF) peut être utilisée pour positionner le signalement.

### Évènements et notifications

La modification d'un signalement, son changement de statut, l'ajout d'un commentaire sont enregistrés en base de données pour :
* mettre à jour la liste des évènements qui apparaît dans la fiche du signalement dans la rubrique _"Activité et commentaires"_ ;
* envoyer des notifications par messages électroniques aux modérateurs, administrateurs ainsi que les autres utilisateurs qui se sont abonnés au projet.


## Architecture

* **Back-Office Django**

L'application est développée en Python à l'aide de la bibliothèque Django. Les administrateurs Django (super-utilisateurs) bénéficient d'une interface d'administration leur permettant de réaliser un certains nombre de tâche d'administration.

* **Base de données PostgreSQL/PostGIS**

L'application alimente une base de données PostgreSQL/PostGIS. Depuis le BO Django, les super-utilisateurs peuvent configurer des vues PostgreSQL relatives aux signalements créés dans chacun des projets.

Cf. [Accès aux données PostgreSQL/PostGIS](external_access.md)

* **Interface web VueJS**

Depuis la version 2.0 l'interface web utilise la bibliothèque VueJS. Cette bibliothèque permet aux utilisateurs d'utiliser l'application GeoContrib en 'mode déconnecté'.

Cf. [Mode déconnecté](offline_mode.md)

* **Librairies cartographiques**

Les interfaces cartographiques de l'application utilisent la bibliothèque Leaflet. Par ailleurs, un outil de géocodage est disponible sur les cartes interactive de l'application.

Cf. [Géocodage](geocoder.md)


## Interface homme-machine de l'application : parcours utilisateur

L'interface homme machine de l'application GéomContrib se veut être simple et accessible. Ici sont développées les différentes vues et les fonctionnalités qui les constituent.

### Page d'accueil de l'application

La page d'accueil de l'application contient :
* un bandeau horizontal avec :
  * le logo et le nom de l'application (cliquable pour revenir à la page d'accueil de l'application depuis n'importe quelle autre page),
  * si aucun utilisateur n'est connecté : un bouton _"Se connecter"_ permettant à l'utilisateur de s'authentifier,
  * si un utilisateur est connecté : le nom de l'utilisateur courant et un bouton de déconnexion. Un clic sur le nom de l'utilisateur renvoie vers sa page _"Mon compte"_
* un bouton de création d'un nouveau projet (présent uniquement pour les utilisateurs ayant le rôle de Gestionnaire métier ou les super-utilisateurs) cf. [Configuration d'un projet](project_settings.md). Il est aussi possible de créer un projet à partir de modèles. cf. [Projets modèles](project_template.md);
* la liste des projets existants avec un extrait de la description et quelques indicateurs. Un clic sur un projet renvoie vers la page d'accueil de ce projet si l'utilisateur courant est habilité à le consulter. Dans le cas contraire un message d'erreur lui est présenté. Cette liste peut être filtrée par niveau d'autorisation requis pour accéder au projet, par le niveau d'autorisation de l'utilisateur pour le projet ou selon si le projet est modéré ou non. Il est aussi possible de faire une recherche par nom de projet. Une option permettant de rendre visible les projets auxquels l'utilisateur n'a pas accès est aussi possible selon la configuration de l'application (depuis la version 3.0.0).

### Menu d'un projet

Lorsque l'utilisateur courant est entré dans un projet un menu supplémentaire apparaît dans le bandeau horizontal d'en-tête. Il donne accès aux principales pages du projet :
* Page d'accueil du projet ;
* Page de consultation des signalements sous forme d'une carte ou d'une liste ;
* Page d'administration des fonds cartographiques (uniquement pour les administrateurs du projet et les super-utilisateurs) ;
* Page d'administration des droits des utilisateurs pour ce projet (uniquement pour les administrateurs du projet et les super-utilisateurs).

Sur la partie de droite, ce bandeau identifie également le niveau d'autorisation de l'utilisateur courant par rapport au projet courant :
* Utilisateur anonyme : indique que l'utilisateur courant n'est pas connecté ;
* Utilisateur connecté : indique que l'utilisateur est connecté mais n'a pas d'autorisation spécifique sur ce projet ;
* Contributeur : indique que l'utilisateur peut saisir des signalements et écrire des commentaires ;
* Supercontributeur : indique que l'utilisateur peut saisir ou modifier tous les signalements du projet, quelque soit le statut des signalements ;
* Modérateur : indique que l'utilisateur peut publier des signalements ;
* Administrateur projet : indique que l'utilisateur peut administrer le projet, à savoir modifier les paramètres du projet, créer des nouveaux types de signalements, paramétrer les fonds cartographiques et administrer les niveaux d'autorisation des autres utilisateurs sur ce projet.

### Page d'accueil d'un projet

La page d'accueil d'un projet contient les éléments suivants :
* Un rappel des informations descriptives du projet dans la partie haute :
  * Titre,
  * Description,
  * Illustration,
* La liste des types de signalements du projet. Un pictogramme indique le type de géométrie de chaque type de signalement. Un clic sur un type de signalements renvoie vers sa page de description.
* Une cartographie des signalements existants (uniquement ceux que l'utilisateur courant est habilité à consulter). Un clic sur cette carte renvoie vers la page de consultation des signalements sous forme de carte ou de liste ;
* Les derniers signalements et commentaires du projet. Un clic sur un signalement ou un commentaire renvoie vers la page de consultation du signalement associé ;
* Les caractéristiques techniques du projet dans la partie basse :
  * Visibilité des signalements publiés et archivés en fonction des autorisations des utilisateurs,
  * Modération du projet - cf. [Modération d'un projet](moderation.md),
* Selon la configuration de l'application, l'administrateur a aussi la possibilité de copier un lien de partage du projet en externe. Ce lien permet de n'avoir accès qu'au projet partagé et non au reste de l'application GéoContrib. cf. [Projets partagés en externe](project_sharing.md).

Au-delà de ces informations, cette page propose également des actions activées en fonction du rôle de l'utilisateur courant par rapport au projet :

Pour les contributeurs du projet et niveau supérieur :
* un bouton de création d'un nouveau signalement en face de chaque type de signalements ;

Pour les administrateurs de projet :
* un bouton d'édition des caractéristiques du projet en haut à droite ;
* un bouton d'abonnement aux évènement du projet en haut à droite (pour les utilisateurs connectés ayant accès au projet) - cf. [Abonnements](subscription.md);
* des boutons de création d'un nouveau type de signalements :
  * un bouton pour dupliquer un type de signalement existant, situé en face de chaque type déjà créé ;
  * un bouton pour créer un nouveau type de signalement manuellement depuis un formulaire de création, sous la liste des types existants ;
  * un bouton pour créer un nouveau type de signalement depuis un fichier GeoJSON téléchargé, sous la liste des types existants ;
* un bouton de modification de la symbologie, en face de chaque type de signalements ponctuels (pour les administrateurs du projet)- cf. [Editer la symbologie d'un type de signalement](symbology.md) ;
* un bouton permettant de supprimer le type de signalement ;
* un bouton permettant de modifier le type de signalement. Lorsque le type de signalement contient au moins un signalement, cette fonction n'est plus accessible. En effet, modifier la structure du type est impossible sans modifier la structure des signalement déjà présents.


### Formulaire de création / édition d'un type de signalements

Les administrateurs d'un projet (et utilisateur de niveau de permission supérieur) ont la possibilité d'ajouter un type de signalement ou d'éditer un type de signalement (tant qu'aucun signalement n'est créé pour ce type).

Le formulaire d'édition permet de choisir un titre pour le type de signalement, une géométrie, et de définir les données métiers ou champs personnalisés - cf. [Champs personnalisés d'un type de signalement](custom_fields.md).

### Page d'un type de signalements

La page de description d'un type de signalements (accessible via la page d'accueil de son projet) présente les informations suivantes :
* Les caractéristiques du type de signalements :
  * Son titre,
  * Son type de géométrie,
  * Les champs personnalisés du type de signalement.
* Les derniers signalements créés pour ce type. Un clic sur un signalement renvoie vers la page de consultation du signalement associé.

Au-delà de ces informations, cette page propose également des actions spécifiques :
* Voir tous les signalements : renvoie vers la page de consultation _"Liste & Carte"_ des signalements du projet ;
* Ajouter un signalement : création d'un signalement de ce type. Cette fonction n'est proposée que pour les contributeurs et les utilisateurs avec un niveau d'autorisation supérieur ;
* Import de signalement via un GeoSJON ou un CSV : création de signalements par l'import d'un fichier GeoJSON ou CSV conforme au modèle de données spécifique du type de signalements. Cette fonction n'est active que pour les contributeurs et les utilisateurs avec un niveau d'autorisation supérieur ;
* Import de signalement via IDGO : création de signalements par l'import de données issues d'une plateforme IDGO. Cette fonction n'est active que si une plateforme IDGO à été connectée à GéoContrib et uniquement pour les contributeurs et les utilisateurs avec un niveau d'autorisation supérieur ;
* Export des signalements : enregistrement des signalements du type de signalements courant sous la forme d'un fichier GeoJSON. Seuls les signalements que l'utilisateur courant a le droit de consulter sont exportés.

 Cf. [Imports et exports de signalements](import_export.md).

### Page de consultation des signalements 'Liste & Carte'

La page de consultation des signalements d'un projet propose 2 vues (par l'intermédiaire des pictogrammes en haut de la page) :
* **une vue cartographique** :
  * présentation de l'ensemble des signalements visibles de l'utilisateur (dépend de ses autorisations par rapport au projet).
  * possibilité de zoomer et de se déplacer dans la carte,
  * consultation des caractéristiques principales d'un signalement dans une petite infobulle à l'aide d'un simple clic,
  * dans cette info-bulle, le clic sur le titre renvoie vers la fiche détaillée du signalement,
  * toujours dans cette info-bulle, le clic sur le type de signalements renvoie vers la fiche détaillée du signalement.

* **une vue tabulaire paginée** :
  * tri par ordre chronologique inverse (les signalements les plus récents sont affichés en premier),
  * présentation des caractéristiques principales : statut (représenté par un pictogramme), type de signalements, titre, date de dernière modification, auteur du signalement et dernier éditeur,
  * case à cocher, permettant à l'utilisateur courant de sélectionner les signalements dont il est l'auteur (ou tous les signalements s'il est administrateur projet ou super-utilisateur). Il peut choisir entre deux actions (pictogrammes en tête de colonne) : mode suppression (les signalements sélectionnés seront supprimés) et mode édition du statut (le statut des signalements sélectionnés sera édité). Si le mode suppression est activé, l'utilisateur peut sélectionner les signalements qu'il souhaite supprimer et cliquer sur l'icône corbeille en haut à droite pour les effacer. Si le mode édition est activé, l'utilisateur peut sélectionner les signalements dont il souhaite modifier le statut, cliquer sur l'icône crayon en haut à droite et choisir le statut de destination des signalements choisis.
  * le clic sur le titre renvoie vers la fiche détaillée du signalement,
  * le clic sur le type de signalements renvoie vers la fiche détaillée du signalement,

Chacune d'entre elles propose un bloc _"Filtres"_ permettant à l'utilisateur de réduire le nombre de signalements à ceux qu'il recherche :
* filtre sur le type de signalements ;
* filtre sur le statut des signalements ;
* filtre textuel recherchant la chaîne de caractères saisie par l'utilisateur dans le titre des signalements.

**Outils de gestion des signalements**

* Ajout d'un signalement : Depuis cette page, le contributeur peut ajouter un signalement au projet en cliquant sur le bouton représentant un "+". Lui sera ensuite proposé le type de signalement auquel son signalement sera ajouté.
 
A l'aide des cases à cocher permettant de sélectionner les signalements dans la vue liste, plusieurs modes sont disponibles pour effectuer des action sur plusieurs signalements en même temps.

* Edition du statut en masse : l'utilisateur peut modifier le statut de plusieurs signalements. Pour cela, il choisit le mode de sélection "Edition de statut" au dessus du tableau et sélectionne les signalements souhaités. Ensuite, il clique sur le bouton représentant un crayon en haut à droite de la page et choisit le statut à appliquer aux signalements choisis.

* Edition d'attributs en masse : l'utilisateur peut modifier les attributs de plusieurs signalements pouvu qu'ils soient du même type. Pour cela, il sélectionne le mode de sélection "Edition d'attribut" et choisit les signalement pour lesquels il souhaite changer les valeurs des attributs. Lorsqu'il a choisi un premier signalement, il ne pourra plus sélectionner de signalement d'un type différent de celui déjà sélectionné. Lorsque la sélection des signalements est faite, le contributeur doit cliquer sur le bouton représentant un crayon pour en modifier les attributs. Un formulaire sera ensuite affiché à l'utilisateur qui lui permettra de modifier les valeurs des champs personnalisés. A la validation du fomulaire, les valeurs des champs modifiés seront écrasées et remplacées.

* Suppression de signalements en masse : l'utilisateur peut supprimer plusieurs signalements en même temps en choisissant le mode de sélection "Supression de signalement". Il peut alors sélectionner les signalements qu'il souhaite supprimer et cliquer sur le bouton représentant unee corbeille en haut à droite de l'écran. Une pop-up de validation s'affiche pour demander la confirmation de la supression.

Pour ces trois derniers outils, la sélection est possible dans la mesure où le contributeur a le droit d'éditer le signalement). Si le signalement n'est pas sélectionnable, c'est que l'utilisateur n'a pas le droit de le modifier.

Il est désormais possible de parcourir les signalements de la liste obtenue en filtrant et triant la table de la vue liste. - Cf. [Parcourir une liste de signalements](browse_through_list_of_features.md)



### Formulaire de création / édition d'un signalement

Les contributeurs ou de niveau supérieur peuvent ajouter des signalements depuis la page d'accueil, la page d'un type de signalements ou la page d'un signalement à l'aide du pictogramme _"+"_ .

Le formulaire de création / édition permet à l'utilisateur de saisir un nom, un statut, une description ainsi que de renseigner l'ensemble des informations relatives aux champs personnalisés définis pour ce type de signalement. - Cf. [Edition d'un signalement et mode édition rapide](feature_editing.md)

Pour tous les types de signalements, une interface cartographique permet de localiser le signalement. L'utilisateur bénéficie d'une fonction de recherche par adresse (cf.[Géocodage](geocoder.md)) et a la possibilité de jouer sur l'affichage des fonds de carte (cf. [Fonds cartographiques](basemaps.md)) configurés par l'administrateur du projet (ordre des couches, opacités, etc).

Pour localiser un signalements de type ponctuel, l'utilisateur peut également :
* utiliser sa géolocalisation (en autorisant le navigateur à utiliser la localisation) et en cliquant sur le bouton _"Positionner le signalement à partir de votre géolocalisation"_ ;
* utiliser une photographie contenant des informations de localisation (tags EXIF associés à une photographie prise avec un appareil équipé d'un GPS) en cliquant sur le bouton _"Importer une image géoréférencée"_ . L'image sera automatiquement ajoutée en pièce jointe.

Guide d'utilisation des outils de cartographie :

* Pour créer une géométrie, il faut activer l'outil "Dessiner un polygone" (ou un point ou une ligne) qui est représenté par un bouton avec un polygone (ou un point ou une ligne) à droite de la carte. Lorsqu'il est actif, l'outil permet au contributeur de dessiner sa géométrie sur la carte. Dans le cas d'une ligne ou d'un polygone, l'utilisateur place les points qui constiueront les angles de sa géométrie puis, lorsqu'il a terminé de la dessiner, il peut double-cliquer sur le dernier point placé pour terminer son tracé.

* Lorsqu'il a dessiné la géométrie, le bouton "Editer un polygone" (ou un point ou une ligne) apparaît à droite de la carte. Il s'agit d'un bouton représentant un crayon et une feuille. Ce bouton permet d'activer le mode d'édition de la géométrie. Lorsque ce mode est activé, le contributeur peut attrapper les points constituant le pourtour de la géométrie pour en modifier leur placement. 

* Afin de supprimer la géométrie tracée, l'utilisateur peut activer le mode "Suppression du polygone (ou du point ou de la ligne) en cliquant sur le bouton à droite représentant une corbeille. Si ce mode est activé, l'utilisateur peut cliquer sur la géometrie et une pop-up lui demandera s'il souhaite effectivement supprimer la géométrie sélectionnée.

* Depuis la version 4.0.0, il est possible d'accrocher une géométrie à une autre afin de respecter des règles de topolgie et être le plus précis possible dans son tracé. Pour activer le mode d'accrochage de la géométrie, l'utilisateur doit cliquer sur le bouron "Activer l'accrochage aux points" et sa souris sera automatiquement placé sur la géométrie la plus proche de son pointeur pour tracer une géométrie contigüe à une autre.

### Page de consultation d'un signalement

La page de consultation d'un signalement présente les informations suivantes :
* L'ensemble des attributs du signalement ;
* Le statut de publication du signalement (cf. [Statuts des signalements](status.md) pour des informations détaillées sur les différents statuts) ;
* la localisation sur une carte ;
* Les liaisons avec d'autres signalements (cf. [Liaisons entre signalements](featurelink.md) pour des informations détaillées sur ces liaisons) ;
* Les pièces jointes du signalement ;
* Le fil d'activité et les commentaires du signalement.

Cette page propose également des actions activées en fonction des autorisations de l'utilisateur :
* Modifier le signalement via un pictogramme en haut à droite de la page (uniquement pour les utilisateurs ayants les droits) ;
* Supprimer le signalement via un pictogramme en haut à droite de la page (uniquement pour son auteur, les administrateurs de projet ou super utilisateurs) ;
* Ajouter un commentaire (uniquement pour les contributeurs et utilisateurs de niveau supérieur).


### Page d'administration des fonds cartographiques

La page d'administration des fonds cartographiques est un formulaire permettant aux administrateurs du projet de :
* Déclarer l'ensemble des couches de données qui seront utilisées dans les différentes interfaces cartographiques du projet. Ces couches servent uniquement de fonds de carte afin d'aider à la localisation des signalements créés dans l'application.
* Elles peuvent être réordonnées à l'aide du champ `Position` ;
* Si aucune couche n'est configurée, une couche configurée par défaut au niveau de l'application est alors affichée dans les interfaces cartographiques.

cf. [Fonds cartographiques](basemaps.md) pour des informations détaillées sur la configuration d'une couche.

### Page d'administration des droits des utilisateurs

La page d'administration des droits des utilisateurs est un formulaire permettant de modifier le niveau
d'autorisation de chaque utilisateur enregistré dans l'application, pour le projet courant.

5 niveaux d'autorisation sont gérés au niveau du projet :
* Utilisateur connecté : aucun privilège particulier n'est accordé à l'utilisateur, c'est le niveau d'autorisation accordé par défaut ;
* Contributeur ;
* Supercontributeur ;
* Modérateur ;
* Administrateur du projet.

cf. [Utilisateurs et autorisations](users.md) pour des informations détaillées sur ces différents niveaux
d'autorisation.

### Pages statiques du bandeau du bas

Le bandeau du bas propose deux pages statiques _"Mentions légales"_ et _"Aide"_, modifiables par les super-utilisateurs depuis l'interface administrateur Django.

Cf. Plus de détail sur le module des [pages statiques](flatpages.md) et sur leur configuration.
