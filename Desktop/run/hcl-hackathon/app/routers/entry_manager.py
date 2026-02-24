from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Ticket, EntryLog, UserRole, TicketStatus, EventStatus
from app.utils.deps import RoleChecker, get_current_user
import datetime

router = APIRouter(prefix="/entry-manager", tags=["Entry Manager"], dependencies=[Depends(RoleChecker([UserRole.ENTRY_MANAGER]))])

@router.post("/tickets/validate/{ticket_code}")
def validate_ticket(ticket_code: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()
    if not ticket:
        return {"is_valid": False, "message": "Ticket not found"}
    
    # Rule 6: Ticket becomes invalid once marked as used.
    if ticket.status == TicketStatus.USED:
        return {"is_valid": False, "message": "Ticket already used"}
    
    if ticket.status == TicketStatus.CANCELLED:
        return {"is_valid": False, "message": "Ticket is cancelled"}

    # Rule 2: Ticket becomes invalid after event date.
    if ticket.order.event.event_date < datetime.datetime.utcnow():
        return {"is_valid": False, "message": "Event is over"}

    return {
        "is_valid": True, 
        "message": "Ticket is valid",
        "ticket_id": ticket.id,
        "event_name": ticket.order.event.name,
        "seat_number": ticket.seat.seat_number
    }

@router.post("/tickets/{ticket_id}/mark-used")
def mark_ticket_used(ticket_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.status != TicketStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Ticket is {ticket.status}")

    ticket.status = TicketStatus.USED
    
    # Log entry
    log = EntryLog(ticket_id=ticket_id, validated_by=current_user.id, status="valid")
    db.add(log)
    db.commit()
    
    return {"message": "Ticket marked as used"}
