import streamlit as st
import uuid, os
from datetime import datetime
from db.bubbledb import add_community_post, get_all_community_posts, get_user, delete_community_post
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
    
st.title("📸 Community Feed")
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

 # resest to defaults
if "post_title" not in st.session_state:
    st.session_state.post_title = ""
if "post_description" not in st.session_state:
        st.session_state.post_description = ""
if "post_star_rating" not in st.session_state:
        st.session_state.post_star_rating = 3
if "deleted_post" not in st.session_state:
        st.session_state.deleted_post = None
 
# star ratings
st.markdown("### Rate this food")
rating_cols = st.columns(5)
for i in range(1, 6):
    star = "⭐" if i <= st.session_state.post_star_rating else "☆"
    if rating_cols[i - 1].button(star, key=f"post_star_{i}"):
        st.session_state.post_star_rating = i
st.markdown(f"You rated this: **{st.session_state.post_star_rating} / 5**")
 
# post forms
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
            str(datetime.now()))
        st.success("Post uploaded!")

                    # resetting fields
        st.session_state.post_title = ""
        st.session_state.post_description = ""
        st.session_state.post_star_rating = 3
        st.rerun()
    else:
        st.warning("Please include at least an image and a title.")

# delete posts
def delete_post(post_id, img_path):
    try:
        if os.path.exists(img_path):
            os.remove(img_path)
    except Exception as e:
        st.error(f"Error deleting image file: {e}")

    try:
        delete_community_post(post_id)
    except Exception as e:
        st.error(f"Error deleting post from database: {e}")
    st.session_state.deleted_post = post_id
    st.rerun()

# displaying posts
st.markdown("### Explore all the posts")
posts = get_all_community_posts()
cols = st.columns(3)

for i, (post_id, email, img_path, full_caption, rating, created_at) in enumerate(posts):
    if post_id == st.session_state.get("deleted_post"):
        continue
    title, description = (full_caption.split("||") + [""])[0:2]
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

        if email == user_email:
            if st.button("🗑️ Delete", key=f"delete_{post_id}"):
                delete_post(post_id, img_path) 