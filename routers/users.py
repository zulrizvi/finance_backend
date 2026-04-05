from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role
from schemas import UserResponse, UpdateRoleRequest, UpdateStatusRequest
from dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users"])

admin_only = Depends(require_role(Role.ADMIN))


@router.get("", response_model=list[UserResponse], dependencies=[admin_only])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.put("/{user_id}/role", response_model=UserResponse, dependencies=[admin_only])
def update_role(user_id: int, body: UpdateRoleRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/status", response_model=UserResponse, dependencies=[admin_only])
def update_status(user_id: int, body: UpdateStatusRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = body.status
    db.commit()
    db.refresh(user)
    return user
