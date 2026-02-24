from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Seat, Event, UserRole, Order, SeatStatus, EventStatus
from app.schemas.schemas import SeatCreate, SeatResponse
from app.utils.deps import RoleChecker

router = APIRouter(prefix="/organizer", tags=["Organizer"], dependencies=[Depends(RoleChecker([UserRole.ORGANIZER]))])

@router.post("/events/{event_id}/seats")
def create_seats(event_id: int, seat_in: SeatCreate, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if seats already created or capacity exceeded
    existing_seats = db.query(Seat).filter(Seat.event_id == event_id).count()
    if existing_seats + seat_in.seat_count > event.venue.total_capacity:
         raise HTTPException(status_code=400, detail=f"Cannot exceed venue capacity ({event.venue.total_capacity})")

    new_seats = []
    for i in range(1, seat_in.seat_count + 1):
        seat_num = f"S-{existing_seats + i}"
        new_seat = Seat(event_id=event_id, seat_number=seat_num, status=SeatStatus.AVAILABLE)
        db.add(new_seat)
        new_seats.append(new_seat)
    
    db.commit()
    return {"message": f"{seat_in.seat_count} seats created for event {event_id}"}

@router.get("/events/{event_id}/booking-summary")
def view_booking_summary(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    total_seats = db.query(Seat).filter(Seat.event_id == event_id).count()
    booked_seats = db.query(Seat).filter(Seat.event_id == event_id, Seat.status == SeatStatus.BOOKED).count()
    total_revenue = sum(order.total_amount for order in event.orders if order.order_status == "confirmed")

    return {
        "event_name": event.name,
        "total_seats": total_seats,
        "booked_seats": booked_seats,
        "available_seats": total_seats - booked_seats,
        "total_revenue": total_revenue
    }

@router.post("/events/{event_id}/close-bookings")
def close_bookings(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = EventStatus.CLOSED
    db.commit()
    return {"message": "Bookings closed for event"}
