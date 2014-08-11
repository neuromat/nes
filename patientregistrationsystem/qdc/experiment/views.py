from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from experiment.models import Experiment


@login_required
def experiment_list(request, template_name="experiment/experiment_list.html"):

    experiments = Experiment.objects.order_by('title')

    context = {"experiments": experiments}
    return render(request, template_name, context)
