/**
 * This script dynamically updates form inputs based on the selected field type in a Django admin interface.
 * It handles three types of fields: boolean, list, and multi-choice list. According to the selection, 
 * it either displays a checkbox (for boolean), a dropdown (for list), or multiple checkboxes (for multi-choice list).
 * It also updates a hidden input field with the selected values to ensure correct data submission.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Create an object to store data for each project attribute form
  let projectAttributeForms = {};
  let currentFieldId;

  listenToNewForm()
  // Update forms at load if several already created previously
  setTimeout(() => {
    for (const formEl of document.getElementsByClassName('dynamic-projectattributeassociation_set')) {
      currentFieldId = formEl.id.slice(-1);
      initNewForm()
    }
  }, 100);

  function initNewForm() {
    // Get references to the necessary HTML elements: attribute field select box and input field.
    const attributeFieldSelect = document.getElementById(`id_projectattributeassociation_set-${currentFieldId}-attribute`);
    
    const hiddenInputField = document.getElementById(`id_projectattributeassociation_set-${currentFieldId}-value`);
    
    // Exit the script if the hidden input field is not present on the page.
    if (!hiddenInputField) return;
    
    // Store the saved default value from the hidden input field.
    const savedDefaultValue = hiddenInputField.value;
    
    // Hide the original input field as we will use custom inputs.
    hiddenInputField.hidden = true;
    
    // Create a new container for custom input elements (checkboxes or select lists).
    const defaultValueCustomContainer = document.createElement('div');
    defaultValueCustomContainer.id = 'default_value_custom_container';
    
    // Insert the new container into the DOM after the hidden input field's parent element.
    hiddenInputField.parentElement.appendChild(defaultValueCustomContainer);
    // Create a new entry for this field id in project attribute forms to keep track
    projectAttributeForms[currentFieldId] = { attributeFieldSelect, defaultValueCustomContainer, hiddenInputField, savedDefaultValue }

    // Call the function to update the form based on the current field type.
    updateDefaultValueInput();
    
    // Add event listener to update the form when the attribute field changes.
    attributeFieldSelect.addEventListener('change', function() {
      updateDefaultValueInput();
    });
  }

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

  // Function to create a select dropdown for 'list' field type.
  function createSelectElement(options, savedDefaultValue) {
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
    setEventListener(selectElt);
    // Set the previously selected option, if any.
    if (savedDefaultValue) {
      selectElt.value = savedDefaultValue;
    }
    return selectElt;
  };

  // Function to create a list of checkboxes for 'multi_choices_list' field type.
  function createMultiSelectElement(options, savedDefaultValue) {
    const multiSelectContainer = document.createElement('ul');
    options.forEach((option, index) => {
      const id = 'id_default_value_' + index;
      const listElt = document.createElement('li');
      const label = createLabelElement(id, option);
      const checkbox = createCheckboxElement(id, option);
      // Check if the checkbox is in the saved default values.
      checkbox.checked = savedDefaultValue.split(',').includes(option);
      label.appendChild(checkbox);
      listElt.appendChild(label);
      multiSelectContainer.appendChild(listElt);
    });
    return multiSelectContainer;
  };

  // Function to update the hidden input field with the selected values.
  function updateDefaultValueHiddenInput() {
    const { attributeFieldSelect, hiddenInputField } = projectAttributeForms[currentFieldId];
    const attributeData = attributesData.find((el) => el.id === Number.parseInt(attributeFieldSelect.value));
    if (!attributeData) return;
  
    switch(attributeData.field_type) {
      case 'boolean':
          const checkbox = document.querySelector('input[name="custom_default_value"]');
          hiddenInputField.value = checkbox.checked;
          break;
      case 'list':
          const select = document.querySelector('select[name="custom_default_value"]');
          hiddenInputField.value = select.value;      
          break;
      case 'multi_choices_list':
          const checkboxes = document.querySelectorAll('input[name="custom_default_value"]:checked');
          let values = Array.from(checkboxes).map(cb => cb.value);
          hiddenInputField.value = values.toString();
          break;
    }
  };

  // Function to attach change event listeners to custom input elements.
  function setEventListener(el) {
    el.addEventListener('change', function() {
      updateDefaultValueHiddenInput();
    });
  }

  // Main function to update the custom input elements based on the selected project attribute.
  function updateDefaultValueInput() {
    // Get datas for this form
    const { attributeFieldSelect, defaultValueCustomContainer, savedDefaultValue } = projectAttributeForms[currentFieldId];
        
    const attributeData = attributesData.find((el) => el.id === Number.parseInt(attributeFieldSelect.value));
    if (!attributeData) return;
    const { options, field_type } = attributeData;
    
    // Clear the custom container before adding new input elements.
    defaultValueCustomContainer.innerHTML = '';
    let formElement;
    switch(field_type) {
        case 'boolean':
            formElement = createCheckboxElement('id_default_value');
            // Set the checkbox state based on the saved value.
            formElement.checked = savedDefaultValue === 'true';
            break;
        case 'list':
            formElement = createSelectElement(options, savedDefaultValue);
            break;
        case 'multi_choices_list':
            formElement = createMultiSelectElement(options, savedDefaultValue);
            break;
    }
    if (formElement) {
      // Add the created form element to the custom container.
      defaultValueCustomContainer.appendChild(formElement);
      // Update the value of the hidden input field in case the user switches project attribute.
      updateDefaultValueHiddenInput();
    }
  }


  function listenToNewForm() {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(function(addedNode) {
            if (addedNode.nodeType === Node.ELEMENT_NODE && addedNode.classList.contains('dynamic-projectattributeassociation_set')) {
              // Ici, vous pouvez appliquer votre logique de personnalisation
              // sur l'addedNode, qui est le nouveau formulaire ajouté
              console.log('Nouveau formulaire ajouté:', addedNode);
              //initNewForm(addedNode.id);
              currentFieldId = addedNode.id.slice(-1);
              initNewForm();
            }
          });
        }
      });
    });
  
    const config = { childList: true, subtree: true };
    // sélecteur qui cible le conteneur de votre InlineFormSet
    const targetNode = document.querySelector('#projectattributeassociation_set-group');
    if (targetNode) {
      observer.observe(targetNode, config);
    }
  };
});
