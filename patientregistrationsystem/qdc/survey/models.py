from django.db import models


class Survey(models.Model):
    lime_survey_id = models.IntegerField(null=False, blank=False, unique=True)
    is_initial_evaluation = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        permissions = (
            ("view_survey", "Can view survey"),
        )
