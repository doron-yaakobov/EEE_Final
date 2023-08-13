from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient, VitalSign
import plotly.graph_objs as go
import plotly.express as px


def patients_list(request):
    # Get the search filter option and search query from the request parameters
    filter_option = request.GET.get('filter_option', '')
    search_query = request.GET.get('search_query', '')

    patients = Patient.objects.all()


    context = {'patients': patients}
    return render(request, 'patient_view/patient_list.html', context)


def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    vital_signs = VitalSign.objects.filter(patient=patient).order_by('-timestamp')

    # Create Plot for Heart Rate
    heart_rate_data = go.Scatter(x=[vs.timestamp for vs in vital_signs],
                                 y=[vs.heart_rate for vs in vital_signs],
                                 mode='lines+markers',
                                 name='Heart Rate')

    # Create Plot for SPO2
    spo2_data = go.Scatter(x=[vs.timestamp for vs in vital_signs],
                           y=[vs.spo2 for vs in vital_signs],
                           mode='lines+markers',
                           name='SPO2')

    # Layout for the plots
    layout = go.Layout(title=f'Vital Signs for {patient.full_name}',
                       xaxis=dict(title='Timestamp'),
                       yaxis=dict(title='Value'))

    heart_rate_plot = go.Figure(data=[heart_rate_data], layout=layout)
    spo2_plot = go.Figure(data=[spo2_data], layout=layout)

    # Convert the plots to JSON to be rendered in the template
    heart_rate_plot_json = heart_rate_plot.to_json()
    spo2_plot_json = spo2_plot.to_json()

    if request.method == 'POST':
        heart_rate = request.POST.get('heart_rate')
        spo2 = request.POST.get('spo2')
        VitalSign.objects.create(patient=patient, heart_rate=heart_rate, spo2=spo2)
        return redirect('patient_detail', patient_id=patient_id)

    return render(request, 'patient_view/patient_detail.html', {
        'patient': patient,
        'vital_signs': vital_signs,
        'heart_rate_plot_json': heart_rate_plot_json,
        'spo2_plot_json': spo2_plot_json
    })
