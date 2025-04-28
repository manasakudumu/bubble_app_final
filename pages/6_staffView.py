import streamlit as st
from db.bubbledb import get_all_feedback, get_user

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Page config
st.title("Dining Staff Feedback Inbox")
st.markdown("_View anonymous feedback from students about your dining hall._")

# Auth check
if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
if user[2] == "Student":
    st.error("Access denied: This page is only for dining staff.")
    st.stop()

# Ask for dining hall
dining_halls = ['Bae', 'Bates', 'Stone', 'Tower']
selected_hall = st.selectbox("Which dining hall are you managing?", dining_halls)

# Fetch and filter feedback
feedback = get_all_feedback()
filtered_feedback = [
    (msg, timestamp) for msg, timestamp in feedback if selected_hall.lower() in msg.lower()
]

if not filtered_feedback:
    st.info(f"No feedback received for {selected_hall} yet.")
else:
    st.markdown(f"### Showing feedback for **{selected_hall}**")
    for i, (msg, timestamp) in enumerate(reversed(filtered_feedback)):
        with st.container():
            st.markdown(
                f"""
                <div style='
                    background-color: white;
                    border-radius: 12px;
                    padding: 1.2rem 1.5rem;
                    margin-bottom: 1.2rem;
                    border: 1px solid #e0d2d8;
                    color: #000000;
                '>
                    <h4 style='color: #ff9ecb; margin-top: 0;'>Feedback #{len(filtered_feedback) - i}</h4>
                    <pre style='white-space: pre-wrap; font-size: 0.95rem; color: #000000;'>{msg}</pre>
                    <p style='font-size: 0.85rem; color: #444;'>Submitted: {timestamp[:16]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )



