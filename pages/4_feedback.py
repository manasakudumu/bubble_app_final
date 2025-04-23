import streamlit as st
from datetime import datetime
from db.bubbledb import submit_feedback, get_user


st.title("💬 Anonymous Feedback")
st.markdown("Your feedback will be anonymous and sent to dining staff.")

user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

msg = st.text_area("Enter your message")
if st.button("Send Feedback"):
    if msg.strip():
        submit_feedback(msg.strip(), str(datetime.now()))
        st.success("our feedback was sent anonymously!")
    else:
        st.warning("Please enter a message before submitting.")
