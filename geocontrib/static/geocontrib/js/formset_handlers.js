window.addEventListener("load", function() {

  // Suppression d'un ligne de formset
  var removables = document.getElementsByClassName("remove-field");
  var RemoveIt = function() {
      var id_remove_field = this.getAttribute("id")
      var id_delete_checkbox = id_remove_field.replace('REM', 'DELETE')
      var checkbox = document.getElementById(id_delete_checkbox);

      checkbox.setAttribute("checked", true);
      this.parentNode.parentNode.style.display = 'none';

  };

  for (var i = 0; i < removables.length; i++) {
      removables[i].addEventListener('click', RemoveIt, false);
  }
  // -----------------------------------------------------------

  // Ajout d'un ligne de formset
  var add_buttons = document.getElementsByClassName("add_button");

  var AddRow = function() {
    var formset_prefix = this.getAttribute("for");
    var total_form = document.getElementById('id_'+formset_prefix+'-TOTAL_FORMS')
    var form_idx = total_form.value;
    var new_row_content = document.getElementsByClassName(
        formset_prefix+'__empty__body')[0].innerHTML.replace(/__prefix__/g, form_idx)
    var content = document.createTextNode(new_row_content);

    document.getElementsByClassName(
      formset_prefix+'__table__tbody')[0].insertAdjacentHTML('beforeend', new_row_content);

    // Ajout d'un de RemoveIt ciblant le nouveau ancre de suppression
    document.getElementById('id_'+formset_prefix+'-'+form_idx+'-REM').addEventListener('click', RemoveIt, false);

    total_form.setAttribute("value", parseInt(form_idx) + 1)
    // total_form.value++
  };

  for (var i = 0; i < add_buttons.length; i++) {
      add_buttons[i].addEventListener('click', AddRow, false);
  }
  // -----------------------------------------------------------

});
