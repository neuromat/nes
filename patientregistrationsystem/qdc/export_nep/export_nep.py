import subprocess

from experiment import models
from django.contrib.auth.models import User

from patient.models import Patient

# Collect and send User's (nep: Researcher's) -> ResearchProject's
# (nep: Study's), Experiment's and Experiment releated objects
users = User.objects.all()

portal_server = "http://192.168.59.61:8000"

for user in users:
    subprocess.call(
        [
            "http",
            "-a",
            "lab1:nep-lab1",
            "--ignore-stdin",
            "POST",
            portal_server + "/api/researchers/",
            "first_name=" + user.first_name,
            "surname=" + user.last_name,
            "nes_id=" + str(user.id),
        ]
    )
    for research_project in models.ResearchProject.objects.filter(owner__id=user.id):
        if research_project.end_date is None:
            subprocess.call(
                [
                    "http",
                    "-a",
                    "lab1:nep-lab1",
                    "--ignore-stdin",
                    "POST",
                    portal_server + "/api/researchers/" + str(user.id) + "/studies/",
                    "title=" + research_project.title,
                    "description=" + research_project.description,
                    "start_date=" + str(research_project.start_date),
                    "nes_id=" + str(research_project.id),
                ]
            )
        else:
            subprocess.call(
                [
                    "http",
                    "-a",
                    "lab1:nep-lab1",
                    "--ignore-stdin",
                    "POST",
                    portal_server + "/api/researchers/" + str(user.id) + "/studies/",
                    "title=" + research_project.title,
                    "description=" + research_project.description,
                    "start_date=" + str(research_project.start_date),
                    "end_date=" + str(research_project.end_date),
                    "nes_id=" + str(research_project.id),
                ]
            )
        for experiment in models.Experiment.objects.filter(
            research_project__id=research_project.id
        ):
            subprocess.call(
                [
                    "http",
                    "-a",
                    "lab1:nep-lab1",
                    "--ignore-stdin",
                    "POST",
                    portal_server
                    + "/api/studies/"
                    + str(research_project.id)
                    + "/experiments/",
                    "title=" + experiment.title,
                    "description=" + experiment.description,
                    "data_acquisition_none="
                    + str(experiment.data_acquisition_is_concluded),
                    "nes_id=" + str(experiment.id),
                ]
            )
            for component in models.Component.objects.filter(
                experiment__id=experiment.id
            ):
                if component.duration_value is None:
                    subprocess.call(
                        [
                            "http",
                            "-a",
                            "lab1:nep-lab1",
                            "--ignore-stdin",
                            "POST",
                            portal_server
                            + "/api/experiments/"
                            + str(experiment.id)
                            + "/protocol_components/",
                            "identification=" + component.identification,
                            "description=" + component.description,
                            "duration_unit=" + str(component.duration_unit),
                            "component_type=" + str(component.component_type),
                            "nes_id=" + str(component.id),
                        ]
                    )
                else:
                    subprocess.call(
                        [
                            "http",
                            "-a",
                            "lab1:nep-lab1",
                            "--ignore-stdin",
                            "POST",
                            portal_server
                            + "/api/experiments/"
                            + str(experiment.id)
                            + "/protocol_components/",
                            "identification=" + component.identification,
                            "description=" + component.description,
                            "duration_value=" + str(component.duration_value),
                            "duration_unit=" + str(component.duration_unit),
                            "component_type=" + str(component.component_type),
                            "nes_id=" + str(component.id),
                        ]
                    )
                for group in models.Group.objects.filter(
                    experimental_protocol__id=component.id
                ):
                    subprocess.call(
                        [
                            "http",
                            "-a",
                            "lab1:nep-lab1",
                            "--ignore-stdin",
                            "POST",
                            portal_server + "/api/"
                            "protocol_components/" + str(component.id) + "/groups/",
                            "title=" + group.title,
                            "nes_id=" + str(group.id),
                        ]
                    )
#                                     'description=' + group.description,

# Send Patient's
for subject in models.Subject.objects.all():
    patient: Patient = Patient.objects.filter(id=subject.patient_id).get()
    subprocess.call(
        [
            "http",
            "-a",
            "lab1:nep-lab1",
            "--ignore-stdin",
            "POST",
            portal_server + "/api/participants/",
            "date_birth=" + str(patient.date_birth),
            "district=" + patient.district,
            "city=" + patient.city,
            "state=" + patient.state,
            "country=" + patient.country,
            "gender=" + patient.gender.name,
            "marital_status=" + patient.marital_status.name
            if patient.marital_status
            else "marital_status=",
            "nes_id=" + str(patient.id),
        ]
    )
