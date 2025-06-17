# accounts/ldap_backend.py

from ldap3 import Server, Connection, ALL, SUBTREE
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from decouple import config

LDAP_SERVER_URI = config('LDAP_SERVER_URI', default=None)
BASE_DN = config('LDAP_BASE_DN', default='ou=system')
BIND_DN_TEMPLATE = config('LDAP_BIND_DN_TEMPLATE', default='uid={},ou=system') 

class LDAPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        user_dn = BIND_DN_TEMPLATE.format(username)

        try:
            server = Server(LDAP_SERVER_URI, get_info=ALL)
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)

            if conn.bound:
                conn.search(
                    search_base=BASE_DN,
                    search_filter=f'(uid={username})',
                    search_scope=SUBTREE,
                    attributes=['cn', 'sn']
                )

                if conn.entries:
                    entry = conn.entries[0]
                    User = get_user_model()
                    user, created = User.objects.get_or_create(username=username)
                    user.first_name = entry.cn.value if 'cn' in entry else ''
                    user.last_name = entry.sn.value if 'sn' in entry else ''
                    user.set_unusable_password()
                    user.save()
                    return user
        except Exception as e:
            print(f"[LDAP ERROR] {e}")
            return None

        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
