# -*- coding: utf-8 -*-

# This file was created based on what is explained in:
# https://code.djangoproject.com/wiki/InitialSQLDataDiangoORMWay
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'qdc.settings'

PermissionTable = [
    _("Can add alcohol frequency"),
    _("Can add alcohol period"),
    _("Can add amount cigarettes"),
    _("Can add block"),
    _("Can add classification of diseases"),
    _("Can add complementary exam"),
    _("Can add component"),
    _("Can add component configuration"),
    _("Can add content type"),
    _("Can add diagnosis"),
    _("Can add exam file"),
    _("Can add experiment"),
    _("Can add flesh tone"),
    _("Can add gender"),
    _("Can add group"),
    _("Can add group"),
    _("Can add historical experiment"),
    _("Can add historical patient"),
    _("Can add historical questionnaire response"),
    _("Can add historical social demographic data"),
    _("Can add historical social history data"),
    _("Can add historical telephone"),
    _("Can add instruction"),
    _("Can add keyword"),
    _("Can add log entry"),
    _("Can add marital status"),
    _("Can add medical record data"),
    _("Can add migration history"),
    _("Can add patient"),
    _("Can add pause"),
    _("Can add payment"),
    _("Can add permission"),
    _("Can add questionnaire"),
    _("Can add questionnaire response"),
    _("Can add questionnaire response"),
    _("Can add religion"),
    _("Can add research project"),
    _("Can add schooling"),
    _("Can add session"),
    _("Can add social demographic data"),
    _("Can add social history data"),
    _("Can add stimulus"),
    _("Can add stimulus type"),
    _("Can add subject"),
    _("Can add subject of group"),
    _("Can add survey"),
    _("Can add task"),
    _("Can add task for the experimenter"),
    _("Can add telephone"),
    _("Can add user"),
    _("Can add user profile"),
    _("Can change alcohol frequency"),
    _("Can change alcohol period"),
    _("Can change amount cigarettes"),
    _("Can change block"),
    _("Can change classification of diseases"),
    _("Can change complementary exam"),
    _("Can change component"),
    _("Can change component configuration"),
    _("Can change content type"),
    _("Can change diagnosis"),
    _("Can change exam file"),
    _("Can change experiment"),
    _("Can change flesh tone"),
    _("Can change gender"),
    _("Can change group"),
    _("Can change group"),
    _("Can change historical experiment"),
    _("Can change historical patient"),
    _("Can change historical questionnaire response"),
    _("Can change historical social demographic data"),
    _("Can change historical social history data"),
    _("Can change historical telephone"),
    _("Can change instruction"),
    _("Can change keyword"),
    _("Can change log entry"),
    _("Can change marital status"),
    _("Can change medical record data"),
    _("Can change migration history"),
    _("Can change patient"),
    _("Can change pause"),
    _("Can change payment"),
    _("Can change permission"),
    _("Can change questionnaire"),
    _("Can change questionnaire response"),
    _("Can change questionnaire response"),
    _("Can change religion"),
    _("Can change research project"),
    _("Can change research project created by others"),
    _("Can change schooling"),
    _("Can change session"),
    _("Can change social demographic data"),
    _("Can change social history data"),
    _("Can change stimulus"),
    _("Can change stimulus type"),
    _("Can change subject"),
    _("Can change subject of group"),
    _("Can change survey"),
    _("Can change task"),
    _("Can change task for the experimenter"),
    _("Can change telephone"),
    _("Can change user"),
    _("Can change user profile"),
    _("Can delete alcohol frequency"),
    _("Can delete alcohol period"),
    _("Can delete amount cigarettes"),
    _("Can delete block"),
    _("Can delete classification of diseases"),
    _("Can delete complementary exam"),
    _("Can delete component"),
    _("Can delete component configuration"),
    _("Can delete content type"),
    _("Can delete diagnosis"),
    _("Can delete exam file"),
    _("Can delete experiment"),
    _("Can delete flesh tone"),
    _("Can delete gender"),
    _("Can delete group"),
    _("Can delete group"),
    _("Can delete historical experiment"),
    _("Can delete historical patient"),
    _("Can delete historical questionnaire response"),
    _("Can delete historical social demographic data"),
    _("Can delete historical social history data"),
    _("Can delete historical telephone"),
    _("Can delete instruction"),
    _("Can delete keyword"),
    _("Can delete log entry"),
    _("Can delete marital status"),
    _("Can delete medical record data"),
    _("Can delete migration history"),
    _("Can delete patient"),
    _("Can delete pause"),
    _("Can delete payment"),
    _("Can delete permission"),
    _("Can delete questionnaire"),
    _("Can delete questionnaire response"),
    _("Can delete questionnaire response"),
    _("Can delete religion"),
    _("Can delete research project"),
    _("Can delete schooling"),
    _("Can delete session"),
    _("Can delete social demographic data"),
    _("Can delete social history data"),
    _("Can delete stimulus"),
    _("Can delete stimulus type"),
    _("Can delete subject"),
    _("Can delete subject of group"),
    _("Can delete survey"),
    _("Can delete task"),
    _("Can delete task for the experimenter"),
    _("Can delete telephone"),
    _("Can delete user"),
    _("Can delete user profile"),
    _("Can view medical record"),
    _("Can view patient"),
    _("Can view questionnaire response"),
    _("Can view questionnaire response"),
    _("Can view research project"),
    _("Can view survey"),
    _("Can export medical record"),
    _("Can export patient"),
    _("Can export questionnaire response"),
    _("Can register equipment"),
    _("Can view sensitive patient data"),
    _("Can send data to plugin"),
]

