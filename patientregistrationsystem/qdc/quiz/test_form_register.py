from django.test import TestCase
from django.contrib.auth.models import *


class FormValidation(TestCase):

    def test_invalid_cpf(self):
        """testa inclusao de paciente com cpf invalido"""

        username_dummy = 'myadmin'
        password_dummy = 'mypassword'

        user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
        user.is_staff = True
        user.save()

        logged = self.client.login(username=username_dummy, password=password_dummy)
        self.assertEqual(logged, True)

        data = {'name_txt': 'Novo paciente',
                'cpf_id': '100.913.651-81'}
        response = self.client.post('/quiz/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf_id", u'CPF 100.913.651-81 n\xe3o \xe9 v\xe1lido')
