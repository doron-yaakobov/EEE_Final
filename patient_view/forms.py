
from django import forms
from .models import VitalSign

class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = ['heart_rate', 'spo2']
