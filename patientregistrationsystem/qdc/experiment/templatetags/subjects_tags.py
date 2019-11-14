from django import template
from patient.models import Patient

register = template.Library()


@register.simple_tag(takes_context=True)
def get_name_or_code(context, patient_id):

    patient = Patient.objects.get(id=patient_id)

    if context.request.user.has_perm('patient.sensitive_data_patient'):
        if patient.name:
            return patient.name
        else:
            return patient.code
    else:
        return patient.code


@register.filter(name='add_attr')
def add_attr(field, attr):
    attrs = {'disabled': attr}
    return field.as_widget(attrs=attrs)
