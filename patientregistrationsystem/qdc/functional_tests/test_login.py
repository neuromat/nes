from selenium.webdriver.common.keys import Keys

from custom_user.tests_helper import create_user, TEST_PASSWORD
from functional_tests.base import FunctionalTest

TEST_USERNAME = 'suzana'


class LoginTest(FunctionalTest):

    def test_can_get_username_link_to_log_in(self):
        user = create_user('Senior researcher', TEST_USERNAME)
        # Suzana goes to the NES and see a form to enter her credentials to
        # log in. She enters her credentials
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('username').send_keys(user.username)
        password = self.browser.find_element_by_name('password')
        password.send_keys(TEST_PASSWORD)  # defined in create_user method
        password.send_keys(Keys.ENTER)

        # As is the first time that she is entering in NES, she has to
        # change your password
        self.wait_for(
            lambda: self.browser.find_element_by_name(
                'old_password').send_keys(TEST_PASSWORD)
        )
        # define old password equals to new password to facilitate other tests
        self.browser.find_element_by_name('new_password1').send_keys(
            TEST_PASSWORD
        )
        repeat_password = self.browser.find_element_by_name('new_password2')
        repeat_password.send_keys(TEST_PASSWORD)
        repeat_password.send_keys(Keys.ENTER)

        # She's logged in!
        self.wait_to_be_logged_in(username=TEST_USERNAME)

        # Now she logs out
        self.browser.find_element_by_link_text(TEST_USERNAME).send_keys(
            Keys.ENTER)
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Logout').click()
        )

        # She is loged out
        self.wait_to_logged_out()
