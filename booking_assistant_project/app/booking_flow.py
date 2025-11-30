from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional

import streamlit as st
import google.generativeai as genai

from .tools import booking_persistence_tool, email_tool
from .rag_pipeline import retrieve_relevant_context
from .config import get_gemini_api_key


@dataclass
class BookingState:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    booking_type: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    confirmed: bool = False
    awaiting_confirmation: bool = False

    def is_complete(self) -> bool:
        return all(
            [
                self.name,
                self.email,
                self.phone,
                self.booking_type,
                self.date,
                self.time,
            ]
        )


def ensure_booking_state():
    if "booking_state" not in st.session_state:
        st.session_state["booking_state"] = BookingState()


def _parse_date(text: str) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except Exception:
            continue
    return None


def _parse_time(text: str) -> Optional[time]:
    for fmt in ("%H:%M", "%I:%M %p"):
        try:
            return datetime.strptime(text.strip(), fmt).time()
        except Exception:
            continue
    return None


def llm_answer(prompt: str, context: str = "") -> str:
    """Call Gemini with optional RAG context."""
    api_key = get_gemini_api_key()
    if not api_key:
        return (
            "Gemini API key is not configured in `.streamlit/secrets.toml` under [gemini].\n"
            "I can still show you the most relevant context from your PDFs:\n\n" + context[:800]
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        full_prompt = f"""You are a polite and helpful AI Booking Assistant for a salon/spa.
Use the following context from policy/FAQ PDFs when it is relevant to answer the user's query.

Context:
{context}

User question:
{prompt}
"""

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Failed to call Gemini: {e}"


def booking_flow_step(user_input: str) -> str:
    ensure_booking_state()
    state: BookingState = st.session_state["booking_state"]

    # If we are waiting for confirmation
    if state.awaiting_confirmation:
        text = user_input.lower()
        if any(k in text for k in ["yes", "confirm", "correct", "sure"]):
            payload = {
                "name": state.name,
                "email": state.email,
                "phone": state.phone,
                "booking_type": state.booking_type,
                "date": state.date,
                "time": state.time,
            }
            result = booking_persistence_tool(payload)
            if not result.get("success"):
                state.awaiting_confirmation = False
                return (
                    "I could not save your booking due to a system error, "
                    "but your details are noted. Please try again later."
                )

            booking_id = result["booking_id"]
            # Send email
            email_body = (
                f"Hi {state.name},\n\n"
                f"Your booking is confirmed.\n"
                f"Booking ID: {booking_id}\n"
                f"Service: {state.booking_type}\n"
                f"Date: {state.date}\n"
                f"Time: {state.time}\n\n"
                f"Thank you!"
            )
            email_res = email_tool(
                to_email=state.email,
                subject="Your Booking Confirmation",
                body=email_body,
            )
            if not email_res.get("success"):
                msg = (
                    f"Your booking is confirmed! ✅\n"
                    f"Booking ID: {booking_id}\n\n"
                    f"However, I couldn't send the email due to an error: "
                    f"{email_res.get('error', 'Unknown error')}"
                )
            else:
                msg = (
                    f"Your booking is confirmed! ✅\n"
                    f"Booking ID: {booking_id}\n"
                    f"A confirmation email has been sent to {state.email}."
                )

            # Reset state for next booking
            st.session_state["booking_state"] = BookingState()
            return msg
        elif any(k in text for k in ["no", "change", "edit", "wrong"]):
            state.awaiting_confirmation = False
            return "Okay, let's start over. Please tell me your *full name* for the booking."
        else:
            return "Please reply with **Yes** to confirm or **No** to modify your booking."

    # Slot filling
    if not state.name:
        state.name = user_input.strip()
        return "Got it. Please provide your *email address*."
    if not state.email:
        if "@" not in user_input or "." not in user_input:
            return "That doesn't look like a valid email. Please enter a valid email (e.g., name@example.com)."
        state.email = user_input.strip()
        return "Thanks. May I have your *phone number*?"
    if not state.phone:
        state.phone = user_input.strip()
        return "What kind of service would you like to book? (e.g., haircut, facial, spa session)"
    if not state.booking_type:
        state.booking_type = user_input.strip()
        return "Great. Please enter your preferred *date* in `YYYY-MM-DD` format."
    if not state.date:
        d = _parse_date(user_input)
        if not d:
            return "I couldn't understand the date. Please enter it as `YYYY-MM-DD`."
        state.date = d
        return "Now, please enter your preferred *time* in `HH:MM` (24h) or `HH:MM AM/PM` format."
    if not state.time:
        t = _parse_time(user_input)
        if not t:
            return "I couldn't understand the time. Please enter it as `HH:MM` (24h) or `HH:MM AM/PM`."
        state.time = t

    # Now we have all fields, summarize & ask for confirmation
    summary = (
        f"Please confirm your booking:\n"
        f"- Name: {state.name}\n"
        f"- Email: {state.email}\n"
        f"- Phone: {state.phone}\n"
        f"- Service: {state.booking_type}\n"
        f"- Date: {state.date}\n"
        f"- Time: {state.time}\n\n"
        f"Reply **Yes** to confirm or **No** to change details."
    )
    state.awaiting_confirmation = True
    return summary


def general_query_answer(user_input: str) -> str:
    # RAG + LLM answer using Gemini
    context, _ = retrieve_relevant_context(user_input)
    return llm_answer(user_input, context=context)
