from django.test import TestCase
from survey.forms import SurveyForm
from django.contrib.auth.models import User

USER_USERNAME = "myadmin"
USER_PWD = "mypassword"


# Tests about the form of creation of a patient (sometimes called participant)
# Briefly, this class tests the first form of the tab 0 of app Patient
class SurveyFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.data: dict[str, Any] = {}

    # Test if the form with only the required fields filled is valid
    def test_SurveyForm_is_valid(self):
        self.data["is_initial_evaluation"] = False
        survey = SurveyForm(data=self.data)
        self.assertTrue(survey.is_valid())

        self.data["is_initial_evaluation"] = True
        survey = SurveyForm(data=self.data)
        self.assertTrue(survey.is_valid())
