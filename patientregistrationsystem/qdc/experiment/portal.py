import coreapi

from django.conf import settings


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

        portal_experiment = rest.client.action(
            rest.schema, ['api', 'experiments', 'read'], params={"nes_id": str(experiment_id)})

        if portal_experiment and 'status' in portal_experiment[0]:
            status = portal_experiment[0]['status']

    return status


def send_user_to_portal(user):

    rest = RestApiClient()

    if not rest.active:
        return None

    portal_user = rest.client.action(
        rest.schema, ['api', 'researchers', 'read'], params={"nes_id": str(user.id)})

    # general params
    params = {"nes_id": str(user.id),
              "first_name": user.first_name,
              "surname": user.last_name,
              "email": user.email}

    # create or update
    if portal_user:
        params["id"] = portal_user[0]['id']

        portal_user = rest.client.action(
            rest.schema, ['api', 'researchers', 'update', 'update'], params=params)
    else:
        portal_user = rest.client.action(
            rest.schema, ['api', 'researchers', 'create'], params=params)

    return portal_user


def send_research_project_to_portal(research_project):

    rest = RestApiClient()

    if not rest.active:
        return None

    portal_research_project = rest.client.action(
        rest.schema, ['api', 'studies', 'read'], params={"nes_id": str(research_project.id)})

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
            rest.schema, ['api', 'studies', 'update', 'update'], params=params)
    else:
        params["id"] = str(research_project.owner.id)
        portal_research_project = rest.client.action(
            rest.schema, ['api', 'researchers', 'studies', 'create'], params=params)

    return portal_research_project


def send_experiment_to_portal(experiment):

    rest = RestApiClient()

    if not rest.active:
        return None

    portal_experiment = rest.client.action(
        rest.schema, ['api', 'experiments', 'read'], params={"nes_id": str(experiment.id)})

    # general params
    params = {"nes_id": str(experiment.id),
              "title": experiment.title,
              "description": experiment.description,
              "data_acquisition_done": str(experiment.data_acquisition_is_concluded)}

    # create or update
    if portal_experiment:
        params["id"] = portal_experiment[0]['id']
        portal_experiment = rest.client.action(
            rest.schema, ['api', 'experiments', 'update', 'update'], params=params)
    else:
        params["id"] = str(experiment.research_project.id)
        portal_experiment = rest.client.action(
            rest.schema, ['api', 'studies', 'experiments', 'create'], params=params)

    return portal_experiment
