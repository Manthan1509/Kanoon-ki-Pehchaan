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
import os
import getpass

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

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Example: "localhost"
        user="root",  # Example: "root"
        password="123456",  # Example: "your_mysql_password"
        database="lawyers"
    )

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
            font-size : 400px
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

username = getpass.getuser()

st.markdown('<div class="main-header"><h1>Kanoon Ki Pehchaan</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users WHERE name = %s",(username,))
users = cursor.fetchall()
cursor.close()
conn.close()
for user in users:
    d= user['degree']
    c=user['college']
    q=user['myQualifications']
    ph=user['Phone_No']
    sm=user['social_media']
    p_url=user['profile_pic_url']
    
new_degree = st.text_input("Edit Degree" , placeholder=f"{d}")
new_college = st.text_input("Edit College" , placeholder=f"{c}")
new_qualifications=st.text_area("Edit Qualifications" , placeholder=f"{q}")
new_phone_no = st.text_input("Edit Phone" , placeholder=f"{ph}")
new_sm = st.text_input("Edit Social Media" , placeholder=f"{sm}")
new_profile_pic = st.file_uploader("Update Profile Picture", type=["jpg", "png", "jpeg"])



if st.button("Submit"):

    
    if new_degree:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = ("UPDATE users SET degree = %s WHERE name = %s")
        
        cursor.execute(update_query,(new_degree, username))
        conn.commit()
        cursor.close()
        conn.close()
        
    if new_college:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = ("UPDATE users SET college = %s WHERE name = %s")
        
        cursor.execute(update_query,(new_college, username))
        conn.commit()
        cursor.close()
        conn.close()
        
    if new_qualifications:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = ("UPDATE users SET myQualifications = %s WHERE name = %s")
        
        cursor.execute(update_query,(new_qualifications, username))
        conn.commit()
        cursor.close()
        conn.close()
    
    if new_phone_no:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = ("UPDATE users SET Phone_No = %s WHERE name = %s")
        
        cursor.execute(update_query,(new_phone_no, username))
        conn.commit()
        cursor.close()
        conn.close()
        
    if new_sm:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = ("UPDATE users SET social_media = %s WHERE name = %s")
        
        cursor.execute(update_query,(new_sm, username))
        conn.commit()
        cursor.close()
        conn.close()

    if new_profile_pic:
         # Ensure the 'images' directory exists
         image_dir = "images"
         os.makedirs(image_dir, exist_ok=True)

         # Define the file path
         image_path = os.path.join(image_dir, f"{username}.jpg")  

         # Save the uploaded file
         with open(image_path, "wb") as f:
             f.write(new_profile_pic.read())

         # Store only the file path in the database
         conn = get_db_connection()
         cursor = conn.cursor()
         update_query = "UPDATE users SET profile_pic_url = %s WHERE name = %s"

         cursor.execute(update_query, (image_path, username))
         conn.commit()

         cursor.close()
         conn.close()
    
    st.success("Profile updated successfully!")
    
st.page_link("pages/lawer.py", label="Go back to Profile", icon="🔙")


    




