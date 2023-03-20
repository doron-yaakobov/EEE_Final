from django.db import models


class Patient(models.Model):
    first_name = models.CharField(max_length=46)
    last_name = models.CharField(max_length=46)
    full_name = models.CharField(max_length=92)
    id = models.DecimalField(max_digits=9, decimal_places=0, primary_key=True)
    enter_date = models.DateField()
    leave_date = models.DateField()
