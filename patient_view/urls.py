from django.contrib import admin
from django.urls import  path
from . import views

# URLS/ URLCONF:
urlpatterns = [
    path('', views.patients_list, name='patients_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),

]
