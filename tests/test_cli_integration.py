
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src.cli import main


class TestCLIIntegration(unittest.TestCase):
    def run_cli(self, xml_content: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "usuarios.xml"
            file_path.write_text(xml_content, encoding="utf-8")

            output = StringIO()
            with redirect_stdout(output):
                exit_code = main([str(file_path)])

            return exit_code, output.getvalue().strip()

    def test_valid_xml(self):
        xml = (
            "<usuarios>\n"
            "<usuario>\n"
            "<id>1</id>\n"
            "<nome>Ana</nome>\n"
            "<idade>20</idade>\n"
            "</usuario>\n"
            "</usuarios>\n"
        )

        exit_code, output = self.run_cli(xml)

        self.assertEqual(exit_code, 0)
        self.assertIn("válida", output)

    def test_empty_file(self):
        exit_code, output = self.run_cli("")

        self.assertEqual(exit_code, 1)
        self.assertEqual(output, "Erro: Arquivo xml vazio")

    def test_root_not_opened(self):
        xml = "<usuario></usuario>"

        exit_code, output = self.run_cli(xml)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            output,
            "Erro sintático: Elemento <usuarios> não foi aberto.",
        )

    def test_invalid_structure_on_line_one(self):
        xml = (
            "<usuarios><usuario><nome>Ana</nome>"
            "<id>1</id><idade>20</idade></usuario></usuarios>"
        )

        exit_code, output = self.run_cli(xml)

        self.assertEqual(exit_code, 1)
        self.assertIn("Erro de validação na linha 1:", output)

    def test_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nao_existe.xml"

            output = StringIO()
            with redirect_stdout(output):
                exit_code = main([str(file_path)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(
                output.getvalue().strip(),
                "Erro: Arquivo xml vazio",
            )

    def test_invalid_type(self):
        xml = (
            "<usuarios>\n"
            "<usuario>\n"
            "<id>abc</id>\n"
            "<nome>Ana</nome>\n"
            "<idade>20</idade>\n"
            "</usuario>\n"
            "</usuarios>\n"
        )

        exit_code, output = self.run_cli(xml)

        self.assertEqual(exit_code, 1)
        self.assertIn("Erro de validação na linha 2:", output)
        self.assertIn("Tipo de dados inválido", output)



if __name__ == "__main__":
    unittest.main()
