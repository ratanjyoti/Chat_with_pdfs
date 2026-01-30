import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDF files"""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    """Split text into chunks for processing"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000, 
        chunk_overlap=500
    )
    chunks = text_splitter.split_text(text)
    return chunks


from langchain_huggingface import HuggingFaceEmbeddings

def get_vector_store(text_chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def user_input(user_question):
    if not os.path.exists("faiss_index"):
        st.error("⚠️ Please upload and process PDF files first!")
        return

    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        new_db = FAISS.load_local(
            "faiss_index", 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        response = chain.invoke({
            "context": docs,
            "input": user_question
        })

        st.write("Reply:", response)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")



def get_conversational_chain():
    """Create a conversational chain for Q&A"""
    prompt_template = """
    Answer the question as detailed as possible from the provided context.
    If the answer is not in the context, say "answer is not available in the context".
    
    Context: 
    {context}
    
    Question: 
    {input}

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "input"])
    
    chain = create_stuff_documents_chain(llm=model, prompt=prompt)
    return chain

def user_input(user_question):
    if not os.path.exists("faiss_index"):
        st.error("⚠️ Please upload and process PDF files first!")
        return

    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        new_db = FAISS.load_local(
            "faiss_index", 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        # IMPORTANT: 'docs' must be a list of Document objects
        response = chain.invoke({
            "context": docs,  
            "input": user_question
        })

        st.write("Reply:", response)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")




def main():
    st.set_page_config(page_title="Chat with PDF", page_icon="📚")
    st.header("Chat with PDF using Gemini 💁")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader(
            "Upload your PDF Files and Click on the Submit & Process Button", 
            accept_multiple_files=True,
            type=['pdf']
        )
        
        if st.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("✅ Done! You can now ask questions.")
            else:
                st.warning("Please upload at least one PDF file.")


if __name__ == "__main__":
    main()