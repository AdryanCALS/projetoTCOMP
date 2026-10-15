import shutil
import subprocess
import sys
from pathlib import Path

ISSUES = [
    {
        "title": "feat(lexer): Implementação do Analisador Léxico e Classificação de Tokens (Cap. 1 - Sipser)",
        "label": "ready-for-human",
        "body": """### Objetivo
Implementar o Analisador Léxico responsável por transformar a sequência de caracteres brutos do arquivo XML em um fluxo de tokens tipados com preservação de número de linha e contexto textual.

### Fundamentação Teórica (Sipser - Cap. 1)
- Modelagem de expressões regulares e Autômatos Finitos Determinísticos para reconhecimento dos padrões léxicos:
  - Tags de abertura: `<usuarios>`, `<usuario>`, `<id>`, `<nome>`, `<idade>`
  - Tags de fechamento: `</usuarios>`, `</usuario>`, `</id>`, `</nome>`, `</idade>`
  - Conteúdo literal entre tags: strings alfanuméricas e espaços.
  - Ignorar espaços em branco e quebras de linha fora das tags.

### Entregáveis
1. `src/models.py`: Enum `TokenType` e dataclass `Token(type, value, line, raw_line)`.
2. `src/lexer.py`: Classe `Lexer` com método `tokenize(source: str) -> list[Token]`.
3. `tests/test_lexer.py`: Testes unitários com casos válidos e inválidos.

**Branch sugerida**: `feature/lexer`
""",
    },
    {
        "title": "feat(parser): Implementação do Analisador Sintático via Autômato com Pilha (Cap. 2 - Sipser)",
        "label": "ready-for-human",
        "body": """### Objetivo
Implementar o Analisador Sintático que consome a lista de tokens e valida a hierarquia estrutural e o fechamento correto das tags através de um Autômato com Pilha (PDA / Pushdown Automaton).

### Fundamentação Teórica (Sipser - Cap. 2)
- Casamento de tags XML resolvido formalmente por um Autômato com Pilha (PDA):
  - Ao encontrar `<tag>`, empilha (`push`).
  - Ao encontrar `</tag>`, desempilha e compara o topo da pilha (`pop`).
  - Pilha deve conter apenas elementos correspondentes e estar vazia ao término da raiz.

### Entregáveis
1. `src/parser.py`: Classe `Parser` validando:
   - Raiz `<usuarios>`: erro `Erro sintático: Elemento <usuarios> não foi aberto.` se ausente.
   - Blocos `<usuario>`: deve conter na ordem exata `<id>`, `<nome>`, `<idade>`.
   - Se a estrutura estiver incorreta: `Erro de validação na linha X: Estrutura inválida em <bloco>.`
2. `tests/test_parser.py`: Testes com múltiplos usuários e validação de erros sintáticos.

**Branch sugerida**: `feature/parser`
""",
    },
    {
        "title": "feat(types): Implementação do Validador de Tipos de Dados via AFDs (Cap. 1 - Sipser)",
        "label": "ready-for-human",
        "body": """### Objetivo
Implementar o Validador de Tipos que verifica se os conteúdos atômicos das tags folha (`id`, `nome`, `idade`) obedecem estritamente às regras de tipos especificadas no enunciado, através de Autômatos Finitos Determinísticos dedicados.

### Fundamentação Teórica (Sipser - Cap. 1)
- Cada tipo é modelado como um AFD formal $M = (Q, \\Sigma, \\delta, q_0, F)$:
  - **AFD de Inteiros** (`id`, `idade`): Aceita somente sequências de dígitos `[0-9]+` (sem decimais, sem sinais, sem letras).
  - **AFD de Texto** (`nome`): Aceita caracteres alfabéticos (incluindo acentuados latinos) e espaços em branco. Rejeita números.

### Entregáveis
1. `src/types_validator.py`: Validação de `id`, `nome`, `idade` via transições formais de estados dos AFDs.
   - Se rejeitado: `Erro de validação na linha X: Tipo de dados inválido em <bloco>.`
2. `tests/test_types.py`: Testes unitários com inteiros válidos, inteiros com letras (ex: `10A1`), decimais, nomes válidos e nomes com dígitos.

**Branch sugerida**: `feature/types`
""",
    },
    {
        "title": "feat(cli): Implementação da CLI, Orquestrador, Formatação de Erros e Suíte de Testes Integrada",
        "label": "ready-for-human",
        "body": """### Objetivo
Implementar o ponto de entrada da aplicação por linha de comando (CLI), orquestrando o pipeline de execução completa (Léxico -> Sintático -> Tipos), tratando o caso de arquivo vazio e garantindo conformidade estrita com o padrão de saída do PDF.

### Requisitos
1. `src/cli.py`:
   - Argumento: `python -m src.cli <caminho_arquivo.xml>`.
   - Tratamento de arquivo vazio ou com espaços em branco: `Erro: Arquivo xml vazio` com código de saída 1.
   - Orquestração: `Lexer -> Parser -> TypeValidator`.
   - Formatação das mensagens exatas do PDF para cada exceção.
   - Código de saída 0 para sucesso, 1 para erro.
2. `tests/test_cli_integration.py`:
   - Teste de integração do arquivo válido do PDF.
   - Testes cobrindo todos os 4 exemplos de erro do PDF.

**Branch sugerida**: `feature/cli`
""",
    },
]


def find_gh_cli():
    gh = shutil.which("gh")
    if gh:
        return gh
    default_win_path = Path("C:/Program Files/GitHub CLI/gh.exe")
    if default_win_path.exists():
        return str(default_win_path)
    return None


def main():
    gh = find_gh_cli()
    if not gh:
        print("Erro: 'gh' CLI não encontrada no sistema.")
        sys.exit(1)

    print(f"Usando GitHub CLI em: {gh}")

    for idx, issue in enumerate(ISSUES, start=1):
        print(f"[{idx}/4] Criando issue: {issue['title']}...")
        cmd = [
            gh,
            "issue",
            "create",
            "--title",
            issue["title"],
            "--body",
            issue["body"],
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f" -> Sucesso: {res.stdout.strip()}")
        else:
            print(f" -> Falha ao criar issue: {res.stderr.strip()}")
            if "not logged in" in res.stderr.lower() or "auth" in res.stderr.lower():
                print("\nPor favor, autentique a CLI do GitHub executando primeiro:")
                print("  gh auth login")
                break


if __name__ == "__main__":
    main()
