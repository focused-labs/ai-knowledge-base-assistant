import http.client
import json
import os

import requests
from PyPDF2 import PdfReader, PdfWriter
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.readers import NotionPageReader

from config import PROCESSED_DATA_DIRECTORY

load_dotenv()

NOTION_INTEGRATION_TOKEN = os.getenv("NOTION_INTEGRATION_TOKEN")
PDF_DIRECTORY = './raw_notion_pdfs'
WEBSITE_DIRECTORY = './raw_website_scrape'
COMBINED_PDF = os.path.join(PROCESSED_DATA_DIRECTORY, "notion_docs_combined.pdf")
COMBINED_NOTION_TEXT_FILE = os.path.join(PROCESSED_DATA_DIRECTORY, 'combined_notion_import.txt')
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


def get_notion_page_title(page_id):
    try:
        headers = {'Authorization': f'Bearer {NOTION_INTEGRATION_TOKEN}', 'Notion-Version': '2022-06-28'}
        connection = http.client.HTTPSConnection("api.notion.com")

        connection.request("GET", f"/v1/pages/{page_id}/properties/title", headers=headers)
        page_title = json.loads(connection.getresponse().read())

        return page_title['results'][0]['title']['plain_text']
    except Exception as e:
        print(f"Failed to retrieve notion metadata{e} for page id: {page_id}")
        return ""


def read_notion(page_ids: list):
    documents = NotionPageReader(integration_token=NOTION_INTEGRATION_TOKEN).load_data(
        page_ids=page_ids
    )
    documents = [
        doc.to_langchain_format()
        for doc in documents
    ]
    with open(COMBINED_NOTION_TEXT_FILE, 'a') as file:
        for doc in documents:
            metadata = get_notion_page_title(doc.metadata['page_id'])
            content = doc.page_content
            file.write(f"# {metadata}\n{content}\n\n")

    print("Documents processed and appended to combined_notion_import.txt")


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