GroupTable = [
    _("Attendant"),
    _("Physiotherapist"),
    _("Doctor"),
    _("Junior researcher"),
    _("Senior researcher"),
    _("Administrator"),
]

patient_content_type = ContentType.objects.get(app_label='patient', model='patient')
medicalrecorddata_content_type = ContentType.objects.get(app_label='patient', model='medicalrecorddata')
survey_content_type = ContentType.objects.get(app_label='survey', model='survey')
patient_quest_response_content_type = ContentType.objects.get(app_label='patient', model='questionnaireresponse')
researchproject_content_type = ContentType.objects.get(app_label='experiment', model='researchproject')
experiment_content_type = ContentType.objects.get(app_label='experiment', model='experiment')
subject_content_type = ContentType.objects.get(app_label='experiment', model='subject')
questionnaireresponse_content_type = ContentType.objects.get(app_label='experiment', model='questionnaireresponse')
equipment_content_type = ContentType.objects.get(app_label='experiment', model='equipment')
user_content_type = ContentType.objects.get(app_label='auth', model='user')
plugin_content_type = ContentType.objects.get(app_label='plugin', model='randomforests')


# CREATE ATTENDANT
group_attendant, attendant_created = Group.objects.get_or_create(name='Attendant')

attendant_permission_list = [Permission.objects.get(codename='add_patient', content_type=patient_content_type),
                             Permission.objects.get(codename='change_patient', content_type=patient_content_type),
                             Permission.objects.get(codename='view_patient', content_type=patient_content_type)]

for permission in attendant_permission_list:
    group_attendant.permissions.add(permission)


# CREATE PHYSIOTHERAPIST
group_physiotherapist, physiotherapist_created = Group.objects.get_or_create(name='Physiotherapist')

physiotherapist_permission_list = list(attendant_permission_list)
physiotherapist_permission_list += [
    Permission.objects.get(
        codename='view_medicalrecorddata',
        content_type=medicalrecorddata_content_type),
    Permission.objects.get(
        codename='view_survey', content_type=survey_content_type),
    Permission.objects.get(
        codename='add_survey', content_type=survey_content_type),
    Permission.objects.get(
        codename='change_survey', content_type=survey_content_type),
    Permission.objects.get(
        codename='delete_survey', content_type=survey_content_type),
    Permission.objects.get(
        codename='add_questionnaireresponse',
        content_type=patient_quest_response_content_type),
    Permission.objects.get(
        codename='change_questionnaireresponse',
        content_type=patient_quest_response_content_type),
    Permission.objects.get(
        codename='view_questionnaireresponse',
        content_type=patient_quest_response_content_type),
    Permission.objects.get(
        codename='delete_questionnaireresponse',
        content_type=patient_quest_response_content_type)
]

for permission in physiotherapist_permission_list:
    group_physiotherapist.permissions.add(permission)


