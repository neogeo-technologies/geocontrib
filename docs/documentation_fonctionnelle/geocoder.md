# Geocodeur

Un outil de géocodage est disponible sur les cartes interactive de l'application. 

## Configuration

Plusieurs fournisseurs de données peuvent être utilisés selon la configuration de l'application. 
Exemple de configuration pour utiliser l'API Adresse de [geo.api.gouv](https://geo.api.gouv.fr/adresse) :

```
# Available geocoders
GEOCODER_PROVIDERS = {
    'ADDOK': 'addok',
    'NOMINATIM': 'nominatim',
    'PHOTON': 'photon'
}

# Active geocoder
SELECTED_GEOCODER = {
    'PROVIDER': 'addok'
}
```

Voici la liste des fournisseurs diposnibles, avec leur valeur à utiliser dans le fichier `settings.py` :

* API Adresse de [geo.api.gouv](https://geo.api.gouv.fr/adresse): `'addok'`
* OSM [Nominatim](https://nominatim.org/release-docs/develop/api/Overview/): `'nominatim'`
* [Photon](http://photon.komoot.de/): `'photon'`
<!-- * [Bing](https://docs.microsoft.com/en-us/bingmaps/rest-services/locations/?redirectedfrom=MSDN): `'bing'` -->


## Source

Le module de géocodage intégré à GéoContrib provient du projet suivant :
https://github.com/perliedman/leaflet-control-geocoder

Les adaptations de ce projet pour GéoContrib ont été déposées dans le dépôt suivant :
https://github.com/neogeo-technologies/leaflet-control-geocoder
