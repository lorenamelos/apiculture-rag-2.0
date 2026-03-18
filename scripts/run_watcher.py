"""
Folder Watcher Script

Monitors the documents directory for new PDF files and
automatically indexes them.

Usage:
    python scripts/run_watcher.py
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DOCUMENTS_DIR
from src.ingestion import FolderWatcher, PDFLoader, TextChunker
from src.embeddings import Embedder
from src.vectorstore import PineconeStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Initialize components once (reused for each file)
embedder = None
store = None
chunker = None


def initialize_components():
    """Initialize ML components (done once at startup)."""
    global embedder, store, chunker
    
    logger.info("Initializing components...")
    embedder = Embedder()
    store = PineconeStore()
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    logger.info("Components ready!")


def index_new_file(file_path: Path):
    """
    Index a newly detected PDF file.
    
    Args:
        file_path: Path to the new PDF
    """
    print(f"\n{'='*50}")
    print(f"📄 New file: {file_path.name}")
    print('='*50)
    
    try:
        # Load PDF
        loader = PDFLoader()
        pages = loader.load(file_path)
        print(f"   Extracted {len(pages)} pages")
        
        if not pages:
            print(f"   ⚠️ No content, skipping")
            return
        
        # Chunk
        chunks = chunker.chunk_pages(pages)
        print(f"   Created {len(chunks)} chunks")
        
        # Embed
        texts = [chunk.text for chunk in chunks]
        print(f"   Generating embeddings...")
        embeddings = embedder.embed_texts(texts)
        
        # Upload
        ids = [chunk.metadata["chunk_id"] for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        print(f"   Uploading to Pinecone...")
        store.upsert(ids=ids, embeddings=embeddings, texts=texts, metadatas=metadatas)
        
        print(f"   ✓ Indexed {len(chunks)} chunks")
        
        # Show total
        stats = store.get_stats()
        print(f"   Total vectors in index: {stats['total_vector_count']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("=" * 50)
    print("🐝 Apicultura RAG - Folder Watcher")
    print("=" * 50)
    print(f"\nWatching: {DOCUMENTS_DIR}")
    print("Drop PDF files here to auto-index them.")
    print("Press Ctrl+C to stop.\n")
    
    # Initialize components
    initialize_components()
    
    # Start watching
    watcher = FolderWatcher(
        watch_directory=DOCUMENTS_DIR,
        on_new_file=index_new_file
    )
    
    watcher.start(blocking=True)


if __name__ == "__main__":
    main()