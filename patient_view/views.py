from django.shortcuts import render

from patient_view.models import Patient


# Create your views here.
def patients_list(request):
    qs = Patient.objects.all()
    return render(request, "patient_view/patient_list.html",
                  {
                      "patients": qs,
                  })
