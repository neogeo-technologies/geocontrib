from collab.choices import GEOM_TYPE
from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.models import Project
from collab.models import Autorisation
from collab.models import CustomUser
from datetime import timedelta
from django import forms
from django.forms.models import BaseModelFormSet
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


class ExtendedBaseFS(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = 'Supprimer ?'


class AutorisationForm(forms.ModelForm):

    first_name = forms.CharField(label="Nom", required=False)
    last_name = forms.CharField(label="Prenom", required=False)
    username = forms.CharField(label="Nom d'utilisateur", required=False)
    email = forms.EmailField(label="Adresse email", required=False)
    level = forms.ChoiceField(label="Niveau d'autorisation", choices=Autorisation.LEVEL, required=False)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username
            self.fields['username'].disabled = True
            self.fields['level'].initial = self.instance.level

    def clean(self):
        if self.cleaned_data.get('DELETE') and not self.instance.pk:
            return None
        required = [
            'email',
            'first_name',
            'username',
            'level'
        ]
        for field in required:
            if not self.cleaned_data[field]:
                raise forms.ValidationError("Tous les champs sont requis.")

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance.pk:
            if self.instance.user.username != self.cleaned_data.get('username') \
                    and CustomUser.objects.filter(username=username).exists():
                raise forms.ValidationError("Ce nom d'utilisateur est réservé")
        elif CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est réservé.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if self.instance.pk:
            if self.instance.user.email != self.cleaned_data.get('email') \
                    and CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Cette adresse est reservée.")

        elif CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse est reservée.")

        return email

    class Meta:
        models = Autorisation
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'level',
        )
