import datetime
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key).items()


@register.filter
def header_display(key):
    return str(key).replace('_', ' ').capitalize()


@register.filter
def feature_key_display(key):
    return str(key).replace('_', ' ').capitalize()


@register.filter
def feature_val_display(val):
    if isinstance(val, datetime.date):
        return val.strftime('%d/%m/%Y')
    return str(val).replace('_', ' ').capitalize()
