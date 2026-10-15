# Pipeline Híbrido: Léxico (AFD), Sintático (PDA) e Validador de Tipos (AFD)

## Contexto e Decisão

Embora a validação de um documento XML plano com profundidade de aninhamento estritamente limitada ($\le 2$ níveis: raiz `<usuarios>` e filhos `<usuario>`) pertença teoricamente à classe das Linguagens Regulares (podendo ser formalmente reconhecida por um único Autômato Finito Determinístico ou Expressão Regular extensa), decidimos estruturar a arquitetura em um **pipeline híbrido modular**:

1. **Analisador Léxico (AFD / Regex)**: Identifica e classifica unidades mínimas (tags de abertura/fechamento, literais de texto) e mapeia números de linha.
2. **Analisador Sintático com Autômato com Pilha (PDA / GLC)**: Processa os tokens através de transições com pilha explícita para validar o correto emparelhamento e aninhamento das tags (`<usuarios>` e `<usuario>`).
3. **Validador de Tipos (AFDs Específicos)**: Submete os valores folha (`id`, `nome`, `idade`) a autômatos finitos dedicados a validar suas restrições formais de tipos.

## Motivação e Trade-offs

- **Conexão Pedagógica com a Disciplina**: Demonstra a aplicação prática dos dois pilares fundamentais da disciplina baseados no livro-texto (*Sipser, 2ª edição*): **Capítulo 1 (Autômatos Finitos e Linguagens Regulares)** e **Capítulo 2 (Gramáticas Livres de Contexto e Autômatos com Pilha)**.
- **Localização Precisa de Erros**: Um AFD monolítico apenas aceitaria ou rejeitaria a cadeia, sem discriminar se a falha decorreu de uma tag não fechada (`Erro sintático: Elemento <usuarios> não foi aberto`), estrutura violada (`Estrutura inválida na linha X`) ou tipo incorreto (`Tipo de dados inválido na linha X`). O modelo com PDA e validação em camadas atende perfeitamente aos requisitos de mensagens de erro do enunciado.
- **Divisão de Trabalho em Equipe**: Permite decompor o projeto em 4 submódulos independentes, coesos e desacoplados, viabilizando que cada um dos 4 integrantes da equipe desenvolva e teste sua parte com baixo risco de conflito de integração.
