window.addEventListener('load', function() {

  // ---------------------------------------------------------------------------
  // Suppression d'un ligne de formset
  // ---------------------------------------------------------------------------
  var removables = document.getElementsByClassName('remove-row');
  var RemoveIt = function() {

      var getter = this.getAttribute('id').replace('-REM', '')
      var hidden_input_delete = document.getElementById('id_'+getter+'-DELETE');
      var current_row = document.getElementById(getter+'-ROW');

      hidden_input_delete.value = 'checked';
      current_row.style.display = 'none';
  };

  for (var i = 0; i < removables.length; i++) {
      removables[i].addEventListener('click', RemoveIt, false);
  }

  // ---------------------------------------------------------------------------
  // Ajout d'un ligne de formset
  // ---------------------------------------------------------------------------
  var add_buttons = document.getElementsByClassName('add_button');

  var AddRow = function() {
    var prefix = this.getAttribute('data-related-fieldset');
    var total_form = document.getElementById('id_'+prefix+'-TOTAL_FORMS')
    var form_idx = total_form.value;

    // Injection de l'indice de la ligne et ajout au formset
    var empty_tbody = document.getElementById(prefix+'-EMPTY_TBODY').innerHTML.replace(/__prefix__/g, form_idx);
    var tbody = document.getElementById(prefix+'-TBODY').insertAdjacentHTML('beforeend', empty_tbody);


    // Ajout d'un event ciblant la nouvelle ancre de suppression
    var remove_field = document.getElementById(prefix+'-'+form_idx+'-REM');
    remove_field.addEventListener('click', RemoveIt, false);

    total_form.setAttribute("value", parseInt(form_idx) + 1);
    // total_form.value++
  };

  for (var i = 0; i < add_buttons.length; i++) {
      add_buttons[i].addEventListener('click', AddRow, false);
  }

});
