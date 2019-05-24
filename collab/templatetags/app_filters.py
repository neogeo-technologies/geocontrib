import datetime
from django.template.defaulttags import register

@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key, ' ')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key).items()


@register.simple_tag
def get_nested_item(dictionary, key, val):
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
