from fpdf import FPDF
import os

def generate_pdf(content: str, title: str, output_path: str):
    pdf = FPDF()
    pdf.add_page()

    # Path to DejaVuSans.ttf inside the utils/fonts directory
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    font_path = os.path.join(font_dir, "DejaVuSans.ttf")

    # Add and set Unicode-compatible font
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 14)

    # Set PDF title
    pdf.set_title(title)

    # Write content line by line
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line.strip())

    # Output PDF
    pdf.output(output_path)
