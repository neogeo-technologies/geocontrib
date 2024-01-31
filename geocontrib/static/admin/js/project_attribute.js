document.addEventListener('DOMContentLoaded', function() {
  // Get references to the field_type select box, options, and the container for the default value
  const fieldTypeSelect = document.getElementById('id_field_type');
  const optionsInputField = document.getElementById('id_options');
  const hiddenInputField = document.getElementById('id_default_value');
  if (!hiddenInputField) return
  const savedDefaultValue = hiddenInputField.value;

  // exit the script if the page doesn't contain the input field
  // hide the input field to store values in it
  hiddenInputField.hidden = true;

  // create a container for the custom inputs
  defaultValueCustomContainer = document.createElement('div');
  defaultValueCustomContainer.id = 'default_value_custom_container';
  // insert it after the label
  hiddenInputField.parentElement.appendChild(defaultValueCustomContainer);

  // Update the form input when the page loads
  updateDefaultValueInput();

  // Add an event listener to update the form input when the field type changes
  fieldTypeSelect.addEventListener('change', function() { // TODO : use at input
      updateDefaultValueInput();
  });

  console.log('optionsInputField', optionsInputField);
  // Add an event listener to update the form input when the options changes
  optionsInputField.addEventListener('change', function() {
      updateDefaultValueInput();
  });

  // Function to generate a checkbox input element
  function generateCheckbox(id, value) {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    checkbox.name = 'custom_default_value';
    if (value) checkbox.value = value;
    setEventListener(checkbox);
    return checkbox;
  };

  // Function to generate a label for an input element
  function generateLabel(id, text) {
    const optionLabel = document.createElement('label');
    optionLabel.setAttribute('for', id);
    optionLabel.textContent = '\n' + text + '\n';
    return optionLabel;
  };

  // Function to create a list of checkboxes for the 'multi_choices_list' option
  function generateCheckboxSelectMultiple() {
    const options = optionsInputField.value;
    const optionsArray = options.split(',').filter(val => val !== '');
    const selectMultipleContainer = document.createElement('ul')
    optionsArray.forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElement = document.createElement('li');
      const label = generateLabel(id, option);
      const checkbox = generateCheckbox(id, option);
      checkbox.checked = savedDefaultValue.split(',').includes(option)
      label.appendChild(checkbox)
      listElement.appendChild(label);
      selectMultipleContainer.appendChild(listElement)
    });
    return selectMultipleContainer;
  };

  function updateDefaultValueHiddenInput() {
    const fieldType = fieldTypeSelect.value;
    switch(fieldType) {
      case 'boolean':
          const checkbox = document.querySelector('input[name="custom_default_value"]');
          hiddenInputField.value = checkbox.checked;
          break;
      case 'list':
          // TODO : get value
          break;
      case 'multi_choices_list':
          const checkboxes = document.querySelectorAll('input[name="custom_default_value"]:checked');
          let values = Array.from(checkboxes).map(cb => cb.value);
          hiddenInputField.value = values.toString();
          break;
      default:
          // Additional cases can be handled here if needed
  }  };

  function setEventListener(el) {
      // Add an event listener to update the hidden input values when a selection occurs
      el.addEventListener('change', function() {
        updateDefaultValueHiddenInput();
    });
  }

  // Function to update the default value input based on the selected field type
  function updateDefaultValueInput() {
    defaultValueCustomContainer.innerHTML = '';

      const fieldType = fieldTypeSelect.value;
      switch(fieldType) {
          case 'boolean':
              const checkbox = generateCheckbox('id_default_value');
              checkbox.checked = savedDefaultValue;
              defaultValueCustomContainer.appendChild(checkbox);
              break;
          case 'list':
              // TODO: create a select element
              const textField = document.createElement('input');
              textField.type = 'text';
              textField.id = 'id_default_value';
              textField.name = 'default_value';
              defaultValueCustomContainer.appendChild(textField);
              break;
          case 'multi_choices_list':
              const selectMultiple = generateCheckboxSelectMultiple();
              defaultValueCustomContainer.appendChild(selectMultiple);
              break;
          default:
              // Additional cases can be handled here if needed
      }
      // update value to save when changing data type (in case user save the form after switching field type without selecting a new default value)
      updateDefaultValueHiddenInput()
  }
});
