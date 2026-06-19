import os
import tempfile
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, file.name)

        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        df = pd.read_excel(input_path)

        pdf_path = os.path.join(tmp, "output.pdf")
        pdf = SimpleDocTemplate(pdf_path)

        data = [df.columns.tolist()] + df.values.tolist()

        table = Table(data, repeatRows=1)

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ])

        table.setStyle(style)

        pdf.build([table])

        with open(pdf_path, "rb") as f:
            return HttpResponse(
                f.read(),
                content_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="excel.pdf"'}
            )