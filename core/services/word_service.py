import os
import tempfile
from django.http import HttpResponse
from docx import Document
from weasyprint import HTML


def convert_word_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        docx_path = os.path.join(temp_dir, file.name)
        pdf_path = os.path.join(temp_dir, "output.pdf")

        # Save uploaded file
        with open(docx_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Read DOCX
            doc = Document(docx_path)

            html_content = "<html><body>"

            for para in doc.paragraphs:
                html_content += f"<p>{para.text}</p>"

            html_content += "</body></html>"

            # Convert HTML → PDF
            HTML(string=html_content).write_pdf(pdf_path)

            with open(pdf_path, "rb") as pdf:
                response = HttpResponse(pdf.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{os.path.splitext(file.name)[0]}.pdf"'
                return response

        except Exception as e:
            return HttpResponse(f"Word conversion failed: {str(e)}", status=500)