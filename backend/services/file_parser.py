import os
from PyPDF2 import PdfReader
from docx import Document


# ================= PDF =================

def extract_pdf_text(path):

    text = ""

    reader = PdfReader(path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ================= DOCX =================

def extract_docx_text(path):

    doc = Document(path)

    text = ""

    for para in doc.paragraphs:

        text += para.text + "\n"

    return text


# ================= MAIN =================

def extract_resume_text(path):

    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_text(path)

    elif ext == ".docx":
        return extract_docx_text(path)

    else:
        raise Exception("Unsupported file type")