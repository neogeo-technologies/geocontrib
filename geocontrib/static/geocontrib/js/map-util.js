const mapUtil = {


    createMap: function (options) {
        const { lat, lng, mapDefaultViewCenter, mapDefaultViewZoom, zoom } = options;

        const map = L.map('map', {
            zoomControl: false,
        })
            .setView(
                [
                    !lat ? mapDefaultViewCenter[0] : lat,
                    !lng ? mapDefaultViewCenter[1] : lng
                ],
                !zoom ? mapDefaultViewZoom : zoom);

        L.control.zoom({ zoomInTitle: 'Zoomer', zoomOutTitle: 'Dézoomer', position: 'topright' }).addTo(map);
        // L.control.layers().addTo(map);


        return map;
    },

    addLayers: function (map, layers, serviceMap, optionsMap) {
        if (layers) {
            layers.forEach((layer) => {
                const options = layer.options
                if (layer.schema_type === 'wms') {
                    L.tileLayer.wms(layer.service, options).addTo(map);
                } else if (layer.schema_type === 'tms') {
                    L.tileLayer(layer.service, options).addTo(map)
                }
            });
        } else {
            L.tileLayer(serviceMap, optionsMap).addTo(map)
        }
    },

    addFeatures: function (map, features) {
        var featureGroup = new L.FeatureGroup()
        features.forEach((feature) => {
            const geomJSON = turf.flip(feature.geometry);

            const popupContent = this._createContentPopup(feature)

            if (geomJSON.type === 'Point') {
                L.circleMarker(geomJSON.coordinates, {
                    color: feature.properties.feature_type.color,
                    radius: 4,
                    fillOpacity: 0.3,
                    weight: 1
                }).bindPopup(popupContent).addTo(featureGroup)
            } else if (geomJSON.type === 'LineString') {
                L.polyline(geomJSON.coordinates, {
                    color: feature.properties.feature_type.color,
                    weight: 1.5
                }).bindPopup(popupContent).addTo(featureGroup)
            } else if (geomJSON.type === 'Polygon') {
                L.polygon(geomJSON.coordinates, {
                    color: feature.properties.feature_type.color,
                    weight: 1.5,
                    fillOpacity: 0.3
                }).bindPopup(popupContent).addTo(featureGroup)
            }
        });
        map.addLayer(featureGroup);
        return featureGroup;
    },

    _createContentPopup: function (feature) {
        const author = feature.properties.creator.full_name ?
            `<div>
              Auteur : ${feature.properties.creator.first_name} ${feature.properties.creator.last_name} ${feature.properties.creator.last_name} ${feature.properties.creator.last_name}
            </div>`: ''

        return `
          <h4>
            <a href="${feature.properties.feature_url}">${feature.properties.title}</a>
          </h4>
          <div>
            Statut : ${feature.properties.status.label}
          </div>
          <div>
            Type : <a href="${feature.properties.feature_type_url}"> ${feature.properties.feature_type.title} </a>
          </div>
          <div>
            Dernière mise à jour : ${feature.properties.updated_on}
          </div>
          ${author}
        `;
    }

}