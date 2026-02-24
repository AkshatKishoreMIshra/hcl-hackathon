from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Event, Seat, Order, Ticket, RefundRequest, SupportCase, UserRole, SeatStatus, EventStatus
from app.schemas.schemas import OrderCreate, OrderResponse, TicketResponse, RefundRequestCreate, SupportCaseCreate, SupportCaseResponse
from app.utils.deps import RoleChecker, get_current_user
from app.services.booking_service import create_booking
import datetime

router = APIRouter(prefix="/customer", tags=["Customer"], dependencies=[Depends(RoleChecker([UserRole.CUSTOMER]))])

@router.get("/events/upcoming")
def view_upcoming_events(db: Session = Depends(get_db)):
    return db.query(Event).filter(Event.status == EventStatus.UPCOMING, Event.event_date > datetime.datetime.utcnow()).all()

@router.get("/events/{event_id}/seats/available")
def view_available_seats(event_id: int, db: Session = Depends(get_db)):
    return db.query(Seat).filter(Seat.event_id == event_id, Seat.status == SeatStatus.AVAILABLE).all()

@router.post("/orders", response_model=OrderResponse)
def place_order(order_in: OrderCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return create_booking(db, current_user.id, order_in.event_id, order_in.seat_ids, order_in.payment_mode)

@router.get("/tickets", response_model=list[TicketResponse])
def view_my_tickets(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Ticket).join(Order).filter(Order.user_id == current_user.id).all()

@router.post("/refunds")
def request_refund(refund_in: RefundRequestCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == refund_in.order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if already requested
    existing = db.query(RefundRequest).filter(RefundRequest.order_id == refund_in.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Refund already requested for this order")

    new_refund = RefundRequest(order_id=refund_in.order_id, reason=refund_in.reason)
    db.add(new_refund)
    db.commit()
    return {"message": "Refund request submitted"}

@router.post("/support", response_model=SupportCaseResponse)
def raise_support_case(case_in: SupportCaseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_case = SupportCase(user_id=current_user.id, **case_in.dict())
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case
