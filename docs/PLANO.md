# Plano passo a passo — Tech Challenge Fase 4

Mapa do que o enunciado pede, do que já está pronto no repositório e do que falta fazer até a entrega.

## Onde estamos

| Requisito do enunciado | Situação | Onde |
|---|---|---|
| 1. Construção da base de conhecimento (seleção, limpeza, ausentes, organização, embeddings, indexação) | Pronto e executado na base real (38.287 documentos) | `data_prep.py`, `index.py`, README §4 |
| 2. Pipeline RAG (transformação, recuperação, seleção, contexto, geração) | Pronto. Recuperação testada na base real; geração por LLM testada só com modelo simulado | `query.py`, `retriever.py`, `generator.py`, README §5 |
| 3. Respostas fundamentadas com evidências visíveis | Pronto | interface, CLI, README §6 |
| 4. Perguntas sem evidência suficiente | Pronto (3 barreiras). **Limiar do e5 e recusa pelo LLM ainda precisam ser medidos** | README §6 e §8 |
| Adicional: metadados | Pronto (nota, ano, categoria, entrega, UF) | README §7 |
| Entregável: repositório com README | Pronto, com dois campos a preencher (equipe e link do vídeo) | `README.md` |
| Entregável: vídeo de até 7 min | Roteiro pronto; gravação pendente | `docs/ROTEIRO_VIDEO.md` |

## O que falta — em ordem

### Etapa 1 — Rodar na sua máquina (≈ 30 min, a maior parte esperando)

1. Clonar, criar o ambiente virtual e instalar: `make setup` (ou os comandos do README §3).
2. `python scripts/download_data.py`
3. `python -m voc_rag.cli prepare` — confira que `prep_report.json` mostra 38.287 documentos.
4. `python -m voc_rag.cli index` — baixa o `multilingual-e5-small` e indexa. Em CPU leva alguns minutos.
5. `pytest` — devem passar 37 testes.

### Etapa 2 — Configurar o LLM (≈ 10 min)

6. Escolher o provedor e preencher o `.env` (`LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`). Opções sem custo para o volume do trabalho: camada gratuita do Gemini ou do Groq, ou Ollama local.
7. Testar: `python -m voc_rag.cli ask "O que os clientes relatam sobre atraso na entrega?"`. A resposta deve vir em tópicos com citações `[n]`.

### Etapa 3 — Calibrar e medir (≈ 20 min) — **não pule**

8. `python -m voc_rag.cli eval --write --e2e`
   - Olhe o **limiar sugerido** e a margem entre "menor suporte no escopo" e "maior suporte fora do escopo". Se houver margem, a barreira 1 está separando bem.
   - Na tabela ponta a ponta, as 11 perguntas que devem ser recusadas precisam aparecer como `recusar`. As 8 fora do escopo idealmente na etapa `recuperacao`; as 3 do domínio sem resposta (iPhone 15, faturamento, aplicativo), na etapa `geracao`.
9. Se algo sair errado:
   - Pergunta fora do escopo sendo respondida → suba `MIN_SIMILARITY` no `.env` ou troque para um LLM mais obediente.
   - Pergunta válida sendo recusada na recuperação → baixe o limiar, ou teste `QUERY_FOCUS=off` e compare a relevância@k.
   - Modelo respondendo sem citar → a barreira 3 descarta a resposta; um modelo um pouco maior costuma resolver.
10. Acrescentar ao `eval/perguntas.json` 5–10 perguntas da própria equipe e rodar de novo.

### Etapa 4 — Fechar a documentação (≈ 30 min)

11. `python -m voc_rag.cli examples` → regenera `docs/EXEMPLOS.md` com respostas do LLM. Leia as dez respostas e confira se cada afirmação bate com a avaliação citada.
12. Atualizar o README §8 com os números do passo 8 (substituir o aviso de "ainda não medido") e o trecho da §9 com uma resposta real do LLM.
13. Preencher equipe e, depois de gravar, o link do vídeo no topo do README.
14. Se o professor exigir a base no repositório, não suba os CSVs: o `download_data.py` já resolve.

### Etapa 5 — Publicar (≈ 10 min)

15. Copiar os arquivos para o repositório `Wanderluzter/tech-challenge-4`, commitar e dar push (comandos na resposta do chat / README).
16. Conferir no GitHub: repositório **público**, README renderizando (inclusive o diagrama Mermaid), `.env` **fora** do repositório.

### Etapa 6 — Vídeo (≈ 1h30 com ensaio)

17. Seguir `docs/ROTEIRO_VIDEO.md`. Deixar o Streamlit aberto e as perguntas já testadas antes de gravar.
18. Ensaiar uma vez cronometrando: o limite é 7 minutos.
19. Subir o vídeo (YouTube não listado ou Drive com acesso por link) e colar o link no README.

### Etapa 7 — Entrega

20. Enviar na plataforma da FIAP o link do repositório e o do vídeo.
21. Bônus de +10 pontos: concluir a trilha *Generative AI Engineering Pathway* da Databricks Academy e enviar o certificado ou o print de *My Activities* com os cursos como *Completed*.

## Checklist dos critérios de avaliação

- [ ] Recupera conteúdos relevantes — conferir relevância@k no `eval` e ler as evidências dos exemplos
- [ ] Constrói contexto adequado — abrir "Contexto enviado ao modelo" na interface
- [ ] Respostas coerentes com as evidências — revisão manual do `docs/EXEMPLOS.md`
- [ ] Evita informações não fundamentadas — tabela ponta a ponta do `eval --e2e`
- [ ] Rastreabilidade dos insights — citações `[n]` + painel de evidências
- [ ] Reconhece falta de informação — as 11 perguntas de recusa do `eval`
- [ ] Repositório claro e reproduzível — peça para alguém de fora seguir o README do zero

## Se sobrar tempo (melhorias com bom retorno)

1. **Reranker** cross-encoder multilíngue sobre os candidatos do RRF.
2. **Anotar relevância** de ~50 pares pergunta–avaliação para medir precisão/recall reais.
3. **Verificador de fidelidade** (LLM-juiz): cada frase é sustentada pela avaliação citada?
4. **Deploy** no Streamlit Community Cloud para o link aparecer no vídeo.
