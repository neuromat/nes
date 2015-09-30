from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import activate, LANGUAGE_SESSION_KEY


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
def language_change(request, language_code):

    activate(language_code)
    request.session[LANGUAGE_SESSION_KEY] = language_code

    return HttpResponseRedirect(request.GET['next'])
