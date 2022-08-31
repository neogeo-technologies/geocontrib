# Installation GeoContrib couplée à une plateforme IDGO

## Authentification des utilisateurs

Dans le cadre d'une installation de GeoContrib couplée à une plateforme de données IDGO, le système d'authentification de GeoContrib utilise le CAS d'IDGO.

Les utilisateurs doivent avoir un compte dans la plateforme de données IDGO. Une fois connecté dans IDGO, à leur première connexion sur l'application GéoContrib, les utilisateurs sont ajoutés dans la base utilisateurs de GéoContrib.

Les informations récupérées sont les suivantes :
* Nom d'utilisateur (login IDGO)
* Nom de famille
* Prénom
* Email

Par défaut, les utilisateurs sont ajoutés dans la base utilisateurs de GeoContrib avec le statut "Actif". Aucune autre permission ne leur est accordée. S'ils doivent évoluer vers des statuts de "Gestionnaire métier" ou de "Super Utilisateur" il faut qu'un autre super utilisateur leur accorde ces nouveaux droits.

Une fois leur compte créé dans la base utilisateur, il est désormais possible de leur accorder des rôles de connexion pour chacun des projets. Depuis le site, dans la page Membres du projet, les utilisateurs inscrits peuvent se voir attribuer les rôles particuliers de Contributeur, Supercontributeur, Modérateur ou Administrateur projet. Sinon, ils auront par défaut le rôle Utilisateur connecté.


## Import de données

Dans le cadre d'une installation couplée avec une plateforme IDGO, les utilisateurs ont la possibilité de charger dans l'application des données déposées sur la plateforme IDGO.

* Il s'agit des ressources pour lesquelles un service OGC WFS a été généré suite à leur publication dans la plateforme. Il doit être possible de les exporter au format Geojson via l'interrogation des flux.
* Les ressources dites "Ressources Beta" dans IDGO ne sont pas concernées par ce plugin.
* Il s'agit des ressources publiées par les organisations pour lesquelles l'utilisateur est membre et/ou contributeur et/ou référent.
* Les ressources ciblées sont ouvertes à tous les utilisateurs (pas de restriction d'accès)
* Les ressources sont issues de datasets "publiés" (et non "privés")

Le détail du fonctionnement de l'import est fourni ici : [Imports et exports de signalements](import_export.md).

---

[Retour à l'accueil](<index.md>)
