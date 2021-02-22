function LoadDropdown () {
  let styles_container = document.getElementById('id_style_container');
  let list_menu = document.getElementById('id_list_menu');
  let all_field_type_list = document.querySelectorAll("input.field-type[value='list']");
  let all_field_options = document.getElementsByClassName('options-field');

  // On vérifie si il existe des champs de type 'list'
  // et on affiche ou cache le conteneur
  let all_field_type_list_values = Array.from(all_field_type_list).map(el => el.value);
  let all_field_options_values = Array.from(all_field_options).map(el => el.value);
  if (!all_field_type_list_values.find(el => el === 'list') || !all_field_options_values.some(el => el.length !== 0)) {
    styles_container.style.display = 'none';
  } else {
    styles_container.style.display = '';
  }

  for (const field_type of all_field_type_list) {
    // si l'identifiant du champs n'est pas déjà
    // dans la dropdown on l'ajoute
    let list_id = field_type.id
    let already_exists = document.getElementById(list_id+"_styles");
    let options = document.getElementById(list_id.replace('field_type', 'options'));

    if (!already_exists && options.value.length) {
      let id_label = list_id.replace('field_type', 'label');
      let id_name = list_id.replace('field_type', 'name');
      let list_label = document.getElementById(id_label);
      let list_name = document.getElementById(id_name);

      let item = document.createElement("div");
      item.id = list_id + '_styles';
      item.className = "item";
      item.setAttribute("data-value", list_name.value);
      item.innerHTML = list_label.value;
      list_menu.appendChild(item);
    } else if (already_exists && options.value.length) {
      let id_label = list_id.replace('field_type', 'label');
      let id_name = list_id.replace('field_type', 'name');
      let list_label = document.getElementById(id_label);
      let list_name = document.getElementById(id_name);

      let item = document.getElementById(list_id + '_styles');
      item.className = "item";
      item.setAttribute("data-value", list_name.value);
    }
  }

  // On rafraichit les couleurs des options
  let field_type_selection = document.getElementById('id_list_selection').getElementsByTagName('input')[0];
  refreshColorSelection = displayColorSelection.bind(field_type_selection);
  refreshColorSelection();

  // On enlève les veleurs qui n'existent plus
  const all_field_type_list_arr = Array.from(all_field_type_list);
  const all_field_options_arr = Array.from(all_field_options);

  const all_field_type_ids = all_field_type_list_arr.map(el => el.id);

  for (const item of Array.from(list_menu.getElementsByClassName('item'))) {

    const value = item.id.replace('_styles', '');
    const options = all_field_options_arr.find(el => el.id === item.id.replace('field_type_styles', 'options')).value;

    if (!all_field_type_ids.find(el => el === value)) {
      list_menu.removeChild(item);
    } else if (!options.length) {
      list_menu.removeChild(item);
    }
  }
}

function initColorDisplay() {
  let colors_selection_container = document.getElementById('id_colors_selection');
  colors_selection_container.hidden = false;
  colors_selection_container.innerHTML = '';

  let styleData = JSON.parse(document.getElementById('id_colors_style').value);
  if (Object.keys(styleData.colors).length) {
    for (const [label, color] of Object.entries(styleData.colors)) {
      const colorDiv = document.createElement('div');
      colorDiv.classList.add('color-input')
      const colorLabel = document.createElement('label');
      colorLabel.innerHTML = label;
      const colorInput = document.createElement('input');
      colorInput.type = 'color';
      colorInput.value = color;
      colorDiv.appendChild(colorLabel);
      colorDiv.appendChild(colorInput);
      colors_selection_container.appendChild(colorDiv);
    }
  }

  let color_selection_fields = document.getElementsByClassName('color-input');
  for (let color_field of color_selection_fields) {
    let color_input = color_field.getElementsByTagName('input')[0];
    color_input.addEventListener('change', saveStyle, false)
  }
}

