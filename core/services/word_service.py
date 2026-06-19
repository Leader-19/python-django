import os
import tempfile
from django.http import HttpResponse
from docx import Document


def convert_word_to_html(file):
    with tempfile.TemporaryDirectory() as temp_dir:

        docx_path = os.path.join(temp_dir, file.name)

        # Save uploaded file
        with open(docx_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            doc = Document(docx_path)

            html = """
            <html>
            <head>
                <meta charset="utf-8">
                <title>Word Conversion</title>
            </head>
            <body>
            """

            for para in doc.paragraphs:
                text = para.text.replace("\n", "<br>")
                html += f"<p>{text}</p>"

            html += "</body></html>"

            return HttpResponse(
                html,
                content_type="text/html",
                headers={
                    "Content-Disposition": f'attachment; filename="{os.path.splitext(file.name)[0]}.html"'
                }
            )

        except Exception as e:
            return HttpResponse(f"Word conversion failed: {str(e)}", status=500)