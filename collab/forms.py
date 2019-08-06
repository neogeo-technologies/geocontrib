import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis import forms
from django.forms.models import BaseModelFormSet
from django.forms.formsets import DELETION_FIELD_NAME

from collab.models import Authorization
from collab.models import Attachment
from collab.models import Comment
from collab.models import CustomField
from collab.models import Feature
from collab.models import FeatureLink
from collab.models import FeatureType
from collab.models import Layer
from collab.models import Project
from collab.models import UserLevelPermission

import logging
logger = logging.getLogger('django')


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
                raise forms.ValidationError("Les champs supplémentaires ne peuvent avoir des nom similaires.")
            names.append(name)


class CustomFieldModelForm(forms.ModelForm):

    class Meta:
        model = CustomField
        fields = ('label', 'name', 'field_type', 'position')


class FeatureTypeModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', required=True)

    class Meta:
        model = FeatureType
        fields = ('title', 'geom_type', 'color')


class ProjectModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', max_length=100)

    thumbnail = forms.ImageField(label="Illustration du projet", required=False)

    description = forms.CharField(
        label='Description', required=False, widget=forms.Textarea())

    moderation = forms.BooleanField(label='Modération', required=False)

    archive_feature = forms.IntegerField(
        label='Délai avant archivage', min_value=0, required=False)

    delete_feature = forms.IntegerField(
        label='Délai avant suppression', min_value=0, required=False)

    access_level_pub_feature = forms.ModelChoiceField(
        label='Visibilité des signalements publiés',
        queryset=UserLevelPermission.objects.filter(rank__lte=2).order_by('rank'),
        empty_label=None,)

    access_level_arch_feature = forms.ModelChoiceField(
        label='Visibilité des signalements archivés',
        queryset=UserLevelPermission.objects.filter(rank__lte=4).order_by('rank'),
        empty_label=None,)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'moderation',
            'thumbnail',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if instance:
            self.fields['archive_feature'].initial = instance.archive_feature
            self.fields['delete_feature'].initial = instance.delete_feature
        else:
            self.fields['archive_feature'].initial = 0
            self.fields['delete_feature'].initial = 0

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.instance.pk:
            if Project.objects.filter(title=title).exclude(pk=self.instance.pk).exists():
                msg = "Veuillez modifier le titre de votre projet, un projet avec ce titre existe déjà."
                raise forms.ValidationError(msg)
        else:
            if Project.objects.filter(title=title).exists():
                msg = "Veuillez modifier le titre de votre projet, un projet avec ce titre existe déjà."
                raise forms.ValidationError(msg)
        return title


class ExtendedBaseFS(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Supprimer ?'


class AuthorizationForm(forms.ModelForm):

    first_name = forms.CharField(label="Nom", required=False)

    last_name = forms.CharField(label="Prenom", required=False)

    username = forms.CharField(label="Nom d'utilisateur")

    email = forms.EmailField(label="Adresse email")

    level = forms.ModelChoiceField(
        label="Niveau d'autorisation",
        queryset=UserLevelPermission.objects.filter(rank__gte=1).order_by('rank'),
        empty_label=None)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['level'].initial = self.instance.level
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].disabled = True
            self.fields['last_name'].disabled = True
            self.fields['email'].disabled = True
            self.fields['username'].disabled = True

    class Meta:
        model = Authorization
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'level',
        )


class CommentForm(forms.ModelForm):

    comment = forms.CharField(required=True, widget=forms.Textarea())

    title = forms.CharField(label="Titre de la pièce jointe", required=False)

    attachment_file = forms.FileField(label="Fichier joint", required=False)

    info = forms.CharField(
        label="Information additonelle au fichier joint", required=False, widget=forms.Textarea())

    class Meta:
        model = Comment
        fields = (
            'comment',
            'title',
            'attachment_file',
            'info',
        )

    def clean(self):
        cleaned_data = super().clean()
        up_file = cleaned_data.get("attachment_file")
        title = cleaned_data.get("title")
        if up_file and not title:
            raise forms.ValidationError(
                "Veuillez donner un titre à votre pièce jointe. "
            )
        return cleaned_data


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment
        fields = (
            'title',
            'attachment_file',
            'info',
        )

    def clean(self):

        cleaned_data = super().clean()
        up_file = cleaned_data.get("attachment_file")
        title = cleaned_data.get("title")
        if up_file and not title:
            raise forms.ValidationError(
                "Veuillez donner un titre à votre pièce jointe. "
            )
        return cleaned_data


class FeatureLinkForm(forms.ModelForm):

    feature_to = forms.ChoiceField(label='Signalement lié')

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

        try:
            qs = Feature.objects.filter(feature_type=feature_type)
            if feature:
                qs = qs.exclude(feature_id=feature.feature_id)

            self.fields['feature_to'].choices = tuple(
                (feat.feature_id, "{} ({} - {})".format(
                    feat.title, feat.creator.username, feat.created_on)) for feat in qs
            )

        except Exception:
            logger.exception('No feature_type found')


class FeatureExtraForm(forms.Form):

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra', None)
        feature = kwargs.pop('feature', None)
        super().__init__(*args, **kwargs)

        for custom_field in extra.order_by('position'):
            if custom_field.field_type == 'boolean':
                self.fields[custom_field.name] = forms.BooleanField(
                    label=custom_field.label, initial=False, required=False,
                )

            if custom_field.field_type == 'char':
                self.fields[custom_field.name] = forms.CharField(
                    label=custom_field.label, max_length=256, required=False)

            if custom_field.field_type == 'date':
                self.fields[custom_field.name] = forms.DateField(
                    label=custom_field.label, required=False,
                )

            if custom_field.field_type == 'integer':
                self.fields[custom_field.name] = forms.IntegerField(
                    label=custom_field.label, required=False)

            if custom_field.field_type == 'decimal':
                self.fields[custom_field.name] = forms.DecimalField(
                    label=custom_field.label, required=False,
                    widget=forms.TextInput(attrs={
                        'localization': False
                    }))

            if custom_field.field_type == 'text':
                self.fields[custom_field.name] = forms.CharField(
                    label=custom_field.label, required=False, widget=forms.Textarea())

            self.fields[custom_field.name].widget.attrs.update({
                'field_type': custom_field.field_type
            })

        if feature and isinstance(feature.feature_data, dict):
            for custom_field in extra:
                self.fields[custom_field.name].initial = feature.feature_data.get(custom_field.name)


class FeatureBaseForm(forms.ModelForm):

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
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] in ['draft', 'published', 'archived'])
            initial = 'draft'

        self.fields['status'] = forms.ChoiceField(
            choices=choices,
            initial=initial,
            label='Statut'
        )

        # TODO: factoriser les attributs de champs geom
        if feature_type.geom_type == "point":
            self.fields['geom'] = forms.PointField(
                label="Localisation",
                required=True,
                srid=4326
            )

        if feature_type.geom_type == "linestring":
            self.fields['geom'] = forms.LineStringField(
                label="Localisation",
                required=True,
                srid=4326
            )

        if feature_type.geom_type == "polygon":
            self.fields['geom'] = forms.PolygonField(
                label="Localisation",
                required=True,
                srid=4326
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


class LayerForm(forms.ModelForm):

    class Meta:
        model = Layer
        fields = ('name', 'title', 'style', 'service', 'order', 'schema_type')
