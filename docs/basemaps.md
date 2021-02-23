# Fonds cartographiques

La gestion des fonds cartographiques est divisée en deux partie dans GéoContrib :
* la gestion des couches de données
* la gestion des fonds cartographiques

## Couches de données

Les couches de données sont gérées par les administrateurs de GéoContrib (via la page d'administration 
/admin/geocontrib/layer/).
Deux types de couches peuvent y être configurées :
* des couches WMS (Web Map Service - standard de l'OGC) ;
* des couches TMS (Tiled Map Service - standard de fait issue de la communauté géospatiale open source).

Chacune de ces couches est décrite par :
* un titre (charge à l'administrateur de l'outil de choisir le titre qui conviendra le mieux)
* une URL de service
* des options : structure JSON directement interprétable par Leaflet (cf. 
https://leafletjs.com/reference-1.6.0.html#tilelayer).

Étant donné que la configuration d'une couche est très liée aux capacités de Leaflet et qu'elle ne bénéficie pas d'une 
interface adaptée à des non-spécialistes, nous donnons ci-dessous quelques exemples de configuration.

Seules les couches affichables dans la projection EPSG:3857 sont supportées.

### Exemples de configuration de couches WMS

**Couche WMS au format PNG :**
```Titre : Ortho 2013 Picardie
Type de couche : WMS
Service : https://www.geopicardie.fr/geoserver/ows
Options : {
    "attribution": "R\u00e9gion Hauts-de-France",
    "layers": "geopicardie:picardie_ortho_ign_2013_vis",
    "format": "image/png",
    "transparent": true}
```

**Couche WMS au format JPEG avec transparence :**
```Titre : Scan25
Type de couche : WMS
Service : https://www.geopicardie.fr/geoserver/ows
Options : {
    "attribution": "IGN",
    "layers": "geopicardie:picardie_scan25",
    "format": "image/jpeg",
    "transparent": true}
```

### Exemples de configuration de couches TMS

**Couche faded du serveur OSM de Géo2France :**

```Titre : OSM Géo2France - Faded
Type de couche : TMS
Service : https://osm.geo2france.fr/mapproxy/tms/1.0.0/faded/webmercator/{z}/{x}/{y}.png
Options : {
    "tms": true,
    "zoomOffset": -1,
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap - G\u00e9o2France",
    "maxZoom": 19}
```
Remarque : Notez l'utilisation des deux options `tms` et `zoomOffSet` que l'on ne retrouve pas dans le paramétrage des 
couches OpenStreetMap officielles.

**Couche OpenStreetMap normal :**
```Titre : OpenStreetMap France
Type de couche : TMS
Service : https://{s}.tile.osm.org/{z}/{x}/{y}.png
Options : {
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap",
    "maxZoom": 20}
```

**Couche OpenStreetMap France :**
```Titre : OpenStreetMap France
Type de couche : TMS
Service : https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png
Options : {
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap",
    "maxZoom": 20}
```

### Options de Leaflet

**minZoom et maxZoom :**
`minZoom` et `maxZoom` vous permettent de définir la plage d'échelles pour laquelle la couche en question est visible.
Il s'agit de nombres entiers qui se référèrent aux niveaux de zoom utilisés par GoogleMaps.
Les plus petits nombres correspondent aux échelles cartographiques les plus petites (niveau mondial, international) 
alors que les plus grands correspondent aux échelles cartographiques les plus grandes (niveau urbain).
cf. https://leafletjs.com/examples/zoom-levels/

Vous pouvez utiliser ces paramètres avec plusieurs couches pour ainsi rendre visible une couche à certaines échelles et 
une autre couche à d'autres échelles.

**opacity :**
Vous pouvez moduler l'opacité d'une couche à l'aide de l'option `opacity`.

## Fonds cartographiques
Chaque projet dispose de sa propre configuration des fonds cartographiques. Cette fonction est accessible aux 
administrateurs de chaque projet via le menu "Fonds cartographiques".

Un fond cartographique est une liste de couches ordonnées (couches décrites plus haut et mise à disposition des 
administrateurs des projets par les administrateur de l'outil). Ces couches sont uniquement affichées sous forme 
d'images dans les cartes. Elles ne peuvent pas être utilisées comme couches d'accrochage lors de la saisie 
(aucune fonction d'accrochage n'existe dans l'application).

L'ordre des couches et leur transparence peuvent être modifiés par les administrateurs du projet.

Les fonds cartographiques sont mis à disposition des utilisateurs qui exploitent les outils cartographiques de 
GéoContrib. Chacun d'eux peut activer le fond cartographique qui lui convient le mieux, voire modifier l'ordre des
couches et leur transparence. Ces personnalisées sont enregistrées au niveau du navigateur web et n'ont pas d'impact 
sur les autres utilisateurs de l'application.
