from survey.models import Survey


def create_survey(sid):
    """
    :param sid: Survey id in LimeSurvey
    :return:
    """
    return Survey.objects.create(lime_survey_id=sid)
