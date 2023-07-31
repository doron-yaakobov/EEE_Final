from django.contrib import admin
from .models import Patient, VitalSign


# admin view for Patient model
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    date_hierarchy = "enter_date"
    search_fields = (
        "id",
        "enter_date",
        "patient_id",
        "last_name",
        "first_name",
        "food_cosher",
        "food_diary_restricted",
        "birth_date",
        "description",
        "leave_date",
    )
    list_display = search_fields


# admin view for VitalSign model
@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ("patient", "timestamp", "heart_rate", "spo2")
    date_hierarchy = "timestamp"




# Note: Add more fields to list_display if you want to display more information in the list view of VitalSigns.
