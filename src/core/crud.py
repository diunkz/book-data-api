from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from decimal import Decimal
from typing import Optional, List
from statistics import median

from . import models


def get_books(db: Session, skip: int = 0, limit: int = 100):
    """Busca uma lista de livros no banco de dados com paginação."""
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book_by_id(db: Session, book_id: int):
    """Busca um único livro no banco de dados pelo seu ID."""
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def search_books(
    db: Session, title: Optional[str] = None, category: Optional[str] = None
):
    """Busca livros por título e/ou categoria."""
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.book_name.ilike(f"%{title}%"))
    if category:
        query = query.filter(models.Book.category.ilike(f"%{category}%"))
    return query.all()


def get_all_categories(db: Session) -> List[str]:
    """Retorna uma lista de todas as categorias únicas."""
    results = (
        db.query(models.Book.category).distinct().order_by(models.Book.category).all()
    )
    return [category[0] for category in results]


def get_stats_overview(db: Session):
    """Calcula as estatísticas gerais da coleção."""

    total_books = db.query(models.Book).count()
    total_categories = db.query(models.Book.category).distinct().count()
    total_stock_quantity = db.query(func.sum(models.Book.quantity)).scalar() or 0

    all_prices = [b.price for b in db.query(models.Book.price).all()]
    average_price = db.query(func.avg(models.Book.price)).scalar() or Decimal("0.0")
    median_price = median(all_prices) if all_prices else Decimal("0.0")

    cheapest_book_obj = db.query(models.Book).order_by(models.Book.price.asc()).first()
    most_expensive_book_obj = (
        db.query(models.Book).order_by(models.Book.price.desc()).first()
    )

    most_reviewed_book_obj = (
        db.query(models.Book).order_by(models.Book.number_of_reviews.desc()).first()
    )

    rating_dist_query = (
        db.query(models.Book.rating, func.count(models.Book.rating))
        .group_by(models.Book.rating)
        .all()
    )
    rating_distribution = {rating: count for rating, count in rating_dist_query}

    return {
        "total_books": total_books,
        "total_categories": total_categories,
        "total_stock_quantity": total_stock_quantity,
        "price_stats": {
            "average": average_price,
            "median": median_price,
            "cheapest_book": (
                {"name": cheapest_book_obj.book_name, "price": cheapest_book_obj.price}
                if cheapest_book_obj
                else None
            ),
            "most_expensive_book": (
                {
                    "name": most_expensive_book_obj.book_name,
                    "price": most_expensive_book_obj.price,
                }
                if most_expensive_book_obj
                else None
            ),
        },
        "most_reviewed_book": (
            {
                "name": most_reviewed_book_obj.book_name,
                "reviews": most_reviewed_book_obj.number_of_reviews,
            }
            if most_reviewed_book_obj
            else None
        ),
        "rating_distribution": rating_distribution,
    }


def get_stats_by_category(db: Session):
    """Calcula estatísticas detalhadas por categoria."""
    return (
        db.query(
            models.Book.category,
            func.count(models.Book.id).label("book_count"),
            func.avg(models.Book.price).label("average_price"),
        )
        .group_by(models.Book.category)
        .all()
    )


def get_top_rated_books(db: Session, limit: int = 5):
    """Retorna os livros com a maior avaliação."""
    return db.query(models.Book).order_by(desc(models.Book.rating)).limit(limit).all()


def get_books_by_price_range(db: Session, min_price: Decimal, max_price: Decimal):
    """Filtra livros dentro de uma faixa de preço."""
    return (
        db.query(models.Book)
        .filter(models.Book.price.between(min_price, max_price))
        .all()
    )
