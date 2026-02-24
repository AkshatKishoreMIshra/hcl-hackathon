from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.models import UserRole, OrderStatus, TicketStatus, EventStatus, RefundStatus, SupportStatus, SeatStatus

# User Schemas
class UserBase(BaseModel):
    name: str
    email: str
    role: UserRole

class UserCreate(UserBase):
    name: str
    email: str
    password: str = Field(
        min_length=6,
        max_length=72  # 👈 ADD THIS
    )

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# Venue Schemas
class VenueBase(BaseModel):
    name: str
    city: str
    address: str
    total_capacity: int

class VenueCreate(VenueBase):
    pass

class VenueResponse(VenueBase):
    id: int
    class Config:
        from_attributes = True

# Event Schemas
class EventBase(BaseModel):
    name: str
    category: str
    event_date: datetime
    ticket_price: float
    max_tickets_per_user: int
    venue_id: int

class EventCreate(EventBase):
    pass

class EventUpdateStatus(BaseModel):
    status: EventStatus

class EventResponse(EventBase):
    id: int
    status: EventStatus
    class Config:
        from_attributes = True

# Seat Schemas
class SeatBase(BaseModel):
    event_id: int
    seat_number: str

class SeatCreate(BaseModel):
    event_id: int
    seat_count: int # To create multiple seats at once

class SeatResponse(SeatBase):
    id: int
    status: SeatStatus
    class Config:
        from_attributes = True

# Order Schemas
class OrderCreate(BaseModel):
    event_id: int
    seat_ids: List[int]
    payment_mode: str

class OrderResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    total_amount: float
    payment_mode: str
    order_status: OrderStatus
    booking_time: datetime
    class Config:
        from_attributes = True

# Ticket Schemas
class TicketResponse(BaseModel):
    id: int
    order_id: int
    seat_id: int
    ticket_code: str
    status: TicketStatus
    generated_at: datetime
    class Config:
        from_attributes = True

# Refund Schemas
class RefundRequestCreate(BaseModel):
    order_id: int
    reason: str

class RefundUpdate(BaseModel):
    status: RefundStatus
    resolution_note: Optional[str] = None

class RefundResponse(BaseModel):
    id: int
    order_id: int
    reason: str
    status: RefundStatus
    resolution_note: Optional[str] = None
    class Config:
        from_attributes = True

# Support Schemas
class SupportCaseCreate(BaseModel):
    subject: str
    description: str

class SupportCaseUpdate(BaseModel):
    status: SupportStatus
    resolution_note: Optional[str] = None

class SupportCaseResponse(SupportCaseCreate):
    id: int
    user_id: int
    status: SupportStatus
    resolution_note: Optional[str] = None
    class Config:
        from_attributes = True

# Ticket Validation
class TicketValidationResponse(BaseModel):
    is_valid: bool
    message: str
    ticket_id: Optional[int] = None
    event_name: Optional[str] = None
    seat_number: Optional[str] = None
