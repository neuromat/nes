from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from export.views import patient_fields
from patient.models import Patient


@login_required
def send_to_plugin(request, template_name="plugin/send_to_plugin.html"):
    participants = Patient.objects.filter(removed=False)

    context = {
        'participants': participants,
        'patient_fields': patient_fields
    }

    return render(request, template_name, context)
