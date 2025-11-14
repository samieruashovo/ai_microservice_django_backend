from django.contrib import admin
from django.urls import path

from api_gateway.core.views import generate_response, get_response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate/', generate_response),
    path('result/<uuid:request_id>/', get_response),
]
