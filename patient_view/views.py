from django.shortcuts import render


# Create your views here.
def patients_list(request):
    return render(request, "patient_view/patient_list.html")
