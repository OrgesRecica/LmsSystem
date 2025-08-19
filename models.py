from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    TARDY = "tardy"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    taught_classes = relationship("Class", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student", foreign_keys="Attendance.student_id")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    teacher = relationship("User", back_populates="taught_classes")
    enrollments = relationship("Enrollment", back_populates="class_obj")
    attendance_records = relationship("Attendance", back_populates="class_obj")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    student = relationship("User", back_populates="enrollments")
    class_obj = relationship("Class", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    grade = Column(Integer)  # Optional attendance grade
    notes = Column(Text)
    marked_by = Column(Integer, ForeignKey("users.id"))  # Teacher who marked attendance
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="attendance_records", foreign_keys=[student_id])
    class_obj = relationship("Class", back_populates="attendance_records")
    marked_by_user = relationship("User", foreign_keys=[marked_by])
