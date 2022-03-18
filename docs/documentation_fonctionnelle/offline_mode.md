# Mode déconnecté

Le mode déconnecté est proposé dans l'application depuis sa version 2.0. Il permet d'utiliser l'application lors de déplacements de terrain, et de prolonger la saisie et l'enregistrement de signalements y compris dans des zones non couvertes par les données mobiles.

Lorsque la connexion est perdue, l'utilisateur peut continuer à naviguer dans l'application, à condition que du cache ait été généré au préalable.

### Création de signalements

Le contributeur peut saisir des signalements via les formulaires de création. A l'enregistrement, il est informé d'une erreur de connexion au serveur. Sur la page d'accueil, le nombre de modifications en attente est indiqué. Lorsque la connexion est rétablie, un bouton _"Envoyer au serveur"_ lui permet d'enregistrer ses nouveaux signalements.

### Mise en cache des fonds cartographiques

En mode déconnecté, les couches cartographiques mises en cache (et restituées dans les vues Cartes) sont les couches du fond par défaut du projet, c'est à dire le 1er fond de la liste des fonds cartographiques du projet.
L'administrateur du projet doit veiller à proposer un fond par défaut qui soit pertinent par rapport à la saisie de données sur le terrain.

Le contrôle des couches n'étant pas proposé en mode déconnecté, l'utilisateur ne pourra pas interroger un autre fond habituellement disponible dans le projet.

### Fonctionnalités suspendues en mode offline

Toutes les fonctionnalités ne sont cependant pas conservées lorsque l'on est déconnecté :

* Envoyer une pièce jointe ;
* Ajouter un commentaire à un signalement ;
* Exporter les données d’un type de signalement ;
* Importer un json dans un type de signalement ;
* Modifier l'ordre des couches et des fonds cartographiques dans les vues Carte.

### Fonctionnalités maintenues (si mise en cache)

-   Naviguer dans le site et les diverses pages du projet
    -   Page d’accueil
    -   Page Liste & Carte
    -   Filtre possible sur la page Liste & Carte
    -   Page d’un type de signalement
    -   Page d’un signalement
-   Créer un signalement à partir de sa localisation GPS
-   Dessiner un signalement sur la carte
-   Modifier un signalement existant

---

[Retour à l'accueil](<README.md>)
