# Exemplos de perguntas e respostas

Gerado por `python -m voc_rag.cli examples` sobre a base real da Olist. Nada aqui foi editado à mão.

- Embeddings: `lsa-tfidf-char-svd256`
- Geração: `extractive` (sem LLM)
- Limiar de similaridade: 0.51

## 1. Quais são os principais problemas relatados pelos clientes?

**Pergunta:** Quais são os principais problemas relatados pelos clientes?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “não recebi o produto, ainda não chegou” | “quero devolver, trocar, cancelar e receber o dinheiro de volta” | “pedido incompleto, veio faltando item, recebi só uma parte” | “entrega atrasada, demorou muito para chegar, fora do prazo” | “produto veio com defeito, quebrado, não funciona”
**Recuperação:** 200 candidatos densos + 200 lexicais → 309 únicos → 198 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.99)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Entrega incompleta / itens faltando [1, 9, 10, 11, 12]
- Produto com defeito ou danificado [4, 6, 8]
- Produto não recebido [2, 9]
- Devolução, troca, cancelamento ou reembolso [3, 7]
- Entrega atrasada / demora [5]

**Avaliações mais relevantes:**
- "Meu pedido veio incompleto. Ficou faltando um item." (nota 1) [1]
- "Ainda NAO recebi o produt. O Produto não chegou." (nota 1) [2]
- "Quero o meu dinheiro de volta , não estou conseguindo cancelar" (nota 1) [3]
- "O relogio não esta funcionando. Nao esta quebrado. Mas nao funciona com a pilha de jeito nenhum. Veio com defeito" (nota 1) [4]
- "Demorou muito para chegar" (nota 3) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `e2151cbbe41614f383562310b6438748` · nota 1 · 2017-11-12 · relogios_presentes · entrega no_prazo · sim 0.87 · citada  
  “Meu pedido veio incompleto. Ficou faltando um item.”
- **[2]** `e6c6d2dd67da56c2d77b24cb73ff2354` · nota 1 · 2018-07-12 · moveis_sala · entrega atrasada · sim 0.99 · citada  
  “Ainda NAO recebi o produt. O Produto não chegou.”
- **[3]** `28ccdb164626d8d580e9070d0913951b` · nota 1 · 2017-04-08 · moveis_decoracao · entrega nao_entregue · sim 0.71 · citada  
  “Quero o meu dinheiro de volta , não estou conseguindo cancelar”
- **[4]** `5daed8162373d5914d7873de82d86355` · nota 1 · 2017-10-22 · relogios_presentes · entrega no_prazo · sim 0.79 · citada  
  “O relogio não esta funcionando. Nao esta quebrado. Mas nao funciona com a pilha de jeito nenhum. Veio com defeito”
- **[5]** `3ee6185e2f5131927f4458b739852daf` · nota 3 · 2017-06-16 · beleza_saude · entrega atrasada · sim 0.78 · citada  
  “Demorou muito para chegar”
- **[6]** `13dcde46c1a250aaed407dd6d5a53b77` · nota 3 · 2018-07-23 · automotivo · entrega no_prazo · sim 0.81 · citada  
  “Produto com defeito. Produto veio quebrado”
- **[7]** `4548534449b1f572e357211b90724f1b` · nota 1 · 2018-09-03 · desconhecida · entrega nao_entregue · sim 0.71 · citada  
  “quero devolver o produto comprei um veio outro;;; quero meu dinheiro de volta.”
- **[8]** `93f72220a2eefce8606c24ba7e121333` · nota 1 · 2018-07-24 · relogios_presentes · entrega no_prazo · sim 0.82 · citada  
  “Produto já veio com defeito não funciona”
- **[9]** `ea367d520c1e07a970c0452a97496afe` · nota 1 · 2017-05-16 · cool_stuff · entrega no_prazo · sim 0.76 · citada  
  “Nao recebi um dos produtos. o pedido veio incompleto!”
- **[10]** `0afdaef42f4cef6492069412f42443d3` · nota 1 · 2018-01-12 · beleza_saude · entrega no_prazo · sim 0.74 · citada  
  “Recebi o produto incompleto, faltou 01 item!”
- **[11]** `d100adcddcef25bfa83bb819d562211c` · nota 2 · 2018-07-01 · utilidades_domesticas · entrega no_prazo · sim 0.82 · citada  
  “Pedido incompleto. Meu pedido chegou faltando um item.”
