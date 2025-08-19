# Learning Management System (LMS)

A comprehensive Learning Management System built with FastAPI backend and Streamlit frontend.

## Features

- **User Management**: Admin, Teacher, and Student roles
- **Class Management**: Create and manage classes
- **Enrollment System**: Enroll students in classes
- **Attendance Tracking**: Mark and view attendance records
- **Role-based Dashboards**: Different interfaces for each user type

## Setup Instructions

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Initialize Database

\`\`\`bash
python init_database.py
\`\`\`

### 3. Start the FastAPI Backend

\`\`\`bash
python main.py
\`\`\`

The API will be available at `http://localhost:8000`

### 4. Start the Streamlit Frontend

In a new terminal:

\`\`\`bash
streamlit run streamlit_app.py
\`\`\`

Or use the helper script:

\`\`\`bash
python run_streamlit.py
\`\`\`

The Streamlit app will be available at `http://localhost:8501`

## Default Admin Account

- **Email**: admin@lms.com
- **Password**: admin123

## API Documentation

Once the FastAPI server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## User Roles

### Admin
- Manage all users, classes, and enrollments
- View system-wide statistics
- Full access to all features

### Teacher
- Manage assigned classes
- Mark student attendance
- View class enrollment and statistics

### Student
- View enrolled classes
- Check personal attendance records
- View attendance statistics

## Usage

1. Start both the FastAPI backend and Streamlit frontend
2. Access the Streamlit app in your browser
3. Login with existing credentials or sign up as a new user
4. Navigate through the role-appropriate dashboard
