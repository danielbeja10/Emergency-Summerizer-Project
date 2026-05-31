import pypdf
import re


def extract_from_pdf(file_path: str) -> str:
    reader = pypdf.PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return clean_text("\n".join(pages))


def extract_from_text(raw: str) -> str:
    return clean_text(raw)


def clean_text(raw: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', raw)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()
