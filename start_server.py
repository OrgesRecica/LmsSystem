#!/usr/bin/env python3
"""
LMS Server Startup Script
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def start_fastapi():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")

def start_streamlit():
    """Start Streamlit app"""
    print("🎨 Starting Streamlit app...")
    time.sleep(3)  # Wait for FastAPI to start
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎓 Learning Management System - Server Startup")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        "main.py", "app.py", "database.py", "models.py", 
        "auth.py", "session_manager.py"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return
    
    print("✅ All required files found")
    print("\n📋 Starting services...")
    print("   - FastAPI Backend: http://localhost:8000")
    print("   - Streamlit Frontend: http://localhost:8501")
    print("   - API Documentation: http://localhost:8000/docs")
    print("\n⚠️  Press Ctrl+C to stop all services\n")
    
    # Start both servers in separate threads
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    
    try:
        fastapi_thread.start()
        streamlit_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down LMS servers...")
        print("✅ All services stopped successfully")

if __name__ == "__main__":
    main()
