# -*- coding: UTF-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


def get_export_dir(instance, filename):
    return "export/%(user)s/%(export)s/%(filename)s" % \
        {'user': instance.export.user.id,
         'export': instance.export.pk, 'filename': filename}


class Export(models.Model):
    user = models.ForeignKey(User, null=False)
    date = models.DateTimeField(null=False, auto_now_add=True)
    input_file = models.FileField(upload_to=get_export_dir, null=False)
    output_export = models.FileField(upload_to=get_export_dir, null=False)

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(Export, self).delete(*args, **kwargs)


#     lime_survey_id = models.IntegerField(null=False, blank=False, unique=True)
#     is_initial_evaluation = models.BooleanField(null=False, blank=False, default=True)
#
#     class Meta:
#         permissions = (
#             ("view_survey", "Can view survey"),
#         )


# class Exportation():
#     def anonymize_code(code):
#         '''
#         :param code: code to be anonymized
#         :return: code anonymyzed
#         '''
#
#         ###
#
#     def anonymize_questionnaire(code):
#
#
#     def anonymize_participant(code):
#
#
#     def read_json(queryset):
#         '''
#         :param queryset: data to be read
#         :return: queryset with data transformed
#         '''
#
#         ###
#
#     def read_LimeSurvey(code):
#         '''
#         :param code:
#         :return:
#         '''
#
#
