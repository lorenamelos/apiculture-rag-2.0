"""
Embedding Module

Converts text into vector representations using Voyage AI's embedding models.

What are embeddings?
- Dense vector representations of text (lists of floats)
- Capture semantic meaning (similar meanings = similar vectors)
- Enable "similarity search" instead of keyword matching
- Think of it as coordinates in "meaning space"

Why Voyage AI?
- Recommended by Anthropic for use with Claude
- High quality embeddings optimized for retrieval
- Generous free tier (200M tokens)
- Multiple model sizes for different needs
"""

import voyageai
import time
from typing import List
import logging

from config.settings import VOYAGE_API_KEY, VOYAGE_EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class Embedder:
    """
    Converts text chunks into vector embeddings.
    
    Uses Voyage AI's embedding API for high-quality semantic representations.
    Handles batching automatically for efficiency and rate limit compliance.
    
    Usage:
        embedder = Embedder()
        vectors = embedder.embed_texts(["hello world", "goodbye world"])
        query_vector = embedder.embed_query("greeting")
    """
    
    # Model dimensions mapping
    MODEL_DIMENSIONS = {
        "voyage-3-lite": 512,
        "voyage-3": 1024,
        "voyage-3.5-lite": 1024,
        "voyage-3-large": 2048,
    }
    
    def __init__(self, model: str = None):
        """
        Initialize the embedder.
        
        Args:
            model: Voyage AI embedding model to use (default from settings)
        """
        self.model = model or VOYAGE_EMBEDDING_MODEL
        self.dimensions = self.MODEL_DIMENSIONS.get(self.model, 1024)
        
        # Initialize Voyage AI client
        self._client = voyageai.Client(api_key=VOYAGE_API_KEY)
        
        logger.info(f"Initialized Embedder with {self.model} ({self.dimensions} dimensions)")
    
    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 50,
        delay_between_batches: float = 0.5
    ) -> List[List[float]]:
        """
        Convert a list of texts (documents) to embeddings.
        
        Processes in batches to respect rate limits.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts per API call
            delay_between_batches: Seconds to wait between batches
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        logger.info(f"Embedding {len(texts)} texts in {total_batches} batches...")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            
            result = self._client.embed(
                texts=batch,
                model=self.model,
                input_type="document"
            )
            
            all_embeddings.extend(result.embeddings)
            
            # Wait between batches to avoid rate limits
            if i + batch_size < len(texts):
                time.sleep(delay_between_batches)
        
        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string.
        
        Note: Queries are embedded differently than documents.
        Voyage AI optimizes query embeddings for retrieval.
        
        Args:
            query: The search query to embed
            
        Returns:
            Embedding vector for the query
        """
        result = self._client.embed(
            texts=[query],
            model=self.model,
            input_type="query"
        )
        
        return result.embeddings[0]