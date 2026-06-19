import os
import tempfile
import pandas as pd
from django.http import HttpResponse


def convert_excel_to_html(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        excel_path = os.path.join(temp_dir, file.name)

        # Save uploaded file
        with open(excel_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            df = pd.read_excel(excel_path)

            html_table = df.to_html(index=False)

            html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>Excel Conversion</title>
                <style>
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                </style>
            </head>
            <body>
            {html_table}
            </body>
            </html>
            """

            return HttpResponse(
                html,
                content_type="text/html",
                headers={
                    "Content-Disposition": f'attachment; filename="{os.path.splitext(file.name)[0]}.html"'
                }
            )

        except Exception as e:
            return HttpResponse(f"Excel conversion failed: {str(e)}", status=500)