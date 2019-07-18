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
from collab.models import Project
from collab.models import UserLevelPermission


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

    slug = forms.SlugField(label='Slug', required=True)

    class Meta:
        model = FeatureType
        fields = ('title', 'slug', 'geom_type')

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if self.instance.pk:
            if FeatureType.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                msg = "Veuillez modifier le slug de ce type de signalement, cette valeur doit etre unique."
                raise forms.ValidationError(msg)
        else:
            if FeatureType.objects.filter(slug=slug).exists():
                msg = "Veuillez modifier le slug de votre projet, cette valeur doit etre unique."
                raise forms.ValidationError(msg)
        return slug


class ProjectModelForm(forms.ModelForm):
    # TODO: demander si on ne peux pas avoir un positif integer field pour le
    # nombre de jours pour archive_feature et delete_feature au lieu d'une durée
    # on calculerai le timedelat plus facilement si on a pas besoin de gerer des horaire
    # de durée..
    title = forms.CharField(label='Titre', max_length=100)

    slug = forms.SlugField(label='Slug', max_length=100)

    thumbnail = forms.ImageField(label="Illustration du projet", required=False)

    description = forms.CharField(
        label='Description', required=False, widget=forms.Textarea())

    moderation = forms.BooleanField(label='Modération', required=False)

    archive_feature = forms.IntegerField(
        label='Délai avant archivage (nb jours)', min_value=0, required=False)

    delete_feature = forms.IntegerField(
        label='Délai avant suppression (nb jours)', min_value=0, required=False)

    access_level_pub_feature = forms.ModelChoiceField(
        label='Visibilité des signalements publiés',
        queryset=UserLevelPermission.objects.filter(rank__lte=2).order_by('rank'))

    access_level_arch_feature = forms.ModelChoiceField(
        label='Visibilité des signalements archivés',
        queryset=UserLevelPermission.objects.filter(rank__gt=2).order_by('rank'))

    class Meta:
        model = Project
        fields = [
            'title',
            'slug',
            # 'created_on'
            'description',
            'moderation',
            'thumbnail',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
            # 'features_info'
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

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if self.instance.pk:
            if Project.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                msg = "Veuillez modifier le slug de votre projet, un projet avec ce slug existe déjà."
                raise forms.ValidationError(msg)
        else:
            if Project.objects.filter(slug=slug).exists():
                msg = "Veuillez modifier le slug de votre projet, un projet avec ce slug existe déjà."
                raise forms.ValidationError(msg)
        return slug


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

    attachment_title = forms.CharField(
        label="Information additonelle (pièce jointe)", max_length=128, required=False)
    attachment_info = forms.CharField(
        label="Titre de la pièce jointe", required=False, widget=forms.Textarea())

    class Meta:
        model = Comment
        fields = (
            'comment',
            'attachment_title',
            'attachment_info',
        )

    def save(self, commit=True, *args, **kwargs):

        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)
        feature = kwargs.pop('feature', None)
        attachment = kwargs.pop('attachment', None)

        instance = super().save(commit=False)

        instance.feature_id = feature.feature_id
        instance.feature_type_slug = feature.feature_type.slug
        instance.author = user
        instance.project = project

        if commit:
            instance.save()
            # if attachment:
            #     Attachment.objects.create(
            #         feature_id=instance.feature_id,
            #         author=instance.author,
            #         project=instance.project,
            #         title='',
            #         info='',
            #         type_objet='comment',
            #         attachment_file=attachment,
            #         comment=instance,
            #     )
            #     import pdb; pdb.set_trace()


        return instance


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = (
            'title',
            'info',
            'attachment_file',
        )


class FeatureLinkForm(forms.ModelForm):

    # feature_id = forms.ModelChoiceField(
    #     Feature.objects.all(), label='Identifiant', to_field_name='feature_id'
    # )

    class Meta:
        model = FeatureLink
        fields = (
            'relation_type',
            'feature_to',
        )

    def __init__(self, *args, **kwargs):

        # import pdb; pdb.set_trace()
        return super().__init__(*args, **kwargs)


class FeatureDynamicForm(forms.ModelForm):
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
        extra = kwargs.pop('extra', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        project = feature_type.project

        choices = tuple(x for x in Feature.STATUS_CHOICES)
        if not project.moderation:
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] != 'pending')

        if project.moderation and not Authorization.has_permission(user, 'can_publish_feature', project):
            choices = tuple(x for x in Feature.STATUS_CHOICES if x[0] in ['draft', 'pending'])

        self.fields["status"] = forms.ChoiceField(
            choices=choices
        )

        # TODO: factoriser les attributs de champs geom
        if feature_type.geom_type == "point":
            self.fields["geom"] = forms.PointField(
                label="Localisation",
                required=False,
            )

        if feature_type.geom_type == "linestring":
            self.fields["geom"] = forms.LineStringField(
                label="Localisation",
                required=False,
            )

        if feature_type.geom_type == "polygon":
            self.fields["geom"] = forms.PolygonField(
                label="Localisation",
                required=False,
            )

        if extra.exists():
            for custom_field in extra.order_by('position'):
                if custom_field.field_type == 'boolean':
                    self.fields[custom_field.name] = forms.BooleanField(
                        label=custom_field.label, initial=False, required=False)

                if custom_field.field_type == 'char':
                    self.fields[custom_field.name] = forms.CharField(
                        label=custom_field.label, max_length=256, required=False)

                if custom_field.field_type == 'date':
                    self.fields[custom_field.name] = forms.DateField(
                        label=custom_field.label, required=False,
                        widget=forms.DateInput(attrs={
                            'class': 'ui calendar',
                            'type': 'date'
                        }))

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

        if isinstance(self.instance.feature_data, dict):
            if extra.exists() and self.instance.feature_data:
                for custom_field in extra:
                    self.fields[custom_field.name].initial = self.instance.feature_data.get(custom_field.name)

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False)

        extra = CustomField.objects.filter(feature_type=instance.feature_type)
        newdict = {field_name: self.cleaned_data.get(field_name) for field_name in extra.values_list('name', flat=True)}
        stringfied = json.dumps(newdict, cls=DjangoJSONEncoder)
        instance.feature_data = json.loads(stringfied)

        if commit:
            instance.save()

        return instance
