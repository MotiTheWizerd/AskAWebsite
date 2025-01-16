import streamlit as st
from typing import Dict, List
import json
import logging
from background_scraper import start_background_scraping
from rag.rag_engine import RAGEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize session state for chat history if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'websites' not in st.session_state:
    st.session_state.websites = {}

if 'scraping_queues' not in st.session_state:
    st.session_state.scraping_queues = {}

# Initialize the previous input state if it doesn't exist
if 'previous_input' not in st.session_state:
    st.session_state.previous_input = ''

def save_website(name: str, url: str):
    """Save a new website to the session state and start background scraping."""
    st.session_state.websites[name] = {"url": url, "status": "pending"}
    logger.info(f"Added new website: {name} with URL: {url}")
    
    # Add system message to chat
    st.session_state.messages.append({
        "role": "system",
        "content": f"Started scraping website: {name}\nURL: {url}"
    })
    
    # Start background scraping
    queue = start_background_scraping(url)
    st.session_state.scraping_queues[name] = queue

def check_scraping_status():
    """Check and update status of ongoing scraping processes."""
    for name, queue in st.session_state.scraping_queues.items():
        if queue is not None:
            try:
                while not queue.empty():
                    status = queue.get_nowait()
                    st.session_state.websites[name]["status"] = status["status"]
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"Website {name}: {status['message']}"
                    })
                    
                    if status["status"] in ["completed", "failed", "error"]:
                        st.session_state.scraping_queues[name] = None
                        
            except Exception as e:
                logger.error(f"Error checking status for {name}: {str(e)}")

def create_website_modal():
    """Create a modal for adding new websites."""
    with st.form(key="website_form"):
        website_name = st.text_input("Website Name", value="test")
        website_url = st.text_input("Website URL", value="https://ai.pydantic.dev/sitemap.xml")
        
        # Create a container for buttons in the same row
        col1, col2 = st.columns([1, 1])  # Equal width columns for buttons
        with col1:
            submit_button = st.form_submit_button(label="Start Scraping")
        with col2:
            cancel_button = st.form_submit_button(label="Cancel")
        
        if cancel_button:
            return True
        if submit_button and website_name and website_url:
            with st.spinner(f"Starting to scrape {website_name}..."):
                save_website(website_name, website_url)
                logger.info(f"Scraping process initiated for {website_name}")
                st.success(f"Successfully started scraping {website_name}")
            return True
    return False

def handle_input():
    """Handle the input when text changes (enter is pressed)"""
    current_input = st.session_state.user_input
    if current_input and current_input != st.session_state.previous_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": current_input})
        
        try:
            # Query using RAGEngine
            with st.spinner("Thinking..."):
                rag_engine = RAGEngine()
                response = rag_engine.query(current_input)
            
            # Add AI response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Sorry, I couldn't process your question. Please try again."
            })
        
        # Store the current input as previous
        st.session_state.previous_input = current_input
        # Clear the input
        st.session_state.user_input = ''

# Page configuration
st.set_page_config(
    page_title="AskAWebsite",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e6e6e6;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 80%;
        color: #1a1a1a;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .chat-message-content {
        flex: 1;
        min-width: 0;
        line-height: 1.5;
    }
    .user-message {
        background-color: #e6f3ff;
        margin-right: auto;
        margin-left: 0;
        text-align: left;
    }
    .system-message {
        background-color: #f0f2f6;
        margin-right: auto;
    }
    .user-icon {
        font-size: 1.2rem;
        color: #2c3e50;
        flex-shrink: 0;
    }
    </style>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

# Header Section
col1, col2 = st.columns([6, 1])
with col1:
    st.title("AskAWebsite")
with col2:
    if st.button("➕", help="Add new website"):
        st.session_state.show_modal = True

# Show modal if button was clicked
if st.session_state.get('show_modal', False):
    if create_website_modal():
        st.session_state.show_modal = False
        st.rerun()

# Check scraping status
check_scraping_status()

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><i class="fas fa-user user-icon"></i><div class="chat-message-content">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message system-message"><div class="chat-message-content">{message["content"]}</div></div>', unsafe_allow_html=True)

# Chat input
with st.container():
    st.text_input(
        "Ask a question about the website:", 
        key="user_input",
        on_change=handle_input
    )
