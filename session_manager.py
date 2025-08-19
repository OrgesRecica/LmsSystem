import streamlit as st
from typing import Optional, Dict, Any
import requests
import json

class SessionManager:
    """Manage user sessions in Streamlit"""
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'token' not in st.session_state:
            st.session_state.token = None
    
    @staticmethod
    def login(email: str, password: str, api_base_url: str = "http://localhost:8000") -> bool:
        """Login user and store session"""
        try:
            response = requests.post(
                f"{api_base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.authenticated = True
                st.session_state.user = data["user"]
                st.session_state.token = data["access_token"]
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return False
    
    @staticmethod
    def signup(email: str, password: str, full_name: str, role: str, api_base_url: str = "http://localhost:8000") -> bool:
        """Register new user"""
        try:
            response = requests.post(
                f"{api_base_url}/auth/signup",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                    "role": role
                }
            )
            
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Signup error: {str(e)}")
            return False
    
    @staticmethod
    def logout():
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_user() -> Optional[Dict[Any, Any]]:
        """Get current user data"""
        return st.session_state.get('user')
    
    @staticmethod
    def get_token() -> Optional[str]:
        """Get current access token"""
        return st.session_state.get('token')
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get current user role"""
        user = SessionManager.get_user()
        return user.get('role') if user else None
    
    @staticmethod
    def require_auth():
        """Require authentication, redirect to login if not authenticated"""
        if not SessionManager.is_authenticated():
            st.warning("Please log in to access this page.")
            st.stop()
    
    @staticmethod
    def require_role(required_role: str):
        """Require specific role"""
        SessionManager.require_auth()
        user_role = SessionManager.get_user_role()
        if user_role != required_role:
            st.error(f"Access denied. Required role: {required_role}")
            st.stop()
    
    @staticmethod
    def make_authenticated_request(url: str, method: str = "GET", data: dict = None, api_base_url: str = "http://localhost:8000"):
        """Make authenticated API request"""
        token = SessionManager.get_token()
        if not token:
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(f"{api_base_url}{url}", headers=headers)
            elif method.upper() == "POST":
                response = requests.post(f"{api_base_url}{url}", headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(f"{api_base_url}{url}", headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(f"{api_base_url}{url}", headers=headers)
            else:
                return None
            
            return response
        except Exception as e:
            st.error(f"API request error: {str(e)}")
            return None
