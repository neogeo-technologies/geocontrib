# Documentation des Permissions dans GeoContrib

## 1. Introduction
Cette documentation décrit les permissions attribuées aux utilisateurs dans GeoContrib en fonction de leur rôle.

## 2. Visibilité des signalements

La visibilité des signalements est configurée au niveau du projet via deux paramètres distincts :

- **Visibilité des signalements publiés** : Définit le rôle minimum requis pour consulter les signalements en statut *publié*.
- **Visibilité des signalements archivés** : Définit le rôle minimum requis pour consulter les signalements en statut *archivé*.

Pour chacun de ces paramètres l'administrateur projet défini à partir de quel rôle un utilisateur peut voir les signalements.

> **Exception** :  
Le rôle **Lecteur** contourne ces restrictions et permet à l’utilisateur de **voir tous les signalements** (publiés et archivés), **indépendamment des paramètres du projet**.  

**Exemple** : "Si project_arch_rank_min = MODERATOR, seuls les modérateurs et administrateurs verront les signalements archivés, sauf pour le rôle Lecteur."

#### Visibilité des signalements en brouillon
Les signalements en statut *brouillon* sont visibles uniquement par:
- L’utilisateur qui les a créés
- L’administrateur du projet pour les signalements des autres utilisateurs

#### Visibilité des signalements en attente de publication
Les signalements *en attente de publication* sont visibles uniquement par:
- L’utilisateur qui les a créés
- Le modérateur et l’administrateur du projet pour les signalements des autres utilisateurs

## 3. Rôles et Permissions d'édition des signalements
Les rôles suivants n’ont aucun droit d’édition sur les signalements et sont exclus du tableau des permissions :

- **Lecteur** (accès en lecture seule)
- **Utilisateur anonyme** (non connecté)
- **Utilisateur connecté** (sauf création, voir note ci-dessous)

> **Note** :  
Si la variable d’environnement **ALLOW_LOGGED_USER_CREATE_FEATURE** est activée (True), les **utilisateurs connectés** peuvent **créer** des signalements, mais **pas les modifier**.

Les utilisateurs sont classés en différents niveaux d'autorisation :

| Rôle | Ajouter des signalements | Modifier les signalements | Publier | Supprimer les signalements | Modérer |
|------|----------------|--------------------------|--------|----------------------|--------|
| **Contributeur** | ✅ | ✅ (uniquement ses propres signalements) | ❌ | ❌ | ❌ |
| **Super Contributeur** | ✅ | ✅ | ✅ | ✅ (seulement ses propres signalements) | ❌ |
| **Modérateur** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Administrateur** | ✅ | ✅ | ✅ | ✅ | ✅ |

## 4. Gestion des Statuts des Signalements

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

## 5. Gestion de la Suppression des Signalements

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

## 6. Restrictions sur les Statuts de Modification

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
