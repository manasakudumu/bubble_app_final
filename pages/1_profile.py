import streamlit as st
from db.bubbledb import get_user, add_user

def setupProfile():
    # Initialize user_email and user_name in session state if they don't exist
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None  # Or set to a default value if necessary
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None  # Or set to a default value if necessary

    user_email = st.session_state["user_email"]
    user_name = st.session_state["user_name"]

    # Now proceed with the rest of your profile setup logic
    if user_email:  # Proceed only if user_email is set
        existing_user = get_user(user_email)
        if not existing_user:
            st.header(f"Hi {user_name}!\nLet's Set Up Your Profile:")

        prefName = st.text_input("Enter Your Preferred Name", key="prefName_input")  # Unique key
        yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], key="yr_select")  # Unique key
        pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronouns_select")  # Unique key
        image = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="image_uploader")  # Unique key

        if st.button("Save Profile"):
            st.session_state["prefName"] = prefName
            st.session_state["yr"] = yr
            st.session_state["pronouns"] = pronouns
            st.session_state["image"] = image
            add_user(user_email, user_name, 'student')
            st.success("Role saved! Redirecting...")
            st.success("Profile completed successfully!")
            st.rerun()

    else:
        st.warning("Please log in to set up your profile.")

    # Fetch current user profile details
    user_data = get_user(user_email)  # Ensure this fetches correct data for the user
    if user_data:
        prefName = st.text_input("Enter Your Preferred Name", value=user_data.get("preferred_name", ""), key="prefName_input_existing")  # Unique key
        yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], index=["2025", "2026", "2027", "2028"].index(user_data.get("class_year", "2025")), key="yr_select_existing")  # Unique key
        pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], index=["She/Her", "He/Him", "They/Them"].index(user_data.get("pronouns", "She/Her")), key="pronouns_select_existing")  # Unique key
        image = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="image_uploader_existing")  # Unique key

setupProfile()
