# Mode déconnecté

Le mode déconnecté est proposé dans l'application depuis sa version 2.0.0. Il permet d'utiliser l'application lors de déplacements de terrain, et de prolonger la saisie et l'enregistrement de signalements y compris dans des zones non couvertes par les données mobiles.

Lorsque la connexion est perdue, l'utilisateur peut continuer à naviguer dans l'application, à condition que les pages consultées aient été mises en cache au préalable.

## Basculer en mode déconnecté

Dès lors que l'utilisateur de GéoContrib perd sa connexion à internet, le mode déconnecté est automatiquement activé. L'utilisateur en est averti par l'apparition d'une icône de réseau barré. De la même manière, si le réseau est détecté à nouveau par l'appareil, GéoContrib basculera en mode connecté et cela est visible par le biais de la disparition de l'icône de réseau barré.

## Fonctionnalités en mode déconnecté

Le mode déconnecté est essentiellement dédié à la contribution en cas de perte de réseau. Ainsi, seuls les outils de contribution et d'édition des signalements seront acessibles entièrement. En effet, la consultation des signalements est possible mais uniquement pour les signalements déjà mis en cache et l'administration des projets et de l'application dans sa globalité ne sont pas disponibles en mode déconnecté.

### Création et édition de signalements

Le contributeur peut saisir des signalements via les formulaires de création et éditer les signalements (ayant été mis en cache au préalable) en mode déconnecté. A l'enregistrement, il est informé d'une erreur de connexion au serveur. Sur la page d'accueil, le nombre de modifications en attente d'être envoyées au serveur est indiqué. Lorsque la connexion est rétablie, un bouton _"Envoyer au serveur"_ lui permet d'enregistrer ses nouveaux signalements.

### Mise en cache des fonds cartographiques

En mode déconnecté, les couches cartographiques mises en cache (et restituées dans les vues Cartes) sont les couches du fond par défaut du projet, c'est à dire le 1er fond de la liste des fonds cartographiques du projet.
L'administrateur du projet doit veiller à proposer un fond par défaut qui soit pertinent par rapport à la saisie de données sur le terrain.

Le contrôle des couches n'étant pas proposé en mode déconnecté, l'utilisateur ne pourra pas interroger un autre fond habituellement disponible dans le projet.

### Fonctionnalités suspendues en mode offline

Toutes les fonctionnalités ne sont cependant pas conservées lorsque l'on est déconnecté :

* Envoyer une pièce jointe ;
* Ajouter un commentaire à un signalement ;
* Exporter les données d’un type de signalement ;
* Importer des signalements dans un type de signalement ;
* Exporter des signalements ;
* Créer un type de signalements ;
* Accéder à la gestion des membres du projet ;
* Accéder à la gestion des fonds de plan ;
* Accéder à l'administration Django.

---

[Retour à l'accueil](<index.md>)
