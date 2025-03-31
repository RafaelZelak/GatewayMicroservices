# Como usar o Gateway:

### Criação de projeto

Todo projeto do gateway ficará armazenado dentro da pasta `./services`.
Onde o nome do projeto é livre, desde que não utilize o mesmo de um projeto já existente

Para fins de exemplificação usaremos os projetos

`./services/template_example` < - Exemplo de uso com Template
`./services/webhook_example` <- Exemplo de uso com Webhook

___
### Projeto com template

#### Estrutura
A estrutura de pastas do deve seguir algumas regras:

Sempre será definida dentro de `./services/`

onde uma pasta com o nome do seu projeto será criada

`mkdir ./services/nome_do_projeto`

E dentro dele, teremos alguns arquivos obrigatórios

(Exemplo de projeto com Template)
``` Bash
template_example/
│── routes.py
│── secured_route.yml
│── __init__.py
│
├── templates/
    ├── index.html
```
- `routes.py` Define TODAS as rotas da sua aplicação
- `secured_route.yml` Arquivo com as permissões de acesso à rota
- `__init__.py` Arquivo vazio apenas para definir diretório Python
- `templates/index.html` Arquivo HTML da rota "/" do seu projeto

Apenas estes arquivos e pastas são obrigatórios, fora eles, você está livre para criar o seu sistema da forma que preferir

#### Importações:
Alguns módulos são necessários para rodar o gateway
```python
from flask import Blueprint
from services.config import create_blueprint_env, secured_route
import os
```
- `flask` - Lib base do gateway utilizada para criar as rotas (APIs)

- `os` - utilizado caso sua rota precise utilizar autenticação LDAP (Explicarei mais tarde neste mesmo documento)

- `from services.config import create_blueprint_env, secured_route` -  Importações do arquivo de configurações, a importação do `create_blueprint_env` é obrigatória, já a importação do `secured_route` é opicional, apenas caso uma rota precise de auth LDAP

#### Gerar Blueprint:
``` python
template_bp = Blueprint('template_service', __name__, template_folder='templates')
```
- `template_bp` - nome da variável do blueprint (será importado no config_flask.py)
- `template_service` - nome do blueprint (deve ser único)
- `template_folder` - diretório relativo de templates (manter como 'templates')

#### Importar arquivo .yml para poder usar `secured_route`:
``` python
template_bp.secured_config_path = os.path.join(os.path.dirname(__file__), "secured_route.yml")
```

> [!WARNING]  
> Caso no seu .env não tiver configurado um dominio LDAP ou você não tenha um dominio LDAP
> Ignore esta parte e pule para "Rota Default"

Arquivo Secure Route:
`secured_route.yml`

``` yml
# Grupos do LDAP com acesso a rota
allowed_groups:
  - "grupoLDAP"

# Users com acesso a rota
allowed_users:
  - "UserLDAP"
```

Caso não tenha Grupo ou User para adicionar, use None

#### Rota Default:

Para definir uma rota, basta chamar o Blueprint gerado, e definir a rota `@template_bp.route('/')`

A rota `/` sempre vai ser a rota padrão definida no config_flask.py (será melhor explicado mais para frente)

Dentro da rota definimos a variável, por exemplo `def index():` e criamos o ambiente para templates do Blueprint `env = create_blueprint_env(__file__)`.

Depois definimos o template que iremos renderizar `template = env.get_template('index.html')` e por fim renderizamos ele `return template.render()`

No final vai ficar algo como

``` python
@template_bp.route('/')
def index():
    env = create_blueprint_env(__file__)
    template = env.get_template('index.html')
    return template.render()
```

#### Rota Segura:

Agora vamos definir uma subrota e habilitar a autenticação via LDAP

para definir uma rota como segura, usamos `@secured_route(blueprint, '/sub-rota', login=True)` e depois continuamos como uma rota normal

``` Python
@secured_route(template_bp, '/home', login=True)
def home():
    env = create_blueprint_env(__file__)
    template = env.get_template('home.html')
    return template.render()
```
___
### Projeto Webhook
Projetos Webhook, ou projetos sem interface, devem seguir o padrão Restful para manter a qualidade e legibilidade do código

#### Estrutura
A estrutura de pastas do deve seguir algumas regras:

Sempre será definida dentro de `./services/`

onde uma pasta com o nome do seu projeto será criada

`mkdir ./services/nome_do_projeto`

