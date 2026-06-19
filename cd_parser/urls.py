from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('parser.urls')),   #  required
    path('core/', include('core.urls')),
]

# from django.contrib import admin
# from django.urls import path, include
# from django.http import HttpResponse

# def home(request):
#     return HttpResponse("Server is running ✅")

# urlpatterns = [
#     path('', home),   # ✅ IMPORTANT: prevents 500 at /
#     path('admin/', admin.site.urls),
#     path('core/', include('core.urls')),
# ]