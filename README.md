# Controle de Estoque

Sistema de controle de estoque em Python, com API REST em FastAPI, interface desktop em PySimpleGUI e armazenamento local em SQLite.

## Funcionalidades

- Cadastro, consulta, edição e exclusão de produtos.
- Busca na interface por nome ou categoria.
- Registro de entradas e saídas com observações.
- Histórico de movimentações.
- Alertas quando a quantidade disponível é menor ou igual ao estoque mínimo.
- Painel com total de produtos, quantidade de itens, valor em estoque e número de alertas.

## Tecnologias

| Componente | Tecnologia |
| --- | --- |
| API REST | FastAPI e Pydantic |
| Servidor da API | Uvicorn |
| Persistência | SQLAlchemy e SQLite |
| Interface desktop | PySimpleGUI |
| Comunicação da interface com a API | Requests |

## Como executar

Os comandos abaixo são para Windows com PowerShell. Execute-os na pasta raiz do projeto, pois o caminho do banco de dados é relativo a ela.

### 1. Obter o projeto

```powershell
git clone https://github.com/vitortuness/controle-de-estoque.git
cd controle-de-estoque
```

O acesso ao repositório privado exige uma conta do GitHub com permissão.

### 2. Criar o ambiente e instalar as dependências

É necessário ter Python com pip instalado. A interface desktop também utiliza o Tkinter, que pode ser verificado com `python -m tkinter`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy pydantic requests PySimpleGUI
```

O arquivo `requirements.txt` está vazio nesta versão; por isso, as dependências são listadas diretamente no comando. O projeto ainda não fixa versões das bibliotecas e a instalação em um ambiente novo precisa ser validada.

### 3. Iniciar a API

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.api:app --reload
```

Com a API em execução:

- API: http://127.0.0.1:8000
- Documentação interativa (Swagger UI): http://127.0.0.1:8000/docs
- Documentação ReDoc: http://127.0.0.1:8000/redoc

A pasta `data/`, o banco `estoque.db` e as tabelas são criados automaticamente na inicialização. O banco começa vazio em uma nova instalação.

### 4. Abrir a interface desktop

Mantenha a API em execução e abra outro terminal na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m ui.interface
```

A interface se conecta a `http://localhost:8000`, endereço definido em `ui/interface.py`. Também é possível utilizar a API diretamente pela documentação interativa, sem abrir a interface.

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/` | Consultar o status da API |
| GET | `/resumo` | Obter os indicadores do estoque |
| GET | `/produtos` | Listar produtos |
| GET | `/produtos/{produto_id}` | Consultar um produto |
| POST | `/produtos` | Cadastrar um produto |
| PUT | `/produtos/{produto_id}` | Atualizar nome, categoria, preço ou estoque mínimo |
| DELETE | `/produtos/{produto_id}` | Excluir um produto |
| POST | `/produtos/{produto_id}/entrada` | Registrar entrada |
| POST | `/produtos/{produto_id}/saida` | Registrar saída |
| GET | `/historico` | Listar movimentações; aceita o filtro `produto_id` |
| GET | `/alertas` | Listar produtos com estoque baixo |

Exemplo de corpo JSON para `POST /produtos`:

```json
{
  "nome": "Caderno",
  "categoria": "Papelaria",
  "quantidade": 20,
  "preco": 15.90,
  "qtd_minima": 5
}
```

Exemplo para registrar uma entrada ou saída:

```json
{
  "quantidade": 3,
  "observacao": "Movimentação de exemplo"
}
```

## Estrutura do projeto

```text
controle-de-estoque/
├── api/
│   └── api.py             # Rotas e modelos de requisição
├── controllers/
│   └── estoque.py         # Operações e indicadores do estoque
├── models/
│   ├── database.py        # Conexão, tabelas e inicialização do banco
│   └── movimentacao.py    # Entradas, saídas e histórico
├── ui/
│   └── interface.py       # Interface desktop
├── data/                 # Banco local, criado na execução
├── .gitignore
├── README.md
└── requirements.txt
```

## Dados e estado atual

Os produtos e as movimentações ficam em `data/estoque.db`. Esse arquivo é ignorado pelo Git; faça uma cópia dele, com a aplicação encerrada, para preservar os dados locais.

A API ainda não implementa autenticação. As instruções acima utilizam o servidor local para desenvolvimento. O projeto também não inclui uma suíte de testes automatizados.
