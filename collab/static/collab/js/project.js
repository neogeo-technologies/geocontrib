// ADD PROJECT add_project.html
$('.ui.selection.dropdown.feature')
  .dropdown()
;

// multiple datefield but need id not class TO DO
// $('[id^=date-field]').calendar({
//   type: 'date'
// });

$('.ui.checkbox.boolfield')
  .checkbox()
;

$(".iconfile").click(function() {
  $(this).parent().find("input:file").click();
});

$('input:file', '.ui.action.input')
  .on('change', function(e) {
    var name = e.target.files[0].name;
    $('input:text', $(e.target).parent()).val(name);
  });


  // form validation
  $('.addproject')
    .form({
      fields: {
        title:  {
          identifier: 'title',
          rules: [
            {
              type   : 'empty',
              prompt : 'Veuillez entrer un titre pour ce projet'
            }
          ]
        },
        visi_feature:  {
          identifier: 'visi_feature',
          rules: [
            {
              type   : 'empty',
              prompt : 'Veuillez choisir une visibilité pour les signalements publiés'
            }
          ]
        },
        visi_archive:  {
          identifier: 'visi_archive',
          rules: [
            {
              type   : 'empty',
              prompt : 'Veuillez choisir une visibilité pour les signalements archivés'
            }
          ]
        },
        illustration:  {
          identifier: 'illustration',
          rules: [
            {
              type   : 'empty',
              prompt : 'Veuillez choisir une illustration pour ce projet'
            }
          ]
        },
      }
    })
  ;
