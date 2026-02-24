from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import User, UserRole, Venue, Event, EventStatus
from app.utils.security import get_password_hash
import datetime

def seed_data():
    db = SessionLocal()
    
    # 1. Seed Users
    users = [
        {"name": "System Admin", "email": "admin@event.com", "password": "adminpassword", "role": UserRole.ADMIN},
        {"name": "John Organizer", "email": "organizer@event.com", "password": "orgpassword", "role": UserRole.ORGANIZER},
        {"name": "Alice Customer", "email": "customer@event.com", "password": "custpassword", "role": UserRole.CUSTOMER},
        {"name": "Bob Entry", "email": "entry@event.com", "password": "entrypassword", "role": UserRole.ENTRY_MANAGER},
        {"name": "Charlie Support", "email": "support@event.com", "password": "supportpassword", "role": UserRole.SUPPORT},
    ]

    for u in users:
        db_user = db.query(User).filter(User.email == u["email"]).first()
        if not db_user:
            new_user = User(
                name=u["name"],
                email=u["email"],
                password=get_password_hash(u["password"]),
                role=u["role"].value
            )
            db.add(new_user)
    
    # 2. Seed a Venue
    venue = db.query(Venue).filter(Venue.name == "Grand Plaza").first()
    if not venue:
        venue = Venue(name="Grand Plaza", city="New York", address="123 Main St", total_capacity=100)
        db.add(venue)
        db.flush()

    # 3. Seed an Event
    event = db.query(Event).filter(Event.name == "Tech Conference 2026").first()
    if not event:
        event = Event(
            name="Tech Conference 2026",
            category="Technology",
            event_date=datetime.datetime(2026, 12, 31, 10, 0),
            ticket_price=150.0,
            max_tickets_per_user=5,
            status=EventStatus.UPCOMING,
            venue_id=venue.id
        )
        db.add(event)

    db.commit()
    db.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
