import unittest
from src.models import Token, TokenType, UserRecord, TypeValidationError
from src.types_validator import afd_inteiro, afd_texto, validate_user_types


class TestTypeValidator(unittest.TestCase):

    def test_afd_inteiro_valido(self):
        self.assertTrue(afd_inteiro.reconhece("101"))
        self.assertTrue(afd_inteiro.reconhece("0"))
        self.assertTrue(afd_inteiro.reconhece("34"))

    def test_afd_inteiro_invalido(self):
        self.assertFalse(afd_inteiro.reconhece("10A1"))   # com letras
        self.assertFalse(afd_inteiro.reconhece("10.5"))   # decimal
        self.assertFalse(afd_inteiro.reconhece("-10"))    # sinal negativo
        self.assertFalse(afd_inteiro.reconhece("+25"))    # sinal positivo
        self.assertFalse(afd_inteiro.reconhece(""))       # vazio

    def test_afd_texto_valido(self):
        self.assertTrue(afd_texto.reconhece("Carlos Silva"))
        self.assertTrue(afd_texto.reconhece("João de Sá"))
        self.assertTrue(afd_texto.reconhece("Érica"))

    def test_afd_texto_invalido(self):
        self.assertFalse(afd_texto.reconhece("Carlos 2")) # com dígitos
        self.assertFalse(afd_texto.reconhece("Ana_Souza"))# caractere especial
        self.assertFalse(afd_texto.reconhece("@Carlos"))
        self.assertFalse(afd_texto.reconhece(""))

    def test_validate_user_types_sucesso(self):
        user = UserRecord(
            id_token=Token(type=TokenType.LITERAL, value="101", line=1),
            name_token=Token(type=TokenType.LITERAL, value="Carlos Silva", line=1),
            age_token=Token(type=TokenType.LITERAL, value="34", line=1),
            line=1,
            raw_line="<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</idade></usuario>"
        )
        self.assertTrue(validate_user_types(user))

    def test_validate_user_types_falha_id(self):
        raw = "<usuario><id>10A1</id><nome>Carlos Silva</nome><idade>34</idade></usuario>"
        user = UserRecord(
            id_token=Token(type=TokenType.LITERAL, value="10A1", line=2),
            name_token=Token(type=TokenType.LITERAL, value="Carlos Silva", line=2),
            age_token=Token(type=TokenType.LITERAL, value="34", line=2),
            line=2,
            raw_line=raw
        )
        with self.assertRaises(TypeValidationError) as ctx:
            validate_user_types(user)
        self.assertEqual(
            ctx.exception.format(),
            f"Erro de validação na linha 2: Tipo de dados inválido em {raw}."
        )


if __name__ == "__main__":
    unittest.main()
    