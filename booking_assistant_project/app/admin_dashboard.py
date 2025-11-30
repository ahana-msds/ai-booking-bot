from typing import Optional
from datetime import date

import streamlit as st
from sqlalchemy import select, and_

from db.database import SessionLocal
from db.models import Booking, Customer


def render_admin_dashboard():
    st.header("Admin Dashboard - Bookings")

    name_filter = st.text_input("Filter by customer name (contains):")
    email_filter = st.text_input("Filter by email (contains):")
    date_filter: Optional[date] = st.date_input(
        "Filter by date (optional):", value=None, key="admin_date_filter"
    )

    session = SessionLocal()
    try:
        stmt = (
            select(Booking, Customer)
            .join(Customer, Booking.customer_id == Customer.customer_id)
            .order_by(Booking.created_at.desc())
        )

        conditions = []
        if name_filter:
            conditions.append(Customer.name.ilike(f"%{name_filter}%"))
        if email_filter:
            conditions.append(Customer.email.ilike(f"%{email_filter}%"))
        if date_filter:
            conditions.append(Booking.date == date_filter)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        results = session.execute(stmt).all()

        if not results:
            st.info("No bookings found for the current filter.")
            return

        rows = []
        for booking, customer in results:
            rows.append(
                {
                    "Booking ID": booking.id,
                    "Customer": customer.name,
                    "Email": customer.email,
                    "Phone": customer.phone,
                    "Service": booking.booking_type,
                    "Date": booking.date,
                    "Time": booking.time,
                    "Status": booking.status,
                    "Created At": booking.created_at,
                }
            )

        st.dataframe(rows, use_container_width=True)
    finally:
        session.close()
