# API de Pedidos — Trabalho 1

**Disciplina:** Desenvolvimento de Sistemas Distribuídos  
**Instituição:** Universidade Paulista (UNIP)

## Integrantes do grupo

| Nº | Nome completo | Turma | RA | Repositório |
|---|---|---|---|---|
| 1 | Jonathan Maciel | CC8Q13 | N137FE2 | https://github.com/Jhonny2508/api-pedidos |
| 2 | Kezia Chianca | CC8Q13 | F350FF0 | https://github.com/keziabash-dot/api-pedidos |
| 3 | Steffany Caroline | CC8Q13 | G843193 | https://github.com/Steffany-Oli/api-pedidos |
| 4 | Willian Machado | CC8Q13 | F3516C2 | https://github.com/WillianapMachado/api-pedidos |

## 1. Objetivo

O projeto consiste no desenvolvimento de uma API de Pedidos utilizando FastAPI e PostgreSQL, com a aplicação e o banco de dados executando separadamente por meio de containers Docker.

A aplicação permite realizar as principais operações relacionadas aos pedidos, incluindo criação, consulta, listagem e alteração de status.

A solução foi organizada em três camadas lógicas:

- **API:** responsável pelo recebimento das requisições HTTP e retorno das respostas.
- **Service:** responsável pela lógica da aplicação e pelas regras dos pedidos.
- **Repository:** responsável pelo acesso e persistência dos dados no banco de dados.

## 2. Arquitetura da solução

A arquitetura da primeira versão do sistema é composta por um cliente, a aplicação de Pedidos e o PostgreSQL.

```text
Cliente
   │
   │ HTTP/JSON
   ▼
┌───────────────────────────────┐
│       Container pedidos       │
│                               │
│  API → Service → Repository   │
└───────────────┬───────────────┘
                │
                │ Protocolo PostgreSQL
                ▼
┌───────────────────────────────┐
│      Container postgres       │
│                               │
│       Volume postgres_data    │
└───────────────────────────────┘
```

A aplicação de Pedidos e o PostgreSQL são executados como componentes separados. As camadas API, Service e Repository permanecem dentro do mesmo processo da aplicação de Pedidos.

### Camada API

Responsável pela interface HTTP, recebendo as requisições e produzindo as respostas da aplicação.

### Camada Service

Responsável pela lógica da aplicação, incluindo o cálculo do `valor_total`, definição do status inicial e tratamento das alterações de status.

### Camada Repository

Responsável pelas operações de persistência e pelo acesso ao banco de dados PostgreSQL.

## 3. Tecnologias utilizadas

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose
- Pydantic

## 4. Estrutura do projeto

```text
app/
├── main.py
├── database.py
├── api/
│   ├── pedidos.py
│   └── health.py
├── services/
│   └── pedido_service.py
├── repositories/
│   └── pedido_repository.py
├── models/
│   └── pedido.py
└── schemas/
    ├── pedido.py
    └── health.py

Dockerfile
docker-compose.yml
requirements.txt
.env.example
.gitignore
.dockerignore
.gitattributes
README.md
```

## 5. Modelo de Pedido

O modelo de pedido possui os seguintes campos:

| Campo | Descrição |
|---|---|
| `id` | Identificador do pedido |
| `cliente` | Identificação textual do cliente |
| `produto` | Identificação textual do produto |
| `quantidade` | Quantidade solicitada |
| `valor_unitario` | Valor de uma unidade do produto |
| `valor_total` | Valor total calculado pela aplicação |
| `status` | Estado atual do pedido |
| `data_criacao` | Data e hora de criação do pedido |

O `valor_total` é calculado pela aplicação a partir da seguinte operação:

```text
valor_total = quantidade × valor_unitario
```

O campo `valor_total` não é informado pelo cliente na criação do pedido.

## 6. Status do pedido

Os estados utilizados nesta versão são:

```text
CRIADO
CONFIRMADO
CANCELADO
```

As transições implementadas são:

```text
CRIADO → CONFIRMADO
CRIADO → CANCELADO
CONFIRMADO → CANCELADO
```

O estado `CANCELADO` é considerado final.

Tentativas de realizar uma transição de status não permitida retornam `409 Conflict`.

## 7. Endpoints

| Método | Endpoint | Descrição | Respostas principais |
|---|---|---|---|
| `POST` | `/pedidos` | Cria um novo pedido | `201`, `422` |
| `GET` | `/pedidos` | Lista os pedidos cadastrados | `200` |
| `GET` | `/pedidos/{id}` | Consulta um pedido específico | `200`, `404` |
| `PATCH` | `/pedidos/{id}/status` | Altera o status de um pedido | `200`, `404`, `409`, `422` |
| `GET` | `/health` | Verifica o estado da aplicação | `200` |

## 8. Criação de pedido

Para criar um pedido, devem ser informados:

- `cliente`
- `produto`
- `quantidade`
- `valor_unitario`

Exemplo:

```json
{
  "cliente": "Maria Silva",
  "produto": "Teclado",
  "quantidade": 2,
  "valor_unitario": 249.90
}
```

A aplicação calcula automaticamente o `valor_total` e define o status inicial como `CRIADO`.

A resposta esperada possui o pedido criado e retorna o status HTTP `201 Created`.

## 9. Consulta de pedido

Para consultar um pedido específico:

```text
GET /pedidos/{id}
```

Quando o pedido existe, a API retorna `200 OK`.

