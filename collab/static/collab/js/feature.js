// tabs
$('.menu .item')
  .tab()
;

// mouse pointer
// # feature detail
$( document ).ready(function() {
  // var element = document.getElementById("addcomment");
  // element.style.cursor = "pointer";

  if(document.getElementById("mapdetail")){
    let mapdetail = new mapboxgl.Map({
              container: 'mapdetail', // container id
              style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
              center: [1.97, 47.14], // starting position [lng, lat]
              zoom: 4 // starting zoomx
    });
  }
});
