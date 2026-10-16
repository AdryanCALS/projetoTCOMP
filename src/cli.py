import sys
from pathlib import Path
from src.types_validator import validate_user_types

from src.lexer import Lexer
from src.parser import Parser
from src.models import (
    TypeValidationError,
    LexicalError,
    SyntacticError,
    StructuralValidationError,
)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("Uso: python -m src.cli <caminho_arquivo.xml>")
        return 1

    file_path = Path(argv[0])

    try:
        source_code = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print("Erro: Arquivo xml vazio")
        return 1

    if not source_code.strip():
        print("Erro: Arquivo xml vazio")
        return 1

    try:
        tokens = Lexer.tokenize(source_code)
        users = Parser.parse(tokens)

        for user in users:
            validate_user_types(user)

    except TypeValidationError as error:
        print(error.format())
        return 1

    except LexicalError as error:
        print(f"Erro léxico: {error.message}")
        return 1

    except SyntacticError as error:
        print(error.format())
        return 1

    except StructuralValidationError as error:
        print(error.format())
        return 1

    print("Estrutura XML válida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())