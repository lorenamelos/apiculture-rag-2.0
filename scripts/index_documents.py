"""
Document Indexing Script

Indexes all PDFs in the documents directory to Pinecone.

Usage:
    python scripts/index_documents.py                    # Index all PDFs
    python scripts/index_documents.py --file doc.pdf     # Index single file
    python scripts/index_documents.py --clear            # Clear index first
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DOCUMENTS_DIR
from src.ingestion import PDFLoader, TextChunker
from src.embeddings import Embedder
from src.vectorstore import PineconeStore


def index_file(file_path: Path, embedder: Embedder, store: PineconeStore, chunker: TextChunker) -> int:
    """
    Index a single PDF file.
    
    Returns:
        Number of chunks indexed
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Load PDF
    loader = PDFLoader()
    try:
        pages = loader.load(file_path)
        print(f"   Extracted {len(pages)} pages")
    except Exception as e:
        print(f"   ❌ Error loading PDF: {e}")
        return 0
    
    if not pages:
        print(f"   ⚠️ No content extracted, skipping")
        return 0
    
    # Chunk
    chunks = chunker.chunk_pages(pages)
    print(f"   Created {len(chunks)} chunks")
    
    # Embed
    texts = [chunk.text for chunk in chunks]
    print(f"   Generating embeddings...")
    embeddings = embedder.embed_texts(texts)
    
    # Prepare metadata and IDs
    ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    
    # Upload to Pinecone
    print(f"   Uploading to Pinecone...")
    store.upsert(ids=ids, embeddings=embeddings, texts=texts, metadatas=metadatas)
    
    print(f"   ✓ Indexed {len(chunks)} chunks")
    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="Index PDF documents to Pinecone")
    parser.add_argument("--file", type=str, help="Index a single file")
    parser.add_argument("--dir", type=str, default=str(DOCUMENTS_DIR), help="Directory with PDFs")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Chunk overlap in characters")
    args = parser.parse_args()
    
    print("=" * 50)
    print("🐝 Apicultura RAG - Document Indexer")
    print("=" * 50)
    
    # Initialize components
    print("\nInitializing components...")
    embedder = Embedder()
    store = PineconeStore()
    chunker = TextChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    
    # Get current stats
    stats = store.get_stats()
    print(f"Current index: {stats['total_vector_count']} vectors")
    
    # Determine files to process
    if args.file:
        files = [Path(args.file)]
    else:
        directory = Path(args.dir)
        files = sorted(directory.glob("*.pdf"))
        print(f"\nFound {len(files)} PDF files in {directory}")
    
    if not files:
        print("No PDF files found!")
        return
    
    # Process files
    total_chunks = 0
    successful = 0
    failed = 0
    
    for file_path in files:
        try:
            chunks = index_file(file_path, embedder, store, chunker)
            total_chunks += chunks
            if chunks > 0:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    # Final stats
    print("\n" + "=" * 50)
    print("📊 Indexing Complete!")
    print("=" * 50)
    print(f"   Files processed: {successful + failed}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total chunks indexed: {total_chunks}")
    
    stats = store.get_stats()
    print(f"   Vectors in index: {stats['total_vector_count']}")


if __name__ == "__main__":
    main()