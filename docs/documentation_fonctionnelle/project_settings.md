# Configuration d'un projet

Les super-utilisateurs et les gestionnaires métier peuvent accéder à l'outil de création d'un projet via le bouton "Créer un nouveau projet" disponible sur l'accueil de l'application.

## Paramètres de base

* Titre : titre du projet tel qu'il apparaîtra aux utilisateurs.
* Description : description permettant de détailler l'objectif, la thématique etc. du projet. Depuis la version 4.0.0, l'administrateur du projet peut rédiger une description mise en forme en format Markdown afin d'y ajouter des liens cliquables et une mise en page spécifique.
* Illustration du projet : l'administrateur peut choisir une image en cliquant sur "Sélectionner une image". Cette image apparaitra pour tous les utilisateurs.

## Visibilité

L'administrateur peut définir deux niveaux de visibilité de son projet :

* Visibilité des signalements publiés : le niveau d'utilisateur choisi sera le niveau minimum requis de l'utilisateur pour accéder aux signalements publiés de ce projet. En dessous de ce niveau, si un utilisateur clique sur le projet, un message l'avertira que le projet n'est pas accessible pour lui. Il ne pourra donc voir que le titre, la description et l'image du projet sur la page d'accueil de GéoContrib. L'administrateur a le choix entre : utilisateur anonyme, utilisateur connecté et contributeur.

* Visibilité des signalements archivés : le niveau d'utilisateur choisi sera le niveau minimum pour voir les signalements ayant le statut "Archivé". On peut ainsi restreindre de façon différente l'accès aux signalements publiés et aux signalements archivés. Les utilisateurs qui n'ont pas accès aux signalements archivés auront quand même accès au projet et aux signalements publiés. L'administrateur a le choix entre : utilisateur anonyme, utilisateur connecté, contributeur et administrateur.

Il est important de noter que les super-utilisateurs auront accès à tous les signalements de tous les projets quel que soit leur rôle dans le projet.

## Paramètres avancés

Les paramètres avancés sont constitués de cases à cocher. Si la case est cochée, le paramètre est activé.

* Modération : si ce paramètre est activé, le projet devient modéré - Cf. [Modération des projets](moderation.md)
* Est un projet type : si ce paramètre est activé, le projet sera ajouté aux modèles - Cf. [Modèle de projet](project_template.md)
* Génération d'un lien de partage externe : si ce paramètre est activé, un lien sera acessible à l'administrateur du projet qui lui permettra de partager le projet de façon isolée - Cf. [Partage d'un projet en externe](project_sharing.md)
* Mode d'édition rapide des signalements ; si ce paramètre est activé, les contributeurs et niveaux supérieurs pourront accéder à un mode d'édition rapide qui permet de modifier un signalement directement sur sa page de détail - Cf. [Edition des signalements - Mode d'édition rapide](feature_editing.md)
* Configuration du parcours de signalements : ce paramètre permet de choisir le filtre et le tri par défaut du parcours de signalements. La liste déroulante du filtre comporte deux options : "désactivé" (aucun filtre n'est appliqué) et "Type de signalement" (la liste sera filtrée selon le type de signalement du signalement sur lequel a cliqué l'utilisateur). La liste déroulante du tri comporte deux options : "Date de modification" (tri pat date de dernière modification) et "Date de création" - Cf. [Parcourir une liste de signalements](browse_through_list_of_features.md)

## Niveau de zoom maximum de la carte

Une règle permet à l'administrateur de sélectionner le niveau de zoom maximum de la carte. C'est-à-dire que si le niveau de zoom est réglé à 1: 250 000, les utilisateurs ne pourront pas zoomer au delà de 1:250 000 et ainsi créer des signalements de forme moins détaillée. Si l'administrateur ne souhaite pas personnaliser ce paramètre, il peut laisser le niveau de zoom par défaut (1:150) qui est le niveau le plus élévé possible.

---

[Retour à l'accueil](<index.md>)
