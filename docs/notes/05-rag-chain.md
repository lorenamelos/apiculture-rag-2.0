# RAG Chain (Geração com Contexto)

## O que é RAG

<!-- TODO: Explicar Retrieval Augmented Generation -->

---

## Anatomia de um prompt RAG
```
[System prompt]
Você é um assistente que responde baseado no contexto fornecido...

[Context]
{chunks recuperados}

[Question]
{pergunta do usuário}
```

<!-- TODO: Detalhar cada componente -->

---

## Citações e grounding

<!-- TODO: Explicar como garantir que respostas citam fontes -->

---

## Problemas comuns

### Alucinação

<!-- TODO: Quando o modelo inventa informação não presente no contexto -->

### Context overflow

<!-- TODO: Quando recupera contexto demais -->

### Lost in the middle

<!-- TODO: Modelos ignoram informação no meio de contextos longos -->

---

## Perguntas de entrevista

### Conceituais

**"O que é RAG e por que usar em vez de fine-tuning?"**
> 

**"Como você evita alucinações em RAG?"**
> 

**"O que é o problema 'lost in the middle'?"**
> 

### Técnicas

**"Como você estrutura o prompt para garantir citações?"**
> 

**"Como avalia a qualidade das respostas do RAG?"**
> 

---

## Métricas de avaliação

- **Faithfulness:** resposta é fiel ao contexto?
- **Relevance:** resposta é relevante à pergunta?
- **Groundedness:** claims são suportados pelo contexto?

---

## Decisões do projeto

**LLM:** 
**Prompt template:** 
**Formato de citação:** 

---

## Observações práticas

<!-- TODO: Adicionar aprendizados durante implementação -->

---

## Referências

- [Anthropic: RAG Best Practices](https://docs.anthropic.com/)
- [RAGAS: RAG Evaluation](https://docs.ragas.io/)