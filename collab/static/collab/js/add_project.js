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
