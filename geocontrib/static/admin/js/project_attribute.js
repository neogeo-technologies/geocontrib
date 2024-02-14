/**
 * This script dynamically updates form inputs based on the selected field type in a Django admin interface.
 * It handles three types of fields: boolean, list, and multi-choice list. According to the selection, 
 * it either displays a checkbox (for boolean), a dropdown (for list), or multiple checkboxes (for multi-choice list).
 * It also updates a hidden input field with the selected values to ensure correct data submission.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Object to store elements of project attribute form
  let formEls = {};

  // Function to initialize form customization and listen for new inline form additions.
  function initializeFormsAndListeners() {
    initFormCustomization();
    initFilterFormCustomization();
    listenToEvents();
  };

  // Initializes forms customization.
  function initFormCustomization() {
    // Get references to the necessary HTML elements: field_type select box and options input field.
    formEls['fieldTypeSelect'] = document.getElementById('id_field_type');
    formEls['optionsInputField'] = document.getElementById('id_options');
    formEls['hiddenInputField'] = document.getElementById('id_default_value');

    // Hide forms not activated
    hideForms();

    // Exit the script if the hidden input field is not present on the page.
    if (!formEls.hiddenInputField) return;

    // Store the saved default value from the hidden input field.
    formEls['savedDefaultValue'] = formEls.hiddenInputField.value;

    // Hide the original input field as we will use custom inputs.
    formEls.hiddenInputField.hidden = true;

    // Create a new container for custom input elements (checkboxes or select lists).
    formEls['defaultValueCustomContainer'] = document.createElement('div');
    formEls.defaultValueCustomContainer.id = 'default_value_custom_container';

    // Insert the new container into the DOM after the hidden input field's parent element.
    formEls.hiddenInputField.parentElement.appendChild(formEls.defaultValueCustomContainer);

    // Call the function to update the form based on the current field type.
    updateDefaultValueInput();
  };

  // Function to update filter default value options
  function updateFilterValueChoices () {
    const options = formEls.optionsInputField.value.split(','); // Suppose que les options sont séparées par des virgules
    formEls.defaultFilterValueField.innerHTML = ''; // Efface les choix existants
    console.log(options);
    // Create a placeholder for te select (not working, should be present at page load, but still keep space and appears if no select)
    formEls.defaultFilterValueField.appendChild(createSelectPlaceholderElement());
    options.forEach(option => formEls.defaultFilterValueField.appendChild(createOptionElement(option)));
  };

  // Function to hide form elements
  function hideForms() {
    // Hide options in edition mode for boolean
    const disabledOptionsEl = document.getElementsByClassName('field-options');
    const fieldTypeEl = document.querySelector(".field-field_type div.readonly")
    if (disabledOptionsEl.length === 1 && fieldTypeEl && fieldTypeEl.textContent === "Booléen") {
      disabledOptionsEl[0].hidden = true;
    }
  };

  // Function to create a checkbox input element.
  function createCheckboxElement(id, value) {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    checkbox.name = 'custom_default_value';
    if (value) {
      checkbox.value = value;
    }
    // Attach an event listener to each checkbox.
    setEventListener(checkbox);
    return checkbox;
  };

  // Function to create a label element for inputs.
  function createLabelElement(id, text) {
    const optionLabel = document.createElement('label');
    optionLabel.setAttribute('for', id);
    optionLabel.textContent = '\n' + text + '\n';
    return optionLabel;
  };

  // Function to create an option element for select.
  function createOptionElement(option='') {
    const optionElt = document.createElement('option');
    optionElt.value = option;
    optionElt.text = option || 'Sélectionner une option';
    return optionElt;
  };

  // Function to create a placeholder to insert in select element (not working, should be present at page load, but still keep space and appears if no select)
  function createSelectPlaceholderElement() {
    const placeholderElt = createOptionElement();
    placeholderElt.setAttribute('selected', '');
    placeholderElt.setAttribute('hidden', '');
    return placeholderElt;
  }

  // Function to create a select dropdown for 'list' field type.
  function createSelectElement() {
    const selectElt = document.createElement('select');
    selectElt.name = 'custom_default_value';
    // Add a placeholder to the select element
    selectElt.appendChild(createSelectPlaceholderElement());
    // Split the options and create an option element for each.
    const options = formEls.optionsInputField.value.split(',').filter(val => val !== '');
    options.forEach(option => {
      const optionElt = createOptionElement(option);
      selectElt.appendChild(optionElt);
    });
    // Attach an event listener to the select element.
    setEventListener(selectElt);
    // Set the previously selected option, if any.
    if (formEls.savedDefaultValue) {
      selectElt.value = formEls.savedDefaultValue;
    }
    return selectElt;
  };

  // Function to create a list of checkboxes for 'multi_choices_list' field type.
  function createMultiSelectElement() {
    const multiSelectContainer = document.createElement('ul');
    const options = formEls.optionsInputField.value.split(',').filter(val => val !== '');
    options.forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElt = document.createElement('li');
      const label = createLabelElement(id, option);
      const checkbox = createCheckboxElement(id, option);
      // Check if the checkbox is in the saved default values.
      checkbox.checked = formEls.savedDefaultValue.split(',').includes(option);
      label.appendChild(checkbox);
      listElt.appendChild(label);
      multiSelectContainer.appendChild(listElt);
    });
    return multiSelectContainer;
  };

  // Function to update the hidden input field with the selected values.
  function updateDefaultValueHiddenInput() {
    const fieldType = formEls.fieldTypeSelect.value;
    switch(fieldType) {
      case 'boolean':
          const checkbox = document.querySelector('input[name="custom_default_value"]');
          formEls.hiddenInputField.value = checkbox.checked;
          break;
      case 'list':
          const select = document.querySelector('select[name="custom_default_value"]');
          formEls.hiddenInputField.value = select.value;      
          break;
      case 'multi_choices_list':
          const checkboxes = document.querySelectorAll('input[name="custom_default_value"]:checked');
          let values = Array.from(checkboxes).map(cb => cb.value);
          formEls.hiddenInputField.value = values.toString();
          break;
    }
  };

  // Function to attach change event listeners to custom input elements.
  function setEventListener(el) {
    el.addEventListener('change', function() {
      updateDefaultValueHiddenInput();
    });
  };

  // Main function to update the custom input elements based on the selected field type.
  function updateDefaultValueInput() {
    // Clear the custom container before adding new input elements.
    formEls.defaultValueCustomContainer.innerHTML = '';

    const fieldType = formEls.fieldTypeSelect.value;
    let formElement;
    switch(fieldType) {
        case 'boolean':
            // Hide the options field for the boolean type and create a checkbox.
            formEls.optionsInputField.parentElement.parentElement.hidden = true;
            formElement = createCheckboxElement('id_default_value');
            // Set the checkbox state based on the saved value.
            formElement.checked = formEls.savedDefaultValue === 'true';
            break;
        case 'list':
            // Show the options field for the list type and create a select dropdown.
            formEls.optionsInputField.parentElement.parentElement.hidden = false;
            formElement = createSelectElement();
            break;
        case 'multi_choices_list':
            // Show the options field for the multi-choice list type and create multiple checkboxes.
            formEls.optionsInputField.parentElement.parentElement.hidden = false;
            formElement = createMultiSelectElement();
            break;
    }
    if (formElement) {
      // Add the created form element to the custom container.
      formEls.defaultValueCustomContainer.appendChild(formElement);
      // Update the value of the hidden input field in case the user switches field type.
      updateDefaultValueHiddenInput();
    }
  };

  // *** FILTERS *** //
  function initFilterFormCustomization() {
    // Get references to the necessary HTML elements: default_filter_enabled checkbox & default_filter_value select.
    formEls['defaultFilterEnabledField'] = document.getElementById('id_default_filter_enabled');
    formEls['defaultFilterValueField'] = document.getElementById('id_default_filter_value');
    
    // Toggle immediately default filter value field at load
    toggleDefaultFilterValueField()
    // Update immediately choices at load
    updateFilterValueChoices();
  }
  
  function toggleDefaultFilterValueField() {
    formEls.defaultFilterValueField.parentElement.parentElement.hidden = !formEls.defaultFilterEnabledField.checked;
  }
  // *** GLOBAL *** //

  // Function to add event listeners
  function listenToEvents() {
    // Add event listener to update the form when the field type changes.
    formEls.fieldTypeSelect.addEventListener('change', function() {
      updateDefaultValueInput();
    });
    
    // Add event listener to update the form when the options change.
    formEls.optionsInputField.addEventListener('change', function() {
      updateDefaultValueInput();
      updateFilterValueChoices();
    });

    // Add event listener to toggle default filter select if activated
    formEls.defaultFilterEnabledField.addEventListener('change', function() {
      toggleDefaultFilterValueField();
    })
  }

  initializeFormsAndListeners(); // Kick off the process when the DOM is fully loaded.
});
