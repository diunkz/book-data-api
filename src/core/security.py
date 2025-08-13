from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# Importa nossas configurações centralizadas
from .config import settings

# --- Configuração de Hashing de Senhas ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções de Utilitário que agora usam as configurações do .env ---


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde à senha criptografada."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera o hash (versão criptografada) de uma senha."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            # minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodifica um token de acesso.
    Retorna o username se o token for válido, ou None caso contrário.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        # Se o token for inválido (expirado, assinatura errada, etc.)
        return None
