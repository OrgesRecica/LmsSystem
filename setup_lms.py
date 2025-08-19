#!/usr/bin/env python3
"""
LMS Setup Script
Initializes the database and creates default admin user
"""

import sys
import os
from pathlib import Path

def setup_database():
    """Initialize database and create admin user"""
    print("🗄️  Setting up database...")
    
    try:
        from database import create_tables, create_admin_user
        
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Create admin user
        create_admin_user()
        print("✅ Admin user created successfully")
        
        print("\n🔑 Default Admin Credentials:")
        print("   Email: admin@example.com")
        print("   Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        import subprocess
        
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🎓 Learning Management System - Setup")
    print("=" * 60)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return
    
    print("🚀 Starting LMS setup process...\n")
    
    # Install dependencies
    if not install_dependencies():
        return
    
    print()
    
    # Setup database
    if not setup_database():
        return
    
    print("\n" + "=" * 60)
    print("✅ LMS Setup Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Run 'python start_server.py' to start the system")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Login with admin credentials or create a new account")
    print("\n🎉 Happy Learning!")

if __name__ == "__main__":
    main()
