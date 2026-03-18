"""
Pinecone Vector Store Module

Handles storage and retrieval of embeddings in Pinecone.

Why Pinecone over Chroma?
- Cloud-hosted (persists across sessions)
- Scales to millions of vectors
- Production-ready (SLAs, monitoring)
- Free tier for development (up to 100k vectors)

Key Concepts:
- Index: Like a database table for vectors
- Namespace: Logical partition within an index (we use "default")
- Metadata: Key-value pairs stored with each vector (for citations)
- Upsert: Insert or update (idempotent - safe to retry)
"""

from pinecone import Pinecone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """
    Represents a single search result.
    
    Attributes:
        id: Unique identifier of the vector
        score: Similarity score (higher = more similar, max 1.0 for cosine)
        text: The original text content
        metadata: Source information for citations
    """
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class PineconeStore:
    """
    Manages vector storage and retrieval in Pinecone.
    
    Handles:
    - Index connection and health checks
    - Vector upserts with metadata
    - Similarity search with filtering
    
    Usage:
        store = PineconeStore()
        store.upsert(ids, embeddings, texts, metadatas)
        results = store.search(query_embedding, top_k=5)
    """
    
    def __init__(self, index_name: str = None, namespace: str = "default"):
        """
        Initialize connection to Pinecone.
        
        Args:
            index_name: Name of the Pinecone index
            namespace: Namespace for this collection of vectors
        """
        self.index_name = index_name or PINECONE_INDEX_NAME
        self.namespace = namespace
        
        # Initialize Pinecone client
        self._client = Pinecone(api_key=PINECONE_API_KEY)
        self._index = self._client.Index(self.index_name)
        
        logger.info(f"Connected to Pinecone index: {self.index_name}")
    
    def upsert(
        self, 
        ids: List[str],
        embeddings: List[List[float]], 
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Insert or update vectors in the store.
        
        Args:
            ids: Unique identifiers for each vector
            embeddings: Vector representations
            texts: Original text content (stored in metadata)
            metadatas: Additional metadata for each vector
            batch_size: Number of vectors per batch (Pinecone recommends ~100)
            
        Returns:
            Number of vectors upserted
        """
        if not ids:
            return 0
        
        # Prepare vectors with metadata
        vectors = []
        for i, (id_, embedding, text, metadata) in enumerate(zip(ids, embeddings, texts, metadatas)):
            # Include text in metadata for retrieval
            full_metadata = {**metadata, "text": text}
            vectors.append({
                "id": id_,
                "values": embedding,
                "metadata": full_metadata
            })
        
        # Upsert in batches
        total_upserted = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self._index.upsert(vectors=batch, namespace=self.namespace)
            total_upserted += len(batch)
            logger.debug(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")
        
        logger.info(f"Upserted {total_upserted} vectors to {self.index_name}")
        return total_upserted
    
    def search(
        self, 
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Find the most similar vectors to a query.
        
        Args:
            query_embedding: Vector representation of the query
            top_k: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"source": "doc.pdf"})
            
        Returns:
            List of SearchResult objects, ordered by similarity (highest first)
        """
        # Query Pinecone
        results = self._index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace,
            filter=filter_dict
        )
        
        # Convert to SearchResult objects
        search_results = []
        for match in results.matches:
            metadata = match.metadata or {}
            text = metadata.pop("text", "")  # Extract text from metadata
            
            search_results.append(SearchResult(
                id=match.id,
                score=match.score,
                text=text,
                metadata=metadata
            ))
        
        logger.info(f"Search returned {len(search_results)} results")
        return search_results
    
    def delete_by_source(self, source_filename: str) -> bool:
        """
        Delete all vectors from a specific source file.
        
        Useful for re-indexing updated documents.
        
        Args:
            source_filename: The filename to remove
            
        Returns:
            True if deletion was successful
        """
        # Pinecone serverless requires deleting by ID, not metadata filter
        # For now, we'd need to query first, then delete by IDs
        # This is a limitation of serverless tier
        logger.warning("delete_by_source requires querying IDs first in serverless mode")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dict with vector count, dimensions, etc.
        """
        stats = self._index.describe_index_stats()
        return {
            "total_vector_count": stats.total_vector_count,
            "namespaces": stats.namespaces,
            "dimension": stats.dimension
        }