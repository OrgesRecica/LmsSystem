from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Class, User, UserRole, Enrollment
from schemas import ClassCreate, Class as ClassSchema
from auth import get_current_active_user, require_teacher_or_admin, require_admin

router = APIRouter(prefix="/classes", tags=["classes"])

@router.post("/", response_model=ClassSchema)
async def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Create a new class (Teachers and Admins only)"""
    # Only teachers can create classes for themselves, admins can create for any teacher
    teacher_id = current_user.id
    if current_user.role == UserRole.ADMIN and hasattr(class_data, 'teacher_id'):
        teacher_id = getattr(class_data, 'teacher_id', current_user.id)
    
    new_class = Class(
        name=class_data.name,
        description=class_data.description,
        teacher_id=teacher_id
    )
    
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return new_class

@router.get("/", response_model=List[ClassSchema])
async def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get classes based on user role"""
    if current_user.role == UserRole.ADMIN:
        # Admin can see all classes
        classes = db.query(Class).filter(Class.is_active == True).all()
    elif current_user.role == UserRole.TEACHER:
        # Teachers can see their own classes
        classes = db.query(Class).filter(
            Class.teacher_id == current_user.id,
            Class.is_active == True
        ).all()
    else:  # Student
        # Students can see classes they're enrolled in
        enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.is_active == True
        ).all()
        class_ids = [e.class_id for e in enrollments]
        classes = db.query(Class).filter(
            Class.id.in_(class_ids),
            Class.is_active == True
        ).all()
    
    return classes

@router.get("/{class_id}", response_model=ClassSchema)
async def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific class details"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check access permissions
    if current_user.role == UserRole.STUDENT:
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.class_id == class_id,
            Enrollment.is_active == True
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.TEACHER:
        if class_obj.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return class_obj

@router.put("/{class_id}", response_model=ClassSchema)
async def update_class(
    class_id: int,
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Update class details"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check permissions
    if current_user.role == UserRole.TEACHER and class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    class_obj.name = class_data.name
    class_obj.description = class_data.description
    
    db.commit()
    db.refresh(class_obj)
    
    return class_obj

@router.delete("/{class_id}")
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete class (Admin only)"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_obj.is_active = False
    db.commit()
    
    return {"message": "Class deleted successfully"}
