import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from session_manager import SessionManager
import requests

def show_admin_dashboard():
    """Main admin dashboard with system overview"""
    SessionManager.require_role("admin")
    
    st.title("System Administration Dashboard")
    st.markdown("---")
    
    # Get comprehensive system stats
    response = SessionManager.make_authenticated_request("/dashboard/stats")
    if response and response.status_code == 200:
        stats = response.json()
        
        # System Overview Metrics
        st.subheader("System Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Users",
                value=stats.get("total_users", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Teachers",
                value=stats.get("total_teachers", 0),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Students",
                value=stats.get("total_students", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="Active Classes",
                value=stats.get("total_classes", 0),
                delta=None
            )
        
        with col5:
            st.metric(
                label="Total Enrollments",
                value=stats.get("total_enrollments", 0),
                delta=None
            )
        
        st.markdown("---")
        
        # Platform Activity Overview
        st.subheader("Platform Activity")
        
        attendance_overview = stats.get("attendance_overview", {})
        
        if attendance_overview.get("total_records", 0) > 0:
            # Create comprehensive visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # System-wide attendance distribution
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
                    title="System-wide Attendance Distribution",
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Attendance metrics
                total_records = attendance_overview.get("total_records", 0)
                present_rate = attendance_overview.get("present_percentage", 0)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = present_rate,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "System Attendance Rate"},
                    delta = {'reference': 85},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#2E8B57"},
                        'steps': [
                            {'range': [0, 60], 'color': "#FFE4E1"},
                            {'range': [60, 80], 'color': "#FFFFE0"},
                            {'range': [80, 100], 'color': "#F0FFF0"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(height=400)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Detailed statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", total_records)
            with col2:
                st.metric("Present Sessions", attendance_overview.get("present", 0))
            with col3:
                st.metric("Absent Sessions", attendance_overview.get("absent", 0))
            with col4:
                st.metric("Tardy Sessions", attendance_overview.get("tardy", 0))
        else:
            st.info("No attendance data available in the system yet.")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("View All Users", type="primary"):
                st.session_state.admin_page = "User Management"
                st.rerun()
        
        with col2:
            if st.button("System Reports", type="primary"):
                st.session_state.admin_page = "System Reports"
                st.rerun()
        
        with col3:
            if st.button("Platform Analytics", type="primary"):
                st.session_state.admin_page = "Platform Analytics"
                st.rerun()
        
        with col4:
            if st.button("Class Overview", type="primary"):
                st.session_state.admin_page = "Class Management"
                st.rerun()
    else:
        st.error("Failed to load system statistics.")

def show_user_management():
    """User management interface"""
    SessionManager.require_role("admin")
    
    st.title("User Management")
    st.markdown("---")
    
    # Tabs for different user management functions
    tab1, tab2, tab3, tab4 = st.tabs(["All Users", "Teachers", "Students", "User Actions"])
    
    with tab1:
        st.subheader("All System Users")
        
        # Get all users
        response = SessionManager.make_authenticated_request("/users/")
        if response and response.status_code == 200:
            users = response.json()
            
            if users:
                # Create comprehensive user table
                user_data = []
                for user in users:
                    user_data.append({
                        "ID": user['id'],
                        "Full Name": user['full_name'],
                        "Email": user['email'],
                        "Role": user['role'].title(),
                        "Status": "Active" if user['is_active'] else "Inactive",
                        "Created": user['created_at'][:10]
                    })
                
                df = pd.DataFrame(user_data)
                
                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    role_filter = st.selectbox("Filter by Role", ["All", "Admin", "Teacher", "Student"])
                with col2:
                    status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
                
                # Apply filters
                filtered_df = df.copy()
                if role_filter != "All":
                    filtered_df = filtered_df[filtered_df['Role'] == role_filter]
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['Status'] == status_filter]
                
                # Display table
                st.dataframe(filtered_df, use_container_width=True)
                
                # User statistics
                st.subheader("User Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Users", len(df))
                with col2:
                    st.metric("Active Users", len(df[df['Status'] == 'Active']))
                with col3:
                    st.metric("Teachers", len(df[df['Role'] == 'Teacher']))
                with col4:
                    st.metric("Students", len(df[df['Role'] == 'Student']))
            else:
                st.info("No users found in the system.")
        else:
            st.error("Failed to load users.")
    
    with tab2:
        st.subheader("Teacher Management")
        
        # Get teachers
        response = SessionManager.make_authenticated_request("/users/teachers")
        if response and response.status_code == 200:
            teachers = response.json()
            
            if teachers:
                # Teacher details with class information
                for teacher in teachers:
                    with st.expander(f"👩‍🏫 {teacher['full_name']}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Email:** {teacher['email']}")
                            st.write(f"**Status:** {'Active' if teacher['is_active'] else 'Inactive'}")
                            st.write(f"**Joined:** {teacher['created_at'][:10]}")
                            
                            # Get teacher's classes
                            classes_response = SessionManager.make_authenticated_request("/classes/")
                            if classes_response and classes_response.status_code == 200:
                                all_classes = classes_response.json()
                                teacher_classes = [c for c in all_classes if c['teacher_id'] == teacher['id']]
                                
                                if teacher_classes:
                                    st.write(f"**Classes:** {len(teacher_classes)}")
                                    for class_obj in teacher_classes:
                                        st.write(f"  • {class_obj['name']}")
                                else:
                                    st.write("**Classes:** None")
                        
                        with col2:
                            if teacher['is_active']:
                                if st.button(f"Deactivate", key=f"deactivate_{teacher['id']}", type="secondary"):
                                    deactivate_response = SessionManager.make_authenticated_request(
                                        f"/users/{teacher['id']}",
                                        method="DELETE"
                                    )
                                    
                                    if deactivate_response and deactivate_response.status_code == 200:
                                        st.success(f"Teacher {teacher['full_name']} deactivated.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to deactivate teacher.")
                            else:
                                st.write("*Inactive*")
            else:
                st.info("No teachers found in the system.")
        else:
            st.error("Failed to load teachers.")
    
    with tab3:
        st.subheader("Student Management")
        
        # Get students
        response = SessionManager.make_authenticated_request("/users/students")
        if response and response.status_code == 200:
            students = response.json()
            
            if students:
                # Student search and filter
                search_term = st.text_input("Search students by name or email")
                
                filtered_students = students
                if search_term:
                    filtered_students = [
                        s for s in students 
                        if search_term.lower() in s['full_name'].lower() or 
                           search_term.lower() in s['email'].lower()
                    ]
                
                # Display students in a grid
                for i in range(0, len(filtered_students), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(filtered_students):
                            student = filtered_students[i + j]
                            
                            with col:
                                with st.container():
                                    st.write(f"**{student['full_name']}**")
                                    st.write(f"Email: {student['email']}")
                                    st.write(f"Status: {'Active' if student['is_active'] else 'Inactive'}")
                                    st.write(f"Joined: {student['created_at'][:10]}")
                                    
                                    # Get student's enrollments
                                    enrollments_response = SessionManager.make_authenticated_request(
                                        f"/enrollments/student/{student['id']}"
                                    )
                                    
                                    if enrollments_response and enrollments_response.status_code == 200:
                                        enrollments = enrollments_response.json()
                                        st.write(f"Enrolled Classes: {len(enrollments)}")
                                    
                                    if student['is_active']:
                                        if st.button(f"Deactivate", key=f"deactivate_student_{student['id']}", type="secondary"):
                                            deactivate_response = SessionManager.make_authenticated_request(
                                                f"/users/{student['id']}",
                                                method="DELETE"
                                            )
                                            
                                            if deactivate_response and deactivate_response.status_code == 200:
                                                st.success(f"Student {student['full_name']} deactivated.")
                                                st.rerun()
                                            else:
                                                st.error("Failed to deactivate student.")
            else:
                st.info("No students found in the system.")
        else:
            st.error("Failed to load students.")
    
    with tab4:
        st.subheader("User Actions & Analytics")
        
        # User registration trends
        st.subheader("User Registration Trends")
        
        # Get all users for analysis
        response = SessionManager.make_authenticated_request("/users/")
        if response and response.status_code == 200:
            users = response.json()
            
            if users:
                # Create DataFrame for analysis
                user_df = pd.DataFrame([
                    {
                        "Date": user['created_at'][:10],
                        "Role": user['role'].title(),
                        "Status": "Active" if user['is_active'] else "Inactive"
                    }
                    for user in users
                ])
                
                user_df['Date'] = pd.to_datetime(user_df['Date'])
                
                # Registration trend by role
                daily_registrations = user_df.groupby(['Date', 'Role']).size().unstack(fill_value=0)
                
                if not daily_registrations.empty:
                    fig_reg = px.line(
                        daily_registrations.reset_index(),
                        x='Date',
                        y=['Admin', 'Teacher', 'Student'],
                        title="User Registrations Over Time",
                        color_discrete_map={
                            'Admin': '#FF6B6B',
                            'Teacher': '#4ECDC4',
                            'Student': '#45B7D1'
                        }
                    )
                    
                    fig_reg.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Number of Registrations",
                        height=400
                    )
                    
                    st.plotly_chart(fig_reg, use_container_width=True)
                
                # Role distribution
                role_counts = user_df['Role'].value_counts()
                
                fig_roles = px.pie(
                    values=role_counts.values,
                    names=role_counts.index,
                    title="User Distribution by Role",
                    color_discrete_map={
                        'Admin': '#FF6B6B',
                        'Teacher': '#4ECDC4',
                        'Student': '#45B7D1'
                    }
                )
                
                st.plotly_chart(fig_roles, use_container_width=True)

def show_class_management():
    """System-wide class management"""
    SessionManager.require_role("admin")
    
    st.title("Class Management")
    st.markdown("---")
    
    # Get all classes
    response = SessionManager.make_authenticated_request("/classes/")
    if response and response.status_code == 200:
        classes = response.json()
        
        if classes:
            # Class overview table
            st.subheader("All Classes in System")
            
            class_data = []
            for class_obj in classes:
                # Get enrollment count
                enrollments_response = SessionManager.make_authenticated_request(f"/enrollments/class/{class_obj['id']}")
                enrollment_count = 0
                if enrollments_response and enrollments_response.status_code == 200:
                    enrollment_count = len(enrollments_response.json())
                
                class_data.append({
                    "ID": class_obj['id'],
                    "Class Name": class_obj['name'],
                    "Teacher": class_obj['teacher']['full_name'],
                    "Teacher Email": class_obj['teacher']['email'],
                    "Students": enrollment_count,
                    "Created": class_obj['created_at'][:10],
                    "Status": "Active" if class_obj['is_active'] else "Inactive"
                })
            
            df = pd.DataFrame(class_data)
            st.dataframe(df, use_container_width=True)
            
            # Class statistics
            st.subheader("Class Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Classes", len(classes))
            with col2:
                active_classes = len([c for c in classes if c['is_active']])
                st.metric("Active Classes", active_classes)
            with col3:
                total_enrollments = sum([row['Students'] for row in class_data])
                st.metric("Total Enrollments", total_enrollments)
            with col4:
                avg_class_size = total_enrollments / len(classes) if classes else 0
                st.metric("Avg Class Size", f"{avg_class_size:.1f}")
            
            # Class size distribution
            st.subheader("Class Size Distribution")
            
            class_sizes = [row['Students'] for row in class_data]
            
            fig_hist = px.histogram(
                x=class_sizes,
                nbins=10,
                title="Distribution of Class Sizes",
                labels={'x': 'Number of Students', 'y': 'Number of Classes'},
                color_discrete_sequence=['#4ECDC4']
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Teacher workload analysis
            st.subheader("Teacher Workload Analysis")
            
            teacher_workload = {}
            for class_obj in classes:
                teacher_name = class_obj['teacher']['full_name']
                if teacher_name not in teacher_workload:
                    teacher_workload[teacher_name] = {'classes': 0, 'students': 0}
                teacher_workload[teacher_name]['classes'] += 1
                
                # Add student count
                enrollments_response = SessionManager.make_authenticated_request(f"/enrollments/class/{class_obj['id']}")
                if enrollments_response and enrollments_response.status_code == 200:
                    teacher_workload[teacher_name]['students'] += len(enrollments_response.json())
            
            workload_data = []
            for teacher, data in teacher_workload.items():
                workload_data.append({
                    "Teacher": teacher,
                    "Classes": data['classes'],
                    "Total Students": data['students']
                })
            
            workload_df = pd.DataFrame(workload_data)
            st.dataframe(workload_df, use_container_width=True)
        else:
            st.info("No classes found in the system.")
    else:
        st.error("Failed to load classes.")

def show_system_reports():
    """Comprehensive system reports"""
    SessionManager.require_role("admin")
    
    st.title("System Reports")
    st.markdown("---")
    
    # Report tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Attendance Reports", "Performance Reports", "Usage Analytics", "Export Data"])
    
    with tab1:
        st.subheader("System-wide Attendance Reports")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        
        # Get all classes for attendance analysis
        classes_response = SessionManager.make_authenticated_request("/classes/")
        if classes_response and classes_response.status_code == 200:
            classes = classes_response.json()
            
            if classes:
                # Collect attendance data for all classes
                all_attendance_data = []
                
                for class_obj in classes:
                    params = f"?start_date={start_date}&end_date={end_date}"
                    attendance_response = SessionManager.make_authenticated_request(
                        f"/attendance/class/{class_obj['id']}{params}"
                    )
                    
                    if attendance_response and attendance_response.status_code == 200:
                        attendance_records = attendance_response.json()
                        
                        for record in attendance_records:
                            all_attendance_data.append({
                                "Date": record['date'][:10],
                                "Class": class_obj['name'],
                                "Teacher": class_obj['teacher']['full_name'],
                                "Student": record['student']['full_name'],
                                "Status": record['status']
                            })
                
                if all_attendance_data:
                    df = pd.DataFrame(all_attendance_data)
                    
                    # Summary statistics
                    total_records = len(df)
                    present_count = len(df[df['Status'] == 'present'])
                    absent_count = len(df[df['Status'] == 'absent'])
                    tardy_count = len(df[df['Status'] == 'tardy'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Records", total_records)
                    with col2:
                        st.metric("Present", present_count, delta=f"{(present_count/total_records*100):.1f}%")
                    with col3:
                        st.metric("Absent", absent_count, delta=f"{(absent_count/total_records*100):.1f}%")
                    with col4:
                        st.metric("Tardy", tardy_count, delta=f"{(tardy_count/total_records*100):.1f}%")
                    
                    # Daily attendance trend
                    daily_attendance = df.groupby(['Date', 'Status']).size().unstack(fill_value=0)
                    
                    fig_daily = px.line(
                        daily_attendance.reset_index(),
                        x='Date',
                        y=['present', 'absent', 'tardy'],
                        title="Daily Attendance Trends",
                        color_discrete_map={
                            'present': '#2E8B57',
                            'absent': '#DC143C',
                            'tardy': '#FF8C00'
                        }
                    )
                    
                    st.plotly_chart(fig_daily, use_container_width=True)
                    
                    # Class-wise attendance rates
                    class_attendance = df.groupby(['Class', 'Status']).size().unstack(fill_value=0)
                    class_attendance['Total'] = class_attendance.sum(axis=1)
                    class_attendance['Attendance Rate'] = (class_attendance.get('present', 0) / class_attendance['Total'] * 100).round(1)
                    
                    st.subheader("Class-wise Attendance Rates")
                    st.dataframe(class_attendance, use_container_width=True)
                else:
                    st.info("No attendance data found for the selected period.")
    
    with tab2:
        st.subheader("Performance Reports")
        
        # Get all users for performance analysis
        users_response = SessionManager.make_authenticated_request("/users/")
        classes_response = SessionManager.make_authenticated_request("/classes/")
        
        if users_response and users_response.status_code == 200 and classes_response and classes_response.status_code == 200:
            users = users_response.json()
            classes = classes_response.json()
            
            # Performance metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Platform Adoption", f"{len(users)} users")
            with col2:
                active_users = len([u for u in users if u['is_active']])
                st.metric("Active Users", f"{active_users}/{len(users)}")
            with col3:
                st.metric("Class Utilization", f"{len(classes)} classes")
            
            # User growth over time
            user_df = pd.DataFrame([
                {
                    "Date": user['created_at'][:10],
                    "Role": user['role'].title()
                }
                for user in users
            ])
            
            user_df['Date'] = pd.to_datetime(user_df['Date'])
            user_growth = user_df.groupby('Date').size().cumsum()
            
            fig_growth = px.line(
                x=user_growth.index,
                y=user_growth.values,
                title="Cumulative User Growth",
                labels={'x': 'Date', 'y': 'Total Users'}
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)
    
    with tab3:
        st.subheader("Usage Analytics")
        
        # Platform usage metrics
        st.write("**Platform Usage Overview**")
        
        # Get comprehensive stats
        response = SessionManager.make_authenticated_request("/dashboard/stats")
        if response and response.status_code == 200:
            stats = response.json()
            
            # Create usage summary
            usage_data = {
                "Metric": [
                    "Total Users",
                    "Active Teachers",
                    "Active Students",
                    "Total Classes",
                    "Total Enrollments",
                    "Attendance Records",
                    "System Attendance Rate"
                ],
                "Value": [
                    stats.get("total_users", 0),
                    stats.get("total_teachers", 0),
                    stats.get("total_students", 0),
                    stats.get("total_classes", 0),
                    stats.get("total_enrollments", 0),
                    stats.get("attendance_overview", {}).get("total_records", 0),
                    f"{stats.get('attendance_overview', {}).get('present_percentage', 0):.1f}%"
                ]
            }
            
            usage_df = pd.DataFrame(usage_data)
            st.dataframe(usage_df, use_container_width=True)
    
    with tab4:
        st.subheader("Export System Data")
        
        st.write("Export comprehensive system data for external analysis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export User Data", type="primary"):
                users_response = SessionManager.make_authenticated_request("/users/")
                if users_response and users_response.status_code == 200:
                    users = users_response.json()
                    user_df = pd.DataFrame(users)
                    csv = user_df.to_csv(index=False)
                    st.download_button(
                        label="Download Users CSV",
                        data=csv,
                        file_name=f"users_export_{date.today()}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("Export Class Data", type="primary"):
                classes_response = SessionManager.make_authenticated_request("/classes/")
                if classes_response and classes_response.status_code == 200:
                    classes = classes_response.json()
                    class_df = pd.DataFrame(classes)
                    csv = class_df.to_csv(index=False)
                    st.download_button(
                        label="Download Classes CSV",
                        data=csv,
                        file_name=f"classes_export_{date.today()}.csv",
                        mime="text/csv"
                    )

def show_platform_analytics():
    """Advanced platform analytics"""
    SessionManager.require_role("admin")
    
    st.title("Platform Analytics")
    st.markdown("---")
    
    # Get comprehensive data
    users_response = SessionManager.make_authenticated_request("/users/")
    classes_response = SessionManager.make_authenticated_request("/classes/")
    stats_response = SessionManager.make_authenticated_request("/dashboard/stats")
    
    if all(r and r.status_code == 200 for r in [users_response, classes_response, stats_response]):
        users = users_response.json()
        classes = classes_response.json()
        stats = stats_response.json()
        
        # Key Performance Indicators
        st.subheader("Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            user_growth_rate = len(users) / max(1, len(users) - 1) * 100 - 100 if len(users) > 1 else 0
            st.metric("User Growth", f"{len(users)}", delta=f"{user_growth_rate:.1f}%")
        
        with col2:
            attendance_rate = stats.get("attendance_overview", {}).get("present_percentage", 0)
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        
        with col3:
            avg_class_size = stats.get("total_enrollments", 0) / max(1, stats.get("total_classes", 1))
            st.metric("Avg Class Size", f"{avg_class_size:.1f}")
        
        with col4:
            active_rate = len([u for u in users if u['is_active']]) / len(users) * 100 if users else 0
            st.metric("User Retention", f"{active_rate:.1f}%")
        
        with col5:
            teacher_utilization = len(classes) / max(1, stats.get("total_teachers", 1))
            st.metric("Teacher Utilization", f"{teacher_utilization:.1f}")
        
        # Advanced visualizations
        st.subheader("Platform Health Metrics")
        
        # Create health score
        health_metrics = {
            "User Engagement": min(100, attendance_rate),
            "Platform Adoption": min(100, len(users) * 10),  # Scaled metric
            "Content Creation": min(100, len(classes) * 20),  # Scaled metric
            "User Retention": active_rate,
            "System Utilization": min(100, avg_class_size * 10)  # Scaled metric
        }
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=list(health_metrics.values()),
            theta=list(health_metrics.keys()),
            fill='toself',
            name='Platform Health'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Platform Health Dashboard"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Trend analysis
        st.subheader("Trend Analysis")
        
        # User registration trends
        user_df = pd.DataFrame([
            {
                "Date": user['created_at'][:10],
                "Role": user['role'].title()
            }
            for user in users
        ])
        
        user_df['Date'] = pd.to_datetime(user_df['Date'])
        
        # Monthly user registrations
        user_df['Month'] = user_df['Date'].dt.to_period('M')
        monthly_registrations = user_df.groupby(['Month', 'Role']).size().unstack(fill_value=0)
        
        if not monthly_registrations.empty:
            fig_monthly = px.bar(
                monthly_registrations.reset_index(),
                x='Month',
                y=['Teacher', 'Student'],
                title="Monthly User Registrations",
                color_discrete_map={
                    'Teacher': '#4ECDC4',
                    'Student': '#45B7D1'
                }
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.error("Failed to load analytics data.")

# Main admin interface
def main_admin_interface():
    """Main admin interface with navigation"""
    SessionManager.init_session()
    SessionManager.require_role("admin")
    
    st.set_page_config(
        page_title="LMS - Admin Portal",
        page_icon="⚙️",
        layout="wide"
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.title("⚙️ Admin Portal")
        user = SessionManager.get_user()
        if user:
            st.write(f"Welcome, **{user['full_name']}**")
            st.write(f"Email: {user['email']}")
        
        st.markdown("---")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "User Management", "Class Management", "System Reports", "Platform Analytics"]
        )
        
        st.markdown("---")
        
        # System status
        st.subheader("System Status")
        st.success("🟢 All Systems Operational")
        
        st.markdown("---")
        
        if st.button("Logout", type="secondary"):
            SessionManager.logout()
            st.rerun()
    
    # Main content area
    if page == "Dashboard":
        show_admin_dashboard()
    elif page == "User Management":
        show_user_management()
    elif page == "Class Management":
        show_class_management()
    elif page == "System Reports":
        show_system_reports()
    elif page == "Platform Analytics":
        show_platform_analytics()

if __name__ == "__main__":
    main_admin_interface()
