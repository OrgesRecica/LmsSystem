from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import UserRole, AttendanceStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Class schemas
class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    teacher_id: int
    created_at: datetime
    is_active: bool
    teacher: User
    
    class Config:
        from_attributes = True

# Enrollment schemas
class EnrollmentCreate(BaseModel):
    student_id: int
    class_id: int

class Enrollment(BaseModel):
    id: int
    student_id: int
    class_id: int
    enrolled_at: datetime
    is_active: bool
    student: User
    class_obj: Class
    
    class Config:
        from_attributes = True

# Attendance schemas
class AttendanceCreate(BaseModel):
    student_id: int
    class_id: int
    date: datetime
    status: AttendanceStatus
    grade: Optional[int] = None
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    status: AttendanceStatus
    grade: Optional[int] = None
    notes: Optional[str] = None

class Attendance(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: datetime
    status: AttendanceStatus
    grade: Optional[int] = None
    notes: Optional[str] = None
    marked_by: Optional[int] = None
    created_at: datetime
    student: User
    class_obj: Class
    
    class Config:
        from_attributes = True

# Dashboard schemas
class AttendanceStats(BaseModel):
    total_sessions: int
    present_count: int
    absent_count: int
    tardy_count: int
    present_percentage: float
    absent_percentage: float
    tardy_percentage: float

class ClassStats(BaseModel):
    class_id: int
    class_name: str
    total_students: int
    attendance_stats: AttendanceStats
