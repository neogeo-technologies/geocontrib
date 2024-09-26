# Docker

## docker-compose

Il exemple de déploiement en utilisant docker-compose existe ici :

https://git.neogeo.fr/geocontrib/geocontrib-docker

## Configuration

L'image Docker de base possède ces variables de configuration :

* `ALLOWED_HOSTS`, default=`"localhost, 127.0.0.1, 0.0.0.0"`, cast=`Csv()`
  Définit les hôtes autorisés à accéder à l'application.

* `CSRF_TRUSTED_ORIGINS`, default=`""`
  Liste des domaines externes autorisés pour les requêtes sécurisées contre les attaques CSRF.  
  Chaque domaine doit inclure un schéma (ex : `https://` ou `http://`) depuis django 4. Utilisé principalement  
  lorsque l'application est servie via plusieurs domaines externes.

* `APPLICATION_ABSTRACT`
  Contient une description de l'application (résumé ou informations générales).

* `APPLICATION_NAME`, default=`"GéoContrib"`
  Le nom de l'application affiché dans l'interface utilisateur.

* `BASE_URL`, default=`"http://localhost:8000"`
  L'URL de base utilisée pour accéder à l'application.

* `CAS_SERVER_URL`, default=None
  URL du serveur CAS (Single Sign-On), si l'application utilise l'authentification CAS.

* `CELERY_ACCEPT_CONTENT`, default=`"application/json"`, cast=`Csv()`
  Formats de contenu que Celery accepte lors de l'exécution des tâches.

* `CELERY_BROKER_URL`, default=`f"redis://{ REDIS_HOST }:6379"`
  URL du courtier de messages utilisé par Celery pour envoyer les tâches.

* `CELERY_RESULT_BACKEND`, default=`f"redis://{ REDIS_HOST }:6379"`
  Backend utilisé par Celery pour stocker les résultats des tâches.

* `CELERY_RESULT_SERIALIZER`, default=`"json"`
  Format utilisé pour sérialiser les résultats des tâches Celery.

* `CELERY_TASK_SERIALIZER`, default=`"json"`
  Format utilisé pour sérialiser les tâches envoyées à Celery.

* `DATA_UPLOAD_MAX_NUMBER_FIELDS`, default=10000
  Nombre maximal de champs pouvant être téléchargés en une seule requête.

* `DB_HOST`, default=`"geocontrib-db"`
  Hôte de la base de données.

* `DB_NAME`, default=`"geocontrib"`
  Nom de la base de données utilisée par l'application.

* `DB_PORT`, default=`"5432"`
  Port utilisé pour se connecter à la base de données.

* `DB_PWD`, default=`"geocontrib"`
  Mot de passe pour se connecter à la base de données.

* `DB_USER`, default=`"geocontrib"`
  Nom d'utilisateur pour se connecter à la base de données.

* `DEBUG`, default=False, cast=`bool`
  Active ou désactive le mode debug de Django.

* `DEFAULT_FROM_EMAIL`, default=`""`
  Adresse email par défaut utilisée pour envoyer des emails depuis l'application.

* `DEFAULT_SENDING_FREQUENCY`, default=`"never"`
  Fréquence d'envoi par défaut pour certaines notifications ou emails.

* `DISABLE_LOGIN_BUTTON`, default=None
  Si activé, cache le bouton de connexion dans l'application.

* `EMAIL_BACKEND`, default=`"django.core.mail.backends.console.EmailBackend"`
  Backend utilisé pour l'envoi d'emails.

* `EMAIL_HOST`, default=`""`
  Hôte SMTP utilisé pour l'envoi des emails.

* `EMAIL_HOST_PASSWORD`, default=`""`
  Mot de passe pour l'authentification sur le serveur SMTP.

* `EMAIL_HOST_USER`, default=`""`
  Nom d'utilisateur pour l'authentification sur le serveur SMTP.

* `EMAIL_PORT`, cast=`int`, default=22
  Port utilisé pour l'envoi des emails via SMTP.

