import coreapi
import os

from django.conf import settings

from .models import Experiment


class RestApiClient(object):
    client = None
    schema = None
    active = False

    def __init__(self):
        auth = coreapi.auth.BasicAuthentication(username=settings.PORTAL_API['USER'],
                                                password=settings.PORTAL_API['PASSWORD'])
        self.client = coreapi.Client(auth=auth)

        try:
            self.schema = self.client.get(settings.PORTAL_API['URL'] + ':' +
                                          settings.PORTAL_API['PORT'] + '/api/schema/')
            self.active = True
        except:
            self.active = False


def get_portal_status():
    return RestApiClient().active


def get_experiment_status_portal(experiment_id):

    rest = RestApiClient()

    status = None

    if rest.active:

        try:
            portal_experiment = rest.client.action(
                rest.schema, ['experiments', 'read'], params={"nes_id": str(experiment_id)})
        except:
            portal_experiment = None

        if portal_experiment and 'status' in portal_experiment[0]:
            status = portal_experiment[0]['status']

    return status


def send_user_to_portal(user):

    rest = RestApiClient()

    if not rest.active:
        return None

    try:
        portal_user = rest.client.action(
            rest.schema, ['researchers', 'read'], params={"nes_id": str(user.id)})

    except:
        portal_user = None

    # general params
    params = {"nes_id": str(user.id),
              "first_name": user.first_name,
              "surname": user.last_name,
              "email": user.email}

    # create or update
    if portal_user:
        # params["id"] = portal_user['id']

        portal_user = rest.client.action(
            rest.schema, ['researchers', 'update'], params=params)
    else:
        portal_user = rest.client.action(
            rest.schema, ['researchers', 'create'], params=params)

    return portal_user


def send_research_project_to_portal(research_project):

    rest = RestApiClient()

    if not rest.active:
        return None

    try:
        portal_research_project = rest.client.action(
            rest.schema, ['studies', 'read'], params={"nes_id": str(research_project.id)})
    except:
        portal_research_project = None

    # general params
    params = {"nes_id": str(research_project.id),
              "title": research_project.title,
              "description": research_project.description,
              "start_date": research_project.start_date.strftime("%Y-%m-%d")}
    if research_project.end_date:
        params["end_date"] = research_project.end_date.strftime("%Y-%m-%d")

    # create or update
    if portal_research_project:
        params["id"] = portal_research_project[0]['id']
        portal_research_project = rest.client.action(
            rest.schema, ['studies', 'update', 'update'], params=params)
    else:
        params["id"] = str(research_project.owner.id)
        portal_research_project = rest.client.action(
            rest.schema, ['researchers', 'studies', 'create'], params=params)

    return portal_research_project


def send_experiment_to_portal(experiment: Experiment):

    rest = RestApiClient()

    if not rest.active:
        return None

    portal_experiment = rest.client.action(
        rest.schema, ['experiments', 'read'], params={"nes_id": str(experiment.id)})

    # general params
    params = {"nes_id": str(experiment.id),
              "title": experiment.title,
              "description": experiment.description,
              "data_acquisition_done": str(experiment.data_acquisition_is_concluded),
              }

    # create or update
    if portal_experiment:
        params["id"] = portal_experiment[0]['id']
        action_keys = ['experiments', 'update', 'update']
    else:
        params["id"] = str(experiment.research_project.id)
        action_keys = ['studies', 'experiments', 'create']

    if experiment.ethics_committee_project_file:
        with open(settings.MEDIA_ROOT + '/' + str(experiment.ethics_committee_project_file), 'rb') as f:
            params["ethics_committee_project_file"] = \
                coreapi.utils.File(os.path.basename(experiment.ethics_committee_project_file.name), f)

            portal_experiment = rest.client.action(rest.schema, action_keys,
                                                   params=params, encoding="multipart/form-data")
    else:
        portal_experiment = rest.client.action(rest.schema, action_keys,
                                               params=params, encoding="multipart/form-data")

    return portal_experiment
