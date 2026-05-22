import os
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from agents.ingest_agent import (
    VECTORSTORE_PATH,
    COLLECTION_STANDARDS,
    EMBED_MODEL,
)


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Add it to .env in the project root."
    )


TOP_K = 5


embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBED_MODEL,
    google_api_key=GOOGLE_API_KEY,
)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)


def get_vectorstore(collection_name: str = COLLECTION_STANDARDS) -> Chroma:
    """
    Opens the persisted ChromaDB vector store.
    """
    return Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings,
        collection_name=collection_name,
    )


def hyde_query_expansion(original_query: str) -> str:
    """
    HyDE = Hypothetical Document Embeddings.

    The LLM creates an ideal standards-style paragraph.
    That expanded text is used for retrieval.
    """
    prompt = f"""
Generate a short hypothetical enterprise architecture standards paragraph
that would answer this review question:

{original_query}

Rules:
- Write only the paragraph.
- Do not include markdown.
- Do not include explanations.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    expanded_query = response.content.strip()

    print(f"[RETRIEVE] HyDE expanded query: {expanded_query[:120]}...")
    return expanded_query


def retrieve_mmr(
    query: str,
    top_k: int = TOP_K,
) -> List[Document]:
    """
    Retrieves relevant standards chunks using MMR.

    MMR balances:
    - relevance to the query
    - diversity across returned chunks
    """
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": top_k,
            "fetch_k": top_k * 2,
            "lambda_mult": 0.6,
        },
    )

    docs = retriever.invoke(query)

    print(f"[RETRIEVE] MMR retrieved {len(docs)} chunks")
    return docs


def retrieve_with_fallback(
    query: str,
    use_hyde: bool = True,
    top_k: int = TOP_K,
) -> Tuple[List[Document], str]:
    """
    Retrieval fallback chain:
    1. Try HyDE + MMR.
    2. If HyDE fails, try direct query + MMR.
    3. If no docs found, return NO_CONTEXT.
    """
    retrieval_query = query

    if use_hyde:
        try:
            retrieval_query = hyde_query_expansion(query)
            docs = retrieve_mmr(retrieval_query, top_k=top_k)

            if docs:
                return docs, "OK_HYDE_MMR"
        except Exception as error:
            print(f"[RETRIEVE] HyDE failed. Falling back to direct MMR. Error: {error}")

    docs = retrieve_mmr(query, top_k=top_k)

    if docs:
        return docs, "OK_DIRECT_MMR"

    return [], "NO_CONTEXT"


def format_retrieved_docs(docs: List[Document]) -> str:
    """
    Formats retrieved docs for prompt context and UI display.
    """
    formatted = []

    for index, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")

        formatted.append(
            f"[Source {index}: {source}, chunk_id={chunk_id}]\n"
            f"{doc.page_content}"
        )

    return "\n\n---\n\n".join(formatted)


if __name__ == "__main__":
    question = "What security requirements must an RFC include?"

    docs, status = retrieve_with_fallback(question)

    print("\nRetrieval Status")
    print("----------------")
    print(status)

    print("\nRetrieved Documents")
    print("-------------------")

    for index, doc in enumerate(docs, start=1):
        print(f"\n{index}. Source: {doc.metadata.get('source')}")
        print(f"Chunk ID: {doc.metadata.get('chunk_id')}")
        print(doc.page_content[:500])