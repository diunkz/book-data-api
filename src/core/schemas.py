from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, List, Dict


# Schema para exibir um livro
class BookSchema(BaseModel):
    id: int
    upc: str
    book_name: str
    currency: str
    price: Decimal
    quantity: int
    availability: bool
    rating: int
    number_of_reviews: int
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    source_page: int

    class Config:
        from_attributes = True


# Schema para o endpoint de health check
class HealthCheckSchema(BaseModel):
    status: str = "ok"
    database_connection: str = "ok"


# Schema para estatísticas de uma categoria
class CategoryStatsSchema(BaseModel):
    category: str
    book_count: int
    average_price: Decimal

    class Config:
        from_attributes = True


class ExtremeBookSchema(BaseModel):
    """Schema para representar um livro em um extremo
    (mais caro/barato ou mais avaliado)."""

    name: str
    price: Optional[Decimal] = None
    reviews: Optional[int] = None


class PriceStatsSchema(BaseModel):
    """Schema para as estatísticas de preço."""

    average: Decimal
    median: Decimal
    cheapest_book: Optional[ExtremeBookSchema] = None
    most_expensive_book: Optional[ExtremeBookSchema] = None


class StatsOverviewSchema(BaseModel):
    """Schema para as estatísticas gerais da coleção."""

    total_books: int
    total_categories: int
    total_stock_quantity: int
    price_stats: PriceStatsSchema
    most_reviewed_book: Optional[ExtremeBookSchema] = None
    rating_distribution: Dict[int, int]
    categories_stats: List[CategoryStatsSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


class UserSchema(BaseModel):
    """Schema para exibir dados de um usuário (sem a senha)."""

    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """Schema para criar um novo usuário."""

    username: str
    password: str


class TokenSchema(BaseModel):
    """Schema para a resposta do token."""

    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    """Schema para os dados contidos dentro do token JWT."""

    username: Optional[str] = None
