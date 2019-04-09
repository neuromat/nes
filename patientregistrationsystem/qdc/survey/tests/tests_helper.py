from survey.models import Survey


def create_survey(sid=212121):
    """
    :param sid: Survey id at LimeSurvey
    :return: Survey model instance
    """
    return Survey.objects.create(lime_survey_id=sid)
