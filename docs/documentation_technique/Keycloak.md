# Configuration SSO Keycloak pour Geocontrib

## Présentation

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
Nom du Realm Keycloak utilisé pour l’authentification (ex : master).

* SSO\_KEYCLOAK\_DISCOVERY\_ENDPOINT  
URL du point de découverte OIDC du Realm Keycloak.
Elle permet à Django de récupérer automatiquement les métadonnées nécessaires à l’authentification OIDC.

* LOG\_URL
  URL utilisée pour se connecter via SSO.

* LOGOUT\_URL
  Spécifie une url de déconnexion remplaçant l'appel au logout django


## Exemple de fichier `.env`
```
SSO_KEYCLOAK_URL=https://<keycloak-host>/
SSO_KEYCLOAK_CLIENT_ID=<client_id>
SSO_KEYCLOAK_CLIENT_SECRET=<client_secret>
SSO_KEYCLOAK_REALM=<realm>
SSO_KEYCLOAK_DISCOVERY_ENDPOINT=https://<keycloak-host>/realms/<realm>/.well-known/openid-configuration
LOG_URL=https://<keycloak-host>/geocontrib/oidc/authenticate/
LOGOUT_URL=https://<keycloak-host>/geocontrib/oidc/logout/
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

- **Problèmes de connexion SSO** : vérifier les logs de l’application et la correspondance des paramètres Keycloak.
- **Erreur 401/403** : vérifier que le client Keycloak a les bons droits et que le secret est valide.

## Références

- [django-pyoidc documentation](https://django-pyoidc.readthedocs.io/latest/tutorial.html)
- [Documentation officielle Keycloak](https://www.keycloak.org/documentation)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)