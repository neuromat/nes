from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def qdc_permission_denied_view(request, template_name="admin/qdc_403.html"):

    context = {}

    return render(request, template_name, context, status=403)


@login_required
def contact(request):
    return render(request, 'quiz/contato.html')