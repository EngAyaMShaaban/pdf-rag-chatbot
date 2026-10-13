import streamlit as st

def start_memory():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        
def add_message (role, content, sources=None):
    st.session_state.messages.append(
        {"role":role, "content": content, "sources":sources or []}
        
    )
    
def get_history():
    #return previous messages as simple text for Gemini
    return"\n".join(
        f"{message['role']}: {message['content']}"
        for message in st.session_state.messages
        
    )
    
def clear_messages():
    st.session_state.messages=[]