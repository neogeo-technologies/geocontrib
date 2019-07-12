// tabs
$('.menu .item')
  .tab()
;

// search
$('.ui.search')
  .search({
    source: content
  })
;

$('.ui.checkbox.boolfield')
  .checkbox()
;

$('.ui.selection.dropdown.status')
  .dropdown()
;

$('.ui.calendar')
  .calendar()
;

// feature detail
$( document ).ready(function() {
  if(document.getElementById("mapdetail")){
    let mapdetail = new mapboxgl.Map({
              container: 'mapdetail', // container id
              style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
              center: [1.97, 47.14], // starting position [lng, lat]
              zoom: 4 // starting zoomx
    });
  }
});
