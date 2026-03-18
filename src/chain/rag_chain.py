"""
RAG Chain Module

Orchestrates the full RAG pipeline: retrieval + generation with citations.

The RAG Flow:
1. User asks a question
2. Retriever finds relevant chunks
3. Chunks are formatted as context
4. LLM generates answer using context
5. Response includes source citations

Why citations matter:
- Verifiability: User can check the source
- Trust: Shows the answer is grounded in documents
- Debugging: Helps identify retrieval issues
"""

import anthropic
from typing import List, Optional
from dataclasses import dataclass
import logging

from config.settings import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from src.retrieval import Retriever, RetrievedChunk

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """
    A source citation for the response.
    
    Attributes:
        source: Filename of the source document
        page: Page number
        text_snippet: Relevant excerpt from the source
    """
    source: str
    page: int
    text_snippet: str


@dataclass 
class RAGResponse:
    """
    Complete response from the RAG chain.
    
    Attributes:
        answer: The generated response text
        citations: List of sources used
        chunks_used: The retrieved chunks (for debugging/display)
    """
    answer: str
    citations: List[Citation]
    chunks_used: List[RetrievedChunk]


class RAGChain:
    """
    Combines retrieval and generation for Q&A with citations.
    
    Usage:
        chain = RAGChain()
        response = chain.query("Como criar abelhas sem ferrão?")
        print(response.answer)
        for citation in response.citations:
            print(f"  - {citation.source}, p.{citation.page}")
    """
    
    def __init__(
        self, 
        retriever: Retriever = None,
        model: str = None,
        top_k: int = 5
    ):
        """
        Initialize the RAG chain.
        
        Args:
            retriever: Retriever instance (creates one if not provided)
            model: Anthropic model to use (default from settings)
            top_k: Number of chunks to retrieve for context
        """
        self.retriever = retriever or Retriever()
        self.model = model or ANTHROPIC_MODEL
        self.top_k = top_k
        
        # Initialize Anthropic client
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        logger.info(f"Initialized RAGChain with model={self.model}, top_k={top_k}")
    
    def _build_system_prompt(self) -> str:
        """System prompt that instructs the model how to behave."""
        return """Você é um assistente especializado que responde perguntas baseado exclusivamente no contexto fornecido.

Regras:
1. Use APENAS informações presentes no contexto para responder
2. Se o contexto não contiver a resposta, diga claramente que não encontrou a informação nos documentos
3. Sempre cite as fontes no formato [Fonte: nome_do_arquivo, Página: X]
4. Seja direto e objetivo nas respostas
5. Responda no mesmo idioma da pergunta"""

    def _format_context(self, chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks as context for the LLM.
        
        Args:
            chunks: List of RetrievedChunk objects
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Documento {i}]\n"
                f"Fonte: {chunk.source}\n"
                f"Página: {chunk.page}\n"
                f"Conteúdo:\n{chunk.text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _build_user_prompt(self, question: str, context: str) -> str:
        """Build the user message with context and question."""
        return f"""Contexto dos documentos:

{context}

---

Pergunta: {question}

Responda baseado no contexto acima, citando as fontes utilizadas."""

    def query(self, question: str, top_k: int = None) -> RAGResponse:
        """
        Answer a question using RAG.
        
        Args:
            question: The user's question
            top_k: Number of chunks to retrieve (uses default if not specified)
            
        Returns:
            RAGResponse with answer and citations
        """
        top_k = top_k or self.top_k
        
        # Step 1: Retrieve relevant chunks
        logger.info(f"Retrieving chunks for: {question[:50]}...")
        chunks = self.retriever.retrieve(question, top_k=top_k)
        
        if not chunks:
            return RAGResponse(
                answer="Não encontrei informações relevantes nos documentos para responder essa pergunta.",
                citations=[],
                chunks_used=[]
            )
        
        # Step 2: Format context
        context = self._format_context(chunks)
        
        # Step 3: Generate response with Claude
        logger.info("Generating response with Claude...")
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self._build_system_prompt(),
            messages=[
                {"role": "user", "content": self._build_user_prompt(question, context)}
            ]
        )
        
        answer = message.content[0].text
        
        # Step 4: Build citations from used chunks
        citations = [
            Citation(
                source=chunk.source,
                page=int(chunk.page),
                text_snippet=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            )
            for chunk in chunks
        ]
        
        logger.info("Response generated successfully")
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            chunks_used=chunks
        )