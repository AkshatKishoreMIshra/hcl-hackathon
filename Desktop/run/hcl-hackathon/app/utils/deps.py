from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, UserRole

def get_current_user(
    db: Session = Depends(get_db),
    x_user_email: str = Header(...)
):
    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid credentials"
        )
    return user

def RoleChecker(allowed_roles: list[UserRole]):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} is not authorized. Required: {[r.value for r in allowed_roles]}"
            )
        return user
    return checker
