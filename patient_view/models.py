from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class Patient(models.Model):
    default_birth_date = datetime.now() - timedelta(days=(365 * 18))

    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=46)
    last_name = models.CharField(max_length=46)
    full_name = models.CharField(max_length=93,
                                 help_text="Please do not edit or delete this. Your changes here will not be saved.",
                                 editable=False)
    patient_id = models.DecimalField(max_digits=9, decimal_places=0)
    enter_date = models.DateTimeField(default=timezone.now)
    leave_date = models.DateTimeField(default=None, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    birth_date = models.DateField(default=default_birth_date, blank=True)
    food_cosher = models.BooleanField(default=None, null=True, blank=True)
    food_diary_restricted = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('patient_id',)


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    heart_rate = models.PositiveIntegerField()
    spo2 = models.PositiveIntegerField()

    # Add more fields here for blood pressure and temperature if you want to record them
    # Note: We will use dummy values for blood pressure and temperature

    def __str__(self):
        return f"{self.patient} - {self.timestamp}"
