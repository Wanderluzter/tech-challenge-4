# Exemplos de perguntas e respostas

Gerado por `python -m voc_rag.cli examples` sobre a base real da Olist. Nada aqui foi editado à mão.

- Embeddings: `intfloat/multilingual-e5-small`
- Geração: `openai_compat` / `nvidia/nemotron-3-ultra-550b-a55b:free`
- Limiar de similaridade: 0.875

## 1. Quais são os principais problemas relatados pelos clientes?

**Pergunta:** Quais são os principais problemas relatados pelos clientes?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “não recebi o produto, ainda não chegou” | “quero devolver, trocar, cancelar e receber o dinheiro de volta” | “pedido incompleto, veio faltando item, recebi só uma parte” | “entrega atrasada, demorou muito para chegar, fora do prazo” | “produto veio com defeito, quebrado, não funciona”
**Recuperação:** 199 candidatos densos + 200 lexicais → 345 únicos → 262 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.97)

**Status:** ok

- **Produto não recebido / não entrega** – tema mais frequente no PANORAMA (3.588 menções, 25,5%); exemplos: cliente sem registro de entrega e sem conseguir cancelar [3], pedidos de reembolso por não recebimento [9, 12].  
- **Devolução, troca, cancelamento ou reembolso** – 1.713 menções (12,2%); clientes relatam dificuldade para devolver produto quebrado [1], cancelar compra [3] ou obter estorno [9, 12].  
- **Entrega incompleta / itens faltando** – 1.460 menções (10,4%); diversos relatos de pedidos com itens ausentes [2, 6, 7, 8].  
- **Entrega atrasada / demora** – 1.200 menções (8,5%); atrasos de 2 a 5 dias além do prazo [9, 10, 12].  
- **Produto com defeito ou danificado** – 988 menções (7,0%); produtos recebidos quebrados ou sem funcionar [1, 4, 5, 11].  

*Outros temas do PANORAMA (produto errado, recomendação, entrega no prazo) não aparecem nas 12 avaliações recuperadas.*

**Evidências (avaliações recuperadas):**

- **[1]** `9837c1aa57c1116c83c2dd5050f685aa` · nota 1 · 2017-11-25 · informatica_acessorios · entrega no_prazo · sim 0.92 · citada  
  “o produto veio quebrado ,,, quero devolver”
- **[2]** `d100adcddcef25bfa83bb819d562211c` · nota 2 · 2018-07-01 · utilidades_domesticas · entrega no_prazo · sim 0.94 · citada  
  “Pedido incompleto. Meu pedido chegou faltando um item.”
- **[3]** `28ccdb164626d8d580e9070d0913951b` · nota 1 · 2017-04-08 · moveis_decoracao · entrega nao_entregue · sim 0.91 · citada  
  “Quero o meu dinheiro de volta , não estou conseguindo cancelar”
- **[4]** `93f72220a2eefce8606c24ba7e121333` · nota 1 · 2018-07-24 · relogios_presentes · entrega no_prazo · sim 0.94 · citada  
  “Produto já veio com defeito não funciona”
- **[5]** `13dcde46c1a250aaed407dd6d5a53b77` · nota 3 · 2018-07-23 · automotivo · entrega no_prazo · sim 0.94 · citada  
  “Produto com defeito. Produto veio quebrado”
- **[6]** `e2151cbbe41614f383562310b6438748` · nota 1 · 2017-11-12 · relogios_presentes · entrega no_prazo · sim 0.93 · citada  
  “Meu pedido veio incompleto. Ficou faltando um item.”
- **[7]** `0afdaef42f4cef6492069412f42443d3` · nota 1 · 2018-01-12 · beleza_saude · entrega no_prazo · sim 0.93 · citada  
  “Recebi o produto incompleto, faltou 01 item!”
- **[8]** `f7f2ecab5ccd99cd5e2a7d8eab6d25e9` · nota 1 · 2017-09-03 · cama_mesa_banho · entrega no_prazo · sim 0.93 · citada  
  “Recebi apenas um item desse pedido. Recebimento incompleto.”
- **[9]** `c3eb3b074d1aaba59e5771516c576189` · nota 1 · 2018-02-28 · utilidades_domesticas · entrega atrasada · sim 0.90 · citada  
  “Eu quero meu dinheiro de volta”
- **[10]** `f29bbead1034936360ff92f70abbe8f6` · nota 2 · 2017-11-07 · beleza_saude · entrega atrasada · sim 0.93 · citada  
  “Produto demorou muito para chegar”
- **[11]** `03a673dc9858b1fe77fc26a3900c129a` · nota 2 · 2018-04-05 · brinquedos · entrega no_prazo · sim 0.93 · citada  
  “Produto veio quebrado”
