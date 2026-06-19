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
                "soffice",
                "--headless",
                "--nologo",
                "--nolockcheck",
                "--convert-to",
                "pdf",
                input_path,
                "--outdir",
                tmp
            ], capture_output=True, text=True, check=True)

            pdf_file = os.path.splitext(file.name)[0] + ".pdf"
            pdf_path = os.path.join(tmp, pdf_file)

            with open(pdf_path, "rb") as pdf:
                return HttpResponse(
                    pdf.read(),
                    content_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{pdf_file}"'
                    }
                )

        except FileNotFoundError:
            return HttpResponse(
                "LibreOffice not installed (soffice not found)",
                status=500
            )

        except subprocess.CalledProcessError as e:
            return HttpResponse(
                f"Conversion failed: {e.stderr}",
                status=500
            )