import streamlit as st
import requests
from session_manager import SessionManager
from teacher_dashboard import main_teacher_interface
from student_dashboard import main_student_interface
from admin_dashboard import main_admin_interface

# Configure Streamlit page
st.set_page_config(
    page_title="Learning Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .login-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .info-message {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    
    .role-selector {
        background: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

def show_welcome_page():
    """Display welcome page with system information"""
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Learning Management System</h1>
        <p>A comprehensive platform for educational institutions to manage classes, attendance, and student performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>👩‍🏫 For Teachers</h3>
            <ul>
                <li>Create and manage classes</li>
                <li>Enroll students</li>
                <li>Mark attendance</li>
                <li>Assign grades</li>
                <li>View analytics and reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎓 For Students</h3>
            <ul>
                <li>View enrolled classes</li>
                <li>Check attendance records</li>
                <li>Monitor grades</li>
                <li>Track performance</li>
                <li>View personal analytics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ For Administrators</h3>
            <ul>
                <li>Manage all users</li>
                <li>System oversight</li>
                <li>Platform analytics</li>
                <li>Generate reports</li>
                <li>Monitor system health</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("---")
    st.subheader("Getting Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-message">
            <h4>New User?</h4>
            <p>Create your account by clicking the <strong>Sign Up</strong> tab above. Choose your role (Teacher or Student) during registration.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-message">
            <h4>Administrator Access</h4>
            <p>Use the default admin credentials:<br>
            <strong>Email:</strong> admin@example.com<br>
            <strong>Password:</strong> admin123</p>
        </div>
        """, unsafe_allow_html=True)
    
    # System status
    st.markdown("---")
    st.subheader("System Status")
    
    # Check API health
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            st.success("🟢 API Server: Online")
        else:
            st.error("🔴 API Server: Issues detected")
    except:
        st.error("🔴 API Server: Offline - Please start the FastAPI server")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Learning Management System v1.0 | Built with FastAPI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

def show_login_form():
    """Display login form"""
    
    st.markdown("""
    <div class="login-container">
        <h2 style="text-align: center; color: #667eea;">Login to Your Account</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("Enter Your Credentials")
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="Use admin@example.com for admin access"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Use admin123 for admin access"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if submitted:
            if email and password:
                with st.spinner("Authenticating..."):
                    success = SessionManager.login(email, password)
                    
                    if success:
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")
            else:
                st.error("Please enter both email and password.")
    
    # Quick access info
    st.markdown("---")
    st.info("""
    **Quick Access:**
    - **Admin:** admin@example.com / admin123
    - **Demo:** Create a teacher or student account to explore features
    """)

def show_signup_form():
    """Display signup form"""
    
    st.markdown("""
    <div class="login-container">
        <h2 style="text-align: center; color: #667eea;">Create New Account</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        st.subheader("Account Information")
        
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a secure password",
            help="Use a strong password with at least 8 characters"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )
        
        st.markdown("""
        <div class="role-selector">
            <h4>Select Your Role</h4>
        </div>
        """, unsafe_allow_html=True)
        
        role = st.selectbox(
            "I am a:",
            options=["teacher", "student"],
            format_func=lambda x: "Teacher" if x == "teacher" else "Student",
            help="Choose your role in the system. Admin accounts cannot be created through signup."
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submitted:
            if all([full_name, email, password, confirm_password, role]):
                if password != confirm_password:
                    st.error("Passwords do not match. Please try again.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    with st.spinner("Creating account..."):
                        success = SessionManager.signup(email, password, full_name, role)
                        
                        if success:
                            st.success("Account created successfully! Please login with your new credentials.")
                            st.balloons()
                        else:
                            st.error("Failed to create account. Email may already be registered.")
            else:
                st.error("Please fill in all required fields.")
    
    st.markdown("---")
    st.info("**Note:** Admin accounts are pre-created and cannot be registered through this form.")

def main():
    """Main application entry point"""
    
    # Initialize session
    SessionManager.init_session()
    
    # Check if user is authenticated
    if SessionManager.is_authenticated():
        user_role = SessionManager.get_user_role()
        
        # Route to appropriate dashboard based on role
        if user_role == "admin":
            main_admin_interface()
        elif user_role == "teacher":
            main_teacher_interface()
        elif user_role == "student":
            main_student_interface()
        else:
            st.error("Invalid user role. Please contact administrator.")
            if st.button("Logout"):
                SessionManager.logout()
                st.rerun()
    else:
        # Show authentication interface
        st.title("🎓 Learning Management System")
        
        # Create tabs for login and signup
        tab1, tab2, tab3 = st.tabs(["Welcome", "Login", "Sign Up"])
        
        with tab1:
            show_welcome_page()
        
        with tab2:
            show_login_form()
        
        with tab3:
            show_signup_form()

if __name__ == "__main__":
    main()