- **[12]** `5430589748eb1d2c1e48e65ce612fddd` · nota 1 · 2018-02-15 · moveis_decoracao · entrega atrasada · sim 0.90 · citada  
  “gostaria de receber meu dinheiro de volta”

---

## 2. Quais reclamações relacionadas à entrega aparecem com maior frequência?

**Pergunta:** Quais reclamações relacionadas à entrega aparecem com maior frequência?

**Transformação da pergunta:** texto de busca focado no assunto → “reclamacoes entrega”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 75 únicos → 38 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.93)

**Status:** ok

**Reclamações de entrega mais frequentes (baseado no PANORAMA de 14.070 avaliações negativas):**

- **Produto não recebido** — ~3.588 menções (25,5%) [PANORAMA]. Exemplos: produto não entregue e sem posicionamento da loja [8]; prazo vencido sem recebimento [9].
- **Entrega incompleta / itens faltando** — ~1.460 menções (10,4%) [PANORAMA]. Exemplos: pedido com dois itens e apenas um entregue [11]; "FALTOU ITENS NA ENTREGA" [12]; cabo não incluso [5].
- **Entrega atrasada / demora** — ~1.200 menções (8,5%) [PANORAMA]. Exemplos: "Demora a entrega" [1], "Demora na entrega" [2], "Atraso na entrega" [3], "Demora entrega" [6], atraso de 2 dias [7], atraso de 7 dias [8].

*Nota:* O PANORAMA usa contagem aproximada por palavras-chave; uma avaliação pode cair em mais de um tema. As 12 avaliações recuperadas ilustram os três padrões acima, mas não representam a base inteira.

**Evidências (avaliações recuperadas):**

- **[1]** `ef3905df6593f5fa7faebc82fb85e2e6` · nota 1 · 2018-01-17 · cama_mesa_banho · entrega no_prazo · sim 0.92 · citada  
  “Demora a entrega”
- **[2]** `b02ae085148e5e1eb6b11142ea9c653c` · nota 2 · 2017-10-04 · fashion_bolsas_e_acessorios · entrega no_prazo · sim 0.92 · citada  
  “Demora na entrega”
- **[3]** `048f89d5550f6d495dbfb726b23ba2a1` · nota 2 · 2018-03-19 · esporte_lazer · entrega atrasada · sim 0.92 · citada  
  “Atraso na entrega”
- **[4]** `68ab95a8aa59bdd29c944282b79614de` · nota 3 · 2017-12-07 · relogios_presentes · entrega no_prazo · sim 0.91 · não citada  
  “entrega Rapida”
- **[5]** `f9f941e29d04f05cac6605d2fe2bded5` · nota 1 · 2018-03-21 · telefonia · entrega no_prazo · sim 0.88 · citada  
  “PRODUTO NÃO VEIO COM O CABO VARIAS RECLAMAÇÕES E NINGUÉM SE MANIFESTOU”
- **[6]** `f09b051abf307c8693ad220930fd39cd` · nota 3 · 2017-11-16 · pet_shop · entrega no_prazo · sim 0.93 · citada  
  “Demora entrega”
- **[7]** `152b505997a2e78b3e2ee3d1120b5efe` · nota 1 · 2018-04-09 · construcao_ferramentas_ferramentas · entrega atrasada · sim 0.88 · citada  
  “produtos ruins. essa baratheon é ruim não tem atendente para não receber reclamações”
- **[8]** `8ff6181cba380f5e072a56e9b2b7d850` · nota 1 · 2018-08-06 · informatica_acessorios · entrega atrasada · sim 0.88 · citada  
  “Produto não entregue. Tudo muito ruim, não tem ninguém com possamos fazer reclamação pela não entrega do do produto. Não tem ouvidoria, para reclamações. Não tem nenhum pessypara informar o por que da demora da entrega.”
- **[9]** `e3c160b9f40b8c16e2e7d5f8ec3d375d` · nota 1 · 2018-01-16 · esporte_lazer · entrega nao_entregue · sim 0.88 · citada  
  “O prazo de entrega, pela loja foi até o dia 05/03/2018. Ainda não recebi o produto. Li várias reclamações de atrasos desta loja..quem sabe chega..”
- **[10]** `41fbe3bbe59583791d750031d36cd67e` · nota 1 · 2017-12-17 · utilidades_domesticas · entrega no_prazo · sim 0.88 · não citada  
  “tenho reclamaçoes quanto ao produto. nao atendeu minhas expectativas, acho mesmo que veio com defeito pois nao funcionou.”
