from django.db import models
from solo.models import SingletonModel

from survey.models import Survey


class RandomForests(SingletonModel):
    admission_assessment = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='survey_admission', blank=True, null=True)
    surgical_evaluation = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='survey_surgical', blank=True, null=True)
    followup_assessment = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='survey_followup', blank=True, null=True)
    plugin_url = models.CharField(max_length=200, default='')

    class Meta:
        permissions = (
            ("can_send_data_to_plugin", "Can send data to plugin"),
        )
