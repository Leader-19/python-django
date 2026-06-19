import os
import tempfile
import pandas as pd

from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape


def convert_excel_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, file.name)

        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Read Excel
        df = pd.read_excel(input_path)

        # Convert to table data
        data = [df.columns.astype(str).tolist()] + df.astype(str).values.tolist()

        pdf_path = os.path.join(tmp, "output.pdf")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A4),   # ✅ IMPORTANT: prevent column breaking
            leftMargin=10,
            rightMargin=10,
            topMargin=10,
            bottomMargin=10
        )

        # ✅ Auto column widths (based on longest text in each column)
        col_widths = []
        for col in df.columns:
            max_len = max(df[col].astype(str).map(len).max(), len(str(col)))
            col_widths.append(max_len * 6)  # adjust multiplier if needed

        table = Table(data, colWidths=col_widths)

        style = TableStyle([
            # ❌ NO HEADER BACKGROUND (removed on purpose)

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("GRID", (0, 0), (-1, -1), 0.3, colors.black),

            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),

            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            # helps reduce weird wrapping behavior
            ("WORDWRAP", (0, 0), (-1, -1), False),
        ])

        table.setStyle(style)

        doc.build([table])

        with open(pdf_path, "rb") as f:
            return HttpResponse(
                f.read(),
                content_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="excel.pdf"'}
            )