import streamlit as st
from db.bubbledb import get_all_feedback, get_user

if "user_email" not in st.session_state:
    st.warning("Please log in to view this page.")
    st.stop()

# Fetch role from session (or DB if needed)
from db.bubbledb import get_user


st.title("Feedback Inbox")

user_email = st.session_state["user_email"]
user = get_user(user_email)
role = user[2]

if role != "Staff":
    st.error("Access denied: This page is only for staff.")
    st.stop()

user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

feedback = get_all_feedback()
if not feedback:
    st.info("No feedback received yet.")
else:
    for msg, timestamp in feedback:
        st.markdown(f" {msg}")
        st.caption(f" Submitted: {timestamp}")
