
# Plugin geOrchestra

## Objectifs

Le plugin geOrchestra réalise quelques adaptation de Geocontrib pour son intégration dans un environnement geOrchestra :
* exploiter l'authentification de l'utilisateur. Le plugin exploite les en-têtes HTTP insérées par le proxy/CAS de 
geOrchestra après l'authentification de l'utilisateur ;
* mettre à jour la base de données des utilisateurs de Geocontrib à partir de l'annuaire LDAP de geOrchestra. La 
gestion des droits des utilisateurs est toujours réalisée dans l'interface de Geocontrib. Cette mise à jour de la base 
des utilisateurs est appelée "synchronisation" dans le reste du présent document ;
* désactiver les fonctions d'authentification native de Geocontrib.

## Principes de fonctionnement

### Authentification

L'identification de l'utilisateur connecté à geOrchestra est réalisé en exploitant les en-têtes HTTP tel que décrit 
dans la documentation de geOrchestra : https://github.com/georchestra/georchestra/tree/20.0.x/security-proxy#headers.

### Synchronisation des utilisateurs

La synchronisation des utilisateurs peut être lancée de 2 manières :
* dans l'interface d'administration de Geocontrib dans la partie "Utilisateurs", un bouton 
"Synchroniser les utilisateurs" est présent en haut de la page. Ce bouton lance immédiatement la synchronisation des 
utilisateurs ;
* via une commande Django incluse dans le fichier manage.py. Pour la lancer : `python manage.py georchestra_user_sync`. 
Cette commande peut être automatisée pour être exécutée périodiquement (via crontab par exemple).

Les informations associées aux utilisateurs et récupérées de l'annuaire LDAP :
* prénom : `givenName` ;
* nom de famille : `sn` ;
* nom d'utilisateur/identifiant unique : `uid` ;
* adresse électronique : `mail` ;
* appartenance à des groupes d'utilisateurs / rôles de georchestra : `memberOf`.

Certains utilisateurs de l'annuaire ne sont pas importés lors de la synchronisation :
* utilisateurs dont le nom/identifiant unique est présent dans `EXCLUDED_USER_NAMES` ;
* utilisateurs appartenant à des groupes présents dans `EXCLUDED_USER_GROUPS` ;
* si `EXCLUSIVE_USER_GROUPS` est défini, tous les utilisateurs n'appartenant à aucun groupe présent dans 
`EXCLUSIVE_USER_GROUPS`.

Certains utilisateurs sont supprimés lors de la synchronisation :
* utilisateurs déjà présents dans Geocontrib et qui ne sont pas importés lors de la synchronisation pour les raisons 
évoquées précédemment ;
* utilisateurs déjà présents dans Geocontrib mais ne figurant pas dans l'annuaire LDAP.

Néanmoins, les utilisateurs figurant dans `PROTECTED_USER_NAMES` ne sont jamais supprimés par la synchronisation. Ils 
peuvent l'être manuellement via l'interface d'administration de Geocontrib.

Certains utilisateurs se voient automatiquement attribués des droits de superutilisateurs dans Geocontrib lors de la 
synchronisation : ceux figurant dans au moins un groupe d'utilisateurs présent dans `ADMIN_USER_GROUPS`.


## Déploiement et configuration

Les exemples de paramètres adaptés au plugin geOrchestra sont présents dans le fichier 
'docker/geocontrib/geocontrib.env'.

### Installation

A compléter...

### Exploitation du SSO de geOrchestra

* OUR_PLUGIN : nom du plugin activé `plugin_georchestra`
* OUR_MIDDLEWARE : identification du middleware utilisé pour l'authentification 
`plugin_georchestra.auth.middleware.RemoteUserMiddleware`
* SSO_SETTED : indication de ne pas utiliser l'authentification par défaut
* HEADER_UID : nom de l'en-tête HTTP identifiant l'utilisateur
* IGNORED_PATHS : routes ignorés

Typiquement :
```
OUR_PLUGIN = plugin_georchestra
HEADER_UID = HTTP_SEC_USERNAME
SSO_SETTED = True
IGNORED_PATHS = geocontrib:logout,
OUR_MIDDLEWARE = plugin_georchestra.auth.middleware.RemoteUserMiddleware
```

### Connexion à l'annuaire LDAP de geOrchestra

