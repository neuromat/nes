from calendar import TextCalendar
from django.db.utils import IntegrityError
from django.test import TestCase
from custom_user.models import Institution
from configuration.models import Contact, LocalInstitution, get_institution_logo_dir


class LocalInstiutionTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        institution: Institution = Institution.objects.create(
            name="Universidade Federal do Rio de Janeiro",
            acronym="UFRJ",
            country="BR",
        )

    def test_valid_LocalInstitution(self) -> None:
        localinstitution = LocalInstitution.objects.create(
            code="1234", institution=Institution.objects.first(), url="https://ufrj.br/"
        )

        self.assertEqual(str(localinstitution), "Local Institution")

    def test_adding_multiple_LocalInstitution(self) -> None:
        LocalInstitution.objects.create(
            code="1234", institution=Institution.objects.first(), url="https://ufrj.br/"
        )

        with self.assertRaises(IntegrityError):
            LocalInstitution.objects.create(
                code="1234",
                institution=Institution.objects.first(),
                url="https://ufrj.br/",
            ),

    def test_get_institution_logo_dir(self) -> None:
        institution = LocalInstitution.objects.create(
            code="1234", institution=Institution.objects.first(), url="https://ufrj.br/"
        )

        self.assertEqual(
            "institution_logo/1/test.png",
            get_institution_logo_dir(institution, "test.png"),
        )


class ContactTest(TestCase):
    def test_valid_contact(self) -> None:
        contact = Contact.objects.create(name="adm test", email="test@test.com")

        self.assertEqual(str(contact), "adm test")