function displayColorSelection() {
  let styleData = JSON.parse(document.getElementById('id_colors_style').value);
  let colors_selection_container = document.getElementById('id_colors_selection');

  if (this.value && this.value !== styleData.custom_field_name) {
    colors_selection_container.hidden = false;
    colors_selection_container.innerHTML = '';

    let selection = document.getElementById('id_list_selection').querySelector(`[data-value=${this.value}]`);
    let id_options = selection.id.replace('field_type_styles', 'options');
    let options = document.getElementById(id_options).value.split(',');
    for (let option of options) {
      const colorDiv = document.createElement('div');
      colorDiv.classList.add('color-input')
      const colorLabel = document.createElement('label');
      colorLabel.innerHTML = option;
      const colorInput = document.createElement('input');
      colorInput.type = 'color';
      colorDiv.appendChild(colorLabel);
      colorDiv.appendChild(colorInput);
      colors_selection_container.appendChild(colorDiv);
    }

    let color_selection_fields = document.getElementsByClassName('color-input');
    for (let color_field of color_selection_fields) {
      let color_input = color_field.getElementsByTagName('input')[0];
      color_input.addEventListener('change', saveStyle, false)
    }
  } else if (this.value) {
    let selection = document.getElementById('id_list_selection').querySelector(`[data-value=${this.value}]`);
    let id_options = selection.id.replace('field_type_styles', 'options');
    let options = document.getElementById(id_options).value.split(',');
    let colors = Object.values(styleData.colors);
    colors_selection_container.innerHTML = '';

    for (let [index, option] of options.entries()) {
      const colorDiv = document.createElement('div');
      colorDiv.classList.add('color-input');
      const colorLabel = document.createElement('label');
      colorLabel.innerHTML = option;
      const colorInput = document.createElement('input');
      colorInput.type = 'color';
      if (colors[index]) {
        colorInput.value = colors[index];
      }
      colorDiv.appendChild(colorLabel);
      colorDiv.appendChild(colorInput);
      colors_selection_container.appendChild(colorDiv);
    }
  } else {
    initColorDisplay();
  }
}

function saveStyle() {
  let savingArea = document.getElementById('id_colors_style');
  let styleData = {
    custom_field_name: '',
    colors: {}
  }

  let customFieldName = document.getElementById('id_list_selection').getElementsByClassName('item active selected')[0];
  styleData.custom_field_name = customFieldName.getAttribute('data-value');

  for (let color_field of document.getElementsByClassName('color-input')) {
    let label = color_field.getElementsByTagName('label')[0].innerHTML;
    let color = color_field.getElementsByTagName('input')[0].value;
    styleData.colors[label] = color;
  }
  savingArea.value = JSON.stringify(styleData);
}

function disableListDropdown() {
  let requiredInputs= Array.from(this.getElementsByClassName('two fields')[0].getElementsByTagName('input'));
  valueLengths = requiredInputs.map(el => el.value.length);
  if (valueLengths.every(el => el !== 0)) {
    this.getElementsByClassName('ui selection dropdown')[0].classList.remove('disabled');
  } else {
    this.getElementsByClassName('ui selection dropdown')[0].classList.add('disabled');
  }
}

window.addEventListener('load', function () {

  LoadDropdown();

  // On parcoure les formets de champs personnalisé
  let personnalizedFields = document.getElementsByClassName('pers-field');
  // Dans chaque formset, on récupère l'input du dropdown 'Type de champ'
  // et on met l'event dessus
  for (let field of personnalizedFields) {
    let disableListDropdownBinded = disableListDropdown.bind(field);
    disableListDropdownBinded();

    field.addEventListener('input', disableListDropdown, false);
    let listDropdown = field.getElementsByClassName('ui selection dropdown')[0].getElementsByTagName('input')[0];
    const id = listDropdown.id;
    let optionsInput = document.getElementById(id.replace('field_type', 'options'));
    optionsInput.addEventListener('input', LoadDropdown, false);
  }

  let field_type_selection = document.getElementById('id_list_selection').getElementsByTagName('input')[0];
  field_type_selection.addEventListener('change', displayColorSelection, false);

  // On affiche les sélecteurs de couleurs si on a style enregistré
  let styleData = JSON.parse(document.getElementById('id_colors_style').value);
  if (styleData.custom_field_name.length) {
    let customFieldInput = document.getElementById('id_list_selection').getElementsByTagName('input')[0];
    let customFieldText = document.getElementById('id_list_selection').getElementsByClassName('text')[0];
    let customFieldItems = document.getElementById('id_list_selection').getElementsByClassName('item');
    for (let item of customFieldItems) {
      if (item.dataset.value === styleData.custom_field_name) {
        item.classList.add('active', 'selected');
        customFieldInput.value = styleData.custom_field_name;
        customFieldText.innerHTML = item.innerHTML;
      }
    }
    let initColorDisplayBinded = initColorDisplay.bind(field_type_selection);
    initColorDisplayBinded();
  }
});

document.addEventListener('add-field', function () {
  // On parcoure les formets de champs personnalisé
  let personnalizedFields = document.getElementsByClassName('pers-field');
  // Dans chaque formset, on récupère l'input du dropdown 'Type de champ'
  // et on met les events dessus
  for (let field of personnalizedFields) {
    field.addEventListener('input', disableListDropdown, false);

    let listDropdown = field.getElementsByClassName('ui selection dropdown')[0].getElementsByTagName('input')[0];
    const id = listDropdown.id;
    let optionsInput = document.getElementById(id.replace('field_type', 'options'));
    optionsInput.addEventListener('input', LoadDropdown, false);
  }

  let field_type_selection = document.getElementById('id_list_selection').getElementsByTagName('input')[0];
  field_type_selection.addEventListener('change', displayColorSelection, false);
});
