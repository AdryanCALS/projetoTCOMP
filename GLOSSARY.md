# Validador de Estrutura XML Plana

Contexto de validação formal de arquivos XML para cadastros de usuários baseado nos modelos de Teoria da Computação (Sipser, 2ª edição).

## Language

**Elemento Raiz**:
O elemento `<usuarios>` que encapsula todo o conteúdo do documento XML, devendo ser o primeiro a abrir e o último a fechar.
_Avoid_: Tag pai, tag principal, container global

**Bloco de Usuário**:
O elemento `<usuario>` que representa uma única entidade cadastral, contendo obrigatoriamente as tags filhas `id`, `nome` e `idade` nesta ordem exata.
_Avoid_: Registro, linha de usuário, item

**Analisador Léxico**:
O componente responsável por processar o fluxo de caracteres de entrada e produzir uma sequência de tokens tipados, preservando o número da linha de origem.
_Avoid_: Scanner, tokenizer genérico

**Analisador Sintático**:
O componente que consome os tokens gerados e valida a hierarquia e o balanceamento de abertura e fechamento de tags por meio de um autômato com pilha.
_Avoid_: Validador estrutural, parser genérico

**Validador de Tipos**:
O componente que inspeciona o conteúdo textual dos nós folha (`id`, `nome`, `idade`) aplicando autômatos finitos determinísticos para garantir os tipos de dados exigidos.
_Avoid_: Validador semântico

**Autômato com Pilha**:
Modelo formal de computação dotado de uma pilha (LIFO) utilizado para reconhecer a linguagem livre de contexto que descreve o casamento de tags do XML.
_Avoid_: Máquina de pilha, stack parser

**Token**:
Objeto atômico gerado pelo analisador léxico que encapsula a categoria sintática, o valor textual extraído, o número da linha no arquivo fonte e o conteúdo original da linha.
_Avoid_: Lexema bruto, pedaço de texto

**Fail-Fast**:
Regra de interrupção imediata do fluxo de validação no momento em que a primeira violação formal (léxica, sintática ou de tipo) é detectada.
_Avoid_: Parada precoce, cancelamento

