from fastapi import FastAPI
from src.api import books, utils, stats, auth  # Importa os novos módulos de rota
from src.core import models
from src.core.database import engine
from src.core.logging_config import setup_api_logging

setup_api_logging()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Data API",
    description="Uma API para consulta de dados de livros extraídos "
    "do site books.toscrape.com",
    version="1.0.0",
)

# Inclui os roteadores na aplicação principal
app.include_router(utils.router)
app.include_router(books.router)
app.include_router(stats.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à Book Data API!"}
