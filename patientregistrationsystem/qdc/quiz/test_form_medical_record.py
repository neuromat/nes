__author__ = 'numec'
# -*- coding: UTF-8 -*-
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test.client import RequestFactory
from util_test import UtilTests
from models import ClassificationOfDiseases, MedicalRecordData, Diagnosis, ComplementaryExam, ExamFile
from views import User, GenderOption, reverse, Patient, \
    medical_record_view, medical_record_update, diagnosis_create, \
    medical_record_create_diagnosis_create, exam_create, exam_view


SEARCH_TEXT = 'search_text'

MEDICAL_RECORD_NEW = "medical_record_new"
PATIENT_VIEW = 'patient_view'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class MedicalRecordFormValidation(TestCase):
    user = ''
    data = {}
    util = UtilTests()

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        self.gender_opt.save()

        self.data = {'name_txt': 'Patient for test',
                     'cpf_id': '374.276.738-08',
                     'gender_opt': str(self.gender_opt.id),
                     'date_birth_txt': '01/02/1995',
                     'email_txt': 'email@email.com'
        }

    def fill_exam_record(self, test_file=True):
        self.data['description'] = 'Hemograma'
        self.data['doctor'] = 'Dr Medico'
        self.data['exam_site'] = 'Hospital'
        self.data['doctor_register'] = '1111'
        self.data['action'] = 'upload'
        self.data['date'] = '10/05/2005'

        if test_file:
            file_to_test = SimpleUploadedFile('quiz/tests.py', 'rb')
            self.data['content'] = file_to_test

    def test_medical_record_create_diagnosis_create(self):
        patient_mock = self.util.create_patient_mock()
        cid10_mock = self.util.create_cid10_mock()

        url = reverse(MEDICAL_RECORD_NEW, args=(patient_mock.pk,))
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Create an instance of a GET request.
        request = self.factory.get(reverse('medical_record_diagnosis_create', args=[patient_mock.pk, cid10_mock.pk, ]))
        request.user = self.user

        response = medical_record_create_diagnosis_create(request, patient_id=patient_mock.pk, cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        medical_record_data = MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()

        url = reverse('medical_record_view', args=[patient_mock.pk, medical_record_data.pk, ])
        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_view(request, patient_mock.pk, medical_record_data.pk)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'status_mode')

        try:
            url = reverse('medical_record_view', args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            self.assertRaises(medical_record_view(request, patient_mock.pk, 9999))

        except Http404:
            pass

        url = reverse("medical_record_edit", args=[patient_mock.pk, medical_record_data.pk, ])
        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_update(request, patient_id=patient_mock.pk, record_id=medical_record_data.pk)
        self.assertEqual(response.status_code, 200)

        try:
            url = reverse("medical_record_edit", args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            response = medical_record_update(request, patient_id=patient_mock.pk, record_id=9999)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

        self.data['action'] = ''
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_data.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 200)

        self.data['action'] = 'finish'
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_data.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 302)

        self.util.create_cid10_to_search()
        cid10_mock = ClassificationOfDiseases.objects.filter(code='B01').first()

        request = self.factory.get(
            reverse('diagnosis_create', args=[patient_mock.pk, medical_record_data.pk, cid10_mock.id, ]))
        request.user = self.user

        response = diagnosis_create(request, patient_id=patient_mock.pk, medical_record_id=medical_record_data.pk,
                                    cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 2)

        diagnosis_mock = Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).first()

        count_exams = ComplementaryExam.objects.all().count()

        request = self.factory.get(
            reverse('exam_create', args=[patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk, ]))
        request.user = self.user

        response = exam_create(request, patient_id=patient_mock.pk, record_id=medical_record_data.pk,
                               diagnosis_id=diagnosis_mock.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

        self.fill_exam_record()

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 1)

        self.fill_exam_record(test_file=False)
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 2)

        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 3)

        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 4)

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_data.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertGreaterEqual(ComplementaryExam.objects.all().count(), 1)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 5)

        complementary_exam = ComplementaryExam.objects.all().first()

        self.fill_exam_record(test_file=False)
        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_data.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 5)

        self.fill_exam_record()
        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_data.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 5)

        self.data['status'] = 'edit'
        request = self.factory.get(
            reverse('exam_view', args=(patient_mock.pk, medical_record_data.pk, complementary_exam.pk,)), self.data)
        request.user = self.user
        response = exam_view(request, patient_mock.pk, medical_record_data.pk, complementary_exam.pk)
        self.assertEqual(response.status_code, 200)

        exam_file = ExamFile.objects.all().first()

        response = self.client.post(
            reverse('exam_file_delete', args=(exam_file.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse('exam_delete', args=(patient_mock.pk, medical_record_data.pk, complementary_exam.pk,)), self.data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 4)

    def test_cid_search(self):
        self.util.create_cid10_to_search()

        # Busca valida
        self.data['medical_record'] = ''
        self.data['patient_id'] = ''
        self.data[SEARCH_TEXT] = 'A'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paratifoide')

        self.data[SEARCH_TEXT] = 'B'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tifoide')

        self.data[SEARCH_TEXT] = '01'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Febres')
        self.assertEqual(response.context['cid_10_list'].count(), 2)

        # Busca invalida
        self.data[SEARCH_TEXT] = 'ZZZA1'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'].count(), 0)

        self.data[SEARCH_TEXT] = ''
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'], '')