# Especificação das Issues do Projeto (GitHub)

Este documento contém o detalhamento das 4 issues para distribuição equilibrada entre os 4 integrantes da equipe. Cada issue mapeia diretamente para um componente da arquitetura e para um capítulo do livro-texto (*Sipser, 2ª edição*).

---

## Issue 1 (Integrante 1)
**Título**: `feat(lexer): Implementação do Analisador Léxico e Classificação de Tokens (Cap. 1 - Sipser)`  
**Label recomendada**: `ready-for-human`, `needs-triage`  
**Branch sugerida**: `feature/lexer`  
**Arquivos de responsabilidade**: `src/models.py`, `src/lexer.py`, `tests/test_lexer.py`

### Descrição
Implementar o Analisador Léxico responsável por transformar a sequência de caracteres brutos do arquivo XML em um fluxo de tokens tipados com preservação de número de linha e contexto textual.

### Fundamentação Teórica (Sipser - Cap. 1)
- Modelagem de expressões regulares e Autômatos Finitos Determinísticos para reconhecimento dos padrões léxicos:
  - Tags de abertura: `<usuarios>`, `<usuario>`, `<id>`, `<nome>`, `<idade>`
  - Tags de fechamento: `</usuarios>`, `</usuario>`, `</id>`, `</nome>`, `</idade>`
  - Conteúdo literal entre tags: strings alfanuméricas e espaços.
  - Ignorar espaços em branco e quebras de linha fora das tags.

### Requisitos e Entregáveis
1. Em `src/models.py`, definir:
   - Enum `TokenType`: `TAG_OPEN`, `TAG_CLOSE`, `LITERAL`, `EOF`.
   - Dataclass `Token`:
     ```python
     @dataclass
     class Token:
         type: TokenType
         value: str
         line: int
         raw_line: str
     ```
2. Em `src/lexer.py`, implementar a classe `Lexer`:
   - Método `tokenize(source: str) -> list[Token]`
   - Rastreamento preciso do número da linha (1-indexed).
   - Manutenção do conteúdo original da linha (`raw_line`) para referência nos erros.
3. Em `tests/test_lexer.py`:
   - Teste com XML válido de exemplo do PDF.
   - Teste de tags com espaços intermediários e quebras de linha.

---

## Issue 2 (Integrante 2)
**Título**: `feat(parser): Implementação do Analisador Sintático via Autômato com Pilha (Cap. 2 - Sipser)`  
**Label recomendada**: `ready-for-human`, `needs-triage`  
**Branch sugerida**: `feature/parser`  
**Arquivos de responsabilidade**: `src/parser.py`, `tests/test_parser.py`

### Descrição
Implementar o Analisador Sintático que consome a lista de tokens e valida a hierarquia estrutural e o fechamento correto das tags através de um Autômato com Pilha (PDA / Pushdown Automaton).

### Fundamentação Teórica (Sipser - Cap. 2)
- O casamento de tags XML em linguagens formais é o clássico problema das linguagens livres de contexto do tipo $L = \{ a^n b^n \mid n \ge 0 \}$, resolvido canonicamente por Autômatos com Pilha (PDA):
  - Ao encontrar uma tag de abertura (`<tag>`), ela é empilhada (`push`).
  - Ao encontrar a tag de fechamento correspondente (`</tag>`), o topo da pilha é desempilhado (`pop`).
  - Caso o topo não corresponda ou a pilha esteja vazia/não-vazia ao final, temos um erro sintático/estrutural.

### Requisitos e Entregáveis
1. Em `src/parser.py`, implementar a classe `Parser`:
   - Uso de pilha explícita (`stack: list[str]`).
   - Validação da raiz:
     - Deve abrir obrigatoriamente com `<usuarios>`. Caso contrário, lançar `SyntacticError("Elemento <usuarios> não foi aberto.")`.
     - Deve fechar ao final com `</usuarios>`.
   - Validação de cada bloco `<usuario>`:
     - Deve conter obrigatoriamente e na ordem exata as tags `<id>`, `<nome>`, `<idade>`.
     - Caso o fechamento de alguma tag falhe ou a estrutura esteja incompleta, lançar `StructuralValidationError(line, raw_line, "Estrutura inválida em <trecho>")`.
   - Retornar uma lista de tuplas/objetos de usuários contendo os tokens dos valores para validação de tipos.
2. Em `tests/test_parser.py`:
   - Testes com múltiplos blocos válidos.
   - Teste do erro `Elemento <usuarios> não foi aberto`.
   - Teste do erro do PDF: `<usuario><id>101</id><nome>Carlos Silva</nome><idade>34</usuario>`.

---

