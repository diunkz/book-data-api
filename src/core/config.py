from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # As variáveis aqui terão seus valores lidos do arquivo .env
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    # ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


# Cria uma instância única das configurações que será usada em todo o projeto
settings = Settings()
