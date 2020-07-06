# Geocodeur

Un outil de géocodage est disponible sur les cartes. Plusieurs fournisseurs de données peuvent être utilisés selon la configuration de l'application. Voici un exemple de configuration pour utiliser l'API Adresse de [geo.api.gouv](https://geo.api.gouv.fr/adresse).

```
# Settings for the geocoder feature
GEOCODER = {
    'PROVIDER': 'addok'
}
```

Voici la liste des fournisseurs diposnibles, avec leur valeur à utiliser dans le fichier `settings.py`

* API Adresse de [geo.api.gouv](https://geo.api.gouv.fr/adresse): `'addok'`
* OSM [Nominatim](https://nominatim.org/release-docs/develop/api/Overview/): `'nominatim'`
* [Photon](http://photon.komoot.de/): `'photon'``
<!-- * [Bing](https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/?redirectedfrom=MSDN): `'bing'` -->


