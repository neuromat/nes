from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import activate

def qdc_permission_denied_view(request, template_name="admin/qdc_403.html"):

    context = {}

    return render(request, template_name, context, status=403)


@login_required
def contact(request):
    context = {
        'contact_email': settings.CONTACT_EMAIL,
        'contact_institution': settings.CONTACT_INSTITUTION,
        'contact_url': settings.CONTACT_URL,
        'logo_institution': settings.LOGO_INSTITUTION,
    }

    return render(request, 'quiz/contato.html', context)

@login_required
#@permission_required('patient.add_medicalrecorddata')
def language_change(request, language_code, template_name='language/change_lang.html'):
    activate(language_code)
    request.LANGUAGE_CODE = language_code
    return render(request, template_name,
                  {})