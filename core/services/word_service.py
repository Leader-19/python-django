import os
import tempfile

from django.http import HttpResponse

# New import
from docx2pdf import convert


def convert_word_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        docx_path = os.path.join(temp_dir, file.name)

        # Save uploaded file
        with open(docx_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        pdf_path = os.path.join(
            temp_dir,
            os.path.splitext(file.name)[0] + ".pdf"
        )

        # Convert DOCX to PDF using Microsoft Word (native on Windows)
        convert(docx_path, pdf_path)

        # Return PDF
        with open(pdf_path, "rb") as pdf:
            response = HttpResponse(
                pdf.read(),
                content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(pdf_path)}"'
            )
            return response