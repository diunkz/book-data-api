from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from ..core import crud, schemas
from ..core.database import SessionLocal

router = APIRouter(prefix="/api/v1", tags=["Books"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/books", response_model=List[schemas.BookSchema])
def read_books(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit)


@router.get("/books/search", response_model=List[schemas.BookSchema])
def search_books_endpoint(
    title: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.search_books(db, title=title, category=category)


@router.get("/books/top-rated", response_model=List[schemas.BookSchema])
def read_top_rated_books(limit: int = 5, db: Session = Depends(get_db)):
    return crud.get_top_rated_books(db, limit=limit)


@router.get("/books/price-range", response_model=List[schemas.BookSchema])
def read_books_by_price_range(
    max_price: Decimal,
    min_price: Decimal = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.get_books_by_price_range(db, min_price=min_price, max_price=max_price)


@router.get("/books/{book_id}", response_model=schemas.BookSchema)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_id(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return db_book


@router.get("/categories", response_model=List[str])
def read_categories(db: Session = Depends(get_db)):
    return crud.get_all_categories(db)
