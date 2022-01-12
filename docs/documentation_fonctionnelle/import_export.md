# Import et export de données

## Création d'un type de signalement et import de données simultanés

Les administrateurs de projets (et utilisateurs avec droits supérieurs) ont la possibilité de créer un type de signalement à partir de la structure d'un fichier.

Depuis la page d'accueil d'un projet, le bouton _"Créer un type de signalements à partir d'un fichier GeoJSON"_ permet à l'utilisateur d'uploader un fichier stocké sur son poste local. Suite au chargement, la structure du fichier est lue et le modèle de données du type de signalement est proposé à l'utilisateur à travers le formulaire d'édition.
L'administrateur peut préciser la géométrie, le titre du type de signalement, et vérifier ou modifier chacun des champs personnalisés.

En bas de page, il peut choisir :
* de créer simplement le type de signalement,
* de créer le type de signalement et d'importer les données du fichier.

## Imports de données dans un type de signalements existant

Cette fonction permet d'importer des signalements depuis un fichier GeoJSON dans un type de signalement existant. Elle est disponible depuis la page du type de signalement.

Seuls les utilisateurs qui peuvent créer des signalements (contributeurs et niveaux de droits supérieurs du projet) peuvent utiliser cette fonction.

## Fonctionnement de l'import

* Import des signalements géré en tâche de fond : l'utilisateur peut poursuivre sa navigation même si l'import n'est pas terminé ;
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

Cette fonction permet d'exporter les signalements d'un type de signalements sous la forme d'un fichier GeoJSON.
* Tout utilisateur pouvant naviguer dans le projet peut exporter les données
* Seules les données que l'utilisateur courant a le droit de consulter figurent dans l'export GeoJSON. Le statut (brouillon, publié, en attente de publication, archive) est mentionné pour chaque signalement.
* L'export ne contient aucune information relative aux évènements et aux auteurs des signalements.
* L'export ne contient aucune référence vers les pièces jointes.
* L'export ne contient aucune information relative aux styles cartographiques des types de signalements.

---

[Retour à l'accueil](<README.md>)
