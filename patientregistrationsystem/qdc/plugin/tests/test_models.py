from django.test import TestCase

from plugin.models import RandomForests


class RandomForestsModelTest(TestCase):

    def test_default_attributes(self):
        random_forests = RandomForests()
        self.assertEqual(random_forests.admission_assessment, None)
        self.assertEqual(random_forests.surgical_evaluation, None)
        self.assertEqual(random_forests.followup_assessment, None)
        self.assertEqual(random_forests.plugin_url, '')
