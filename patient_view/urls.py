from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from . import views




# URLS/ URLCONF:
urlpatterns = [
    path('', views.patients_list),
]
