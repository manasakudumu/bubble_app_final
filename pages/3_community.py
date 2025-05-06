# pages/3_community.py
import cloudinary
import cloudinary.uploader
import cloudinary.api

from auth_guard import require_login  
require_login()                # ← Must be first Streamlit‐related call

import streamlit as st
import uuid, os
from datetime import datetime, date      # ← added `date` here
from db.bubbledb import (
    add_community_post,
    get_all_community_posts,
    get_user,
    delete_community_post,
)
from nav import render_sidebar

cloudinary.config(
    cloud_name=st.secrets["cloudinary"]["cloud_name"],
    api_key=st.secrets["cloudinary"]["api_key"],
    api_secret=st.secrets["cloudinary"]["api_secret"]
)

# --- Hide the default sidebar nav header ---
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

# --- authentication ---
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

# --- new post form ---
if "post_star_rating" not in st.session_state:
    st.session_state.post_star_rating = 3
if "post_title" not in st.session_state:
    st.session_state.post_title = ""
if "post_description" not in st.session_state:
    st.session_state.post_description = ""

st.markdown("### Rate this post")
rating_cols = st.columns(5)
for i in range(1, 6):
    star = "⭐" if i <= st.session_state.post_star_rating else "☆"
    if rating_cols[i - 1].button(star, key=f"post_star_{i}"):
        st.session_state.post_star_rating = i
st.markdown(f"You rated this: **{st.session_state.post_star_rating} / 5**")

with st.form("post_form"):
    img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    title = st.text_input("Post Title", value=st.session_state.post_title)
    description = st.text_area("Post Description", value=st.session_state.post_description)
    submitted = st.form_submit_button("Post")

if submitted:
    if img and title:
        post_id = str(uuid.uuid4())

        try:
            result = cloudinary.uploader.upload(img, public_id=f"bubble_app/{post_id}")
            file_url = result["secure_url"]

            add_community_post(
                post_id,
                user_email,
                file_url,
                f"{title}||{description}",
                st.session_state.post_star_rating,
                str(datetime.now()),
            )
            st.success("Post uploaded!")

            st.session_state.post_title = ""
            st.session_state.post_description = ""
            st.session_state.post_star_rating = 3
            st.rerun()

        except Exception as e:
            st.error(f"Image upload failed: {e}")
    else:
        st.warning("Please include at least an image and a title.")


# --- delete helper ---
def delete_post(post_id, img_path):
    try:
        delete_community_post(post_id)
    except Exception as e:
        st.error(f"Error deleting post from database: {e}")

    st.session_state.deleted_post = post_id
    st.rerun()

# --- FILTERS ---
st.markdown("### 📂 Filter Posts")

posts = get_all_community_posts()

# Username substring filter
filter_username = st.text_input(
    "Filter by username contains…",
    value="",
    help="Type any substring of the poster’s username",
)

# Date calendar filter
use_date_filter = st.checkbox("Filter by date", value=False)
if use_date_filter:
    filter_date = st.date_input("Select date", value=date.today())
else:
    filter_date = None

# Apply filters
filtered = []
for post_id, email, img_path, full_caption, rating, created_at in posts:
    username = email.split("@")[0]
    date_only = created_at.split(" ")[0]  # "YYYY-MM-DD"

    if filter_username and filter_username.lower() not in username.lower():
        continue

    if filter_date:
        if date_only != filter_date.strftime("%Y-%m-%d"):
            continue

    filtered.append((post_id, email, img_path, full_caption, rating, created_at))

# Decide list to display
if (filter_username or filter_date) and not filtered:
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
        if img_path.startswith("http"):
            st.image(img_path, use_container_width=True)
        else:
            st.warning("Image URL is invalid or not found.")


        st.markdown(f"**{title.strip()}**")
        if description.strip():
            st.caption(description.strip())
        st.markdown(f"{'⭐' * rating + '☆' * (5 - rating)}")
        st.markdown(f"*Posted by {email.split('@')[0]} — {created_at[:10]}*")

        # allow deletion of own posts
        if email == user_email:
            if st.button("🗑️ Delete", key=f"delete_{post_id}"):
                delete_post(post_id, img_path)