- **[12]** `f783a6c8d1fdd0a75c2d5501b07afc8e` · nota 2 · 2018-07-11 · utilidades_domesticas · entrega no_prazo · sim 0.69 · citada  
  “Pedido incompleto. Meio pedido veio faltando boa parte das perças. Estou tentando entrar em contato com a loja e nao consigo!”

---

## 2. Quais reclamações relacionadas à entrega aparecem com maior frequência?

**Pergunta:** Quais reclamações relacionadas à entrega aparecem com maior frequência?

**Transformação da pergunta:** texto de busca focado no assunto → “reclamacoes entrega”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 71 únicos → 13 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.62)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Produto não recebido [4, 5, 6, 10]
- Entrega atrasada / demora [4, 5, 6]
- Entrega incompleta / itens faltando [6, 8]
- Produto com defeito ou danificado [3]
- Devolução, troca, cancelamento ou reembolso [10]

**Avaliações mais relevantes:**
- "PRODUTO NÃO VEIO COM O CABO VARIAS RECLAMAÇÕES E NINGUÉM SE MANIFESTOU" (nota 1) [1]
- "Mandei diversas reclamações e somente um foi respondida porém não atendida." (nota 1) [2]
- "Comprei 02 computadores, e um deles veio com defeito. Mesmo abrindo 02 reclamações, nem a baratheon e nem a targaryen sequer responderam as minhas reclamações" (nota 1) [3]
- "Produto não entregue. Tudo muito ruim, não tem ninguém com possamos fazer reclamação pela não entrega do do produto. Não tem ouvidoria, para reclamações. Não tem nenhum pessypar..." (nota 1) [4]
- "O prazo de entrega, pela loja foi até o dia 05/03/2018. Ainda não recebi o produto. Li várias reclamações de atrasos desta loja..quem sabe chega.." (nota 1) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `f9f941e29d04f05cac6605d2fe2bded5` · nota 1 · 2018-03-21 · telefonia · entrega no_prazo · sim 0.56 · citada  
  “PRODUTO NÃO VEIO COM O CABO VARIAS RECLAMAÇÕES E NINGUÉM SE MANIFESTOU”
- **[2]** `89e36888c39685c524a74270824e9fdb` · nota 1 · 2017-07-25 · instrumentos_musicais · entrega nao_entregue · sim 0.54 · citada  
  “Mandei diversas reclamações e somente um foi respondida porém não atendida.”
- **[3]** `601269563463601b0b1b1f09bea7d013` · nota 1 · 2017-12-16 · pcs · entrega no_prazo · sim 0.52 · citada  
  “Comprei 02 computadores, e um deles veio com defeito. Mesmo abrindo 02 reclamações, nem a baratheon e nem a targaryen sequer responderam as minhas reclamações”
- **[4]** `8ff6181cba380f5e072a56e9b2b7d850` · nota 1 · 2018-08-06 · informatica_acessorios · entrega atrasada · sim 0.60 · citada  
  “Produto não entregue. Tudo muito ruim, não tem ninguém com possamos fazer reclamação pela não entrega do do produto. Não tem ouvidoria, para reclamações. Não tem nenhum pessypara informar o por que da demora da entrega.”
- **[5]** `e3c160b9f40b8c16e2e7d5f8ec3d375d` · nota 1 · 2018-01-16 · esporte_lazer · entrega nao_entregue · sim 0.52 · citada  
  “O prazo de entrega, pela loja foi até o dia 05/03/2018. Ainda não recebi o produto. Li várias reclamações de atrasos desta loja..quem sabe chega..”
- **[6]** `9579e23f23d95aa2dd4112876a9f25ca` · nota 1 · 2018-03-14 · beleza_saude · entrega no_prazo · sim 0.55 · citada  
  “Produto não entregue no prazo fiz várias reclamações inclusive no reclama Aki mesmo assim veio faltando dois produtos só recebi ativador de cachos falaram que ainda entregaria essa semana vou aguarda”
- **[7]** `c073a54bbfbbd0282b00f3d50ccdd00f` · nota 1 · 2018-07-10 · telefonia · entrega no_prazo · sim 0.61 · não citada  
  “reclamação. produto incorreto”
- **[8]** `3e5855205340c723730123053cc1171f` · nota 1 · 2017-11-28 · ferramentas_jardim · entrega no_prazo · sim 0.58 · citada  
  “Faltou 2 produtos na entrega, tive de ligar na loja para reclamar.”
