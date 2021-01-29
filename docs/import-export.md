# Import et export de données

Fonctions disponibles au niveau de la page descriptive d'un type de signalements.

## Import

**Description** : Cette fonction permet d'importer des signalements depuis un fichier GeoJSON.

**Accès** : Fonction disponible pour chaque type de signalement de chaque projet (dans la page descriptive du type de 
signalements)

**Disponibilité** : Uniquement pour les utilisateurs qui peuvent créer des signalements (contributeurs et niveaux de 
droits supérieurs du projet)

**Action réalisée** :
* Création de nouveaux signalements
* La fonction n'est pas capable de mettre à jour des signalements existants ni de supprimer des signalements existants
* Les enregistrements soupçonnés de former des doublons sont marqués automatiquement à l'aide du mécanisme de relation 
entre signalements. Les doublons sont identifiés par l'égalité de leur titre et de leur description, ou par l'égalité de leur géométrie)
* Les enregistrements importés sont enregistrés avec le statut "brouillon"

**Contraintes** :
* Le modèle de données supporté par la fonction d'import est décrit dans la page descriptive du type de signalements
* Seuls les champs portant les mêmes noms que la table des signalements en base sont exploités
* Des champs supplémentaires doivent être ajoutés au fichier Json ('title' champs unique, 'feature_type' slug du type de signalement)
* Pour les champs correspondant à des listes de choix : seules les valeurs seront exploitées (pas les libellés en 
langage naturel)
* Géométries supportées pour Excel : colonne geom en WKT dans le système de coordonnées attendu (pas de reprojection - 
cf. DB_SRID dans settings.py)
* La projection doit être du 4326
* Les types "multi" (multiPolygon, multiLigne) ne sont pas exploitables.

## Export

Cette fonction permet d'exporter les signalements d'un type de signalements sous la forme d'un fichier GeoJSON.
