from django.shortcuts import render
from django.http import HttpResponse
import traceback

from .services.word_service import convert_word_to_html
from .services.excel_service import convert_excel_to_html


# ✅ ADD THIS FIRST (VERY IMPORTANT)
def safe_view(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return HttpResponse(
                f"ERROR:\n{str(e)}\n\nTRACE:\n{traceback.format_exc()}",
                status=500
            )
    return wrapper


# ✅ WORD VIEW
@safe_view
def word_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_word.html", {
                "error": "Please upload a Word file"
            })

        return convert_word_to_html(file)

    return render(request, "forms/upload_word.html")


# ✅ EXCEL VIEW
@safe_view
def excel_to_pdf_view(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return render(request, "forms/upload_excel.html", {
                "error": "Please upload an Excel file"
            })

        return convert_excel_to_html(file)

    return render(request, "forms/upload_excel.html")