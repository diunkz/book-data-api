import csv
import argparse
import logging
import os
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.models import Book
from src.core.logging_config import setup_logging


def load_data_from_csv(db: Session, csv_filename: str, clear_table: bool):
    """
    Lê um arquivo CSV e carrega os dados para a tabela de livros no banco de dados.
    """
    logger = logging.getLogger(__name__)

    if not os.path.exists(csv_filename):
        logger.error(f"Arquivo CSV não encontrado em: {csv_filename}")
        return

    if clear_table:
        logger.info("A flag --clear_table foi usada. Limpando a tabela 'books'...")
        db.query(Book).delete()
        db.commit()
        logger.info("Tabela 'books' limpa com sucesso.")

    existing_upcs = {book.upc for book in db.query(Book.upc).all()}
    logger.info(
        f"Encontrados {len(existing_upcs)} livros existentes no banco de dados. "
        "Pulando duplicatas."
    )

    books_to_add = []
    with open(csv_filename, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            upc = row.get("upc")
            if upc in existing_upcs:
                logger.debug(f"Pulando livro com UPC já existente: {upc}")
                continue

            try:
                book_data = {
                    "upc": upc,
                    "book_name": row.get("book_name"),
                    "currency": row.get("currency"),
                    "price": Decimal(row.get("price", "0.00")),
                    "quantity": int(row.get("quantity", 0)),
                    "availability": row.get("availability", "False").lower() == "true",
                    "rating": int(row.get("rating", 0)),
                    "number_of_reviews": int(row.get("number_of_reviews", 0)),
                    "category": row.get("category"),
                    "description": row.get("description"),
                    "image_url": row.get("image_url"),
                    "source_page": int(row.get("source_page", 0)),
                }
                books_to_add.append(Book(**book_data))
                existing_upcs.add(upc)
            except (ValueError, InvalidOperation, TypeError) as e:
                logger.error(
                    f"Erro ao processar linha com UPC {upc}: {e} - Linha ignorada."
                )

    if books_to_add:
        logger.info(
            f"Adicionando {len(books_to_add)} novos livros ao banco de dados..."
        )
        db.add_all(books_to_add)
        db.commit()
        logger.info("Novos livros adicionados com sucesso.")
    else:
        logger.info("Nenhum livro novo para adicionar.")


def main(csv_filename: str, clear_table: bool):
    """Função principal para carregar dados do CSV para o banco."""
    setup_logging()
    logger = logging.getLogger(__name__)

    db = None
    try:
        db = SessionLocal()
        load_data_from_csv(db, csv_filename, clear_table)
    finally:
        if db:
            db.close()
    logger.info("Processo de carregamento finalizado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Carrega dados de livros de um arquivo CSV para o banco de dados."
    )
    parser.add_argument(
        "--csv_name",
        default="books_data_detailed.csv",
        help="Caminho para o arquivo CSV a ser carregado.",
    )
    parser.add_argument(
        "--clear_table",
        action="store_true",
        help="Limpa a tabela de livros no banco de dados antes "
        "de carregar os novos dados.",
    )

    args = parser.parse_args()
    main(args.csv_name, args.clear_table)
