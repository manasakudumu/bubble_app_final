# auth_guard.py
import streamlit as st
from auth import google_login

def require_login():
    st.set_page_config(page_title="Bubble", layout="wide")

    # Show welcome + login message
    st.markdown("""
        <style>
            ul[data-testid="stSidebarNavItems"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

        st.sidebar.header("Login")
        st.sidebar.write("Please log in with your Google account:")
        if google_login():
            st.rerun()
        st.stop()