- **[11]** `5148ad2bdca65375e9504355d79c6ad4` · nota 1 · 2018-07-15 · beleza_saude · entrega no_prazo · sim 0.89 · citada  
  “Entrega incompleta. Realizei um pedido com dois itens e apenas 1 deles foi entregue. Fiz algumas reclamações e até agora ninguém entrou em contato comigo pra entregar o outro produto ou para devolver o dinheiro.”
- **[12]** `4b3cef43bab1762205a0244024741178` · nota 1 · 2018-07-23 · automotivo · entrega no_prazo · sim 0.92 · citada  
  “FALTOU ITENS NA ENTREGA”

---

## 3. O que os clientes mais elogiam em suas experiências de compra?

**Pergunta:** O que os clientes mais elogiam em suas experiências de compra?

**Transformação da pergunta:** texto de busca focado no assunto → “elogiam experiencias compra”; pergunta delimita elogios / clientes satisfeitos → nota 4 ou 5
**Filtros aplicados:** `{"review_score": {"gte": 4, "lte": 5}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “entrega rápida, chegou antes do prazo” | “recomendo a loja e o produto” | “produto de ótima qualidade, muito bom”
**Recuperação:** 120 candidatos densos + 120 lexicais → 206 únicos → 144 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.97)

**Status:** ok

- **Entrega rápida ou antes do prazo** — tema mais frequente nas avaliações positivas (≈33 % das 24 217 análises, segundo o PANORAMA) e presente na maioria das avaliações recuperadas [2,3,4,5,7,8,9,11,12].  
- **Recomendação da loja ou do produto** — segundo tema em volume (≈23 % no PANORAMA) e citado explicitamente em duas avaliações [6,10].  
- **Boa qualidade do produto** — terceiro tema (≈17 % no PANORAMA) e mencionado em uma avaliação [1].  

*Nota: os percentuais vêm da contagem aproximada por palavras‑chave no PANORAMA; as avaliações recuperadas são uma amostra de 12 comentários.*

**Evidências (avaliações recuperadas):**

- **[1]** `727fdc53d2891323aa72c4c79650c325` · nota 5 · 2018-05-30 · telefonia · entrega no_prazo · sim 0.94 · citada  
  “Muito bom. Produto de ótima qualidade”
- **[2]** `184aef5f199649bd09fd31e6b9bd48c6` · nota 5 · 2018-06-11 · esporte_lazer · entrega no_prazo · sim 0.96 · citada  
  “Super rapida entrega chegou antes do prazo”
- **[3]** `6d005991d96ba4bbf92603b3fda4bfe1` · nota 4 · 2017-11-22 · cool_stuff · entrega no_prazo · sim 0.95 · citada  
  “A entrega foi muito rápida chegou antes do prazo esperado.”
- **[4]** `85ce05b797ff5a7a765321c5a47f554f` · nota 5 · 2017-07-03 · malas_acessorios · entrega no_prazo · sim 0.95 · citada  
  “a entrega foi rápida.chegou antes do prazo”
- **[5]** `8a24b9108e492e22e16764ce68fe3111` · nota 5 · 2017-01-29 · ferramentas_jardim · entrega no_prazo · sim 0.96 · citada  
  “Entrega muito rapida, muito antes do prazo”
- **[6]** `0ebfe8313806bd1ea58091e73fbc3e3a` · nota 5 · 2017-01-13 · ferramentas_jardim · entrega no_prazo · sim 0.94 · citada  
  “Recomendo a loja e o produto”
- **[7]** `f9d9e910e3321e4730fc205691d4dc4e` · nota 4 · 2017-07-25 · cama_mesa_banho · entrega no_prazo · sim 0.96 · citada  
  “muito rápida a entrega antes do prazo”
- **[8]** `ffee16b6eb3608ea21ad8048a809380c` · nota 5 · 2018-01-05 · ferramentas_jardim · entrega no_prazo · sim 0.96 · citada  
  “Entrega rápida , muito antes do prazo”
- **[9]** `4ec49604a1ce1c26d2de9183d0b63028` · nota 4 · 2017-06-02 · perfumaria · entrega no_prazo · sim 0.95 · citada  
  “Entrega muito rápida antes do prazo”
- **[10]** `4058856ef8c22bd07311401448e92444` · nota 5 · 2018-07-02 · beleza_saude · entrega no_prazo · sim 0.97 · citada  
  “recomendo o produto e a loja”
- **[11]** `e6d997a9eefec8b38ace473c14e35c11` · nota 5 · 2017-08-16 · esporte_lazer · entrega no_prazo · sim 0.95 · citada  
  “entrega rapida, antes do prazo”
- **[12]** `c6d02e0d596955917b3a1956afd19362` · nota 5 · 2018-02-02 · informatica_acessorios · entrega no_prazo · sim 0.96 · citada  
  “entrega muito rápida, antes do prazo estipulado”

---

## 4. Quais problemas são relatados por clientes insatisfeitos?

**Pergunta:** Quais problemas são relatados por clientes insatisfeitos?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas insatisfeitos”; pergunta delimita clientes insatisfeitos / nota baixa → nota 1 ou 2
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 2}}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “não recebi o produto, ainda não chegou” | “quero devolver, trocar, cancelar e receber o dinheiro de volta” | “pedido incompleto, veio faltando item, recebi só uma parte” | “entrega atrasada, demorou muito para chegar, fora do prazo” | “produto veio com defeito, quebrado, não funciona”
**Recuperação:** 199 candidatos densos + 200 lexicais → 344 únicos → 268 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.97)

**Status:** ok

- **Produto não recebido** — 3.264 menções (30,4%) no panorama; avaliações [4] (sem entrega registrada) e [12] (prazo encerrado sem recebimento) ilustram o problema.  
- **Devolução, troca, cancelamento ou reembolso** — 1.509 menções (14,1%); [1] pede devolução de item quebrado, [4] não consegue cancelar e quer dinheiro de volta, [11] solicita reembolso.  
- **Entrega incompleta / itens faltando** — 1.166 menções (10,9%); [2], [5], [6] e [8] relatam pedidos recebidos com itens ausentes.  
- **Entrega atrasada / demora** — 919 menções (8,6%); [7] (2 dias de atraso), [11] (8 dias) e [12] (7 dias, produto não chegou) citam demora.  
- **Produto com defeito ou danificado** — 771 menções (7,2%); [1], [3], [9] e [10] descrevem produtos quebrados ou que não funcionam.  
- **Produto errado ou diferente do anunciado** — 632 menções (5,9%) e **Qualidade abaixo do esperado** — 378 menções (3,5%) aparecem no panorama, mas não têm exemplos diretos nas 12 avaliações recuperadas.

**Evidências (avaliações recuperadas):**

- **[1]** `9837c1aa57c1116c83c2dd5050f685aa` · nota 1 · 2017-11-25 · informatica_acessorios · entrega no_prazo · sim 0.92 · citada  
  “o produto veio quebrado ,,, quero devolver”
- **[2]** `d100adcddcef25bfa83bb819d562211c` · nota 2 · 2018-07-01 · utilidades_domesticas · entrega no_prazo · sim 0.94 · citada  
  “Pedido incompleto. Meu pedido chegou faltando um item.”
- **[3]** `93f72220a2eefce8606c24ba7e121333` · nota 1 · 2018-07-24 · relogios_presentes · entrega no_prazo · sim 0.94 · citada  
  “Produto já veio com defeito não funciona”
- **[4]** `28ccdb164626d8d580e9070d0913951b` · nota 1 · 2017-04-08 · moveis_decoracao · entrega nao_entregue · sim 0.91 · citada  
  “Quero o meu dinheiro de volta , não estou conseguindo cancelar”
- **[5]** `e2151cbbe41614f383562310b6438748` · nota 1 · 2017-11-12 · relogios_presentes · entrega no_prazo · sim 0.93 · citada  
  “Meu pedido veio incompleto. Ficou faltando um item.”
- **[6]** `0afdaef42f4cef6492069412f42443d3` · nota 1 · 2018-01-12 · beleza_saude · entrega no_prazo · sim 0.93 · citada  
  “Recebi o produto incompleto, faltou 01 item!”
- **[7]** `f29bbead1034936360ff92f70abbe8f6` · nota 2 · 2017-11-07 · beleza_saude · entrega atrasada · sim 0.93 · citada  
  “Produto demorou muito para chegar”
- **[8]** `f7f2ecab5ccd99cd5e2a7d8eab6d25e9` · nota 1 · 2017-09-03 · cama_mesa_banho · entrega no_prazo · sim 0.93 · citada  
  “Recebi apenas um item desse pedido. Recebimento incompleto.”
- **[9]** `03a673dc9858b1fe77fc26a3900c129a` · nota 2 · 2018-04-05 · brinquedos · entrega no_prazo · sim 0.93 · citada  
  “Produto veio quebrado”
- **[10]** `5b14c151dac1c3e27a55c5c512a684b0` · nota 1 · 2018-08-21 · fashion_bolsas_e_acessorios · entrega no_prazo · sim 0.93 · citada  
  “Defeito produto. Recebi o pingente com defeito, quebrado.”
- **[11]** `a69b6a51e6a71c2189bfdf8eb8416ac0` · nota 1 · 2017-10-21 · telefonia · entrega atrasada · sim 0.90 · citada  
  “Quero meu dinheiro de volta”
- **[12]** `1bfec3e913196c72c1ea06fc8816bd9c` · nota 1 · 2018-05-06 · informatica_acessorios · entrega atrasada · sim 0.93 · citada  
  “entrega atrasada. o prazo terminou e nao recebi meu produto”

---

## 5. Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

**Pergunta:** Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

**Transformação da pergunta:** texto de busca focado no assunto → “qualidade produtos”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 78 únicos → 44 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.95)

**Status:** ok

**Padrões de qualidade nas avaliações**

- **Predomínio de menções positivas**: 11 de 12 avaliações recuperadas citam qualidade de forma favorável ("qualidade", "ótima qualidade", "boa qualidade", "qualidade esperada") [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12].
- **Associação a recompra e recomendação**: Clientes que elogiam a qualidade frequentemente indicam fidelidade ("Sempre compro") ou recomendam [5, 8, 9, 10].
- **Presença em múltiplas categorias**: Elogios aparecem em cama_mesa_banho, perfumaria, esporte_lazer, ferramentas_jardim, telefonia, utilidades_domesticas, informatica_acessorios e relogios_presentes [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12].
- **Menção negativa pontual**: Uma avaliação relata "baixa qualidade" (nota 2) [3].
- **Panorama da base**: "Boa qualidade do produto" aparece em ~11,5% das avaliações (4.408 menções); "Produto com defeito ou danificado" em ~3,3% (1.274 menções) — contagens aproximadas por palavras-chave.

**Limitação**: A amostra recuperada é majoritariamente positiva; não há relatos detalhados sobre tipos de defeito, durabilidade ou comparação entre categorias.

**Evidências (avaliações recuperadas):**

- **[1]** `2e41aff5540a25f4ae6d0fd675458bb5` · nota 5 · 2017-08-11 · cama_mesa_banho · entrega no_prazo · sim 0.95 · citada  
  “produtos de qualidade”
- **[2]** `ae448fc7207c85ab3045092e2ee0d1e7` · nota 3 · 2017-12-09 · perfumaria · entrega no_prazo · sim 0.94 · citada  
  “produtos de ótima qualidade”
- **[3]** `be29016f816daa6c0ef6264984a71e61` · nota 2 · 2017-11-28 · esporte_lazer · entrega no_prazo · sim 0.90 · citada  
  “Produtos de baixa qualidade.”
- **[4]** `317424786f416435834d8cea3d02112f` · nota 5 · 2017-05-14 · esporte_lazer · entrega no_prazo · sim 0.91 · citada  
  “Os produtos são de ótima qualidade.”
- **[5]** `c899c8813995b5e0620eda0120294e91` · nota 5 · 2017-09-17 · cama_mesa_banho · entrega no_prazo · sim 0.90 · citada  
  “Produtos de qualidade... recomendadíssimo”
- **[6]** `15c72b68259c35ea984ed16bf7633730` · nota 4 · 2017-03-08 · ferramentas_jardim · entrega no_prazo · sim 0.94 · citada  
  “produto de qualidade”
- **[7]** `a948b3b15a2d1011e0380b3948ba783a` · nota 4 · 2018-04-02 · telefonia · entrega no_prazo · sim 0.92 · citada  
  “Produtos de boa qualidade ,”
- **[8]** `ac5bb807a20ac6e17c4fea902dd5c2d7` · nota 5 · 2017-06-15 · cama_mesa_banho · entrega no_prazo · sim 0.90 · citada  
  “Recomendo produtos. Toma qualidade.”
- **[9]** `3d2e151da275e5a6c1eba0d887bd8414` · nota 5 · 2018-05-30 · utilidades_domesticas · entrega no_prazo · sim 0.90 · citada  
  “Recomendo. Produtos de qualidade”
- **[10]** `6de88c959f8877e1d63c2522343d9099` · nota 4 · 2018-03-23 · informatica_acessorios · entrega no_prazo · sim 0.89 · citada  
  “Sempre compro, produtos de qualidade...”
- **[11]** `832e54fbe19c3788e8493da8b12b9847` · nota 5 · 2018-03-23 · telefonia · entrega no_prazo · sim 0.90 · citada  
  “Muito bom os produtos e otima qualidade”
- **[12]** `eec6a964ce3972761d2334ebb7dd5293` · nota 4 · 2017-08-23 · relogios_presentes · entrega no_prazo · sim 0.90 · citada  
  “Produtos chegaram com qualidade esperada”

---

## 6. O que os clientes mais elogiam na categoria beleza e saúde?

**Pergunta:** O que os clientes mais elogiam na categoria beleza e saúde?

**Transformação da pergunta:** texto de busca focado no assunto → “elogiam”; pergunta delimita elogios / clientes satisfeitos → nota 4 ou 5; categoria citada → beleza_saude
**Filtros aplicados:** `{"review_score": {"gte": 4, "lte": 5}, "categoria": "beleza_saude"}`
**Pergunta ampla, expandida em sub-buscas pelos temas mais frequentes do recorte:** “entrega rápida, chegou antes do prazo” | “recomendo a loja e o produto” | “produto de ótima qualidade, muito bom”
**Recuperação:** 117 candidatos densos + 119 lexicais → 205 únicos → 176 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.97)

**Status:** ok

- **Entrega rápida ou dentro do prazo** — tema mais frequente no PANORAMA (≈37% das avaliações com a palavra-chave) e citado explicitamente em várias avaliações da amostra [3, 7, 9].  
- **Recomendação da loja e/ou do produto** — segundo tema no PANORAMA (≈25%) e presente na maioria das avaliações recuperadas [1, 4, 5, 6, 8, 10, 11, 12].  
- **Boa qualidade do produto** — terceiro tema no PANORAMA (≈13%) e mencionado diretamente em algumas avaliações [2, 6, 9].  

*Nota: os números do PANORAMA são contagens aproximadas por palavras-chave (uma avaliação pode conter vários temas); as 12 avaliações recuperadas são uma amostra das mais relevantes.*

**Evidências (avaliações recuperadas):**

- **[1]** `12af7591bfb1fc87142424b66c02aa08` · nota 5 · 2017-11-24 · beleza_saude · entrega no_prazo · sim 0.94 · citada  
  “Recomendo a loja e o produto”
- **[2]** `e36166cca20f917430ef21ce433e3c3f` · nota 5 · 2017-11-24 · beleza_saude · entrega no_prazo · sim 0.94 · citada  
  “Produto de ótima qualidade”
- **[3]** `9b9f2f534826695f04e5b7985c4384cd` · nota 5 · 2018-04-08 · beleza_saude · entrega no_prazo · sim 0.95 · citada  
  “Entrega super rápida, antes do prazo”
- **[4]** `4058856ef8c22bd07311401448e92444` · nota 5 · 2018-07-02 · beleza_saude · entrega no_prazo · sim 0.97 · citada  
  “recomendo o produto e a loja”
- **[5]** `0641436a9623d106942c029b834584e4` · nota 5 · 2017-03-05 · beleza_saude · entrega atrasada · sim 0.94 · citada  
  “Recomendo loja e produto”
- **[6]** `632ca34143ae20bbcd2861e9283a4f2e` · nota 5 · 2017-03-11 · beleza_saude · entrega no_prazo · sim 0.93 · citada  
  “Recomendo produto de ótima qualidade”
- **[7]** `0a3a04c6fd676cd1b4c6f2b797f19c74` · nota 5 · 2017-07-19 · beleza_saude · entrega no_prazo · sim 0.94 · citada  
  “O produto chegou antes do prazo. A entrega foi super rápida!”
- **[8]** `dd7ad46e529dee82ac30a6f2561e0aa3` · nota 5 · 2018-08-19 · beleza_saude · entrega no_prazo · sim 0.93 · citada  
  “recomendo. Ótima loja e produtos”
- **[9]** `9919d4be00f6c4a7754148257bfa6f10` · nota 5 · 2017-10-31 · beleza_saude · entrega no_prazo · sim 0.94 · citada  
  “entrega super rápida , produto de ótima qualidade”
- **[10]** `15aefdc2e90c71084f40b1ab5ad42d49` · nota 5 · 2017-03-08 · beleza_saude · entrega no_prazo · sim 0.92 · citada  
  “Gostei muito da loja recomendo.”
- **[11]** `201bea6ed3623237914ca32b620a44e1` · nota 5 · 2017-04-25 · beleza_saude · entrega no_prazo · sim 0.91 · citada  
  “sim eu recomendo esta loja,”
- **[12]** `b2947bd264e3309233935a4a96d2773c` · nota 4 · 2017-09-04 · beleza_saude · entrega no_prazo · sim 0.93 · citada  
  “recomendo tanto a loja como o produto.gostei”

---

## 7. Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?

**Pergunta:** Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias?

**Transformação da pergunta:** texto de busca focado no assunto → “experiencias entrega insatisfatorias”; entrega insatisfatória → pedidos entregues após o prazo ou sem entrega registrada
**Filtros aplicados:** `{"entrega_status": ["atrasada", "nao_entregue"]}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 79 únicos → 8 acima do limiar 0.88 → 8 no contexto (similaridade máx. 0.88)