- **[9]** `48473f056dbedf83a49b22fb0dd16805` · nota 3 · 2017-12-01 · brinquedos · entrega no_prazo · sim 0.62 · não citada  
  “reclamação. uma das bonecas veio sem chupeta”
- **[10]** `45df9a4e72717bb9df868ad69b732267` · nota 1 · 2018-02-26 · ferramentas_jardim · entrega atrasada · sim 0.53 · citada  
  “A entrega deste produto só foi possível após reclamação e mediação pelo RECLAMEAQUI. lannister tentou desqualificar a compra e devolver "credito" quando a FOCALOUCA desonrou a venda e não entregou o”
- **[11]** `b24256a5bc7d16294b6b9f1965702418` · nota 3 · 2018-03-06 · informatica_acessorios · entrega no_prazo · sim 0.53 · não citada  
  “Os produtos foram entregues em dias diferentes, o que gerou reclamação na entrega do primeiro pacote.”
- **[12]** `91819ee1e79ef33c1bdb10568b37dc71` · nota 3 · 2018-02-10 · esporte_lazer · entrega no_prazo · sim 0.51 · não citada  
  “ATÉ AGORA NÃO TENHO NADA A RECLAMAR”

---

## 3. O que os clientes mais elogiam em suas experiências de compra?

**Pergunta:** O que os clientes mais elogiam em suas experiências de compra?

