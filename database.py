from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UserRole
from passlib.context import CryptContext
import os

# Database configuration
DATABASE_URL = "sqlite:///./lms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin_user = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin@example.com / admin123")
        else:
            print("Admin user already exists")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    create_admin_user()
