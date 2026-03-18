# test_ingestion.py
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import PDFLoader, TextChunker

# Carrega um PDF
loader = PDFLoader()
pages = loader.load(Path("data/documents/CriacaoAbelhaSemFerrao.pdf"))

print(f"Loaded {len(pages)} pages")
for page in pages[:2]:  # Mostra as 2 primeiras
    print(f"  Page {page.metadata['page']}: {len(page.text)} chars")

# Divide em chunks
chunker = TextChunker(chunk_size=500, chunk_overlap=100)
chunks = chunker.chunk_pages(pages)

print(f"\nCreated {len(chunks)} chunks")
for chunk in chunks[:3]:  # Mostra os 3 primeiros
    print(f"  {chunk.metadata['chunk_id']}: {chunk.text[:80]}...")

# #-----------------------------------------------------------------------
# # Test embeddings (COMENTADO - já testou)
# from src.embeddings import Embedder
# embedder = Embedder()
# sample_texts = [chunk.text for chunk in chunks[:3]]
# vectors = embedder.embed_texts(sample_texts)
# print(f"\nEmbedding test:")
# print(f"  Model: {embedder.model}")
# print(f"  Dimensions: {embedder.dimensions}")
# print(f"  Embedded {len(vectors)} texts")
# print(f"  Vector sample: [{vectors[0][0]:.4f}, {vectors[0][1]:.4f}, ... {vectors[0][-1]:.4f}]")

# #-----------------------------------------------------------------------
# # Upload to Pinecone (COMENTADO - já fez upload)
# from src.vectorstore import PineconeStore
# store = PineconeStore()
# print(f"\nUploading {len(chunks)} chunks to Pinecone...")
# all_texts = [chunk.text for chunk in chunks]
# all_metadatas = [chunk.metadata for chunk in chunks]
# all_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
# all_embeddings = embedder.embed_texts(all_texts)
# store.upsert(ids=all_ids, embeddings=all_embeddings, texts=all_texts, metadatas=all_metadatas)
# stats = store.get_stats()
# print(f"  Total vectors after upload: {stats['total_vector_count']}")

# -----------------------------------------------------------------------
# Test retrieval (usa 1 chamada de embedding - barato)
from src.retrieval import Retriever

retriever = Retriever()  # cria embedder e store internamente

query = "Como criar abelhas sem ferrão?"
results = retriever.retrieve(query, top_k=3)

print(f"\nRetrieval test:")
print(f"  Query: {query}")
print(f"  Results:")
for i, chunk in enumerate(results, 1):
    print(f"    {i}. [{chunk.source}, p.{chunk.page}] (score: {chunk.score:.3f})")
    print(f"       {chunk.text[:100]}...")


# -----------------------------------------------------------------------
# Test RAG Chain (usa 1 embedding + 1 chamada Claude)
from src.chain import RAGChain

chain = RAGChain()

query = "Quais são os principais cuidados para criar abelhas sem ferrão?"
response = chain.query(query, top_k=3)

print(f"\nRAG Chain test:")
print(f"  Query: {query}")
print(f"\n  Answer:\n{response.answer}")
print(f"\n  Citations:")
for citation in response.citations:
    print(f"    - {citation.source}, Página {citation.page}")