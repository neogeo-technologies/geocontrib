from django.contrib.gis import forms

from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import ProjectAttribute
from geocontrib.forms.common import alphanumeric


class FeatureTypeAdminForm(forms.ModelForm):
    class Meta:
        model = FeatureType
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class CustomFieldModelAdminForm(forms.ModelForm):
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Alias pour cette colonne"
        })
    )

    class Meta:
        model = CustomField
        fields = ('name', 'alias', 'field_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field_type'].disabled = True

    def save(self, *args, **kwargs):
        return None


class HiddenDeleteBaseFormSet(forms.BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[forms.formsets.DELETION_FIELD_NAME].widget = forms.HiddenInput()


class HiddenDeleteModelFormSet(forms.BaseModelFormSet, HiddenDeleteBaseFormSet):
    pass


class FeatureSelectFieldAdminForm(forms.Form):
    related_field = forms.ChoiceField(
        label="Champs à ajouter",
        choices=[(
            str(field.name), "{0} - {1}".format(field.name, field.get_internal_type())
        ) for field in Feature._meta.get_fields(include_parents=False) if field.concrete is True],
        required=False
    )
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Alias pour cette colonne"
        }),
        validators=[alphanumeric]
    )


class AddPosgresViewAdminForm(forms.Form):
    name = forms.CharField(
        label="Nom",
        required=True,
        validators=[alphanumeric]
    )

    status = forms.MultipleChoiceField(
        label="Statut",
        choices=tuple(x for x in Feature.STATUS_CHOICES),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creator'].required = True

class ProjectAttributeAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectAttribute
        fields = ['label', 'name', 'field_type', 'options', 'default_value']

    def __init__(self, *args, **kwargs):
        super(ProjectAttributeAdminForm, self).__init__(*args, **kwargs)
        # Ici, vous pouvez ajuster le champ default_value en fonction de field_type
        # Par exemple, si field_type est 'boolean', changez le widget en CheckboxInput
        #breakpoint()
        if 'field_type' in self.fields:
            field_type = self.fields['field_type'].initial
            if field_type == 'boolean':
                self.fields['default_value'].widget = forms.CheckboxInput()
            if field_type == 'multi_choices_list':
                self.fields['default_value'].widget = forms.CheckboxSelectMultiple()
            # ... autres conditions pour 'list' et 'multi_choices_list'