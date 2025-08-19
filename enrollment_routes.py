from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Enrollment, User, Class, UserRole
from schemas import EnrollmentCreate, Enrollment as EnrollmentSchema
from auth import get_current_active_user, require_teacher_or_admin

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@router.post("/", response_model=EnrollmentSchema)
async def enroll_student(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Enroll a student in a class"""
    # Verify class exists
    class_obj = db.query(Class).filter(Class.id == enrollment_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify student exists and is a student
    student = db.query(User).filter(User.id == enrollment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.role != UserRole.STUDENT:
        raise HTTPException(status_code=400, detail="User is not a student")
    
    # Check if teacher owns the class (unless admin)
    if current_user.role == UserRole.TEACHER and class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment_data.student_id,
        Enrollment.class_id == enrollment_data.class_id,
        Enrollment.is_active == True
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Student already enrolled in this class")
    
    # Create enrollment
    new_enrollment = Enrollment(
        student_id=enrollment_data.student_id,
        class_id=enrollment_data.class_id
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    return new_enrollment

@router.get("/class/{class_id}", response_model=List[EnrollmentSchema])
async def get_class_enrollments(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all enrollments for a specific class"""
    # Verify class exists
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check permissions
    if current_user.role == UserRole.TEACHER and class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.STUDENT:
        # Students can only see if they're enrolled
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.class_id == class_id,
            Enrollment.is_active == True
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.is_active == True
    ).all()
    
    return enrollments

@router.get("/student/{student_id}", response_model=List[EnrollmentSchema])
async def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all enrollments for a specific student"""
    # Check permissions
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()
    
    return enrollments

@router.delete("/{enrollment_id}")
async def remove_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Remove student from class"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Check permissions for teachers
    if current_user.role == UserRole.TEACHER:
        class_obj = db.query(Class).filter(Class.id == enrollment.class_id).first()
        if class_obj.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    enrollment.is_active = False
    db.commit()
    
    return {"message": "Student removed from class successfully"}
