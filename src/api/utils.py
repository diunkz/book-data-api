import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import SessionLocal
from ..core.schemas import HealthCheckSchema

logger = logging.getLogger(__name__)

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
        db.execute(text("SELECT 1"))
        return HealthCheckSchema(status="ok", database_connection="ok")
    except Exception as e:
        logger.error(f"Health check falhou na conexão com o DB: {e}")
        return HealthCheckSchema(status="ok", database_connection="error")
