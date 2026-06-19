import os
import tempfile
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse


def convert_word_to_pdf(file):
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, file.name)

        with open(input_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        doc = Document(input_path)

        pdf_path = os.path.join(tmp, "output.pdf")
        pdf = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()

        content = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                content.append(Paragraph(text, styles["Normal"]))
                content.append(Spacer(1, 10))

        pdf.build(content)

        with open(pdf_path, "rb") as f:
            return HttpResponse(
                f.read(),
                content_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="word.pdf"'}
            )