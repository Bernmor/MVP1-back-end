# API da Movie Dashboard

Uma API baseada em Flask para um painel de controle de filmes que permite aos usuários rastrear filmes que desejam assistir e assistiram.

## Descrição do Projeto

Esta API serve como back-end para o aplicativo Movie Dashboard. Ele fornece endpoints para gerenciamento de usuários, operações de banco de dados de filmes, rastreamento de lista de observação e estatísticas pessoais de filmes. A API é construída com Flask e usa SQLite via SQLAlchemy para persistência de dados.
### Principais Características

- Gestão de usuários (criar, ler, excluir)
- Gestão de listas de observação pessoais
- Watched movie tracking with ratings and notes
- Rastreamento de filmes assistidos com classificações e notas dados do painel de estatísticas do usuário

## Installation Instructions

### Prerequisites

- Python 3.8+ 
- pip (Python package installer)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bernmor/MVP1-back-end
   cd movie-dashboard-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual (recomendado)**
   - No Windows:
     ```bash
     venv\Scripts\activate
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Crie um diretório para a base de dados**
   ```bash
   mkdir -p database
   ```

6. **Rode a aplicação**
   ```bash
   python app.py
   ```

   A API estará disponível em `http://localhost:5000`.

## Documentação

A documentação da API está disponível através da UI do Swagger em `http://localhost:5000/api/docs` quando a aplicação está em execução.

### Principais Endpoints

- `/api/users` - Gestão de usuários
- `/api/movies` - Operações de catálogo de filmes
- `/api/users/{userId}/watchlist` - Gestão de listas de observação
- `/api/users/{userId}/watched` -  Gestão de filmes assistidos
- `/api/users/{userId}/stats` - Estatísticas do usuário

## Estrutura do Projeto

```
back_end/
├── app.py                  # Arquivo principal com as rotas de API
├── models/                 # Modelos de dados
│   ├── __init__.py         # Inicializa o BD
│   ├── base.py             # Classe base
│   ├── movies.py           # Modelo de filmes
│   ├── user.py             # Modelo de usuários
│   ├── user_movies.py      # Modelo de relacionamento User-movie
├── static/                 # Arquivos estáticos
│   └── swagger.json        # Documentação da API
├── database/               # Arquivos de SQLite
│   └── db.sqlite3          # Arquivo de BD
└── requirements.txt        # Dependências do projeto
```

## Feito com

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para operações de BD
- [SQLite](https://www.sqlite.org/) - BD
- [Flask-CORS](https://flask-cors.readthedocs.io/) - CORS para Flask
- [Flask-Swagger-UI](https://github.com/sveint/flask-swagger-ui) - Integração Swagger UI