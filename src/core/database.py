from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define o caminho para o arquivo do banco de dados SQLite
# Ele será criado na pasta 'data' na raiz do projeto
DATABASE_URL = "sqlite:///./data/books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base que os modelos ORM irão herdar
Base = declarative_base()
