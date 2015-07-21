# -*- coding: utf-8 -*-

# This file was created based on what is explained in:
# https://code.djangoproject.com/wiki/InitialSQLDataDiangoORMWay

from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'qdc.settings'

# from settings import *

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from patient.models import AlcoholFrequency, AlcoholPeriod, AmountCigarettes, FleshTone, Gender, MaritalStatus, \
    Payment, Religion, Schooling

g = Group(name='Administrador')
g.save()
g.permissions.add(Permission.objects.get(codename='add_user'),
                  Permission.objects.get(codename='change_user'),
                  Permission.objects.get(codename='delete_user'))

g = Group(name='Atendente')
g.save()
patient_content_type = ContentType.objects.get(app_label='patient', model='patient')
attendant_permission_list = [Permission.objects.get(codename='add_patient', content_type=patient_content_type),
                             Permission.objects.get(codename='change_patient', content_type=patient_content_type),
                             Permission.objects.get(codename='view_patient', content_type=patient_content_type),
                             Permission.objects.get(codename='delete_patient', content_type=patient_content_type)]
for p in attendant_permission_list:
    g.permissions.add(p)

g = Group(name='Fisioterapeuta')
g.save()
medicalrecorddata_content_type = ContentType.objects.get(app_label='patient', model='medicalrecorddata')
survey_content_type = ContentType.objects.get(app_label='survey', model='survey')
patient_quest_response_content_type = ContentType.objects.get(app_label='patient', model='questionnaireresponse')
# Can do what a attendant does
physiotherapist_permission_list = attendant_permission_list
# Plus
physiotherapist_permission_list += [
    # Medical record data
    Permission.objects.get(codename='view_medicalrecorddata', content_type=medicalrecorddata_content_type),
    # Survey
    Permission.objects.get(codename='view_survey', content_type=survey_content_type),
    Permission.objects.get(codename='add_survey', content_type=survey_content_type),
    Permission.objects.get(codename='change_survey', content_type=survey_content_type),
    Permission.objects.get(codename='delete_survey', content_type=survey_content_type),
    # Questionnaire response
    Permission.objects.get(codename='add_questionnaireresponse', content_type=patient_quest_response_content_type),
    Permission.objects.get(codename='change_questionnaireresponse', content_type=patient_quest_response_content_type),
    Permission.objects.get(codename='view_questionnaireresponse', content_type=patient_quest_response_content_type),
    Permission.objects.get(codename='delete_questionnaireresponse', content_type=patient_quest_response_content_type)
]
for p in physiotherapist_permission_list:
    g.permissions.add(p)

g = Group(name='Médico')
g.save()
# Can do what a physiotherapist does
doctor_permission_list = physiotherapist_permission_list
# Plus
doctor_permission_list.append(Permission.objects.get(codename='add_medicalrecorddata',
                                                     content_type=medicalrecorddata_content_type))
for p in doctor_permission_list:
    g.permissions.add(p)

g = Group(name='Pesquisador júnior')
g.save()
researchproject_content_type = ContentType.objects.get(app_label='experiment', model='researchproject')
experiment_content_type = ContentType.objects.get(app_label='experiment', model='experiment')
questionnaireresponse_content_type = ContentType.objects.get(app_label='experiment', model='questionnaireresponse')
subject_content_type = ContentType.objects.get(app_label='experiment', model='subject')
# Can do what a physiotherapist does
junior_researcher_permission_list = physiotherapist_permission_list
# Plus
junior_researcher_permission_list += [
    # Research project
    Permission.objects.get(codename='add_researchproject', content_type=researchproject_content_type),
    Permission.objects.get(codename='change_researchproject', content_type=researchproject_content_type),
    Permission.objects.get(codename='view_researchproject', content_type=researchproject_content_type),
    Permission.objects.get(codename='delete_researchproject', content_type=researchproject_content_type),
    # Experiment
    Permission.objects.get(codename='add_experiment', content_type=experiment_content_type),
    Permission.objects.get(codename='change_experiment', content_type=experiment_content_type),
    Permission.objects.get(codename='delete_experiment', content_type=experiment_content_type),
    # Experiment questionnaire response
    Permission.objects.get(codename='add_questionnaireresponse', content_type=questionnaireresponse_content_type),
    Permission.objects.get(codename='change_questionnaireresponse', content_type=questionnaireresponse_content_type),
    Permission.objects.get(codename='view_questionnaireresponse', content_type=questionnaireresponse_content_type),
    Permission.objects.get(codename='delete_questionnaireresponse', content_type=questionnaireresponse_content_type),
    # Subject
    Permission.objects.get(codename='add_subject', content_type=subject_content_type),
    Permission.objects.get(codename='change_subject', content_type=subject_content_type),
    Permission.objects.get(codename='delete_subject', content_type=subject_content_type),
]

