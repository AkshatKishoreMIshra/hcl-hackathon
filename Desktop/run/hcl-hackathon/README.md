# Online Event Ticket Booking Platform

A complete FastAPI-based backend for managing event ticket bookings.

## Tech Stack
- FastAPI
- SQLAlchemy (SQLite)
- Pydantic
- Passlib (Bcrypt)

## Folder Structure
```
app/
 ├── main.py            # Entry point
 ├── database.py        # DB config
 ├── models/            # SQLAlchemy models
 ├── schemas/           # Pydantic schemas
 ├── routers/           # API routes by role
 ├── services/          # Business logic
 ├── utils/             # Security & Dependencies
 ├── seed.py            # Initial data
```

## Setup & Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Seed Initial Data**
   ```bash
   python -m app.seed
   ```

3. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access Swagger UI**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## Authentication (Role Simulation)
The application uses two mandatory headers for authentication (no JWT):
- `X-User-Email`: The email of the registered user.
- `X-Role`: The role of the user (must match the database).

Available Seed Users:
- **Admin**: `admin@event.com` / `adminpassword`
- **Organizer**: `organizer@event.com` / `orgpassword`
- **Customer**: `customer@event.com` / `custpassword`
- **Entry Manager**: `entry@event.com` / `entrypassword`
- **Support**: `support@event.com` / `supportpassword`

## Sample Payload for Ordering (Customer)
**Endpoint**: `POST /customer/orders`
**Headers**:
- `X-User-Email`: `customer@event.com`
- `X-Role`: `customer`

**Body**:
```json
{
  "event_id": 1,
  "seat_ids": [1, 2],
  "payment_mode": "Credit Card"
}
```

## Business Rules Implemented
1. **Booking upcoming events only.**
2. **Ticket invalid after event date.**
3. **Max tickets per user per event enforcement.**
4. **Refund allowed only before event date.**
5. **Atomic refund logic** (Order=refunded, Seat=available, Ticket=cancelled).
6. **Ticket invalid once marked as used.**
7. **Seat double-booking prevention** (via transaction block and status checks).
8. **Proper HTTP status codes and error messages.**
