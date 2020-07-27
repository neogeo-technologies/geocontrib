window.addEventListener('load', function() {

  // ---------------------------------------------------------------------------
  // Suppression d'un form
  // ---------------------------------------------------------------------------
  let form_deleters = document.querySelectorAll("div[data-delete-form]");

  function RemoveIt() {
    let data_segment_attr = this.getAttribute('data-delete-form').replace('-DELETE', '-SEGMENT');
    let data_segment = document.querySelector("div[data-segment='" + data_segment_attr + "']")
    let hidden_input_delete = document.getElementById("id_" + this.getAttribute('data-delete-form'))

    hidden_input_delete.checked = true;
    data_segment.style.display = 'none';
  };

  for (let i = 0; i < form_deleters.length; i++) {
    form_deleters[i].addEventListener('click', RemoveIt, false);
  }

  // ---------------------------------------------------------------------------
  // Ajout d'un form
  // ---------------------------------------------------------------------------
  let form_creators = document.querySelectorAll("a[data-add-form]");

  function AddIt() {
    let prefix = this.getAttribute('data-add-form').replace('-ADD', '');
    let total_forms = document.getElementById('id_' + prefix + '-TOTAL_FORMS')

    let form_idx = total_forms.value;

    let segments = document.querySelector("div[data-segments=" + prefix + "-SEGMENTS]");

    // TODO:
    // Si form vide de context layers
    // on index le bouton de suppression de couche en fonction du TOTAL_FORMS de contextlayer
    // on increment ensuite ce TOTAL_FORMS de contextlayer
    if (prefix.startsWith('contextlayer')){
      // <input type="hidden" name="contextlayer-basemap_set-1-contextlayer_set-TOTAL_FORMS" value="0" id="id_contextlayer-basemap_set-1-contextlayer_set-TOTAL_FORMS">
      // let contextlayer_total_forms = document.getElementById('id_' + prefix + '-TOTAL_FORMS')
    }

    let new_form = document.querySelector("div[data-empty-form=" + prefix + "-EMPTY]").innerHTML.replace(/__prefix__/g, form_idx);
    let add_form = document.querySelector("div[data-segments=" + prefix + "-SEGMENTS]").insertAdjacentHTML('beforeend', new_form);

    // Scroll sur le nouveau form
    let element = document.querySelector("div[data-segments=" + prefix + "-SEGMENTS]")
    element.scrollIntoView({block: "end"});


    // Ajout d'un event ciblant la nouvelle ancre de suppression
    let remove_field = document.querySelector("div[data-delete-form=" + prefix + "-" + form_idx + "-DELETE]");
    remove_field.addEventListener('click', RemoveIt, false);

    total_forms.value++

    // Ajout d'un event ciblant de potentiels boutons d'ajout
    // vrai lorsqu'on crée un nouveau basemap et son les contextlayer imbriqué
    if (prefix.startsWith('basemap')){
      let sub_creators = document.querySelectorAll("a[data-add-form]");
      for (let i = 0; i < sub_creators.length; i++) {
        sub_creators[i].addEventListener('click', AddIt, false);
      }
    }

  }
  for (let i = 0; i < form_creators.length; i++) {
    form_creators[i].addEventListener('click', AddIt, false);
  }

})
