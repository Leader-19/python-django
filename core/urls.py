from django.urls import path
from .views import word_to_pdf_view, excel_to_pdf_view

urlpatterns = [
    path('word/', word_to_pdf_view, name='word_to_pdf'),
    path('excel/', excel_to_pdf_view, name='excel_pdf'),
]