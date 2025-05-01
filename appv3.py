import streamlit as st
from auth import google_login
from user_profile import render_user_profile
from db.bubbledb import (
    create_tables, create_journal_table,
    create_posts_table, create_feedback_table,
    get_user, add_user, delete_user
)

st.set_page_config(page_title="Bubble", page_icon="🫧", layout="wide")

# hide default nav
st.markdown("""
    <style>
        ul[data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

create_tables()
create_journal_table()
create_posts_table()
create_feedback_table()
# delete_user("mk122@wellesley.edu")

# auth
st.sidebar.header("Login")

# welcome message
if "access_token" not in st.session_state:
    st.markdown("""
        <div style='
            background-color: #fef6fb;
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            border: 2px solid #ffd6e7;
            margin-top: 3rem;
        '>
            <h1 style='font-size: 3.2rem;'>🫧 Welcome to Bubble! 🫧</h1>
            <p style='font-size: 1.3rem;'>
                Please log in with your Wellesley Google account to begin journaling your meals
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.write("Please log in with your Google account:")
    if google_login():
        st.rerun()
    st.stop()


render_user_profile()

# get role
user_email = st.session_state["user_email"]
user_name = st.session_state["user_name"]

if "role" not in st.session_state:
    user = get_user(user_email)
    if user:
        st.session_state["role"] = user[2]

role = st.session_state.get("role")

# role not selected
user = get_user(user_email)
if not user:
    st.markdown("### Welcome!")
    st.info("Please select your role to continue.")
    role_selection = st.radio("Are you a student or staff?", ["Student", "Staff"])
    if st.button("Save Role"):
        add_user(user_email, user_name, role_selection)  
        st.session_state["role"] = role_selection        
        st.success("Role saved! Reloading...")
        st.rerun()
else:
    st.session_state["role"] = user[2]


# custom sidebar
st.sidebar.title("Navigation")

if role == "Student":
    if st.sidebar.button(" My Profile"):
        st.switch_page("pages/1_profile.py")
    if st.sidebar.button(" Food Journal"):
        st.switch_page("pages/2_foodJournal.py")
    if st.sidebar.button(" Community"):
        st.switch_page("pages/3_community.py")
    if st.sidebar.button(" Send Feedback"):
        st.switch_page("pages/4_feedback.py")
    if st.sidebar.button(" Resources"):
        st.switch_page("pages/5_resources.py")
    if st.sidebar.button(" Trends"):
        st.switch_page("pages/7_visualizations.py")

elif role == "Staff":
    if st.sidebar.button(" Feedback Inbox"):
        st.switch_page("pages/6_staffView.py")

st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("appv3.py")

if st.sidebar.button(" Log Out"):
    st.session_state.clear()
    st.rerun()


# 
if role:
    st.markdown("""
        <div style='text-align: center; padding-top: 1rem;'>
            <h1 style='font-size: 3rem;'>🫧 Welcome to Bubble! 🫧</h1>
            <p style='font-size: 1.2rem; color: #ffb6c1;'>
                Your cozy space to journal your meals, reflect your mood, and share food love 💌
            </p>
        </div>
    """, unsafe_allow_html=True)

if role:
    st.divider()
    st.markdown("##  Where would you like to go today?")
    col1, col2, col3 = st.columns(3)

if role == "Student":
    with col1:
        st.subheader("Food Journal")
        st.write("Track your meals and moods.")
        if st.button("Go to Journal"):
            st.switch_page("pages/2_foodJournal.py")
    with col2:
        st.subheader("Community")
        st.write("Post, explore, and rate meals.")
        if st.button("Go to Community"):
            st.switch_page("pages/3_community.py")
    with col3:
        st.subheader("Feedback")
        st.write("Leave anonymous feedback.")
        if st.button("Send Feedback"):
            st.switch_page("pages/4_feedback.py")
    st.divider()
    st.markdown("### More tools")
    col4, col5 = st.columns(2)
    with col4:
        if st.button("Resources"):
            st.switch_page("pages/5_resources.py")
    with col5:
        if st.button("My Profile"):
            st.switch_page("pages/1_profile.py")

elif role == "Staff":
    st.success("You're logged in as dining staff")
    if st.button("View Feedback Inbox"):
        st.switch_page("pages/6_staffView.py")
