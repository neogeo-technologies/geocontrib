/**
 * This script dynamically updates form inputs based on the selected field type in a Django admin interface.
 * It handles three types of fields: boolean, list, and multi-choice list. According to the selection, 
 * it either displays a checkbox (for boolean), a dropdown (for list), or multiple checkboxes (for multi-choice list).
 * It also updates a hidden input field with the selected values to ensure correct data submission.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Object to store configurations for each project attribute form by field ID.
  let projectAttributeForms = {};

  // Function to initialize form customization and listen for new inline form additions.
  function initializeFormsAndListeners() {
    listenToNewFormAdditions();
    
    // Delay to ensure DOM elements are fully loaded before customization.
    setTimeout(() => {
      document.querySelectorAll('.dynamic-projectattributeassociation_set').forEach(formElement => {
        const fieldId = extractFieldId(formElement.id);
        initFormCustomization(fieldId);
      });
    }, 100);
  }

  // Initializes customization for a new or existing form identified by fieldId.
  function initFormCustomization(fieldId) {
    // Get references to the necessary HTML elements: attribute field select box and input field.
    const attributeFieldSelect = document.getElementById(`id_projectattributeassociation_set-${fieldId}-attribute`);
    
    const hiddenInputField = document.getElementById(`id_projectattributeassociation_set-${fieldId}-value`);
    
    // Exit the script if the hidden input field is not present on the page.
    if (!hiddenInputField) return;
    
    // Store the saved default value from the hidden input field.
    const savedValue = hiddenInputField.value;
    
    // Hide the original input field as we will use custom inputs.
    hiddenInputField.hidden = true;
    
    // Create a new container for custom input elements (checkboxes or select lists).
    const valueCustomContainer = document.createElement('div');
    valueCustomContainer.id = 'value_custom_container';
    
    // Insert the new container into the DOM after the hidden input field's parent element.
    hiddenInputField.parentElement.appendChild(valueCustomContainer);
    // Create a new entry for this field id in project attribute forms to keep track
    projectAttributeForms[fieldId] = { attributeFieldSelect, valueCustomContainer, hiddenInputField, savedValue }

    // Call the function to update the form based on the current field type.
    updateDefaultValueInput(fieldId);
    
    // Add event listener to update the form when the attribute field changes.
    attributeFieldSelect.addEventListener('change', function() {
      updateDefaultValueInput(fieldId);
    });
  }

  // Extracts the field ID from the given element ID.
  function extractFieldId(elementId) {
    return elementId.match(/\d+/)[0]; // Matches the first sequence of digits in the ID.
  }

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

  // Function to create a checkbox input element.
  function createCheckboxElement(fieldId, id, value) {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    checkbox.name = 'custom_default_value';
    if (value) {
      checkbox.value = value;
    }
    // Attach an event listener to each checkbox.
    setEventListener(checkbox, fieldId);
    return checkbox;
  };

  // Function to create a select dropdown for 'list' field type.
  function createSelectElement(fieldId, options, savedValue) {
    const selectElt = document.createElement('select');
    selectElt.name = 'custom_default_value';
    // Create a placeholder for te select (not working, should be present at page load, but still keep space and appears if no select)
    const placeholderElt = createOptionElement();
    placeholderElt.setAttribute('selected', '');
    placeholderElt.setAttribute('hidden', '');
    selectElt.appendChild(placeholderElt);
    // Create an option element for each.
    options.forEach(option => {
      const optionElt = createOptionElement(option);
      selectElt.appendChild(optionElt);
    });
    // Attach an event listener to the select element.
    setEventListener(selectElt, fieldId);
    // Set the previously selected option, if any.
    if (savedValue) {
      selectElt.value = savedValue;
    }
    return selectElt;
  };

  // Function to create a list of checkboxes for 'multi_choices_list' field type.
  function createMultiSelectElement(fieldId, options, savedValue) {
    const multiSelectContainer = document.createElement('ul');
    options.forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElt = document.createElement('li');
      const label = createLabelElement(id, option);
      const checkbox = createCheckboxElement(fieldId, id, option);
      // Check if the checkbox is in the saved default values.
      checkbox.checked = savedValue.split(',').includes(option);
      label.appendChild(checkbox);
      listElt.appendChild(label);
      multiSelectContainer.appendChild(listElt);
    });
    return multiSelectContainer;
  };

  // Function to update the hidden input field with the selected values.
  function updateDefaultValueHiddenInput(fieldId) {
    const { attributeFieldSelect, hiddenInputField, valueCustomContainer } = projectAttributeForms[fieldId];
    const attributeData = attributesData.find((el) => el.id === Number.parseInt(attributeFieldSelect.value));
    if (!attributeData) return;
  
    switch(attributeData.field_type) {
      case 'boolean':
          const checkbox = valueCustomContainer.querySelector('input[name="custom_default_value"]');
          hiddenInputField.value = checkbox.checked;
          break;
      case 'list':
          const select = valueCustomContainer.querySelector('select[name="custom_default_value"]');
          hiddenInputField.value = select.value;      
          break;
      case 'multi_choices_list':
          const checkboxes = valueCustomContainer.querySelectorAll('input[name="custom_default_value"]:checked');
          let values = Array.from(checkboxes).map(cb => cb.value);
          hiddenInputField.value = values.toString();
          break;
    }
  };

  // Function to attach change event listeners to custom input elements.
  function setEventListener(el, fieldId) {
    el.addEventListener('change', function() {
      updateDefaultValueHiddenInput(fieldId);
    });
  }

  // Main function to update the custom input elements based on the selected project attribute.
  function updateDefaultValueInput(fieldId) {
    // Get datas for this form
    const { attributeFieldSelect, valueCustomContainer, savedValue } = projectAttributeForms[fieldId];
    
    const attributeData = attributesData.find((el) => el.id === Number.parseInt(attributeFieldSelect.value));
    if (!attributeData) return;
    const { options, field_type } = attributeData;
    
    // Clear the custom container before adding new input elements.
    valueCustomContainer.innerHTML = '';
    let formElement;
    switch(field_type) {
        case 'boolean':
            formElement = createCheckboxElement(fieldId, 'id_default_value');
            // Set the checkbox state based on the saved value.
            formElement.checked = savedValue === 'true';
            break;
        case 'list':
            formElement = createSelectElement(fieldId, options, savedValue);
            break;
        case 'multi_choices_list':
            formElement = createMultiSelectElement(fieldId, options, savedValue);
            break;
    }
    if (formElement) {
      // Add the created form element to the custom container.
      valueCustomContainer.appendChild(formElement);
      // Update the value of the hidden input field in case the user switches project attribute.
      updateDefaultValueHiddenInput(fieldId);
    }
  }

  // Observes the DOM for new inline form additions and initializes customization for each.
  function listenToNewFormAdditions() {
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(addedNode => {
          if (addedNode.nodeType === Node.ELEMENT_NODE && addedNode.classList.contains('dynamic-projectattributeassociation_set')) {
            const newFieldId = extractFieldId(addedNode.id);
            initFormCustomization(newFieldId);
          }
        });
      });
    });

    const config = { childList: true, subtree: true };
    const targetNode = document.querySelector('#projectattributeassociation_set-group');
    if (targetNode) observer.observe(targetNode, config);
  }

  initializeFormsAndListeners(); // Kick off the process when the DOM is fully loaded.
});
