from django.test import TestCase

from validation import CPF

class CPF_validation_test(TestCase):

    goodValues = (
        '288.666.827-30',
        '597.923.110-25',
        '981.108.954-09',
        '174.687.414-76',
        '774.321.431-10',
    )

    goodOnlyNumbersValues = (
        '28866682730',
        '59792311025',
        '98110895409',
        '17468741476',
        '77432143110',
    )

    badValues = (
        '288.666.827-31',
        '597.923.110-26',
        '981.108.954-00',
        '174.687.414-77',
        '774.321.431-11',
    )

    badOnlyNumbersValues = (
        '28866682731',
        '59792311026',
        '98110895400',
        '17468741477',
        '77432143111',
    )


    def test_good_values(self):
        '''testa os valores validos'''
        for cpf in self.goodValues:
            result = CPF(cpf).isValid()
            self.assertEqual(result, True)


    def test_good_only_numbers_values(self):
        '''testa os valores validos para somente numeros'''
        for cpf in self.goodOnlyNumbersValues:
            result = CPF(cpf).isValid()
            self.assertEqual(result, True)


    def test_bad_values(self):
        '''testa os valores invalidos'''
        for cpf in self.badValues:
            result = CPF(cpf).isValid()
            self.assertEqual(result, False)


    def test_bad_only_numbers_values(self):
        '''testa os valores invalidos para somente numeros'''
        for cpf in self.badOnlyNumbersValues:
            result = CPF(cpf).isValid()
            self.assertEqual(result, False)


    def test_empty_value(self):
        '''testa cpf vazio '''
        result = CPF('').isValid()
        self.assertEqual(result, False)


    def test_alpha_value(self):
        '''testa cpf com letras'''
        result = CPF('111.ABC').isValid()
        self.assertEqual(result, False)


    def test_special_character_value(self):
        '''testa cpf com letras'''
        result = CPF('!@#$%&*()-_=+[]|"?><;:').isValid()
        self.assertEqual(result, False)


    def test_long_string_value(self):
        '''testa cpf com letras'''
        result = CPF('123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890').isValid()
        self.assertEqual(result, False)
