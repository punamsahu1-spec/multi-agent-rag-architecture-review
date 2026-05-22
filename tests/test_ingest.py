from agents.ingest_agent import load_document, chunk_documents


def test_load_document():
    docs = load_document("standards_docs/rfc_template_standard.md")

    assert len(docs) > 0
    assert len(docs[0].page_content) > 100
    assert "source" in docs[0].metadata


def test_chunk_documents():
    docs = load_document("standards_docs/rfc_template_standard.md")
    chunks = chunk_documents(docs, chunk_size=300, chunk_overlap=30)

    assert len(chunks) > 0

    for chunk in chunks:
        assert len(chunk.page_content) <= 450

    assert "chunk_id" in chunks[0].metadata
    assert "chunk_size" in chunks[0].metadata


def test_chunk_overlap_basic_sanity():
    docs = load_document("standards_docs/rfc_template_standard.md")
    chunks = chunk_documents(docs, chunk_size=300, chunk_overlap=50)

    assert len(chunks) > 1