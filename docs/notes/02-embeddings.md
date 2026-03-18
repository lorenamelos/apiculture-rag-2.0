# Embeddings em Sistemas RAG

## O que são embeddings

<!-- TODO: Explicar o conceito após implementar -->

---

## Como funcionam

### A analogia do mapa de significados

<!-- TODO: Adicionar analogia visual -->

### Dimensionalidade

<!-- TODO: Explicar o que significa 512 vs 1024 vs 2048 dimensões -->

---

## Modelos de embedding

| Modelo | Dimensões | Custo | Qualidade | Quando usar |
|--------|-----------|-------|-----------|-------------|
| voyage-3-lite | 512 | Baixo | Boa | |
| voyage-3 | 1024 | Médio | Alta | |
| voyage-3-large | 2048 | Alto | Muito alta | |
| text-embedding-3-small | 1536 | Baixo | Boa | |

---

## input_type: document vs query

<!-- TODO: Explicar por que embeddings de query são diferentes de documentos -->

---

## Perguntas de entrevista

### Conceituais

**"O que são embeddings e por que usamos em RAG?"**
> 

**"Qual a diferença entre embeddings de documento e de query?"**
> 

**"Como escolher o modelo de embedding?"**
> 

### Técnicas

**"Como você mede a qualidade dos embeddings?"**
> 

**"O que fazer quando embeddings de domínios específicos não performam bem?"**
> 

---

## Decisões do projeto

**Modelo escolhido:** 
**Justificativa:** 

---

## Observações práticas

<!-- TODO: Adicionar aprendizados durante implementação -->

---

## Referências

- [Voyage AI Docs](https://docs.voyageai.com/)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)