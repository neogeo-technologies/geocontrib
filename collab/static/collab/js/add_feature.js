
$("#feature_type").change(function () {
    name = $("input[name=feature]").val();

    url = ''
    $.ajax({
      url: url,
      type: 'GET',
      data:{
        name: name
      },
      success: function (result) {
         $('#form_body').html(result);
      },
      error: function(err) {
        alert('Error occured', err);
      }
    });

});

$('.ui.selection.dropdown.feature')
  .dropdown()
;
