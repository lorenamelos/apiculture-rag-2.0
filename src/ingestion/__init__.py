"""
Ingestion module - handles PDF loading, text chunking, and file watching.
"""

from .pdf_loader import PDFLoader
from .chunker import TextChunker
from .watcher import FolderWatcher

__all__ = ["PDFLoader", "TextChunker", "FolderWatcher"]
