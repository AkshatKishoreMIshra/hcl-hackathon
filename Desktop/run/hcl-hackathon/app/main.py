from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, admin, organizer, customer, entry_manager, support
from app.models import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Online Event Ticket Booking Platform")

# Include Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(organizer.router)
app.include_router(customer.router)
app.include_router(entry_manager.router)
app.include_router(support.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Online Event Ticket Booking Platform API"}
