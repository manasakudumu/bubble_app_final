import streamlit as st
import uuid, os
from datetime import datetime
from db.bubbledb import add_community_post, get_all_community_posts, get_user

st.title("📸 Community Feed")
if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()
    
user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

with st.form("post_form"):
                img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
                caption = st.text_area("Enter a caption")
                rating = st.slider("Rate this food", 1, 5, 3)
                if st.form_submit_button("Post"):
                    if img:
                        os.makedirs("posts", exist_ok=True)
                        post_id = str(uuid.uuid4())
                        file_path = f"posts/{post_id}.jpg"
                        with open(file_path, "wb") as f:
                            f.write(img.read())
                        add_community_post(post_id, user_email, file_path, caption, rating, str(datetime.now()))
                
                st.markdown("### Explore all the posts")
                posts = get_all_community_posts()
                cols = st.columns(3)
                for i, (post_id, email, img_path, caption, rating, created_at) in enumerate(posts):
                    with cols[i % 3]:
                            st.image(img_path, use_container_width=True)
                            st.caption(caption)
                            st.markdown(f"{'⭐' * rating + '☆' * (5 - rating)}")
                            st.markdown(f"*Posted by {email.split('@')[0]} — {created_at[:10]}*")
                