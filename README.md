# Validador de Estrutura XML Plana
> **Projeto Prático da Disciplina de Teoria da Computação**  
> **Grupo 01** | Livro-texto: *Introdução à Teoria da Computação (Michael Sipser, 2ª Edição)*

---

## 1. Visão Geral do Projeto

Este projeto consiste na implementação de um validador de documentos XML planos destinados ao cadastro de usuários. O objetivo central é aliar os conceitos formais estudados na disciplina de Teoria da Computação à construção de um software robusto, modular e com diagnóstico preciso de erros.

O validador assegura que:
1. O elemento raiz `<usuarios>` abra e feche corretamente.
2. Cada bloco `<usuario>` abra e feche corretamente e contenha exatamente as tags filhas `<id>`, `<nome>` e `<idade>` nessa ordem.
3. Cada dado interno respeite as restrições de tipos:
   - `id` e `idade`: inteiros sem casas decimais (apenas dígitos `[0-9]+`).
   - `nome`: exclusivamente texto (caracteres alfabéticos e espaços).

---

## 2. Fundamentação Teórica e Decisão Arquitetural (Sipser, 2ª Edição)

### A Natureza Formal do Problema

No estudo de linguagens formais, documentos com aninhamento arbitrário de delimitadores (como tags `<tag>` e `</tag>` em XML ou parênteses balanceados) geram linguagens do tipo $L = \{ w c w^R \mid w \in \Sigma^* \}$, que comprovadamente **não são regulares** pelo Lema do Bombeamento para Linguagens Regulares (*Sipser, Teorema 1.70*). Elas pertencem à classe das **Linguagens Livres de Contexto (LLC)** e requerem **Autômatos com Pilha (PDA)** (*Sipser, Capítulo 2*).

Entretanto, este trabalho trata de um **XML plano**, cuja profundidade de aninhamento é estritamente finita e limitada:
$$\text{Raiz } \langle\text{usuarios}\rangle \longrightarrow \text{Nó } \langle\text{usuario}\rangle \longrightarrow \text{Folhas } \langle\text{id}\rangle, \langle\text{nome}\rangle, \langle\text{idade}\rangle$$

Como a profundidade é limitada a uma constante fixa, a linguagem formalmente pertence à classe das **Linguagens Regulares** (*Sipser, Capítulo 1*), podendo, em teoria, ser reconhecida por um único Autômato Finito Determinístico (AFD) ou Expressão Regular extensa.

### Decisão Arquitetural: Pipeline Híbrido (ADR 0001)

Optamos deliberadamente por **não** utilizar uma expressão regular única ou um AFD monolítico. Em vez disso, adotamos um **pipeline híbrido modular**:

```mermaid
flowchart LR
    A["Arquivo XML"] --> B["Analisador Léxico<br/>(AFD / Sipser Cap. 1)"]
    B --> C["Fluxo de Tokens<br/>(com linhas)"]
    C --> D["Analisador Sintático<br/>(PDA / Sipser Cap. 2)"]
    D --> E["Validador de Tipos<br/>(AFDs / Sipser Cap. 1)"]
    E --> F["Resultado / Erro Formatado"]
```

#### Justificativas da Decisão:
1. **Localização e Diagnóstico Rigoroso de Erros**: Um AFD monolítico apenas rejeitaria a cadeia de forma binária. A decomposição em Léxico + Sintático com Pilha + Validador de Tipos permite emitir com exatidão as mensagens requeridas no enunciado:
   - Erro de raiz: `Erro sintático: Elemento <usuarios> não foi aberto.`
   - Erro de estrutura com contexto: `Erro de validação na linha X: Estrutura inválida em <bloco>.`
   - Erro de tipo com contexto: `Erro de validação na linha X: Tipo de dados inválido em <bloco>.`
2. **Conexão Pedagógica com a Ementa**: Aplica tanto os **Autômatos Finitos (Capítulo 1)** quanto as **Gramáticas Livres de Contexto e Autômatos com Pilha (Capítulo 2)**.
3. **Divisão Equitativa de Trabalho em Equipe**: Permite uma divisão 1:1 perfeitamente balanceada para 4 integrantes.

---

## 3. Formalização Matemática dos Modelos

### 3.1. Gramática Livre de Contexto (GLC)
A sintaxe do documento é descrita pela GLC $G = (V, \Sigma, R, S)$ (*Sipser, Definição 2.2*):
- **Variáveis ($V$)**: $\{ S, \text{Usuarios}, \text{ListaUsuario}, \text{Usuario}, \text{Id}, \text{Nome}, \text{Idade}, \text{ValorInt}, \text{ValorTexto} \}$
- **Símbolos Terminais ($\Sigma$)**: Todos os literais de tags (`<usuarios>`, `</usuarios>`, etc.) e o conjunto de caracteres válidos para os valores.
- **Símbolo Inicial**: $S$
- **Regras de Produção ($R$)**:
  $$S \to \langle\text{usuarios}\rangle \, \text{ListaUsuario} \, \langle/\text{usuarios}\rangle$$
  $$\text{ListaUsuario} \to \text{Usuario} \, \text{ListaUsuario} \mid \varepsilon$$
  $$\text{Usuario} \to \langle\text{usuario}\rangle \, \text{Id} \, \text{Nome} \, \text{Idade} \, \langle/\text{usuario}\rangle$$
  $$\text{Id} \to \langle\text{id}\rangle \, \text{ValorInt} \, \langle/\text{id}\rangle$$
  $$\text{Nome} \to \langle\text{nome}\rangle \, \text{ValorTexto} \, \langle/\text{nome}\rangle$$
  $$\text{Idade} \to \langle\text{idade}\rangle \, \text{ValorInt} \, \langle/\text{idade}\rangle$$

