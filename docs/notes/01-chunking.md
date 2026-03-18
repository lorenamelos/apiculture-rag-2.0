# Chunking em Sistemas RAG

## O que é e por que precisamos

Chunking é o processo de dividir documentos grandes em pedaços menores para busca e processamento. É necessário porque:

1. **Limite de contexto** — LLMs têm limite de tokens
2. **Custo** — mais tokens = mais caro (embedding + geração)
3. **Precisão na busca** — documentos grandes geram embeddings "diluídos"
4. **Ruído** — texto irrelevante no contexto confunde o modelo

### Analogia do fichário

Um livro inteiro numa única ficha não rankeia bem para buscas específicas. Várias fichas específicas permitem encontrar exatamente o trecho relevante.

---

## Parâmetros críticos

### chunk_size

| Tamanho | Uso | Trade-off |
|---------|-----|-----------|
| Pequeno (200-500) | Q&A factual, precisão alta | Pode perder contexto |
| Médio (500-1000) | Uso geral, equilíbrio | Padrão recomendado |
| Grande (1000-2000) | Sumarização, análise | Busca menos precisa |

### chunk_overlap

Caracteres repetidos entre chunks consecutivos. Evita perder informação nas bordas.

**Regra prática:** 10-20% do chunk_size.
```
Sem overlap:  [Chunk 1: "...põe ovos."][Chunk 2: "Os ovos viram..."]
                                      ↑ corte seco

Com overlap:  [Chunk 1: "...põe ovos. Os ovos viram"]
                        [Chunk 2: "põe ovos. Os ovos viram larvas..."]
                                      ↑ contexto preservado
```

---

## Estratégias de splitting

| Estratégia | Como funciona | Quando usar |
|------------|---------------|-------------|
| Character | Corta a cada N chars | Quase nunca (quebra palavras) |
| Recursive Character | Tenta parágrafos → linhas → sentenças → palavras | Uso geral, textos diversos |
| Sentence | Quebra em fim de sentenças | Textos bem estruturados |
| Semantic | Usa embeddings para detectar mudança de assunto | Alto custo, alta qualidade |

### Recursive Character (o que usamos)

Ordem de tentativa:
1. `\n\n` — parágrafos
2. `\n` — linhas
3. `. ? !` — sentenças
4. ` ` — palavras
5. `` — caracteres

---

## Perguntas de entrevista

### Conceituais

**"Por que chunking em vez de embedar documento inteiro?"**
> Embeddings de documentos grandes ficam "diluídos". Chunks menores = busca precisa, menor custo, respeita limites de contexto.

**"Como escolhe o tamanho do chunk?"**
> Depende do caso. Q&A factual: menor (300-500). Análise com contexto: maior (1000-1500). Sempre testar empiricamente.

**"O que acontece com chunk muito pequeno/grande?"**
> Pequeno: perde contexto, ambiguidade. Grande: embedding diluído, busca imprecisa, custo alto.

**"Para que serve overlap?"**
> Evita perder informação nas bordas. Garante contexto completo em pelo menos um chunk.

### Técnicas

**"Como lida com tabelas em PDFs?"**
> Tabelas perdem estrutura na extração. Opções: pdfplumber (preserva melhor), converter para markdown, ou chunking específico que preserva tabelas como unidade.

**"Documento com seções heterogêneas?"**
> Usar metadata (título da seção), chunkar por seção/capítulo, ou semantic chunking para detectar mudanças de tópico.

**"Como avalia se chunking está bom?"**
> Testar com queries reais. Inspecionar chunks recuperados: o contexto necessário está presente? Se precisa de múltiplos chunks para contexto completo, chunks podem estar pequenos demais.

### Debugging

**"RAG retornando respostas incompletas — como diagnostica?"**
> Inspecionar chunks recuperados. Chunk relevante incompleto → aumentar size/overlap. Chunk nem recuperado → problema de embedding ou extração.

---

## Decisões do projeto

**Configuração escolhida:**
- `chunk_size`: 1000 caracteres
- `chunk_overlap`: 200 caracteres (20%)
- Estratégia: RecursiveCharacterTextSplitter

**Justificativa:** equilíbrio para documentos técnicos sobre apicultura, permite contexto suficiente para explicações, overlap preserva continuidade.

---

## Observações práticas

- Página 1 (capa) gerou texto duplicado (`C C r r i i a a ç ç ã ã o o`) — comum em PDFs com texto estilizado
- Chunks ruins naturalmente não são recuperados (baixa similaridade)
- Metadatas preservados: `source`, `page`, `chunk_id` — essenciais para citações

---

## Referências

- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chunking Strategies for RAG](https://www.pinecone.io/learn/chunking-strategies/)