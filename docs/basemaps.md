# Fonds cartographiques

Chaque projet dispose de sa propre configuration des fonds cartographiques. Cette fonction estaccessible dans le menu 
du projet et est accessible aux administrateurs du projet.

Deux types de fonds cartographiques sont exploitables :
* des couches WMS (Web Map Service - standard de l'OGC) ;
* des couches TMS (Tiled Map Service - standard de fait issue de la communauté géospatiale open source).

L'administrateur du projet peut empiler plusieurs couches, qu'il s'agisse de fonds de cartes (comme 
des cartes topographiques, des modèles numériques de terrain ou des orthophotographies) ou qu'il s'agisse de couches 
métier (réseaux, zonages...). Ces couches sont uniquement affichées sous forme d'images dans les cartes. Elles ne 
peuvent pas être utilisées comme couches d'accrochage lors de la saisie (aucune fonction d'accrochage n'existe dans 
l'application).

L'ordre des couches et leur transparence peuvent être modifiés par les administrateur du projet.
Seules les couches affichables dans la projection EPSG:3857 sont supportées.

Ces configurations ne peuvent pas être partagées entre projets. Pour utiliser une même chose dans plusieurs projets il
faut procéder par recopie manuelle.

Étant donné que la configuration d'une couche est très liée aux capacités de Leaflet à gérer ces types de couches et 
qu'elle ne bénéficie pas d'une interface adaptée à des non-spécialistes, nous donnons ci-dessous quelques exemples de 
configuration.

## Exemples de configuration de couches WMS

### Couche WMS au format PNG
```Titre : Ortho 2013 Picardie
Type de couche : WMS
Service : https://www.geopicardie.fr/geoserver/ows
Options : {
    "attribution": "R\u00e9gion Hauts-de-France",
    "layers": "geopicardie:picardie_ortho_ign_2013_vis",
    "format": "image/png",
    "transparent": true}
```

### Couche WMS au format JPEG avec transparence
```Titre : Scan25
Type de couche : WMS
Service : https://www.geopicardie.fr/geoserver/ows
Options : {
    "attribution": "IGN",
    "layers": "geopicardie:picardie_scan25",
    "format": "image/jpeg",
    "transparent": true}
```

## Exemples de configuration de couches TMS

### Couche faded du serveur OSM de Géo2France

Notez l'utilisation des deux options `tms` et `zoomOffSet` que l'on ne retrouve pas dans le paramétrage des couches 
OpenStreetMap officielles.

```Titre : OSM Géo2France - Faded
Type de couche : TMS
Service : https://osm.geo2france.fr/mapproxy/tms/1.0.0/faded/webmercator/{z}/{x}/{y}.png
Options : {
    "tms": true,
    "zoomOffset": -1,
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap - G\u00e9o2France",
    "maxZoom": 19}
```

### Couche OpenStreetMap normal
```Titre : OpenStreetMap France
Type de couche : TMS
Service : https://{s}.tile.osm.org/{z}/{x}/{y}.png
Options : {
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap",
    "maxZoom": 20}
```

### Couche OpenStreetMap France
```Titre : OpenStreetMap France
Type de couche : TMS
Service : https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png
Options : {
    "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap",
    "maxZoom": 20}
```

## Options de Leaflet

### minZoom et maxZoom
`minZoom` et `maxZoom` vous permettent de définir la plage d'échelles pour laquelle la couche en question est visible.
Il s'agit de nombres entiers qui se référèrent aux niveaux de zoom utilisés par GoogleMaps.
Les plus petits nombres correspondent aux échelles cartographiques les plus petites (niveau mondial, international) 
alors que les plus grands correspondent aux échelles cartographiques les plus grandes (niveau urbain).
cf. https://leafletjs.com/examples/zoom-levels/

Vous pouvez utiliser ces paramètres avec plusieurs couches pour ainsi rendre visible une couche à certaines échelles et 
une autre couche à d'autres échelles.

### opacity
Vous pouvez moduler l'opacité d'une couche à l'aide de l'option `opacity` 
(cf. https://leafletjs.com/reference-1.5.0.html#gridlayer-opacity)