# CREATE DOCTOR
group_doctor, doctor_created = Group.objects.get_or_create(name='Doctor')

doctor_permission_list = list(physiotherapist_permission_list)
doctor_permission_list += [Permission.objects.get(codename='add_medicalrecorddata',
                                                  content_type=medicalrecorddata_content_type)]

for permission in doctor_permission_list:
    group_doctor.permissions.add(permission)


# CREATE JUNIOR RESEARCHER
group_junior_researcher, junior_researcher_created = Group.objects.get_or_create(name='Junior researcher')

junior_researcher_permission_list = list(physiotherapist_permission_list)
junior_researcher_permission_list += [Permission.objects.get(codename='add_researchproject',
                                                             content_type=researchproject_content_type),
                                      Permission.objects.get(codename='change_researchproject',
                                                             content_type=researchproject_content_type),
                                      Permission.objects.get(codename='view_researchproject',
                                                             content_type=researchproject_content_type),
                                      Permission.objects.get(codename='delete_researchproject',
                                                             content_type=researchproject_content_type),
                                      Permission.objects.get(codename='add_experiment',
                                                             content_type=experiment_content_type),
                                      Permission.objects.get(codename='change_experiment',
                                                             content_type=experiment_content_type),
                                      Permission.objects.get(codename='delete_experiment',
                                                             content_type=experiment_content_type),
                                      Permission.objects.get(codename='add_questionnaireresponse',
                                                             content_type=questionnaireresponse_content_type),
                                      Permission.objects.get(codename='change_questionnaireresponse',
                                                             content_type=questionnaireresponse_content_type),
                                      Permission.objects.get(codename='view_questionnaireresponse',
                                                             content_type=questionnaireresponse_content_type),
                                      Permission.objects.get(codename='delete_questionnaireresponse',
                                                             content_type=questionnaireresponse_content_type),
                                      Permission.objects.get(codename='register_equipment',
                                                             content_type=equipment_content_type),
                                      Permission.objects.get(codename='add_subject',
                                                             content_type=subject_content_type),
                                      Permission.objects.get(codename='change_subject',
                                                             content_type=subject_content_type),
                                      Permission.objects.get(codename='delete_subject',
                                                             content_type=subject_content_type),
                                      Permission.objects.get(codename='can_send_data_to_plugin',
                                                             content_type=plugin_content_type)
                                      ]

for permission in junior_researcher_permission_list:
    group_junior_researcher.permissions.add(permission)


# CREATE SENIOR RESEARCHER
group_senior_researcher, senior_researcher_created = Group.objects.get_or_create(name='Senior researcher')

senior_researcher_permission_list = list(junior_researcher_permission_list)
senior_researcher_permission_list += [Permission.objects.get(codename='change_researchproject_from_others',
                                                             content_type=researchproject_content_type),
                                      Permission.objects.get(codename='export_patient',
                                                             content_type=patient_content_type),
                                      Permission.objects.get(codename='export_medicalrecorddata',
                                                             content_type=medicalrecorddata_content_type),
                                      Permission.objects.get(codename='export_questionnaireresponse',
                                                             content_type=patient_quest_response_content_type),
                                      Permission.objects.get(codename='sensitive_data_patient',
                                                             content_type=patient_content_type)]

for permission in senior_researcher_permission_list:
    group_senior_researcher.permissions.add(permission)


# CREATE ADMINISTRATOR
group_admininstrator, administrator_created = Group.objects.get_or_create(name='Administrator')

administrator_permission_list = list(senior_researcher_permission_list)
administrator_permission_list += [Permission.objects.get(codename='add_user',
                                                         content_type=user_content_type),
                                  Permission.objects.get(codename='change_user',
                                                         content_type=user_content_type),
                                  Permission.objects.get(codename='delete_user',
                                                         content_type=user_content_type),
                                  Permission.objects.get(codename='delete_patient',
                                                         content_type=patient_content_type),
                                  Permission.objects.get(codename='change_researchproject_owner',
                                                         content_type=researchproject_content_type),
                                  Permission.objects.get(codename='add_medicalrecorddata',
                                                         content_type=medicalrecorddata_content_type)]

for permission in administrator_permission_list:
    group_admininstrator.permissions.add(permission)

# Do not remove this line. It is important to the correct operation of the script
