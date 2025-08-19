#!/usr/bin/env python3
"""
Database repair script for LMS
Run this to fix common database issues
"""

import os
import sys
from pathlib import Path

def reset_database():
    """Remove existing database and recreate"""
    print("Resetting database...")
    
    db_path = Path("lms.db")
    if db_path.exists():
        try:
            db_path.unlink()
            print("✓ Removed existing database file")
        except Exception as e:
            print(f"✗ Could not remove database file: {e}")
            return False
    
    # Recreate database
    try:
        from database import create_tables, create_admin_user
        
        print("Creating new database...")
        create_tables()
        print("✓ Database tables created")
        
        create_admin_user()
        print("✓ Admin user created")
        
        print("\n🎉 Database reset complete!")
        print("Admin credentials: admin@example.com / admin123")
        
        return True
        
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_missing_packages():
    """Install commonly missing packages"""
    print("Installing missing packages...")
    
    packages = [
        "sqlalchemy",
        "passlib[bcrypt]", 
        "python-jose[cryptography]",
        "streamlit",
        "fastapi",
        "uvicorn"
    ]
    
    for package in packages:
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Installed {package}")
            else:
                print(f"✗ Failed to install {package}: {result.stderr}")
        except Exception as e:
            print(f"✗ Error installing {package}: {e}")

def main():
    """Main repair function"""
    print("=== LMS Database Repair Tool ===\n")
    
    print("Choose an option:")
    print("1. Reset database (delete and recreate)")
    print("2. Install missing packages")
    print("3. Both (recommended)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["2", "3"]:
        install_missing_packages()
        print()
    
    if choice in ["1", "3"]:
        reset_database()
    
    print("\nAfter running this script, try:")
    print("  python troubleshoot_db.py")
    print("  python init_database.py")

if __name__ == "__main__":
    main()
