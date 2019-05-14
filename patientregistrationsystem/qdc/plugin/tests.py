from django.core.urlresolvers import reverse, resolve

from export.tests.tests_helper import ExportTestCase
from plugin.views import send_to_plugin


class PluginTest(ExportTestCase):

    def setUp(self):
        super(PluginTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_send_to_plugin_status_code(self):
        url = reverse('send_to_plugin')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugin/send_to_plugin.html')

    def test_animal_new_url_resolves_animal_new_view(self):
        view = resolve('/plugin/')
        self.assertEquals(view.func, send_to_plugin)
