from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from database import get_db
from models import User, Class, Enrollment, Attendance, UserRole, AttendanceStatus
from schemas import AttendanceStats, ClassStats
from auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics based on user role"""
    if current_user.role == UserRole.ADMIN:
        return await get_admin_stats(db)
    elif current_user.role == UserRole.TEACHER:
        return await get_teacher_stats(db, current_user.id)
    else:  # Student
        return await get_student_stats(db, current_user.id)

async def get_admin_stats(db: Session) -> Dict:
    """Get admin dashboard statistics"""
    total_users = db.query(User).filter(User.is_active == True).count()
    total_teachers = db.query(User).filter(User.role == UserRole.TEACHER, User.is_active == True).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT, User.is_active == True).count()
    total_classes = db.query(Class).filter(Class.is_active == True).count()
    total_enrollments = db.query(Enrollment).filter(Enrollment.is_active == True).count()
    
    # Attendance statistics
    total_attendance_records = db.query(Attendance).count()
    present_count = db.query(Attendance).filter(Attendance.status == AttendanceStatus.PRESENT).count()
    absent_count = db.query(Attendance).filter(Attendance.status == AttendanceStatus.ABSENT).count()
    tardy_count = db.query(Attendance).filter(Attendance.status == AttendanceStatus.TARDY).count()
    
    return {
        "total_users": total_users,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_classes": total_classes,
        "total_enrollments": total_enrollments,
        "attendance_overview": {
            "total_records": total_attendance_records,
            "present": present_count,
            "absent": absent_count,
            "tardy": tardy_count,
            "present_percentage": (present_count / total_attendance_records * 100) if total_attendance_records > 0 else 0,
            "absent_percentage": (absent_count / total_attendance_records * 100) if total_attendance_records > 0 else 0,
            "tardy_percentage": (tardy_count / total_attendance_records * 100) if total_attendance_records > 0 else 0
        }
    }

async def get_teacher_stats(db: Session, teacher_id: int) -> Dict:
    """Get teacher dashboard statistics"""
    teacher_classes = db.query(Class).filter(Class.teacher_id == teacher_id, Class.is_active == True).all()
    class_ids = [c.id for c in teacher_classes]
    
    total_classes = len(teacher_classes)
    total_students = db.query(Enrollment).filter(
        Enrollment.class_id.in_(class_ids),
        Enrollment.is_active == True
    ).count()
    
    # Attendance statistics for teacher's classes
    attendance_records = db.query(Attendance).filter(Attendance.class_id.in_(class_ids)).all()
    total_records = len(attendance_records)
    
    present_count = len([a for a in attendance_records if a.status == AttendanceStatus.PRESENT])
    absent_count = len([a for a in attendance_records if a.status == AttendanceStatus.ABSENT])
    tardy_count = len([a for a in attendance_records if a.status == AttendanceStatus.TARDY])
    
    # Class-wise statistics
    class_stats = []
    for class_obj in teacher_classes:
        class_enrollments = db.query(Enrollment).filter(
            Enrollment.class_id == class_obj.id,
            Enrollment.is_active == True
        ).count()
        
        class_attendance = db.query(Attendance).filter(Attendance.class_id == class_obj.id).all()
        class_total = len(class_attendance)
        class_present = len([a for a in class_attendance if a.status == AttendanceStatus.PRESENT])
        class_absent = len([a for a in class_attendance if a.status == AttendanceStatus.ABSENT])
        class_tardy = len([a for a in class_attendance if a.status == AttendanceStatus.TARDY])
        
        class_stats.append({
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "total_students": class_enrollments,
            "attendance_stats": {
                "total_sessions": class_total,
                "present_count": class_present,
                "absent_count": class_absent,
                "tardy_count": class_tardy,
                "present_percentage": (class_present / class_total * 100) if class_total > 0 else 0,
                "absent_percentage": (class_absent / class_total * 100) if class_total > 0 else 0,
                "tardy_percentage": (class_tardy / class_total * 100) if class_total > 0 else 0
            }
        })
    
    return {
        "total_classes": total_classes,
        "total_students": total_students,
        "attendance_overview": {
            "total_records": total_records,
            "present": present_count,
            "absent": absent_count,
            "tardy": tardy_count,
            "present_percentage": (present_count / total_records * 100) if total_records > 0 else 0,
            "absent_percentage": (absent_count / total_records * 100) if total_records > 0 else 0,
            "tardy_percentage": (tardy_count / total_records * 100) if total_records > 0 else 0
        },
        "class_statistics": class_stats
    }

async def get_student_stats(db: Session, student_id: int) -> Dict:
    """Get student dashboard statistics"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.is_active == True
    ).all()
    
    total_classes = len(enrollments)
    class_ids = [e.class_id for e in enrollments]
    
    # Student's attendance records
    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.class_id.in_(class_ids)
    ).all()
    
    total_records = len(attendance_records)
    present_count = len([a for a in attendance_records if a.status == AttendanceStatus.PRESENT])
    absent_count = len([a for a in attendance_records if a.status == AttendanceStatus.ABSENT])
    tardy_count = len([a for a in attendance_records if a.status == AttendanceStatus.TARDY])
    
    # Class-wise attendance
    class_attendance = []
    for enrollment in enrollments:
        class_obj = db.query(Class).filter(Class.id == enrollment.class_id).first()
        class_records = [a for a in attendance_records if a.class_id == enrollment.class_id]
        class_total = len(class_records)
        class_present = len([a for a in class_records if a.status == AttendanceStatus.PRESENT])
        class_absent = len([a for a in class_records if a.status == AttendanceStatus.ABSENT])
        class_tardy = len([a for a in class_records if a.status == AttendanceStatus.TARDY])
        
        class_attendance.append({
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "teacher_name": class_obj.teacher.full_name,
            "attendance_stats": {
                "total_sessions": class_total,
                "present_count": class_present,
                "absent_count": class_absent,
                "tardy_count": class_tardy,
                "present_percentage": (class_present / class_total * 100) if class_total > 0 else 0,
                "absent_percentage": (class_absent / class_total * 100) if class_total > 0 else 0,
                "tardy_percentage": (class_tardy / class_total * 100) if class_total > 0 else 0
            }
        })
    
    return {
        "total_classes": total_classes,
        "overall_attendance": {
            "total_records": total_records,
            "present": present_count,
            "absent": absent_count,
            "tardy": tardy_count,
            "present_percentage": (present_count / total_records * 100) if total_records > 0 else 0,
            "absent_percentage": (absent_count / total_records * 100) if total_records > 0 else 0,
            "tardy_percentage": (tardy_count / total_records * 100) if total_records > 0 else 0
        },
        "class_attendance": class_attendance
    }
