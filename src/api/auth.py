# src/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core import crud, schemas, security
from ..core.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# Função de dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Dependência que decodifica o token, valida o usuário e o retorna.
    """
    username = security.decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post(
    "/users", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED
)
def create_new_user(user: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    """
    Cria um novo usuário.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username já registrado")
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.TokenSchema)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica o usuário e retorna um token de acesso.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserSchema)
def read_users_me(current_user: schemas.UserSchema = Depends(get_current_user)):
    """
    Endpoint de exemplo para buscar os dados do usuário logado.
    A proteção acontece na dependência `get_current_user`.
    """
    return current_user
