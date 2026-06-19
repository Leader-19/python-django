import os
import tempfile
from django.http import HttpResponse
from docx import Document
from fpdf import FPDF


def convert_word_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        docx_path = os.path.join(temp_dir, file.name)
        pdf_path = os.path.join(temp_dir, "output.pdf")

        # Save file
        with open(docx_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            doc = Document(docx_path)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    pdf.multi_cell(0, 10, text)

            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{os.path.splitext(file.name)[0]}.pdf"'
                return response

        except Exception as e:
            return HttpResponse(f"Word conversion failed: {str(e)}", status=500)