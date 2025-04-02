import json

from django import forms
from django.contrib.gis.forms import GeometryField
from django.core.serializers.json import DjangoJSONEncoder

from geocontrib import logger
from geocontrib.models import Authorization
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink


class FeatureBaseForm(forms.ModelForm):

    title = forms.CharField(label='Nom', required=True)

    geom = GeometryField(
        label="Localisation",
        required=True,
        srid=4326,
    )

    class Meta:
        model = Feature
        fields = (
            'title',
            'description',
            'status',
            'geom'
        )

    def __init__(self, *args, **kwargs):
        feature_type = kwargs.pop('feature_type')
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        project = feature_type.project

        # Status choices
        initial = 'draft'
        choices = tuple(x for x in Feature.STATUS_CHOICES)
        if not project.moderation:
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] != 'pending')
            initial = 'published' if not self.instance else self.instance.status

        if project.moderation and not Authorization.has_permission(user, 'can_publish_feature', project):
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] in ['draft', 'pending'])
            initial = 'pending'

        if project.moderation and Authorization.has_permission(user, 'can_publish_feature', project):
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] in ['draft', 'pending', 'published', 'archived'])
            initial = 'draft'

        self.fields['status'] = forms.ChoiceField(
            choices=choices,
            initial=initial,
            label='Statut'
        )

    def save(self, commit=True, *args, **kwargs):

        extra = kwargs.pop('extra', None)
        feature_type = kwargs.pop('feature_type', None)
        project = kwargs.pop('project', None)
        creator = kwargs.pop('creator', None)
        instance = super().save(commit=False)

        if extra and feature_type:
            custom_fields = CustomField.objects.filter(feature_type=feature_type)
            newdict = {
                field_name: extra.get(field_name) for field_name in custom_fields.values_list('name', flat=True)
            }
            stringfied = json.dumps(newdict, cls=DjangoJSONEncoder)
            instance.feature_data = json.loads(stringfied)

        if creator:
            instance.creator = creator

        if commit:
            instance.feature_type = feature_type
            instance.project = project
            instance.save()

        return instance


class FeatureExtraForm(forms.Form):

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra', None)
        feature = kwargs.pop('feature', None)
        super().__init__(*args, **kwargs)

        if not extra:
            return

        self._build_fields(extra)
        self._populate_initial_values(extra, feature)

    def _build_fields(self, extra):
        for custom_field in extra.order_by('position'):
            self.fields[custom_field.name] = self._create_form_field(custom_field)
            self.fields[custom_field.name].widget.attrs.update({
                'field_type': custom_field.field_type
            })

    def _create_form_field(self, custom_field):
        """Return a Django form field instance based on the field type."""
        field_type = custom_field.field_type
        common_kwargs = {'label': custom_field.label, 'required': False}

        if field_type == 'boolean':
            return forms.BooleanField(initial=False, **common_kwargs)

        if field_type == 'char':
            return forms.CharField(max_length=256, **common_kwargs)

        if field_type == 'date':
            return forms.DateField(**common_kwargs)

        if field_type == 'integer':
            return forms.IntegerField(**common_kwargs)

        if field_type == 'decimal':
            return forms.DecimalField(
                widget=forms.TextInput(attrs={'localization': False}),
                **common_kwargs
            )

        if field_type == 'text':
            return forms.CharField(widget=forms.Textarea(), **common_kwargs)

        if field_type == 'list' and custom_field.options:
            choices = [(str(opt), str(opt)) for opt in custom_field.options]
            return forms.ChoiceField(choices=choices, **common_kwargs)

        # Default fallback (optional, or raise exception)
        return forms.CharField(**common_kwargs)

    def _populate_initial_values(self, extra, feature):
        if feature and isinstance(feature.feature_data, dict):
            for custom_field in extra:
                self.fields[custom_field.name].initial = feature.feature_data.get(custom_field.name)


class FeatureLinkForm(forms.ModelForm):

    feature_to = forms.ModelChoiceField(
        label="Signalement lié", queryset=Feature.objects.all(),
        empty_label=None)

    class Meta:
        model = FeatureLink
        fields = (
            'relation_type',
            'feature_to',
        )

    def __init__(self, *args, **kwargs):
        feature_type = kwargs.pop('feature_type', None)
        feature = kwargs.pop('feature', None)
        super().__init__(*args, **kwargs)
        qs = Feature.objects.all()
        if feature_type:
            qs = qs.filter(
                feature_type=feature_type
            )
        if feature:
            qs = qs.exclude(
                feature_id=feature.feature_id
            )
        try:
            self.fields['feature_to'].queryset = qs
            self.fields['feature_to'].label_from_instance = lambda obj: "{} ({} - {})".format(
                obj.title, obj.display_creator, obj.created_on.strftime("%d/%m/%Y %H:%M"))
        except Exception:
            logger.exception('No related features found')

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('DELETE'):
            if self._errors.get('feature_to'):
                from django.forms.utils import ErrorList
                errors = self._errors.setdefault("feature_to", ErrorList())
                if len(errors)>0:
                    errors.pop()
                errors.append("Le signalement lié n'est pas correcte.")