**Transformação da pergunta:** texto de busca focado no assunto → “elogiam experiencias compra”; pergunta delimita elogios / clientes satisfeitos → nota 4 ou 5
**Filtros aplicados:** `{"review_score": {"gte": 4, "lte": 5}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “entrega rápida, chegou antes do prazo” | “recomendo a loja e o produto” | “produto de ótima qualidade, muito bom”
**Recuperação:** 120 candidatos densos + 120 lexicais → 178 únicos → 105 acima do limiar 0.51 → 12 no contexto (similaridade máx. 1.00)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Entrega rápida ou no prazo [1, 4, 7, 8, 9, 10, 11]
- Recomendação da loja ou do produto [3, 9, 11, 12]
- Qualidade abaixo do esperado [2, 5, 6]
- Boa qualidade do produto [2, 5, 6]

**Avaliações mais relevantes:**
- "a entrega foi rápida.chegou antes do prazo" (nota 5) [1]
- "De ótima qualidade!!!. Muito bom!!" (nota 5) [2]
- "Recomendo a loja e o produto" (nota 5) [3]
- "Super rapida entrega chegou antes do prazo" (nota 5) [4]
- "Muito bom os produtos e otima qualidade" (nota 5) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `85ce05b797ff5a7a765321c5a47f554f` · nota 5 · 2017-07-03 · malas_acessorios · entrega no_prazo · sim 0.95 · citada  
  “a entrega foi rápida.chegou antes do prazo”
- **[2]** `26c8ff1d2b283a59242ac9a752c247cf` · nota 5 · 2018-05-02 · cool_stuff · entrega no_prazo · sim 0.96 · citada  
  “De ótima qualidade!!!. Muito bom!!”
- **[3]** `0ebfe8313806bd1ea58091e73fbc3e3a` · nota 5 · 2017-01-13 · ferramentas_jardim · entrega no_prazo · sim 1.00 · citada  
  “Recomendo a loja e o produto”
- **[4]** `184aef5f199649bd09fd31e6b9bd48c6` · nota 5 · 2018-06-11 · esporte_lazer · entrega no_prazo · sim 0.89 · citada  
  “Super rapida entrega chegou antes do prazo”
- **[5]** `832e54fbe19c3788e8493da8b12b9847` · nota 5 · 2018-03-23 · telefonia · entrega no_prazo · sim 0.89 · citada  
  “Muito bom os produtos e otima qualidade”
- **[6]** `727fdc53d2891323aa72c4c79650c325` · nota 5 · 2018-05-30 · telefonia · entrega no_prazo · sim 1.00 · citada  
  “Muito bom. Produto de ótima qualidade”
- **[7]** `e6d997a9eefec8b38ace473c14e35c11` · nota 5 · 2017-08-16 · esporte_lazer · entrega no_prazo · sim 0.89 · citada  
  “entrega rapida, antes do prazo”
- **[8]** `0a3a04c6fd676cd1b4c6f2b797f19c74` · nota 5 · 2017-07-19 · beleza_saude · entrega no_prazo · sim 0.83 · citada  
  “O produto chegou antes do prazo. A entrega foi super rápida!”
- **[9]** `290eb60d8634b687486c311a961ecb4d` · nota 5 · 2018-08-22 · utilidades_domesticas · entrega no_prazo · sim 0.72 · citada  
  “Entrega rápida. Chegou até antes do prazo previsto. Recomendo.”
- **[10]** `6d005991d96ba4bbf92603b3fda4bfe1` · nota 4 · 2017-11-22 · cool_stuff · entrega no_prazo · sim 0.75 · citada  
  “A entrega foi muito rápida chegou antes do prazo esperado.”
- **[11]** `b22e7a5bb4238e7c4b6943596cd4faa1` · nota 5 · 2018-02-23 · utilidades_domesticas · entrega no_prazo · sim 0.81 · citada  
  “Recomendo super rápida a entrega,chegou antes do prazo.”
- **[12]** `b0e751c0a4d26a1c432124d55d506d3b` · nota 5 · 2018-07-13 · eletrodomesticos · entrega no_prazo · sim 0.91 · citada  
  “recomendo a loja”

---

## 4. Quais problemas são relatados por clientes insatisfeitos?

**Pergunta:** Quais problemas são relatados por clientes insatisfeitos?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas insatisfeitos”; pergunta delimita clientes insatisfeitos / nota baixa → nota 1 ou 2
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 2}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “não recebi o produto, ainda não chegou” | “quero devolver, trocar, cancelar e receber o dinheiro de volta” | “pedido incompleto, veio faltando item, recebi só uma parte” | “entrega atrasada, demorou muito para chegar, fora do prazo” | “produto veio com defeito, quebrado, não funciona”
**Recuperação:** 200 candidatos densos + 200 lexicais → 304 únicos → 194 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.99)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Produto com defeito ou danificado [3, 7, 9, 11]
- Entrega incompleta / itens faltando [1, 10, 12]
- Produto não recebido [2, 10]
- Devolução, troca, cancelamento ou reembolso [4, 8]
- Entrega atrasada / demora [5, 6]

**Avaliações mais relevantes:**
- "Meu pedido veio incompleto. Ficou faltando um item." (nota 1) [1]
- "Ainda NAO recebi o produt. O Produto não chegou." (nota 1) [2]
- "O relogio não esta funcionando. Nao esta quebrado. Mas nao funciona com a pilha de jeito nenhum. Veio com defeito" (nota 1) [3]
- "Quero o meu dinheiro de volta , não estou conseguindo cancelar" (nota 1) [4]
- "Demorou muito pra chegar" (nota 1) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `e2151cbbe41614f383562310b6438748` · nota 1 · 2017-11-12 · relogios_presentes · entrega no_prazo · sim 0.87 · citada  
  “Meu pedido veio incompleto. Ficou faltando um item.”
- **[2]** `e6c6d2dd67da56c2d77b24cb73ff2354` · nota 1 · 2018-07-12 · moveis_sala · entrega atrasada · sim 0.99 · citada  
  “Ainda NAO recebi o produt. O Produto não chegou.”
- **[3]** `5daed8162373d5914d7873de82d86355` · nota 1 · 2017-10-22 · relogios_presentes · entrega no_prazo · sim 0.79 · citada  
  “O relogio não esta funcionando. Nao esta quebrado. Mas nao funciona com a pilha de jeito nenhum. Veio com defeito”
- **[4]** `28ccdb164626d8d580e9070d0913951b` · nota 1 · 2017-04-08 · moveis_decoracao · entrega nao_entregue · sim 0.71 · citada  
  “Quero o meu dinheiro de volta , não estou conseguindo cancelar”
- **[5]** `47f3961ddbc91e07bd55fc4cdd11f9af` · nota 1 · 2017-05-25 · cool_stuff · entrega no_prazo · sim 0.74 · citada  
  “Demorou muito pra chegar”
- **[6]** `7c0de218885cc260013e84382ecff66c` · nota 1 · 2018-03-06 · construcao_ferramentas_iluminacao · entrega atrasada · sim 0.57 · citada  
  “Entrega atrasada!”
- **[7]** `5b14c151dac1c3e27a55c5c512a684b0` · nota 1 · 2018-08-21 · fashion_bolsas_e_acessorios · entrega no_prazo · sim 0.72 · citada  
  “Defeito produto. Recebi o pingente com defeito, quebrado.”
- **[8]** `4548534449b1f572e357211b90724f1b` · nota 1 · 2018-09-03 · desconhecida · entrega nao_entregue · sim 0.71 · citada  
  “quero devolver o produto comprei um veio outro;;; quero meu dinheiro de volta.”
- **[9]** `93f72220a2eefce8606c24ba7e121333` · nota 1 · 2018-07-24 · relogios_presentes · entrega no_prazo · sim 0.82 · citada  
  “Produto já veio com defeito não funciona”
- **[10]** `ea367d520c1e07a970c0452a97496afe` · nota 1 · 2017-05-16 · cool_stuff · entrega no_prazo · sim 0.76 · citada  
  “Nao recebi um dos produtos. o pedido veio incompleto!”
- **[11]** `1f9abf59f4b7b1ccfcb945f669ffad9a` · nota 1 · 2017-07-03 · brinquedos · entrega no_prazo · sim 0.66 · citada  
  “o produto veio quebrado”
- **[12]** `0afdaef42f4cef6492069412f42443d3` · nota 1 · 2018-01-12 · beleza_saude · entrega no_prazo · sim 0.74 · citada  
  “Recebi o produto incompleto, faltou 01 item!”

---

## 5. Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

**Pergunta:** Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

**Transformação da pergunta:** texto de busca focado no assunto → “qualidade produtos”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 76 únicos → 43 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.99)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Qualidade abaixo do esperado [3, 6, 8, 12]
- Boa qualidade do produto [2, 8, 12]
- Recomendação da loja ou do produto [4, 10]

**Avaliações mais relevantes:**
- "produtos de qualidade" (nota 5) [1]
- "Produtos de boa qualidade." (nota 5) [2]
- "Produtos de baixa qualidade." (nota 2) [3]
- "Produtos de qualidade... recomendadíssimo" (nota 5) [4]
- "Produtos chegaram com qualidade esperada" (nota 4) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `2e41aff5540a25f4ae6d0fd675458bb5` · nota 5 · 2017-08-11 · cama_mesa_banho · entrega no_prazo · sim 0.99 · citada  
  “produtos de qualidade”
- **[2]** `b3d919d72cc9aaba9f80678d6230c650` · nota 5 · 2017-06-13 · telefonia · entrega no_prazo · sim 0.89 · citada  
  “Produtos de boa qualidade.”
- **[3]** `be29016f816daa6c0ef6264984a71e61` · nota 2 · 2017-11-28 · esporte_lazer · entrega no_prazo · sim 0.85 · citada  
  “Produtos de baixa qualidade.”
- **[4]** `c899c8813995b5e0620eda0120294e91` · nota 5 · 2017-09-17 · cama_mesa_banho · entrega no_prazo · sim 0.73 · citada  
  “Produtos de qualidade... recomendadíssimo”
- **[5]** `eec6a964ce3972761d2334ebb7dd5293` · nota 4 · 2017-08-23 · relogios_presentes · entrega no_prazo · sim 0.66 · citada  
  “Produtos chegaram com qualidade esperada”
- **[6]** `2e44ced94d422c1b429b7a713e624c21` · nota 1 · 2017-06-07 · brinquedos · entrega no_prazo · sim 0.56 · citada  
  “Os produtos que me mandaram foram replicas do que eu solicitei. Produtos de péssima qualidade!!!”
- **[7]** `dcebfef07ae5bad804471747a19338e0` · nota 5 · 2018-04-02 · informatica_acessorios · entrega no_prazo · sim 0.63 · não citada  
  “Estão de parabéns pela pontualidade e qualidade dos produtos.”
- **[8]** `adf2fe8cbb936cf9d3764d318feda46a` · nota 5 · 2017-06-01 · relogios_presentes · entrega no_prazo · sim 0.60 · citada  
  “Americas produtos de ótima qualidade, obrigado!”
- **[9]** `8d7495e0ce43f2bf18ba6f5a8ea6b52c` · nota 5 · 2017-06-16 · cama_mesa_banho · entrega no_prazo · sim 0.54 · não citada  
  “muito maravillosa esta loja produtos de primeira qualidade”
- **[10]** `3d2e151da275e5a6c1eba0d887bd8414` · nota 5 · 2018-05-30 · utilidades_domesticas · entrega no_prazo · sim 0.84 · citada  
  “Recomendo. Produtos de qualidade”
- **[11]** `6de88c959f8877e1d63c2522343d9099` · nota 4 · 2018-03-23 · informatica_acessorios · entrega no_prazo · sim 0.73 · não citada  
  “Sempre compro, produtos de qualidade...”
- **[12]** `ae448fc7207c85ab3045092e2ee0d1e7` · nota 3 · 2017-12-09 · perfumaria · entrega no_prazo · sim 0.84 · citada  
  “produtos de ótima qualidade”

---

## 6. O que os clientes mais elogiam na categoria beleza e saúde?

**Pergunta:** O que os clientes mais elogiam na categoria beleza e saúde?

**Transformação da pergunta:** texto de busca focado no assunto → “elogiam”; pergunta delimita elogios / clientes satisfeitos → nota 4 ou 5; categoria citada → beleza_saude
**Filtros aplicados:** `{"review_score": {"gte": 4, "lte": 5}, "categoria": "beleza_saude"}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “entrega rápida, chegou antes do prazo” | “recomendo a loja e o produto” | “produto de ótima qualidade, muito bom”
**Recuperação:** 120 candidatos densos + 119 lexicais → 170 únicos → 107 acima do limiar 0.51 → 12 no contexto (similaridade máx. 1.00)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Entrega rápida ou no prazo [1, 4, 5, 7, 11]
- Boa qualidade do produto [2, 7, 8, 12]
- Recomendação da loja ou do produto [3, 6, 9, 10]
- Qualidade abaixo do esperado [2, 7, 12]

