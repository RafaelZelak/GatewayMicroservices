# 1. Criar a Pasta do Serviço

Dentro do diretório services/, crie uma nova pasta para o seu serviço. Por exemplo, se você deseja criar um serviço chamado novo_servico, a estrutura ficaria:

````
services/
└── novo_servico/
    ├── __init__.py
    └── name.py
````

# 2. Criar o Arquivo de Rotas (name.py)

Este arquivo vai conter toda a lógica da sua aplicação, podendo ser tando um Webhook para uma API rest, quanto um template para sua aplicação

### 2.1 - Exemplo de aplicação para API Restful (GET e POST)

```` python
from flask import jsonify, request
from flask.views import MethodView

class WebhookNovoServico(MethodView):
    def get(self):
        return jsonify({"message": "GET recebido no novo serviço"}), 200

    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum payload JSON enviado"}), 400
        return jsonify({"message": "POST recebido no novo serviço", "data": data}), 200
````

**Importações**:
- `jsonify` e `request` são usados para lidar com requisições e respostas em JSON, que é padrão em APIs RESTful.
- `MethodView` permite criar views baseadas em classe, facilitando a separação de lógica para diferentes métodos HTTP.

**Classe WebhookNovoServico:**
- Define dois métodos, `get` e `post`, que lidam respectivamente com requisições GET e POST para o mesmo endpoint.
- Essa estrutura torna o código mais organizado e escalável, especialmente quando o endpoint precisa suportar vários métodos.

### 2.2 Exemplo de aplicação para `render_template`

``` Python
from flask import Blueprint, render_template
from .views import WebhookNovoServico

# Criação do blueprint para o novo serviço
novo_servico_bp = Blueprint('novo_servico', __name__, template_folder='templates')

# Rota que renderiza um template
@novo_servico_bp.route('/pagina')
def exibir_pagina():
    return render_template('pagina_novo_servico.html')

# Registra a rota do webhook com os métodos GET e POST utilizando a classe definida em views.py
novo_servico_bp.add_url_rule('/webhook', view_func=WebhookNovoServico.as_view('webhook_novo_servico'))
```
<br><br>
**Importações e Criação do Blueprint:**
- `Blueprint` é usado para agrupar as rotas e recursos deste serviço.
- O parâmetro `__name__` indica o nome do módulo atual e `template_folder='templates'` especifica onde os arquivos HTML estão localizados, mantendo os templates organizados dentro do serviço.
<br><br>
**Rota com render_template:**
- A função `exibir_pagina` mapeada para a rota `/pagina` usa `render_template` para renderizar o arquivo `pagina_novo_servico.html`.
- Isso permite separar a lógica de apresentação (HTML) da lógica de processamento.
<br><br>
**Registro da Rota Webhook:**
- `add_url_rule` associa a rota `/webhook` à view baseada na classe `WebhookNovoServico`.
- A função `as_view('webhook_novo_servico')` converte a classe em uma view que pode lidar com diferentes métodos HTTP (GET e POST).
- Essa abordagem permite que a mesma URL gerencie múltiplos métodos de forma organizada.