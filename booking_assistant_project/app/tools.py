from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, time

import streamlit as st
from email_validator import validate_email, EmailNotValidError

from db.database import SessionLocal, engine
from db.models import Base, Customer, Booking
from .config import get_email_config


# Ensure tables exist
Base.metadata.create_all(bind=engine)


def validate_email_address(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def booking_persistence_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist booking in SQLite and return booking ID."""
    session = SessionLocal()
    try:
        name = payload["name"]
        email = payload["email"]
        phone = payload["phone"]
        booking_type = payload["booking_type"]
        b_date: date = payload["date"]
        b_time: time = payload["time"]

        # Upsert customer (simple: find by email+phone)
        customer = (
            session.query(Customer)
            .filter(Customer.email == email, Customer.phone == phone)
            .first()
        )
        if not customer:
            customer = Customer(name=name, email=email, phone=phone)
            session.add(customer)
            session.flush()

        booking = Booking(
            customer_id=customer.customer_id,
            booking_type=booking_type,
            date=b_date,
            time=b_time,
            status="CONFIRMED",
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)

        return {"success": True, "booking_id": booking.id}
    except Exception as e:
        session.rollback()
        st.error(f"DB error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        session.close()


def email_tool(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    cfg = get_email_config()
    if not cfg or not cfg.get("username") or not cfg.get("password"):
        return {"success": False, "error": "Email is not configured in secrets."}

    msg = MIMEMultipart()
    msg["From"] = f"{cfg['from_name']} <{cfg['username']}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.starttls()
            server.login(cfg["username"], cfg["password"])
            server.send_message(msg)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
