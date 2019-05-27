// mouse pointer
// # feature detail
$( document ).ready(function() {
  var element = document.getElementById("addcomment");
  element.style.cursor = "pointer";

  if(document.getElementById("mapdetail")){
    let mapdetail = new mapboxgl.Map({
              container: 'mapdetail', // container id
              style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
              center: [1.97, 47.14], // starting position [lng, lat]
              zoom: 4 // starting zoomx
    });
  }
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

// # modify feature
// modify type of cursor
var element = document.getElementById("modify_feature");
element.style.cursor = "pointer";
$("#modify_feature").on('click', function(e) {
    url = ''
    $.ajax({
      url: url,
      type: 'GET',
      success: function (data) {
          $('#feature_detail').html("");
          $('#edit_feature').html(data);
      },
      error: function(err) {
        console.log('Error occured', err);
      }
    });

});