* LDAP_URI : adresse du serveur LDAP. Valeur par défaut : Aucune.
* LDAP_USERDN : paramètre user utilisé par l'objet Connection du module ldap3. Valeur par défaut : Aucune.
* LDAP_PASSWD : mot de passe. Valeur par défaut : Aucune.
* LDAP_SEARCH_BASE : préfiltre sur un groupe d'utilisateurs. Exemple (pour éviter d'avoir les utilisateurs dont le 
compte est en attente de modération) : `ou=users,dc=georchestra,dc=org`.Valeur par défaut : `dc=georchestra,dc=org`.
* LDAP_SEARCH_FILTER : filtre appliqué au contenu du LDAP. Valeur par défaut : `(objectClass=person)`

Typiquement :
```
LDAP_URI = ldap://ldap
LDAP_USERDN = cn=admin,dc=georchestra,dc=org
LDAP_PASSWD = secret
LDAP_SEARCH_BASE = ou=users,dc=georchestra,dc=org
LDAP_SEARCH_FILTER = (objectClass=person)
```

### Liste d'utilisateurs particulières

* PROTECTED_USER_NAMES : liste de noms d'utilisateurs (leur identifiant unique) à ne pas supprimer lors de la 
synchronisation des utilisateurs (liste de valeurs séparées par des virgules). Exemple : `admin,super_admin`. Valeur 
par défaut : aucune.
* EXCLUDED_USER_NAMES : liste des noms d'utilisateurs à ne pas importer dans Geocontrib lors de la synchronisation 
(liste de valeurs séparées par des virgules). Exemple : `geoserver_privileged_user`. Valeur par défaut : aucune.

### Liste de groupes d'utilisateurs particulières

* ADMIN_USER_GROUPS : liste des groupes d'utilisateurs à considérer comme des administrateurs (liste de valeurs 
séparées par des points-virgules). Les membres de ces groupes qui sont importés par la synchronisation récupèrent 
automatiquement les privilèges suivants : équipe, administrateur et super-utilisateur. Ils acquièrent donc tous les 
droits d'administration via l'interface d'administration de l'application. Chacun des groupes d'utilisateurs est défini 
à l'aide d'un filtre LDAP appliqué sur le champ `membreOf` des utilisateurs. 
Exemple : `cn=SUPERUSER,ou=roles,dc=georchestra,dc=org;cn=ADMINISTRATOR,ou=roles,dc=georchestra,dc=org;cn=GEOCONTRIB_ADMIN,ou=roles,dc=georchestra,dc=org`. 
Valeur par défaut : `cn=SUPERUSER,ou=roles,dc=georchestra,dc=org;cn=ADMINISTRATOR,ou=roles,dc=georchestra,dc=org`.
* EXCLUSIVE_USER_GROUPS : liste des groupes d'utilisateurs auxquels les utilisateurs doivent appartenir pour être 
importés dans Geocontrib (liste de valeurs séparées par des points-virgules). Seuls les membres de ces groupes sont 
importés (même s'ils font partie des groupes identifiés dans ADMIN_USER_GROUPS). Chacun des groupes d'utilisateurs est 
défini à l'aide d'un filtre LDAP appliqué sur le champ `membreOf` des utilisateurs. 
Exemple : `cn=SUPERUSER,ou=roles,dc=georchestra,dc=org;cn=ADMINISTRATOR,ou=roles,dc=georchestra,dc=org;cn=GEOCONTRIB_USER,ou=roles,dc=georchestra,dc=org`.
Valeur par défaut : aucune.
* EXCLUDED_USER_GROUPS : liste des groupes d'utilisateurs à ne pas importer dans Geocontrib (liste de valeurs séparées 
par des points-virgules). Cela concerne typiquement les utilisateurs dont les comptes sont en attente de modératio. 
Chacun des groupes d'utilisateurs est défini à l'aide d'un filtre LDAP appliqué sur le champ `membreOf` des 
utilisateurs. Exemple : `cn=pendingorg,ou=pendingorgs,dc=georchestra,dc=org`. Valeur par défaut : Aucune.

### Exclure les utilisateurs en attente de modération

Deux méthodes :
* Utiliser LDAP_SEARCH_BASE avec la valeur `ou=users,dc=georchestra,dc=org`;
* Utiliser EXCLUDED_USER_GROUPS en y insérant le groupe `cn=pendingorg,ou=pendingorgs,dc=georchestra,dc=org`.

