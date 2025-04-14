import os
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# importando os elementos definidos no modelo
from models.base import Base
from models.movies import Movies
from models.user_movies import UserMovie
from models.user import User

# url de acesso ao banco (essa é uma url de acesso ao sqlite local)

if not os.path.exists("./database"):
    os.makedirs("./database")

db_url = 'sqlite:///database/db.sqlite3'

# cria a engine de conexão com o banco
engine = create_engine(db_url, echo=False)

# Instancia um criador de seção com o banco
Session = sessionmaker(bind=engine)

# cria o banco se ele não existir
if not database_exists(engine.url):
    create_database(engine.url)

# cria as tabelas do banco, caso não existam
Base.metadata.create_all(engine)