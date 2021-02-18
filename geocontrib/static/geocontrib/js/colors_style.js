window.addEventListener('load', function () {
  let field_types = document.querySelectorAll("input.field-type[value='list']");
  for (let i = 0; i < field_types.length; i++) {
    field_types[i].addEventListener('change', ReloadDropdown, false);
  }

  function ReloadDropdown () {
    console.log(this);
    LoadDropdown();
  }



  // let custom_style_button = document.getElementById('id_custom_style_button');
  // let init_button_inner = custom_style_button.innerHTML;
  // custom_style_button.onclick = function() {
  //   let styles_container = document.getElementById('id_style_container');
  //   if (styles_container.hasAttribute("hidden")) {
  //     custom_style_button.innerHTML = "<i class='ui cancel icon'></i>Annuler/Réinitialiser";
  //     styles_container.hidden = false;
  //     LoadDropdown();
  //   } else {
  //     styles_container.hidden = true;
  //     custom_style_button.innerHTML = init_button_inner;
  //   }
  //   // Cette element va recevoir les données à submit
  //   let json_input = document.getElementById('id_colors_style_textarea');
  // }

  function LoadDropdown () {
    // a déterminer qd cacher/montrer le container de style
    let styles_container = document.getElementById('id_style_container');
    styles_container.hidden = false;

    let list_label_selected = document.getElementById('id_list_label_selected');
    let list_menu = document.getElementById('id_list_menu')
    let all_field_type_list = document.querySelectorAll("input.field-type[value='list']")
    for (const field_type of all_field_type_list) {
      // si l'identifiant du champs n'est pas déjà
      // dans la dropdown on l'ajoute
      let list_id = field_type.id
      let already_exists = document.getElementById(list_id+"_styles")
      if (not already_exists) {

        let id_label = list_id.replace('field_type', 'label');
        let id_name = list_id.replace('field_type', 'name');
        let id_options = list_id.replace('field_type', 'options');
        let list_label = document.getElementById(id_label)
        let list_name = document.getElementById(id_name)

        // les options seront plutot charger au change de la liste de valeurs choisi
        // let list_options = document.getElementById(id_options)

        let item = document.createElement("div");
        item.id = list_id + '_styles';
        item.className = "item";
        item.setAttribute("data-value", list_name.value);
        item.innerHTML = list_label.value;
        list_menu.appendChild(item);

        // on charge les option au change de la liste de valeur choisi
        // LoadStyles(list_name, list_options);
      }
    }
  }

  function LoadStyles(list_name, options) {
    let list_options = options.value.split(",");
    let colors_selection = document.getElementById('id_colors_selection');
    colors_selection.hidden = false;

    let colors_panel = document.getElementById('id_colors_panel_'+list_name.value)
    if (colors_panel) {
      console.log('oops');
    } else {
      let colors_panel = document.createElement("div");
      colors_panel.className = "colors_panel"
      colors_panel.id = "id_colors_panel_" + list_name.value

      for (const option of list_options) {
        console.log(option);
        let input = document.createElement("input");
        input.type = "color";
        input.style = "width:100%;height:38px;";
        input.id = "id_color_" + option
        input.value = document.getElementById('id_color').value
        let label = document.createElement("label");
        label.for = input.id;
        label.innerHTML = option;
        colors_panel.appendChild(label);
        colors_panel.appendChild(input);
      }

      colors_selection.appendChild(colors_panel);
    }
  }

});
