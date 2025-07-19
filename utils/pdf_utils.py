# utils/pdf_utils.py

from fpdf import FPDF
import os

def generate_pdf(title: str, content: str, output_path: str = "output/book.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    
    pdf.set_title(title)
    pdf.multi_cell(0, 10, f"{title}\n\n{content}")
    
    pdf.output(output_path)
    return output_path
