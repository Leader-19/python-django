from django.shortcuts import render
from .services.word_service import convert_word_to_pdf
from .services.excel_service import convert_excel_to_pdf


def word_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_word.html", {
                "error": "Please upload a Word file"
            })

        return convert_word_to_pdf(file)

    return render(request, "forms/upload_word.html")


def excel_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_excel.html", {
                "error": "Please upload an Excel file"
            })

        return convert_excel_to_pdf(file)

    return render(request, "forms/upload_excel.html")