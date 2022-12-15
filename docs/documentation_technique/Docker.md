# Docker

## docker-compose

Il exemple de déploiement en utilisant docker-compose existe ici :

https://git.neogeo.fr/geocontrib/geocontrib-docker

## Configuration

L'image docker de base possèdes ces variables de configuration :
* "ALLOWED_HOSTS", default="localhost, 127.0.0.1, 0.0.0.0", cast=Csv()
* "APPLICATION_ABSTRACT"
* "APPLICATION_NAME", default="GéoContrib"
* "BASE_URL", default="http://localhost:8000"
* "CAS_SERVER_URL", None
* "CELERY_ACCEPT_CONTENT", default="application/json", cast=Csv()
* "CELERY_BROKER_URL", default=f"redis://{ REDIS_HOST }:6379"
* "CELERY_RESULT_BACKEND", default=f"redis://{ REDIS_HOST }:6379"
* "CELERY_RESULT_SERIALIZER", default="json"
* "CELERY_TASK_SERIALIZER", default="json"
* "DATA_UPLOAD_MAX_NUMBER_FIELDS", default=10000
* "DB_HOST", default="geocontrib-db"
* "DB_NAME", default="geocontrib"
* "DB_PORT", default="5432"
* "DB_PWD", default="geocontrib"
* "DB_USER", default="geocontrib"
* "DEBUG", default=False, cast=bool
* "DEFAULT_FROM_EMAIL", default=""
* "DEFAULT_SENDING_FREQUENCY", default="never"
* "DISABLE_LOGIN_BUTTON", default=None
* "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
* "EMAIL_HOST", default=""
* "EMAIL_HOST_PASSWORD", default=""
* "EMAIL_HOST_USER", default=""
* "EMAIL_PORT", cast=int, default=22
* "EMAIL_USE_TLS", cast=bool, default=True
* "FAVICON_PATH", default=os.path.join(MEDIA_URL, "logo-neogeo-circle.png")
* "FILE_MAX_SIZE", default=10000000
* "IDGO_LOGIN", default="geocontrib"
* "IDGO_PASSWORD", default="CHANGE_ME"
* "IDGO_URL", default="https://idgo.dev.neogeo.local/api/resources_vector_by_user/"
* "IDGO_VERIFY_CERTIFICATE", default=False
* "IMAGE_FORMAT", default="application/pdf,image/png,image/jpeg"
* "LANGUAGE_CODE", default="fr-FR"
* "LOGIN_URL", default="geocontrib:login"
* "LOGO_PATH", default=os.path.join(MEDIA_URL, "logo-neogeo-circle.png")
* "LOG_LEVEL", default="INFO"
* "LOG_LEVEL", default="INFO"
* "LOG_URL", default=None
* "MAGIC_IS_AVAILABLE", default=True, cast=bool)  # File image validation (@seb / install IdeoBFC
* "MAPSERVER_URL", default="https://mapserver.dev.neogeo.local/maps/"
* "PROJECT_COPY_RELATED_AUTHORIZATION", default=True
* "OUR_APPS", default="geocontrib, api", cast=Csv()
* "REDIS_HOST", default="redis"
* "SECRET_KEY", default="SECRET_KEY"
* "SELECTED_GEOCODER_PROVIDER", default="addok"
* "SSO_MIDDLEWARE", default="", cast=Csv()
* "SSO_PLUGIN", default="", cast=Csv()
* "THIRD_PARTY_DJANGO_APPS", default="rest_framework, rest_framework_gis, django_celery_beat,", cast=Csv()
* "TIME_ZONE", default="Europe/Paris"
* "URL_PREFIX", default=""
* "USE_L10N", default=False, cast=bool
* "USE_X_FORWARDED_HOST", default=False, cast=bool

Variables utilisées pour configurer le frontend:
* APPLICATION_NAME
* APPLICATION_ABSTRACT
* LOGO_PATH
* FAVICON_PATH
* DISABLE_LOGIN_BUTTON
* LOG_URL
* BASE_URL
* CATALOG_NAME
* IDGO
* DEFAULT_BASE_MAP_SCHEMA_TYPE
* DEFAULT_BASE_MAP_SERVICE
* DEFAULT_BASE_MAP_OPTIONS
* DEFAULT_MAP_VIEW_CENTER
* DEFAULT_MAP_VIEW_ZOOM
* MAP_PREVIEW_CENTER
* DISPLAY_FORBIDDEN_PROJECTS
* DISPLAY_FORBIDDEN_PROJECTS_DEFAULT
