from django.template.defaulttags import register
from django.forms.fields import CheckboxInput
from django.forms.fields import DateInput
from urllib.parse import urljoin
from django.contrib.sites.models import Site

import logging

logger = logging.getLogger(__name__)

try:
    CURRENT_SITE_DOMAIN = Site.objects.get_current().domain
except Exception:
    CURRENT_SITE_DOMAIN = 'http://SETUP-URL-IN-ADMIN'
    logger.warning('Sites not migrated yet. Please make sure you have Sites setup on Django Admin')


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
    url = urljoin(CURRENT_SITE_DOMAIN, relative_url)
    return url
