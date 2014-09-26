# -*- coding: UTF-8 -*-
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test.client import RequestFactory
from util_test import UtilTests
from models import ClassificationOfDiseases, MedicalRecordData, Diagnosis, ComplementaryExam, ExamFile
from views import User, Gender, reverse, Patient, \
    medical_record_view, medical_record_update, diagnosis_create, \
    medical_record_create_diagnosis_create, exam_create, exam_view


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
        #print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

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

    def test_diagnosis_create_and_delete(self):
        """
        Testar a criação, leitura, atualização e exclusão do Diagnóstico
        """

        # Create mock objects to tests
        self.util.create_cid10_to_search()
        cid10_mock = ClassificationOfDiseases.objects.filter(code='B01').first()
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)

        request = self.factory.get(
            reverse('diagnosis_create', args=[patient_mock.pk, medical_record_mock.pk, cid10_mock.id, ]))
        request.user = self.user
        response = diagnosis_create(request, patient_id=patient_mock.pk, medical_record_id=medical_record_mock.pk,
                                    cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

        # Test for diagnosis delete
        count_diagnosis = Diagnosis.objects.all().count()

        response = self.client.post(
            reverse('diagnosis_delete', args=(patient_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.all().count(), count_diagnosis - 1)

    def test_medical_record_crud(self):
        """
        Testar a criação, leitura, atualização e exclusão do Avaliação Medica (MedicalRecord)
        """
        patient_mock = self.util.create_patient_mock(user=self.user)
        cid10_mock = self.util.create_cid10_mock()

        # Create a new Medical Record and check if it created with successfully
        url = reverse('medical_record_new', args=(patient_mock.pk,))
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # It test uses a GET method. Create an instance of a GET request -
        request = self.factory.get(reverse('medical_record_diagnosis_create', args=[patient_mock.pk, cid10_mock.pk, ]))
        request.user = self.user
        response = medical_record_create_diagnosis_create(request, patient_id=patient_mock.pk, cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        # Test a Medical Record View method
        medical_record_data = MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()

        url = reverse('medical_record_view', args=[patient_mock.pk, medical_record_data.pk, ])

        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_view(request, patient_mock.pk, medical_record_data.pk)
        self.assertEqual(response.status_code, 200)

        # It makes tests with a invalid ID for method medical record view
        try:
            url = reverse('medical_record_view', args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            self.assertRaises(medical_record_view(request, patient_mock.pk, 9999))

        except Http404:
            pass

    def test_medical_record_edit(self):
        """
        Testar a edição de avaliação medica
        """

        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        # Test a medical record edit method - no changes it will occurs - just pass by the method
        url = reverse("medical_record_edit", args=[patient_mock.pk, medical_record_mock.pk, ])
        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_update(request, patient_id=patient_mock.pk, record_id=medical_record_mock.pk)
        self.assertEqual(response.status_code, 200)


        # It makes tests with a invalid ID for method medical record edit
        try:
            url = reverse("medical_record_edit", args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            response = medical_record_update(request, patient_id=patient_mock.pk, record_id=9999)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

        # It will coverage all method - medical record edit
        self.data['action'] = ''
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 200)

        self.data['action'] = 'finish'
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 302)

    def test_exam_create(self):
        """
        Testar a criação de exames
        """
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

        count_exams = ComplementaryExam.objects.all().count()

        # A simple test of Exam Create Method.
        request = self.factory.get(
            reverse('exam_create', args=[patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk, ]))
        request.user = self.user

        response = exam_create(request, patient_id=patient_mock.pk, record_id=medical_record_mock.pk,
                               diagnosis_id=diagnosis_mock.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

        # Test of Exam Create with file attachment
        self.fill_exam_record()

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 1)

        # Test of exam Create withoud file attachment
        self.fill_exam_record(test_file=False)
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 2)

        # A tests more conditionals of exam create method.
        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 3)

        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 4)

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertGreaterEqual(ComplementaryExam.objects.all().count(), 1)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 5)

    def create_complementary_exam(self, patient_mock, medical_record_mock, diagnosis_mock):
        """
        Testar a inclusao de exames complementares
        """
        self.fill_exam_record()

        count_exams = ComplementaryExam.objects.all().count()

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 1)

    def test_exam_update(self):
        """
        Testar a atualização de um exame complementar
        """
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

        self.create_complementary_exam(patient_mock, medical_record_mock, diagnosis_mock)
        count_exams = ComplementaryExam.objects.all().count()

        # Tests for exam edit method
        complementary_exam = ComplementaryExam.objects.all().first()

        self.fill_exam_record(test_file=False)
        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

        self.fill_exam_record()
        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

    def test_exam_file_upload(self):
        """
        Testar a adição de exame com arquivo anexo - inclusao e remoção
        """
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

        # Tests for exam edit method
        self.create_complementary_exam(patient_mock, medical_record_mock, diagnosis_mock)
        complementary_exam = ComplementaryExam.objects.all().first()
        count_exams = ComplementaryExam.objects.all().count()

        self.data['status'] = 'edit'
        request = self.factory.get(
            reverse('exam_view', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        request.user = self.user
        response = exam_view(request, patient_mock.pk, medical_record_mock.pk, complementary_exam.pk)
        self.assertEqual(response.status_code, 200)

        # Tests delete file from exam
        exam_file = ExamFile.objects.all().first()

        response = self.client.post(
            reverse('exam_file_delete', args=(exam_file.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # It will delete first exam created
        response = self.client.post(
            reverse('exam_delete', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), 0)

    def test_cid_search(self):
        """
        Testa busca pelo CID
        """

        search_text_meta = 'search_text'

        # Create a cids to make search.
        self.util.create_cid10_to_search()

        # Busca valida
        self.data['medical_record'] = ''
        self.data['patient_id'] = ''
        self.data[search_text_meta] = 'A'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paratifoide')

        self.data[search_text_meta] = 'B'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tifoide')

        self.data[search_text_meta] = '01'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Febres')
        self.assertEqual(response.context['cid_10_list'].count(), 2)

        # Busca invalida
        self.data[search_text_meta] = 'ZZZA1'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'].count(), 0)

        self.data[search_text_meta] = ''
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'], '')