import os
import tempfile
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from django.http import HttpResponse


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, file.name)

        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        df = pd.read_excel(input_path, engine="openpyxl")
        df = df.fillna("")
        df = df.astype(str)

        pdf_path = os.path.join(tmp, "output.pdf")

        # 👉 IMPORTANT: use LANDSCAPE for many columns
        pdf = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A4),
            rightMargin=10,
            leftMargin=10,
            topMargin=10,
            bottomMargin=10
        )

        data = [df.columns.tolist()] + df.values.tolist()

        # 👉 AUTO column width control (KEY FIX)
        col_count = len(df.columns)
        page_width = landscape(A4)[0] - 20
        col_width = page_width / col_count

        table = Table(data, repeatRows=1, colWidths=[col_width] * col_count)

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),

            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])

        table.setStyle(style)

        pdf.build([table])

        with open(pdf_path, "rb") as f:
            return HttpResponse(
                f.read(),
                content_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="excel.pdf"'}
            )