**Avaliações mais relevantes:**
- "O produto chegou antes do prazo. A entrega foi super rápida!" (nota 5) [1]
- "produto de otima qualidade" (nota 5) [2]
- "Recomendo a loja e o produto" (nota 4) [3]
- "Entrega rápida!. Tudo certo e entrega antes do prazo." (nota 5) [4]
- "Entrega super rápida, antes do prazo" (nota 5) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `0a3a04c6fd676cd1b4c6f2b797f19c74` · nota 5 · 2017-07-19 · beleza_saude · entrega no_prazo · sim 0.83 · citada  
  “O produto chegou antes do prazo. A entrega foi super rápida!”
- **[2]** `bacb714e23ed3ff1c447bef5fc5fb60b` · nota 5 · 2018-01-10 · beleza_saude · entrega no_prazo · sim 0.89 · citada  
  “produto de otima qualidade”
- **[3]** `62ca8958765c0ee385d12af0c94f4745` · nota 4 · 2017-12-15 · beleza_saude · entrega no_prazo · sim 1.00 · citada  
  “Recomendo a loja e o produto”
- **[4]** `0e399c3c6b3cb79170831ccd7ad0852b` · nota 5 · 2018-06-10 · beleza_saude · entrega no_prazo · sim 0.70 · citada  
  “Entrega rápida!. Tudo certo e entrega antes do prazo.”
