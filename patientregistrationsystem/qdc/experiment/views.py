from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from experiment.models import Experiment, Questionnaire
from experiment.forms import ExperimentForm

from quiz.abc_search_engine import Questionnaires

@login_required
def experiment_list(request, template_name="experiment/experiment_list.html"):

    experiments = Experiment.objects.order_by('title')

    context = {"experiments": experiments}

    return render(request, template_name, context)


@login_required
def experiment_create(request, template_name="experiment/experiment_register.html"):

    experiment_form = ExperimentForm(request.POST or None)
    questionnaires_list = Questionnaires().find_all_active_questionnaires()

    if request.method == "POST":

        if request.POST['action'] == "save":

            if experiment_form.is_valid():

                experiment_added = experiment_form.save()

                if 'chosen_questionnaires' in request.POST:

                    for survey_id in request.POST.getlist('chosen_questionnaires'):

                        questionnaire = Questionnaire()

                        try:
                            questionnaire = Questionnaire.objects.get(survey_id=survey_id)
                        except questionnaire.DoesNotExist:
                            Questionnaire(survey_id=survey_id).save()
                            questionnaire = Questionnaire.objects.get(survey_id=survey_id)

                        experiment_added.questionnaires.add(questionnaire)

                messages.success(request, 'Experimento criado com sucesso.')

                redirect_url = reverse("experiment_list")
                # redirect_url = reverse("experiment_edit", args=(experiment_added))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": True,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


@login_required
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):

    experiment = get_object_or_404(Experiment, pk=experiment_id)
    questionnaires_list = []

    if experiment:
        questionnaires_list = Questionnaires().find_all_active_questionnaires()

        experiment_form = ExperimentForm(request.POST or None, instance=experiment)

        if request.method == "POST":

            if request.POST['action'] == "save":

                if experiment_form.is_valid():

                    experiment_form.save()

                    redirect_url = reverse("experiment_edit", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": False,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


