
# Plugin Géorchestra

## Configuration

**Dans le fichier _settings.py_ de l'application :**

* Ajouter l'application :

    ```
    INSTALLED_APPS = [
        # ...
        'plugin_georchestra',
        # ...
    ]
    ```

* Ajouter les modules d'authentification à la liste des Middleware dans le settings.py de l'application :

    ```
    MIDDLEWARE = [
        # ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'plugin_ideo_bfc.auth.middleware.RemoteUserMiddleware',
        # ...
    ```

* Activer le module, indiquer l'attribut du HEADER et l'url de fermeture de session

    ```
    OIDC_SETTED = True  # False par défaut
    HEADER_UID = 'OIDC_CLAIM_uid'  # Valeur par défaut
    SSO_LOGOUT_URL = ''
    ```

* Déterminer, si besoin, une liste de pattern d'url ne nécessitant pas de traitement SSO:

    ```
    IGNORE_PATH = ['geocontrib:login', ] # Vide par défaut
    ```


### Dans le fichier _urls.py_ de l'application


## Informations utiles


L'_username_ du modèle **User** de Django correspond à l'identifiant de l'agent/employée.
