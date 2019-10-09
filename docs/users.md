Utilisateurs et autorisations

Rôles / Profils attribuables par projet :
* Contributeur
* Modérateur
* Administrateur projet 

Autres profils non spécifiquement associés à un projet :
* Super utilisateur
* Gestionnaire métier
* Utilisateur connecté (utilisateur authentifié)
* Utilisateur anonyme (utilisateur sans compte ou non authentifié)


## Super utilisateur

Un super-utilisateur peut :
* Se connecter à l'interface d'admin de Django ;
* Donner les rôles suivants n'importe quel utilisateur :
  * Super utilisateur,
  * Gestionnaire métier.


## Gestionnaire métier

Un gestionnaire métier peut :
* Créer de nouveaux projets

Le créateur d'un nouveau projet en devient automatiquement administrateur projet du projet en question. 


## Utilisateur connecté

Un utilisateur connecté qui peut avoir accès à un projet peut :
* S'abonner aux notifications du projet


## Contributeur

Un contributeur peut :
* Créer des signalements dans les projets dont il est contributeur
* Créer des commentaires dans les projets dont il est contributeur
* Changer le statut des signalements dont il est l'auteur
* Modifier les attributs des signalements dont il est l'auteur
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
* archivé -> en attente de publication (automatique si le projet est modéré et que le signalement a été édité par son 
auteur)


## Modérateur

Un modérateur a les droits d'un contributeur ainsi que des droits supplémentaires.
Un utilisateur peut devenir modérateur d'un projet uniquement si le projet est modéré.

Il peut :
* Changer le statut des signalements, y compris pour ceux dont il n'est pas l'auteur
* Modifier les attributs des signalements, y compris pour ceux dont il n'est pas l'auteur
* Ajouter et supprimer des pièces jointes pour les signalements, y compris pour ceux dont il n'est pas l'auteur

Changements de statuts réalisables par un modérateur :
* publié -> archivé
* publié -> brouillon
* publié -> en attente de publication
* en attente de publication -> publié
* archivé -> publié
* archivé -> brouillon
* archivé -> en attente de publication


## Administrateur projet

Un administrateur projet a les droits d'un modérateur ainsi que des droits supplémentaires.

Il peut :
* Éditer le projet
* Ajouter un nouveau type de signalements au projet
* Modifier les autorisations des utilisateurs du projet
* Configurer les fonds cartographiques utilisés dans les cartes du projet
