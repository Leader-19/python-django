import os
import tempfile
import pandas as pd
from django.http import HttpResponse
from fpdf import FPDF


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        excel_path = os.path.join(temp_dir, file.name)
        pdf_path = os.path.join(temp_dir, "output.pdf")

        with open(excel_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            df = pd.read_excel(excel_path)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=10)

            # column headers
            col_names = list(df.columns)
            pdf.multi_cell(0, 10, " | ".join(col_names))
            pdf.ln()

            # rows
            for _, row in df.iterrows():
                line = " | ".join(str(x) for x in row.values)
                pdf.multi_cell(0, 8, line)

            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{os.path.splitext(file.name)[0]}.pdf"'
                return response

        except Exception as e:
            return HttpResponse(f"Excel conversion failed: {str(e)}", status=500)