# Documentation des Permissions dans GeoContrib

## 1. Introduction
Cette documentation décrit les permissions attribuées aux utilisateurs dans GeoContrib en fonction de leur rôle.

## 2. Rôles et Permissions
Les utilisateurs sont classés en différents niveaux d'autorisation :

| Rôle | Accès au projet | Ajouter des signalements | Modifier ses propres signalements | Modifier tous les signalements | Publier | Supprimer ses propres signalements | Supprimer tous les signalements | Modérer |
|------|---------------|----------------|--------------------------|----------------------|--------|--------------------------|----------------------|--------|
| **Utilisateur anonyme (non connecté)** | ✅ (selon visibilité projet) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Utilisateur connecté** | ✅ (selon visibilité projet) | ❌ | ❌ | ❌ | ✅ (si projet non modéré) | ❌ | ❌ | ❌ |
| **Contributeur** | ✅ | ✅ | ✅ (uniquement ses propres signalements) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Super Contributeur** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (seulement ses propres signalements) | ❌ | ❌ |
| **Modérateur** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Administrateur** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## 3. Gestion des Statuts des Signalements

La modification du statut des signalements dépend du rôle de l'utilisateur et du mode de modération du projet.

- **Projet sans modération** :
  - Un contributeur peut créer un signalement directement en "publié".
  - Un super contributeur peut modifier tous les statuts (brouillon, publié, archivé).
  - Un administrateur ou modérateur peut modifier tous les statuts sans restriction.

- **Projet avec modération** :
  - Un contributeur peut créer un signalement mais celui-ci sera en "publication en cours".
  - Un super contributeur peut modifier les signalements et les soumettre à la modération.
  - Un modérateur ou administrateur peut valider et publier les signalements.
  - Un modérateur voit tous les signalements, y compris les brouillons des autres utilisateurs.

- **Cas particuliers** :
  - Un utilisateur anonyme ne voit que les signalements "publiés" et éventuellement "archivés" selon la configuration du projet.
  - Un administrateur peut voir et modifier tous les signalements.

## 4. Gestion de la Suppression des Signalements

Les règles de suppression des signalements sont définies selon le rôle de l’utilisateur :

| Rôle | Peut supprimer ses propres signalements ? | Peut supprimer tous les signalements ? |
|------|--------------------------------|---------------------------------|
| **Contributeur** | ❌ | ❌ |
| **Super Contributeur** | ✅ (seulement ses propres signalements) | ❌ |
| **Modérateur** | ❌ | ❌ |
| **Administrateur** | ✅ (peut supprimer tous les signalements) | ✅ |

- **Les contributeurs ne peuvent pas supprimer de signalements.**
- **Les super contributeurs peuvent supprimer uniquement leurs propres signalements.**
- **Les modérateurs ne peuvent pas supprimer de signalements.**
- **Seuls les administrateurs peuvent supprimer tous les signalements.**

## 5. Restrictions sur les Statuts de Modification

Lorsqu'un utilisateur modifie un signalement, il ne peut le modifier que vers un statut autorisé en fonction de son rôle et du mode de modération du projet.

- **Un contributeur :**
  - Peut modifier **uniquement ses propres signalements**.
  - En mode modéré, peut passer un signalement de **brouillon → en attente**.
  - En mode non modéré, peut passer un signalement de **brouillon → publié**.
  - Ne peut pas modifier les signalements des autres utilisateurs.

- **Un super contributeur :**
  - Peut modifier **tous les signalements**.
  - En mode modéré, peut passer un signalement de **brouillon → en attente → publié**.
  - En mode non modéré, peut modifier entre **brouillon, publié, archivé**.
  - Peut modifier les **brouillons des autres utilisateurs**.

- **Un modérateur ou administrateur :**
  - Peut modifier **tous les statuts de tous les signalements**.

---

Ce document est une première version. Des corrections ou des précisions peuvent être nécessaires.