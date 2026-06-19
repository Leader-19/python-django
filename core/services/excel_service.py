import os
import tempfile
import subprocess
from django.http import HttpResponse


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, file.name)

        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            subprocess.run([
                "soffice",   # or "libreoffice"
                "--headless",
                "--nologo",
                "--nolockcheck",
                "--convert-to", "pdf",
                input_path,
                "--outdir", tmp
            ], check=True)

            pdf_path = os.path.join(
                tmp,
                os.path.splitext(file.name)[0] + ".pdf"
            )

            with open(pdf_path, "rb") as f:
                return HttpResponse(
                    f.read(),
                    content_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="excel.pdf"'}
                )

        except Exception as e:
            return HttpResponse(f"Conversion failed: {str(e)}", status=500)