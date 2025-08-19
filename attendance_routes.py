from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Date, func
from typing import List, Optional
from datetime import datetime, date
from database import get_db
from models import Attendance, User, Class, Enrollment, UserRole, AttendanceStatus
from schemas import AttendanceCreate, AttendanceUpdate, Attendance as AttendanceSchema
from auth import get_current_active_user, require_teacher_or_admin

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/", response_model=AttendanceSchema)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Mark attendance for a student"""
    # Verify class exists and teacher has access
    class_obj = db.query(Class).filter(Class.id == attendance_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if current_user.role == UserRole.TEACHER and class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify student is enrolled
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == attendance_data.student_id,
        Enrollment.class_id == attendance_data.class_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student not enrolled in this class")
    
    # Check if attendance already exists for this date
    existing_attendance = db.query(Attendance).filter(
        Attendance.student_id == attendance_data.student_id,
        Attendance.class_id == attendance_data.class_id,
        func.date(Attendance.date) == attendance_data.date
    ).first()
    
    if existing_attendance:
        # Update existing attendance
        existing_attendance.status = attendance_data.status
        existing_attendance.grade = attendance_data.grade
        existing_attendance.notes = attendance_data.notes
        existing_attendance.marked_by = current_user.id
        
        db.commit()
        db.refresh(existing_attendance)
        return existing_attendance
    else:
        # Create new attendance record
        new_attendance = Attendance(
            student_id=attendance_data.student_id,
            class_id=attendance_data.class_id,
            date=attendance_data.date,
            status=attendance_data.status,
            grade=attendance_data.grade,
            notes=attendance_data.notes,
            marked_by=current_user.id
        )
        
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)
        
        return new_attendance

@router.get("/class/{class_id}", response_model=List[AttendanceSchema])
async def get_class_attendance(
    class_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance records for a class"""
    # Verify class exists and check permissions
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if current_user.role == UserRole.TEACHER and class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.STUDENT:
        # Students can only see their own attendance
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.class_id == class_id,
            Enrollment.is_active == True
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Attendance).filter(Attendance.class_id == class_id)
    
    # Filter by student if student role
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Attendance.student_id == current_user.id)
    
    # Apply date filters
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.all()
    return attendance_records

@router.get("/student/{student_id}", response_model=List[AttendanceSchema])
async def get_student_attendance(
    student_id: int,
    class_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance records for a student"""
    # Check permissions
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    # Filter by class if specified
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
        
        # Additional permission check for teachers
        if current_user.role == UserRole.TEACHER:
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            if class_obj and class_obj.teacher_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
    
    # Apply date filters
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.all()
    return attendance_records

@router.put("/{attendance_id}", response_model=AttendanceSchema)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Update attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Check permissions for teachers
    if current_user.role == UserRole.TEACHER:
        class_obj = db.query(Class).filter(Class.id == attendance.class_id).first()
        if class_obj.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    attendance.status = attendance_data.status
    attendance.grade = attendance_data.grade
    attendance.notes = attendance_data.notes
    attendance.marked_by = current_user.id
    
    db.commit()
    db.refresh(attendance)
    
    return attendance

@router.delete("/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    """Delete attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Check permissions for teachers
    if current_user.role == UserRole.TEACHER:
        class_obj = db.query(Class).filter(Class.id == attendance.class_id).first()
        if class_obj.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(attendance)
    db.commit()
    
    return {"message": "Attendance record deleted successfully"}
