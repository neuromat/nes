from django import template
from patient.models import Patient

register = template.Library()


@register.simple_tag(takes_context=True)
def get_name_or_code(context, patient_id) -> str:
    patient: Patient = Patient.objects.get(id=patient_id)

    if context.request.user.has_perm("patient.sensitive_data_patient"):
        return patient.name if patient.name else patient.code
    else:
        return patient.code
