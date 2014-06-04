from django.test import TestCase
from django.contrib.auth.models import *


class FormValidation(TestCase):

    def test_invalid_cpf(self):

        user = User.objects.create_user(username = 'myadmin', email ='test@dummy.com', password = 'mypwd')
        uid = user.id
        user.is_staff = True
        user.save()

        logged = self.client.login(username='myadmin', password='mypwd')
        self.assertEqual(logged, True)

        data = {'name_txt': 'outro novo 2', 'cpf_id': '100.913.651-81'}
        response = self.client.post('/quiz/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf_id", u'CPF 100.913.651-81 n\xe3o \xe9 v\xe1lido')
