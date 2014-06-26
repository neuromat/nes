# -*- coding: UTF-8 -*-
from django.test import TestCase
import re


class FormUserValidation(TestCase):
    def test_password_pattern(self):
        """Testa o pattern definido """
        # Detalhamento do pattern
        #     (			# Start of group
        #       (?=.*\d)		#   must contains one digit from 0-9
        #       (?=.*[a-z])		#   must contains one lowercase characters
        #       (?=.*[A-Z])		#   must contains one uppercase characters
        #       (?=.*[@#$%])		#   must contains one special symbols in the list "@#$%"
        #               .		#     match anything with previous condition checking
        #               {6,20}	#        length at least 6 characters and maximum of 20
        #     )
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = "abcC2@!$"

        self.assertTrue(self.confirm_password(pattern, password), True)

    def test_password_confirmation(self):
        """Testa a senha e confirmacao de senha """
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = "abcC1@!$"
        confirm_password = "abcC0@!$"
        a = re.compile(pattern)
        self.assertTrue(a.match(password), True)
        self.assertEqual(password,confirm_password)

    def confirm_password(self, pattern, password):
        a = re.compile(pattern)
        return a.match(password)