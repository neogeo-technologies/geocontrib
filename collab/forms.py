from collab.choices import GEOM_TYPE
from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.models import Project
from datetime import timedelta
from django import forms


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
            return ''
        except Exception as exp:
            return str(exp)
