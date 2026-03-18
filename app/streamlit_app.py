"""
Streamlit Chat Interface

Provides a chat-style UI for interacting with the RAG system.

Run with:
    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.chain import RAGChain


# Page configuration
st.set_page_config(
    page_title="Apicultura RAG",
    page_icon="🐝",
    layout="wide"
)


@st.cache_resource
def load_rag_chain():
    """Load RAG chain once and cache it."""
    return RAGChain()


def main():
    # Header
    st.title("🐝 Apicultura RAG")
    st.caption("Faça perguntas sobre criação de abelhas sem ferrão")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Load RAG chain
    chain = load_rag_chain()
    
    # Sidebar with info
    with st.sidebar:
        st.header("Sobre")
        st.markdown("""
        Este sistema usa **RAG (Retrieval Augmented Generation)** para responder 
        perguntas baseado em documentos sobre apicultura.
        
        **Como funciona:**
        1. Sua pergunta é convertida em embedding
        2. Buscamos os trechos mais relevantes
        3. Claude gera uma resposta com citações
        """)
        
        st.divider()
        
        st.header("Configurações")
        top_k = st.slider("Chunks a recuperar", min_value=1, max_value=10, value=5)
        show_sources = st.checkbox("Mostrar fontes detalhadas", value=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "citations" in message and show_sources:
                with st.expander("📚 Fontes consultadas"):
                    for citation in message["citations"]:
                        st.markdown(f"**{citation['source']}**, Página {citation['page']}")
                        st.caption(citation["snippet"])
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Faça sua pergunta sobre abelhas sem ferrão..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Buscando nos documentos..."):
                response = chain.query(prompt, top_k=top_k)
            
            st.markdown(response.answer)
            
            # Show sources
            if show_sources and response.citations:
                with st.expander("📚 Fontes consultadas"):
                    for citation in response.citations:
                        st.markdown(f"**{citation.source}**, Página {citation.page}")
                        st.caption(citation.text_snippet)
                        st.divider()
        
        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
            "citations": [
                {
                    "source": c.source,
                    "page": c.page,
                    "snippet": c.text_snippet
                }
                for c in response.citations
            ]
        })


if __name__ == "__main__":
    main()