
# Plugin IDéO BFC

## Configuration
Toute les confs sont déjà définies dans le fichier '~/docker/geocontrib/geocontrib.env'
et sont définies ainsi:

```
OUR_PLUGIN=plugin_ideo_bfc
HEADER_UID=HTTP_SEC_USERNAME
SSO_SETTED=True
IGNORED_PATHS=geocontrib:logout,
OUR_MIDDLEWARE=plugin_ideo_bfc.auth.middleware.RemoteUserMiddleware
```

## Informations utiles


L'_username_ du modèle **User** de Django correspond à l'identifiant de l'agent/employée.
