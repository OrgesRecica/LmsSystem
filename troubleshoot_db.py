#!/usr/bin/env python3
"""
Database troubleshooting script for LMS
Run this to diagnose and fix database initialization issues
"""

import os
import sys
import traceback
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'sqlalchemy',
        'passlib',
        'bcrypt'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_database_file():
    """Check database file permissions and location"""
    print("\nChecking database file...")
    
    db_path = Path("lms.db")
    
    if db_path.exists():
        print(f"✓ Database file exists at: {db_path.absolute()}")
        
        # Check permissions
        if os.access(db_path, os.R_OK):
            print("✓ Database file is readable")
        else:
            print("✗ Database file is not readable")
            
        if os.access(db_path, os.W_OK):
            print("✓ Database file is writable")
        else:
            print("✗ Database file is not writable")
            
    else:
        print("ℹ Database file doesn't exist yet (will be created)")
        
        # Check if we can create files in current directory
        try:
            test_file = Path("test_write.tmp")
            test_file.touch()
            test_file.unlink()
            print("✓ Can create files in current directory")
        except Exception as e:
            print(f"✗ Cannot create files in current directory: {e}")
            return False
    
    return True

def test_database_connection():
    """Test database connection and table creation"""
    print("\nTesting database connection...")
    
    try:
        from sqlalchemy import create_engine
        from models import Base
        
        # Test engine creation
        DATABASE_URL = "sqlite:///./lms.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        print("✓ Database engine created successfully")
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful")
        
        # Test table creation
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        traceback.print_exc()
        return False

def test_admin_creation():
    """Test admin user creation"""
    print("\nTesting admin user creation...")
    
    try:
        from database import create_admin_user, SessionLocal
        from models import User
        
        # Try to create admin user
        create_admin_user()
        print("✓ Admin user creation completed")
        
        # Verify admin user exists
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.email == "admin@example.com").first()
            if admin:
                print("✓ Admin user verified in database")
                print(f"  - Email: {admin.email}")
                print(f"  - Name: {admin.full_name}")
                print(f"  - Role: {admin.role.value}")
            else:
                print("✗ Admin user not found in database")
                return False
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Admin creation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all database diagnostics"""
    print("=== LMS Database Troubleshooter ===\n")
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Database File", check_database_file),
        ("Database Connection", test_database_connection),
        ("Admin User Creation", test_admin_creation)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ {check_name} failed with error: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All checks passed! Your database should be working.")
        print("\nYou can now run:")
        print("  python init_database.py")
        print("  python main.py")
        print("  streamlit run streamlit_app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check file permissions in your project directory")
        print("3. Make sure you're in the correct project directory")
        print("4. Try deleting lms.db and running init_database.py again")

if __name__ == "__main__":
    main()
