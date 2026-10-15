import unittest

from src.lexer import Lexer
from src.models import StructuralValidationError, SyntacticError
from src.parser import Parser


def parse(source: str):
    return Parser.parse(Lexer.tokenize(source))


VALID_XML = (
    "<usuarios>\n"
    "<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</idade></usuario>\n"
    "<usuario><id>102</id><nome>Ana Souza</nome><idade>28</idade></usuario>\n"
    "</usuarios>"
)


class TestParserValid(unittest.TestCase):
    def test_multiple_valid_users(self):
        users = parse(VALID_XML)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].id_token.value, "101")
        self.assertEqual(users[0].name_token.value, "Carlos Silva")
        self.assertEqual(users[0].age_token.value, "34")
        self.assertEqual(users[1].id_token.value, "102")
        self.assertEqual(users[1].name_token.value, "Ana Souza")
        self.assertEqual(users[1].age_token.value, "28")

    def test_user_records_keep_line_info(self):
        users = parse(VALID_XML)
        self.assertEqual(users[0].line, 2)
        self.assertEqual(users[1].line, 3)
        self.assertEqual(users[1].id_token.line, 3)

    def test_empty_root_has_no_users(self):
        self.assertEqual(parse("<usuarios></usuarios>"), [])

    def test_many_users(self):
        body = "".join(
            f"<usuario><id>{i}</id><nome>Nome</nome><idade>{20 + i}</idade></usuario>\n"
            for i in range(50)
        )
        users = parse(f"<usuarios>\n{body}</usuarios>")
        self.assertEqual(len(users), 50)

    def test_block_spread_over_multiple_lines(self):
        source = (
            "<usuarios>\n<usuario>\n<id>1</id>\n<nome>Ana</nome>\n"
            "<idade>20</idade>\n</usuario>\n</usuarios>"
        )
        users = parse(source)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].age_token.line, 5)

    def test_empty_field_yields_empty_value_token(self):
        users = parse("<usuarios><usuario><id></id><nome>A</nome><idade>1</idade></usuario></usuarios>")
        self.assertEqual(users[0].id_token.value, "")


class TestParserSyntacticErrors(unittest.TestCase):
    def assert_syntactic(self, source, message):
        with self.assertRaises(SyntacticError) as ctx:
            parse(source)
        self.assertEqual(ctx.exception.message, message)
        return ctx.exception

    def test_root_not_opened(self):
        err = self.assert_syntactic(
            "<usuario><id>1</id><nome>A</nome><idade>2</idade></usuario>",
            "Elemento <usuarios> não foi aberto.",
        )
        self.assertEqual(err.format(), "Erro sintático: Elemento <usuarios> não foi aberto.")

    def test_only_eof_tokens(self):
        self.assert_syntactic("", "Elemento <usuarios> não foi aberto.")

    def test_root_not_closed(self):
        self.assert_syntactic(
            "<usuarios><usuario><id>1</id><nome>A</nome><idade>2</idade></usuario>",
            "Elemento <usuarios> não foi fechado.",
        )

    def test_content_after_root_closed(self):
        self.assert_syntactic(
            "<usuarios></usuarios><usuarios></usuarios>",
            "Conteúdo inesperado após o fechamento de </usuarios>.",
        )


class TestParserStructuralErrors(unittest.TestCase):
    def assert_structural(self, source, line):
        with self.assertRaises(StructuralValidationError) as ctx:
            parse(source)
        self.assertEqual(ctx.exception.line, line)
        return ctx.exception

    def test_pdf_example_mismatched_close(self):
        bad = "<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</usuario>"
        err = self.assert_structural(f"<usuarios>\n{bad}\n</usuarios>", 2)
        self.assertEqual(err.raw_line, bad)
        self.assertEqual(err.message, f"Estrutura inválida em {bad}")
        self.assertEqual(
            err.format(), f"Erro de validação na linha 2: Estrutura inválida em {bad}."
        )

    def test_pdf_example_on_line_one(self):
        bad = "<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</usuario>"
        # com a raiz na mesma linha, o erro ocorre na linha 1
        with self.assertRaises(StructuralValidationError) as ctx:
            parse(f"<usuarios>{bad}</usuarios>")
        self.assertEqual(ctx.exception.line, 1)

    def test_fields_out_of_order(self):
        self.assert_structural(
            "<usuarios>\n<usuario><nome>A</nome><id>1</id><idade>2</idade></usuario>\n</usuarios>", 2
        )

    def test_missing_field(self):
        self.assert_structural(
            "<usuarios>\n<usuario><id>1</id><nome>A</nome></usuario>\n</usuarios>", 2
        )

    def test_extra_field(self):
        self.assert_structural(
            "<usuarios>\n<usuario><id>1</id><nome>A</nome><idade>2</idade><x>1</x></usuario>\n</usuarios>", 2
        )

    def test_duplicate_field(self):
        self.assert_structural(
            "<usuarios>\n<usuario><id>1</id><id>2</id><nome>A</nome><idade>2</idade></usuario>\n</usuarios>", 2
        )

    def test_unclosed_field(self):
        self.assert_structural(
            "<usuarios>\n<usuario><id>1<nome>A</nome><idade>2</idade></usuario>\n</usuarios>", 2
        )

    def test_unclosed_block_at_eof_is_not_silently_accepted(self):
        with self.assertRaises(StructuralValidationError):
            parse("<usuarios>\n<usuario><id>1</id>")

    def test_stray_tag_directly_in_root(self):
        self.assert_structural("<usuarios>\n<id>1</id>\n</usuarios>", 2)

    def test_text_directly_in_root(self):
        self.assert_structural("<usuarios>\nlixo\n</usuarios>", 2)

    def test_empty_block(self):
        self.assert_structural("<usuarios>\n<usuario></usuario>\n</usuarios>", 2)

    def test_fail_fast_reports_first_error_only(self):
        source = (
            "<usuarios>\n"
            "<usuario><id>1</id><nome>A</nome><idade>2</usuario>\n"
            "<usuario><nome>B</nome></usuario>\n"
            "</usuarios>"
        )
        self.assert_structural(source, 2)


if __name__ == "__main__":
    unittest.main()
