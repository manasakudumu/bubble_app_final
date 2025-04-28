import streamlit as st
from db.bubbledb import get_user, update_profile, add_user

#alter_users_table()
def setupProfile():
    # Initialize user_email and user_name in session state if they don't exist
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None  # Or set to a default value if necessary
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None  # Or set to a default value if necessary

    user_email = st.session_state["user_email"]
    user_name = st.session_state["user_name"]
    if user_email:  
        existing_user = get_user(user_email)[0]
        if not existing_user:
            st.header(f"Hi {user_name}!\nLet's Set Up Your Profile:")

            prefName = st.text_input("Enter Your Preferred Name", key="prefName_input")  # Unique key
            yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], key="yr_select")  # Unique key
            pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronouns_select")  # Unique key
            
            imageFile = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="image_uploader")  # Unique key
            if imageFile is not None:
                image = imageFile.read()


            if st.button("Save Profile"):
                st.session_state["prefName"] = prefName
                st.session_state["yr"] = yr
                st.session_state["pronouns"] = pronouns
                st.session_state["image"] = image
                update_profile(prefName, yr, pronouns, image)
                st.success("Profile completed successfully!")
                st.rerun()
        else:
            user_name=user_name.split()[0]
            st.header(f"Welcome back, {user_name}!\nEdit Your Profile Below")
            
            prefName = st.text_input("Enter Your Preferred Name", key="prefName_input")  # Unique key
            yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], key="yr_select")  # Unique key
            pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronouns_select")  # Unique key
            
            image=None
            imageFile= st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="image_uploader")  # Unique key
            if imageFile is not None:
                image = imageFile.read()
 
            if st.button("Save Profile"):
                st.session_state["prefName"] = prefName
                st.session_state["yr"] = yr
                st.session_state["pronouns"] = pronouns
                st.session_state["image"] = image
                update_profile(prefName, yr, pronouns, image)
                st.success("Profile updated successfully!")
    else:
        st.warning("Please log in to set up your profile.")

    # Fetch current user profile details
    # user_data = get_user(user_email)  # Ensure this fetches correct data for the user
    # if user_data:
    #     prefName = st.text_input("Enter Your Preferred Name", key="updateName")  # Unique key
    #     yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], key="yrUpdate")  # Unique key
    #     pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronounsUpdate")  # Unique key
    #     image = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="imageUpda")  # Unique key

setupProfile()