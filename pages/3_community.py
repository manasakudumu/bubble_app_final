# pages/3_community.py

from auth_guard import require_login  
require_login()                # ← Must be first Streamlit-related call

import streamlit as st
import uuid, os
from datetime import datetime
from db.bubbledb import (
    add_community_post,
    get_all_community_posts,
    get_user,
    delete_community_post,
)
from nav import render_sidebar

# now it’s safe to do any st.markdown, st.title, etc.
st.markdown(
    """
    <style>
        ul[data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("📸 Community Feed")

# --- authenication ---
if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state.get("user_email")
user = get_user(user_email)

if not user or user[2] != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

# render the sidebar now that we know the role
st.session_state["role"] = "Student"
render_sidebar("Student")

# -- new post form ---
# reset form defaults if not yet in session_state
if "post_star_rating" not in st.session_state:
    st.session_state.post_star_rating = 3
if "post_title" not in st.session_state:
    st.session_state.post_title = ""
if "post_description" not in st.session_state:
    st.session_state.post_description = ""

# Star rating selector
st.markdown("### Rate this post")
rating_cols = st.columns(5)
for i in range(1, 6):
    star = "⭐" if i <= st.session_state.post_star_rating else "☆"
    if rating_cols[i - 1].button(star, key=f"post_star_{i}"):
        st.session_state.post_star_rating = i
st.markdown(f"You rated this: **{st.session_state.post_star_rating} / 5**")

# Post creation form
with st.form("post_form"):
    img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    title = st.text_input("Post Title", value=st.session_state.post_title)
    description = st.text_area("Post Description", value=st.session_state.post_description)
    submitted = st.form_submit_button("Post")

if submitted:
    if img and title:
        os.makedirs("posts", exist_ok=True)
        post_id = str(uuid.uuid4())
        file_path = f"posts/{post_id}.jpg"
        with open(file_path, "wb") as f:
            f.write(img.read())

        add_community_post(
            post_id,
            user_email,
            file_path,
            f"{title}||{description}",
            st.session_state.post_star_rating,
            str(datetime.now()),
        )
        st.success("Post uploaded!")
        # reset form state
        st.session_state.post_title = ""
        st.session_state.post_description = ""
        st.session_state.post_star_rating = 3
        st.experimental_rerun()
    else:
        st.warning("Please include at least an image and a title.")

# -- delete helper ---
def delete_post(post_id, img_path):
    # remove image file
    try:
        if os.path.exists(img_path):
            os.remove(img_path)
    except Exception as e:
        st.error(f"Error deleting image file: {e}")

    # remove from DB
    try:
        delete_community_post(post_id)
    except Exception as e:
        st.error(f"Error deleting post from database: {e}")

    # mark for UI removal
    st.session_state.deleted_post = post_id
    st.experimental_rerun()

# --- FILTERS ---
st.markdown("### 📂 Filter Posts")

# fetch and preprocess all posts
posts = get_all_community_posts()
all_dates = sorted({created_at.split(" ")[0] for (_, _, _, _, _, created_at) in posts})

filter_username = st.text_input(
    "Filter by username contains…",
    value="",
    help="Type any substring of the poster’s username",
)
filter_date = st.selectbox("Filter by date", ["All"] + all_dates)

# apply filters
filtered = []
for post_id, email, img_path, full_caption, rating, created_at in posts:
    username = email.split("@")[0]
    date_only = created_at.split(" ")[0]

    if filter_username and filter_username.lower() not in username.lower():
        continue
    if filter_date != "All" and date_only != filter_date:
        continue
    filtered.append((post_id, email, img_path, full_caption, rating, created_at))

# decide which list to display
if (filter_username or filter_date != "All") and not filtered:
    st.info("No posts match your filters.")
    display_posts = []
elif filtered:
    display_posts = filtered
else:
    display_posts = posts

# --- RENDER POSTS ---
cols = st.columns(3)
for i, (post_id, email, img_path, full_caption, rating, created_at) in enumerate(display_posts):
    if post_id == st.session_state.get("deleted_post"):
        continue

    title, description = (full_caption.split("||") + [""])[:2]

    with cols[i % 3]:
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.warning("Image file not found.")

        st.markdown(f"**{title.strip()}**")
        if description.strip():
            st.caption(description.strip())
        st.markdown(f"{'⭐' * rating + '☆' * (5 - rating)}")
        st.markdown(f"*Posted by {email.split('@')[0]} — {created_at[:10]}*")

        # allow deletion of own posts
        if email == user_email:
            if st.button("🗑️ Delete", key=f"delete_{post_id}"):
                delete_post(post_id, img_path)
