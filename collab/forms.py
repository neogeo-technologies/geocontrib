from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.models import Project
from collab.models import Autorisation
from datetime import timedelta
from django import forms
from django.forms.models import BaseModelFormSet
from django.forms.models import BaseFormSet
from django.forms.formsets import DELETION_FIELD_NAME


class ProjectForm(forms.Form):

    title = forms.CharField(label='Titre', max_length=100)
    illustration = forms.ImageField(label="Illustration du projet",
                            required=False)
    description = forms.CharField(
                  widget=forms.Textarea(),
                  label='Description', required=False)
    moderation = forms.BooleanField(label='Modération', required=False)
    nbday_archive = forms.IntegerField(label='Délai avant archivage',
                                          required=False)
    nbday_delete = forms.IntegerField(label='Délai avant suppression',
                                         required=False)
    visi_feature = forms.ChoiceField(label='Visibilité des signalements publiés',
                                     choices=USER_TYPE,
                                     widget=forms.Select())
    visi_archive = forms.ChoiceField(label='Visibilité des signalements archivés',
                                     choices=USER_TYPE_ARCHIVE,
                                     widget=forms.Select())

    def create_project(self):
        result = {}
        try:
            # add archive_feature / delete_feature
            nbday = self.cleaned_data.pop('nbday_archive')
            if nbday:
                self.cleaned_data['archive_feature'] = timedelta(days=nbday)
            nbday = self.cleaned_data.pop('nbday_delete', '')
            if nbday:
                self.cleaned_data['delete_feature'] = timedelta(days=nbday)
            obj = Project(**self.cleaned_data)
            obj.save()
            result["project"] = obj
        except Exception as exp:
            result["db_error"] = str(exp)

        return result


class FeatureRelatedForm(forms.Form):
    relation = forms.ChoiceField(
        label="lien",
        choices=(
            ('', '----'),
            ('doublon', 'Doublon'),
            ('remplace', 'Remplace'),
            ('est_remplace_par', 'Est remplacé par'),
            ('depend_de', 'Dépend de'),
        ),
        widget=forms.Select(),
        required=False
    )

    feature_id = forms.CharField(label='Identifiants', max_length=256, required=False)


class LocalizedBaseFS(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Supprimer ?'


class LocalizedModelBaseFS(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Supprimer ?'


class AutorisationForm(forms.ModelForm):

    first_name = forms.CharField(label="Nom", required=False)
    last_name = forms.CharField(label="Prenom", required=False)
    username = forms.CharField(label="Nom d'utilisateur")
    email = forms.EmailField(label="Adresse email")
    level = forms.ChoiceField(label="Niveau d'autorisation", choices=Autorisation.LEVEL)

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
        models = Autorisation
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'level',
        )
