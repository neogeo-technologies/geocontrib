from django.contrib.gis import forms
from django.forms import HiddenInput
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import BaseModelFormSet
from django.utils import timezone

from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission
from geocontrib.choices import ADMIN


class AuthorizationBaseFS(BaseModelFormSet):
    def clean(self):
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


class ProjectModelForm(forms.ModelForm):

    title = forms.CharField(label='Titre', max_length=100)

    thumbnail = forms.ImageField(label="Illustration du projet", required=False)

    description = forms.CharField(
        label='Description', required=False, widget=forms.Textarea())

    moderation = forms.BooleanField(label='Modération', required=False)

    is_project_type = forms.BooleanField(
        label="Est un projet type", required=False)

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

    create_from = forms.CharField(required=False, widget=HiddenInput())

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
            'is_project_type',
            'create_from',
        ]

    def __init__(self, *args, **kwargs):

        slug = kwargs.pop('create_from', None)
        project_type = Project.objects.filter(slug=slug).first()

        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if instance:
            # Optionnel
            for key in ['archive_feature', 'delete_feature']:
                source = getattr(instance, key)
                self.fields[key].initial = source
        elif project_type:
            for key in [
                    'archive_feature', 'delete_feature',
                    'access_level_pub_feature', 'access_level_arch_feature',
                    'description', 'moderation', 'thumbnail']:
                source = getattr(project_type, key)
                self.fields[key].initial = source
            self.fields['title'].initial = "{} (Copie-{})".format(
                project_type.title, timezone.now().strftime("%d/%m/%Y %H:%M")
            )
            self.fields['title'].help_text = "Le titre d'un projet doit etre unique. "
            self.fields['create_from'].initial = slug
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
            raise forms.ValidationError({
                'archive_feature': "Le délais de suppression doit être supérieur au délais d'archivage. "
            })
        return cleaned_data
