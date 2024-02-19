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
    """
    A custom ModelForm for the ProjectAttribute model in the Django admin.

    This form is designed to be used in the ProjectAttributeAdmin to provide
    an interface for creating and editing ProjectAttribute instances. It specifies
    which fields should be included in the form and allows for further customization
    of the form behavior and appearance if needed.
    """
    
    class Meta:
        # Specifies the model associated with this form.
        model = ProjectAttribute
        
        # Defines the list of fields that should be included in the form.
        # This ensures only relevant fields are displayed in the admin interface for editing.
        fields = ['label', 'name', 'field_type', 'options', 'default_value', 'display_filter', 'default_filter_enabled', 'default_filter_value']

