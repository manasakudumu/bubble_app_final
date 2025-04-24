import streamlit as st
from db.bubbledb import get_user, add_user,alter_users_table

#alter_users_table()
def setupProfile():
    if "user_email" not in st.session_state or "user_name" not in st.session_state:
        st.warning("Please log in to set up your profile.")
        return

    user_email = st.session_state["user_email"]
    user_name = st.session_state["user_name"]
    user_data = get_user(user_email)

<<<<<<< HEAD
    # Now proceed with the rest of your profile setup logic
    if user_email:  # Proceed only if user_email is set
        existing_user = get_user(user_email)[0]
        if not existing_user:
            st.header(f"Hi {user_name}!\nLet's Set Up Your Profile:")
=======
    st.header(f"Hi {user_name}! ")
>>>>>>> a8111422e0e2bc07776a3d33e5f2e86df572b105

    if not user_data:
        st.subheader("Let's set up your profile:")

        pref_name = st.text_input("Preferred Name", key="pref_name_new")
        yr = st.selectbox("Class Year", ["2025", "2026", "2027", "2028"], key="year_new")
        pronouns = st.selectbox("Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronouns_new")
        image = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="image_new")

        if st.button("Save Profile"):
            add_user(user_email, user_name, "Student")  # You may want to store other details too
            st.session_state["prefName"] = pref_name
            st.session_state["yr"] = yr
            st.session_state["pronouns"] = pronouns
            st.session_state["image"] = image
<<<<<<< HEAD
            add_user(user_email, user_name, 'student', prefName, yr, pronouns)
            st.success("Profile completed successfully!")
=======
            st.success("Profile saved! ")
>>>>>>> a8111422e0e2bc07776a3d33e5f2e86df572b105
            st.rerun()
    else:
        st.subheader("Your current profile:")

<<<<<<< HEAD
    # Fetch current user profile details
    # user_data = get_user(user_email)  # Ensure this fetches correct data for the user
    # if user_data:
    #     prefName = st.text_input("Enter Your Preferred Name", key="updateName")  # Unique key
    #     yr = st.selectbox("Select Your Class Year", ["2025", "2026", "2027", "2028"], key="yrUpdate")  # Unique key
    #     pronouns = st.selectbox("Select Your Pronouns", ["She/Her", "He/Him", "They/Them"], key="pronounsUpdate")  # Unique key
    #     image = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="imageUpda")  # Unique key
=======
        preferred_name = user_data[3] if len(user_data) > 3 else ""
        class_year = user_data[4] if len(user_data) > 4 else "2025"
        pronouns_value = user_data[5] if len(user_data) > 5 else "She/Her"

        pref_name = st.text_input("Preferred Name", value=preferred_name, key="pref_name_existing")
        yr = st.selectbox("Class Year", ["2025", "2026", "2027", "2028"],
                          index=["2025", "2026", "2027", "2028"].index(class_year), key="year_existing")
        pronouns = st.selectbox("Pronouns", ["She/Her", "He/Him", "They/Them"],
                                index=["She/Her", "He/Him", "They/Them"].index(pronouns_value), key="pronouns_existing")

        image = st.file_uploader("Upload New Profile Photo", type=["jpg", "jpeg", "png"], key="image_existing")

        if st.button("Update Profile"):
            st.success("Profile updated! ")
            st.switch_page("appv3.py")
>>>>>>> a8111422e0e2bc07776a3d33e5f2e86df572b105

setupProfile()