**Status:** ok

**Temas principais nas avaliações com entrega insatisfatória (base: 5.509 avaliações, nota média 1,75)**

- **Produto não recebido / entrega não efetuada** — tema mais frequente no panorama (~2.541 menções, 46,1% por palavras-chave) [2, 6].
- **Entrega atrasada / demora** — segunda maior ocorrência (~831 menções, 15,1%); clientes citam atrasos de 1 a 25 dias e impacto em obras ou planos [1, 3, 4, 8].
- **Devolução, troca, cancelamento ou reembolso** — aparece em ~641 menções (11,6%), sugerindo que atrasos/não-entrega geram pedidos de estorno ou troca.
- **Atendimento / falta de retorno** — ~211 menções (3,8%); insatisfação com ausência de resposta ou suporte.
- **Entrega incompleta / itens faltando** — ~90 menções (1,6%).
- **Qualidade do produto** — citada junto ao atraso em algumas avaliações (ex.: “produto de baixa qualidade”) [1], mas tema menor no panorama (~107 menções, 1,9%).
- **Avaliações positivas apesar do atraso** — existem casos isolados de nota 5 mesmo com entrega tardia [7].

*Observação:* as contagens do PANORAMA são aproximadas por palavras-chave (uma avaliação pode cair em vários temas). As 8 avaliações recuperadas ilustram os padrões, mas não representam a base toda.

