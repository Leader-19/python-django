import os
import tempfile
import pandas as pd
from django.http import HttpResponse
from weasyprint import HTML


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        excel_path = os.path.join(temp_dir, file.name)
        pdf_path = os.path.join(temp_dir, "output.pdf")

        # Save uploaded file
        with open(excel_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Read Excel
            df = pd.read_excel(excel_path)

            # Convert to HTML table
            html_table = df.to_html(index=False)

            html_content = f"""
            <html>
            <body>
            {html_table}
            </body>
            </html>
            """

            # Convert HTML → PDF
            HTML(string=html_content).write_pdf(pdf_path)

            with open(pdf_path, "rb") as pdf:
                response = HttpResponse(pdf.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{os.path.splitext(file.name)[0]}.pdf"'
                return response

        except Exception as e:
            return HttpResponse(f"Excel conversion failed: {str(e)}", status=500)