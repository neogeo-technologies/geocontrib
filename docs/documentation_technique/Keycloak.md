# Configuration de Geocontrib pour utiliser KEYCLOAK SSO

## Installation

Il faut utiliser le module django-pyoidc (installé avec geocontrib) et suivre l'installation comme indiqué ici https://django-pyoidc.readthedocs.io/latest/tutorial.html

## Configuration docker

L'image docker intègre tout ce qu'il mais il faut quand même la configurer:

Ajouter des variables d'environnement:
* SSO\_KEYCLOAK\_URL: URL de login du serveur KEYCLOAK, sert aussi à activer les URL géocontrib de login
* SSO\_KEYCLOAK\_DISCOVERY\_ENDPOINT: URL du point de découverte OIDC du Realm Keycloak. Elle permet à Django de récupérer automatiquement les métadonnées nécessaires.


 