**Evidências (avaliações recuperadas):**

- **[1]** `190b01af91fb754443307e59209136d6` · nota 1 · 2018-06-19 · automotivo · entrega atrasada · sim 0.88 · citada  
  “produto insatisfatorio. demora na entrega e produto de baixa qualidade”
- **[2]** `fb273933480c85e5897cea81904ce534` · nota 1 · 2017-02-23 · beleza_saude · entrega atrasada · sim 0.88 · citada  
  “sem opinião produto não entregue”
- **[3]** `dd6e0f7168d75cd78769333f7630a036` · nota 3 · 2018-03-08 · moveis_decoracao · entrega atrasada · sim 0.88 · citada  
  “O atraso na entrega prejudicou a obra”
- **[4]** `5dac7ad9e8958f5e3bf17fb30b96c6b4` · nota 2 · 2018-03-18 · ferramentas_jardim · entrega atrasada · sim 0.88 · citada  
  “Bom dia!estou insatisfeita com a demora”
- **[5]** `f228dd6fee66568cede962423139fe7c` · nota 2 · 2017-07-23 · cama_mesa_banho · entrega nao_entregue · sim 0.88 · não citada  
  “insatisfação 1”
- **[6]** `4adfad59289a2e8a92288351b9f73137` · nota 3 · 2017-07-23 · cama_mesa_banho · entrega nao_entregue · sim 0.88 · citada  
  “ENTREGA NÃO EFETUADA”
