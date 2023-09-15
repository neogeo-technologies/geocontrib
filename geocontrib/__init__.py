import logging

from geocontrib.choices import ANONYMOUS
from geocontrib.choices import LOGGED_USER
from geocontrib.choices import CONTRIBUTOR
from geocontrib.choices import MODERATOR
from geocontrib.choices import ADMIN
from geocontrib.choices import LOWER_LEVELS
from geocontrib.choices import EXTENDED_LEVELS
from geocontrib.choices import ALL_LEVELS

__all__ = [
    'ANONYMOUS',
    'LOGGED_USER',
    'CONTRIBUTOR',
    'MODERATOR',
    'ADMIN',
    'LOWER_LEVELS',
    'EXTENDED_LEVELS',
    'ALL_LEVELS'
]


logger = logging.getLogger(__name__)

default_app_config = 'geocontrib.apps.GeocontribConfig'

__version__ = '5.0.3'
