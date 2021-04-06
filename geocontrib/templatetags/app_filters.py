from django.template.defaulttags import register
from django.forms.fields import CheckboxInput
from django.forms.fields import DateInput
from django.conf import settings
from urllib.parse import urljoin

import logging

logger = logging.getLogger(__name__)

BASE_URL = getattr(settings, 'BASE_URL', '')


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


@register.filter
def absurl(relative_url):
    if not isinstance(relative_url, str):
        relative_url = str(relative_url)
    return urljoin(BASE_URL, relative_url)
