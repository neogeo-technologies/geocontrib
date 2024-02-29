/**
 * This script enhances the Django admin interface for ProjectAttribute models by dynamically updating
 * form inputs based on the selected field type. It supports three types of fields: boolean, list, and
 * multi-choice list. Depending on the selected type, the script dynamically displays a checkbox, a dropdown,
 * or multiple checkboxes. It also ensures the correct values are captured and submitted by updating a
 * hidden input field. Additionally, the script manages conditional display of form elements based on
 * the attribute type and user interactions.
 */
document.addEventListener('DOMContentLoaded', function() {
  // *** GLOBAL *** //
  // Global object to store form element references for easy access and manipulation.
  let formEls = {};

  // Initializes the form by setting up customizations and event listeners for both
  // default value input and default filter input based on the field type.
  function initializeFormsAndListeners() {
    initDefaultValueFormCustomization();
    initDefaultFilterFormCustomization();
    listenToEvents(); // Sets up listeners for field type and options changes.
  };

  // Function to attach change event listeners to custom input elements.
  function setCustomFormEventListener(el, formName) {
    el.addEventListener('change', function() {
      if (formName === 'custom_default_value') {
        updateHiddenInputValue(formName, formEls.defaultValueHiddenInputField)
      } else if (formName === 'custom_default_filter') {
        updateHiddenInputValue(formName, formEls.defaultFilterHiddenInputField)
      }
    });
  };

  // Function to retrieve field_type from disabled field in edition mode
  function retrieveFieldValueInEditMode(fieldName) {
    const field = document.querySelector(`.field-${fieldName} div.readonly`);
    return field ? field.textContent: '';
  };

  // Get field type from input elements in creation mode otherwise from readonly element in edit mode
  function getFieldType() {
    return formEls.fieldTypeSelect ? formEls.fieldTypeSelect.value : retrieveFieldValueInEditMode('field_type');
  }

  // Get options from input elements in creation mode otherwise from readonly element in edit mode
  function getOptions() {
    let options = formEls.optionsInputField ? formEls.optionsInputField.value : retrieveFieldValueInEditMode('options');
    // Split the options string into an array, remove empty values and trim whitespace (for edition mode)
    return options.split(',').filter(val => val !== '').map(val => val.trim());
  }

  // Function to create a checkbox input element.
  function createCheckboxElement(id, formName, value) {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    checkbox.name = formName;
    if (value) {
      checkbox.value = value;
    }
    // Attach an event listener to each checkbox.
    setCustomFormEventListener(checkbox, formName);
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
  function createSelectElement(formName, recordedValue) {
    const selectElt = document.createElement('select');
    selectElt.name = formName;
    // Add a placeholder to the select element
    selectElt.appendChild(createSelectPlaceholderElement());
    // Add an option to unselect any values at beginning
    const emptyValueOptionElt = createOptionElement('Aucune');
    emptyValueOptionElt.value = '';
    selectElt.appendChild(emptyValueOptionElt);
    // Create an option element for each.
    getOptions().forEach(option => {
      const optionElt = createOptionElement(option);
      selectElt.appendChild(optionElt);
    });

    // Attach an event listener to the select element.
    setCustomFormEventListener(selectElt, formName);
    // Set the previously selected value, if any.
    if (recordedValue) {
      selectElt.value = recordedValue;
    }
    return selectElt;
  };
  
  // Function to create a list of checkboxes for 'multi_choices_list' field type.
  function createMultiSelectElement(formName, recordedValue) {
    const multiSelectContainer = document.createElement('ul');
    getOptions().forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElt = document.createElement('li');
      const label = createLabelElement(id, option);
      const checkbox = createCheckboxElement(id, formName, option);
      // Check if the checkbox is in the previously recorded value.
      checkbox.checked = recordedValue.split(',').includes(option);
      label.appendChild(checkbox);
      listElt.appendChild(label);
      multiSelectContainer.appendChild(listElt);
    });
    return multiSelectContainer;
  };

  // Function to create a custom form element to insert in its container
  function createCustomFormElement(fieldName, recordedValue) {
    const formName = 'custom_' + fieldName
    let formElement;
    switch(getFieldType()) {
        case 'boolean':
        case 'Booléen':
            formElement = createCheckboxElement('id_' + fieldName, formName);
            // Set the checkbox state based on the saved value.
            formElement.checked = recordedValue === 'true';
            break;
        case 'list':
        case 'Liste de valeurs':
            formElement = createSelectElement(formName, recordedValue);
            break;
        case 'multi_choices_list':
        case 'Liste à choix multiples':
            formElement = createMultiSelectElement(formName, recordedValue);
            break;
    }
    return formElement;
  };

  // Function to update the hidden input field with the selected values.
  function updateHiddenInputValue(formName, hiddenInputElt) {
    switch(getFieldType()) {
      case 'boolean':
      case 'Booléen':
          const checkbox = document.querySelector(`input[name="${formName}"]`);
          hiddenInputElt.value = checkbox.checked;
          break;
      case 'list':
      case 'Liste de valeurs':
          const select = document.querySelector(`select[name="${formName}"]`);
          hiddenInputElt.value = select.value;
          break;
      case 'multi_choices_list':
      case 'Liste à choix multiples':
          const checkboxes = document.querySelectorAll(`input[name="${formName}"]:checked`);
          let values = Array.from(checkboxes).map(cb => cb.value);
          hiddenInputElt.value = values.toString();
          break;
    }
  };

  // Function to toggle visibility of options form element
  function toggleOptionsForm() {
    if (formEls.fieldTypeSelect) {
      if (formEls.fieldTypeSelect.value === 'boolean') {
        formEls.optionsInputField.parentElement.parentElement.hidden = true;
      } else {
        formEls.optionsInputField.parentElement.parentElement.hidden = false;
      }
    }
  };

  // Function to add event listeners
  function listenToEvents() {
    // Add event listener to update the form when the field type changes.
    if (formEls.fieldTypeSelect) {
      formEls.fieldTypeSelect.addEventListener('change', function() {
        updateDefaultValueForm();
        updateDefaultFilterForm();
        toggleOptionsForm();
      });
    }
    
    // Add event listener to update the form when the options change.
    if (formEls.optionsInputField) {
      formEls.optionsInputField.addEventListener('change', function() {
        updateDefaultValueForm();
        updateDefaultFilterForm();
      });
    }

    // Add event listener to toggle default filter enabled checkbox
    if (formEls.displayFilterField) {
      formEls.displayFilterField.addEventListener('change', function() {
        toggleDefaultFilterEnabledDField();
      });
    }
  
    // Add event listener to toggle default filter value select if activated
    if (formEls.defaultFilterEnabledField) {
      formEls.defaultFilterEnabledField.addEventListener('change', function() {
        toggleDefaultFilterValueField();
      });
    }
  };

  // *** DEFAULT VALUE  *** //

  // Initializes forms customization.
  function initDefaultValueFormCustomization() {
    // Get references to the necessary HTML elements: field_type select box and options input field.
    formEls['fieldTypeSelect'] = document.getElementById('id_field_type');
    formEls['optionsInputField'] = document.getElementById('id_options');
    formEls['defaultValueHiddenInputField'] = document.getElementById('id_default_value');

    // Hide options in edition mode for boolean
    const disabledOptionsEl = document.getElementsByClassName('field-options');
    const fieldTypeEl = document.querySelector(".field-field_type div.readonly")
    if (disabledOptionsEl.length === 1 && fieldTypeEl && fieldTypeEl.textContent === "Booléen") {
      disabledOptionsEl[0].hidden = true;
    } else {
      // In creation mode, hide options field when field_type is boolean, else display it
      toggleOptionsForm();
    }

    // Exit the script if the hidden input field is not present on the page.
    if (!formEls.defaultValueHiddenInputField) return;

    // Store the saved default value from the hidden input field.
    formEls['recordedDefaultValue'] = formEls.defaultValueHiddenInputField.value;

    // Hide the original input field as we will use custom inputs.
    formEls.defaultValueHiddenInputField.hidden = true;

    // Create a new container for custom input elements (checkboxes or select lists).
    formEls['defaultValueCustomContainer'] = document.createElement('div');
    formEls.defaultValueCustomContainer.id = 'default_value_custom_container';


    // Insert the new container into the DOM after the hidden input field's parent element.
    formEls.defaultValueHiddenInputField.parentElement.appendChild(formEls.defaultValueCustomContainer);

    // Call the function to update the form based on the current field type.
    updateDefaultValueForm();
  };

  // Function to update the custom input elements based on the selected field type.
  function updateDefaultFilterForm() {
    const fieldName = 'default_filter';
    // Clear the custom container before adding new input elements.
    formEls.defaultFilterCustomContainer.innerHTML = '';
    // Create the custom form corresponding to the field_type
    const formElement = createCustomFormElement(fieldName, formEls.recordedDefaultFilter);
    if (formElement) {
      // Add the created form element to the custom container.
      formEls.defaultFilterCustomContainer.appendChild(formElement);
      // Update the value of the hidden input field in case the user switches field type.
      updateHiddenInputValue('custom_' + fieldName, formEls.defaultFilterHiddenInputField);
    }
  };

  // Function to update the custom input elements based on the selected field type.
  function updateDefaultValueForm() {
    // Clear the custom container before adding new input elements.
    formEls.defaultValueCustomContainer.innerHTML = '';
    const fieldName = 'default_value';
    // Create the custom form corresponding to the field_type
    const formElement = createCustomFormElement(fieldName, formEls.recordedDefaultValue);
    if (formElement) {
      // Add the created form element to the custom container.
      formEls.defaultValueCustomContainer.appendChild(formElement);
      // Update the value of the hidden input field in case the user switches field type.
      updateHiddenInputValue('custom_' + fieldName, formEls.defaultValueHiddenInputField)
    }
  };

  // *** FILTERS *** //
  function initDefaultFilterFormCustomization() {
    // Get references to the necessary HTML elements: display_filter checkbox, default_filter_enabled checkbox & default_filter_value select.
    formEls['displayFilterField'] = document.getElementById('id_display_filter');
    formEls['defaultFilterEnabledField'] = document.getElementById('id_default_filter_enabled');
    formEls['defaultFilterHiddenInputField'] = document.getElementById('id_default_filter_value');
    
    // Toggle immediately default filter enabled field at load
    toggleDefaultFilterEnabledDField()
    // Toggle immediately default filter value field at load
    toggleDefaultFilterValueField()

    // Exit the script if the hidden input field is not present on the page.
    if (!formEls.defaultFilterHiddenInputField) return;

    // Store the saved default value from the hidden input field.
    formEls['recordedDefaultFilter'] = formEls.defaultFilterHiddenInputField.value;

    // Hide the original input field as we will use custom inputs.
    formEls.defaultFilterHiddenInputField.hidden = true;

    // Create a new container for custom input elements (checkboxes or select lists).
    formEls['defaultFilterCustomContainer'] = document.createElement('div');
    formEls.defaultFilterCustomContainer.id = 'default_filter_custom_container';

    // Insert the new container into the DOM after the hidden input field's parent element.
    formEls.defaultFilterHiddenInputField.parentElement.appendChild(formEls.defaultFilterCustomContainer);

    // Call the function to update the form based on the current field type.
    updateDefaultFilterForm();
  };
  
  // Toggle visibility of default filter enabled row, depending on display filter checkbox
  function toggleDefaultFilterEnabledDField() {
    if (!formEls.defaultFilterEnabledField) return;
    formEls.defaultFilterEnabledField.parentElement.parentElement.hidden = !formEls.displayFilterField.checked;
    // Hiding activate default filter should hide as well default filter value selector
    toggleDefaultFilterValueField();
  };
  // Toggle visibility of default filter value row, depending on default filter activation checkbox
  function toggleDefaultFilterValueField() {
    if (!formEls.defaultFilterHiddenInputField) return;
    // if filter is not set to be displayed, hide the default filter value field
    // or if a filter is set to be displayed, but the default filter is not enabled, hide the default filter value field as well
    const isHidden = !formEls.displayFilterField.checked || !formEls.defaultFilterEnabledField.checked;
    formEls.defaultFilterHiddenInputField.parentElement.parentElement.hidden = isHidden;
  };

  // *** MAIN *** //

  initializeFormsAndListeners(); // Kick off the process when the DOM is fully loaded.
});
