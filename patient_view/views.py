from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient, VitalSign
from .forms import VitalSignForm


# Create your views here.
def patients_list(request):
    qs = Patient.objects.all()
    return render(
        request,
        "patient_view/patient_list.html",
        {
            "patients": qs,
        }
    )


def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital_signs = VitalSign.objects.filter(patient=patient)

    if request.method == 'POST':
        form = VitalSignForm(request.POST)
        if form.is_valid():
            vital_sign = form.save(commit=False)
            vital_sign.patient = patient
            vital_sign.save()
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = VitalSignForm()

    context = {
        'patient': patient,
        'vital_signs': vital_signs,
        'form': form,
    }
    return render(request, 'patient_view/patient_detail.html', context)
