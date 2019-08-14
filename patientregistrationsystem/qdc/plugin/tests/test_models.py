from django.test import TestCase

from plugin.models import RandomForests


class RandomForestsModelTest(TestCase):

    def test_default_attributes(self):
        random_forests = RandomForests()
        self.assertEqual(random_forests.plugin_url, '')
