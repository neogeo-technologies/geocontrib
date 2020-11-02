let map;
let dictLayersToLeaflet = {};

const mapUtil = {
  getMap: () => {
    return map;
  },

  createMap: function (options) {
    const {
      lat,
      lng,
      mapDefaultViewCenter,
      mapDefaultViewZoom,
      zoom,
      zoomControl = true,
    } = options;

    map = L.map('map', {
      zoomControl: false,
    }).setView(
      [
        !lat ? mapDefaultViewCenter[0] : lat,
        !lng ? mapDefaultViewCenter[1] : lng,
      ],
      !zoom ? mapDefaultViewZoom : zoom
    );

    if (zoomControl) {
      L.control
        .zoom({
          zoomInTitle: 'Zoomer',
          zoomOutTitle: 'Dézoomer',
          position: 'topright',
        })
        .addTo(map);
    }

    return map;
  },

  addLayers: function (layers, serviceMap, optionsMap) {
    if (layers) {
      layers.forEach((layer) => {
				const options = layer.options;
				if (options) {
					options.opacity = layer.opacity;

					if (layer.schema_type === 'wms') {
						const leafletLayer = L.tileLayer
							.wms(layer.service, options)
							.addTo(map);
						dictLayersToLeaflet[layer.id] = leafletLayer._leaflet_id;
					} else if (layer.schema_type === 'tms') {
						const leafletLayer = L.tileLayer(layer.service, options).addTo(map);
						dictLayersToLeaflet[layer.id] = leafletLayer._leaflet_id;
					}
				}
       
      });
    } else {
      L.tileLayer(serviceMap, optionsMap).addTo(map);
    }
  },

  // Remove the base layers (not the features)
  removeLayers: function () {
    map.eachLayer((leafLetlayer) => {
      if (
        Object.values(dictLayersToLeaflet).includes(leafLetlayer._leaflet_id)
      ) {
        map.removeLayer(leafLetlayer);
      }
    });
    dictLayersToLeaflet = {};
  },

  updateOpacity(layerId, opacity) {
    const internalLeafletLayerId = dictLayersToLeaflet[layerId];
    map.eachLayer((layer) => {
      if (layer._leaflet_id === internalLeafletLayerId) {
        layer.setOpacity(opacity);
      }
    });
  },

  updateOrder(layers) {
    // First remove existing layers
    map.eachLayer((leafLetlayer) => {
      layers.forEach((layerOptions) => {
        if (dictLayersToLeaflet[layerOptions.id] === leafLetlayer._leaflet_id) {
          map.removeLayer(leafLetlayer);
        }
      });
    });
    dictLayersToLeaflet = {};

    // Redraw the layers
    this.addLayers(layers);
  },

  addFeatures: function (features, filter) {
    featureGroup = new L.FeatureGroup();
    features.forEach((feature) => {

      let filters = [];

      if (filter) {
        const typeCheck = filter.featureType && feature.properties.feature_type.slug === filter.featureType;
        const statusCheck = filter.featureStatus && feature.properties.status.value === filter.featureStatus;
        const titleCheck = filter.featureTitle && feature.properties.title.includes(filter.featureTitle);
        filters = [typeCheck, statusCheck, titleCheck];
      }

      if (!filter || !Object.values(filter).some(val => val) || Object.values(filter).some(val => val) && filters.length && filters.every(val => val !== false)) {

        const geomJSON = turf.flip(feature.geometry);

        const popupContent = this._createContentPopup(feature);

        if (geomJSON.type === 'Point') {
          L.circleMarker(geomJSON.coordinates, {
            color: feature.properties.feature_type.color,
            radius: 4,
            fillOpacity: 0.5,
            weight: 3,
          })
            .bindPopup(popupContent)
            .addTo(featureGroup);
        } else if (geomJSON.type === 'LineString') {
          L.polyline(geomJSON.coordinates, {
            color: feature.properties.feature_type.color,
            weight: 3,
          })
            .bindPopup(popupContent)
            .addTo(featureGroup);
        } else if (geomJSON.type === 'Polygon') {
          L.polygon(geomJSON.coordinates, {
            color: feature.properties.feature_type.color,
            weight: 3,
            fillOpacity: 0.5,
          })
            .bindPopup(popupContent)
            .addTo(featureGroup);
        }
      }
    });
    map.addLayer(featureGroup);
    return featureGroup;
  },

  addMapEventListener: function (eventName, callback) {
    map.on(eventName, callback);
  },

  _createContentPopup: function (feature) {
    const author = feature.properties.creator.full_name
      ? `<div>
              Auteur : ${feature.properties.creator.first_name} ${feature.properties.creator.last_name}
            </div>`
      : feature.properties.creator.username ? `Auteur: ${feature.properties.creator.username}` : '';

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
  },
};
