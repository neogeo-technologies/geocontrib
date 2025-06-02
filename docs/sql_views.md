# 📄 Documentation – Commande `generate_sql_view`

## 🎯 Objectif

La commande Django `generate_sql_view` permet de générer dynamiquement des **vues SQL PostgreSQL** à partir des entités `FeatureType` ou `Project`. Ces vues facilitent la consultation des données métier en exposant un schéma lisible et consolidé.

## ⚙️ Modes de fonctionnement

### Mode `Type`
- Génère une vue SQL **pour un seul `FeatureType`**
- La vue expose les données standards et les **champs personnalisés**
- En cas de suppression (`is_ft_deletion=True`), la vue est supprimée

**Exemple de nom de vue** :
`v_signalement--voirie__demonstration`

### Mode `Projet`
- Génère une vue combinée pour **tous les `FeatureType` d’un projet**
- Les `FeatureType` doivent avoir des **champs personnalisés identiques** (nom + type)
- Si ce n’est pas le cas, la commande **échoue** sauf si on passe `--force_project_view_with_aliases`
- Permet une vision consolidée multi-types

**Exemple de nom de vue** :
`v_demonstration`

## 🏗️ Structure des vues générées

### Champs standards :
- `feature_id`, `title`, `description`, `geom`, `status`
- `project_id`, `feature_type_id`, `creator_id`, `created_on`, `updated_on`

### Champs personnalisés :
- Injectés dynamiquement à partir des `CustomField`
- Nom de colonne généré par normalisation :
  - Minuscules
  - Espaces remplacés
  - Accentuation supprimée
- Suffixés `__1`, `__2`, ... en cas de **collision**

## 🧱 Schéma SQL

- Le schéma PostgreSQL utilisé est défini via l’option `--schema_name`
- Par défaut : `data`
- L’ancien schéma est **supprimé** puis recréé avec les nouvelles vues

## 🔁 Options CLI

| Option | Description |
|--------|-------------|
| `--feature_type_id` | ID du type de signalement |
| `--feature_type_slug` | Slug (nom lisible) du type |
| `--project_id` | ID du projet |
| `--mode` | `Type` ou `Projet` |
| `--schema_name` | Nom du schéma PostgreSQL cible |
| `--deleted_cf_id` | Champ personnalisé supprimé |
| `--is_ft_deletion` | Booléen – suppression d’un type ? |
| `--force_project_view_with_aliases` | Ignore les divergences de champs et utilise des alias |

## ⚠️ Gestion des collisions

- Deux champs distincts avec un nom normalisé identique → suffixe `__n`
- Logique de compatibilité forcée avec `--force_project_view_with_aliases`
- Avertissements dans les logs si conflit

## 🚨 Comportement en cas d’erreur

- Si `mode` inconnu → `CommandError`
- Si `project_id` ou `feature_type_id` manquant → erreur bloquante
- Si `FeatureType` supprimé en cascade (signal `post_delete`) :
  - Le signal tente de supprimer la vue correspondante
  - Si le `Project` est déjà supprimé → la suppression est ignorée proprement (aucune erreur)

## 🧪 Tests unitaires associés

Les tests couvrent :
- Validation des modes (`Type`, `Projet`)
- Création/suppression de vues
- Erreurs de cohérence entre champs personnalisés
- Gestion des champs supprimés
- Résolution des collisions de noms de champs
- Génération silencieuse si `FeatureType` orphelin

## 🔍 Références de fichiers

- Commande : `geocontrib/management/commands/generate_sql_view.py`
- Signal : `geocontrib/signals.py`
- Tests : `api/tests/test_generate_sql_views.py`

## 📝 Exemple d’usage

```bash
python manage.py generate_sql_view \
  --mode=Projet \
  --project_id=5 \
  --schema_name=data

python manage.py generate_sql_view \
  --mode=Type \
  --feature_type_id=12 \
  --schema_name=data \
  --is_ft_deletion=True
```
