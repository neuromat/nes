from faker.factory import Factory

from survey.models import Survey


def create_survey(sid=212121):
    """
    :param sid: Survey id at LimeSurvey
    :return: Survey model instance
    """
    Faker = Factory.create()
    fake = Faker
    fake.seed(0)

    return Survey.objects.create(
        lime_survey_id=sid,
        en_title=fake.text(max_nb_chars=100),
        pt_title=fake.text(max_nb_chars=100),
    )
