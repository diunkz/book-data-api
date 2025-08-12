from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- 1. IMPORTE A FUNÇÃO 'text'
from ..core.database import SessionLocal
from ..core.schemas import HealthCheckSchema

router = APIRouter(tags=["Utilities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/v1/health", response_model=HealthCheckSchema)
def health_check(db: Session = Depends(get_db)):
    """Verifica o status da API e a conectividade com o banco de dados."""
    try:
        # --- 2. USE a função text() AQUI ---
        db.execute(text("SELECT 1"))
        return HealthCheckSchema(status="ok", database_connection="ok")
    except Exception as e:
        # Se ocorrer qualquer erro na linha acima, ele cai aqui
        logging.getLogger(__name__).error(
            f"Health check falhou na conexão com o DB: {e}"
        )
        return HealthCheckSchema(status="ok", database_connection="error")
