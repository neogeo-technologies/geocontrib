$('.tabular.menu .item').tab();

$(document).ready(function() {
    var table = $('table.display').DataTable({
         "scrollX": true,
         "language": {
               "url": "../../../static/collab/js/datatables_french.json"
          },
          "columnDefs": [
            {"className": "dt-body-left", "targets": "_all"}
          ],
         "dom": 'frtip',
         "buttons": [
             {
                   extend: 'excel',
                   text: 'Excel',
                   exportOptions: {
                       modifier: {
                           page: 'current'
                       }
                   }
             },
             {
                   extend: 'print',
                   text: 'Imprimer',
                   exportOptions: {
                       modifier: {
                           page: 'current'
                       }
                   }
             },
             'csv',
            {
              extend: 'csv',
              text: 'Export CSV de tous les champs',
              exportOptions: {
                  modifier: {
                      selected: null
                  }
              }
           }
            // 'copy',   'pdf'
         ],
         "select": true
    });
} );


// $('.tabular.menu .item.carte').one('click', function() {
//     maplist = new mapboxgl.Map({
//               container: 'maplist', // container id
//               style: 'https://openmaptiles.geo.data.gouv.fr/styles/osm-bright/style.json', // stylesheet location
//               center: [1.97, 47.14], // starting position [lng, lat]
//               zoom: 4 // starting zoomx
//     });
//     var mapDiv = document.getElementById('maplist');
//     maplist._container = mapDiv;
//     maplist.on('load', function() {
//             maplist.resize();
//     });
//
// });
