import io
from typing import List, Tuple

import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(file: io.BytesIO) -> str:
    reader = PdfReader(file)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)


def chunk_text(text: str, max_chars: int = 800) -> List[str]:
    chunks = []
    current = []
    current_len = 0
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if current_len + len(paragraph) > max_chars:
            chunks.append(" ".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += len(paragraph)
    if current:
        chunks.append(" ".join(current))
    return chunks


def build_vector_store(chunks: List[str]):
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)
    return vectorizer, matrix


def ensure_rag_state():
    if "rag_store" not in st.session_state:
        st.session_state["rag_store"] = {
            "chunks": [],
            "vectorizer": None,
            "matrix": None,
        }


def ingest_pdfs(files: List[io.BytesIO]):
    ensure_rag_state()
    all_chunks = []
    for f in files:
        try:
            text = extract_text_from_pdf(f)
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
        except Exception as e:
            st.error(f"Failed to process PDF: {e}")
    if not all_chunks:
        st.warning("No valid text extracted from PDFs.")
        return

    vectorizer, matrix = build_vector_store(all_chunks)
    st.session_state["rag_store"] = {
        "chunks": all_chunks,
        "vectorizer": vectorizer,
        "matrix": matrix,
    }
    st.success(f"Indexed {len(all_chunks)} text chunks from uploaded PDFs.")


def retrieve_relevant_context(query: str, top_k: int = 4) -> Tuple[str, List[Tuple[str, float]]]:
    ensure_rag_state()
    store = st.session_state["rag_store"]
    if not store["chunks"] or store["vectorizer"] is None:
        return "", []

    vectorizer = store["vectorizer"]
    matrix = store["matrix"]
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, matrix).flatten()
    if sims.max() <= 0:
        return "", []

    indices = sims.argsort()[::-1][:top_k]
    selected = [(store["chunks"][i], float(sims[i])) for i in indices]
    context = "\n\n".join([c for c, _ in selected])
    return context, selected
