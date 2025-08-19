import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from session_manager import SessionManager
import requests

def show_teacher_dashboard():
    """Main teacher dashboard page"""
    SessionManager.require_role("teacher")
    
    st.title("Teacher Dashboard")
    st.markdown("---")
    
    # Get dashboard stats
    response = SessionManager.make_authenticated_request("/dashboard/stats")
    if response and response.status_code == 200:
        stats = response.json()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Classes",
                value=stats.get("total_classes", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Students",
                value=stats.get("total_students", 0),
                delta=None
            )
        
        with col3:
            attendance_overview = stats.get("attendance_overview", {})
            st.metric(
                label="Attendance Rate",
                value=f"{attendance_overview.get('present_percentage', 0):.1f}%",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Total Sessions",
                value=attendance_overview.get("total_records", 0),
                delta=None
            )
        
        st.markdown("---")
        
        # Attendance Overview Chart
        st.subheader("Overall Attendance Overview")
        
        if attendance_overview.get("total_records", 0) > 0:
            # Pie chart for attendance distribution
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Present', 'Absent', 'Tardy'],
                values=[
                    attendance_overview.get("present", 0),
                    attendance_overview.get("absent", 0),
                    attendance_overview.get("tardy", 0)
                ],
                hole=0.4,
                marker_colors=['#2E8B57', '#DC143C', '#FF8C00']
            )])
            
            fig_pie.update_layout(
                title="Attendance Distribution",
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No attendance data available yet.")
        
        # Class-wise Statistics
        st.subheader("Class-wise Performance")
        
        class_stats = stats.get("class_statistics", [])
        if class_stats:
            # Create DataFrame for class statistics
            class_df = pd.DataFrame([
                {
                    "Class": stat["class_name"],
                    "Students": stat["total_students"],
                    "Sessions": stat["attendance_stats"]["total_sessions"],
                    "Present %": stat["attendance_stats"]["present_percentage"],
                    "Absent %": stat["attendance_stats"]["absent_percentage"],
                    "Tardy %": stat["attendance_stats"]["tardy_percentage"]
                }
                for stat in class_stats
            ])
            
            # Display table
            st.dataframe(class_df, use_container_width=True)
            
            # Bar chart for attendance rates by class
            if len(class_df) > 0:
                fig_bar = px.bar(
                    class_df,
                    x="Class",
                    y=["Present %", "Absent %", "Tardy %"],
                    title="Attendance Rates by Class",
                    color_discrete_map={
                        "Present %": "#2E8B57",
                        "Absent %": "#DC143C",
                        "Tardy %": "#FF8C00"
                    }
                )
                
                fig_bar.update_layout(
                    xaxis_title="Classes",
                    yaxis_title="Percentage",
                    height=400
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No classes found. Create your first class to get started!")
    else:
        st.error("Failed to load dashboard data.")

def show_class_management():
    """Class management page"""
    SessionManager.require_role("teacher")
    
    st.title("Class Management")
    st.markdown("---")
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["My Classes", "Create New Class", "Edit Classes"])
    
    with tab1:
        st.subheader("My Classes")
        
        # Get teacher's classes
        response = SessionManager.make_authenticated_request("/classes/")
        if response and response.status_code == 200:
            classes = response.json()
            
            if classes:
                for class_obj in classes:
                    with st.expander(f"📚 {class_obj['name']}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Description:** {class_obj.get('description', 'No description')}")
                            st.write(f"**Created:** {class_obj['created_at'][:10]}")
                            st.write(f"**Status:** {'Active' if class_obj['is_active'] else 'Inactive'}")
                        
                        with col2:
                            if st.button(f"View Details", key=f"view_{class_obj['id']}"):
                                st.session_state.selected_class = class_obj['id']
                                st.rerun()
            else:
                st.info("You haven't created any classes yet. Use the 'Create New Class' tab to get started!")
        else:
            st.error("Failed to load classes.")
    
    with tab2:
        st.subheader("Create New Class")
        
        with st.form("create_class_form"):
            class_name = st.text_input("Class Name", placeholder="e.g., Mathematics 101")
            class_description = st.text_area("Description", placeholder="Brief description of the class")
            
            submitted = st.form_submit_button("Create Class")
            
            if submitted:
                if class_name:
                    class_data = {
                        "name": class_name,
                        "description": class_description
                    }
                    
                    response = SessionManager.make_authenticated_request(
                        "/classes/",
                        method="POST",
                        data=class_data
                    )
                    
                    if response and response.status_code == 200:
                        st.success(f"Class '{class_name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create class. Please try again.")
                else:
                    st.error("Please enter a class name.")
    
    with tab3:
        st.subheader("Edit Classes")
        
        # Get classes for editing
        response = SessionManager.make_authenticated_request("/classes/")
        if response and response.status_code == 200:
            classes = response.json()
            
            if classes:
                class_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in classes}
                selected_class_key = st.selectbox("Select Class to Edit", list(class_options.keys()))
                
                if selected_class_key:
                    selected_class_id = class_options[selected_class_key]
                    selected_class = next(c for c in classes if c['id'] == selected_class_id)
                    
                    with st.form("edit_class_form"):
                        new_name = st.text_input("Class Name", value=selected_class['name'])
                        new_description = st.text_area("Description", value=selected_class.get('description', ''))
                        
                        submitted = st.form_submit_button("Update Class")
                        
                        if submitted:
                            update_data = {
                                "name": new_name,
                                "description": new_description
                            }
                            
                            response = SessionManager.make_authenticated_request(
                                f"/classes/{selected_class_id}",
                                method="PUT",
                                data=update_data
                            )
                            
                            if response and response.status_code == 200:
                                st.success("Class updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update class.")
            else:
                st.info("No classes available to edit.")

