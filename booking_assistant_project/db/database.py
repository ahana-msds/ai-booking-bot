from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st

Base = declarative_base()

def get_database_url() -> str:
    # Use Streamlit secrets
    try:
        return st.secrets["database"]["url"]
    except Exception:
        # Fallback to local SQLite
        return "sqlite:///booking.db"

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
