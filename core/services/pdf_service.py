from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse

def dataframe_to_pdf(df):
    html = df.to_html(index=False)

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="output.pdf"'

    return response