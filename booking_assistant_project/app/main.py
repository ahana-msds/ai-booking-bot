import streamlit as st

from app.chat_logic import append_message, detect_intent, ensure_memory
from app.booking_flow import booking_flow_step, general_query_answer
from app.rag_pipeline import ingest_pdfs
from app.admin_dashboard import render_admin_dashboard


st.set_page_config(page_title="AI Booking Assistant (Gemini)", layout="wide")

st.title("‍ AI Salon Booking Assistant (Gemini)")
st.caption("Chat-based RAG + Booking system with Admin Dashboard, powered by Google Gemini")


def render_sidebar():
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to:",
            options=["Chat Assistant", "Admin Dashboard"],
            index=0,
        )
        st.markdown("---")
        st.subheader("Upload PDFs for RAG")
        uploaded_files = st.file_uploader(
            "Upload policy/FAQ PDFs",
            type=["pdf"],
            accept_multiple_files=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Index PDFs") and uploaded_files:
                ingest_pdfs(uploaded_files)
        with col2:
            if st.button("Clear PDFs"):
                if "rag_store" in st.session_state:
                    del st.session_state["rag_store"]
                st.success("Cleared indexed PDF context.")

        return page


def render_chat_page():
    ensure_memory()
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question or start a booking request...")
    if user_input:
        append_message("user", user_input)
        intent = detect_intent(user_input)
        with st.chat_message("assistant"):
            if intent == "booking":
                reply = booking_flow_step(user_input)
            else:
                reply = general_query_answer(user_input)
            st.markdown(reply)
            append_message("assistant", reply)


def main():
    page = render_sidebar()
    if page == "Chat Assistant":
        render_chat_page()
    else:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
