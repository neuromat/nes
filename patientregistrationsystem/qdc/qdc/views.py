from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def qdc_permission_denied_view(request, template_name="admin/qdc_403.html"):

    context = {}

    return render(request, template_name, context, status=403)


@login_required
def contact(request):
    context = {
        'contact_email': settings.CONTACT_EMAIL,
        'contact_institution': settings.CONTACT_INSTITUTION,
        'contact_url': settings.CONTACT_URL,
    }

    return render(request, 'quiz/contato.html', context)