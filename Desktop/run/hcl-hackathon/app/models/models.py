from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import enum
import uuid

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    CUSTOMER = "customer"
    ENTRY_MANAGER = "entry_manager"
    SUPPORT = "support"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TicketStatus(str, enum.Enum):
    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"

class EventStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class SupportStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String) # For simple role simulation

    orders = relationship("Order", back_populates="customer")
    support_cases = relationship("SupportCase", back_populates="user")

class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    city = Column(String)
    address = Column(String)
    total_capacity = Column(Integer)

    events = relationship("Event", back_populates="venue")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    event_date = Column(DateTime)
    ticket_price = Column(Float)
    max_tickets_per_user = Column(Integer)
    status = Column(String, default=EventStatus.UPCOMING)
    venue_id = Column(Integer, ForeignKey("venues.id"))

    venue = relationship("Venue", back_populates="events")
    seats = relationship("Seat", back_populates="event")
    orders = relationship("Order", back_populates="event")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    seat_number = Column(String)
    status = Column(String, default=SeatStatus.AVAILABLE)

    event = relationship("Event", back_populates="seats")
    ticket = relationship("Ticket", back_populates="seat", uselist=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    total_amount = Column(Float)
    payment_mode = Column(String)
    order_status = Column(String, default=OrderStatus.PENDING)
    booking_time = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("User", back_populates="orders")
    event = relationship("Event", back_populates="orders")
    tickets = relationship("Ticket", back_populates="order")
    refund_request = relationship("RefundRequest", back_populates="order", uselist=False)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    ticket_code = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default=TicketStatus.ACTIVE)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    order = relationship("Order", back_populates="tickets")
    seat = relationship("Seat", back_populates="ticket")
    entry_log = relationship("EntryLog", back_populates="ticket", uselist=False)

class RefundRequest(Base):
    __tablename__ = "refund_requests"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    reason = Column(String)
    status = Column(String, default=RefundStatus.PENDING)
    resolution_note = Column(String, nullable=True)

    order = relationship("Order", back_populates="refund_request")

class SupportCase(Base):
    __tablename__ = "support_cases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    description = Column(String)
    status = Column(String, default=SupportStatus.OPEN)
    resolution_note = Column(String, nullable=True)

    user = relationship("User", back_populates="support_cases")

class EntryLog(Base):
    __tablename__ = "entry_logs"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    validated_by = Column(Integer, ForeignKey("users.id"))
    validation_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String) # valid/invalid

    ticket = relationship("Ticket", back_populates="entry_log")
