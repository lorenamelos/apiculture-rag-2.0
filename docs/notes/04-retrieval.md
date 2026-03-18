# Retrieval (Busca Semântica)

## Semantic search vs keyword search

<!-- TODO: Explicar a diferença fundamental -->

---

## O processo de retrieval
```
Query → Embed → Buscar no vector store → Top-K chunks → Contexto para LLM
```

<!-- TODO: Detalhar cada etapa -->

---

## Parâmetros importantes

### top_k

<!-- TODO: Explicar trade-off de quantos chunks retornar -->

### score_threshold

<!-- TODO: Explicar quando filtrar por similaridade mínima -->

### Filtros por metadata

<!-- TODO: Explicar uso de filtros -->

---

## Técnicas avançadas

### Hybrid search (sparse + dense)

<!-- TODO: Explicar combinação de BM25 com embeddings -->

### Reranking

<!-- TODO: Explicar segunda passada com modelo de reranking -->

### Query expansion

<!-- TODO: Explicar reformulação de queries -->

---

## Perguntas de entrevista

### Conceituais

**"Qual a diferença entre keyword search e semantic search?"**
> 

**"O que é o parâmetro top_k e como escolher?"**
> 

**"O que é hybrid search e quando usar?"**
> 

### Técnicas

**"Seu retrieval está retornando chunks irrelevantes. Como diagnostica?"**
> 

**"Como você avalia a qualidade do retrieval?"**
> 

---

## Métricas de avaliação

- **Recall@K:** 
- **Precision@K:** 
- **MRR (Mean Reciprocal Rank):** 

---

## Decisões do projeto

**top_k:** 
**Métrica de similaridade:** 
**Threshold:** 

---

## Observações práticas

<!-- TODO: Adicionar aprendizados durante implementação -->

---

## Referências

- [Pinecone: Semantic Search](https://www.pinecone.io/learn/semantic-search/)