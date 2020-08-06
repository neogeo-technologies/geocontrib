from argparse import RawTextHelpFormatter
from collections import Counter
import itertools
import json
import logging
import re

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from ldap3 import Connection, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
from decouple import config, Csv

from geocontrib import choices
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission


LDAP_URI = config('LDAP_URI', default=None)
LDAP_USERDN = config('LDAP_BINDDN', default=None)
LDAP_PASSWD = config('LDAP_PASSWD', default=None)
LDAP_SEARCH_BASE = config('LDAP_SEARCH_BASE', default="dc=georchestra,dc=org")
LDAP_SEARCH_FILTER = config('LDAP_SEARCH_FILTER', default="(objectClass=person)")

MAPPED_REMOTE_FIELDS = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'username': 'uid',
    'email': 'mail',
    'member_of': 'memberOf',
}

PROTECTED_USER_NAMES = config('PROTECTED_USER_NAMES', default='', cast=Csv())
EXCLUDED_USER_NAMES = config('EXCLUDED_USER_NAMES', default='', cast=Csv())
ADMIN_USER_GROUPS = config(
    'ADMIN_USER_GROUPS',
    default='cn=SUPERUSER,ou=roles,dc=georchestra,dc=org;cn=ADMINISTRATOR,ou=roles,dc=georchestra,dc=org',
    cast=Csv(delimiter=';'))
EXCLUSIVE_USER_GROUPS = config(
    'EXCLUSIVE_USER_GROUPS',
    default='',
    cast=Csv(delimiter=';'))
EXCLUDED_USER_GROUPS = config(
    'EXCLUDED_USER_GROUPS',
    default='',
    cast=Csv(delimiter=';'))

User = get_user_model()

logger = logging.getLogger(__name__)


class GeorchestraImportError(Exception):
    pass


def get_mapped_value(row, key, default=None):
    if key in MAPPED_REMOTE_FIELDS.keys():
        return row.get(MAPPED_REMOTE_FIELDS[key], [default, ])
    return None


