# Mode déconnecté

Le mode déconnecté est proposé dans l'application depuis sa version 2.0. Il permet d'utiliser l'application lors de déplacements de terrain, et de prolonger la saisie et l'enregistrement de signalements y compris dans des zones non couvertes par les données mobiles.

Lorsque la connexion est perdue, l'utilisateur peut continuer à naviguer dans l'application, à condition que du cache ait été généré au préalable.

Il peut saisir des signalements via les formulaires de création. A l'enregistrement, il est informé d'une erreur de connexion au serveur. Sur la page d'accueil, le nombre de modifications en attente est indiqué. Lorsque la connexion est rétablie, un bouton _"Envoyer au serveur"_ lui permet d'enregistrer ses nouveaux signalements.

Toutes les fonctionnalités ne sont cependant pas conservées lorsque l'on est déconnecté.

### Fonctionnalités suspendues en mode offline

* Envoyer une pièce jointe ;
* Ajouter un commentaire à un signalement ;
* Exporter les données d’un type de signalement ;
* Importer un json dans un type de signalement ;

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
