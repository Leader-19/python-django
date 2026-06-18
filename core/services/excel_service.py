import os
import subprocess
from django.http import HttpResponse


def convert_excel_to_pdf(file):
    os.makedirs("media", exist_ok=True)

    input_path = os.path.abspath(f"media/{file.name}")
    output_dir = os.path.abspath("media")

    # save uploaded file
    with open(input_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # convert using LibreOffice
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        input_path
    ], check=True)

    output_path = input_path.rsplit(".", 1)[0] + ".pdf"

    with open(output_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="output.pdf"'

    return response