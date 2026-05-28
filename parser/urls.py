from django.urls import path
from .views import upload_and_export

urlpatterns = [
    path('', upload_and_export, name='home'),
    path('txt/', upload_and_export, name='txt'),
]