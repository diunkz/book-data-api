from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..core import crud, schemas
from ..core.database import SessionLocal

router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/overview", response_model=schemas.StatsOverviewSchema)
def read_stats_overview(db: Session = Depends(get_db)):
    """
    Retorna um resumo completo com estatísticas gerais da coleção de livros.
    """
    stats = crud.get_stats_overview(db)
    category_stats = crud.get_stats_by_category(db)

    # Adiciona as estatísticas de categoria ao dicionário principal
    stats["categories_stats"] = category_stats

    return stats


@router.get("/categories", response_model=List[schemas.CategoryStatsSchema])
def read_stats_by_category(db: Session = Depends(get_db)):
    """
    Retorna estatísticas detalhadas para cada categoria de livro.
    """
    return crud.get_stats_by_category(db)
