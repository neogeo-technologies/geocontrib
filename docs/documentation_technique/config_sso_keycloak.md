# Guide de Configuration SSO Keycloak pour Geocontrib

Geocontrib peut être configuré pour utiliser l’authentification unique (SSO) via Keycloak grâce au module [`django-pyoidc`](https://django-pyoidc.readthedocs.io/latest/tutorial.html).

Cette documentation explique comment paramétrer cette intégration SSO, que l’installation soit classique ou conteneurisée (Docker).

## Installation

* Dans une installation classique il faut installer la librairie en lançant la commande: ```
pip install -r requirements.txt```

* Dans une installation docker, la librairie est installé à la création du conteneur.

## Variables d'environnement

L'image docker intègre tout ce qu'il mais il faut quand même la configurer:

Ajouter des variables d'environnement:
* SSO\_KEYCLOAK\_URL  
URL de base du serveur Keycloak.
Sert de référence principale pour les échanges d’authentification et pour activer les URLs de login Geocontrib.

* SSO\_KEYCLOAK\_CLIENT\_ID  
Identifiant du client déclaré dans Keycloak pour Geocontrib.
Doit correspondre à l'ID du client configuré dans l’interface Keycloak (onglet Clients).

* SSO\_KEYCLOAK\_CLIENT\_SECRET
Secret partagé entre Keycloak et Geocontrib pour authentifier les requêtes (obtenu dans Keycloak, à garder confidentiel).

* SSO\_KEYCLOAK\_REALM  
Nom du Realm Keycloak utilisé pour l’authentification (ex : master, mais de préférence en créer un différent de master).

* SSO\_KEYCLOAK\_DISCOVERY\_ENDPOINT  
URL du point de découverte OIDC du Realm Keycloak.
Elle permet à Django de récupérer automatiquement les métadonnées nécessaires à l’authentification OIDC.

* SSO\_CALLBACK\_PATH  
Chemin de rappel (callback) utilisé après l’authentification réussie via Keycloak.
-> Dans la plupart des cas la valeur par défaut suffit, par contre ce chemin doit être enregistré dans le client Keycloak comme URI de redirection autorisée.

* SSO\_POST\_LOGOUT\_REDIRECT\_URI
Url de redirection après déconnexion d'un service SSO (keycloak).

* SSO\_ADMIN\_USERS  
Lorsque l'utilisateur est créé ou mis à jour via le SSO, s'il correspond à l'un des usernames de cette liste, il se voit attribuer les rôles is_staff et is_superuser dans Django.

* LOG\_URL  
URL utilisée pour se connecter via SSO

* LOGOUT\_URL  
Spécifie une url de déconnexion remplaçant l'appel au logout django


## Exemple de fichier `.env`
```
# Variables SSO requises pour keycloak
SSO_KEYCLOAK_URL=https://<keycloak-host>/
SSO_KEYCLOAK_CLIENT_ID=<client_id>
SSO_KEYCLOAK_CLIENT_SECRET=<client_secret>
SSO_KEYCLOAK_REALM=<realm>
SSO_KEYCLOAK_DISCOVERY_ENDPOINT=https://<keycloak-host>/realms/<realm>/.well-known/openid-configuration

# Les trois variables suivantes n'ont pas besoin d'être définies si pas de changement aux valeurs par défaut
SSO_CALLBACK_PATH=https://<geocontrib-app>/geocontrib/oidc/callback/
SSO_POST_LOGOUT_REDIRECT_URI=https://<geocontrib-app>/geocontrib/
SSO_ADMIN_USER_GROUPS=geocontrib-admins

# Configuration du frontend geocontrib
LOG_URL=https://<geocontrib-app>/geocontrib/oidc/authenticate/
LOGOUT_URL=https://<geocontrib-app>/geocontrib/oidc/logout/
```

## Procédure de modification et de déploiement

1. Modifier les valeurs selon les paramètres Keycloak fournis dans le fichier .env.

2. Redémarrer l’application :
    * Pour Docker :
    Relancer le déploiement dans la CI pour prendre en compte les nouvelles variables dans le conteneur
    * Pour une installation classique :  
    Redémarrer le service web (ex : ```systemctl restart gunicorn```).

Vérifier le bon fonctionnement du SSO en se connectant via l’interface Geocontrib.

## Dépannage

Problème de redirection après connexion/déconnexion
Si la redirection échoue (par exemple, l'URL de callback), cela peut être lié à une variable d'environnement incorrecte.

Solution :
En installation classique : Assurez-vous que la variable (comme SSO_CALLBACK_PATH) est définie et non vide dans le fichier .env. Si elle est vide, supprimez l'entrée.

Avec Docker Compose personnalisé : Le fichier docker-compose.yml fourni avec l'application gère déjà ce cas. Pour une configuration personnalisée, définissez une valeur par défaut pour la variable :
```
environment:
  - SSO_CALLBACK_PATH=${SSO_CALLBACK_PATH:-/geocontrib/oidc/callback/}
```
Cela garantit que les URLs de redirection sont valides et fonctionnent correctement.

### Problèmes de redirection après connexion/déconnexion

1. **Vérifiez les URL de redirection dans Keycloak :**
   - Assurez-vous que les **Valid Redirect URIs** et **Valid Post Logout Redirect URIs** dans Keycloak sont bien configurées et correspondent à celles de votre application Django.
     - Exemple : `https://<geocontrib-app>/geocontrib/oidc/callback/` pour la connexion et `https://<geocontrib-app>/geocontrib/` pour la déconnexion.

2. **Vérifiez les variables d'environnement dans le fichier `.env` :**
   - Assurez-vous que les variables SSO_CALLBACK_PATH (connexion) et SSO_POST_LOGOUT_REDIRECT_URI (déconnexion) sont bien définies et non vides dans votre fichier .env.   
   Si une de ces variables est vide, supprimez l'entrée dans le fichier .env ou, pour Docker Compose personnalisé, définissez une valeur par défaut :  
   ```
    - SSO_CALLBACK_PATH=${SSO_CALLBACK_PATH:-/geocontrib/oidc/callback/}
   ```

3. **Vérifiez la configuration du service worker (Workbox) :**
   - Assurez-vous que **Workbox** ne bloque pas les URLs de callback ou de logout dans son cache. Le chemin `/oidc/` étant blacklisté dans la configuration, cela ne devrait normalement pas se produire, mais il est utile de vérifier cette configuration pour éviter toute interférence.


### **Erreur `401 Unauthorized` ou `403 Forbidden` :**
  - Vérifiez les logs de l'application pour s'assurer que le **client Keycloak** et le **secret** sont correctement configurés.

### **Erreur 404 ou comportement de page non trouvée après authentification :**
  - Assurez-vous que les URLs comme `/geocontrib/oidc/callback/` et `/geocontrib/oidc/logout/` sont bien configurées dans Nginx et non traitées par le front-end (Vue.js).

## Références

- [django-pyoidc documentation](https://django-pyoidc.readthedocs.io/latest/tutorial.html)
- [Documentation officielle Keycloak](https://www.keycloak.org/documentation)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)