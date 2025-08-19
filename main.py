from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables, create_admin_user
from auth_routes import router as auth_router
from class_routes import router as class_router
from enrollment_routes import router as enrollment_router
from attendance_routes import router as attendance_router
from user_routes import router as user_router
from dashboard_routes import router as dashboard_router

# Create FastAPI app
app = FastAPI(
    title="LMS API",
    description="Learning Management System API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(class_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)
app.include_router(user_router)
app.include_router(dashboard_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_tables()
    create_admin_user()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LMS API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
