Backend de embeddings: `intfloat/multilingual-e5-small` — 30 perguntas.

- Filtros inferidos corretamente: **30/30**
- Relevância@k por termos (média, perguntas no escopo): **0.779**
- Aceitar/recusar com o limiar atual (0.875): **100%** de acerto
- Limiar sugerido: **0.875** (100% de acerto) — menor suporte no escopo: 0.875, maior suporte fora do escopo: 0.874

| Pergunta | No escopo | Filtros ok | Relevância@k | Sim. máx. | Sim. suporte |
|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | sim | ✓ | 0.42 | 0.966 | 0.96 |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | sim | ✓ | 0.58 | 0.925 | 0.919 |
| O que os clientes mais elogiam em suas experiências de compra? | sim | ✓ | 1.00 | 0.968 | 0.959 |
| Quais problemas são relatados por clientes insatisfeitos? | sim | ✓ | 0.50 | 0.966 | 0.959 |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | sim | ✓ | 1.00 | 0.949 | 0.941 |
| O que os clientes relatam sobre problemas relacionados à entrega? | sim | ✓ | 0.83 | 0.919 | 0.912 |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | sim | ✓ | 0.33 | 0.926 | 0.919 |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | sim | ✓ | 0.50 | 0.966 | 0.959 |
| O que os clientes mais elogiam na categoria beleza e saúde? | sim | ✓ | 1.00 | 0.968 | 0.948 |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | sim | ✓ | 0.83 | 0.879 | 0.877 |
| Clientes reclamam de produto recebido com defeito ou quebrado? | sim | ✓ | 0.92 | 0.913 | 0.911 |
| Há relatos de clientes que receberam um produto diferente do que compraram? | sim | ✓ | 1.00 | 0.939 | 0.937 |
| Como os clientes avaliam o atendimento quando têm um problema? | sim | ✓ | 0.92 | 0.904 | 0.895 |
| Os clientes reclamam de pedidos que chegaram incompletos? | sim | ✓ | 0.58 | 0.916 | 0.904 |
| Os clientes reclamam do aplicativo de celular da loja? | sim | ✓ | 0.50 | 0.899 | 0.896 |
| Quais dificuldades os clientes relatam ao pedir troca ou devolução? | sim | ✓ | 1.00 | 0.934 | 0.922 |
| Os clientes relatam problemas com reembolso ou estorno? | sim | ✓ | 1.00 | 0.884 | 0.875 |
| O que os clientes dizem sobre a embalagem dos produtos? | sim | ✓ | 0.83 | 0.918 | 0.914 |
| Há reclamações sobre cobrança indevida ou pedido cancelado sem aviso? | sim | ✓ | 1.00 | 0.884 | 0.883 |
| Quais elogios os clientes fazem aos produtos de cama, mesa e banho? | sim | ✓ | 0.83 | 0.915 | 0.907 |
| Qual é a capital da França? | não | ✓ | — | 0.819 | 0.812 |
| Explique como funciona a fotossíntese. | não | ✓ | — | 0.867 | 0.86 |
| Escreva um código em Python para ordenar uma lista. | não | ✓ | — | 0.87 | 0.867 |
| Quem ganhou a Copa do Mundo de 2002? | não | ✓ | — | 0.873 | 0.864 |
| Qual a previsão do tempo para amanhã em São Paulo? | não | ✓ | — | 0.877 | 0.869 |
| Qual foi a cotação do dólar ontem? | não | ✓ | — | 0.869 | 0.866 |
| Me dê uma receita de bolo de cenoura. | não | ✓ | — | 0.879 | 0.874 |
| Quais os sintomas da dengue? | não | ✓ | — | 0.866 | 0.864 |
| Como declarar o imposto de renda? | não | ✓ | — | 0.864 | 0.861 |
| Quem é o presidente dos Estados Unidos? | não | ✓ | — | 0.837 | 0.832 |

Ponta a ponta — geração: `openai_compat`, limiar 0.875
Decisão correta (responder x recusar): **32/34**

| Pergunta | Esperado | Obtido | Etapa da recusa | Citações | Correto |
|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | responder | responder | — | 12 | ✓ |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | responder | responder | — | 9 | ✓ |
| O que os clientes mais elogiam em suas experiências de compra? | responder | responder | — | 12 | ✓ |
| Quais problemas são relatados por clientes insatisfeitos? | responder | responder | — | 12 | ✓ |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | responder | responder | — | 12 | ✓ |
| O que os clientes relatam sobre problemas relacionados à entrega? | responder | responder | — | 11 | ✓ |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | responder | responder | — | 11 | ✓ |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | responder | responder | — | 12 | ✓ |
| O que os clientes mais elogiam na categoria beleza e saúde? | responder | responder | — | 12 | ✓ |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | responder | responder | — | 7 | ✓ |
| Clientes reclamam de produto recebido com defeito ou quebrado? | responder | responder | — | 12 | ✓ |
| Há relatos de clientes que receberam um produto diferente do que compraram? | responder | responder | — | 2 | ✓ |
| Como os clientes avaliam o atendimento quando têm um problema? | responder | recusar | geracao | 0 | ✗ |
| Os clientes reclamam de pedidos que chegaram incompletos? | responder | responder | — | 11 | ✓ |
| Os clientes reclamam do aplicativo de celular da loja? | responder | responder | — | 1 | ✓ |
| Quais dificuldades os clientes relatam ao pedir troca ou devolução? | responder | responder | — | 10 | ✓ |
| Os clientes relatam problemas com reembolso ou estorno? | responder | recusar | recuperacao | 0 | ✗ |
| O que os clientes dizem sobre a embalagem dos produtos? | responder | responder | — | 10 | ✓ |
| Há reclamações sobre cobrança indevida ou pedido cancelado sem aviso? | responder | responder | — | 9 | ✓ |
| Quais elogios os clientes fazem aos produtos de cama, mesa e banho? | responder | responder | — | 12 | ✓ |
| Qual é a capital da França? | recusar | recusar | recuperacao | 0 | ✓ |
| Explique como funciona a fotossíntese. | recusar | recusar | recuperacao | 0 | ✓ |
| Escreva um código em Python para ordenar uma lista. | recusar | recusar | recuperacao | 0 | ✓ |
| Quem ganhou a Copa do Mundo de 2002? | recusar | recusar | recuperacao | 0 | ✓ |
| Qual a previsão do tempo para amanhã em São Paulo? | recusar | recusar | recuperacao | 0 | ✓ |
| Qual foi a cotação do dólar ontem? | recusar | recusar | recuperacao | 0 | ✓ |
| Me dê uma receita de bolo de cenoura. | recusar | recusar | recuperacao | 0 | ✓ |
| Quais os sintomas da dengue? | recusar | recusar | recuperacao | 0 | ✓ |
| Como declarar o imposto de renda? | recusar | recusar | recuperacao | 0 | ✓ |
| Quem é o presidente dos Estados Unidos? | recusar | recusar | recuperacao | 0 | ✓ |
| O que os clientes acham do tempo de bateria do iPhone 15? | recusar | recusar | recuperacao | 0 | ✓ |
| Qual foi o faturamento total da empresa em 2018? | recusar | recusar | geracao | 0 | ✓ |
| Os clientes conseguiram pagar com Pix? | recusar | recusar | recuperacao | 0 | ✓ |
| O que os clientes acham do programa de cashback? | recusar | recusar | recuperacao | 0 | ✓ |