* `EMAIL_USE_TLS`, cast=`bool`, default=True
  Active ou désactive l'utilisation de TLS pour les emails.

* `FAVICON_PATH`, default=`os.path.join(MEDIA_URL, "logo-neogeo-circle.png")`
  Chemin vers l'icône favicon de l'application.

* `FILE_MAX_SIZE`, default=10000000
  Taille maximale autorisée pour le téléchargement de fichiers en octets.

* `LOGOUT_HIDDEN`, default=False, cast=`bool`
  Si activé, cache le bouton de déconnexion.

* `HIDE_USER_CREATION_BUTTON`, default=False, cast=`bool`
  Si activé, cache le bouton de création de compte utilisateur.

* `IDGO_LOGIN`, default=`"geocontrib"`
  Nom d'utilisateur utilisé pour l'authentification avec le service IDGO.

* `IDGO_PASSWORD`, default=`"CHANGE_ME"`
  Mot de passe utilisé pour l'authentification avec le service IDGO.

* `IDGO_URL`, default=`"https://idgo.dev.neogeo.local/api/resources_vector_by_user/"`
  URL pour accéder aux ressources IDGO.

* `IDGO_VERIFY_CERTIFICATE`, default=False
  Active ou désactive la vérification du certificat SSL pour IDGO.

* `IMAGE_FORMAT`, default=`"application/pdf,image/png,image/jpeg"`
  Formats de fichiers acceptés pour le téléchargement d'images.

* `LANGUAGE_CODE`, default=`"fr-FR"`
  Langue par défaut de l'application.

* `LOGIN_URL`, default=`"geocontrib:login"`
  URL vers la page de connexion de l'application.

* `LOGO_PATH`, default=`os.path.join(MEDIA_URL, "logo-neogeo-circle.png")`
  Chemin vers le logo utilisé dans l'interface de l'application.

* `LOG_LEVEL`, default=`"INFO"`
  Niveau de journalisation utilisé pour l'application (INFO, DEBUG, ERROR, etc.).

* `MAGIC_IS_AVAILABLE`, default=True, cast=`bool`
  Indique si la bibliothèque ImageMagick est disponible pour la validation des images.

* `MAPSERVER_URL`, default=`"https://mapserver.dev.neogeo.local/maps/"`
  URL du serveur cartographique utilisé pour les cartes.

* `PROJECT_COPY_RELATED_AUTHORIZATION`, default=True
  Permet la copie des autorisations liées lors de la duplication de projets.

* `OUR_APPS`, default=`"geocontrib, api"`, cast=`Csv()`
  Liste des applications internes de l'application.

* `REDIS_HOST`, default=`"redis"`
  Hôte du serveur Redis utilisé pour la mise en file d'attente des tâches Celery.

* `SECRET_KEY`, default=`"SECRET_KEY"`
  Clé secrète utilisée par Django pour la sécurité des sessions.

* `SSO_MIDDLEWARE`, default=`""`, cast=`Csv()`
  Liste des middlewares pour la gestion de l'authentification unique (SSO).

* `SSO_PLUGIN`, default=`""`, cast=`Csv()`
  Liste des plugins pour la gestion de l'authentification unique (SSO).

* `THIRD_PARTY_DJANGO_APPS`, default=`"rest_framework, rest_framework_gis, django_celery_beat"`, cast=`Csv()`
  Liste des applications Django tierces utilisées dans l'application.

* `TIME_ZONE`, default=`"Europe/Paris"`
  Fuseau horaire par défaut de l'application.

* `URL_PREFIX`, default=`""`
  Spécifie le chemin de base où l'application est servie après le nom de domaine.  
  Cela est utile si l'application est hébergée dans un sous-répertoire,  
  par exemple : `https://example.com/geocontrib/`.

