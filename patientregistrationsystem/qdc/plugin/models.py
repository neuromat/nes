from django.db import models
from solo.models import SingletonModel

from survey.models import Survey


class RandomForests(SingletonModel):
    admission_assessment = models.ForeignKey(Survey, related_name='survey_admission')
    surgical_evaluation = models.ForeignKey(Survey, related_name='survey_surgical')

    class Meta:
        permissions = (
            ("can_send_data_to_plugin", "Can send data to plugin"),
        )
