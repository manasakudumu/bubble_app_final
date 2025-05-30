import streamlit as st
from db.bubbledb import get_user
from nav import render_sidebar

from auth_guard import require_login
require_login()

st.markdown("""
    <style>
        ul[data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Resources & Support")

if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if "role" in st.session_state:
    render_sidebar(st.session_state["role"])


if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()


st.markdown("[Visit Wellesley Dining](https://www.wellesley.edu/life-at-wellesley/campus-dining)")
st.markdown("**Allergens:** [Navigating the Culinary Centers with Dietary Restrictions](http://www.wellesleyfresh.com/allergens-preferences.html)")
st.markdown("[Nutrition info series](http://www.wellesleyfresh.com/documents/Nutrition-Info-Series-January-2025-Edition-1.pdf)")

st.markdown("### Key contacts")
st.markdown("**General dining feedback:** dining@wellesley.edu")
st.markdown("**Dining manager (Tower, Bates, Stone):** 781-283-XXXXX")
st.markdown("**Wellesley fresh office:** 781-283-XXX")
st.markdown("**Campus nutritionist:** nutritionist@wellesley.edu")

st.markdown("### Emergencies or health issues")
st.markdown("If you are experiencing a medical emergency related to food, call campus police at **(781) 283-2121**.")
st.markdown("For non-urgent health concerns, contact Wellesley Health Services, HealthMD@wellesley.edu or call **781-283-2810**.")