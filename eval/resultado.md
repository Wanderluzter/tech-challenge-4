Backend de embeddings: `intfloat/multilingual-e5-small` — 30 perguntas.

- Filtros inferidos corretamente: **30/30**
- Relevância@k por termos (média, perguntas no escopo): **0.779**
- Corte único que separaria este conjunto: **0.875** (100% de acerto) — menor suporte no escopo: 0.875, maior suporte fora do escopo: 0.874
- Zona cinzenta calibrada: piso **0.865**, limiar de confiança **0.884** — 7 pergunta(s) seguem para o LLM confirmar; erros que o LLM não pode corrigir: **0**

| Pergunta | No escopo | Filtros ok | Relevância@k | Sim. máx. | Sim. suporte | Zona |
|---|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | sim | ✓ | 0.42 | 0.966 | 0.96 | confiante |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | sim | ✓ | 0.58 | 0.925 | 0.919 | confiante |
| O que os clientes mais elogiam em suas experiências de compra? | sim | ✓ | 1.00 | 0.968 | 0.959 | confiante |
| Quais problemas são relatados por clientes insatisfeitos? | sim | ✓ | 0.50 | 0.966 | 0.959 | confiante |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | sim | ✓ | 1.00 | 0.949 | 0.941 | confiante |
| O que os clientes relatam sobre problemas relacionados à entrega? | sim | ✓ | 0.83 | 0.919 | 0.912 | confiante |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | sim | ✓ | 0.33 | 0.926 | 0.919 | confiante |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | sim | ✓ | 0.50 | 0.966 | 0.959 | confiante |
| O que os clientes mais elogiam na categoria beleza e saúde? | sim | ✓ | 1.00 | 0.968 | 0.948 | confiante |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | sim | ✓ | 0.83 | 0.879 | 0.877 | zona cinzenta |
| Clientes reclamam de produto recebido com defeito ou quebrado? | sim | ✓ | 0.92 | 0.913 | 0.911 | confiante |
| Há relatos de clientes que receberam um produto diferente do que compraram? | sim | ✓ | 1.00 | 0.939 | 0.937 | confiante |
| Como os clientes avaliam o atendimento quando têm um problema? | sim | ✓ | 0.92 | 0.904 | 0.895 | confiante |
| Os clientes reclamam de pedidos que chegaram incompletos? | sim | ✓ | 0.58 | 0.916 | 0.904 | confiante |
| Os clientes reclamam do aplicativo de celular da loja? | sim | ✓ | 0.50 | 0.899 | 0.896 | confiante |
| Quais dificuldades os clientes relatam ao pedir troca ou devolução? | sim | ✓ | 1.00 | 0.934 | 0.922 | confiante |
| Os clientes relatam problemas com reembolso ou estorno? | sim | ✓ | 1.00 | 0.884 | 0.875 | zona cinzenta |
| O que os clientes dizem sobre a embalagem dos produtos? | sim | ✓ | 0.83 | 0.918 | 0.914 | confiante |
| Há reclamações sobre cobrança indevida ou pedido cancelado sem aviso? | sim | ✓ | 1.00 | 0.884 | 0.883 | zona cinzenta |
| Quais elogios os clientes fazem aos produtos de cama, mesa e banho? | sim | ✓ | 0.83 | 0.915 | 0.907 | confiante |
| Qual é a capital da França? | não | ✓ | — | 0.819 | 0.812 | recusa direta |
| Explique como funciona a fotossíntese. | não | ✓ | — | 0.867 | 0.86 | recusa direta |
| Escreva um código em Python para ordenar uma lista. | não | ✓ | — | 0.87 | 0.867 | zona cinzenta |
| Quem ganhou a Copa do Mundo de 2002? | não | ✓ | — | 0.873 | 0.864 | recusa direta |
| Qual a previsão do tempo para amanhã em São Paulo? | não | ✓ | — | 0.877 | 0.869 | zona cinzenta |
| Qual foi a cotação do dólar ontem? | não | ✓ | — | 0.869 | 0.866 | zona cinzenta |
| Me dê uma receita de bolo de cenoura. | não | ✓ | — | 0.879 | 0.874 | zona cinzenta |
| Quais os sintomas da dengue? | não | ✓ | — | 0.866 | 0.864 | recusa direta |
| Como declarar o imposto de renda? | não | ✓ | — | 0.864 | 0.861 | recusa direta |
| Quem é o presidente dos Estados Unidos? | não | ✓ | — | 0.837 | 0.832 | recusa direta |

