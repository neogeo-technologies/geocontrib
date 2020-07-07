function getDataFilters() {
    var $form = $("#form-filters").serializeArray()
    var requestURL = `{% url 'geocontrib:feature_list' slug=project.slug %}`
    for (var field of $form) {
      if (field.value) {
        if (requestURL.includes('?')) {
          requestURL = `${requestURL}&${field.name}=${field.value}`
        } else {
          requestURL = `${requestURL}?${field.name}=${field.value}`
        }
      }
    }
    document.location = requestURL
  }

  $(document).ready(function() {

    $('#form-filters .ui.selection.dropdown').dropdown({
      clearable: true
    })

    $(document).on('click', '#submit-search', function () {
      getDataFilters()
    })
    $(document).on('change', '#form-filters .filter', function () {
      getDataFilters()
    })

    $('#table-features').DataTable({
      "language": {
          "sProcessing":     "Traitement en cours...",
          "sSearch":         "",
          "sLengthMenu":     "Afficher _MENU_ &eacute;l&eacute;ments",
          "sInfo":           "Affichage de l'&eacute;l&eacute;ment _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
          "sInfoEmpty":      "Affichage de l'&eacute;l&eacute;ment 0 &agrave; 0 sur 0 &eacute;l&eacute;ment",
          "sInfoFiltered":   "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
          "sInfoPostFix":    "",
          "sLoadingRecords": "Chargement en cours...",
          "sZeroRecords":    "Aucun &eacute;l&eacute;ment &agrave; afficher",
          "sEmptyTable":     "Aucune donn&eacute;e disponible",
          "oPaginate": {
              "sFirst":      "Premier",
              "sPrevious":   "Pr&eacute;c&eacute;dent",
              "sNext":       "Suivant",
              "sLast":       "Dernier"
          },
          "oAria": {
              "sSortAscending":  ": activer pour trier la colonne par ordre croissant",
              "sSortDescending": ": activer pour trier la colonne par ordre d&eacute;croissant"
          }
      },
      "searching" : false,
      "ordering" : true,
      "order": [],
      "lengthChange" : false,
      "pageLength": 15,
      "columnDefs": [{ className: "dt-center", targets: "_all" }]
    })

    var main = parseInt($("main").css("height"),10)
    $("#map").css("height", main - 150)

    // get initial zoom and center defined in the form
    var $formFilters = $("#form-filters");
    var zoom = $formFilters.find("input[name=zoom]").val()
    var lat = $formFilters.find("input[name=lat]").val()
    var lng = $formFilters.find("input[name=lng]").val()

    var mapDefaultViewCenter = {{ DEFAULT_MAP_VIEW.center }};
    var mapDefaultViewZoom = {{ DEFAULT_MAP_VIEW.zoom }};
    var map = L.map('map', {zoomControl: false}).setView([
      lat === "" ? mapDefaultViewCenter[0] : lat,
      lng === "" ? mapDefaultViewCenter[1] : lng
    ], zoom === "" ? mapDefaultViewZoom : zoom)

    L.control.zoom({zoomInTitle:'Zoomer', zoomOutTitle:'Dézoomer'}).addTo(map)

    // update zoom and center on each move
    map.on("moveend", function() {
      $formFilters.find("input[name=zoom]").val(map.getZoom())
      $formFilters.find("input[name=lat]").val(map.getCenter().lat)
      $formFilters.find("input[name=lng]").val(map.getCenter().lng)
    })

    {% if layers %}
      {% for layer in layers %}
        var options = {{ layer.options|safe }}
        console.log(`{{ layer.service }}`, options);
        {% if layer.schema_type == "wms" %}
          L.tileLayer.wms('{{ layer.service }}', options).addTo(map)
        {% elif layer.schema_type == "tms" %}
          L.tileLayer('{{ layer.service }}', options).addTo(map)
        {% endif %}
      {% endfor %}
    {% else %}
      L.tileLayer('{{ SERVICE }}',  JSON.parse('{{ OPTIONS | escapejs }}')).addTo(map)
    {% endif %}

    var featureGroup = new L.FeatureGroup()
    {% for feature in features %}
      var geomFeatureJSON = wellknown.parse("{{ feature.geom.wkt }}")
      var geomJSON = turf.flip(geomFeatureJSON)
      var popupContent = `
        <h4>
          <a href="{% url 'geocontrib:feature_detail' slug=project.slug feature_type_slug=feature.feature_type.slug feature_id=feature.feature_id  %}">{{ feature.title }}</a>
        </h4>
        <div>
          Statut :
          {% if feature.status == 'archived' %}
            Archivé
          {% elif feature.status == 'pending' %}
            En attente de publication
          {% elif feature.status == 'published' %}
            Publié
          {% elif feature.status == 'draft' %}
            Brouillon
          {% endif %}
        </div>
        <div>
          Type : <a href="{% url 'geocontrib:feature_type_detail' slug=project.slug feature_type_slug=feature.feature_type.slug %}"> {{ feature.feature_type.title }} </a>
        </div>
        <div>
          Dernière mise à jour : {{feature.updated_on|date:'d/m/Y' }}
        </div>
        {% if user.is_authenticated %}
          <div>
            Auteur : {{ feature.creator.first_name }} {{ feature.creator.last_name }}
          </div>
        {% endif %}
      `

      if (geomJSON.type === 'Point') {
        L.circleMarker(geomJSON.coordinates, {
          color: '{{ feature.feature_type.color }}',
          radius: 4,
          fillOpacity: 0.3,
          weight: 1
        }).bindPopup(popupContent).addTo(featureGroup)
      } else if (geomJSON.type === 'LineString') {
        L.polyline(geomJSON.coordinates, {
          color: '{{ feature.feature_type.color }}',
          weight: 1.5
        }).bindPopup(popupContent).addTo(featureGroup)
      } else if (geomJSON.type === 'Polygon') {
        L.polygon(geomJSON.coordinates, {
          color: '{{ feature.feature_type.color }}',
          weight: 1.5,
          fillOpacity: 0.3
        }).bindPopup(popupContent).addTo(featureGroup)
      }
    {% endfor %}
    map.addLayer(featureGroup);
    
    // fit maps to bound only if no initial zoom and center are defined
    if (lat === "" || lng === "" || zoom === "") {
      map.fitBounds(featureGroup.getBounds())
    }

    let geocoder;
    // Get the settings.py variable SELECTED_GEOCODER_PROVIDER. This way avoids XCC attacks
    const geocoderLabel = JSON.parse(document.getElementById('selected-provider').textContent);
    if (geocoderLabel) {
      const LIMIT_RESULTS = 5;

      // Load the geocoder specify in settings.py
      if (geocoderLabel === '{{ GEOCODER_PROVIDERS.ADDOK }}') {
        geocoder = L.Control.Geocoder.addok({limit: LIMIT_RESULTS});
      } else if (geocoderLabel === '{{ GEOCODER_PROVIDERS.PHOTON }}') {
        geocoder = L.Control.Geocoder.photon();
      } else if (geocoderLabel === '{{ GEOCODER_PROVIDERS.NOMINATIM }}') {
        geocoder = L.Control.Geocoder.nominatim();
      }

      var control = L.Control.geocoder({
        placeholder: 'Chercher une adresse...',
        geocoder: geocoder,
      }).addTo(map);
    }
  });
