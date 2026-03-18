"""
Retrieval Module

Handles semantic search to find relevant document chunks.

Semantic Search vs Keyword Search:
- Keyword: "bee diseases" only matches docs containing those exact words
- Semantic: "bee diseases" also matches "colony health problems", 
            "varroa mite infestations", etc.

This is possible because embeddings capture meaning, not just words.

The Retrieval Process:
1. User asks a question
2. Question is embedded (converted to vector)
3. Vector store finds most similar document chunks
4. Top-k chunks are returned as context for the LLM
"""

from typing import List, Optional
from dataclasses import dataclass
import logging

from src.embeddings import Embedder
from src.vectorstore import PineconeStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """
    A chunk retrieved for RAG context.
    
    Attributes:
        text: The chunk content
        source: Filename of the source document
        page: Page number in the source
        score: Relevance score from vector search (0-1, higher is better)
    """
    text: str
    source: str
    page: int
    score: float


class Retriever:
    """
    Retrieves relevant document chunks for a query.
    
    Combines the embedder and vector store to perform
    end-to-end semantic search.
    
    Usage:
        retriever = Retriever()
        chunks = retriever.retrieve("Como criar abelhas sem ferrão?")
        for chunk in chunks:
            print(f"[{chunk.source}, p.{chunk.page}]: {chunk.text[:100]}...")
    """
    
    def __init__(
        self, 
        embedder: Embedder = None, 
        vector_store: PineconeStore = None,
        top_k: int = 5
    ):
        """
        Initialize the retriever.
        
        Args:
            embedder: Embedder instance (creates one if not provided)
            vector_store: PineconeStore instance (creates one if not provided)
            top_k: Default number of chunks to retrieve
        """
        self.embedder = embedder or Embedder()
        self.vector_store = vector_store or PineconeStore()
        self.top_k = top_k
        
        logger.info(f"Initialized Retriever with top_k={top_k}")
    
    def retrieve(
        self, 
        query: str,
        top_k: int = None,
        filter_source: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """
        Find relevant chunks for a query.
        
        Args:
            query: The user's question
            top_k: Number of chunks to retrieve (uses default if not specified)
            filter_source: Optional filename to restrict search
            
        Returns:
            List of RetrievedChunk objects, ordered by relevance
        """
        top_k = top_k or self.top_k
        
        # Step 1: Embed the query
        query_embedding = self.embedder.embed_query(query)
        
        # Step 2: Search vector store
        filter_dict = {"source": filter_source} if filter_source else None
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        # Step 3: Convert to RetrievedChunk objects
        chunks = []
        for result in results:
            chunks.append(RetrievedChunk(
                text=result.text,
                source=result.metadata.get("source", "unknown"),
                page=result.metadata.get("page", 0),
                score=result.score
            ))
        
        logger.info(f"Retrieved {len(chunks)} chunks for query: {query[:50]}...")
        return chunks