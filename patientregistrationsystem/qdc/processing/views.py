import tempfile
from typing import Any

from git import Object

import experiment
import mne
from click import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from experiment.models import Experiment, Group, ResearchProject, SubjectOfGroup
from patient.models import Patient

from .forms import UploadFileForm


def handle_uploaded_file(file: File) -> str:
    with tempfile.NamedTemporaryFile("wb+", delete=False, suffix=".edf") as f:
        for chunk in file.chunks():
            f.write(chunk)
        return f.name


# @login_required
# def index(
#     request: HttpRequest, template_name: str = "processing/file_selection.html"
# ) -> HttpResponse:
#     df = None

#     experiment_list = get_avaliable_projects()

#     if request.method == "POST":
#         form = UploadFileForm(request.POST or None, request.FILES)
#         if form.is_valid():
#             file = request.FILES.get("file")
#             file_name = handle_uploaded_file(file)

#             mne_file = mne.io.read_raw_edf(file_name)
#             df = mne_file.describe()
#             print(mne_file)

#     else:
#         form = UploadFileForm()

#     context: dict[str, Any] = {"form": form, "df": df, "experiment_list": experiment_list,}

#     return render(request, template_name, context)


@login_required
def index(
    request: HttpRequest, template_name: str = "processing/file_selection.html"
) -> HttpResponse:
    research_projects = ResearchProject.objects.order_by("start_date")
    experiment_list = get_avaliable_projects()
    group_list = None
    study_list = []
    study_selected = []

    if request.method == "POST":
        participants_list = Patient.objects.filter(removed=False)
        if request.POST["action"] == "next-step-participants":
            subject_list = []
            groups_selected = request.POST.getlist("group_selected")
            request.session["group_selected_list"] = groups_selected
            if groups_selected:
                for group_selected_id in groups_selected:
                    group_selected = Group.objects.filter(pk=group_selected_id)
                    subject_of_groups = SubjectOfGroup.objects.filter(
                        group__in=group_selected
                    )
                    for subject_of_group in subject_of_groups:
                        patient = subject_of_group.subject.patient
                        if patient.id not in subject_list:
                            subject_list.append(patient.id)

                participants_list = participants_list.filter(pk__in=subject_list)
                request.session["filtered_participant_data"] = [
                    item.id for item in participants_list
                ]

                redirect_url = reverse("select_files", args=())
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, _("No group(s) selected!"))

    context: dict[str, Any] = {
        "research_projects": research_projects,
        "study_list": study_list,
        "study_selected": study_selected,
        "experiment_list": experiment_list,
        "group_list": group_list,
    }

    return render(request, template_name, context)


@login_required
def select_files(
    request: HttpRequest, template_name: str = "processing/file_selection.html"
) -> HttpResponse:
    return Object()


def get_avaliable_projects() -> list[Experiment]:
    avaliable_projects: list[Experiment] = []

    avaliable_projects = list(Experiment.objects.all())

    return avaliable_projects
