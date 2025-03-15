import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Example: "localhost"
        user="root",  # Example: "root"
        password="123456",  # Example: "your_mysql_password"
        database="lawyers"
    )

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("FIREBASE_API_KEY")

# Check if API key is available
if not api_key:
    logger.error("Firebase API key not found. Make sure to set the FIREBASE_API_KEY environment variable.")
    st.error("Configuration error: Firebase API key not available. Please contact support.")

# Initialize Firebase with credential file path checking
def init_firebase():
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            # Check if credential file exists
            cred_file = "kanoon-ki-pehchaan-6ff0ed4a9c13.json"
            if not Path(cred_file).exists():
                logger.error(f"Firebase credential file not found: {cred_file}")
                st.error("Configuration error: Firebase credentials not available. Please contact support.")
                return False
                
            cred = credentials.Certificate(cred_file)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        st.error("An error occurred during initialization. Please try again later.")
        return False

# Page configuration
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Kanoon ki Pehchaan
def local_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
            padding-bottom: 100px;
            color: #ffffff;
        }

        /* Header styling */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            animation: fadeIn 1s ease-in-out;
        }

        .flag-stripe {
            height: 8px;
            background: linear-gradient(90deg, #ff9933 33%, white 33% 66%, #138808 66%);
            margin-bottom: 1rem;
            animation: slideIn 1s ease-in-out;
        }

        /* Input styling */
        .stTextInput input {
            border-radius: 25px !important;
            padding: 1rem !important;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            width: 100%;  /* Full width */
            transition: all 0.3s ease;
        }

        .stTextInput input:focus {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }

        /* Button styling */
        .stButton button {
            border-radius: 25px !important;
            padding: 0.5rem 1rem !important;
            background: linear-gradient(135deg, #ff9933 0%, #138808 100%);
            color: #ffffff;
            border: none;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        /* Authentication form styling */
        .auth-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            max-width: 500px;
            margin: 0 auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Firebase Authentication functions
def sign_up_with_email_and_password(email, password, username=None):
    if not email or not password:
        st.error("Email and password are required.")
        return False
        
    if not username:
        username = email.split('@')[0]  # Default username from email if not provided
        
    try:
        # Initialize Firebase if not already initialized
        if not init_firebase():
            return False
            
        # Create user in Firebase
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        logger.info(f"User created successfully: {email}")
        st.success('Account created successfully!')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = ("INSERT INTO users VALUES(%s,NULL,NULL,NULL,NULL,NULL,NULL);")
        
        cursor.execute(insert_query,(username,))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set session state
        st.session_state.username = username
        st.session_state.useremail = email
        st.session_state.authenticated = True
        
        # Redirect to home page
        st.switch_page("pages/home.py")
        return True
    except Exception as e:
        error_message = str(e)
        logger.error(f"Signup failed: {error_message}")
        
        # Provide user-friendly error messages
        if "EMAIL_EXISTS" in error_message:
            st.error("This email is already registered. Try logging in instead.")
        elif "WEAK_PASSWORD" in error_message:
            st.error("Password should be at least 6 characters long.")
        elif "INVALID_EMAIL" in error_message:
            st.error("Please enter a valid email address.")
        else:
            st.error(f"Signup failed: {error_message}")
        return False

def sign_in_with_email_and_password(email, password):
    if not email or not password:
        st.error("Email and password are required.")
        return False
        
    try:
        # Make API request to Firebase Auth REST API
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # Send request
        r = requests.post(rest_api_url, params={"key": api_key}, data=json.dumps(payload))
        data = r.json()
        
        # Check for successful login
        if 'email' in data:
            logger.info(f"User logged in successfully: {email}")
            
            # Set session state
            st.session_state.username = data.get('displayName', 'User')
            st.session_state.useremail = data['email']
            st.session_state.authenticated = True
            
            # Redirect to home page
            st.switch_page("pages/home.py")
            return True
        else:
            error_code = data.get('error', {}).get('message', 'Unknown error')
            logger.error(f"Login failed: {error_code}")
            
            # Provide user-friendly error messages
            if "EMAIL_NOT_FOUND" in error_code:
                st.error("Email not found. Please check your email or sign up for a new account.")
            elif "INVALID_PASSWORD" in error_code:
                st.error("Invalid password. Please try again.")
            elif "USER_DISABLED" in error_code:
                st.error("This account has been disabled. Please contact support.")
            else:
                st.error(f"Login failed: {error_code}")
            return False
    except Exception as e:
        logger.error(f"Signin failed: {e}")
        st.error(f"An error occurred during login. Please try again later.")
        return False

def reset_password(email):
    if not email:
        return False, "Email address is required."
        
    try:
        # Make API request to Firebase Auth REST API
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {
            "email": email,
            "requestType": "PASSWORD_RESET"
        }
        
        # Send request
        r = requests.post(rest_api_url, params={"key": api_key}, data=json.dumps(payload))
        
        # Check response
        if r.status_code == 200:
            logger.info(f"Password reset email sent to: {email}")
            return True, "Password reset email sent successfully."
        else:
            error_message = r.json().get('error', {}).get('message', 'Unknown error')
            logger.error(f"Password reset failed: {error_message}")
            
            # Provide user-friendly error messages
            if "EMAIL_NOT_FOUND" in error_message:
                return False, "Email not found. Please check your email address."
            else:
                return False, f"Password reset failed: {error_message}"
    except Exception as e:
        logger.error(f"Password reset exception: {e}")
        return False, f"An error occurred: {str(e)}"

# Forget Password Function
def forget():
    st.subheader("Reset Password")
    email = st.text_input('Email Address', key='reset_email')
    
    if st.button('Send Reset Link'):
        if not email:
            st.warning("Please enter your email address.")
        else:
            success, message = reset_password(email)
            if success:
                st.success(message)
            else:
                st.warning(message)

# Authentication Page
def auth_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖️ Kanoon ki Pehchaan")
    st.caption("Your AI-powered Guide to Indian Legal System")
    st.markdown('</div>', unsafe_allow_html=True)

    # Create tabs for Login and Signup
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Login to Your Account")
        
        email = st.text_input('Email Address', key='login_email')
        password = st.text_input('Password', type='password', key='login_password')
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button('Login', key='login_button'):
                if not email or not password:
                    st.error('Please enter both email and password.')
                else:
                    sign_in_with_email_and_password(email, password)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        
        username = st.text_input('Username (Optional)', key='signup_username')
        email = st.text_input('Email Address', key='signup_email')
        password = st.text_input('Password', type='password', key='signup_password')
        confirm_password = st.text_input('Confirm Password', type='password', key='signup_confirm_password')
        
        # Terms and conditions checkbox
        terms_agree = st.checkbox('I agree to the Terms and Conditions')
        
        if st.button('Sign Up', key='signup_button'):
            if not email or not password:
                st.error('Please enter both email and password.')
            elif password != confirm_password:
                st.error('Passwords do not match.')
            elif not terms_agree:
                st.error('You must agree to the Terms and Conditions.')
            else:
                sign_up_with_email_and_password(email, password, username)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab3:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        forget()
        st.markdown('</div>', unsafe_allow_html=True)

# Main function
def main():
    # Check if user is already authenticated
    if st.session_state.get('authenticated', False):
        st.switch_page("pages/home.py")
    else:
        auth_page()

# Run the app
if __name__ == "__main__":
    main()