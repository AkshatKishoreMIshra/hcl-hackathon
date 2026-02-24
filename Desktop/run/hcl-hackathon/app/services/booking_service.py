from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import Event, Seat, Order, Ticket, OrderStatus, TicketStatus, EventStatus, SeatStatus, User, RefundRequest, RefundStatus
import datetime
from typing import List

def create_booking(db: Session, user_id: int, event_id: int, seat_ids: List[int], payment_mode: str):
    # Business Rules
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # 1. Booking allowed only for upcoming events.
    if event.status != EventStatus.UPCOMING:
        raise HTTPException(status_code=400, detail="Event is not open for booking")
    
    # 2. Ticket becomes invalid after event date (implicit check)
    if event.event_date < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="Event has already passed")

    # 3. User cannot exceed max_tickets_per_user per event.
    existing_orders = db.query(Order).filter(Order.user_id == user_id, Order.event_id == event_id, Order.order_status != OrderStatus.CANCELLED).all()
    existing_ticket_count = sum(len(order.tickets) for order in existing_orders)
    if existing_ticket_count + len(seat_ids) > event.max_tickets_per_user:
        raise HTTPException(status_code=400, detail=f"Exceeds max tickets per user ({event.max_tickets_per_user})")

    # 7. Seat cannot be double booked (Race condition prevention using transaction and checking status)
    # We use db.begin_nested() or just the standard session transaction.
    # We lock the seats for update if possible, but SQLite has limited locking. 
    # For SQLite, a simple check within the same transaction is usually enough if serializable.
    
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids), Seat.event_id == event_id).with_for_update().all()
    if len(seats) != len(seat_ids):
        raise HTTPException(status_code=400, detail="Some seats not found for this event")
    
    for seat in seats:
        if seat.status != SeatStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail=f"Seat {seat.seat_number} is already booked")

    # Calculate total amount
    total_amount = event.ticket_price * len(seat_ids)

    # Create Order
    new_order = Order(
        user_id=user_id,
        event_id=event_id,
        total_amount=total_amount,
        payment_mode=payment_mode,
        order_status=OrderStatus.CONFIRMED # Simulating payment confirmed
    )
    db.add(new_order)
    db.flush() # Get order ID

    # Update seats and create tickets
    for seat in seats:
        seat.status = SeatStatus.BOOKED
        ticket = Ticket(
            order_id=new_order.id,
            seat_id=seat.id,
            status=TicketStatus.ACTIVE
        )
        db.add(ticket)

    db.commit()
    db.refresh(new_order)
    return new_order

def process_refund(db: Session, refund_request_id: int, status: RefundStatus, note: str):
    # Rule 5: If refund approved: Order=refunded, Seat=available, Ticket=cancelled
    refund_req = db.query(RefundRequest).get(refund_request_id)
    if not refund_req:
        raise HTTPException(status_code=404, detail="Refund request not found")
    
    if refund_req.status != RefundStatus.PENDING:
        raise HTTPException(status_code=400, detail="Refund request already processed")
    
    order = refund_req.order
    event = order.event

    # Rule 4: Refund allowed only before event_date.
    if event.event_date < datetime.datetime.utcnow():
        refund_req.status = RefundStatus.REJECTED
        refund_req.resolution_note = "Event date passed. Refund not allowed."
        db.commit()
        raise HTTPException(status_code=400, detail="Refund not allowed after event date")

    refund_req.status = status
    refund_req.resolution_note = note

    if status == RefundStatus.APPROVED:
        order.order_status = OrderStatus.REFUNDED
        for ticket in order.tickets:
            ticket.status = TicketStatus.CANCELLED
            seat = ticket.seat
            seat.status = SeatStatus.AVAILABLE
    
    db.commit()
    return refund_req
