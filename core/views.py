from django.shortcuts import render
from django.http import HttpResponse

from .services.word_service import convert_word_to_html
from .services.excel_service import convert_excel_to_html


def word_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_word.html", {
                "error": "Please upload a Word file"
            })

        try:
            return convert_word_to_html(file)
        except Exception as e:
            return HttpResponse(f"Word Error: {str(e)}", status=500)

    return render(request, "forms/upload_word.html")


def excel_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_excel.html", {
                "error": "Please upload an Excel file"
            })

        try:
            return convert_excel_to_html(file)
        except Exception as e:
            return HttpResponse(f"Excel Error: {str(e)}", status=500)

    return render(request, "forms/upload_excel.html")