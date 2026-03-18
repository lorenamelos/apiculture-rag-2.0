"""
Centralized configuration for the RAG pipeline.

This module loads environment variables and provides typed configuration
objects for each component. Single source of truth for all settings.

Stack:
- LLM: Anthropic Claude (chat/generation)
- Embeddings: Voyage AI (text-to-vector)
- Vector Store: Pinecone (cloud-hosted)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# Path Configuration
# =============================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directory where PDFs are stored/watched
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Anthropic Configuration (LLM)
# =============================================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


# =============================================================================
# Voyage AI Configuration (Embeddings)
# =============================================================================

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
VOYAGE_EMBEDDING_MODEL = os.getenv("VOYAGE_EMBEDDING_MODEL", "voyage-3-lite")

# Embedding dimensions for voyage-3-lite
# voyage-3.5-lite: 1024 dimensions (faster, cheaper)
# voyage-3: 1024 dimensions (balanced)
# voyage-3-large: 2048 dimensions (highest quality)
EMBEDDING_DIMENSIONS = 1024  # for voyage-3.5-lite


# =============================================================================
# Pinecone Configuration
# =============================================================================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "apicultura-rag")


# =============================================================================
# Chunking Configuration
# =============================================================================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


# =============================================================================
# Retrieval Configuration
# =============================================================================

# Number of chunks to retrieve for context
TOP_K = 5


# =============================================================================
# Validation
# =============================================================================

def validate_config() -> dict:
    """
    Validate that all required configuration is present.
    Returns a dict with status and any missing keys.
    """
    required = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "VOYAGE_API_KEY": VOYAGE_API_KEY,
        "PINECONE_API_KEY": PINECONE_API_KEY,
    }
    
    missing = [key for key, value in required.items() if not value]
    
    return {
        "valid": len(missing) == 0,
        "missing": missing
    }