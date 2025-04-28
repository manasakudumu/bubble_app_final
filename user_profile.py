import streamlit as st
import requests
from db.bubbledb import update_profile



@st.cache_data(ttl=3600)
def get_user_info(access_token):
    """Fetch and cache user profile info from Google."""
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"User info fetch failed: {e}")
    return None


def render_user_profile():
    """Render user profile photo and greeting, if user opts in."""
    access_token = st.session_state.get("access_token")
    if not access_token:
        return

    show_profile = st.sidebar.checkbox("Show profile info", value=True)

    if show_profile:
        uploaded_photo = st.session_state.get("image")  # Get uploaded image
        if "prefName" in st.session_state:
            first_name = st.session_state["prefName"]
        else:
            user = get_user_info(access_token)
            first_name = user.get("given_name") or user.get("name", "there").split()[0]

        
        if uploaded_photo:
            picture = uploaded_photo
        else:
            picture = user.get("picture")


        col1, col2 = st.sidebar.columns([1, 4])
        with col1:
            st.image(picture, width=40)
        with col2:
            st.markdown(f"**Hello, {first_name}!**")
    
