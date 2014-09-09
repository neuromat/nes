__author__ = 'mori'
from django.shortcuts import render


def qdc_permission_denied_view(request, template_name="admin/qdc_403.html"):

    context = {}

    return render(request, template_name, context, status=403)