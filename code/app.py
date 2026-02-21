import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

from book_loader import download_book
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv

# UI imports — new page-router based ui
from ui import load_css, sidebar_ui, library_page, search_page, reader_page
from htmlTemplates import welcome_card

load_dotenv()




# =========================
# SESSION STATE
# =========================

def init_state():
    defaults = {
        "chat_history": [],
        "active_book":  None,
        "page":         "library",   # "library" | "search" | "upload" | "reader"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# =========================
# EMBEDDINGS CACHE
# =========================

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# =========================
# PDF TEXT
# =========================

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text


# =========================
# TEXT CHUNKS
# =========================

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=500
    )
    return splitter.split_text(text)


# =========================
# VECTOR STORE
# =========================

def get_vector_store(chunks):
    embeddings = load_embeddings()
    db = FAISS.from_texts(chunks, embedding=embeddings)
    db.save_local("faiss_index")


# =========================
# LOAD BOOK FROM WEB
# NOTE: @st.cache_data caches by URL — same URL returns instantly.
# When a NEW book is selected the URL changes so it re-downloads & re-indexes.
# =========================

@st.cache_data(show_spinner=False)
def load_book_from_web(url: str) -> int:
    """Download, chunk, and index a Gutenberg book. Returns chunk count."""
    text   = download_book(url)
    chunks = get_text_chunks(text)
    get_vector_store(chunks)
    return len(chunks)


# =========================
# AI CHAIN
# =========================

def get_chain():
    prompt_template = """
You are an expert literary assistant helping readers understand and explore books.
Answer questions using ONLY the provided context from the book.

If the answer is not found in the context, respond with:
"That information isn't in the loaded text. Try asking something else about the book."

Be insightful and detailed. Quote relevant passages when helpful.

Context:
{context}

Question:
{input}

Answer:
"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "input"]
    )
    # create_stuff_documents_chain returns a RUNNABLE whose .invoke() returns a STRING
    # not a dict — so we do NOT call .get("answer") on it
    return create_stuff_documents_chain(llm=model, prompt=prompt)


# =========================
# ASK QUESTION
# FIX: chain.invoke() returns a plain string, not a dict
# =========================

def ask_question(question: str) -> str:
    if not os.path.exists("faiss_index"):
        return "No book is loaded yet. Please load a book from the library or upload a PDF."

    embeddings = load_embeddings()
    db = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs   = db.similarity_search(question, k=4)
    chain  = get_chain()

    # invoke returns a str directly — NOT a dict
    answer = chain.invoke({"context": docs, "input": question})

    # If somehow a dict slips through, handle gracefully
    if isinstance(answer, dict):
        answer = answer.get("answer") or answer.get("output") or str(answer)

    st.session_state.chat_history.append(("User", question))
    st.session_state.chat_history.append(("Bot", answer))

    return answer


# =========================
# MAIN — PAGE ROUTER
# =========================

def main():
    st.set_page_config(
        page_title="BookChat — AI Literature Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()

    # Sidebar is always visible (nav + upload + status)
    sidebar_ui(get_pdf_text, get_text_chunks, get_vector_store)

    # ── Route to the correct page ──
    page = st.session_state.get("page", "library")

    if page == "library":
        library_page(load_book_from_web)

    elif page == "search":
        search_page(load_book_from_web)

    elif page == "upload":
        if not os.path.exists("faiss_index"):
            st.markdown(welcome_card, unsafe_allow_html=True)
        else:
            book  = st.session_state.get("active_book") or {}
            emoji = book.get("emoji", "📄")
            title = book.get("title", "Document loaded")
            st.markdown(f"""
            <div style="text-align:center;padding:60px 24px;">
                <div style="font-size:52px;margin-bottom:16px;">{emoji}</div>
                <div style="font-family:'Lora',serif;font-size:20px;font-weight:700;
                            color:#1a1a2e;margin-bottom:8px;">{title}</div>
                <div style="font-size:14px;color:#6b6880;">Ready to chat!</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💬 Open Reader →", key="go_reader_upload"):
                st.session_state.page = "reader"
                st.rerun()

    elif page == "reader":
        reader_page(ask_question)


# =========================
if __name__ == "__main__":
    main()