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

Les utilisateurs **administrateurs** dans Geocontrib sont gérés via leur appartenance à un **groupe Keycloak** (par défaut `/admins`).  
L’application Geocontrib attribue automatiquement les droits d’administration à tout utilisateur membre de ce groupe dans Keycloak, lors de la connexion via SSO.

### Créer et configurer le groupe d’administrateurs dans Keycloak

1. Connectez-vous à l’interface d’administration Keycloak avec un compte ayant les droits nécessaires.
2. Accédez à :  
   **Groups** (ou “Groupes”).
3. Cliquez sur **Create group** (ou “Créer un groupe”).
4. Saisissez le nom du groupe souhaité (par défaut : `admins`).
5. Cliquez sur **Save**.

Le groupe apparaît alors dans la liste.  
Vous pouvez maintenant y ajouter des membres :

1. Cliquez sur le groupe (`/admins` ou le nom de votre choix).
2. Allez dans l’onglet **Members** (ou “Membres”).
3. Cliquez sur **Add member** (ou “Ajouter un membre”).
4. Sélectionnez l’utilisateur à ajouter, puis validez.

**Remarque :**  
Le(s) nom(s) de groupe(s) utilisés pour l’administration sont configurables via la variable d’environnement `SSO_ADMIN_USER_GROUPS`.


### Configurer le mappage “Group Membership” dans Keycloak

Par défaut, Keycloak n’inclut pas l’information des groupes de l’utilisateur dans le jeton d’authentification (token OIDC) envoyé à Geocontrib.  

Pour que Geocontrib puisse connaître les groupes Keycloak de chaque utilisateur, il est nécessaire de créer un **mapper “Group Membership”** sur le client OIDC utilisé.

1. Accédez à :  
   **Clients > [Votre client Geocontrib] > Dedicated scopes**
2. Sélectionnez l’onglet **Mappers** (ou “Mappages”).
3. Cliquez sur **“Create”** (ou “Ajouter un mappage”).
4. Remplissez le formulaire comme suit :
    - **Name** : `groups`
    - **Mapper Type** : `Group Membership`
    - **Token Claim Name** : `groups`
    - **Full group path** : `true` (recommandé, retournera `/admins`)
    - **Add to ID token** : `ON`
    - **Add to access token** : `ON`
    - **Add to userinfo** : `ON`
5. Cliquez sur **Save**.

> **Remarque :**  
> Après avoir ajouté ce mapper, les utilisateurs devront se déconnecter puis se reconnecter pour obtenir un nouveau token OIDC intégrant la liste de leurs groupes.


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

