import fitz
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()