- **[5]** `9b9f2f534826695f04e5b7985c4384cd` · nota 5 · 2018-04-08 · beleza_saude · entrega no_prazo · sim 0.77 · citada  
  “Entrega super rápida, antes do prazo”
- **[6]** `3e47ee5e922c857edaeb1f0249c70e7a` · nota 5 · 2017-04-16 · beleza_saude · entrega no_prazo · sim 0.72 · citada  
  “Otima loja,, recomendo,...”
- **[7]** `cb04972fa9fedc59b149c76610979502` · nota 5 · 2017-11-23 · beleza_saude · entrega no_prazo · sim 0.72 · citada  
  “Estetoscopio de ótima qualidade e entrega muito rápida.”
- **[8]** `650b166de480d4c326751c1efa14a232` · nota 5 · 2018-04-28 · beleza_saude · entrega no_prazo · sim 0.55 · citada  
  “Muito bom. Produto de boa qualidade, ótima costura, superou minhas expectativas.”
- **[9]** `15aefdc2e90c71084f40b1ab5ad42d49` · nota 5 · 2017-03-08 · beleza_saude · entrega no_prazo · sim 0.64 · citada  
  “Gostei muito da loja recomendo.”
- **[10]** `201bea6ed3623237914ca32b620a44e1` · nota 5 · 2017-04-25 · beleza_saude · entrega no_prazo · sim 0.71 · citada  
  “sim eu recomendo esta loja,”
- **[11]** `911f0088899c2d924524fe52a5fc7482` · nota 5 · 2018-06-19 · beleza_saude · entrega no_prazo · sim 0.70 · citada  
  “Entrega rápida!. Entrega antes do prazo!!! Recebi o produto em 03 dias!!!”
- **[12]** `8f17f539b9a0564eaf31899dbc8d9775` · nota 4 · 2018-04-09 · beleza_saude · entrega no_prazo · sim 0.82 · citada  
  “Otimo produto. Otima qualidade”

