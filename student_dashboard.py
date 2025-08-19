import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from session_manager import SessionManager
import requests

def show_student_dashboard():
    """Main student dashboard page"""
    SessionManager.require_role("student")
    
    st.title("Student Dashboard")
    st.markdown("---")
    
    # Get dashboard stats
    response = SessionManager.make_authenticated_request("/dashboard/stats")
    if response and response.status_code == 200:
        stats = response.json()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Enrolled Classes",
                value=stats.get("total_classes", 0),
                delta=None
            )
        
        with col2:
            overall_attendance = stats.get("overall_attendance", {})
            st.metric(
                label="Overall Attendance Rate",
                value=f"{overall_attendance.get('present_percentage', 0):.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Total Sessions",
                value=overall_attendance.get("total_records", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="Present Days",
                value=overall_attendance.get("present", 0),
                delta=None
            )
        
        st.markdown("---")
        
        # Overall Attendance Visualization
        st.subheader("My Attendance Overview")
        
        if overall_attendance.get("total_records", 0) > 0:
            # Create two columns for different visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart for attendance distribution
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Present', 'Absent', 'Tardy'],
                    values=[
                        overall_attendance.get("present", 0),
                        overall_attendance.get("absent", 0),
                        overall_attendance.get("tardy", 0)
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
            
            with col2:
                # Gauge chart for attendance rate
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = overall_attendance.get('present_percentage', 0),
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Attendance Rate"},
                    delta = {'reference': 80},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#2E8B57"},
                        'steps': [
                            {'range': [0, 50], 'color': "#FFE4E1"},
                            {'range': [50, 80], 'color': "#FFFFE0"},
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
        else:
            st.info("No attendance data available yet. Attend some classes to see your statistics!")
        
        # Class-wise Performance
        st.subheader("Performance by Class")
        
        class_attendance = stats.get("class_attendance", [])
        if class_attendance:
            # Create DataFrame for class performance
            class_df = pd.DataFrame([
                {
                    "Class": attendance["class_name"],
                    "Teacher": attendance["teacher_name"],
                    "Sessions": attendance["attendance_stats"]["total_sessions"],
                    "Present": attendance["attendance_stats"]["present_count"],
                    "Absent": attendance["attendance_stats"]["absent_count"],
                    "Tardy": attendance["attendance_stats"]["tardy_count"],
                    "Attendance Rate": f"{attendance['attendance_stats']['present_percentage']:.1f}%"
                }
                for attendance in class_attendance
            ])
            
            # Display table with styling
            st.dataframe(
                class_df,
                use_container_width=True,
                column_config={
                    "Attendance Rate": st.column_config.ProgressColumn(
                        "Attendance Rate",
                        help="Your attendance rate for this class",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # Bar chart for class-wise attendance rates
            if len(class_df) > 1:
                # Extract numeric values for plotting
                class_df['Attendance_Numeric'] = class_df['Attendance Rate'].str.rstrip('%').astype(float)
                
                fig_bar = px.bar(
                    class_df,
                    x="Class",
                    y="Attendance_Numeric",
                    title="Attendance Rate by Class",
                    color="Attendance_Numeric",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 100]
                )
                
                fig_bar.update_layout(
                    xaxis_title="Classes",
                    yaxis_title="Attendance Rate (%)",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("You're not enrolled in any classes yet.")
    else:
        st.error("Failed to load dashboard data.")

def show_my_classes():
    """Display student's enrolled classes"""
    SessionManager.require_role("student")
    
    st.title("My Classes")
    st.markdown("---")
    
    # Get enrolled classes
    response = SessionManager.make_authenticated_request("/classes/")
    if response and response.status_code == 200:
        classes = response.json()
        
        if classes:
            for class_obj in classes:
                with st.expander(f"📚 {class_obj['name']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {class_obj.get('description', 'No description available')}")
                        st.write(f"**Teacher:** {class_obj['teacher']['full_name']}")
                        st.write(f"**Teacher Email:** {class_obj['teacher']['email']}")
                        st.write(f"**Class Created:** {class_obj['created_at'][:10]}")
                    
                    with col2:
                        # Get class-specific attendance stats
                        user = SessionManager.get_user()
                        if user:
                            attendance_response = SessionManager.make_authenticated_request(
                                f"/attendance/student/{user['id']}?class_id={class_obj['id']}"
                            )
                            
                            if attendance_response and attendance_response.status_code == 200:
                                attendance_records = attendance_response.json()
                                
                                if attendance_records:
                                    total_sessions = len(attendance_records)
                                    present_count = len([r for r in attendance_records if r['status'] == 'present'])
                                    attendance_rate = (present_count / total_sessions * 100) if total_sessions > 0 else 0
                                    
                                    st.metric("Sessions Attended", f"{present_count}/{total_sessions}")
                                    st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
                                else:
                                    st.info("No attendance records yet")
                            else:
                                st.info("Unable to load attendance data")
        else:
            st.info("You're not enrolled in any classes yet. Contact your teacher to get enrolled.")
    else:
        st.error("Failed to load your classes.")

def show_attendance_records():
    """Display detailed attendance records"""
    SessionManager.require_role("student")
    
    st.title("My Attendance Records")
    st.markdown("---")
    
    # Get student's classes for filtering
    classes_response = SessionManager.make_authenticated_request("/classes/")
    if not classes_response or classes_response.status_code != 200:
        st.error("Failed to load classes.")
        return
    
    classes = classes_response.json()
    if not classes:
        st.info("You're not enrolled in any classes yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        class_options = {"All Classes": None}
        class_options.update({f"{c['name']}": c['id'] for c in classes})
        selected_class = st.selectbox("Filter by Class", list(class_options.keys()))
    
    with col2:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    
    with col3:
        end_date = st.date_input("End Date", value=date.today())
    
    # Get attendance records
    user = SessionManager.get_user()
    if not user:
        st.error("User session not found.")
        return
    
    # Build query parameters
    params = f"?start_date={start_date}&end_date={end_date}"
    if selected_class != "All Classes" and class_options[selected_class]:
        params += f"&class_id={class_options[selected_class]}"
    
    response = SessionManager.make_authenticated_request(f"/attendance/student/{user['id']}{params}")
    
    if response and response.status_code == 200:
        attendance_records = response.json()
        
        if attendance_records:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Detailed Records", "Summary Statistics", "Attendance Trends"])
            
            with tab1:
                st.subheader("Detailed Attendance Records")
                
                # Create DataFrame
                records_data = []
                for record in attendance_records:
                    records_data.append({
                        "Date": record['date'][:10],
                        "Class": record['class_obj']['name'],
                        "Teacher": record['class_obj']['teacher']['full_name'],
                        "Status": record['status'].title(),
                        "Grade": record.get('grade', 'N/A'),
                        "Notes": record.get('notes', '')
                    })
                
                df = pd.DataFrame(records_data)
                
                # Style the dataframe
                def style_status(val):
                    if val == 'Present':
                        return 'background-color: #d4edda; color: #155724'
                    elif val == 'Absent':
                        return 'background-color: #f8d7da; color: #721c24'
                    elif val == 'Tardy':
                        return 'background-color: #fff3cd; color: #856404'
                    return ''
                
                styled_df = df.style.applymap(style_status, subset=['Status'])
                st.dataframe(styled_df, use_container_width=True)
            
            with tab2:
                st.subheader("Summary Statistics")
                
                # Calculate statistics
                total_records = len(attendance_records)
                present_count = len([r for r in attendance_records if r['status'] == 'present'])
                absent_count = len([r for r in attendance_records if r['status'] == 'absent'])
                tardy_count = len([r for r in attendance_records if r['status'] == 'tardy'])
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Sessions", total_records)
                with col2:
                    st.metric("Present", present_count, delta=f"{(present_count/total_records*100):.1f}%")
                with col3:
                    st.metric("Absent", absent_count, delta=f"{(absent_count/total_records*100):.1f}%")
                with col4:
                    st.metric("Tardy", tardy_count, delta=f"{(tardy_count/total_records*100):.1f}%")
                
                # Class-wise breakdown
                if selected_class == "All Classes":
                    st.subheader("Breakdown by Class")
                    
                    class_breakdown = {}
                    for record in attendance_records:
                        class_name = record['class_obj']['name']
                        if class_name not in class_breakdown:
                            class_breakdown[class_name] = {'present': 0, 'absent': 0, 'tardy': 0}
                        class_breakdown[class_name][record['status']] += 1
                    
                    breakdown_data = []
                    for class_name, stats in class_breakdown.items():
                        total = sum(stats.values())
                        breakdown_data.append({
                            "Class": class_name,
                            "Total Sessions": total,
                            "Present": stats['present'],
                            "Absent": stats['absent'],
                            "Tardy": stats['tardy'],
                            "Attendance Rate": f"{(stats['present']/total*100):.1f}%"
                        })
                    
                    breakdown_df = pd.DataFrame(breakdown_data)
                    st.dataframe(breakdown_df, use_container_width=True)
            
            with tab3:
                st.subheader("Attendance Trends")
                
                # Create DataFrame for visualization
                df = pd.DataFrame([
                    {
                        "Date": record['date'][:10],
                        "Class": record['class_obj']['name'],
                        "Status": record['status']
                    }
                    for record in attendance_records
                ])
                
                # Convert date to datetime for better plotting
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Daily attendance trend
                daily_stats = df.groupby(['Date', 'Status']).size().unstack(fill_value=0)
                
                if not daily_stats.empty:
                    fig_trend = px.area(
                        daily_stats.reset_index(),
                        x='Date',
                        y=['present', 'absent', 'tardy'],
                        title="Daily Attendance Trend",
                        color_discrete_map={
                            'present': '#2E8B57',
                            'absent': '#DC143C',
                            'tardy': '#FF8C00'
                        }
                    )
                    
                    fig_trend.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Number of Sessions",
                        height=400
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                
                # Weekly attendance pattern
                df['Weekday'] = df['Date'].dt.day_name()
                weekday_stats = df.groupby(['Weekday', 'Status']).size().unstack(fill_value=0)
                
                if not weekday_stats.empty:
                    # Reorder weekdays
                    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_stats = weekday_stats.reindex([day for day in weekday_order if day in weekday_stats.index])
                    
                    fig_weekday = px.bar(
                        weekday_stats.reset_index(),
                        x='Weekday',
                        y=['present', 'absent', 'tardy'],
                        title="Attendance Pattern by Day of Week",
                        color_discrete_map={
                            'present': '#2E8B57',
                            'absent': '#DC143C',
                            'tardy': '#FF8C00'
                        }
                    )
                    
                    fig_weekday.update_layout(
                        xaxis_title="Day of Week",
                        yaxis_title="Number of Sessions",
                        height=400
                    )
                    
                    st.plotly_chart(fig_weekday, use_container_width=True)
        else:
            st.info("No attendance records found for the selected period.")
    else:
        st.error("Failed to load attendance records.")

def show_grades():
    """Display student grades"""
    SessionManager.require_role("student")
    
    st.title("My Grades")
    st.markdown("---")
    
    # Get student's attendance records with grades
    user = SessionManager.get_user()
    if not user:
        st.error("User session not found.")
        return
    
    response = SessionManager.make_authenticated_request(f"/attendance/student/{user['id']}")
    
    if response and response.status_code == 200:
        attendance_records = response.json()
        
        # Filter records that have grades
        graded_records = [r for r in attendance_records if r.get('grade') is not None]
        
        if graded_records:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Grade Records", "Grade Statistics", "Grade Trends"])
            
            with tab1:
                st.subheader("All Grade Records")
                
                # Create DataFrame
                grade_data = []
                for record in graded_records:
                    grade_data.append({
                        "Date": record['date'][:10],
                        "Class": record['class_obj']['name'],
                        "Teacher": record['class_obj']['teacher']['full_name'],
                        "Attendance": record['status'].title(),
                        "Grade": record['grade'],
                        "Notes": record.get('notes', '')
                    })
                
                df = pd.DataFrame(grade_data)
                
                # Style grades
                def style_grade(val):
                    if isinstance(val, (int, float)):
                        if val >= 90:
                            return 'background-color: #d4edda; color: #155724'
                        elif val >= 80:
                            return 'background-color: #d1ecf1; color: #0c5460'
                        elif val >= 70:
                            return 'background-color: #fff3cd; color: #856404'
                        else:
                            return 'background-color: #f8d7da; color: #721c24'
                    return ''
                
                styled_df = df.style.applymap(style_grade, subset=['Grade'])
                st.dataframe(styled_df, use_container_width=True)
            
            with tab2:
                st.subheader("Grade Statistics")
                
                # Calculate overall statistics
                grades = [r['grade'] for r in graded_records]
                avg_grade = sum(grades) / len(grades)
                max_grade = max(grades)
                min_grade = min(grades)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Grade", f"{avg_grade:.1f}")
                with col2:
                    st.metric("Highest Grade", max_grade)
                with col3:
                    st.metric("Lowest Grade", min_grade)
                with col4:
                    st.metric("Total Graded Sessions", len(graded_records))
                
                # Grade distribution
                st.subheader("Grade Distribution")
                
                fig_hist = px.histogram(
                    x=grades,
                    nbins=10,
                    title="Grade Distribution",
                    labels={'x': 'Grade', 'y': 'Frequency'},
                    color_discrete_sequence=['#2E8B57']
                )
                
                fig_hist.update_layout(height=400)
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Class-wise grade statistics
                st.subheader("Grades by Class")
                
                class_grades = {}
                for record in graded_records:
                    class_name = record['class_obj']['name']
                    if class_name not in class_grades:
                        class_grades[class_name] = []
                    class_grades[class_name].append(record['grade'])
                
                class_stats = []
                for class_name, grades in class_grades.items():
                    class_stats.append({
                        "Class": class_name,
                        "Average Grade": f"{sum(grades)/len(grades):.1f}",
                        "Highest Grade": max(grades),
                        "Lowest Grade": min(grades),
                        "Graded Sessions": len(grades)
                    })
                
                class_df = pd.DataFrame(class_stats)
                st.dataframe(class_df, use_container_width=True)
            
            with tab3:
                st.subheader("Grade Trends")
                
                # Create DataFrame for visualization
                df = pd.DataFrame([
                    {
                        "Date": record['date'][:10],
                        "Class": record['class_obj']['name'],
                        "Grade": record['grade']
                    }
                    for record in graded_records
                ])
                
                # Convert date to datetime
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                
                # Grade trend over time
                fig_trend = px.line(
                    df,
                    x='Date',
                    y='Grade',
                    color='Class',
                    title="Grade Trends Over Time",
                    markers=True
                )
                
                fig_trend.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Grade",
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Moving average
                if len(df) > 3:
                    df['Moving_Average'] = df['Grade'].rolling(window=3).mean()
                    
                    fig_ma = px.line(
                        df,
                        x='Date',
                        y=['Grade', 'Moving_Average'],
                        title="Grade Trend with Moving Average",
                        color_discrete_map={
                            'Grade': '#2E8B57',
                            'Moving_Average': '#FF8C00'
                        }
                    )
                    
                    fig_ma.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Grade",
                        height=400
                    )
                    
                    st.plotly_chart(fig_ma, use_container_width=True)
        else:
            st.info("No graded assignments found. Your teachers haven't assigned grades yet.")
    else:
        st.error("Failed to load grade information.")

# Main student interface
def main_student_interface():
    """Main student interface with navigation"""
    SessionManager.init_session()
    SessionManager.require_role("student")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎓 Student Portal")
        user = SessionManager.get_user()
        if user:
            st.write(f"Welcome, **{user['full_name']}**")
            st.write(f"Email: {user['email']}")
        
        st.markdown("---")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "My Classes", "Attendance Records", "My Grades"]
        )
        
        st.markdown("---")
        
        if st.button("Logout", type="secondary"):
            SessionManager.logout()
            st.rerun()
    
    # Main content area
    if page == "Dashboard":
        show_student_dashboard()
    elif page == "My Classes":
        show_my_classes()
    elif page == "Attendance Records":
        show_attendance_records()
    elif page == "My Grades":
        show_grades()

if __name__ == "__main__":
    main_student_interface()
