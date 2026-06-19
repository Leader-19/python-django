import os
import tempfile
import subprocess
from django.http import HttpResponse


def convert_word_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        docx_path = os.path.join(temp_dir, file.name)

        # Save uploaded file
        with open(docx_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Convert DOCX → PDF (LibreOffice)
            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                docx_path,
                "--outdir",
                temp_dir
            ], check=True, timeout=120)

            pdf_name = os.path.splitext(file.name)[0] + ".pdf"
            pdf_path = os.path.join(temp_dir, pdf_name)

            with open(pdf_path, "rb") as pdf:
                response = HttpResponse(pdf.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{pdf_name}"'
                return response

        except Exception as e:
            return HttpResponse(f"Word conversion failed: {str(e)}", status=500)