from collections import Counter
import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ldap3 import Connection, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
from decouple import config, Csv

import logging


# TODO: A voir si ces variables doivent etre définies dans les settings
# ou juste au niveau systeme (je penche pour le systeme)
LDAP_URI = config('LDAP_URI', default=None)
LDAP_BINDDN = config('LDAP_BINDDN', default=None)
LDAP_PASSWD = config('LDAP_PASSWD', default=None)
LDAP_SEARCH_FILTER = config('LDAP_SEARCH_FILTER', default="(cn=*)")
PROTECTED_USERNAMES = config('PROTECTED_USERNAMES', cast=Csv())

MAPPED_REMOTE_FIELDS = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'username': 'uid',
    'email': 'mail'
}

User = get_user_model()

logger = logging.getLogger(__name__)


class GeorchestraImportError(Exception):
    pass


def get_mapped_value(row, key, default=None):
    if key in MAPPED_REMOTE_FIELDS.keys():
        return row.get(MAPPED_REMOTE_FIELDS[key], [default, ])[0]
    return None


class Command(BaseCommand):

    help = """Import de données depuis une source georchestra.
    $ python manage.py georchestra_import
    - Configurer MAPPED_REMOTE_FIELDS selon la structure de données source
    - Configurer PROTECTED_USERNAMES dans les settings en indiquant la liste
    des utilisateurs à conserver entre chaque import

    """

    def search_ldap(self, connection):
        connection.search(
            search_base="dc=georchestra,dc=org",
            search_filter=LDAP_SEARCH_FILTER,
            attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])

        return [json.loads(data.entry_to_json()).get('attributes', {}) for data in connection.entries]

    def get_remote_data(self):
        # TODO: Lorsque le docker de geoorchestra sera en place
        # recuperer les données remote depuis ce serveur et mapper les données
        # pour en faire une liste exploitable
        for key in [LDAP_URI, LDAP_BINDDN, LDAP_PASSWD]:
            logger.debug(key)
        connection = Connection(LDAP_URI, LDAP_BINDDN, LDAP_PASSWD, auto_bind=True)
        data = self.search_ldap(connection)
        return data

    def check_remote_data(self, remote_data):
        if len(remote_data) == 0:
            return
        try:
            counter = Counter([get_mapped_value(row, 'username') for row in remote_data])
        except KeyError:
            msg = "Données sources invalides: champs uid manquant"
            logger.error(msg)
            raise GeorchestraImportError(msg)

        for k, v in counter.items():
            if v > 1:
                msg = "Données sources invalides: deux instances ne peuvent avoir le meme username: {}".format(k)
                logger.error(msg)
                raise GeorchestraImportError(msg)

    def flush_local_db(self, remote_data):
        # suppression des utilisateurs absents de l'import en cours
        # on garde cependant les utilisateurs 'protégés'
        deleted = User.objects.exclude(
            username__in=[get_mapped_value(row, 'username') for row in remote_data]
        ).exclude(
            username__in=PROTECTED_USERNAMES
        ).delete()
        logger.debug(deleted)

    def user_update_or_create(self, row):
        try:
            user, created = User.objects.update_or_create(
                username=get_mapped_value(row, 'username'),
                defaults=dict(
                    first_name=get_mapped_value(row, 'first_name', 'N/A'),
                    last_name=get_mapped_value(row, 'last_name', 'N/A'),
                    email=get_mapped_value(row, 'email', 'undefined@undefined.io'),
                )
            )
        except Exception:
            logger.exception('User cannot be created: {0}'.format(row))
            pass
        else:
            logger.debug(
                'User {0} {1}'.format(user.username, 'created' if created else 'updated')
            )

    def create_users(self, remote_data):
        for row in remote_data:
            self.user_update_or_create(row)

    def handle(self, *args, **options):
        remote_users = self.get_remote_data()
        self.check_remote_data(remote_users)
        self.flush_local_db(remote_users)
        self.create_users(remote_users)
