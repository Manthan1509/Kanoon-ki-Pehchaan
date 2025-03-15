import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Page configuration (set only once at the beginning)
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
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

        /* Chat message styling */
        .stChatMessage {
            max-width: 100% !important;  /* Match input width */
            margin: 0.5rem auto;
            border-radius: 15px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadeInUp 0.5s ease-in-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stChatMessage:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        /* User message styling */
        [data-testid="user"] {
            margin-left: auto;
            background: rgba(227, 242, 253, 0.1) !important;
            border: 1px solid rgba(187, 222, 251, 0.2);
            color: #ffffff;
            width: 100%;  /* Match input width */
        }

        /* Assistant message styling */
        [data-testid="assistant"] {
            margin-right: auto;
            background: rgba(248, 249, 250, 0.1) !important;
            border: 1px solid rgba(233, 236, 239, 0.2);
            color: #ffffff;
            width: 100%;  /* Match input width */
        }

        /* Sidebar styling */
        .stSidebar {
            background: rgba(30, 30, 47, 0.9) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        .sidebar-content {
            padding: 1.5rem;
            color: #ffffff;
        }

        .sidebar-content h3 {
            color: #ff9933;
            animation: fadeIn 1s ease-in-out;
        }

        .sidebar-content p {
            color: #ffffff;
            animation: fadeIn 1.5s ease-in-out;
        }

        /* Footer styling */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 47, 0.9);
            padding: 1rem;
            text-align: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.9em;
            color: #ffffff;
            backdrop-filter: blur(10px);
            animation: fadeIn 2s ease-in-out;
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

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* SEO-friendly meta tags */
        <meta name="description" content="Kanoon ki Pehchaan - Your AI-powered Guide to Indian Legal System. Get instant answers to your legal queries related to Indian laws.">
        <meta name="keywords" content="Indian law, legal assistant, AI, Kanoon ki Pehchaan, legal advice, Indian legal system">
        <meta name="author" content="Kanoon ki Pehchaan Team">
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Initialize session state variables
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are Kanoon ki Pehchaan, an AI assistant specialized in Indian law. Provide accurate information about Indian legal matters, citing relevant sections, acts, and case laws where applicable. Do not answer questions unrelated to Indian law."}
        ]
    if "response_time" not in st.session_state:
        st.session_state.response_time = 0
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False

# Initialize LLM model with caching
@st.cache_resource
def get_model():
    try:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None

# Function to check if query is related to Indian law
def is_indian_law_related(query):
    if not query or not isinstance(query, str):
        return False
        
    query = query.lower()
    indian_legal_keywords = [
        "indian", "india", "ipc", "crpc", "constitution", "section", "act", "law", "legal",
        "supreme court", "high court", "district court", "tribunal", "judge", "advocate",
        "petition", "writ", "fir", "case", "bill", "parliament", "legislation",
        "fundamental rights", "directive principles", "preamble", "arrest", "bail",
        "property", "marriage", "divorce", "inheritance", "contract", "company", 
        "gst", "income tax", "consumer", "cyber", "digital", "reservation",
        "pil", "public interest litigation", "article", "amendment", "ibc", "rbi",
        "sebi", "ministry", "police", "criminal", "civil", "procedure", "evidence",
        "negotiable instruments", "arbitration", "lok adalat", "nyaya panchayat",
        "judicial review", "hindu", "muslim", "christian", "parsi", "personal law",
        "lok sabha", "rajya sabha", "ordinance", "notification", "gazette"
    ]
    
    # Check for keywords
    for keyword in indian_legal_keywords:
        if keyword in query:
            return True
    
    # Check for regex patterns
    patterns = [
        r"section \d+", r"article \d+", r"ipc \d+", r"crpc \d+",
        r"act of \d{4}", r"indian constitution", r"supreme court",
        r"high court", r"lok adalat", r"legal rights in india",
        r"indian penal", r"criminal procedure", r"civil procedure"
    ]
    
    for pattern in patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
            
    return False

# Create header function
def create_header():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖️ Kanoon ki Pehchaan")
    st.caption("Your AI-powered Guide to Indian Legal System")
    st.markdown('</div>', unsafe_allow_html=True)

