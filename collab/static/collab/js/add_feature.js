$('.ui.selection.dropdown.feature')
  .dropdown()
;

$('.ui.selection.dropdown.status')
  .dropdown()
;
// multiple datefield but need id not class TO DO
// $('[id^=date-field]').calendar({
//   type: 'date'
// });

$('.ui.checkbox.boolfield')
  .checkbox()
;

var mapaddfeature = new mapboxgl.Map({
          container: 'mapdaddfeature', // container id
          style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
          center: [1.97, 47.14], // starting position [lng, lat]
          zoom: 4 // starting zoomx
});