## Issue 3 (Integrante 3)
**Título**: `feat(types): Implementação do Validador de Tipos de Dados via AFDs (Cap. 1 - Sipser)`  
**Label recomendada**: `ready-for-human`, `needs-triage`  
**Branch sugerida**: `feature/types`  
**Arquivos de responsabilidade**: `src/types_validator.py`, `tests/test_types.py`

### Descrição
Implementar o Validador de Tipos que verifica se os conteúdos atômicos das tags folha (`id`, `nome`, `idade`) obedecem estritamente às regras de tipos especificadas no enunciado, através de Autômatos Finitos Determinísticos dedicados.

### Fundamentação Teórica (Sipser - Cap. 1)
- Cada regra de tipo é formalizada como um AFD $M = (Q, \Sigma, \delta, q_0, F)$:
  - **AFD de Inteiros (para `id` e `idade`)**:
    - $\Sigma = \{ '0', '1', \dots, '9' \}$
    - $Q = \{ q_0, q_{int}, q_{erro} \}$
    - $\delta(q_0, d) = q_{int}$ para $d \in \Sigma$; $\delta(q_{int}, d) = q_{int}$; qualquer outro caractere transita para $q_{erro}$.
    - $F = \{ q_{int} \}$.
  - **AFD de Texto (para `nome`)**:
    - $\Sigma = \{ \text{letras alfabéticas maiúsculas/minúsculas, caracteres acentuados latinos, espaço em branco} \}$.
    - $Q = \{ q_0, q_{txt}, q_{erro} \}$
    - $F = \{ q_{txt} \}$. Dígitos numéricos e símbolos especiais transitam para $q_{erro}$.

### Requisitos e Entregáveis
1. Em `src/types_validator.py`, implementar:
   - Funções/Classes `validate_integer(value: str) -> bool` e `validate_text(value: str) -> bool` simulando as transições de estado do AFD.
   - Função `validate_user_fields(id_val: str, name_val: str, age_val: str, line: int, raw_line: str)`:
     - Valida `id` e `idade` no AFD de Inteiro.
     - Valida `nome` no AFD de Texto.
     - Caso algum valor seja rejeitado pelo autômato, lançar `DataValidationError(line, raw_line, "Tipo de dados inválido em <bloco>")`.
2. Em `tests/test_types.py`:
   - Teste de aceitação para inteiros válidos (`101`, `34`, `0`).
   - Teste de rejeição para alfanuméricos (`10A1`), números decimais (`34.5`) e negativos (`-10`).
   - Teste de aceitação para nomes em texto com espaços e acentos (`Carlos Silva`, `Ana Souza`).
   - Teste de rejeição para nomes contendo números (`Carlos 2`).

---

## Issue 4 (Integrante 4)
**Título**: `feat(cli): Implementação da CLI, Orquestrador, Formatação de Erros e Suíte de Testes Integrada`  
**Label recomendada**: `ready-for-human`, `needs-triage`  
**Branch sugerida**: `feature/cli`  
**Arquivos de responsabilidade**: `src/cli.py`, `tests/test_cli_integration.py`

### Descrição
Implementar o ponto de entrada da aplicação por linha de comando (CLI), orquestrando o pipeline de execução completa (Léxico -> Sintático -> Tipos), tratando o caso de arquivo vazio e garantindo que as mensagens de saída correspondam perfeitamente aos padrões exigidos pelo enunciado do PDF.

### Requisitos e Entregáveis
1. Em `src/cli.py`, implementar:
   - Suporte a argumento CLI: `python -m src.cli <caminho_arquivo.xml>`.
   - Checagem prévia de arquivo vazio: se o arquivo não existir ou seu conteúdo estiver vazio (apenas espaços em branco), imprimir exatamente:
     ```
     Erro: Arquivo xml vazio
     ```
     e finalizar o processo com código de saída `1`.
   - Execução do pipeline: `source -> Lexer -> Parser -> TypeValidator`.
   - Captura de exceções e formatação rigorosa:
     - `SyntacticError`: `Erro sintático: Elemento <usuarios> não foi aberto.`
     - `StructuralValidationError`: `Erro de validação na linha {line}: Estrutura inválida em {bloco}.`
     - `DataValidationError`: `Erro de validação na linha {line}: Tipo de dados inválido em {bloco}.`
     - Saída com código `1` em caso de erro.
   - Caso o XML seja válido:
     - Imprimir mensagem de confirmação de sucesso e finalizar com código `0`.
2. Em `tests/test_cli_integration.py`:
   - Teste de integração do arquivo válido do PDF.
   - Teste de integração do arquivo vazio.
   - Teste do erro sintático (ausência da tag `<usuarios>`).
   - Teste do erro de validação de estrutura na linha 1.
   - Teste do erro de validação de tipo de dados na linha 2.
