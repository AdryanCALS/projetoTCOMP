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
