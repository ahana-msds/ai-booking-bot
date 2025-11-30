from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=False, index=True)
    phone = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="customer")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    booking_type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(String, default="CONFIRMED")
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="bookings")
