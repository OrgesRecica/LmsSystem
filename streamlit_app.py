import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import json
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None

class LMSClient:
    """Client for interacting with the LMS API"""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        return response.json() if response.status_code == 200 else None
    
    def signup(self, email: str, password: str, full_name: str, role: str) -> Dict[str, Any]:
        """Register new user"""
        response = requests.post(
            f"{self.base_url}/auth/signup",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role
            }
        )
        return response.json() if response.status_code == 200 else None
    
    def get_classes(self) -> list:
        """Get all classes"""
        response = requests.get(f"{self.base_url}/classes", headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def create_class(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create new class"""
        response = requests.post(
            f"{self.base_url}/classes",
            json={"name": name, "description": description},
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def get_enrollments(self, class_id: Optional[int] = None) -> list:
        """Get enrollments"""
        url = f"{self.base_url}/enrollments"
        if class_id:
            url += f"?class_id={class_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def enroll_student(self, student_id: int, class_id: int) -> Dict[str, Any]:
        """Enroll student in class"""
        response = requests.post(
            f"{self.base_url}/enrollments",
            json={"student_id": student_id, "class_id": class_id},
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def get_attendance(self, class_id: Optional[int] = None, student_id: Optional[int] = None) -> list:
        """Get attendance records"""
        url = f"{self.base_url}/attendance"
        params = []
        if class_id:
            params.append(f"class_id={class_id}")
        if student_id:
            params.append(f"student_id={student_id}")
        if params:
            url += "?" + "&".join(params)
        
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def mark_attendance(self, student_id: int, class_id: int, status: str, 
                       attendance_date: str, grade: Optional[int] = None, 
                       notes: Optional[str] = None) -> Dict[str, Any]:
        """Mark attendance"""
        data = {
            "student_id": student_id,
            "class_id": class_id,
            "date": attendance_date,
            "status": status
        }
        if grade is not None:
            data["grade"] = grade
        if notes:
            data["notes"] = notes
            
        response = requests.post(
            f"{self.base_url}/attendance",
            json=data,
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def get_users(self, role: Optional[str] = None) -> list:
        """Get users"""
        url = f"{self.base_url}/users"
        if role:
            url += f"?role={role}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        response = requests.get(f"{self.base_url}/dashboard/stats", headers=self.headers)
        return response.json() if response.status_code == 200 else {}

def login_page():
    """Login page"""
    st.title("🎓 Learning Management System")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit and email and password:
                client = LMSClient(API_BASE_URL)
                result = client.login(email, password)
                
                if result and "access_token" in result:
                    st.session_state.authenticated = True
                    st.session_state.user = result["user"]
                    st.session_state.token = result["access_token"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            full_name = st.text_input("Full Name")
            role = st.selectbox("Role", ["student", "teacher"])
            submit = st.form_submit_button("Sign Up")
            
            if submit and email and password and full_name:
                client = LMSClient(API_BASE_URL)
                result = client.signup(email, password, full_name, role)
                
                if result:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Failed to create account")

def admin_dashboard():
    """Admin dashboard"""
    st.title("👨‍💼 Admin Dashboard")
    
    client = LMSClient(API_BASE_URL, st.session_state.token)
    
    # Dashboard stats
    stats = client.get_dashboard_stats()
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", stats.get("total_users", 0))
        with col2:
            st.metric("Total Classes", stats.get("total_classes", 0))
        with col3:
            st.metric("Total Students", stats.get("total_students", 0))
        with col4:
            st.metric("Total Teachers", stats.get("total_teachers", 0))
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "Classes", "Enrollments", "Attendance"])
    
    with tab1:
        st.subheader("User Management")
        users = client.get_users()
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df[['id', 'email', 'full_name', 'role', 'is_active']])
    
    with tab2:
        st.subheader("Class Management")
        
        # Create new class
        with st.expander("Create New Class"):
            with st.form("create_class"):
                class_name = st.text_input("Class Name")
                class_description = st.text_area("Description")
                if st.form_submit_button("Create Class"):
                    result = client.create_class(class_name, class_description)
                    if result:
                        st.success("Class created successfully!")
                        st.rerun()
        
        # Display existing classes
        classes = client.get_classes()
        if classes:
            df = pd.DataFrame(classes)
            st.dataframe(df[['id', 'name', 'description', 'teacher', 'is_active']])
    
    with tab3:
        st.subheader("Enrollment Management")
        enrollments = client.get_enrollments()
        if enrollments:
            df = pd.DataFrame(enrollments)
            st.dataframe(df)
    
    with tab4:
        st.subheader("Attendance Overview")
        attendance = client.get_attendance()
        if attendance:
            df = pd.DataFrame(attendance)
            st.dataframe(df)

def teacher_dashboard():
    """Teacher dashboard"""
    st.title("👨‍🏫 Teacher Dashboard")
    
    client = LMSClient(API_BASE_URL, st.session_state.token)
    
    # Get teacher's classes
    classes = client.get_classes()
    teacher_classes = [c for c in classes if c.get('teacher', {}).get('id') == st.session_state.user['id']]
    
    if not teacher_classes:
        st.info("You don't have any classes assigned yet.")
        return
    
    # Class selection
    selected_class = st.selectbox(
        "Select Class",
        teacher_classes,
        format_func=lambda x: x['name']
    )
    
    if selected_class:
        tab1, tab2, tab3 = st.tabs(["Class Info", "Students", "Attendance"])
        
        with tab1:
            st.subheader(f"Class: {selected_class['name']}")
            st.write(f"Description: {selected_class.get('description', 'No description')}")
            
            # Get enrollments for this class
            enrollments = client.get_enrollments(selected_class['id'])
            st.metric("Total Students", len(enrollments))
        
        with tab2:
            st.subheader("Enrolled Students")
            enrollments = client.get_enrollments(selected_class['id'])
            if enrollments:
                students_data = []
                for enrollment in enrollments:
                    students_data.append({
                        'Student ID': enrollment['student']['id'],
                        'Name': enrollment['student']['full_name'],
                        'Email': enrollment['student']['email'],
                        'Enrolled Date': enrollment['enrolled_at'][:10]
                    })
                df = pd.DataFrame(students_data)
                st.dataframe(df)
        
        with tab3:
            st.subheader("Attendance Management")
            
            # Mark attendance form
            with st.expander("Mark Attendance"):
                enrollments = client.get_enrollments(selected_class['id'])
                if enrollments:
                    with st.form("mark_attendance"):
                        student_options = {e['student']['full_name']: e['student']['id'] for e in enrollments}
                        selected_student = st.selectbox("Select Student", list(student_options.keys()))
                        attendance_date = st.date_input("Date", value=date.today())
                        status = st.selectbox("Status", ["present", "absent", "tardy"])
                        grade = st.number_input("Grade (optional)", min_value=0, max_value=100, value=None)
                        notes = st.text_area("Notes (optional)")
                        
                        if st.form_submit_button("Mark Attendance"):
                            student_id = student_options[selected_student]
                            result = client.mark_attendance(
                                student_id=student_id,
                                class_id=selected_class['id'],
                                status=status,
                                attendance_date=attendance_date.isoformat(),
                                grade=grade if grade else None,
                                notes=notes if notes else None
                            )
                            if result:
                                st.success("Attendance marked successfully!")
                                st.rerun()
            
            # Display attendance records
            attendance_records = client.get_attendance(class_id=selected_class['id'])
            if attendance_records:
                attendance_data = []
                for record in attendance_records:
                    attendance_data.append({
                        'Date': record['date'][:10],
                        'Student': record['student']['full_name'],
                        'Status': record['status'],
                        'Grade': record.get('grade', 'N/A'),
                        'Notes': record.get('notes', '')
                    })
                df = pd.DataFrame(attendance_data)
                st.dataframe(df)

def student_dashboard():
    """Student dashboard"""
    st.title("👨‍🎓 Student Dashboard")
    
    client = LMSClient(API_BASE_URL, st.session_state.token)
    
    # Get student's enrollments
    enrollments = client.get_enrollments()
    student_enrollments = [e for e in enrollments if e['student']['id'] == st.session_state.user['id']]
    
    if not student_enrollments:
        st.info("You are not enrolled in any classes yet.")
        return
    
    # Display enrolled classes
    st.subheader("My Classes")
    for enrollment in student_enrollments:
        with st.expander(f"📚 {enrollment['class_obj']['name']}"):
            st.write(f"**Teacher:** {enrollment['class_obj']['teacher']['full_name']}")
            st.write(f"**Description:** {enrollment['class_obj'].get('description', 'No description')}")
            st.write(f"**Enrolled:** {enrollment['enrolled_at'][:10]}")
    
    # Attendance records
    st.subheader("My Attendance")
    attendance_records = client.get_attendance(student_id=st.session_state.user['id'])
    
    if attendance_records:
        attendance_data = []
        for record in attendance_records:
            attendance_data.append({
                'Date': record['date'][:10],
                'Class': record['class_obj']['name'],
                'Status': record['status'],
                'Grade': record.get('grade', 'N/A'),
                'Notes': record.get('notes', '')
            })
        df = pd.DataFrame(attendance_data)
        st.dataframe(df)
        
        # Attendance statistics
        st.subheader("Attendance Statistics")
        status_counts = df['Status'].value_counts()
        col1, col2, col3 = st.columns(3)
        
        total_records = len(df)
        with col1:
            present_count = status_counts.get('present', 0)
            st.metric("Present", f"{present_count}/{total_records}", 
                     f"{(present_count/total_records*100):.1f}%" if total_records > 0 else "0%")
        with col2:
            absent_count = status_counts.get('absent', 0)
            st.metric("Absent", f"{absent_count}/{total_records}",
                     f"{(absent_count/total_records*100):.1f}%" if total_records > 0 else "0%")
        with col3:
            tardy_count = status_counts.get('tardy', 0)
            st.metric("Tardy", f"{tardy_count}/{total_records}",
                     f"{(tardy_count/total_records*100):.1f}%" if total_records > 0 else "0%")

def main():
    """Main application"""
    st.set_page_config(
        page_title="LMS - Learning Management System",
        page_icon="🎓",
        layout="wide"
    )
    
    # Sidebar
    with st.sidebar:
        if st.session_state.authenticated:
            st.write(f"Welcome, {st.session_state.user['full_name']}")
            st.write(f"Role: {st.session_state.user['role'].title()}")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.token = None
                st.rerun()
        else:
            st.write("Please login to continue")
    
    # Main content
    if not st.session_state.authenticated:
        login_page()
    else:
        user_role = st.session_state.user['role']
        if user_role == 'admin':
            admin_dashboard()
        elif user_role == 'teacher':
            teacher_dashboard()
        elif user_role == 'student':
            student_dashboard()

if __name__ == "__main__":
    main()
