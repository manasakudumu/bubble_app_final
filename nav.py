import streamlit as st

def render_sidebar(role):
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
        if st.sidebar.button(" Profile"):
            st.switch_page("pages/1_profile.py")
        if st.sidebar.button(" Feedback Inbox"):
            st.switch_page("pages/6_staffView.py")
        

    st.sidebar.divider()
    if st.sidebar.button(" Home"):
        st.switch_page("appv3.py")

    if st.sidebar.button(" Log Out"):
        st.session_state.clear()
        st.rerun()