- **[7]** `3620d6e5d561991af5ff9f6a8bdcc3c4` · nota 5 · 2018-05-03 · ferramentas_jardim · entrega atrasada · sim 0.88 · citada  
  “exelente. atendeu as expectivas”
- **[8]** `940883016d9c7bf718dafcbbebfb7c61` · nota 1 · 2018-04-03 · cama_mesa_banho · entrega atrasada · sim 0.88 · citada  
  “insatisfeita”

---

## 8. Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

**Pergunta:** Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

**Transformação da pergunta:** texto de busca focado no assunto → “problemas ao prazo entrega”; pergunta sobre problemas/reclamações → exclui notas 4 e 5
**Filtros aplicados:** `{"review_score": {"gte": 1, "lte": 3}}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 80 únicos → 55 acima do limiar 0.88 → 12 no contexto (similaridade máx. 0.93)

**Status:** ok

As avaliações que citam explicitamente **prazo de entrega** como problema:

- **[1]** “Um prazo de entrega demorado” (nota 3, entrega registrada como no prazo)  
- **[3]** “Produto com o prazo de entrega atrasado” (nota 3, entrega atrasada 9 dias)  
- **[12]** “Não atende o prazo de entrega” (nota 1, entrega atrasada 3 dias)

Outras avaliações relatam **atraso na entrega** sem usar a expressão “prazo”:

- **[2]** “problemas com a entrega” (atraso de 27 dias)  
- **[4]** “problemas com a entrega a mercadoria não foi entrgue” (atraso de 12 dias)  
- **[5]** “Atraso na entrega” (atraso de 21 dias)

Avaliações com **entrega registrada como “no prazo”** mas que reclamam de demora ou falta de aviso:

- **[6]** “muitos problemas na entrega… não fui avisada”  
- **[7]** “problemas na entrega”  
- **[9]** “Muita demora na entrega”

Avaliações sem entrega registrada (produto não recebido):

- **[8]** “não recebi o produto ainda”  
- **[11]** “Não chegou ainda estou na esperando ainda”

**Panorama**: o tema “Entrega atrasada / demora” aparece em ~1.200 avaliações (8,5% da amostra filtrada) e “Produto não recebido” em ~3.588 (25,5%), indicando recorrência. [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]

**Evidências (avaliações recuperadas):**

- **[1]** `cc7aa30132ae7195c15ac60a6d96f63d` · nota 3 · 2017-08-08 · artes · entrega no_prazo · sim 0.93 · citada  
  “Um prazo de entrega demorado”
- **[2]** `daa6deed220cd3beeb7bfe4648a6a912` · nota 1 · 2018-06-23 · automotivo · entrega atrasada · sim 0.89 · citada  
  “estou tendo problemas com a entrega do produto é lamentável.”
- **[3]** `f6cdef6e564ca38cd4dcff3ddba22fe1` · nota 3 · 2018-02-17 · bebes · entrega atrasada · sim 0.92 · citada  
  “Produto com o prazo de entrega atrasado”
- **[4]** `ebc75dc1e5f1aab722d127a0847be818` · nota 2 · 2017-08-01 · malas_acessorios · entrega atrasada · sim 0.89 · citada  
  “tive problemas com a entrega a mercadoria não foi entrgue”
- **[5]** `048f89d5550f6d495dbfb726b23ba2a1` · nota 2 · 2018-03-19 · esporte_lazer · entrega atrasada · sim 0.92 · citada  
  “Atraso na entrega”
- **[6]** `c82e20ab06764504caa5a5754ba2050a` · nota 1 · 2018-04-27 · relogios_presentes · entrega no_prazo · sim 0.89 · citada  
  “muitos problemas na entrega do mesmo. não fui avisada sobre a entrega.”
- **[7]** `27bb48e9d6189b09e21b69b62f8c4097` · nota 1 · 2018-07-23 · informatica_acessorios · entrega no_prazo · sim 0.89 · citada  
  “problemas na entrega. infelizmente essa compra não foi bem sucedida”
- **[8]** `8dda0b425abc1dff16f4f1d295f80c3e` · nota 2 · 2018-03-14 · beleza_saude · entrega nao_entregue · sim 0.89 · citada  
  “Tive problemas com a entrega, não recebi o produto ainda.”
- **[9]** `3ffed17f5010b9c6d33706b790732482` · nota 1 · 2017-07-14 · utilidades_domesticas · entrega no_prazo · sim 0.92 · citada  
  “Muita demora na entrega”
- **[10]** `a6ae1375e10c5bd2f0984336dbfaf998` · nota 2 · 2017-12-15 · audio · entrega no_prazo · sim 0.89 · não citada  
  “O produto está com problemas (defeito).”
- **[11]** `20787e5ce2d5175a20135e52e3a701e8` · nota 2 · 2018-05-12 · desconhecida · entrega nao_entregue · sim 0.90 · citada  
  “Problemas com entrega. Não chegou ainda estou na esperando ainda”
- **[12]** `47479f9482563d40ca3102c5e82e01aa` · nota 1 · 2018-03-20 · brinquedos · entrega atrasada · sim 0.92 · citada  
  “Não atende o prazo de entrega”

---

## 9. Qual é a capital da França?

**Pergunta:** Qual é a capital da França?

**Transformação da pergunta:** texto de busca focado no assunto → “capital franca”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 2 lexicais → 42 únicos → 0 acima do limiar 0.88 → 0 no contexto (similaridade máx. 0.82)

**Status:** sem_evidencia (recusa na etapa de recuperacao)

Não encontrei evidências suficientes nas avaliações dos clientes para responder a essa pergunta com segurança.

_Motivo: Apenas 0 avaliação(ões) atingiram a similaridade mínima de 0.88 (maior similaridade encontrada: 0.82; mínimo exigido: 3 avaliações)._


---

## 10. O que os clientes acham do tempo de bateria do iPhone 15?

**Pergunta:** O que os clientes acham do tempo de bateria do iPhone 15?

**Transformação da pergunta:** texto de busca focado no assunto → “tempo bateria iphone”; nenhum filtro inferido: busca em toda a base
**Filtros aplicados:** `{}`
**Recuperação:** 40 candidatos densos + 40 lexicais → 75 únicos → 1 acima do limiar 0.88 → 0 no contexto (similaridade máx. 0.90)

**Status:** sem_evidencia (recusa na etapa de recuperacao)

Não encontrei evidências suficientes nas avaliações dos clientes para responder a essa pergunta com segurança.

_Motivo: Apenas 1 avaliação(ões) atingiram a similaridade mínima de 0.88 (maior similaridade encontrada: 0.90; mínimo exigido: 3 avaliações)._


---