Ponta a ponta — geração: `openai_compat` / `gemini-3-flash-preview`, piso 0.865, limiar de confiança 0.884
Decisão correta (responder x recusar): **34/34**
Perguntas que chegaram ao LLM: 25/34

| Pergunta | Esperado | Obtido | Zona | Etapa da recusa | Citações | Correto |
|---|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes? | responder | responder | confiante | — | 12 | ✓ |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | responder | responder | confiante | — | 12 | ✓ |
| O que os clientes mais elogiam em suas experiências de compra? | responder | responder | confiante | — | 12 | ✓ |
| Quais problemas são relatados por clientes insatisfeitos? | responder | responder | confiante | — | 12 | ✓ |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | responder | responder | confiante | — | 12 | ✓ |
| O que os clientes relatam sobre problemas relacionados à entrega? | responder | responder | confiante | — | 11 | ✓ |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | responder | responder | confiante | — | 12 | ✓ |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | responder | responder | confiante | — | 12 | ✓ |
| O que os clientes mais elogiam na categoria beleza e saúde? | responder | responder | confiante | — | 12 | ✓ |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | responder | responder | zona cinzenta | — | 12 | ✓ |
| Clientes reclamam de produto recebido com defeito ou quebrado? | responder | responder | confiante | — | 11 | ✓ |
| Há relatos de clientes que receberam um produto diferente do que compraram? | responder | responder | confiante | — | 12 | ✓ |
| Como os clientes avaliam o atendimento quando têm um problema? | responder | responder | confiante | — | 10 | ✓ |
| Os clientes reclamam de pedidos que chegaram incompletos? | responder | responder | confiante | — | 9 | ✓ |
| Os clientes reclamam do aplicativo de celular da loja? | responder | responder | confiante | — | 4 | ✓ |
| Quais dificuldades os clientes relatam ao pedir troca ou devolução? | responder | responder | confiante | — | 12 | ✓ |
| Os clientes relatam problemas com reembolso ou estorno? | responder | responder | zona cinzenta | — | 11 | ✓ |
| O que os clientes dizem sobre a embalagem dos produtos? | responder | responder | confiante | — | 10 | ✓ |
| Há reclamações sobre cobrança indevida ou pedido cancelado sem aviso? | responder | responder | zona cinzenta | — | 11 | ✓ |
| Quais elogios os clientes fazem aos produtos de cama, mesa e banho? | responder | responder | confiante | — | 12 | ✓ |
| Qual é a capital da França? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Explique como funciona a fotossíntese. | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Escreva um código em Python para ordenar uma lista. | recusar | recusar | zona cinzenta | geracao | 0 | ✓ |
| Quem ganhou a Copa do Mundo de 2002? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Qual a previsão do tempo para amanhã em São Paulo? | recusar | recusar | zona cinzenta | geracao | 0 | ✓ |
| Qual foi a cotação do dólar ontem? | recusar | recusar | zona cinzenta | geracao | 0 | ✓ |
| Me dê uma receita de bolo de cenoura. | recusar | recusar | zona cinzenta | geracao | 0 | ✓ |
| Quais os sintomas da dengue? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Como declarar o imposto de renda? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Quem é o presidente dos Estados Unidos? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| O que os clientes acham do tempo de bateria do iPhone 15? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| Qual foi o faturamento total da empresa em 2018? | recusar | recusar | zona cinzenta | geracao | 0 | ✓ |
| Os clientes conseguiram pagar com Pix? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
| O que os clientes acham do programa de cashback? | recusar | recusar | recusa direta | recuperacao | 0 | ✓ |
