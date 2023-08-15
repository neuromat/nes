import random

from django.db import models


class Survey(models.Model):
    code = models.CharField(max_length=10, unique=True)

    lime_survey_id = models.IntegerField(unique=True)
    is_initial_evaluation = models.BooleanField(default=True)
    pt_title = models.CharField(null=True, max_length=255, default=None)
    en_title = models.CharField(null=True, max_length=255, default=None)
    is_active = models.BooleanField(null=True)

    def __str__(self):
        if self.en_title:
            return self.en_title
        elif self.pt_title:
            return self.pt_title
        else:
            return self.code

    class Meta:
        permissions = (
            # ("view_survey", "Can view survey"),
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.create_random_survey_code()
        super(Survey, self).save(*args, **kwargs)

    @staticmethod
    def create_random_survey_code():
        used_codes = set([survey.code for survey in Survey.objects.all()])
        possible_code = set(["Q" + str(item) for item in range(1, 100000)])
        available_codes = list(possible_code - used_codes)
        return random.choice(available_codes)


class SensitiveQuestion(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="sensitive_questions"
    )
    code = models.CharField(max_length=150)
    question = models.TextField()

    class Meta:
        unique_together = ("survey", "code")
