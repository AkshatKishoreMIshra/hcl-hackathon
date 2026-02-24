from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import SupportCase, RefundRequest, UserRole, RefundStatus, SupportStatus
from app.schemas.schemas import SupportCaseResponse, SupportCaseUpdate, RefundResponse, RefundUpdate
from app.utils.deps import RoleChecker
from app.services.booking_service import process_refund

router = APIRouter(prefix="/support", tags=["Support"], dependencies=[Depends(RoleChecker([UserRole.SUPPORT]))])

@router.get("/cases", response_model=list[SupportCaseResponse])
def view_support_cases(db: Session = Depends(get_db)):
    return db.query(SupportCase).all()

@router.patch("/cases/{case_id}", response_model=SupportCaseResponse)
def update_case(case_id: int, case_in: SupportCaseUpdate, db: Session = Depends(get_db)):
    case = db.query(SupportCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = case_in.status
    if case_in.resolution_note:
        case.resolution_note = case_in.resolution_note
    db.commit()
    db.refresh(case)
    return case

@router.get("/refunds", response_model=list[RefundResponse])
def view_refund_requests(db: Session = Depends(get_db)):
    return db.query(RefundRequest).all()

@router.post("/refunds/{refund_id}/process")
def process_refund_request(refund_id: int, refund_in: RefundUpdate, db: Session = Depends(get_db)):
    return process_refund(db, refund_id, refund_in.status, refund_in.resolution_note)
