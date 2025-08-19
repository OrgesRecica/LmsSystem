from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, UserRole
from schemas import User as UserSchema
from auth import get_current_active_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserSchema])
async def get_users(
    role: UserRole = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (Admin only)"""
    query = db.query(User).filter(User.is_active == True)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    return users

@router.get("/teachers", response_model=List[UserSchema])
async def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all teachers"""
    teachers = db.query(User).filter(
        User.role == UserRole.TEACHER,
        User.is_active == True
    ).all()
    return teachers

@router.get("/students", response_model=List[UserSchema])
async def get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all students"""
    students = db.query(User).filter(
        User.role == UserRole.STUDENT,
        User.is_active == True
    ).all()
    return students

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific user"""
    # Users can see their own profile, admins can see all
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Deactivate user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot deactivate admin users")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}
