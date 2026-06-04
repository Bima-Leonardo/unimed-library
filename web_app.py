import streamlit as st
from web_admin import show_admin
from web_books import show_books_page

# Page Config
st.set_page_config(page_title="UNIMED Digital Library", page_icon="📚", layout="centered")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# IF NOT LOGGED IN (LOGIN PAGE)
if not st.session_state.logged_in:
    
    # Header Section (Clean text, no images)
    st.markdown("<h1 style='text-align: center; color: #1e7d32; margin-bottom: 0;'>UNIMED LIBRARY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #757575; font-style: italic;'>Web-Based Digital Library System</p>", unsafe_allow_html=True)

    st.write("---")
    
    # Notification/Info Box
    st.info("📢 **Information:** Use `admin` credentials to manage books or `user` credentials for student simulation.")

    # Login Form
    with st.container():
        st.markdown("### 🔐 System Login")
        username = st.text_input("Username", placeholder="Enter your username...")
        password = st.text_input("Password", type="password", placeholder="Enter your password...")

        st.write("") # Spacer
        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("🟢 USER LOGIN", use_container_width=True):
            if username == "user" and password == "user":
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.toast("Welcome User! 👋", icon="🔥")
                st.rerun()
            else:
                st.error("❌ User Login Failed! Invalid username or password.")

        if col_btn2.button("🟠 ADMIN LOGIN", use_container_width=True):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.toast("Welcome Admin! 🛡️", icon="🚀")
                st.rerun()
            else:
                st.error("❌ Admin Login Failed! Invalid username or password.")
            
    st.write("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>State University of Medan © 2026</p>", unsafe_allow_html=True)

# IF LOGGED IN (REDIRECT TO PAGES)
else:
    if st.session_state.role == "admin":
        show_admin()
    elif st.session_state.role == "user":
        show_books_page()
