import os
import pickle
import PyPDF2
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# --- Document Loading and Parsing ---

def get_document_text(uploaded_files):
    """
    Extracts text from a list of uploaded files (PDFs and DOCX).

    Args:
        uploaded_files: A list of Streamlit UploadedFile objects.

    Returns:
        A single string containing the concatenated text from all documents.
    """
    text = ""
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    return text


# --- Text Chunking ---

def get_text_chunks(text):
    """
    Splits a long string of text into smaller, manageable chunks.

    Args:
        text: The input string.

    Returns:
        A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000
    )
    chunks = text_splitter.split_text(text)
    return chunks


# --- Vector Store Creation ---

def get_vector_store(text_chunks):
    """
    Creates and saves a FAISS vector store from text chunks.

    This function generates embeddings for each text chunk using Google's AI
    and stores them in a FAISS index for efficient similarity searching.
    The created vector store is saved to a local file for reuse.

    Args:
        text_chunks: A list of text chunks.
    """
    if not text_chunks:
        return

    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

        # Save the vector store locally
        with open("faiss_vector_store.pkl", "wb") as f:
            pickle.dump(vector_store, f)

    except Exception as e:
        print(f"An error occurred during vector store creation: {e}")
        # Potentially handle specific exceptions for API errors, etc.


def process_documents(uploaded_files):
    """
    Main function to orchestrate document processing.

    Args:
        uploaded_files: List of files uploaded via Streamlit.

    Returns:
        True if processing was successful, False otherwise.
    """
    if not uploaded_files:
        return False

    raw_text = get_document_text(uploaded_files)
    if not raw_text:
        return False

    text_chunks = get_text_chunks(raw_text)
    if not text_chunks:
        return False

    get_vector_store(text_chunks)

    return True