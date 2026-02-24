from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Venue, Event, UserRole, EventStatus
from app.schemas.schemas import VenueCreate, VenueResponse, EventCreate, EventResponse, EventUpdateStatus
from app.utils.deps import RoleChecker

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])

@router.post("/venues", response_model=VenueResponse)
def add_venue(venue_in: VenueCreate, db: Session = Depends(get_db)):
    db_venue = Venue(**venue_in.dict())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

@router.post("/events", response_model=EventResponse)
def add_event(event_in: EventCreate, db: Session = Depends(get_db)):
    # Check if venue exists
    venue = db.query(Venue).get(event_in.venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    db_event = Event(**event_in.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.patch("/events/{event_id}/status", response_model=EventResponse)
def update_event_status(event_id: int, status_in: EventUpdateStatus, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = status_in.status
    db.commit()
    db.refresh(event)
    return event
