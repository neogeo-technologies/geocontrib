from django.contrib.gis import forms
from django.forms import HiddenInput
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from geocontrib.models import BaseMap
from geocontrib.models import ContextLayer
from geocontrib.models import Layer
from geocontrib.models import Project


class ContextLayerForm(forms.ModelForm):
    layer = forms.ModelChoiceField(
        label="Couche", queryset=Layer.objects.all(), empty_label=None)

    queryable = forms.BooleanField(label='Requêtable', required=False)

    class Meta:
        model = ContextLayer
        fields = ['layer', 'order', 'opacity', 'queryable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].widget = HiddenInput()


ContextLayerFormset = inlineformset_factory(
    BaseMap, ContextLayer, form=ContextLayerForm,
    fields=['layer', 'order', 'opacity', 'queryable'], extra=0)


class BaseMapInlineFormset(BaseInlineFormSet):
    """
    from wsimmerson@https://github.com/wsimmerson/DjangoNestedForms
    """
    def add_fields(self, form, index):
        super().add_fields(form, index)

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
                    form.save(commit=commit)  # ???
                    form.nested.save(commit=commit)

        return result


class BaseMapForm(forms.ModelForm):

    title = forms.CharField(label="Titre", required=True)

    class Meta:
        model = BaseMap
        fields = ['title', ]


ProjectBaseMapInlineFormset = inlineformset_factory(
    parent_model=Project, form=BaseMapForm, model=BaseMap, formset=BaseMapInlineFormset,
    fields=['title', ], extra=0, can_delete=True)
