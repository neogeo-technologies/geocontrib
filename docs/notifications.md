# Système de notifications

## Vue d'ensemble
Notre système de notifications est conçu pour informer les utilisateurs des événements significatifs au sein de leurs projets, tels que la création, la mise à jour et la suppression de signalements, de commentaires et de pièces jointes. Ce système est configurable, permettant d'adapter les notifications aux besoins spécifiques des projets et aux préférences des utilisateurs.  

**Caractéristiques configurables commune à toutes les notifications** :  

  - **Modèles Personnalisables** : Le contenu des notifications peut être personnalisé à travers des modèles éditables stockés dans la base de données, permettant un ajustement dynamique du contenu dans l'interface d'administration.

## Types de Notifications

### 1. Notifications groupées
- **Objectif** : Informer tous les abonnés des différents projets sur les événements variés tels que les mises à jour, les suppressions et les créations de signalement, les évolutions du projet, ainsi que la publication de commentaires ou de pièces jointes.

- **Fonctionnement** : Les notifications sont regroupées grâce aux instances `StackedEvent`, crées par un Signal

- **Filtre** : Uniqement les événements pour les signalements dont le statut n'est pas à brouillon au moment de la génération de la notification sont envoyés.

- **Déclencheur** : Les notifications sont regroupées grâce aux instances `StackedEvent` et envoyées périodiquement selon la configuration de la tâche périodique associée.

- **Caractéristiques Configurables** :
  - **Niveau d'envoi des notifications** : Les administrateurs peuvent configurer l'envoi des notifications groupées à un niveau globale ou par projet. Ceci est géré par le champ `per_project` dans le modèle `NotificationModel`.
  - **Désactivation des notifications** : Vous pouvez désactiver les notifications pour un type de signalement via l'interface d'administration ou la configuration d'affichage de signalement dans l'application frontend. L'envoi des notifications de publication de documents clés ne sont pas impactés par ce pramétrage.

### 2. Notifications de publications de documents clés
- **Objectif** : Informer tous les abonnés des différents projets sur les publications importantes de documents au sein de leurs projets.

- **Fonctionnement** : Les notifications sont regroupées grâce aux instances `StackedEvent` spécifiques, en utilisant la propriété `only_key_document`. Les piles d'événements sont crées par un Signal, lors de la publication d'une pièce jointe avec le paramètre `is_key_document`.

- **Filtre** : Uniqement les événements pour les signalements dont le statut n'est pas à brouillon au moment de la génération de la notification sont envoyés.

- **Déclencheur** : Les notifications sont envoyées périodiquement selon la configuration de la tâche périodique associée.

- **Caractéristiques Configurables** :
  - **Activation des Notifications** : Les administrateurs peuvent activer ou désactiver les notifications pour les documents clés au niveau d'un type de signalement. Ceci est géré par le champ booléen `enable_key_doc_notif` dans le modèle `FeatureType`.

### 3. Notifications de créations de signalements en attente de modération
- **Objectif** : Informer les modérateurs des signalements nécessitant une modération dans les projets configurés avec le paramètre de modération activé.

- **Fonctionnement** : L'envoi de la notification est faite au niveau du modèle `Event` par la méthode `ping_users`

- **Déclencheur** : Se produit lorsqu'un signalement est créé ou modifié par un contributeur, ce qui lui attribue automatiquement le statut "En attente de publication".

### 4. Notifications de publications de signalements après modération
- **Objectif** : Informer le créateur d'un signalement lorsque sa soumission a été approuvée et publiée par un modérateur.

- **Fonctionnement** : L'envoi de la notification est faite au niveau du modèle `Event` par la méthode `ping_users`

- **Déclencheur** : Se produit lorsqu'un signalement passe du statut "En attente de publication" à "Publié'.

### 5. Notifications de publications de signalements par groupe d'utilisateurs
- **Objectif** :  Informer les membres d'un groupe d'utilisateurs de la publication d'un signalement lié à un groupe dont il est membre.

- **Fonctionnement** :  
  L'envoi de la notification est faite au niveau du modèle `Event` par la méthode `ping_users`. 
 
  Lorsqu'un signalement est publié, la méthode :  
  - Vérifie l'existence de champs personnalisés (`CustomField`) de type `notif_group` pour le type de signalement concerné.  
  - Récupère les groupes d'utilisateurs associés au signalement via ses données (`feature_data`).  
  - Ajoute automatiquement le groupe global (`is_global=True`) si présent.  
  - Récupère les membres des groupes identifiés, en excluant l'auteur du signalement.  
  - Envoie une notification aux utilisateurs via `notif_users_groups_published_feature()`.  

- **Déclencheur** :  
  Se produit lorsqu'un signalement lié à un groupe d'utilisateurs passe au statut "Publié". 

- **Caractéristiques Configurables** :  
  - **Activation des Notifications** : Les notifications sont activés dès lors qu'un champ personnalisé de type "Notification à un groupe" est configuré pour un type de signalement


### 6. Notifications de création de compte utilisateur
- **Objectif** : Informer l'utilisateur lorsque son compte a été créé dans geocontrib après une connexion par SSO.

- **Fonctionnement** : L'envoi de la notification est faite au niveau de pyoidc_backend

- **Déclencheur** : Se produit lorsqu'un nouvel utilisateur est ajouté suite à une connexion via keycloak.


### 7. Notification administrateur de l'ajout d'un utilisateur
- **Objectif** : Informer l'administrateur lorsqu'un nouvel utilisateur a été créé dans geocontrib après une connexion par SSO.

- **Fonctionnement** : L'envoi de la notification est faite au niveau de pyoidc_backend

- **Déclencheur** : Se produit lorsqu'un nouvel utilisateur est ajouté suite à une connexion via keycloak.


# 8. Notifications de création de projet & abonnement 1-clic

- **Objectif** : Informer automatiquement les membres d’un projet de sa création et leur permettre de s’abonner rapidement aux notifications du projet via un lien “M’abonner”.

- **Fonctionnement** : L’action déclenchée par le bouton frontend poste vers l’API. La vue déclenche ensuite une tâche Celery pour envoyer les emails en arrière-plan, évitant de bloquer l’interface.

- **Déclencheur** : Se produit lorsqu’un administrateur clique sur “Notifier les membres” dans la page des membres du projet. Peut-être lancé via la commande `python manage.py notify_project_creation_with_subscription`.
