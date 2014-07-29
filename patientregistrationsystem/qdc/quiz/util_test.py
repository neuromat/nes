from django.test import TestCase
from views import Patient, GenderOption
from models import ClassificationOfDiseases

class UtilTests():
    def create_patient_mock(self, name='Pacient Test'):
        """ Cria um paciente para ser utilizado durante os testes """
        gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        gender_opt.save()

        p_mock = Patient()
        p_mock.name_txt = name
        p_mock.date_birth_txt = '2001-01-15'
        p_mock.cpf_id = '374.276.738-08'
        p_mock.gender_opt_id = gender_opt.id
        p_mock.save()
        return p_mock

    def create_cid10_to_search(self):
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()
        cid10 = ClassificationOfDiseases.objects.create(code='B01', description='Febres tifoide ',
                                                        abbreviated_description='B01 Febres tifoide ')
        cid10.save()

    def create_cid10_mock(self):
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()

        return cid10