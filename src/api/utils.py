from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
        db.execute("SELECT 1")
        return HealthCheckSchema(status="ok", database_connection="ok")
    except Exception:
        return HealthCheckSchema(status="ok", database_connection="error")
