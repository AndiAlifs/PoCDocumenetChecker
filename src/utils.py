
from PyPDF2 import PdfReader

def extract_pdf(file):
    reader = PdfReader(file)
    return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
