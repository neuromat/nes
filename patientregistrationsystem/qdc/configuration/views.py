from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import UsefulLink


@login_required
def useful_links_view(
    request: HttpRequest, template_name: str = "configuration/links_list.html"
) -> HttpResponse:
    useful_links = UsefulLink.objects.all()

    context = {
        "useful_links": useful_links,
    }

    return render(request, template_name, context)
