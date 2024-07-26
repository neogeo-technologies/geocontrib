from django.contrib.gis import forms

from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureType
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
    """
    A form for selecting fields from the Feature model to include in a formset.
    
    This form allows users to choose fields from the `Feature` model to include in a PostgreSQL view.
    It provides options for selecting fields and specifying aliases for those fields. 
    The 'deletion_on' field is excluded from the choices to ensure since it is not included 
    in the PostgreSQL view.
    """
    
    # A choice field for selecting which field from the `Feature` model to include.
    related_field = forms.ChoiceField(
        label="Champs à ajouter",
        choices=[
            (
                str(field.name),  # Value sent in the form submission
                "{0} - {1}".format(field.name, field.get_internal_type())  # Human-readable label
            ) for field in Feature._meta.get_fields(include_parents=False)  # Get fields of the Feature model
            if field.concrete is True and field.name != 'deletion_on'  # Exclude non-concrete fields and 'deletion_on'
        ],
        required=False  # This field is optional
    )    
    # A text field for specifying an alias for the selected field.
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Alias pour cette colonne"  # Placeholder text in the input field
        }),
        validators=[alphanumeric]  # Apply alphanumeric validation to the input
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
