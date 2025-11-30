from typing import Literal

import streamlit as st


def ensure_memory():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


def append_message(role: Literal["user", "assistant"], content: str):
    ensure_memory()
    st.session_state["messages"].append({"role": role, "content": content})
    # Keep only last 25 messages
    st.session_state["messages"] = st.session_state["messages"][-25:]


def detect_intent(user_input: str) -> str:
    text = user_input.lower()
    booking_keywords = [
        "book",
        "booking",
        "appointment",
        "reservation",
        "schedule",
        "slot",
    ]
    if any(k in text for k in booking_keywords):
        return "booking"
    return "general"