* `USE_X_FORWARDED_HOST`, default=False, cast=`bool`
  Permet à Django d'utiliser l'en-tête `X-Forwarded-Host` transmis par un proxy inverse  
  pour générer des URLs correctes (par exemple pour la pagination) en fonction de l'URL publique.  
  Ceci est généralement utilisé dans des environnements où l'application est derrière un proxy comme geoOrchestra.  
  [Plus d'infos ici](https://redmine.neogeo.fr/issues/22571#note-11).


## Variables utilisées pour configurer le frontend :

* `APPLICATION_ABSTRACT`
  Description courte affichée dans l'en-tête de l'application.
  
* `APPLICATION_NAME`
  Nom de l'application, affiché dans l'en-tête et les notifications.
  
* `BASE_URL`
  Après le nom de domaine, spécifie l'URL de base à utiliser pour toutes les URL relatives.
  
* `CATALOG_NAME`
  Nom du catalogue à partir duquel importer des fonctionnalités.
  
* `DEFAULT_MAP_VIEW_CENTER`
  Coordonnées du centre de la carte lors du chargement initial.
  
* `DEFAULT_BASE_MAP_SCHEMA_TYPE`
  Type de carte de base utilisé par défaut (ex : TMS, WMTS ou WMS).
  
* `DEFAULT_BASE_MAP_SERVICE`
  Service fournissant la carte de base par défaut.
  
* `DEFAULT_BASE_MAP_OPTIONS`
  Options de la carte de base par défaut, inclut `maxZoom` et `attribution`.
  
* `DEFAULT_MAP_VIEW_ZOOM`
  Niveau de zoom par défaut lors du chargement de la carte.
  
* `DISABLE_LOGIN_BUTTON`
  Cache le bouton de connexion lorsque l'authentification est gérée en dehors de l'application.
  
* `DISPLAY_FORBIDDEN_PROJECTS`
  Spécifie si tous les projets doivent être affichés dans la liste de la page principale.
  
* `DISPLAY_FORBIDDEN_PROJECTS_DEFAULT`
  Valeur par défaut pour l'affichage des projets interdits.
  
* `FAVICON_PATH`
  Chemin où le favicon est stocké.
  
* `FONT_FAMILY`
  Police à utiliser dans l'application.
  
* `HEADER_COLOR`
  Couleur de fond pour personnaliser l'en-tête.
  
* `GEORCHESTRA_INTEGRATION`
  Active un composant d'en-tête pour intégrer l'application à Georchestra.
  
* `IDGO`
  Booléen pour afficher les boutons d'importation de fonctionnalités à partir d'un catalogue.
  
* `LOG_URL`
  URL utilisée pour se connecter via SSO.
  
* `LOGO_PATH`
  Chemin où le logo est stocké.
  
* `MAP_PREVIEW_CENTER`
  Centre de la prévisualisation de la carte affichée lors de la configuration de l'échelle maximale d'un projet.
  
* `PRIMARY_COLOR`
  Couleur personnalisée pour les éléments de l'application, comme les bordures et icônes (remplace la couleur teal).
  
* `PRIMARY_HIGHLIGHT_COLOR`
  Couleur pour les éléments de l'application lors des actions comme survol, focus, ou actif. Il est recommandé d'utiliser une couleur plus foncée (une couleur plus claire nécessiterait de changer la couleur de la police, ce qui n'est pas encore implémenté).
  
* `PROJECT_FILTERS`
  Filtres à afficher dans la liste des projets. Doit être une liste sous forme de chaîne de caractères. Exemple : la liste complète de tous les filtres disponibles est `'access_level,user_access_level,moderation,search'`. Pour ne pas afficher de filtres, la valeur serait `'empty'` (ou toute chaîne non incluse dans les filtres disponibles, `''` ne fonctionnerait pas car la valeur par défaut la remplacerait).
  
* `SSO_LOGIN_URL_WITH_REDIRECT`
  URL utilisée pour se connecter via SSO avec une redirection vers une URL d'origine.
  
* `URL_DOCUMENTATION`
  URL de la documentation de GéoContrib.
  
* `URL_DOCUMENTATION_FEATURE`
  URL de la documentation de GéoContrib pour les fonctionnalités.
