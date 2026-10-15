from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Categorias léxicas dos tokens no XML plano."""
    TAG_OPEN = auto()
    TAG_CLOSE = auto()
    LITERAL = auto()
    EOF = auto()


@dataclass
class Token:
    """Representação de uma unidade atômica identificada pelo analisador léxico."""
    type: TokenType
    value: str
    line: int
    raw_line: str = ""


class LexicalError(Exception):
    """Exceção levantada quando um padrão léxico inválido é encontrado."""
    def __init__(self, message: str, line: int = 1, raw_line: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.raw_line = raw_line

class SyntacticError(Exception):
    """Erro sintático global (ex.: raiz <usuarios> ausente ou não fechada)."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def format(self) -> str:
        return f"Erro sintático: {self.message}"


class StructuralValidationError(Exception):
    """Erro de estrutura em um bloco (tags fora de ordem, ausentes ou mal fechadas)."""
    def __init__(self, line: int, raw_line: str, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.raw_line = raw_line
        self.message = message

    def format(self) -> str:
        return f"Erro de validação na linha {self.line}: {self.message}."


@dataclass
class UserRecord:
    """Bloco <usuario> aprovado pelo parser, com os tokens de valor para a validação de tipos."""
    id_token: Token
    name_token: Token
    age_token: Token
    line: int
    raw_line: str