E dentro dele, teremos alguns arquivos obrigatórios

(Exemplo de projeto Webhook)
``` Bash
template_example/
│── routes.py
│── __init__.py
```
- `routes.py` Define TODAS as rotas e métodos da sua aplicação
- `__init__.py` Arquivo vazio apenas para definir diretório Python

Apenas estes arquivos e pastas são obrigatórios, fora eles, você está livre para criar o seu sistema da forma que preferir

#### Importações:
Alguns módulos são necessários para rodar o gateway
```python
from flask import Blueprint
from flask.views import MethodView
```
`flask` - Lib base do gateway utilizada para criar as rotas (APIs)

`flask MethodView` - Utilizado para configurar APIs REST

Para esse caso criei um aruquivo de Enum que serve para enumerar retornos de requisições HTTP, caso queira usar basta importar:

```python
from enums.http_status_enum import HttpStatusEnum
```

#### Gerar Blueprint:
``` python
webhook_bp = Blueprint('webhook_service', __name__)
```
- `webhook_bp` - nome da variável do blueprint (será importado no config_flask.py)

#### Criação da Classe para API REST:

```python
class WebhookAPI(MethodView):
```
WebhookAPI que herda de MethodView

Essa classe será responsável por lidar com as requisições HTTP

#### Métodos:

Podemos usar todos os métodos de uma API REST como funções
`GET, POST, PUT, DELETE, etc.`

Vamos fazer um exemplo com `GET` e `POST`

**GET:**
``` Python
    def get(self):
        return jsonify({"message": "Webhook GET recebido com sucesso"}), HttpStatusEnum.OK.value
```
**POST:**
```Python
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Payload JSON não fornecido"}), HttpStatusEnum.BAD_REQUEST.value

        return jsonify({"message": "Webhook POST recebido com sucesso", "data": data}), HttpStatusEnum.OK.value
```

#### Registrar a rota:

Agora precisamos registra a view para a rota /webhook, associando os métodos GET e POST

Ficando a URL final: `/api/webhook`

Quando lidamos com webhook, definimos sempre um url_rule para cada método HTTP
sendo /webhook a subrota do blueprint e as_view('webhook_api') o nome da view (devem ser únicos)

Com a estrutura final sendo:

``` Python
webhook_bp.add_url_rule('/webhook', view_func=WebhookAPI.as_view('webhook_api'))
```
___
### Definir rota Flask

Para definir uma rota, é necessário importar o projeto e definir a rota em `./config_flask.py`

onde no inicio do arquivo, importamos o blueprint do projeto

Para exemplo, iremos definir as rotas dos dois porojetos criados:

```python
from services.template_example.routes import template_bp
from services.webhook_example.routes import webhook_bp
```

sendo `template_bp` o Blueprint definido no arquivo routes.py no projeto template_example

Após isso registra a rota para o projeto

```python
 app.register_blueprint(template_bp, url_prefix='/template')
 app.register_blueprint(webhook_bp, url_prefix='/api')
```

Agora todo o seu projeto está configurado, mas agora precisamos inicia-lo

Caso seja a primeira vez que o projeto está sendo rodado, execute (com privilégios de ADM) o arquivo `localhost.ps1` para adicionar o `http://gateway.localhost/` na tabela de hosts do PC

Caso queira modificar manualmente, basta abrir o arquivo

`C:\Windows\System32\drivers\etc\hosts`

E adcionar a seguinte linha no final do arquivo:

`127.0.0.1    gateway.localhost`

Após este processo, vamos rodar o Docker, para este projeto, utilizamos Docker Composer

- `docker compose up --build -d`

Com isso sua imagem Docker vai ser montada e automaticamente o servidor vai ser inicializado (para isso é necessário ter o Docker Desktop baixado)

Caso precise aplicar alguma modificação no código, é necessário desativar o Conteiner

- `docker compose down`

E depois ativa-lo novamente.

Com o projeto rodando, é possível acessar seu template em

`http://gateway.localhost/template/`

Ou você pode fazer uma requisição HTTP usando o Bruno

## Temos a parte de Database e uma Seed para exemplo

para adicionar mais seeds basta colocar o arquivo JSON na pasta:

`./seed/data/*.json`

E no arquivo:

`./seed/migration.py`

adicionar na linha:
``` python
    SEED_FILES = [
        ("cnaes", "seed/data/cnaes.json"),
        ("nova_collection", "seed/data/nova_collection.json")
    ]
```
