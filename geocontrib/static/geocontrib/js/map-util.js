let map;
let dictLayersToLeaflet = {};

const mapUtil = {

	getMap: () => {
		return map;
	},

	createMap: function (options) {
		const { lat, lng, mapDefaultViewCenter, mapDefaultViewZoom, zoom } = options;

		map = L.map('map', {
			zoomControl: false,
		})
			.setView(
				[
					!lat ? mapDefaultViewCenter[0] : lat,
					!lng ? mapDefaultViewCenter[1] : lng
				],
				!zoom ? mapDefaultViewZoom : zoom);

		L.control.zoom({ zoomInTitle: 'Zoomer', zoomOutTitle: 'Dézoomer', position: 'topright' }).addTo(map);
	},

	addLayers: function (layers, serviceMap, optionsMap) {
		console.log(layers);
		if (layers) {
			layers.forEach((layer) => {
				const options = layer.options;
				if (layer.schema_type === 'wms') {
					const leafletLayer = L.tileLayer.wms(layer.service, options).addTo(map);
					dictLayersToLeaflet[layer.id] = leafletLayer._leaflet_id;
				} else if (layer.schema_type === 'tms') {
					const leafletLayer = L.tileLayer(layer.service, options).addTo(map);
					dictLayersToLeaflet[layer.id] = leafletLayer._leaflet_id;
				}
			});
		} else {
			L.tileLayer(serviceMap, optionsMap).addTo(map)
		}
	},

	// Remove the base layers (not the features)
	removeLayers: function () {
		map.eachLayer((leafLetlayer) => {
			if (Object.values(dictLayersToLeaflet).includes(leafLetlayer._leaflet_id)) {
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

	addFeatures: function (features) {
		featureGroup = new L.FeatureGroup()
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

	addMapEventListener: function(eventName, callback) {
		map.on(eventName, callback);
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