# AI Booking Assistant – Streamlit + RAG (Gemini)

This project implements an AI-driven Booking Assistant with:

- Chat-based interface using Streamlit
- PDF-based RAG (Retrieval Augmented Generation)
- Conversational booking flow with slot filling
- SQLite persistence for customers and bookings
- Email confirmation after successful booking
- Admin dashboard to view/search bookings
- Short-term conversation memory
- Gemini (Google Generative AI) as the LLM backend

## Quick Start

1. Install dependencies (locally or in Streamlit Cloud):

```bash
pip install -r requirements.txt
```

2. Set secrets in `.streamlit/secrets.toml` (see provided template).

3. Run the app:

```bash
streamlit run app/main.py
```

4. Open the browser URL shown in the terminal to use the assistant.

## Notes

- Booking domain: **Salon / Spa** (you can rename labels in `booking_flow.py`).
- RAG uses simple TF-IDF similarity over uploaded PDFs and LLM responses from Gemini.
- SQLite DB is created automatically as `booking.db` in the project root.
