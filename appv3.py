import streamlit as st
from auth import google_login
from user_profile import render_user_profile
from db.bubbledb import (
    create_tables, create_journal_table,
    create_posts_table, create_feedback_table,
    get_user, add_user, delete_user
)

st.set_page_config(page_title="Bubble", page_icon="🫧", layout="wide")

create_tables()
create_journal_table()
create_posts_table()
create_feedback_table()
# delete_user("mk122@wellesley.edu")

st.sidebar.header("Login")

# Google OAuth login
if "access_token" not in st.session_state:
    st.sidebar.write("Please log in with your Google account:")
    if google_login():
        st.rerun()
    st.stop()

render_user_profile()

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
            st.switch_page("pages/2_foodJournal.py") 
        else:
            st.switch_page("pages/6_staffView.py")

