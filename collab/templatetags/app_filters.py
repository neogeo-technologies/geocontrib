import datetime
from django.template.defaulttags import register


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


@register.simple_tag
def get_nested_item(dictionary, key, val=""):
    if not val:
        return dictionary.get(key, '')
    data = dictionary.get(key, '')
    return data.get(val, '')


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