# Display messages function
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                <div style="
                    background: rgba(227, 242, 253, 0.2);
                    padding: 12px;
                    border-radius: 15px;
                    border: 1px solid rgba(187, 222, 251, 0.3);
                    margin-bottom: 8px;
                    color: #ffffff;
                    width: 100%;
                    animation: fadeInUp 0.5s ease-in-out;
                ">
                    {message["content"]}
                </div>
                <div style="
                    font-size: 0.8em;
                    color: #bbdefb;
                    text-align: right;
                    margin-top: 4px;
                ">
                    {datetime.now().strftime("%H:%M")}
                </div>
                """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"""
                <div style="
                    background: rgba(248, 249, 250, 0.2);
                    padding: 12px;
                    border-radius: 15px;
                    border: 1px solid rgba(233, 236, 239, 0.3);
                    margin-bottom: 8px;
                    color: #ffffff;
                    width: 100%;
                    animation: fadeInUp 0.5s ease-in-out;
                ">
                    {message["content"]}
                </div>
                <div style="
                    font-size: 0.8em;
                    color: #e9ecef;
                    text-align: right;
                    margin-top: 4px;
                ">
                    {datetime.now().strftime("%H:%M")} | ⏱️ {st.session_state.response_time:.1f}s
                </div>
                """, unsafe_allow_html=True)

# Process user input function
def process_user_input(user_input):
    if not user_input or not user_input.strip():
        return
        
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div style="
            background: rgba(227, 242, 253, 0.2);
            padding: 12px;
            border-radius: 15px;
            border: 1px solid rgba(187, 222, 251, 0.3);
            margin-bottom: 8px;
            color: #ffffff;
            width: 100%;
            animation: fadeInUp 0.5s ease-in-out;
        ">
            {user_input}
        </div>
        <div style="
            font-size: 0.8em;
            color: #bbdefb;
            text-align: right;
            margin-top: 4px;
        ">
            {datetime.now().strftime("%H:%M")}
        </div>
        """, unsafe_allow_html=True)
    
    # Check if query is related to Indian law
    is_legal_query = is_indian_law_related(user_input)
    
    with st.chat_message("assistant", avatar="⚖️"):
        if not is_legal_query:
            response = "I apologize, but I can only answer questions related to Indian law. Please rephrase your question to focus on Indian legal matters."
            st.markdown(f"""
            <div style="
                background: rgba(248, 249, 250, 0.2);
                padding: 12px;
                border-radius: 15px;
                border: 1px solid rgba(233, 236, 239, 0.3);
                margin-bottom: 8px;
                color: #ffffff;
                width: 100%;
                animation: fadeInUp 0.5s ease-in-out;
            ">
                {response}
            </div>
            <div style="
                font-size: 0.8em;
                color: #e9ecef;
                text-align: right;
                margin-top: 4px;
            ">
                {datetime.now().strftime("%H:%M")} | ⏱️ 0.0s
            </div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Prepare messages for LangChain
            langchain_messages = []
            for message in st.session_state.messages:
                if message["role"] == "system":
                    langchain_messages.append(SystemMessage(content=message["content"]))
                elif message["role"] == "user":
                    langchain_messages.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=message["content"]))
            
            # Process with Gemini
            model = get_model()
            if model:
                start_time = time.time()
                with st.spinner("Researching Indian law..."):
                    # Enhance prompt with Indian law context
                    enhanced_prompt = (
                        f"{langchain_messages[-1].content} "
                        "Please provide information specifically in the context of Indian law, "
                        "citing relevant sections, provisions, or case laws from India where applicable."
                    )
                    langchain_messages[-1] = HumanMessage(content=enhanced_prompt)
                    
                    try:
                        result = model.invoke(langchain_messages)
                        end_time = time.time()
                        st.session_state.response_time = end_time - start_time
                        
                        # Display assistant message
                        st.markdown(f"""
                        <div style="
                            background: rgba(248, 249, 250, 0.2);
                            padding: 12px;
                            border-radius: 15px;
                            border: 1px solid rgba(233, 236, 239, 0.3);
                            margin-bottom: 8px;
                            color: #ffffff;
                            width: 100%;
                            animation: fadeInUp 0.5s ease-in-out;
                        ">
                            {result.content}
                        </div>
                        <div style="
                            font-size: 0.8em;
                            color: #e9ecef;
                            text-align: right;
                            margin-top: 4px;
                        ">
                            {datetime.now().strftime("%H:%M")} | ⏱️ {st.session_state.response_time:.1f}s
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add assistant message to session state
                        st.session_state.messages.append({"role": "assistant", "content": result.content})
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question."
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                st.error("Could not initialize the AI model. Please try again later.")

# Main function
def main():
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.switch_page("account.py")
        return
    
    # Add logout button in sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        if st.button("Logout"):
            # Clear session state and redirect to login page
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("account.py")
            st.stop()
            
        # Sidebar content
        st.markdown("### ⚙️ About Kanoon ki Pehchaan")
        st.markdown("""
            **Kanoon ki Pehchaan** is an AI-powered legal assistant designed to help you navigate the complexities of Indian law. 
            Whether you're a law student, professional, or just curious, this tool provides accurate and reliable information 
            on various legal matters in India.
        """)
        st.markdown("### 📚 Key Features")
        st.markdown("""
            - **Comprehensive Legal Database**: Access information on Indian laws, acts, and case laws.
            - **Real-time Assistance**: Get instant answers to your legal queries.
            - **User-friendly Interface**: Easy to use with a modern and intuitive design.
        """)
        st.markdown("### 📜 Disclaimer")
        st.markdown("""
            This tool is for informational purposes only and does not constitute legal advice. 
            Always consult a qualified legal professional for specific legal matters.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    
    # Main content
    create_header()
    
    # Welcome message if chat hasn't started
    if not st.session_state.chat_started:
        st.info("🙏 Namaste! Welcome to Kanoon ki Pehchaan! I'm your Indian legal assistant. How can I help you understand Indian laws today?")
        st.session_state.chat_started = True
        
    # Display previous messages
    display_messages()
    
    # Chat input
    user_input = st.chat_input("Ask about Indian laws and legal matters...")
    if user_input:
        process_user_input(user_input)

    # Footer
    total_chars = sum(len(m.get('content', '')) for m in st.session_state.messages)
    st.markdown(f'''
    <div class="footer">
        Powered by <strong>Gemini 1.5 Pro</strong> | 
        Response Time: {st.session_state.response_time:.1f}s | 
        Characters Processed: {total_chars}
    </div>
    ''', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()