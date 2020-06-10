window.addEventListener("load", function() {

  (function($) {

    $('#add_more').click(function () {
      let total_form = $('#id_form-TOTAL_FORMS');
      let form_idx = total_form.val();

      $('#formset_wrapper').append(
          $('#emptyform_wrapper').html().replace(/__prefix__/g, form_idx)
        );
      total_form.val(parseInt(form_idx)+1);
    });

  })(django.jQuery);

});