def show_student_enrollment():
    """Student enrollment management"""
    SessionManager.require_role("teacher")
    
    st.title("Student Enrollment")
    st.markdown("---")
    
    # Get teacher's classes
    classes_response = SessionManager.make_authenticated_request("/classes/")
    if not classes_response or classes_response.status_code != 200:
        st.error("Failed to load classes.")
        return
    
    classes = classes_response.json()
    if not classes:
        st.warning("You need to create at least one class before enrolling students.")
        return
    
    # Tabs for enrollment actions
    tab1, tab2 = st.tabs(["Enroll Students", "Manage Enrollments"])
    
    with tab1:
        st.subheader("Enroll New Student")
        
        # Get available students
        students_response = SessionManager.make_authenticated_request("/users/students")
        if students_response and students_response.status_code == 200:
            students = students_response.json()
            
            if students:
                with st.form("enroll_student_form"):
                    # Class selection
                    class_options = {f"{c['name']}": c['id'] for c in classes}
                    selected_class = st.selectbox("Select Class", list(class_options.keys()))
                    
                    # Student selection
                    student_options = {f"{s['full_name']} ({s['email']})": s['id'] for s in students}
                    selected_student = st.selectbox("Select Student", list(student_options.keys()))
                    
                    submitted = st.form_submit_button("Enroll Student")
                    
                    if submitted and selected_class and selected_student:
                        enrollment_data = {
                            "student_id": student_options[selected_student],
                            "class_id": class_options[selected_class]
                        }
                        
                        response = SessionManager.make_authenticated_request(
                            "/enrollments/",
                            method="POST",
                            data=enrollment_data
                        )
                        
                        if response and response.status_code == 200:
                            st.success(f"Student enrolled in {selected_class} successfully!")
                            st.rerun()
                        else:
                            error_msg = response.json().get("detail", "Failed to enroll student") if response else "Failed to enroll student"
                            st.error(error_msg)
            else:
                st.info("No students available for enrollment.")
        else:
            st.error("Failed to load students.")
    
    with tab2:
        st.subheader("Current Enrollments")
        
        # Class selector
        class_options = {f"{c['name']}": c['id'] for c in classes}
        selected_class_name = st.selectbox("Select Class to View Enrollments", list(class_options.keys()))
        
        if selected_class_name:
            class_id = class_options[selected_class_name]
            
            # Get enrollments for selected class
            response = SessionManager.make_authenticated_request(f"/enrollments/class/{class_id}")
            if response and response.status_code == 200:
                enrollments = response.json()
                
                if enrollments:
                    # Display enrollments in a nice format
                    enrollment_data = []
                    for enrollment in enrollments:
                        enrollment_data.append({
                            "Student Name": enrollment['student']['full_name'],
                            "Email": enrollment['student']['email'],
                            "Enrolled Date": enrollment['enrolled_at'][:10],
                            "Status": "Active" if enrollment['is_active'] else "Inactive",
                            "Enrollment ID": enrollment['id']
                        })
                    
                    df = pd.DataFrame(enrollment_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Option to remove students
                    st.subheader("Remove Student from Class")
                    student_to_remove = st.selectbox(
                        "Select student to remove",
                        options=[f"{e['student']['full_name']} ({e['student']['email']})" for e in enrollments],
                        key="remove_student"
                    )
                    
                    if st.button("Remove Student", type="secondary"):
                        # Find enrollment ID
                        selected_enrollment = next(
                            e for e in enrollments 
                            if f"{e['student']['full_name']} ({e['student']['email']})" == student_to_remove
                        )
                        
                        response = SessionManager.make_authenticated_request(
                            f"/enrollments/{selected_enrollment['id']}",
                            method="DELETE"
                        )
                        
                        if response and response.status_code == 200:
                            st.success("Student removed from class successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to remove student.")
                else:
                    st.info(f"No students enrolled in {selected_class_name} yet.")
            else:
                st.error("Failed to load enrollments.")

def show_attendance_management():
    """Attendance marking and management"""
    SessionManager.require_role("teacher")
    
    st.title("Attendance Management")
    st.markdown("---")
    
    # Get teacher's classes
    classes_response = SessionManager.make_authenticated_request("/classes/")
    if not classes_response or classes_response.status_code != 200:
        st.error("Failed to load classes.")
        return
    
    classes = classes_response.json()
    if not classes:
        st.warning("You need to create classes and enroll students first.")
        return
    
    # Tabs for attendance actions
    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "View Attendance", "Attendance Reports"])
    
    with tab1:
        st.subheader("Mark Attendance")
        
        # Class and date selection
        col1, col2 = st.columns(2)
        
        with col1:
            class_options = {f"{c['name']}": c['id'] for c in classes}
            selected_class = st.selectbox("Select Class", list(class_options.keys()))
        
        with col2:
            attendance_date = st.date_input("Attendance Date", value=date.today())
        
        if selected_class:
            class_id = class_options[selected_class]
            
            # Get enrolled students
            response = SessionManager.make_authenticated_request(f"/enrollments/class/{class_id}")
            if response and response.status_code == 200:
                enrollments = response.json()
                
                if enrollments:
                    st.subheader(f"Students in {selected_class}")
                    
                    # Create attendance form
                    with st.form("attendance_form"):
                        attendance_data = []
                        
                        for enrollment in enrollments:
                            student = enrollment['student']
                            
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
                            
                            with col1:
                                st.write(f"**{student['full_name']}**")
                                st.write(f"_{student['email']}_")
                            
                            with col2:
                                status = st.selectbox(
                                    "Status",
                                    options=["present", "absent", "tardy"],
                                    key=f"status_{student['id']}"
                                )
                            
                            with col3:
                                grade = st.number_input(
                                    "Grade",
                                    min_value=0,
                                    max_value=100,
                                    value=None,
                                    key=f"grade_{student['id']}"
                                )
                            
                            with col4:
                                notes = st.text_input(
                                    "Notes",
                                    key=f"notes_{student['id']}"
                                )
                            
                            attendance_data.append({
                                "student_id": student['id'],
                                "status": status,
                                "grade": grade,
                                "notes": notes
                            })
                        
                        submitted = st.form_submit_button("Save Attendance", type="primary")
                        
                        if submitted:
                            success_count = 0
                            error_count = 0
                            error_details = []  # Added to collect specific error messages
                            
                            for data in attendance_data:
                                attendance_datetime = datetime.combine(attendance_date, datetime.min.time())
                                
                                attendance_record = {
                                    "student_id": data["student_id"],
                                    "class_id": class_id,
                                    "date": attendance_datetime.isoformat(),
                                    "status": data["status"],
                                    "grade": data["grade"],
                                    "notes": data["notes"]
                                }
                                
                                response = SessionManager.make_authenticated_request(
                                    "/attendance/",
                                    method="POST",
                                    data=attendance_record
                                )
                                
                                if response and response.status_code == 200:
                                    success_count += 1
                                else:
                                    error_count += 1
                                    if response:
                                        try:
                                            error_msg = response.json().get("detail", f"HTTP {response.status_code}")
                                        except:
                                            error_msg = f"HTTP {response.status_code}"
                                    else:
                                        error_msg = "No response from server"
                                    
                                    student_name = next(
                                        (e['student']['full_name'] for e in enrollments 
                                         if e['student']['id'] == data["student_id"]), 
                                        "Unknown Student"
                                    )
                                    error_details.append(f"{student_name}: {error_msg}")
                            
                            if success_count > 0:
                                st.success(f"Attendance saved for {success_count} students!")
                            if error_count > 0:
                                st.error(f"Failed to save attendance for {error_count} students.")
                                with st.expander("Error Details"):
                                    for error in error_details:
                                        st.write(f"• {error}")
                            
                            if success_count > 0:
                                st.rerun()
                else:
                    st.info(f"No students enrolled in {selected_class}.")
            else:
                st.error("Failed to load enrolled students.")
    
    with tab2:
        st.subheader("View Attendance Records")
        
        # Class selection and date range
        col1, col2, col3 = st.columns(3)
        
        with col1:
            class_options = {f"{c['name']}": c['id'] for c in classes}
            selected_class = st.selectbox("Select Class", list(class_options.keys()), key="view_class")
        
        with col2:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        
        with col3:
            end_date = st.date_input("End Date", value=date.today())
        
        if selected_class:
            class_id = class_options[selected_class]
            
            # Get attendance records
            params = f"?start_date={start_date}&end_date={end_date}"
            response = SessionManager.make_authenticated_request(f"/attendance/class/{class_id}{params}")
            
            if response and response.status_code == 200:
                attendance_records = response.json()
                
                if attendance_records:
                    # Create DataFrame
                    records_data = []
                    for record in attendance_records:
                        records_data.append({
                            "Date": record['date'][:10],
                            "Student": record['student']['full_name'],
                            "Status": record['status'].title(),
                            "Grade": record.get('grade', 'N/A'),
                            "Notes": record.get('notes', '')
                        })
                    
                    df = pd.DataFrame(records_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Summary statistics
                    st.subheader("Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_records = len(attendance_records)
                    present_count = len([r for r in attendance_records if r['status'] == 'present'])
                    absent_count = len([r for r in attendance_records if r['status'] == 'absent'])
                    tardy_count = len([r for r in attendance_records if r['status'] == 'tardy'])
                    
                    with col1:
                        st.metric("Total Records", total_records)
                    with col2:
                        st.metric("Present", present_count)
                    with col3:
                        st.metric("Absent", absent_count)
                    with col4:
                        st.metric("Tardy", tardy_count)
                else:
                    st.info("No attendance records found for the selected period.")
            else:
                st.error("Failed to load attendance records.")
    
    with tab3:
        st.subheader("Attendance Reports")
        
        # Class selection
        class_options = {f"{c['name']}": c['id'] for c in classes}
        selected_class = st.selectbox("Select Class for Report", list(class_options.keys()), key="report_class")
        
        if selected_class:
            class_id = class_options[selected_class]
            
            # Get attendance data for visualization
            response = SessionManager.make_authenticated_request(f"/attendance/class/{class_id}")
            
            if response and response.status_code == 200:
                attendance_records = response.json()
                
                if attendance_records and len(attendance_records) > 0:
                    # Create visualizations
                    df = pd.DataFrame([
                        {
                            "Date": record['date'][:10],
                            "Student": record['student']['full_name'],
                            "Status": record['status']
                        }
                        for record in attendance_records
                    ])
                    
                    # Attendance trend over time
                    daily_stats = df.groupby(['Date', 'Status']).size().unstack(fill_value=0)
                    
                    # Ensure all required columns exist
                    for status in ['present', 'absent', 'tardy']:
                        if status not in daily_stats.columns:
                            daily_stats[status] = 0
                    
                    # Only create chart if we have sufficient data
                    if len(daily_stats) > 0 and not daily_stats.empty:
                        # Reset index to make Date a column
                        daily_stats_reset = daily_stats.reset_index()
                        
                        # Create the line chart with proper data validation
                        fig_trend = px.line(
                            daily_stats_reset,
                            x='Date',
                            y=['present', 'absent', 'tardy'],
                            title="Attendance Trend Over Time",
                            color_discrete_map={
                                'present': '#2E8B57',
                                'absent': '#DC143C',
                                'tardy': '#FF8C00'
                            }
                        )
                        
                        fig_trend.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Number of Students",
                            height=400
                        )
                        
                        st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("Insufficient data to generate attendance trend chart.")
                    
                    # Student-wise attendance summary
                    student_stats = df.groupby(['Student', 'Status']).size().unstack(fill_value=0)
                    
                    # Ensure all status columns exist for student stats too
                    for status in ['present', 'absent', 'tardy']:
                        if status not in student_stats.columns:
                            student_stats[status] = 0
                    
                    student_stats['Total'] = student_stats.sum(axis=1)
                    student_stats['Attendance Rate'] = (student_stats.get('present', 0) / student_stats['Total'] * 100).round(1)
                    
                    st.subheader("Student-wise Attendance Summary")
                    st.dataframe(student_stats, use_container_width=True)
                else:
                    st.info("No attendance data available for reports.")
            else:
                st.error("Failed to load attendance data.")

# Main teacher interface
def main_teacher_interface():
    """Main teacher interface with navigation"""
    SessionManager.init_session()
    SessionManager.require_role("teacher")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("👩‍🏫 Teacher Portal")
        user = SessionManager.get_user()
        if user:
            st.write(f"Welcome, **{user['full_name']}**")
            st.write(f"Email: {user['email']}")
        
        st.markdown("---")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Class Management", "Student Enrollment", "Attendance Management"]
        )
        
        st.markdown("---")
        
        if st.button("Logout", type="secondary"):
            SessionManager.logout()
            st.rerun()
    
    # Main content area
    if page == "Dashboard":
        show_teacher_dashboard()
    elif page == "Class Management":
        show_class_management()
    elif page == "Student Enrollment":
        show_student_enrollment()
    elif page == "Attendance Management":
        show_attendance_management()

if __name__ == "__main__":
    main_teacher_interface()
