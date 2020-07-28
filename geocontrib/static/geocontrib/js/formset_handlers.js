window.addEventListener('load', function() {

  // ---------------------------------------------------------------------------
  // Suppression d'un ligne de formset
  // ---------------------------------------------------------------------------
  let removables = document.getElementsByClassName('remove-row');
  function RemoveIt(){

      let getter = this.getAttribute('id').replace('-REM', '')
      let hidden_input_delete = document.getElementById(''.concat('id_', getter, '-DELETE'));
      let current_row = document.getElementById(getter+'-ROW');

      hidden_input_delete.value = 'checked';
      current_row.style.display = 'none';
  };

  for (let i = 0; i < removables.length; i++) {
      removables[i].addEventListener('click', RemoveIt, false);
  }

  // ---------------------------------------------------------------------------
  // Ajout d'un ligne de formset
  // ---------------------------------------------------------------------------
  let add_buttons = document.getElementsByClassName('add_button');

  function AddRow(){
    let prefix = this.getAttribute('data-related-fieldset');
    let total_form = document.getElementById('id_'+prefix+'-TOTAL_FORMS')
    let form_idx = total_form.value;

    // Injection de l'indice de la ligne et ajout au formset
    let empty_tbody = document.getElementById(prefix+'-EMPTY_TBODY').innerHTML.replace(/__prefix__/g, form_idx);
    console.log(empty_tbody);
    let tbody = document.getElementById(prefix+'-TBODY').insertAdjacentHTML('beforeend', empty_tbody);


    // Ajout d'un event ciblant la nouvelle ancre de suppression
    let remove_field = document.getElementById(prefix+'-'+form_idx+'-REM');
    remove_field.addEventListener('click', RemoveIt, false);

    total_form.setAttribute("value", parseInt(form_idx) + 1);
    // total_form.value++
  };

  for (let i = 0; i < add_buttons.length; i++) {
    add_buttons[i].addEventListener('click', AddRow, false);
  }

});