### 3.2. Autômato com Pilha (PDA)
O emparelhamento das tags é validado por um PDA $M = (Q, \Sigma, \Gamma, \delta, q_0, F)$ (*Sipser, Definição 2.13*):
- $\Gamma = \{ \$ , \text{TAG\_USUARIOS}, \text{TAG\_USUARIO}, \text{TAG\_ID}, \text{TAG\_NOME}, \text{TAG\_IDADE} \}$ (alfabeto da pilha, onde $\$$ é o marcador de fundo de pilha).
- **Mecanismo de Transição**:
  - Para qualquer tag de abertura $t \in \{ \text{usuarios}, \text{usuario}, \text{id}, \text{nome}, \text{idade} \}$: executa $\text{push}(t)$.
  - Para qualquer tag de fechamento correspondente $t$: verifica se $\text{topo}(\text{pilha}) == t$. Se sim, executa $\text{pop}()$; se não, rejeita imediatamente por inconsistência sintática.
  - Ao atingir o fim da entrada com $\text{topo} == \$$, a cadeia é aceita sintaticamente.

### 3.3. Autômatos Finitos Determinísticos para Validação de Tipos
Os dados textuais extraídos das folhas são submetidos a AFDs $M = (Q, \Sigma, \delta, q_0, F)$ (*Sipser, Definição 1.5*):

#### AFD de Inteiros (para `id` e `idade`):
- $\Sigma = \{ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' \}$
- $Q = \{ q_0, q_1, q_{erro} \}$ com $F = \{ q_1 \}$
- Função de transição $\delta$:
  $$\delta(q_0, d) = q_1 \quad (\forall d \in \Sigma)$$
  $$\delta(q_1, d) = q_1 \quad (\forall d \in \Sigma)$$
  $$\delta(q, c) = q_{erro} \quad (\text{para qualquer } c \notin \Sigma)$$

#### AFD de Texto (para `nome`):
- $\Sigma = \{ \text{letras maiúsculas/minúsculas, caracteres latinos acentuados e espaço em branco} \}$
- $Q = \{ q_0, q_1, q_{erro} \}$ com $F = \{ q_1 \}$
- Rejeita qualquer dígito numérico ou caractere especial não textual.

---

## 4. Divisão de Trabalho da Equipe (4 Issues no GitHub)

Para garantir que todos os 4 integrantes trabalhem de forma igualitária e sem dependências bloqueantes, o desenvolvimento foi dividido em 4 issues:

| Issue | Responsável | Módulo / Arquivos | Base Teórica |
| :--- | :--- | :--- | :--- |
| **#1 - Analisador Léxico** | Integrante 1 | `src/models.py`<br/>`src/lexer.py`<br/>`tests/test_lexer.py` | Sipser Cap. 1: Expressões Regulares e Tokens |
| **#2 - Analisador Sintático** | Integrante 2 | `src/parser.py`<br/>`tests/test_parser.py` | Sipser Cap. 2: Autômato com Pilha e GLCs |
| **#3 - Validador de Tipos** | Integrante 3 | `src/types_validator.py`<br/>`tests/test_types.py` | Sipser Cap. 1: Autômatos Finitos Determinísticos |
| **#4 - CLI e Testes Integrados** | Integrante 4 | `src/cli.py`<br/>`tests/test_cli_integration.py` | Integração, tratamento de erros e CLI |

A especificação detalhada de cada issue encontra-se em [docs/issues/ISSUES.md](docs/issues/ISSUES.md).

---

## 5. Estrutura do Repositório

```
Projeto-TCOMP/
├── src/
│   ├── __init__.py
│   ├── models.py           # Dataclass Token, Enums e Exceções customizadas
│   ├── lexer.py            # Analisador Léxico (Integrante 1)
│   ├── parser.py           # Analisador Sintático via PDA (Integrante 2)
│   ├── types_validator.py  # Validador de Tipos de Dados via AFDs (Integrante 3)
│   └── cli.py              # CLI, tratamento de arquivo vazio e erros (Integrante 4)
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_types.py
│   └── test_cli_integration.py
├── documentation/
│   └── Grupo 01 - Tcomp.pdf
├── docs/
│   ├── adr/
│   │   └── 0001-pipeline-hibrido-afd-pda.md
│   └── issues/
│       └── ISSUES.md
├── scripts/
│   └── create_issues.py
├── GLOSSARY.md
└── README.md
```

---

## 6. Como Executar o Projeto e os Testes

### Pré-requisitos
- Python 3.10 ou superior.

### Execução do Validador
```bash
python -m src.cli caminho/para/arquivo.xml
```

### Execução dos Testes Automatizados
```bash
python -m unittest discover -s tests -p "test_*.py"
```
