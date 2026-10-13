"""Small RAG pipeline: read PDFs, retrieve text, and answer."""

from uuid import uuid4

from pypdf import PdfReader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompts import ANSWER_PROMPT

def read_pdfs(pdf_files):
    #Turn uploaded PDFs into Langchain documents
    documents=[]
    
    for pdf_file in pdf_files:#loop on pdf
        reader= PdfReader(pdf_file)
        for page_number,page in enumerate(reader.pages, start=1):
            text=page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source":pdf_file.name, "page":page_number},
                    )
                )
    return documents


def build_vector_store(pdf_files, api_key):
    #Read PDFs, split them into chuncks, and store their embeddings
    documents= read_pdfs(pdf_files)
    if not documents:
        raise ValueError("No readable text was found in the uploaded PDFs.")
    splitter= RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)#built-in class in langchain
    chuncks= splitter.split_documents(documents)
    
    embeddings= GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", google_api_key=api_key
    )
    # a fresh collection each time, so rebuilding doesn't mix old PDFs with new ones
    return Chroma.from_documents(
        chuncks, embeddings, collection_name=f"pdfs_{uuid4().hex}"
    )

def get_answer_text(response):
    #get only readable text from a gemini response
    content=response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts=[
            part["text"]
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"),str)

        ]
        return "\n".join(text_parts)
    
    return str(content)

def answer_question(vector_store, question, history, api_key):
    """Retrieve useful chuncks and ask Gemini to answer from them only"""
    documents=vector_store.similarity_search(question,k=3)
    context="\n\n".join(
        f"Source: {doc.metadata['source']}, page {doc.metadata['page']}\n{doc.page_content}" for doc in documents
    )
    prompt= ANSWER_PROMPT.format(context=context, history=history, question=question)
    model= ChatGoogleGenerativeAI(
        model="gemini-3.5-flash", google_api_key=api_key, temperature=0.7
    )
    response=model.invoke(prompt)
    answer=get_answer_text(response)
    sources=sorted(
        {f"{doc.metadata['source']} ( page {doc.metadata['page']})" for doc in documents}
    )
    return answer, sources
        
    
    