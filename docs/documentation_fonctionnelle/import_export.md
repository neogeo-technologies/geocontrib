# Import et export de données

GéoContrib permet de créer des signalements via un import de données depuis des sources extérieures mais aussi d'exporter des signalements vers un fichier.

## Création d'un type de signalement et import de données simultanés

Les administrateurs de projets (et utilisateurs avec droits supérieurs) ont la possibilité de créer un type de signalement à partir de la structure de données existantes. Ainsi la structure est dupliquée sous la forme d'un type de signalements avec des champs personnalisés.

### Via un fichier GeoJSON

Depuis la page d'accueil d'un projet, le bouton _"Créer un type de signalements à partir d'un fichier GeoJSON"_ permet à l'utilisateur d'uploader un fichier stocké sur son poste local. Suite au chargement, la structure du fichier est lue et le modèle de données du type de signalement est proposé à l'utilisateur à travers le formulaire d'édition.
L'administrateur peut préciser la géométrie, le titre du type de signalement, et vérifier ou modifier chacun des champs personnalisés.

En bas de page, il peut choisir :
* de créer simplement le type de signalement,
* de créer le type de signalement et d'importer les données du fichier.

### Via un fichier CSV
Depuis la page d'accueil d'un projet, le bouton _"Créer un type de signalements à partir d'un fichier CSV"_ permet à l'utilisateur d'uploader un fichier stocké sur son poste local.
*L'import CSV n'est disponible que pour les géométries POINT.*

**Formatage du fichier**
Le fichier importé doit respecter certaines règles de formatage:
- Séparateurs:
    - Virgules: dans ce cas, les valeurs de tout les champs ne peuvent contenir de virgules.
    - Point-virgules: les valeurs des champs peuvent contenir des virgules.
    - Aucun autre séparateur n'est supporté.
- Champs de coordonnées:
    - Le fichier doit obligatoirement contenir des champs de coordonnées sous la forme de 2 champs: "lon" et "lat"
    - Les coordonnées doivent être au format WGS84 (EPSG 4326).

Tout les champs ne correspondant pas au champs réservés à la construction d'un type de signalement seront listés en tant que champs personnalisés.

### Via une plateforme IDGO

Cette fonctionnalité n'est disponible que pour les installations de GeoContrib couplée avec une plateforme IDGO.

Depuis la page d'accueil d'un projet, le bouton _"Créer un type de signalements à partir du catalogue IDGO"_ permet à l'utilisateur de choisir une ressource appartenant à l'organisation à laquelle il est rattaché dans IDGO. Il clique sur le bouton de lancement de l'import pour générer le type de signalement. Suite au chargement, la structure du fichier est lue et le modèle de données du type de signalement est proposé à l'utilisateur à travers le formulaire d'édition.
L'administrateur peut préciser la géométrie, le titre du type de signalement, et vérifier ou modifier chacun des champs personnalisés.

En bas de page, il peut choisir :
* de créer simplement le type de signalement,
* de créer le type de signalement et d'importer les données du fichier.

## Import de données dans un type de signalements existant

Cette fonction permet d'importer des signalements depuis des données extérieures à GéoContrib dans un type de signalement existant. Elle est disponible depuis la page du type de signalement.

Seuls les utilisateurs qui peuvent créer des signalements (contributeurs et niveaux de droits supérieurs du projet) peuvent utiliser cette fonction.

### Import d'un fichier GeoJSON

Si l'utilisateur souhaite charger un fichier GeoJSON dans un type de signalements existant, il doit dérouler le menu _"Importer des signalements"_ de la page du type de signalements. Il choisit ensuite le fichier de données qu'il souhaite importer dans son explorateur de fichiers et clique sur le bouton _"Lancer l'import"_. Les données sont importées dans le type de signalements.

### Import depuis une plateforme IDGO

Cette fonctionnalité n'est disponible que pour les installations de GeoContrib couplée avec une plateforme IDGO.

Si l'utilisateur souhaite charger des données depuis IDGO dans un type de signalements existant, il doit dérouler le menu _"Importer des signalements"_ de la page du type de signalements. Il clique ensuite sur le bouton _"Importer des signalements à partir du catalogue IDGO"_ et est renvoyé vers un formulaire lui proposant de choisir une ressource appartenant à l'organisation à laquelle il est rattaché dans IDGO. Il peut valider son choix en cliquant sur le bouton _"Lancer l'import avec le fichier"_. Les données sont importées dans le type de signalements.

## Informations concernant l'import

* L'import des signalements est géré en tâche de fond : l'utilisateur peut poursuivre sa navigation même si l'import n'est pas terminé ;
* Les enregistrements soupçonnés de former des doublons sont marqués automatiquement à l'aide du mécanisme de relation entre signalements. Les doublons sont identifiés par l'égalité de leur titre et de leur description, ou par l'égalité de leur géométrie) ;
* Les enregistrements importés sont enregistrés avec le statut "brouillon", sauf s'ils ont un attributs "status" mentionnant leur état (brouillon : draft ; publication en cours : pending ; publié : published ; archivé : archived) ;
* Lors d'un ré-import, si des signalements possèdent le même identifiant qu'un signalement existant, celui-ci est mis à jour avec les informations contenues dans le fichier.

**Contraintes** :
* Seuls les champs portant les mêmes noms que la table des signalements en base sont exploités, les autres ne sont pas pris en compte ;
* Pour les champs correspondant à des listes de choix seules les valeurs seront exploitées (pas les libellés en langage naturel) : ces champs sont donc considérés comme des champs de type 'Texte'. L'utilisateur doit reconfigurer manuellement les listes de choix ;
* Géométries supportées pour Excel : colonne geom en WKT dans le système de coordonnées attendu (pas de reprojection - cf. DB_SRID dans settings.py) ;
* La projection doit être du 4326 ;
* Les types "multi" (multiPolygon, multiLigne) ne sont pas exploitables.

## Export d'un type de signalements

Cette fonction permet d'exporter les signalements d'un type de signalements sous la forme d'un fichier GeoJSON ou CSV.
* Tout utilisateur pouvant naviguer dans le projet peut exporter les données
* Seules les données que l'utilisateur courant a le droit de consulter figurent dans l'export GeoJSON ou CSV. Le statut (brouillon, publié, en attente de publication, archive) est mentionné pour chaque signalement.
* L'export ne contient aucune information relative aux évènements et aux auteurs des signalements.
* L'export ne contient aucune référence vers les pièces jointes.
* L'export ne contient aucune information relative aux styles cartographiques des types de signalements.

---

[Retour à l'accueil](<README.md>)
