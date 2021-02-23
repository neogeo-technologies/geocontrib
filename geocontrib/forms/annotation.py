from django import forms

from geocontrib.models import Attachment
from geocontrib.models import Comment


class CommentForm(forms.ModelForm):

    comment = forms.CharField(required=True, widget=forms.Textarea())

    title = forms.CharField(label="Titre de la pièce jointe", required=False)

    attachment_file = forms.FileField(label="Fichier joint", required=False)

    info = forms.CharField(
        label="Information additionnelle au fichier joint",
        required=False, widget=forms.Textarea())

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
