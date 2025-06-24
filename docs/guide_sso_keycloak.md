# SSO Keycloak pour Geocontrib

## Présentation

Geocontrib peut être configuré pour utiliser l’authentification unique (SSO) via Keycloak grâce au module [`django-pyoidc`](https://django-pyoidc.readthedocs.io/latest/tutorial.html).

Cette documentation présente le fonctionnement de l'authentification SSO, ainsi que la configuration, le test de connexion, la gestion des administrateurs et les notifications associées.

## Fonctionnement

### Login via SSO (Keycloak)

1. **L'utilisateur clique sur "Se connecter"** dans l'application Geocontrib.
2. Il est redirigé vers le portail **Keycloak**, où il saisit ses identifiants.
3. Une fois authentifié, l'utilisateur est redirigé vers **Geocontrib** et est automatiquement connecté.
4. L'utilisateur reçoit une **notification par email** confirmant la création de son compte dans Geocontrib, avec un lien vers la page de son profil.
5. Si l'utilisateur est un **administrateur**, son statut `is_staff` et `is_superuser` est automatiquement mis à jour.
6. Les **administrateurs** reçoivent également une notification par email avec un lien vers la page de détail de l'utilisateur dans l'administration Django.

### Logout via SSO (Keycloak)

1. **L'utilisateur clique sur "Se déconnecter"** dans Geocontrib.
2. Cela entraîne la **déconnexion de Geocontrib** et de **Keycloak** simultanément.
3. Si l'utilisateur se déconnecte via **Keycloak**, la session **Django** est également terminée.
4. Une fois déconnecté, l'utilisateur est redirigé vers l'**URL de redirection après logout** définie dans Keycloak, telle que spécifiée dans la configuration (`SSO_POST_LOGOUT_REDIRECT_URI`).

## Configuration

### Prérequis

Avant de configurer le SSO dans geocontrib, assurez-vous que :
- Une instance **Keycloak** est installé et accessible.
- Un **client SSO** est créé dans Keycloak pour l'application Geocontrib, de préférence **pas dans le realm "master"**.

### 1. Dans Keycloak :
- **Création d'un client Keycloak** :
    - Crée un client dans Keycloak pour Geocontrib (par exemple : `geocontrib-client`).
    - Dans l'interface Keycloak, allez dans le client et configurez les paramètres suivants :
      - **Valid Redirect URIs** :  
        ```
        https://<geocontrib-app>/geocontrib/oidc/callback/
        ```
      - **Valid Post Logout Redirect URIs** :  
        ```
        https://<geocontrib-app>/geocontrib/
        ```
    - Vérifiez que les URLs sont correctes

### 2. Dans Geocontrib (Django) :
L'authentification via Keycloak est activée en renseignant la variable d'environnement `SSO_KEYCLOAK_URL`.

Les variables suivantes doivent être configurées dans votre `.env` (se référer à la [documentation technique](./documentation_technique/config_sso_keycloak.md) pour le détail des variables d'environnement) :
- `SSO_KEYCLOAK_URL`
- `SSO_KEYCLOAK_CLIENT_ID`
- `SSO_KEYCLOAK_CLIENT_SECRET`
- `SSO_KEYCLOAK_REALM`
- `SSO_KEYCLOAK_DISCOVERY_ENDPOINT`
- `SSO_CALLBACK_PATH` (si nécessaire)
- `SSO_POST_LOGOUT_REDIRECT_URI`
- `LOG_URL` et `LOGOUT_URL`

## Gestion des comptes administrateurs Django

Les utilisateurs **administrateurs** dans Geocontrib sont définis via le paramètre `SSO_ADMIN_USERS`.  
Lors de la création ou mise à jour d’un utilisateur via Keycloak, si son username correspond à l’un des utilisateurs dans `SSO_ADMIN_USERS`, il sera marqué comme administrateur dans Geocontrib.

## Parcours de test de connexion SSO

### 1. Préparation de l'utilisateur dans Keycloak

Avant de tester la connexion SSO, il est important que l'utilisateur soit correctement configuré dans **Keycloak** :

- **Utilisateur dans le bon Realm** : L'utilisateur doit être créé dans le **realm correct**, celui du client configuré pour l'application.
- **Email vérifié** : L'email de l'utilisateur doit être vérifié pour éviter les erreurs de connexion.
- **Mot de passe défini** : L'utilisateur doit avoir un mot de passe configuré dans Keycloak pour pouvoir se connecter via SSO.
- **Attention aux comptes administrateurs** : Il est déconseillé de tester la connexion SSO avec un compte administrateur Keycloak qui pourrait ne pas avoir son email enregistré, ce qui provoquerait une erreur à la connexion.

### 2. Tester la connexion SSO

Voici les étapes pour tester la connexion SSO pour un utilisateur :

1. L'utilisateur clique sur "Se connecter" dans Geocontrib.
2. Il est redirigé vers le portail Keycloak où il renseigne ses identifiants.
3. Une fois authentifié, il est redirigé vers Geocontrib et est automatiquement connecté.

## Notifications dans Geocontrib

Après une création d'utilisateur dans geocontrib réussie via SSO, certaines notifications sont envoyées :

- **Notification à l'utilisateur** : Un e-mail est envoyé pour confirmer la création du compte et inclut un lien vers la page de son profil dans Geocontrib.
- **Notification aux administrateurs** : Les administrateurs reçoivent une notification contenant un lien vers la page de détail de l'utilisateur dans l'administration Django.

Ces notifications peuvent être personnalisées si nécessaire dans l'administration django.

