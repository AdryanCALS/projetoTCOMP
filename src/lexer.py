from src.models import Token, TokenType, LexicalError


class Lexer:
    """Analisador Léxico para o XML plano de usuários (Sipser, Cap. 1)."""

    @classmethod
    def tokenize(cls, source_code: str) -> list[Token]:
        lines = source_code.splitlines(keepends=True)
        if not lines:
            return [Token(type=TokenType.EOF, value="", line=1, raw_line="")]

        tokens: list[Token] = []

        pos = 0
        total_len = len(source_code)

        # Mapeamento de posições para (start_pos, line_num, clean_line)
        line_offsets: list[tuple[int, int, str]] = []
        current_offset = 0
        for idx, line in enumerate(lines, start=1):
            clean_line = line.rstrip("\r\n")
            line_offsets.append((current_offset, idx, clean_line))
            current_offset += len(line)

        def get_line_info(offset: int) -> tuple[int, str]:
            for start, num, text in reversed(line_offsets):
                if offset >= start:
                    return num, text
            return 1, line_offsets[0][2] if line_offsets else ""

        while pos < total_len:
            char = source_code[pos]

            if char in " \t\r\n":
                pos += 1
                continue

            current_line, raw_line = get_line_info(pos)

            if char == "<":
                # Início de tag
                end_tag = source_code.find(">", pos)
                next_open = source_code.find("<", pos + 1)

                if end_tag == -1 or (next_open != -1 and next_open < end_tag) or "\n" in source_code[pos:end_tag]:
                    raise LexicalError(
                        message=f"Tag não finalizada com '>' na linha {current_line}",
                        line=current_line,
                        raw_line=raw_line,
                    )

                tag_content = source_code[pos + 1 : end_tag].strip()
                if not tag_content:
                    raise LexicalError(
                        message=f"Tag vazia encontrada na linha {current_line}",
                        line=current_line,
                        raw_line=raw_line,
                    )

                if tag_content.startswith("/"):
                    tag_name = tag_content[1:].strip()
                    tokens.append(
                        Token(
                            type=TokenType.TAG_CLOSE,
                            value=tag_name,
                            line=current_line,
                            raw_line=raw_line,
                        )
                    )
                else:
                    tag_name = tag_content
                    tokens.append(
                        Token(
                            type=TokenType.TAG_OPEN,
                            value=tag_name,
                            line=current_line,
                            raw_line=raw_line,
                        )
                    )

                pos = end_tag + 1
            else:
                # Conteúdo literal até o próximo '<'
                next_tag = source_code.find("<", pos)
                if next_tag == -1:
                    literal_chunk = source_code[pos:]
                    pos = total_len
                else:
                    literal_chunk = source_code[pos:next_tag]
                    pos = next_tag

                literal_val = literal_chunk.strip()
                if literal_val:
                    tokens.append(
                        Token(
                            type=TokenType.LITERAL,
                            value=literal_val,
                            line=current_line,
                            raw_line=raw_line,
                        )
                    )

        last_line = line_offsets[-1][1] if line_offsets else 1
        last_raw = line_offsets[-1][2] if line_offsets else ""
        tokens.append(Token(type=TokenType.EOF, value="", line=last_line, raw_line=last_raw))
        return tokens
