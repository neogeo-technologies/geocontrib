import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis import forms
from django.forms.models import BaseModelFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.forms import HiddenInput

from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import BaseMap
from geocontrib.models import Comment
from geocontrib.models import ContextLayer
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import Layer
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission

import logging
logger = logging.getLogger(__name__)


########################
# DJANGO ADMIN FORMSET #
########################
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
        ) for field in Feature._meta.get_fields()],
        required=False
    )
    alias = forms.CharField(
        label="Alias",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Alias pour cette colonne"
        })
    )


class AddPosgresViewAdminForm(forms.Form):
    name = forms.CharField(
        label="Nom",
        required=True,
    )

    status = forms.MultipleChoiceField(
        label="Statut",
        choices=tuple(x for x in Feature.STATUS_CHOICES),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


#############################
# CUSTOM BASE MODEL FORMSET #
#############################

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


class AuthorizationBaseFS(BaseModelFormSet):
    def clean(self):
        from geocontrib.choices import ADMIN
        if any(self.errors):
            return
        try:
            has_administrator = any([form.cleaned_data.get('level').user_type_id == ADMIN for form in self.forms])
        except Exception:
            raise forms.ValidationError("Erreur critique dans la sauvegarde des membres. ")
        else:
            if not has_administrator:
                raise forms.ValidationError("Vous devez désigner au moins un administrateur par projet.")

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Supprimer ?'


####################
# ANNOTATION FORMS #
####################

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


##################
# CONTENTS FORMS #
##################

class AuthorizationForm(forms.ModelForm):

    first_name = forms.CharField(label="Nom", required=False)

    last_name = forms.CharField(label="Prenom", required=False)

    username = forms.CharField(label="Nom d'utilisateur")

    email = forms.EmailField(label="Adresse email", required=False)

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


class CustomFieldModelForm(forms.ModelForm):

    class Meta:
        model = CustomField
        fields = ('label', 'name', 'field_type', 'position', 'options')
        help_texts = {
            'label': "Nom en language naturel du champ",
            'name': "Nom technique du champ tel qu'il apparaît dans la base de données ou dans l'export GeoJSON (sans accents, sans espaces, ni caractères exotiques)",
            'position': "Numéro d'ordre du champ dans le formulaire de saisie du signalement",
            'options': "Valeurs possibles de ce champ, séparées par des virgules"
        }


class FeatureBaseForm(forms.ModelForm):

    title = forms.CharField(label='Nom', required=True)

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

            if custom_field.field_type == 'list' and custom_field.options:
                self.fields[custom_field.name] = forms.ChoiceField(
                    label=custom_field.label,
                    choices=[(str(xx), str(xx)) for xx in custom_field.options],
                    required=False)

            self.fields[custom_field.name].widget.attrs.update({
                'field_type': custom_field.field_type
            })

        if feature and isinstance(feature.feature_data, dict):
            for custom_field in extra:
                self.fields[custom_field.name].initial = feature.feature_data.get(custom_field.name)


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
                    feat.title, feat.display_creator, feat.created_on.strftime("%d/%m/%Y %H:%M"))) for feat in qs
            )

        except Exception:
            logger.exception('No feature_type found')


class FeatureTypeModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', required=True)

    class Meta:
        model = FeatureType
        fields = ('title', 'geom_type', 'color')

    # def __init__(self, *args, **kwargs):
    #     feature_type = kwargs.get('instance')
    #
    #     super().__init__(*args, **kwargs)
    #
    #     if feature_type.geom_type == "point":
    #         self.fields['geom'] = forms.PointField(
    #             label="Localisation",
    #             required=True,
    #             srid=4326
    #         )
    #
    #     if feature_type.geom_type == "linestring":
    #         self.fields['geom'] = forms.LineStringField(
    #             label="Localisation",
    #             required=True,
    #             srid=4326
    #         )
    #
    #     if feature_type.geom_type == "polygon":
    #         self.fields['geom'] = forms.PolygonField(
    #             label="Localisation",
    #             required=True,
    #             srid=4326
    #         )


class ProjectModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', max_length=100)

    thumbnail = forms.ImageField(label="Illustration du projet", required=False)

    description = forms.CharField(
        label='Description', required=False, widget=forms.Textarea())

    moderation = forms.BooleanField(label='Modération', required=False)

    archive_feature = forms.IntegerField(
        label='Délai avant archivage', required=False)

    delete_feature = forms.IntegerField(
        label='Délai avant suppression', required=False)

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

    def clean(self):
        cleaned_data = super().clean()
        archive_feature = cleaned_data.get('archive_feature', None)
        delete_feature = cleaned_data.get('delete_feature', None)
        if archive_feature and delete_feature and archive_feature > delete_feature:
            raise forms.ValidationError(
                "Le délai d'archivage doit être inférieur au délai de suppression. "
            )
        return cleaned_data


class ContextLayerForm(forms.ModelForm):
    layer = forms.ModelChoiceField(label="Couche", queryset=Layer.objects.all(), empty_label=None)

    class Meta:
        model = ContextLayer
        fields = ['layer', 'order', 'opacity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].widget = HiddenInput()


ContextLayerFormset = inlineformset_factory(
    BaseMap, ContextLayer, form=ContextLayerForm, fields=['layer', 'order', 'opacity'], extra=0)


class BaseMapInlineFormset(BaseInlineFormSet):
    """
    from wsimmerson@https://github.com/wsimmerson/DjangoNestedForms
    """
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # for hidding delete input
        # form.fields[DELETION_FIELD_NAME].widget = HiddenInput()

        # save the formset in the 'nested' property
        data = form.data if any(form.data) else None

        form.nested = ContextLayerFormset(
            instance=form.instance,
            data=data,
            files=form.files if form.is_bound else None,
            prefix='contextlayer-%s-%s' % (
                form.prefix,
                ContextLayerFormset.get_default_prefix()))

    def is_valid(self):
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result


ProjectBaseMapInlineFormset = inlineformset_factory(
    parent_model=Project, model=BaseMap, formset=BaseMapInlineFormset,
    fields=['title', ], extra=0, can_delete=True)