---

## 7. Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?

**Pergunta:** Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?

**Transformação da pergunta:** texto de busca focado no assunto → “experiencias entrega insatisfatorias”; entrega insatisfatória → pedidos entregues após o prazo ou sem entrega registrada
**Filtros aplicados:** `{"entrega_status": ["atrasada", "nao_entregue"]}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 80 únicos → 2 acima do limiar 0.51 → 0 no contexto (similaridade máx. 0.71)

**Status:** sem_evidencia (recusa na etapa de recuperacao)

Não encontrei evidências suficientes nas avaliações dos clientes para responder a essa pergunta com segurança.

_Motivo: Apenas 2 avaliação(ões) atingiram a similaridade mínima de 0.51 (maior similaridade encontrada: 0.71; mínimo exigido: 3 avaliações)._


---

## 8. Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

**Pergunta:** Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas ao prazo entrega”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 60 únicos → 41 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.89)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Temas mais presentes nas 12 avaliações recuperadas:**
- Produto não recebido [4, 8, 12]
- Produto com defeito ou danificado [6]

**Avaliações mais relevantes:**
- "Entrega sem problemas." (nota 3) [1]
- "estou tendo problemas com a entrega do produto é lamentável." (nota 1) [2]
- "tive problemas com a entrega a mercadoria não foi entrgue" (nota 2) [3]
- "Tive problemas com a entrega, não recebi o produto ainda." (nota 2) [4]
- "muitos problemas na entrega do mesmo. não fui avisada sobre a entrega." (nota 1) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `2e6818de484079f7e138c9bcc1936090` · nota 3 · 2017-09-06 · telefonia · entrega no_prazo · sim 0.89 · citada  
  “Entrega sem problemas.”
- **[2]** `daa6deed220cd3beeb7bfe4648a6a912` · nota 1 · 2018-06-23 · automotivo · entrega atrasada · sim 0.69 · citada  
  “estou tendo problemas com a entrega do produto é lamentável.”
- **[3]** `ebc75dc1e5f1aab722d127a0847be818` · nota 2 · 2017-08-01 · malas_acessorios · entrega atrasada · sim 0.60 · citada  
  “tive problemas com a entrega a mercadoria não foi entrgue”
- **[4]** `8dda0b425abc1dff16f4f1d295f80c3e` · nota 2 · 2018-03-14 · beleza_saude · entrega nao_entregue · sim 0.68 · citada  
  “Tive problemas com a entrega, não recebi o produto ainda.”
- **[5]** `c82e20ab06764504caa5a5754ba2050a` · nota 1 · 2018-04-27 · relogios_presentes · entrega no_prazo · sim 0.66 · citada  
  “muitos problemas na entrega do mesmo. não fui avisada sobre a entrega.”
- **[6]** `a6ae1375e10c5bd2f0984336dbfaf998` · nota 2 · 2017-12-15 · audio · entrega no_prazo · sim 0.57 · citada  
  “O produto está com problemas (defeito).”
- **[7]** `27bb48e9d6189b09e21b69b62f8c4097` · nota 1 · 2018-07-23 · informatica_acessorios · entrega no_prazo · sim 0.52 · não citada  
  “problemas na entrega. infelizmente essa compra não foi bem sucedida”
- **[8]** `49ef8de8e52ee16303f159ce620844d9` · nota 1 · 2018-01-29 · utilidades_domesticas · entrega nao_entregue · sim 0.61 · citada  
  “nunca tive problemas emrelaçao a entrega so que dessa vez nao me entregaram”
- **[9]** `29ceda25c8d305a2b52e74669d4441b9` · nota 3 · 2018-01-19 · informatica_acessorios · entrega no_prazo · sim 0.75 · não citada  
  “sem maiores problemas”
- **[10]** `eef257db1ec8d36de355d272048eb3e7` · nota 1 · 2018-02-13 · moveis_quarto · entrega nao_entregue · sim 0.68 · não citada  
  “Ja é as egunda vez que tenho problemas com entregas”
- **[11]** `ead794da001e8e2f6bc52a86b6db7a4d` · nota 3 · 2017-02-28 · perfumaria · entrega atrasada · sim 0.54 · não citada  
  “Só tive problemas Com relação a entrega, mas agora recebi ; super satisfeita”
- **[12]** `9183ee1d6da9be1da5e0776fc4b023d6` · nota 1 · 2018-02-20 · telefonia · entrega no_prazo · sim 0.55 · citada  
  “NAO CHEGOU POR PROBLEMAS NOS CORREIOS”

---

## 9. Qual é a capital da França?

**Pergunta:** Qual é a capital da França?

**Transformação da pergunta:** texto de busca focado no assunto → “capital franca”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 2 lexicais → 42 únicos → 2 acima do limiar 0.51 → 0 no contexto (similaridade máx. 0.60)

**Status:** sem_evidencia (recusa na etapa de recuperacao)

Não encontrei evidências suficientes nas avaliações dos clientes para responder a essa pergunta com segurança.

_Motivo: Apenas 2 avaliação(ões) atingiram a similaridade mínima de 0.51 (maior similaridade encontrada: 0.60; mínimo exigido: 3 avaliações)._


---

## 10. O que os clientes acham do tempo de bateria do iPhone 15?

**Pergunta:** O que os clientes acham do tempo de bateria do iPhone 15?

**Transformação da pergunta:** texto de busca focado no assunto → “tempo bateria iphone”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 68 únicos → 38 acima do limiar 0.51 → 12 no contexto (similaridade máx. 0.81)

**Status:** ok

_Modo extrativo (sem LLM configurado): os trechos abaixo são citações literais das avaliações recuperadas, sem síntese por modelo de linguagem._

**Avaliações mais relevantes:**
- "Quanto tempo dura a bateria" (nota 3) [1]
- "Pedi uma bateria para um notebook e até agora nada de chegar pedi a um tempo já" (nota 1) [2]
- "Foi em tempo recorde" (nota 5) [3]
- "Entrega a tempo" (nota 5) [4]
- "No tempo certo!" (nota 4) [5]

**Evidências (avaliações recuperadas):**

- **[1]** `c987fd39540c7ff14d6a874ee46c507b` · nota 3 · 2017-08-24 · market_place · entrega no_prazo · sim 0.81 · citada  
  “Quanto tempo dura a bateria”
- **[2]** `e85c87188f652bcf45e5d2d0df500414` · nota 1 · 2018-03-04 · informatica_acessorios · entrega atrasada · sim 0.52 · citada  
  “Pedi uma bateria para um notebook e até agora nada de chegar pedi a um tempo já”
- **[3]** `d54c4e69cf4f0c14e85313754605f2d4` · nota 5 · 2018-05-20 · perfumaria · entrega no_prazo · sim 0.70 · citada  
  “Foi em tempo recorde”
- **[4]** `8eb0b70ab47c002e3dd2cc0584d8b1a1` · nota 5 · 2017-07-01 · bebes · entrega no_prazo · sim 0.71 · citada  
  “Entrega a tempo”
- **[5]** `1a92049a52b183a1cd6a799fb2d41ae0` · nota 4 · 2017-05-04 · ferramentas_jardim · entrega no_prazo · sim 0.62 · citada  
  “No tempo certo!”
- **[6]** `27f17c9150d7367f41de88be072260a4` · nota 5 · 2017-10-28 · consoles_games · entrega no_prazo · sim 0.63 · não citada  
  “Chegou antes do tempo”
- **[7]** `1bec0bc314f003122b19b77525b7c750` · nota 4 · 2017-07-15 · cool_stuff · entrega no_prazo · sim 0.56 · não citada  
  “Entregaram no tempo bom”
- **[8]** `8bbcc29967c921b34d88e84b2e58da42` · nota 5 · 2017-08-28 · esporte_lazer · entrega no_prazo · sim 0.72 · não citada  
  “Entrega em tempo hábil”
- **[9]** `a3b7a9e53dd37282f079c9bb60dd498d` · nota 5 · 2017-12-28 · papelaria · entrega no_prazo · sim 0.52 · não citada  
  “Entregue no tempo correto”
- **[10]** `b74836fc42f499d2a95b16d560e88534` · nota 5 · 2017-11-14 · brinquedos · entrega no_prazo · sim 0.56 · não citada  
  “gostei do tempo de entrega”
- **[11]** `7b6a02bf7a01c72b4cde77e96b349fa6` · nota 5 · 2017-08-24 · automotivo · entrega no_prazo · sim 0.55 · não citada  
  “Entregue no tempo certo”
- **[12]** `00a94c6eefaf318ce0d3b56ce51b4d31` · nota 5 · 2018-01-17 · beleza_saude · entrega no_prazo · sim 0.56 · não citada  
  “Chegou no tempo certo”

---
