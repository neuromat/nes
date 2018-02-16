import os

import time

import sys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        exec(open('add_initial_data.py').read())
        # redirect sys.stderr to avoid display success message
        # during test
        stdout_backup, sys.stdout = sys.stdout, open('/tmp/tests.txt', 'w+')
        call_command('loaddata', 'load_initial_data.json')
        sys.stdout.close()
        sys.stdout = stdout_backup

        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        self.browser = webdriver.Firefox(profile)

        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

        # A neuroscience researcher wants to access NES in your lab
        self.browser.get(self.live_server_url)

    def tearDown(self):
        self.browser.quit()

    @staticmethod
    def wait_for(fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_to_be_logged_in(self, username):
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('suzana')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(username, navbar.text)

    def wait_to_logged_out(self):
        self.wait_for(
            lambda: self.browser.find_element_by_name('username')
        )
        login_button = self.browser.find_element_by_css_selector('.btn')
        self.assertEqual('Login', login_button.text)
