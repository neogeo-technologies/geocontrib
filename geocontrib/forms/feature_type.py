from django import forms
from django.forms import JSONField
from django.forms.models import BaseModelFormSet

from geocontrib.models import CustomField
from geocontrib.models import FeatureType
from geocontrib.forms.common import alphanumeric


class CustomFieldModelBaseFS(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        names = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            name = form.cleaned_data.get('name')
            if name in names:
                raise forms.ValidationError(
                    "Les champs supplémentaires ne peuvent avoir des noms similaires.")
            names.append(name)


class CustomFieldModelForm(forms.ModelForm):
    name = forms.CharField(
        label="Nom", max_length=128, required=True,
        help_text=(
            "Nom technique du champ tel qu'il apparaît dans la base de données "
            "ou dans l'export GeoJSON. "
            "Seuls les caractères alphanumériques et les traits d'union "
            "sont autorisés: a-z, A-Z, 0-9, _ et -)"),
        validators=[alphanumeric])

    class Meta:
        model = CustomField
        fields = ('label', 'name', 'field_type', 'position', 'options')
        help_texts = {
            'label': "Nom en language naturel du champ",
            'position': "Numéro d'ordre du champ dans le formulaire de saisie du signalement",
            'options': "Valeurs possibles de ce champ, séparées par des virgules"
        }


class FeatureTypeModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', required=True)

    colors_style = JSONField(
        label='Style Couleur', required=False,
        # TODO voir si nécessaire au front
        initial={'custom_field_name': '', 'colors': {}}
    )

    class Meta:
        model = FeatureType
        fields = ('title', 'geom_type', 'color', 'colors_style')
