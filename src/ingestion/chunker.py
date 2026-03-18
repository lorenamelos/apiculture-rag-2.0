"""
Text Chunking Module

Splits documents into smaller chunks for embedding and retrieval.
Preserves metadata through the chunking process for citation tracking.
"""

import unicodedata
import re
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter

import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """
    Represents a text chunk with its metadata.
    
    Attributes:
        text: The chunk content
        metadata: Source info (filename, page, chunk_index, etc.)
    """
    text: str
    metadata: Dict[str, Any]


class TextChunker:
    """
    Splits text into overlapping chunks while preserving metadata.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", ", ", " ", ""]
        )
    
    def chunk_pages(self, pages: List[Any]) -> List[Chunk]:
        """
        Split page contents into chunks.
        
        Args:
            pages: List of PageContent objects (from PDFLoader)
            
        Returns:
            List of Chunk objects with inherited + extended metadata
        """
        all_chunks = []
        
        for page in pages:
            if hasattr(page, 'text'):
                text = page.text
                metadata = page.metadata
            else:
                text = page["text"]
                metadata = page["metadata"]
            
            text_chunks = self._splitter.split_text(text)
            
            for idx, chunk_text in enumerate(text_chunks):
                chunk_metadata = self._add_chunk_metadata(
                    original_metadata=metadata,
                    chunk_index=idx,
                    total_chunks=len(text_chunks)
                )
                
                all_chunks.append(Chunk(text=chunk_text, metadata=chunk_metadata))
        
        logger.info(
            f"Created {len(all_chunks)} chunks from {len(pages)} pages "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        
        return all_chunks
    
    def _add_chunk_metadata(
        self, 
        original_metadata: Dict[str, Any], 
        chunk_index: int,
        total_chunks: int
    ) -> Dict[str, Any]:
        """
        Extend metadata with chunk-specific information.
        """
        extended = original_metadata.copy()
        
        extended["chunk_index"] = chunk_index
        extended["total_chunks_in_page"] = total_chunks
        
        source = original_metadata.get("source", "unknown")
        page = original_metadata.get("page", 0)
        
        # Sanitize source name for ASCII-only ID (Pinecone requirement)
        safe_source = self._sanitize_for_id(source)
        extended["chunk_id"] = f"{safe_source}_p{page}_c{chunk_index}"
        
        return extended
    
    def _sanitize_for_id(self, text: str) -> str:
        """
        Convert text to ASCII-safe string for use as ID.
        """
        # Normalize unicode (decompose accents)
        text = unicodedata.normalize('NFKD', text)
        
        # Remove non-ASCII characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Replace spaces and special chars with underscore
        text = re.sub(r'[^a-zA-Z0-9._-]', '_', text)
        
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        
        # Remove leading/trailing underscores
        text = text.strip('_')
        
        return text