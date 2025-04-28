#app version 3 - with pages

import streamlit as st
from auth import google_login
from user_profile import render_user_profile
from db.bubbledb import (
    create_tables, create_journal_table,
    create_posts_table, create_feedback_table,
    get_user, add_user, delete_user
)

st.set_page_config(page_title="Bubble", page_icon="🫧", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
create_tables()
create_journal_table()
create_posts_table()
create_feedback_table()
delete_user("mk122@wellesley.edu")

st.sidebar.header("Login")

# Google OAuth login
if "access_token" not in st.session_state:
    st.sidebar.write("Please log in with your Google account:")
    if google_login():
        print("🆕 Version 3 is running!")
        st.rerun()
    st.stop()

render_user_profile()

st.markdown(
    """
    <div style='text-align: center; padding-top: 1rem;'>
        <h1 style='font-size: 3rem;'>🫧 Welcome to Bubble! 🫧</h1>
        <p style='font-size: 1.2rem; color: #ffb6c1;'>
            Your cozy space to journal your meals, reflect your mood, and share food love 💌
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# role selection
user_email = st.session_state["user_email"]
user_name = st.session_state["user_name"]
existing_user = get_user(user_email)

if not existing_user:
    st.markdown("### Welcome!")
    st.info("Please select your role to continue.")
    role_selection = st.radio("Are you a student or staff?", ["Student", "Staff"])
    if st.button("Save Role"):
        add_user(user_email, user_name, role_selection)
        st.success("Role saved! Redirecting...") 
        if role_selection == "Student":
            st.switch_page("pages/1_profile.py") 
        else:
            st.switch_page("pages/6_staffView.py")
    st.stop()

role = existing_user[2]

st.markdown("## 🌟 Where would you like to go today?")
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