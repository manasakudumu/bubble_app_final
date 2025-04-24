import streamlit as st
from db.bubbledb import get_all_feedback, get_user

# Fetch role from session (or DB if needed)
from db.bubbledb import get_user


st.title("Feedback Inbox")

if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
role = user[2]

if role != "Staff":
    st.error("Access denied: This page is only for staff.")
    st.stop()


feedback = get_all_feedback()
if not feedback:
    st.info("No feedback received yet.")
else:
    for msg, timestamp in feedback:
        st.markdown(f" {msg}")
        st.caption(f" Submitted: {timestamp}")
