import glob
import os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Add it to .env in the project root."
    )


EMBED_MODEL = "gemini-embedding-001"
VECTORSTORE_PATH = "vectorstore"
COLLECTION_STANDARDS = "rfc_standards"
COLLECTION_RFC = "rfc_upload"


embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBED_MODEL,
    google_api_key=GOOGLE_API_KEY,
)

def load_document(file_path: str) -> List[Document]:
    """
    Loads a markdown or text document using plain Python.
    Handles common Windows encoding issues.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp1252")

    doc = Document(
        page_content=text,
        metadata={
            "source": str(path)
        }
    )

    print(f"[INGEST] Loaded: {file_path} (1 document object)")
    return [doc]

def chunk_documents(
    docs: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    Splits documents into chunks using RecursiveCharacterTextSplitter.

    Why this splitter:
    - It tries larger semantic breaks first.
    - It avoids breaking text randomly where possible.
    - Overlap preserves context across chunk boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(docs)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    if chunks:
        avg_size = sum(len(chunk.page_content) for chunk in chunks) // len(chunks)
    else:
        avg_size = 0

    print(f"[INGEST] Chunked → {len(chunks)} chunks, avg size={avg_size} chars")
    return chunks


def store_in_vectordb(
    chunks: List[Document],
    collection_name: str = COLLECTION_STANDARDS,
) -> Chroma:
    """
    Embeds chunks and stores them in ChromaDB.
    """
    if not chunks:
        raise ValueError("No chunks provided for vector store ingestion.")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH,
        collection_name=collection_name,
    )

    print(f"[INGEST] Stored {len(chunks)} chunks → collection: {collection_name}")
    return vectorstore


def seed_standards() -> Chroma:
    """
    Ingests all standards docs into the RFC standards collection.
    """
    all_chunks = []

    for file_path in glob.glob("standards_docs/*.md"):
        docs = load_document(file_path)
        chunks = chunk_documents(docs)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No standards docs found in standards_docs/")

    return store_in_vectordb(all_chunks, COLLECTION_STANDARDS)


def ingest_rfc(file_path: str) -> Tuple[Chroma, List[Document]]:
    """
    Ingests one RFC document into the RFC upload collection.
    """
    docs = load_document(file_path)
    chunks = chunk_documents(docs, chunk_size=400, chunk_overlap=80)
    vectorstore = store_in_vectordb(chunks, COLLECTION_RFC)

    return vectorstore, chunks


if __name__ == "__main__":
    print("=== Seeding Standards Knowledge Base ===")
    seed_standards()
    print("=== Done ===")