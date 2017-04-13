import coreapi

from django.conf import settings


def get_experiment_status_portal(experiment_id):

    auth = coreapi.auth.BasicAuthentication(username=settings.PORTAL_API['USER'],
                                            password=settings.PORTAL_API['PASSWORD'])
    client = coreapi.Client(auth=auth)
    schema = client.get(settings.PORTAL_API['URL'] + ':' + settings.PORTAL_API['PORT'] + '/api/schema/')
    portal_experiment = client.action(schema, ['api', 'experiments', 'read'], params={"nes_id": str(experiment_id)})

    status = None
    if portal_experiment and 'status' in portal_experiment[0]:
        status = portal_experiment[0]['status']
    return status
