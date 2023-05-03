from django.contrib import admin
from . import models


# admin view
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


# Register your models here.
admin.site.register(models.Patient, PatientAdmin)
