# Configuration de Geocontrib pour utiliser CAS

## Installation

Il faut utiliser le module django-cas-ng (installé avec geocontrib) et suivre l'installation comme indiqué ici https://djangocas.dev/docs/latest/configuration.html#settings

## Configuration docker

L'image docker intègre tout ce qu'il mais il faut quand même la configurer:

Ajouter des variables d'environnement:
* CAS\_SERVER\_URL: URL de login du serveur CAS, sert aussi à activer les URL géocontrib de login
* SSO\_PLUGIN=django\_cas\_ng
* SSO\_MIDDLEWARE=django\_cas\_ng.middleware.CASMiddleware

 
