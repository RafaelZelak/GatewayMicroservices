# services/auth_service.py
import getpass
import yaml
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE
from decouple import config

class AuthService:
    @staticmethod
    def get_admin_connection():
        try:
            domain = config('AD_DOMAIN')
            admin_user = config('AD_ADMIN_USER')
            admin_password = config('AD_ADMIN_PASSWORD')

            server = Server(domain, get_info=ALL_ATTRIBUTES)
            admin_conn = Connection(
                server,
                user=f'{admin_user}@{domain}',
                password=admin_password,
                authentication='SIMPLE'
            )
            if admin_conn.bind():
                return admin_conn
            else:
                print("Falha ao conectar com credenciais de administrador.")
                return None
        except Exception as e:
            print("Erro ao obter conexão de administrador:", e)
            return None

    @staticmethod
    def authenticate(username, password):
        try:
            domain = config("AD_DOMAIN")
            server = Server(domain, get_info=ALL_ATTRIBUTES)
            user_dn = f'{username}@{domain}'

            # Validação das credenciais do usuário
            conn = Connection(server, user=user_dn, password=password)
            if not conn.bind():
                print("Falha na autenticação do usuário.")
                return None
            conn.unbind()

            # Busca detalhes do usuário (ex.: grupos) via conexão de administrador
            admin_conn = AuthService.get_admin_connection()
            if not admin_conn:
                print("Não foi possível conectar com as credenciais de administrador.")
                return None

            search_base = f"DC={domain.replace('.', ',DC=')}"
            search_filter = f"(sAMAccountName={username})"
            admin_conn.search(
                search_base,
                search_filter,
                search_scope=SUBTREE,
                attributes=["memberOf", "displayName"]
            )
            if admin_conn.entries:
                user_entry = admin_conn.entries[0]
                display_name = user_entry.displayName.value if hasattr(user_entry, 'displayName') else username
                groups = user_entry.memberOf.values if hasattr(user_entry, 'memberOf') else []
                # Extrai somente o nome comum (CN) de cada grupo
                cn_groups = [group.split(",")[0].replace("CN=", "") for group in groups]
                admin_conn.unbind()
                return {
                    'username': username,
                    'display_name': display_name,
                    'groups': cn_groups
                }
            else:
                print("Usuário não encontrado na pesquisa LDAP.")
                admin_conn.unbind()
                return None
        except Exception as e:
            print("Erro durante a autenticação:", e)
            return None

def load_access_config(yaml_file):
    """
    Carrega a configuração de acesso do arquivo YAML.
    Retorna um dicionário com as chaves 'allowed_groups' e 'allowed_users'.
    """
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            allowed_groups = data.get('allowed_groups', [])
            # Se allowed_groups tiver [null] ou estiver vazio, retorna None
            if allowed_groups and allowed_groups[0] is None:
                allowed_groups = None
            allowed_users = data.get('allowed_users', [])
            return {
                'allowed_groups': allowed_groups,
                'allowed_users': allowed_users
            }
    except Exception as e:
        print("Erro ao carregar o arquivo YAML:", e)
        return {'allowed_groups': None, 'allowed_users': []}
