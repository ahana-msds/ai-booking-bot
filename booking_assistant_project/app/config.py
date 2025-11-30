import streamlit as st


def get_gemini_api_key() -> str:
    try:
        return st.secrets["gemini"]["api_key"]
    except Exception:
        return ""


def get_email_config():
    try:
        email_secrets = st.secrets["email"]
        return {
            "smtp_host": email_secrets.get("smtp_host", "smtp.gmail.com"),
            "smtp_port": int(email_secrets.get("smtp_port", 587)),
            "username": email_secrets.get("username"),
            "password": email_secrets.get("password"),
            "from_name": email_secrets.get("from_name", "AI Booking Assistant"),
        }
    except Exception:
        return None
