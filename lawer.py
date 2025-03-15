import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import re
import getpass
from PIL import Image
import firebase_admin
from firebase_admin import credentials, auth , storage
from firebase_admin import db
import mysql.connector
import os

cred = credentials.Certificate("kanoon-ki-pehchaan-6ff0ed4a9c13.json")

# Initialize Firebase App (Only once in the application)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Load environment variables
load_dotenv()

# Page configuration (set only once at the beginning)
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
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
st.markdown(f'<h1>{username} Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" integrity="sha512-Evv84Mr4kqVGRNSgIGL/F/aIDqQb7xQ2vcrdIwxfjThSH8CSR7PBEakCr51Ck+w+/U6swU2Im1vVX0SVk9ABhg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
""", unsafe_allow_html=True)

def get_user_email(uid):
    try:
        user = auth.get_user(uid)
        return user.email
    except firebase_admin.auth.UserNotFoundError:
        return "User not found"

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT profile_pic_url FROM users WHERE name = %s",(username,))
users = cursor.fetchall()
cursor.close()
conn.close()



for user in users:
    
    if os.path.exists(user["profile_pic_url"]):
        st.image(user["profile_pic_url"], width=150, caption="Profile Picture")
    st.markdown("---")





st.markdown(f"""<h2>Personal Info</h2>
                <div>
               <span style="text-decoration:underline;">Name</span>
               <span> : {username}</span>
               </div>
               <div>
               <span style="text-decoration:underline;">Email</span>
               <span> : {get_user_email("dxyTfIes6PanyLAOKghvvpdWAos1")}</span>
               </div>               
            """,unsafe_allow_html=True)






        
st.header("Your Profile")

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users WHERE name = %s",(username,))
users = cursor.fetchall()
cursor.close()
conn.close()

# Display user profiles
for user in users:
    st.subheader(user["name"])
    st.text(f"Degree: {user['degree']}")
    st.text(f"College: {user['college']}")
    st.text(f"Qualifications : {user['myQualifications']}")
    st.text(f"Phone Number : {user['Phone_No']}")
    st.text(f"Social Media : {user['social_media']}")
    
st.markdown(
    """
    ---
    <div style="text-align: center;">
        <a href="/editlawyer" style="color: #ffffff; text-decoration: none;">
            <i class="fa-solid fa-user-pen"></i> Edit Details
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
