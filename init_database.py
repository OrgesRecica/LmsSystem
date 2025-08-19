#!/usr/bin/env python3
"""
Database initialization script for LMS
Run this script to create tables and admin user
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import create_tables, create_admin_user

def main():
    print("Initializing LMS database...")
    
    # Create all tables
    create_tables()
    print("✓ Database tables created")
    
    # Create admin user
    create_admin_user()
    print("✓ Admin user setup complete")
    
    print("\nDatabase initialization complete!")
    print("Admin credentials: admin@example.com / admin123")

if __name__ == "__main__":
    main()
