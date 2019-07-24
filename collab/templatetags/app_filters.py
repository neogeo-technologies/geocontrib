import datetime
from django.template.defaulttags import register
from django.forms.fields import CheckboxInput
from django.forms.fields import DateInput


@register.filter
def display_key(key):
    key_list = ['id', 'user_id', 'project_id', 'feature_id', 'creation_date', 'deletion_date', 'archive_date', 'modification_date', 'user']
    if key not in key_list:
        return True
    else:
        return False


@register.filter
def get_dict_item(dictionary, key):
    if dictionary.get(key, ' '):
        return dictionary.get(key, ' ')
    else:
        return ''


@register.filter
def get_item(dictionary, key):
    if dictionary.get(key, ''):
        return dictionary.get(key).items()
    else:
        return ''


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


@register.filter
def get_timestamp(timestamp):
    if timestamp:
        # ts = """{nbjours} Jours {nbmin} Minutes {nbsec} Secondes """.format(
        #    nbjours=timestamp.days,
        #    nbmin=timestamp.seconds // 3600,
        #    nbsec=timestamp.seconds // 60 % 60)
        try:
            ts = """{nbjours}""".format(
               nbjours=timestamp.days)
            return ts
        except Exception as e:
                return "0"
    else:
        return "0"


@register.filter
def lookup(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, False)


@register.filter
def is_checkbox(value):
    return isinstance(value, CheckboxInput)


@register.filter
def is_date(value):
    return isinstance(value, DateInput)


@register.filter
def get_identity(user_a, user_b):

    idtt = user_a.username
    if user_b.is_authenticated and (user_a.last_name or user_b.first_name):
        idtt = user_a.get_full_name()
    return idtt
