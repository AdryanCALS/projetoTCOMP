import unittest
from src.models import TokenType, Token, LexicalError
from src.lexer import Lexer


class TestLexer(unittest.TestCase):
    def test_empty_string_returns_eof_token(self):
        tokens = Lexer.tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
        self.assertEqual(tokens[0].value, "")
        self.assertEqual(tokens[0].line, 1)

    def test_open_and_close_tags(self):
        source = "<usuarios></usuarios>"
        tokens = Lexer.tokenize(source)
        expected = [
            Token(type=TokenType.TAG_OPEN, value="usuarios", line=1, raw_line=source),
            Token(type=TokenType.TAG_CLOSE, value="usuarios", line=1, raw_line=source),
            Token(type=TokenType.EOF, value="", line=1, raw_line=source),
        ]
        self.assertEqual(tokens, expected)

    def test_literals_with_spaces_and_numbers(self):
        source = "<nome>Carlos Silva</nome><idade>34</idade>"
        tokens = Lexer.tokenize(source)
        self.assertEqual(tokens[0], Token(TokenType.TAG_OPEN, "nome", 1, source))
        self.assertEqual(tokens[1], Token(TokenType.LITERAL, "Carlos Silva", 1, source))
        self.assertEqual(tokens[2], Token(TokenType.TAG_CLOSE, "nome", 1, source))
        self.assertEqual(tokens[3], Token(TokenType.TAG_OPEN, "idade", 1, source))
        self.assertEqual(tokens[4], Token(TokenType.LITERAL, "34", 1, source))
        self.assertEqual(tokens[5], Token(TokenType.TAG_CLOSE, "idade", 1, source))
        self.assertEqual(tokens[6], Token(TokenType.EOF, "", 1, source))

    def test_multiline_line_number_and_raw_line_tracking(self):
        source = "<usuarios>\n<usuario><id>101</id></usuario>\n</usuarios>"
        tokens = Lexer.tokenize(source)

        # Linha 1: <usuarios>
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].raw_line, "<usuarios>")
        self.assertEqual(tokens[0].value, "usuarios")

        # Linha 2: <usuario><id>101</id></usuario>
        line2_str = "<usuario><id>101</id></usuario>"
        self.assertEqual(tokens[1].line, 2)
        self.assertEqual(tokens[1].raw_line, line2_str)
        self.assertEqual(tokens[1].value, "usuario")

        self.assertEqual(tokens[2].line, 2)
        self.assertEqual(tokens[2].raw_line, line2_str)
        self.assertEqual(tokens[2].value, "id")

        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].raw_line, line2_str)
        self.assertEqual(tokens[3].value, "101")

        # Linha 3: </usuarios>
        self.assertEqual(tokens[6].line, 3)
        self.assertEqual(tokens[6].raw_line, "</usuarios>")
        self.assertEqual(tokens[6].value, "usuarios")

    def test_unclosed_tag_raises_lexical_error(self):
        source = "<usuarios\n<usuario>"
        with self.assertRaises(LexicalError) as ctx:
            Lexer.tokenize(source)
        self.assertIn("Tag não finalizada", str(ctx.exception))

    def test_full_valid_xml_from_assignment_pdf(self):
        source = (
            "<usuarios>\n"
            "<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</idade></usuario>\n"
            "<usuario><id>102</id><nome>Ana Souza</nome><idade>28</idade></usuario>\n"
            "</usuarios>"
        )
        tokens = Lexer.tokenize(source)
        # Deve ter todos os tokens sem erros
        self.assertEqual(tokens[0].type, TokenType.TAG_OPEN)
        self.assertEqual(tokens[0].value, "usuarios")
        self.assertEqual(tokens[-1].type, TokenType.EOF)

        # Verificar se os literais foram extraídos intactos
        literals = [t.value for t in tokens if t.type == TokenType.LITERAL]
        self.assertEqual(literals, ["101", "Carlos Silva", "34", "102", "Ana Souza", "28"])


if __name__ == "__main__":
    unittest.main()
