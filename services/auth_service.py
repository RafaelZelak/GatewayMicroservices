# NÃO MEXER NESTE ARQUIVO!

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()

class AuthService:
    @staticmethod
    def authenticate(username, password):
        try:
            domain = os.environ.get("DOMAIN")
            server = Server(domain, get_info=ALL_ATTRIBUTES)
            user_dn = f'{username}@{domain}'

            conn = Connection(server, user=user_dn, password=password)
            if not conn.bind():
                print("Falha na autenticação do usuário.")
                return None

            search_base = f"DC={domain.replace('.', ',DC=')}"
            search_filter = f"(sAMAccountName={username})"
            conn.search(
                search_base,
                search_filter,
                search_scope=SUBTREE,
                attributes=["memberOf", "displayName"]
            )
            if conn.entries:
                user_entry = conn.entries[0]
                display_name = user_entry.displayName.value if hasattr(user_entry, 'displayName') else username
                groups = user_entry.memberOf.values if hasattr(user_entry, 'memberOf') else []
                cn_groups = [group.split(",")[0].replace("CN=", "") for group in groups]
                conn.unbind()
                return {
                    'username': username,
                    'display_name': display_name,
                    'groups': cn_groups
                }
            else:
                print("Usuário não encontrado na pesquisa LDAP.")
                conn.unbind()
                return None
        except Exception as e:
            print("Erro durante a autenticação:", e)
            return None
