let map;
let dictLayersToLeaflet = {};

L.TileLayer.BetterWMS = L.TileLayer.WMS.extend({

	onAdd: function (map) {
		// Triggered when the layer is added to a map.
		//   Register a click listener, then do all the upstream WMS things
		L.TileLayer.WMS.prototype.onAdd.call(this, map);
		map.on('click', this.getFeatureInfo, this);
	},

	onRemove: function (map) {
		// Triggered when the layer is removed from a map.
		//   Unregister a click listener, then do all the upstream WMS things
		L.TileLayer.WMS.prototype.onRemove.call(this, map);
		map.off('click', this.getFeatureInfo, this);
	},

	getFeatureInfo: function (evt) {
		const queryableLayerSelected = document.getElementById(`queryable-layers-selector-${this.wmsParams.basemapId}`).getElementsByClassName('selected')[0].innerHTML;
		if (queryableLayerSelected === this.wmsParams.title) {
			// Make an AJAX request to the server and hope for the best
			var url = this.getFeatureInfoUrl(evt.latlng);
			var showResults = L.Util.bind(this.showGetFeatureInfo, this);
			$.ajax({
				url: url,
				success: function (data, status, xhr) {
					var err = typeof data === 'object' ? null : data;
					if (data.features || err) {
						showResults(err, evt.latlng, data);
					}
				},
				error: function (xhr, status, error) {
					if (!error) { error = 'Données de la couche inaccessibles' }
					showResults(error, evt.latlng);
				}
			});
		}
	},
	
	getFeatureInfoUrl: function (latlng) {
		// Construct a GetFeatureInfo request URL given a point
		var point = this._map.latLngToContainerPoint(latlng, this._map.getZoom());
		var size = this._map.getSize(),
				
				params = {
					request: 'GetFeatureInfo',
					service: 'WMS',
					// srs: this.wmsParams.srs,
					srs: 'EPSG:4326',
					// styles: this.wmsParams.styles,
					// transparent: this.wmsParams.transparent,
					version: this.wmsParams.version,      
					format: this.wmsParams.format,
					bbox: this._map.getBounds().toBBoxString(),
					height: size.y,
					width: size.x,
					layers: this.wmsParams.layers,
					query_layers: this.wmsParams.layers,
					info_format: 'application/json'
				};
		
		params[params.version === '1.3.0' ? 'i' : 'x'] = Math.floor(point.x);
		params[params.version === '1.3.0' ? 'j' : 'y'] = Math.floor(point.y);
		
		return this._url + L.Util.getParamString(params, this._url, true);
	},
	
	showGetFeatureInfo: function (err, latlng, data) {

		let content;

		if (err) {
			console.log('Erreur lors du getFeatureInfo sur la carte');
			content = `
				<h4>${this.options.title}</h4>
				<p>Données de la couche inaccessibles</p>
			`
		} else {
		
			// Otherwise show the content in a popup
			let contentLines = [];
			let contentTitle;
			if (data.features.length > 0) {
				Object.entries(data.features[0].properties).forEach(entry => {
					const [key, value] = entry;
					if (key !== 'bbox') {
						contentLines.push(`<div>${key}: ${value}</div>`);
					}
				})
				contentTitle = `<h4>${this.options.title}</h4>`;
				content = contentTitle.concat(contentLines.join(''));

				L.popup({ maxWidth: 800})
					.setLatLng(latlng)
					.setContent(content)
					.openOn(this._map);
			} else {
				console.log('Pas de features trouvées pour cette couche');
			}
		}
	}

});

L.tileLayer.betterWms = function (url, options) {
	return new L.TileLayer.BetterWMS(url, options);  
};

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
						let leafletLayer;
						if (layer.queryable) {
							options.title = layer.title;
							leafletLayer = L.tileLayer
								.betterWms(layer.service, options)
								.addTo(map);
						} else {
							leafletLayer = L.tileLayer
								.wms(layer.service, options)
								.addTo(map);
						}
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
			: feature.properties.creator.username ? `<div>Auteur: ${feature.properties.creator.username}</div>` : '';

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
