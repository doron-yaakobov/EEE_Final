"""EEE_Final URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path

# VIEW FUNCTIONS
# def home(request):
#     # assert False, "<Assertion Message>"
#     return HttpResponse(f"Hello world!!!")


# def patient_id(request, id: int):
#     return HttpResponse(f"<b>Patient ID is:</b> {id}")
#     # return JsonResponse()


# URLS/ URLCONF:
urlpatterns = [
    # path('', home),

    # path('patients/<int:id>/', patient_id),

    # path('patients/', patient_id, {
    #     "id": 209495381
    # }),

    path('admin/', admin.site.urls),
    path("", include("patient_view.urls"))
]
