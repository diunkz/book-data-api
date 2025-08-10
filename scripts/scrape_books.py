import csv
import httpx
import argparse
import re
import os
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Iterable
from decimal import Decimal, InvalidOperation

from src.core.logging_config import setup_logging

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = f"{BASE_URL}catalogue/"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_total_pages(client: httpx.Client) -> int:
    """
    Raspa a primeira página do catálogo para descobrir o número total de páginas.
    Retorna 50 como um valor padrão em caso de erro.
    """
    logger = logging.getLogger(__name__)
    url = f"{CATALOGUE_URL}page-1.html"
    try:
        response = client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        # Encontra o texto "Page 1 of 50"
        pager_text = soup.find("li", class_="current").text.strip()
        # Usa regex para extrair o último número
        match = re.search(r"Page \d+ of (\d+)", pager_text)
        if match:
            total = int(match.group(1))
            logger.info(f"Total de páginas detectado no site: {total}")
            return total
    except Exception as e:
        logger.warning(
            f"Não foi possível detectar o total de páginas dinamicamente. "
            f"Usando 50 como padrão. Erro: {e}"
        )
    return 50


def scrape_book_details(
    book_url: str, page_number: int, client: httpx.Client
) -> Optional[Dict]:
    """
    Entra na página de um livro específico e extrai todos os detalhes.
    """
    try:
        response = client.get(book_url, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        product_table = soup.find("table", class_="table-striped")
        table_rows = product_table.find_all("tr")
        product_info = {row.find("th").text: row.find("td").text for row in table_rows}

        availability_text = product_info.get("Availability", "")
        quantity_match = re.search(r"\((\d+) available\)", availability_text)
        quantity = int(quantity_match.group(1)) if quantity_match else 0

        description_tag = soup.find("div", id="product_description")
        description = (
            description_tag.find_next_sibling("p").text if description_tag else ""
        )

        category = soup.find("ul", class_="breadcrumb").find_all("li")[2].text.strip()

        rating_p = soup.find("p", class_="star-rating")
        rating_class = rating_p["class"][1]
        rating = RATING_MAP.get(rating_class, 0)

        image_tag = soup.find("div", class_="item active").find("img")
        image_url = BASE_URL + image_tag["src"].replace("../../", "")

        price_text = soup.find("p", class_="price_color").text

        currency = "N/A"
        if "£" in price_text:
            currency = "GBP"
        elif "$" in price_text:
            currency = "USD"
        elif "€" in price_text:
            currency = "EUR"
        elif "R$" in price_text:
            currency = "BRL"

        try:
            price_value = Decimal(re.sub(r"[^0-9.]", "", price_text))
        except (InvalidOperation, TypeError):
            price_value = Decimal("0.00")

        return {
            "upc": product_info.get("UPC"),
            "book_name": soup.find("h1").text,
            "currency": currency,
            "price": price_value,
            "quantity": quantity,
            "availability": quantity > 0,
            "rating": rating,
            "number_of_reviews": int(product_info.get("Number of reviews", 0)),
            "category": category,
            "description": description,
            "image_url": image_url,
            "source_page": page_number,
        }
    except httpx.HTTPStatusError as e:
        logging.error(f"Erro de status HTTP ao acessar {book_url}: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado ao processar o livro {book_url}: {e}")
    return None


def get_book_links_from_page(
    page_number: int, client: httpx.Client
) -> tuple[List[str], bool]:
    """
    Raspa uma página de catálogo para obter os links de todos os livros.
    """
    url = f"{CATALOGUE_URL}page-{page_number}.html"
    try:
        response = client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        book_links = [CATALOGUE_URL + a["href"] for a in soup.select("h3 > a")]
        has_next_page = soup.find("li", class_="next") is not None
        return book_links, has_next_page
    except httpx.HTTPStatusError:
        logging.warning(
            f"Não foi possível acessar a página de catálogo {page_number}. Pode ser "
            f"o fim do site."
        )
        return [], False


def load_scrape_state(csv_filename: str) -> tuple[set, int]:
    """Lê um CSV existente para carregar o estado anterior do scraping."""
    logger = logging.getLogger(__name__)
    logger.info(f"Modo 'append' ativado. Lendo dados de '{csv_filename}'...")

    scraped_upcs = set()
    last_scraped_page = 0

    with open(csv_filename, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("upc"):
                scraped_upcs.add(row["upc"])
            if row.get("source_page"):
                last_scraped_page = max(last_scraped_page, int(row["source_page"]))

    logger.info(
        f"Encontrados {len(scraped_upcs)} livros. Última página com dados: "
        f"{last_scraped_page}. Continuando..."
    )
    return scraped_upcs, last_scraped_page


def determine_page_iterator(
    pages_to_scrape: str,
    append_mode: bool,
    last_scraped_page: int,
    total_pages: int,
) -> Optional[Iterable[int]]:
    """Determina o range de páginas a serem raspadas com base nos argumentos."""
    logger = logging.getLogger(__name__)

    if pages_to_scrape.lower() == "all":
        start_page = 1
        if append_mode and last_scraped_page > 0:
            start_page = last_scraped_page
        return range(start_page, total_pages + 1)
    else:
        try:
            return [int(p.strip()) for p in pages_to_scrape.split(",")]
        except ValueError:
            logger.error(
                f"Formato de página inválido: '{pages_to_scrape}'. Use 'all' ou "
                f"números separados por vírgula."
            )
            return None


def run_scraper(
    writer: csv.DictWriter,
    client: httpx.Client,
    page_iterator: Iterable[int],
    scraped_upcs: set,
):
    """Executa o loop principal de scraping."""
    logger = logging.getLogger(__name__)

    for page_num in page_iterator:
        logger.debug(f"Processando página de catálogo {page_num}...")
        links, has_next = get_book_links_from_page(page_num, client)

        if not links and isinstance(page_iterator, range) and not has_next:
            logger.info("Chegou ao fim do site.")
            break

        for book_url in links:
            details = scrape_book_details(book_url, page_num, client)
            if details:
                if details["upc"] not in scraped_upcs:
                    writer.writerow(details)
                    scraped_upcs.add(details["upc"])
                    logger.info(
                        f"Página {page_num}: Capturado '"
                        f"{details['book_name'][:40]}...'"
                    )
                else:
                    logger.debug(
                        f"Página {page_num}: Pulando (já existe) '"
                        f"{details['book_name'][:40]}...'"
                    )


def main(pages_to_scrape: str, append_mode: bool, csv_filename: str):
    """Função principal que orquestra o processo de scraping."""
    setup_logging()
    logger = logging.getLogger(__name__)

    scraped_upcs, last_scraped_page = set(), 0
    file_exists = os.path.exists(csv_filename)

    if append_mode and file_exists:
        scraped_upcs, last_scraped_page = load_scrape_state(csv_filename)

    headers = [
        "upc",
        "book_name",
        "currency",
        "price",
        "quantity",
        "availability",
        "rating",
        "number_of_reviews",
        "category",
        "description",
        "image_url",
        "source_page",
    ]
    file_mode = "a" if append_mode and file_exists else "w"

    with (
        httpx.Client(timeout=20.0, follow_redirects=True) as client,
        open(csv_filename, file_mode, newline="", encoding="utf-8") as csvfile,
    ):
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if file_mode == "w":
            writer.writeheader()

        total_pages = 50
        if pages_to_scrape.lower() == "all":
            total_pages = get_total_pages(client)

        page_iterator = determine_page_iterator(
            pages_to_scrape, append_mode, last_scraped_page, total_pages
        )
        if page_iterator is None:
            return

        if isinstance(page_iterator, range):
            pages = f"todas a partir de {page_iterator.start}"
        else:
            pages = str(page_iterator)
        logger.info(f"Iniciando scraping para as páginas: {pages}")

        run_scraper(writer, client, page_iterator, scraped_upcs)

    logger.info(f"Scraping concluído. Dados salvos em '{csv_filename}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Web scraper para o site books.toscrape.com",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--pages",
        default="all",
        help='Número(s) de página para raspar (ex: 5 ou 3,5,7 ou [4, 5, 6]) ou "all".',
    )
    parser.add_argument(
        "--csv_name",
        default="books_data_detailed.csv",
        help="Nome do arquivo CSV de saída.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Ativa o modo de continuação (append) para um CSV existente.",
    )

    args = parser.parse_args()
    main(args.pages, args.append, args.csv_name)
