// mouse pointer

var element = document.getElementById("addcomment");
element.style.cursor = "pointer";

let mapdetail = new mapboxgl.Map({
          container: 'mapdetail', // container id
          style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
          center: [1.97, 47.14], // starting position [lng, lat]
          zoom: 4 // starting zoomx
});


$(function(){
	$("#addcomment").click(function(){
		$(".comment").modal('show');
	});
	$(".comment").modal({
		closable: true
	});
});

$('.comment_form')
  .form({
    fields: {
      comment     :  {
        identifier: 'comment',
        rules: [
          {
            type   : 'empty',
            prompt : 'Veuillez entrer un commentaire'
          }
        ]
      }
    }
  })
;
