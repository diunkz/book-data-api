# Book Data API 📚

Este repositório contém o código-fonte de uma API RESTful para consulta de dados de livros, desenvolvida como parte de um Tech Challenge. A solução inclui um pipeline de dados completo, desde a extração (web scraping), passando pelo carregamento em um banco de dados, até a disponibilização dos dados através de endpoints seguros e bem documentados.

## 🏛️ Arquitetura

O projeto é estruturado como um pipeline de dados desacoplado que alimenta uma API. O fluxo principal é:

`[Fonte Web] -> [1. Extração] -> [2. Armazenamento Intermediário] -> [3. Carregamento] -> [4. Banco de Dados] -> [5. API] -> [6. Cliente]`

![Diagrama da Arquitetura](arquitetura.png)

## ✨ Features

* **Pipeline de Dados Robusto:** Scripts separados para extração (`scrape`) e carregamento (`load`), com modo de continuação (`--append`) para resiliência.
* **Banco de Dados Versionado:** Uso de **SQLAlchemy** como ORM e **Alembic** para gerenciar as migrações do schema, garantindo consistência entre ambientes.
* **API Moderna:** Construída com **FastAPI**, com schemas de validação **Pydantic** e documentação interativa automática (Swagger UI).
* **Autenticação Segura:** Implementação de autenticação via **JWT** com endpoints para criação de usuários e login.
* **Qualidade de Código:** Formatação e linting garantidos por **Ruff** e **Black**.
* **Logging Estruturado:** Logs separados para o pipeline de dados (`ingestion.log`) e para a API (`api.log`), facilitando a depuração e monitoramento.

## 🛠️ Tecnologias Utilizadas

* **Python 3.13+**
* **Poetry** para gerenciamento de dependências.
* **FastAPI** como framework web.
* **Uvicorn** como servidor ASGI.
* **SQLAlchemy** como ORM.
* **Alembic** para migrações de banco de dados.
* **Pydantic** para validação de dados.
* **Ruff** e **Black** para qualidade de código.
* **HTTPX** e **BeautifulSoup4** para web scraping.

## 🚀 Setup e Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

### Pré-requisitos
* **Git**
* **Python 3.13** (recomendável gerenciar com `pyenv`)
* **Poetry**

### Passos de Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/diunkz/book-data-api
    cd book-data-api
    ```

2.  **Configure o Ambiente Python:**
    Se estiver usando `pyenv`, defina a versão local (opcional, mas recomendado).
    ```bash
    pyenv local 3.13.2
    ```

3.  **Instale as Dependências:**
    O Poetry irá ler o `pyproject.toml` e `poetry.lock` para criar um ambiente virtual e instalar todas as bibliotecas necessárias.
    ```bash
    poetry install
    ```

4.  **Configure as Variáveis de Ambiente:**
    Crie uma cópia do arquivo de exemplo `.env.example` e nomeie-a `.env`. Você precisará criar primeiro o arquivo `.env.example`.
    ```bash
    cp .env.example .env
    ```

    **Conteúdo para o arquivo `.env.example`:**
    ```env
    # Chave secreta para assinar os tokens JWT.
    # Em produção, use um valor longo e aleatório (ex: openssl rand -hex 32)
    SECRET_KEY="uma-chave-secreta-de-exemplo"

    # Algoritmo de assinatura do JWT
    ALGORITHM="HS256"

    # Tempo de expiração do token de acesso em segundos
    ACCESS_TOKEN_EXPIRE_SECONDS=1800 # 30 minutos
    ```

## ⚙️ Como Usar

O projeto possui três fluxos de trabalho principais: preparar o banco, popular os dados e rodar a API.

### 1. Preparar o Banco de Dados (Alembic)
Este comando lê os arquivos de migração e cria (ou atualiza) as tabelas no banco de dados. Execute-o uma vez durante o setup inicial ou após qualquer alteração nos modelos.

```bash
poetry run alembic upgrade head
```

### 2. Executar o Pipeline de Dados
O pipeline consiste em dois scripts que devem ser executados a partir da raiz do projeto.

**2.1. Extrair os Dados (Scraping):**
Este script raspa os dados do site e os salva em um arquivo CSV.

```bash
# Raspar todas as páginas
poetry run python -m scripts.scrape_books --pages all

# Raspar páginas específicas (ex: 1 e 5)
poetry run python -m scripts.scrape_books --pages "1, 5"
```

**2.2. Carregar os Dados para o Banco:**
Este script lê o arquivo CSV gerado e insere os dados no banco de dados.

```bash
# Carregar o arquivo padrão (books_data_detailed.csv)
poetry run python -m scripts.csv_to_books_db

# Limpar a tabela e carregar os dados do zero
poetry run python -m scripts.csv_to_books_db --clear_table
```

### 3. Rodar a API
Execute o servidor web Uvicorn para iniciar a API.

```bash
poetry run uvicorn main_api:app --reload
```
* A API estará disponível em `http://127.0.0.1:8000`.
* A documentação interativa (Swagger UI) estará em `http://127.0.0.1:8000/docs`.

## ✅ Qualidade de Código

Este projeto utiliza o **Ruff** para linting e formatação, garantindo um código limpo e padronizado.

* **Para verificar o código por erros e problemas de estilo:**
    ```bash
    poetry run ruff check .
    ```