Quando o identificador informado não corresponde a um pedido cadastrado, a API retorna `404 Not Found`.

## 10. Listagem de pedidos

O endpoint:

```text
GET /pedidos
```

retorna a coleção de pedidos existentes no banco de dados.

Nesta versão não é utilizada paginação.

## 11. Alteração de status

O endpoint:

```text
PATCH /pedidos/{id}/status
```

recebe o novo estado do pedido.

Exemplo:

```json
{
  "status": "CONFIRMADO"
}
```

A alteração respeita as transições de status definidas para a aplicação.

## 12. Endpoint de saúde

O endpoint:

```text
GET /health
```

é utilizado para verificar se a aplicação está operacional.

Resposta esperada:

```json
{
  "status": "ok"
}
```

## 13. Persistência no PostgreSQL

Os pedidos são persistidos em um banco de dados PostgreSQL executado em um container separado da aplicação.

Os dados são armazenados no volume Docker:

```text
postgres_data
```

Dessa forma, os pedidos não dependem da memória da aplicação e permanecem disponíveis após o reinício do container `pedidos`.

Para testar a persistência:

```bash
docker compose restart pedidos
```

Depois do reinício, o mesmo pedido pode ser consultado novamente pela API.

## 14. Configuração

A conexão com o PostgreSQL é configurada por meio da variável de ambiente:

```text
DATABASE_URL
```

As informações de endereço, porta, usuário e senha do banco não ficam fixadas diretamente no código da aplicação.

O arquivo:

```text
.env.example
```

contém um exemplo das variáveis utilizadas pelo Docker Compose.

O arquivo `.env` não é obrigatório para a execução inicial, pois o `docker-compose.yml` possui valores padrão.

## 15. Docker

A solução utiliza dois serviços no Docker Compose:

### `pedidos`

Serviço responsável pela execução da API FastAPI.

A API é disponibilizada na porta:

```text
8000
```

### `postgres`

Serviço responsável pelo banco de dados PostgreSQL.

O PostgreSQL é acessível pela aplicação por meio da rede interna do Docker.

Os dados são mantidos pelo volume:

```text
postgres_data
```

## 16. Pré-requisitos

Para executar o projeto, é necessário possuir:

- Docker Desktop instalado;
- Docker Compose v2;
- Git, caso o projeto seja obtido diretamente do GitHub.

## 17. Execução do projeto

Após obter o repositório, entre na pasta do projeto e utilize:

```bash
git checkout APIPedidos-1-final
docker compose up -d --build
```

A API estará disponível em:

```text
http://localhost:8000
```

A documentação interativa do FastAPI estará disponível em:

```text
http://localhost:8000/docs
```

As tabelas utilizadas pela aplicação são criadas automaticamente durante a inicialização.

## 18. Exemplo de obtenção do projeto

```bash
git clone https://github.com/keziabash-dot/api-pedidos.git
cd api-pedidos
git checkout APIPedidos-1-final
docker compose up -d --build
```

## 19. Exemplos de teste

### Verificar a saúde da aplicação

```bash
curl http://localhost:8000/health
```

Resposta:

```json
{
  "status": "ok"
}
```

### Criar um pedido

No Windows PowerShell, pode ser utilizado `curl.exe`:

```bash
curl.exe -X POST http://localhost:8000/pedidos -H "Content-Type: application/json" -d "{\"cliente\":\"Maria Silva\",\"produto\":\"Teclado\",\"quantidade\":2,\"valor_unitario\":249.90}"
```

### Listar pedidos

```bash
curl.exe http://localhost:8000/pedidos
```

### Consultar um pedido

```bash
curl.exe http://localhost:8000/pedidos/1
```

### Consultar um pedido inexistente

```bash
curl.exe -i http://localhost:8000/pedidos/9999
```

### Alterar o status de um pedido

```bash
curl.exe -X PATCH http://localhost:8000/pedidos/1/status -H "Content-Type: application/json" -d "{\"status\":\"CONFIRMADO\"}"
```

## 20. Experimento de persistência

Uma forma de verificar a persistência dos dados é:

### 1. Criar um pedido

```bash
curl.exe -X POST http://localhost:8000/pedidos -H "Content-Type: application/json" -d "{\"cliente\":\"Ana\",\"produto\":\"Mouse\",\"quantidade\":1,\"valor_unitario\":80}"
```

### 2. Consultar o pedido

```bash
curl.exe http://localhost:8000/pedidos/1
```

### 3. Reiniciar somente a aplicação

```bash
docker compose restart pedidos
```

### 4. Consultar novamente o pedido

```bash
curl.exe http://localhost:8000/pedidos/1
```

O pedido deve continuar disponível, pois os dados estão armazenados no PostgreSQL e associados ao volume persistente.

## 21. Comandos úteis

Verificar o estado dos containers:

```bash
docker compose ps
```

Visualizar os logs da aplicação:

```bash
docker compose logs -f pedidos
```

Visualizar os logs do PostgreSQL:

```bash
docker compose logs -f postgres
```

Parar os containers:

```bash
docker compose down
```

Parar os containers e remover também o volume do banco:

```bash
docker compose down -v
```

## 22. Versão final para avaliação

A versão entregue para avaliação está identificada pela tag:

```text
APIPedidos-1-final
```

Para utilizar exatamente a versão entregue:

```bash
git checkout APIPedidos-1-final
```

Depois:

```bash
docker compose up -d --build
```

A avaliação deve considerar o conteúdo associado a essa tag.