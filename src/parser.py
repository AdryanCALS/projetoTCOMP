from src.models import (
    StructuralValidationError,
    SyntacticError,
    Token,
    TokenType,
    UserRecord,
)

ROOT_TAG = "usuarios"
BLOCK_TAG = "usuario"
FIELD_ORDER = ("id", "nome", "idade")

# Estados de controle finito do PDA
_START = "START"            # nada lido: espera <usuarios>
_IN_ROOT = "IN_ROOT"        # dentro de <usuarios>, entre blocos
_IN_BLOCK = "IN_BLOCK"      # dentro de <usuario>: espera <campo> ou </usuario>
_AFTER_OPEN = "AFTER_OPEN"  # logo após <campo>: espera valor ou </campo>
_AFTER_VALUE = "AFTER_VALUE"  # após o valor: espera </campo>
_DONE = "DONE"              # </usuarios> lido: só EOF é aceito


class Parser:
    """Analisador Sintático via Autômato com Pilha (Sipser, Cap. 2).

    - <tag>  -> push na pilha
    - </tag> -> pop, comparando com o topo
    A pilha deve ficar vazia ao fim da raiz. Além do casamento, valida que cada
    <usuario> contém exatamente <id>, <nome>, <idade>, nessa ordem (fail-fast).
    """

    @classmethod
    def parse(cls, tokens: list[Token]) -> list[UserRecord]:
        stack: list[str] = []
        users: list[UserRecord] = []
        state = _START

        field_idx = 0
        block_open: Token | None = None
        values: list[Token] = []

        def structural(token: Token) -> StructuralValidationError:
            return StructuralValidationError(
                line=token.line,
                raw_line=token.raw_line,
                message=f"Estrutura inválida em {token.raw_line}",
            )

        def pop_expected(token: Token) -> None:
            """Transição de pop: o topo da pilha deve casar com a tag de fechamento."""
            if not stack or stack[-1] != token.value:
                raise structural(token)
            stack.pop()

        for token in tokens:
            if state == _START:
                if token.type is TokenType.TAG_OPEN and token.value == ROOT_TAG:
                    stack.append(token.value)
                    state = _IN_ROOT
                else:
                    raise SyntacticError("Elemento <usuarios> não foi aberto.")

            elif state == _IN_ROOT:
                if token.type is TokenType.TAG_OPEN and token.value == BLOCK_TAG:
                    stack.append(token.value)
                    block_open = token
                    values = []
                    field_idx = 0
                    state = _IN_BLOCK
                elif token.type is TokenType.TAG_CLOSE and token.value == ROOT_TAG:
                    pop_expected(token)
                    state = _DONE
                elif token.type is TokenType.EOF:
                    raise SyntacticError("Elemento <usuarios> não foi fechado.")
                else:
                    raise structural(token)

            elif state == _IN_BLOCK:
                if (
                    token.type is TokenType.TAG_OPEN
                    and field_idx < len(FIELD_ORDER)
                    and token.value == FIELD_ORDER[field_idx]
                ):
                    stack.append(token.value)
                    state = _AFTER_OPEN
                elif (
                    token.type is TokenType.TAG_CLOSE
                    and token.value == BLOCK_TAG
                    and field_idx == len(FIELD_ORDER)
                ):
                    pop_expected(token)
                    id_t, name_t, age_t = values
                    users.append(
                        UserRecord(
                            id_token=id_t,
                            name_token=name_t,
                            age_token=age_t,
                            line=block_open.line,
                            raw_line=block_open.raw_line,
                        )
                    )
                    state = _IN_ROOT
                else:
                    raise structural(token)

            elif state == _AFTER_OPEN:
                if token.type is TokenType.LITERAL:
                    values.append(token)
                    state = _AFTER_VALUE
                elif token.type is TokenType.TAG_CLOSE and token.value == stack[-1]:
                    # Campo vazio (<id></id>): estruturalmente válido; gera valor
                    # vazio para que o validador de tipos o rejeite.
                    pop_expected(token)
                    values.append(Token(TokenType.LITERAL, "", token.line, token.raw_line))
                    field_idx += 1
                    state = _IN_BLOCK
                else:
                    raise structural(token)

            elif state == _AFTER_VALUE:
                if token.type is TokenType.TAG_CLOSE and token.value == stack[-1]:
                    pop_expected(token)
                    field_idx += 1
                    state = _IN_BLOCK
                else:
                    raise structural(token)

            elif state == _DONE:
                if token.type is not TokenType.EOF:
                    raise SyntacticError("Conteúdo inesperado após o fechamento de </usuarios>.")

        if state == _START:
            raise SyntacticError("Elemento <usuarios> não foi aberto.")
        if state != _DONE:
            raise SyntacticError("Elemento <usuarios> não foi fechado.")

        assert not stack  # pilha vazia ao término da raiz
        return users
