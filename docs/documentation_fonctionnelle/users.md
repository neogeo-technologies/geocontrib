# Utilisateurs et autorisations

Autorisations attribuables par projet :
* Utilisateur connecté (utilisateur authentifié)
* Contributeur
* SuperContributeur
* Modérateur
* Administrateur projet

Autorisations indépendantes des projets :
* Super utilisateur
* Gestionnaire métier
* Statut équipe


## Autorisations liées aux projets

### Utilisateur connecté

Un utilisateur connecté qui peut avoir accès à un projet peut :
* S'abonner aux notifications du projet

### Contributeur

Un contributeur peut :
* Créer et supprimer des signalements dans les projets dont il est contributeur
* Changer le statut des signalements dont il est l'auteur
* Modifier les attributs des signalements dont il est l'auteur
* Ajouter des commentaires
* Ajouter et supprimer des pièces jointes pour les signalements dont il est l'auteur
* Supprimer des signalements dont il est l'auteur

Changements de statuts réalisables par un contributeur :
* brouillon -> en attente de publication (si le projet est modéré)
* brouillon -> publié (si le projet n'est pas modéré)
* brouillon -> archivé
* publié -> archivé
* publié -> brouillon
* publié -> en attente de publication (automatique si le projet est modéré et que le signalement a été édité par son
auteur)
* archivé -> publié (si le projet n'est pas modéré)
* archivé -> brouillon
* archivé -> en attente de publication (automatique si le projet est modéré et que le signalement a été édité par son auteur)

### Super Contributeur

Un supercontributeur a les mêmes droits qu'un contributeur, mais il peut interagir avec les contributions des autres utilisateurs comme s'il s'agissait de ses propres contributions, sauf en ce qui concerne la suppression : il ne peut supprimer que les signalements dont il est l'auteur.


### Modérateur

Un modérateur a les droits d'un contributeur ainsi que des droits supplémentaires.
Un utilisateur peut devenir modérateur d'un projet uniquement si le projet est modéré.

Il peut :
* Changer le statut des signalements, y compris pour ceux dont il n'est pas l'auteur si les signalements ne sont pas en brouillon ;
* Modifier les attributs des signalements, y compris pour ceux dont il n'est pas l'auteur si les signalements ne sont pas en brouillon ;
* Ajouter et supprimer des pièces jointes pour les signalements, y compris pour ceux dont il n'est pas l'auteur si les signalements ne sont pas en brouillon.

Changements de statuts réalisables par un modérateur :
* publié -> archivé
* publié -> brouillon
* publié -> en attente de publication
* en attente de publication -> publié
* archivé -> publié
* archivé -> brouillon
* archivé -> en attente de publication

### Administrateur projet

Un administrateur projet a les droits d'un modérateur ainsi que des droits supplémentaires.

Il peut :
* Éditer le projet
* Ajouter un nouveau type de signalements au projet
* Modifier les autorisations des utilisateurs du projet
* Configurer les fonds cartographiques utilisés dans les cartes du projet
* Supprimer tous les signalements


## Autorisations indépendantes des projets

### Super utilisateur

Un super-utilisateur peut :
* Se connecter à l'interface d'admin de Django ;
* Donner les rôles suivants n'importe quel utilisateur :
  * Super utilisateur,
  * Gestionnaire métier.


### Gestionnaire métier

Un gestionnaire métier peut :
* Créer de nouveaux projets

Le créateur d'un nouveau projet en devient automatiquement administrateur projet du projet en question.


### Statut équipe

Un utilisateur avec le statut équipe peut se connecter à l'interface administrateur.
Il accède aux fonctionnalités de l'interface selon les permissions qui lui ont été accordées.
