import os

import requests
from PyPDF2 import PdfReader, PdfWriter
from bs4 import BeautifulSoup

from config import PROCESSED_DATA_DIRECTORY

PDF_DIRECTORY = './raw_notion_pdfs'
WEBSITE_DIRECTORY = './raw_website_scrape'
COMBINED_PDF = os.path.join(PROCESSED_DATA_DIRECTORY, "notion_docs_combined.pdf")
MAX_FILE_SIZE = 512
MAX_NUM_FILES = 24


def combine_pdfs(input_path, output_path):
    writer = PdfWriter()
    for pdf in os.listdir(input_path):
        if pdf.endswith('.pdf'):
            reader = PdfReader(os.path.join(input_path, pdf))
            for page in reader.pages:
                writer.add_page(page)
    with open(output_path, "wb") as out:
        writer.write(out)


def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)


def parse_and_combine_pdfs():
    combine_pdfs(PDF_DIRECTORY, COMBINED_PDF)

    if get_file_size(COMBINED_PDF) > MAX_FILE_SIZE:
        print("ERROR - Combination of all notion pdfs is too large of a file. Please parse into smaller pdfs")


def save_website_scrape(urls: list):
    if not os.path.exists(WEBSITE_DIRECTORY):
        os.makedirs(WEBSITE_DIRECTORY)

    combined_text = ''
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            filename_html = os.path.join(WEBSITE_DIRECTORY, url.split('//')[1].replace('/', '_') + '.html')
            with open(filename_html, 'w', encoding='utf-8') as file:
                file.write(str(soup))

            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ', strip=True)
            combined_text += text + '\n\n'
        else:
            print(f"Failed to retrieve {url}")

    filename_txt = os.path.join(PROCESSED_DATA_DIRECTORY, 'website_combined_text.txt')
    with open(filename_txt, 'w', encoding='utf-8') as file:
        file.write(combined_text)
