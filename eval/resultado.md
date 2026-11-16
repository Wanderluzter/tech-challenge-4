Backend de embeddings: `lsa-tfidf-char-svd256` — 22 perguntas.

- Filtros inferidos corretamente: **22/22**
- Relevância@k por termos (média, perguntas no escopo): **0.738**
- Aceitar/recusar com o limiar atual (0.51): **86%** de acerto
- Limiar sugerido: **0.51** (86% de acerto) — menor suporte no escopo: 0.51, maior suporte fora do escopo: 0.793

| Pergunta | No escopo | Filtros ok | Relevância@k | Sim. máx. | Sim. suporte |
|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | sim | ✓ | 0.75 | 0.991 | 0.873 |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | sim | ✓ | 0.58 | 0.619 | 0.601 |
| O que os clientes mais elogiam em suas experiências de compra? | sim | ✓ | 1.00 | 1.0 | 1.0 |
| Quais problemas são relatados por clientes insatisfeitos? | sim | ✓ | 0.67 | 0.991 | 0.873 |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | sim | ✓ | 1.00 | 0.99 | 0.862 |
| O que os clientes relatam sobre problemas relacionados à entrega? | sim | ✓ | 0.83 | 0.953 | 0.798 |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | sim | ✓ | 0.00 | 0.894 | 0.748 |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | sim | ✓ | 0.67 | 0.991 | 0.873 |
| O que os clientes mais elogiam na categoria beleza e saúde? | sim | ✓ | 1.00 | 1.0 | 0.998 |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | sim | ✓ | 0.75 | 0.709 | 0.51 |
| Clientes reclamam de produto recebido com defeito ou quebrado? | sim | ✓ | 0.92 | 0.754 | 0.609 |
| Há relatos de clientes que receberam um produto diferente do que compraram? | sim | ✓ | 1.00 | 0.748 | 0.715 |
| Como os clientes avaliam o atendimento quando têm um problema? | sim | ✓ | 0.83 | 0.695 | 0.652 |
| Os clientes reclamam de pedidos que chegaram incompletos? | sim | ✓ | 0.33 | 0.714 | 0.678 |
| Qual é a capital da França? | não | ✓ | — | 0.596 | 0.502 |
| Explique como funciona a fotossíntese. | não | ✓ | — | 0.837 | 0.793 |
| Escreva um código em Python para ordenar uma lista. | não | ✓ | — | 0.52 | 0.466 |
| Quem ganhou a Copa do Mundo de 2002? | não | ✓ | — | 0.622 | 0.553 |
| Qual a previsão do tempo para amanhã em São Paulo? | não | ✓ | — | 0.735 | 0.678 |
| Qual foi a cotação do dólar ontem? | não | ✓ | — | 0.615 | 0.505 |
| Me dê uma receita de bolo de cenoura. | não | ✓ | — | 0.538 | 0.49 |
| Quais os sintomas da dengue? | não | ✓ | — | 0.467 | 0.439 |

Ponta a ponta — geração: `extractive`, limiar 0.51
Decisão correta (responder x recusar): **18/25**

| Pergunta | Esperado | Obtido | Etapa da recusa | Citações | Correto |
|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | responder | responder | — | 12 | ✓ |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | responder | responder | — | 8 | ✓ |
| O que os clientes mais elogiam em suas experiências de compra? | responder | responder | — | 12 | ✓ |
| Quais problemas são relatados por clientes insatisfeitos? | responder | responder | — | 12 | ✓ |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | responder | responder | — | 9 | ✓ |
| O que os clientes relatam sobre problemas relacionados à entrega? | responder | responder | — | 8 | ✓ |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | responder | responder | — | 8 | ✓ |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | responder | responder | — | 12 | ✓ |
| O que os clientes mais elogiam na categoria beleza e saúde? | responder | responder | — | 12 | ✓ |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | responder | recusar | recuperacao | 0 | ✗ |
| Clientes reclamam de produto recebido com defeito ou quebrado? | responder | responder | — | 12 | ✓ |
| Há relatos de clientes que receberam um produto diferente do que compraram? | responder | responder | — | 10 | ✓ |
| Como os clientes avaliam o atendimento quando têm um problema? | responder | responder | — | 11 | ✓ |
| Os clientes reclamam de pedidos que chegaram incompletos? | responder | responder | — | 12 | ✓ |
| Qual é a capital da França? | recusar | recusar | recuperacao | 0 | ✓ |
| Explique como funciona a fotossíntese. | recusar | responder | — | 11 | ✗ |
| Escreva um código em Python para ordenar uma lista. | recusar | recusar | recuperacao | 0 | ✓ |
| Quem ganhou a Copa do Mundo de 2002? | recusar | responder | — | 7 | ✗ |
| Qual a previsão do tempo para amanhã em São Paulo? | recusar | responder | — | 6 | ✗ |
| Qual foi a cotação do dólar ontem? | recusar | recusar | recuperacao | 0 | ✓ |
| Me dê uma receita de bolo de cenoura. | recusar | recusar | recuperacao | 0 | ✓ |
| Quais os sintomas da dengue? | recusar | recusar | recuperacao | 0 | ✓ |
| O que os clientes acham do tempo de bateria do iPhone 15? | recusar | responder | — | 5 | ✗ |
| Qual foi o faturamento total da empresa em 2018? | recusar | responder | — | 6 | ✗ |
| Os clientes reclamam do aplicativo de celular da loja? | recusar | responder | — | 5 | ✗ |
