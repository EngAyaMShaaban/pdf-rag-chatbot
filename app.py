"""Small app"""
import streamlit as st

from memory import add_message, clear_messages, get_history, start_memory
from rag import build_vector_store, answer_question

st.set_page_config(page_title="PDF Chatbot", page_icon="📄")
st.title("📄 PDF Chatbot")
st.caption("Upload PDFs, build a knowledge base, then ask questions.")

start_memory()

with st.sidebar:
    api_key= st.text_input("Gemini API Key", type="password")
    pdf_files= st.file_uploader(
        "Upload PDF files", type="pdf", accept_multiple_files=True
    )
    
    if st.button("Build knowledge base"):
        if not api_key:
            st.error("Enter your Gemini API key first.")
        elif not pdf_files:
            st.error("Upload at least one PDF file.")
        else:
            try:
                with st.spinner("Reading and indexing PDFs .... "):
                    st.session_state.vector_store= build_vector_store(pdf_files, api_key)
                clear_messages()
                st.success("Knowledge base is ready")
            except ValueError as error:
                st.error(str(error))
            
    if st.button("clear conversation"):
        clear_messages()
        st.rerun()
        
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message["content"])
        if message["role"]=="assistant" and message.get("sources"):
            st.caption("Sources: "+", ".join(message["sources"]))


question= st.chat_input("ASK Question about your PDFs")
if question:
    if "vector_store" not in st.session_state:
        st.warning("Upload PDFs and build the knowledge base first.")
    elif not api_key:
        st.warning("Enter your Gemini API Key in the sidebar.")
    else:
        history= get_history()
        add_message("user",question)
        
        with st.chat_message("user"):
            st.write(question)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching PDFs..."):
                answer, sources=answer_question(st.session_state.vector_store, question, history, api_key)
            st.write(answer)
            if sources:
                st.caption("Sources: "+ ", ".join(sources))
                
        add_message("assistant", answer, sources)
            