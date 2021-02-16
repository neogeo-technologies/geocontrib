window.addEventListener('load', function () {
	// ---------------------------------------------------------------------------
	// Suppression d'un form
	// ---------------------------------------------------------------------------
	let form_deleters = document.querySelectorAll('div[data-delete-form]');

	function RemoveIt() {
		let data_segment_attr = this.getAttribute('data-delete-form').replace(
			'-DELETE',
			'-SEGMENT'
		);
		let data_segment = document.querySelector(
			"div[data-segment='" + data_segment_attr + "']"
		);
		let hidden_input_delete = document.getElementById(
			'id_' + this.getAttribute('data-delete-form')
		);

		hidden_input_delete.checked = true;
		data_segment.style.display = 'none';

		// On submit a chaque suppression d'un form
		// document.getElementById("form-layers").submit();
	}

	for (let i = 0; i < form_deleters.length; i++) {
		form_deleters[i].addEventListener('click', RemoveIt, false);
	}

	// ---------------------------------------------------------------------------
	// Ajout d'un form
	// ---------------------------------------------------------------------------
	let form_creators = document.querySelectorAll('a[data-add-form]');

	function AddIt() {
		let prefix = this.getAttribute('data-add-form').replace('-ADD', '');
		let total_forms = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
		let form_idx = total_forms.value;
		let new_form = document.querySelector(
			'div[data-empty-form=' + prefix + '-EMPTY]'
		);
		let marked_form = '';

		// Si ajout d'un basemap
		if (prefix.startsWith('basemap')) {
			// on recupere le gabarit d'un form de basemap vide (contenant aussi les form.nested de contextlayer)
			// on change basemap_set-__prefix__ par basemap_set-N ou N est le total des form de basemap
			marked_form = new_form.innerHTML.replace(
				/basemap_set-__prefix__/g,
				'basemap_set-' + form_idx
			);
			// on ne modifie pas le pattern contextlayer_set-__prefix__
		} else {
			// sinon si ajout d'un context layer
			// alors on modifie les __prefix__ par le total des form de contextlayer
			marked_form = new_form.innerHTML.replace(/__prefix__/g, form_idx);
		}

		let add_form = document
			.querySelector('div[data-segments=' + prefix + '-SEGMENTS]')
			.insertAdjacentHTML('beforeend', marked_form);

		if (prefix.startsWith('basemap')) {
			document.getElementById('id_basemap_set-' + form_idx + '-title').required = true;
		}

		// Scroll sur le nouveau form
		let element = document.querySelector(
			'div[data-segments=' + prefix + '-SEGMENTS]'
		);
		element.scrollIntoView({ block: 'end' });

		// Ajout d'un event ciblant la nouvelle ancre de suppression
		let remove_field = document.querySelector(
			'div[data-delete-form=' + prefix + '-' + form_idx + '-DELETE]'
		);
		remove_field.addEventListener('click', RemoveIt, false);

		// Ajout d'un event ciblant de potentiels boutons d'ajout
		// vrai lorsqu'on crée un nouveau basemap et son les contextlayer imbriqué
		if (prefix.startsWith('basemap')) {
			let sub_creators = document.querySelectorAll('a[data-add-form]');
			for (let i = 0; i < sub_creators.length; i++) {
				sub_creators[i].addEventListener('click', AddIt, false);
			}
		}

		// on incremente le nombre total de form du type de celui ajouté
		total_forms.value++;
	}
	for (let i = 0; i < form_creators.length; i++) {
		form_creators[i].addEventListener('click', AddIt, false);
	}

	// ---------------------------------------------------------------------------
	// Utilisation de sortable.js pour changer l'ordre des couches
	// ---------------------------------------------------------------------------
	const layersContainer = document.getElementsByClassName('layers-container');
	Array.from(layersContainer).forEach((layerContainer) => {
		// Drag and drop feature to change the order of the layers
		new Sortable(layerContainer, {
			animation: 150,
			handle: '.layer-handle-sort', // The element that is active to drag
			ghostClass: 'blue-background-class',
			dragClass: 'white-opacity-background-class',
			onEnd: () => {
				// Update the order of the layers in the hidden input
				const layerItems = layerContainer.querySelectorAll(
					'input[name*="-order"]'
				);
				layerItems.forEach((layerItem, index) => {
					layerItem.value = index;
				});
			},
		});
	});
});
