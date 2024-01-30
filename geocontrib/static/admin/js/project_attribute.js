document.addEventListener('DOMContentLoaded', function() {
  // Get references to the field_type select box, options, and the container for the default value
  const fieldTypeSelect = document.getElementById('id_field_type');
  const options = document.getElementById('id_options').value;
  const defaultValueContainer = document.getElementById('id_default_value').parentElement;
  const defaultValueLabel = document.getElementById('id_default_value').nextElementSibling;

  // Update the form input when the page loads
  updateDefaultValueInput();

  // Add an event listener to update the form input when the field type changes
  fieldTypeSelect.addEventListener('change', function() {
      updateDefaultValueInput();
  });

  // Function to generate a checkbox input element
  function generateCheckbox(id, value) {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    checkbox.name = 'default_value';
    checkbox.value = value;
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
  function generateCheckboxSelectMultiple(options) {
    const selectMultipleContainer = document.createElement('ul')
    selectMultipleContainer.id = 'id_default_value';
    options.forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElement = document.createElement('li');
      const label = generateLabel(id, option);
      const checkbox = generateCheckbox(id, option)
      label.appendChild(checkbox)
      listElement.appendChild(label);
      selectMultipleContainer.appendChild(listElement)
    });
    return selectMultipleContainer;
  };

  // Function to update the default value input based on the selected field type
  function updateDefaultValueInput() {
      defaultValueContainer.innerHTML = '';

      const fieldType = fieldTypeSelect.value;
      switch(fieldType) {
          case 'boolean':
              const checkbox = generateCheckbox('id_default_value');
              defaultValueContainer.appendChild(checkbox);
              defaultValueContainer.appendChild(defaultValueLabel);
              break;
          case 'list':
              const textField = document.createElement('input');
              textField.type = 'text';
              textField.id = 'id_default_value';
              textField.name = 'default_value';
              defaultValueContainer.appendChild(defaultValueLabel);
              defaultValueContainer.appendChild(textField);
              break;
          case 'multi_choices_list':
              const selectMultiple = generateCheckboxSelectMultiple(options.split(','));
              defaultValueContainer.appendChild(defaultValueLabel);
              defaultValueContainer.appendChild(selectMultiple);
              break;
          default:
              // Additional cases can be handled here if needed
      }
  }
});
