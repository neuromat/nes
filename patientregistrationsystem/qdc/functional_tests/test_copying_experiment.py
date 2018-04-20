from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore

from custom_user.tests_helper import create_user
from functional_tests.base import FunctionalTest
from functional_tests.test_login import TEST_USERNAME
from experiment.tests import ObjectsFactory


class CopyExperimentTest(FunctionalTest):

    def create_pre_authenticated_session(self):
        user = create_user(
            group_name='Senior researcher', username=TEST_USERNAME
        )
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        # to set a cookie we need to first visit the domain.
        # 404 pages load the quickest
        self.browser.get(self.live_server_url + '/404_no_such_url')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/'
        ))

    @staticmethod
    def create_objects():
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        # experimental_protocol = ObjectsFactory.
        group = ObjectsFactory.create_group(experiment)

    def test_can_see_copy_experiment_button(self):
        username = TEST_USERNAME
        self.browser.get(self.live_server_url)
        self.wait_to_logged_out()

        self.create_pre_authenticated_session()
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(username)

        # Suzana, a senior researcher user in NES, is trying to change
        # an experiment with an experimental protocol that already has data
        # collection. The system does not allow that, so a modal appears
        # telling her that she can copy the experiment with all experiment
        # data.
        self.create_objects()
