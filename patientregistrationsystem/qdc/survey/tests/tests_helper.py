from survey.models import Survey


def create_survey(sid):
    """
    :param sid: Survey id in LimeSurvey
    :return: Survey model instance
    """
    # TODO: make sid with faker
    return Survey.objects.create(lime_survey_id=sid)
