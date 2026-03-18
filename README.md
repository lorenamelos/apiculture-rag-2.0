# Apicultura RAG 🐝

A production-ready Retrieval Augmented Generation (RAG) system for querying document archives with source citations.

Built as a portfolio project demonstrating end-to-end RAG pipeline implementation.

## Features

- **PDF Ingestion**: Extract text from PDFs with metadata preservation
- **Smart Chunking**: Recursive text splitting with overlap for context preservation
- **Semantic Search**: Vector similarity search using Voyage AI embeddings
- **Cloud Vector Store**: Persistent storage with Pinecone
- **AI-Powered Answers**: Claude generates responses grounded in your documents
- **Source Citations**: Every answer includes verifiable source references
- **Chat Interface**: Clean Streamlit UI for interactive Q&A
- **Auto-Indexing**: Folder watcher automatically indexes new PDFs 

## Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PDF       │────▶│   Chunker   │────▶│  Embedder   │
│   Loader    │     │  (LangChain)│     │ (Voyage AI) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │◀────│  RAG Chain  │◀────│  Pinecone   │
│     UI      │     │  (Claude)   │     │ Vector Store│
└─────────────┘     └─────────────┘     └─────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Anthropic Claude |
| Embeddings | Voyage AI |
| Vector Store | Pinecone |
| PDF Processing | pdfplumber |
| Framework | LangChain |
| UI | Streamlit |

## Quick Start

### 1. Clone and install
```bash
git clone https://github.com/lorenamelos/apiculture-rag-2.0.git
cd apicultura-rag
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
- `ANTHROPIC_API_KEY` - Get from [console.anthropic.com](https://console.anthropic.com)
- `VOYAGE_API_KEY` - Get from [dash.voyageai.com](https://dash.voyageai.com)
- `PINECONE_API_KEY` - Get from [app.pinecone.io](https://app.pinecone.io)

### 3. Create Pinecone index

In the Pinecone console, create an index with:
- **Dimensions**: 1024
- **Metric**: cosine

### 4. Add documents and index
```bash
# Add PDFs to data/documents/
cp your-documents/*.pdf data/documents/

# Index all documents
python scripts/index_documents.py
```

### 5. Run the app
```bash
streamlit run app/streamlit_app.py
```

## Project Structure
```
apicultura-rag/
├── app/
│   └── streamlit_app.py      # Chat interface
├── config/
│   └── settings.py           # Centralized configuration
├── data/
│   └── documents/            # PDF storage (gitignored)
├── scripts/
│   └── index_documents.py    # Batch indexing script
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py     # PDF text extraction
│   │   └── chunker.py        # Text splitting
│   ├── embeddings/
│   │   └── embedder.py       # Voyage AI embeddings
│   ├── vectorstore/
│   │   └── pinecone_store.py # Pinecone operations
│   ├── retrieval/
│   │   └── retriever.py      # Semantic search
│   └── chain/
│       └── rag_chain.py      # RAG with citations
├── tests/
│   └── test_ingestion.py     # Test suite
├── docs/
│   └── notes/                # Learning documentation
├── .env.example
├── requirements.txt
└── README.md
```

## Usage Examples

### Index a single document
```bash
python scripts/index_documents.py --file data/documents/manual.pdf
```

### Index all documents
```bash
python scripts/index_documents.py
```

### Query via Python
```python
from src.chain import RAGChain

chain = RAGChain()
response = chain.query("What are the main beekeeping practices?")

print(response.answer)
for citation in response.citations:
    print(f"  - {citation.source}, Page {citation.page}")
```

### Auto-indexing with folder watcher
```bash
# Terminal 1: Start the watcher
python scripts/run_watcher.py

# Terminal 2: Drop a PDF in the folder
cp new_document.pdf data/documents/

# The watcher will automatically detect and index the file
```

## Key Design Decisions

### Why Voyage AI over OpenAI embeddings?
Voyage AI is Anthropic's recommended embedding partner, offers a generous free tier (200M tokens), and provides high-quality retrieval-optimized embeddings.

### Why Pinecone over Chroma?
Pinecone provides cloud-hosted persistence, scales to millions of vectors, and offers production-ready reliability with a free tier suitable for development.

### Why pdfplumber over PyPDF?
pdfplumber provides better text extraction for complex layouts and preserves table structures more accurately.

## Limitations

- **Image-heavy PDFs**: Current implementation extracts text only. Diagrams, charts, and images are not processed.
- **Scanned PDFs**: Requires OCR preprocessing (not included).
- **Large documents**: Very large PDFs may hit rate limits during embedding.

## Future Enhancements

- [ ] Google Drive / Dropbox integration
- [ ] Multimodal support (image understanding)
- [ ] OCR for scanned documents
- [ ] Hybrid search (semantic + keyword)

## License

MIT

## Author

Built by [Lorena Santos] (https://github.com/lorenamelos) as a portfolio project demonstrating production-ready RAG implementation.