from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text

# Using the Base in database.py
from .database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    upc = Column(String(50), unique=True, nullable=False, index=True)
    book_name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default="GBP")
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    availability = Column(Boolean, default=True)
    rating = Column(Integer)
    number_of_reviews = Column(Integer, default=0)
    category = Column(String(100))
    description = Column(Text)
    image_url = Column(String(255))
    source_page = Column(Integer)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