for p in junior_researcher_permission_list:
    g.permissions.add(p)

g = Group(name='Pesquisador sênior')
g.save()
# Can do what a junior researcher does
senior_researcher_permission_list = junior_researcher_permission_list
# Plus
senior_researcher_permission_list.append(Permission.objects.get(codename='change_researchproject_from_others',
                                                                content_type=researchproject_content_type))
for p in senior_researcher_permission_list:
    g.permissions.add(p)

# Alcohol frequency
af = AlcoholFrequency(name="Todos os dias")
af.save()
af = AlcoholFrequency(name="Todos os finais de semana")
af.save()
af = AlcoholFrequency(name="Esporadicamente")
af.save()

# Alcohol period
ap = AlcoholPeriod(name="Mais de 10 anos")
ap.save()
ap = AlcoholPeriod(name="5-10 anos")
ap.save()
ap = AlcoholPeriod(name="1-5 anos")
ap.save()
ap = AlcoholPeriod(name="Menos de 1 ano")
ap.save()

# Amount cigarettes
ac = AmountCigarettes(name="Mais de 3 maços")
ac.save()
ac = AmountCigarettes(name="1-2 maços")
ac.save()
ac = AmountCigarettes(name="Menos de 1 maço")
ac.save()

# Flesh tone
ft = FleshTone(name="Amarelo")
ft.save()
ft = FleshTone(name="Branco")
ft.save()
ft = FleshTone(name="Indígena")
ft.save()
ft = FleshTone(name="Pardo")
ft.save()
ft = FleshTone(name="Preto")
ft.save()

# Gender
g = Gender(name="Masculino")
g.save()
g = Gender(name="Feminino")
g.save()

# Marital status
ms = MaritalStatus(name="Não informado")
ms.save()
ms = MaritalStatus(name="Viúvo")
ms.save()
ms = MaritalStatus(name="Separado/Divorciado")
ms.save()
ms = MaritalStatus(name="Casado/Convive junto")
ms.save()
ms = MaritalStatus(name="Solteiro")
ms.save()

# Payment
p = Payment(name="Particular")
p.save()
p = Payment(name="Convênio")
p.save()
p = Payment(name="SUS")
p.save()

# Religion
r = Religion(name="Budismo")
r.save()
r = Religion(name="Candomblé")
r.save()
r = Religion(name="Católica")
r.save()
r = Religion(name="Espírita")
r.save()
r = Religion(name="Evangélica")
r.save()
r = Religion(name="Igreja de Jesus Cristo dos Santos dos Últimos Dias")
r.save()
r = Religion(name="Judaismo")
r.save()
r = Religion(name="Protestante")
r.save()
r = Religion(name="Religiões Orientais")
r.save()
r = Religion(name="Sem religião")
r.save()
r = Religion(name="Testemunha de Jeová")
r.save()
r = Religion(name="Umbanda")
r.save()

# Schooling
s = Schooling(name="Superior completo")
s.save()
s = Schooling(name="Médio completo")
s.save()
s = Schooling(name="Fundamental completo")
s.save()
s = Schooling(name="5º Ano Fundamental")
s.save()
s = Schooling(name="Analfabeto / até 4º Ano Fundamental")
s.save()
