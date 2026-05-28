from django.shortcuts import render
from django.http import HttpResponse
from .services.word_service import convert_word_to_pdf

from django.shortcuts import render
from .services.excel_service import convert_excel_to_pdf


def word_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        pdf = convert_word_to_pdf(file)

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="word.pdf"'

        return response

    return render(request, "forms/upload_word.html")


def excel_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_excel.html", {
                "error": "Please upload a file"
            })

        return convert_excel_to_pdf(file)

    return render(request, "forms/upload_excel.html")