class Command(BaseCommand):

    help = """Import de données depuis une source georchestra.
$ python manage.py georchestra_user_sync
Configurez les paramètres LDAP_SEARCH_BASE, PROTECTED_USER_NAMES,
EXCLUDED_USER_NAMES, ADMIN_USER_GROUPS, EXCLUSIVE_USER_GROUPS et
EXCLUDED_USER_GROUPS pour cibler plus précisément les utilisateurs à
synchroniser."""

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def search_ldap(self, connection):
        connection.search(
            search_base=LDAP_SEARCH_BASE,
            search_filter=LDAP_SEARCH_FILTER,
            attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])

        return [json.loads(data.entry_to_json()).get('attributes', {}) for data in connection.entries]

    def get_remote_data(self):
        # récupérer les données remote depuis ce serveur et mapper les données
        # pour en faire une liste
        connection_dict = {
            "server": LDAP_URI,
            "user": LDAP_USERDN,
            "password": LDAP_PASSWD,
            "auto_bind": True
        }
        logger.debug("Ldap connexion parameters: {0}".format(connection_dict))
        connection = Connection(**connection_dict)
        data = self.search_ldap(connection)
        return data

    def check_remote_data(self, remote_data):
        if len(remote_data) == 0:
            return
        try:
            counter = Counter([get_mapped_value(row, 'username')[0] for row in remote_data])
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
            username__in=[get_mapped_value(row, 'username')[0] for row in remote_data]
        ).exclude(
            username__in=PROTECTED_USER_NAMES
        ).delete()
        logger.debug("Deleted users: {0}: ".format(deleted))

    def sync_ldap_groups(self, user, row):
        # Tous les utilisateurs LDAP doivent au moins avoir le role "utilisateur connecté"
        for project in Project.objects.all():
            Authorization.objects.get_or_create(
                project=project, user=user,
                defaults={'level': UserLevelPermission.objects.get(user_type_id=choices.LOGGED_USER)}
            )

        # On liste les noms de groupe auxquels est affilié l'utilisateur
        member_of = get_mapped_value(row, 'member_of', [])
        all_groups = [re.findall('cn=(.*?),', item) for item in member_of]
        flattened_groups = list(set(itertools.chain(*all_groups)))
        if len(flattened_groups) > 0:
            # Tous les utilisateurs LDAP membres de groupes référencés dans des 'ldap_project_contrib_groups'
            # et qui sont "utilisateur connecté" de ces projets deviennent contributeurs

            # On liste les projets pour lesquels l'utilisateur est membre des groupes 'ldap_project_contrib_groups'
            # Ces utilisateurs se retrouvent "contributeur" s'ils n'étaient pas déjà "modérateur"
            contrib_qs = Project.objects.filter(ldap_project_contrib_groups__overlap=flattened_groups)
            if contrib_qs.exists():
                for project in contrib_qs or []:
                    try:
                        auth = Authorization.objects.get(project=project, user=user)
                    except Authorization.DoesNotExist:
                        pass
                    else:
                        # Si un utilisateur d’un des groupes de 'ldap_project_contrib_groups'
                        # est déjà présent dans le projet comme modérateur
                        # il ne sera pas déclassé en contributeur,

                        # Si un utilisateur d’un des groupes de 'ldap_project_contrib_groups'
                        # est déjà présent dans le projet comme administrateur projet
                        # il sera automatiquement déclassé en contributeur,
                        # idem pour simple utilisateur
                        if auth.level.user_type_id != choices.MODERATOR:
                            auth.level = UserLevelPermission.objects.get(user_type_id=choices.CONTRIBUTOR)
                            auth.save(update_fields=['level', ])
                            logger.debug("User '{0}' set as {1}'s Project '{2}' ".format(
                                user.username, auth.level.user_type_id, project.slug)
                            )

            # On liste les projets pour lesquels l'utilisateur est membre des groupes 'ldap_project_admin_groups'
            # Les utilisateurs de ces groupes se retrouvent "administrateur de projet"
            admin_qs = Project.objects.filter(ldap_project_admin_groups__overlap=flattened_groups)
            if admin_qs.exists():
                for project in admin_qs or []:
                    # Si un utilisateur d’un rôle animateur dans le LDAP est déjà
                    # présent dans le projet comme contributeur ou modérateur
                    # il se verra automatiquement appliqué le rôle d’administrateur du projet
                    # (idem pour simple utilisateur)
                    auth, created = Authorization.objects.update_or_create(
                        project=project, user=user,
                        defaults={
                            'level': UserLevelPermission.objects.get(user_type_id=choices.ADMIN)
                        }
                    )

                    logger.debug("User '{0}' set as {1}'s Project '{2}' ".format(
                        user.username, auth.level.user_type_id, project.slug)
                    )

            # On liste les projets pour lesquels l'utilisateur n'est ni membre des groupes 'ldap_project_admin_groups'
            # ni membre des goupes 'ldap_project_contrib_groups'
            # Les utilisateurs absent de ces groupes se retrouvent simples "utilisateur connecté"
            not_admin_and_not_contrib_qs = Project.objects.exclude(ldap_project_admin_groups__overlap=flattened_groups)\
                .exclude(ldap_project_contrib_groups__overlap=flattened_groups)
            if not_admin_and_not_contrib_qs.exists():
                for project in not_admin_and_not_contrib_qs or []:
                    auth, created = Authorization.objects.update_or_create(
                        project=project, user=user,
                        defaults={
                            'level': UserLevelPermission.objects.get(user_type_id=choices.LOGGED_USER)
                        }
                    )

                    logger.debug("User '{0}' set as {1}'s Project '{2}' ".format(
                        user.username, auth.level.user_type_id, project.slug)
                    )

    def user_update_or_create(self, row):
        try:
            user, created = User.objects.update_or_create(
                username=get_mapped_value(row, 'username')[0],
                defaults=dict(
                    first_name=get_mapped_value(row, 'first_name', 'N/A')[0],
                    last_name=get_mapped_value(row, 'last_name', 'N/A')[0],
                    email=get_mapped_value(row, 'email', 'undefined@undefined.io')[0],
                )
            )

            # ajout des droits de super utilisateur aux utilisateurs appartenant aux groupes d'admin dans le ldap
            member_of = get_mapped_value(row, 'member_of')
            is_user_admin = False
            if member_of and ADMIN_USER_GROUPS:
                is_user_admin = True in [item in member_of for item in ADMIN_USER_GROUPS]
                if is_user_admin:
                    user.is_staff = True
                    user.is_admin = True
                    user.is_superuser = True
                    user.save()
            self.sync_ldap_groups(user, row)
        except Exception:
            logger.exception('User cannot be created: {0}'.format(row))
            pass
        else:
            logger.debug(
                'User {0} {1}'.format(user.username, 'created' if created else 'updated')
            )

    def create_users(self, remote_data):
        for row in remote_data:
            username = get_mapped_value(row, 'username')[0]

            # est-ce que l'utilisateur appartient aux groupes exclus ?
            excluded_user = False
            member_of = get_mapped_value(row, 'member_of')
            if member_of and EXCLUDED_USER_GROUPS:
                excluded_user = True in [item in member_of for item in EXCLUDED_USER_GROUPS]
                if excluded_user:
                    logger.debug(
                        'Excluded user - reason {0} - not created: {1}'.format('EXCLUDED_USER_GROUPS', username)
                    )

            # est-ce que l'utilisateur appartient à la liste des groupes exclusifs ?
            # s'il n'appartient à aucun de ces groupes il est exclu
            if not excluded_user and member_of and EXCLUSIVE_USER_GROUPS:
                included_user = True in [item in member_of for item in EXCLUSIVE_USER_GROUPS]
                if not included_user:
                    excluded_user = True
                    logger.debug(
                        'Excluded user - reason {0} - not created: {1}'.format('EXCLUSIVE_USER_GROUPS', username)
                    )

            # est-ce que l'utilisateur appartient à la liste des utilisateurs exclus
            if not excluded_user and EXCLUDED_USER_NAMES:
                if username in EXCLUDED_USER_NAMES:
                    excluded_user = True
                    logger.debug(
                        'Excluded user - reason {0} - not created: {1}'.format('EXCLUDED_USER_NAMES', username)
                    )

            if not excluded_user:
                self.user_update_or_create(row)
            else:
                # suppression de l'utilisateur sauf s'il fait partie des utilisateurs protégés
                User.objects.filter(username=username).exclude(username__in=PROTECTED_USER_NAMES).delete()

    def handle(self, *args, **options):
        remote_users = self.get_remote_data()
        logger.info(remote_users)
        self.check_remote_data(remote_users)
        self.flush_local_db(remote_users)
        self.create_users(remote_users)
