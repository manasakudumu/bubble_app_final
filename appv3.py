#app version 3 - with pages

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid
import requests
import plotly.express as px
st.set_page_config(page_title="Bubble", page_icon="🫧", layout="wide")
from auth import google_login
from user_profile import render_user_profile
from db.bubbledb import (
    create_tables, create_journal_table,
    add_user, get_user, delete_user, 
    add_journal_entry, get_journal_entries, 
    create_posts_table, add_community_post, get_all_community_posts, drop_community_posts_table, 
    create_feedback_table, submit_feedback, get_all_feedback
)

create_tables()
create_journal_table()
create_posts_table()
create_feedback_table()
# delete_user("mk122@wellesley.edu")

# DEBUG = False # keep False when testing Google Login
DEBUG = True # set to True, when you don't want to go through authentication


def fake_login():
    """A simple function to handle the fake login process.
    """
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username:
            st.session_state['user'] = username
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Please enter a valid username.")

# code from milestone 1       
# data for locations and meals
data = [
    {'location': 'Bae', 'meal': 'Breakfast', 'locationID': 96, 'mealID': 148},
    {'location': 'Bae', 'meal': 'Lunch', 'locationID': 96, 'mealID': 149},
    {'location': 'Bae', 'meal': 'Dinner', 'locationID': 96, 'mealID': 312},
    {'location': 'Bates', 'meal': 'Breakfast', 'locationID': 95, 'mealID': 145},
    {'location': 'Bates', 'meal': 'Lunch', 'locationID': 95, 'mealID': 146},
    {'location': 'Bates', 'meal': 'Dinner', 'locationID': 95, 'mealID': 311},
    {'location': 'Stone', 'meal': 'Breakfast', 'locationID': 131, 'mealID': 261},
    {'location': 'Stone', 'meal': 'Lunch', 'locationID': 131, 'mealID': 262},
    {'location': 'Stone', 'meal': 'Dinner', 'locationID': 131, 'mealID': 263},
    {'location': 'Tower', 'meal': 'Breakfast', 'locationID': 97, 'mealID': 153},
    {'location': 'Tower', 'meal': 'Lunch', 'locationID': 97, 'mealID': 154},
    {'location': 'Tower', 'meal': 'Dinner', 'locationID': 97, 'mealID': 310},
]

# converting data to DataFrame
df = pd.DataFrame(data)

# base URL for API, defining locally?
base_url = 'https://dish.avifoodsystems.com/api/menu-items/week'

# function to get menu from API
def get_menu(date, locationId, mealId):
    params = {
        'date': date,
        'locationId': locationId,
        'mealId': mealId
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        menu_items = response.json()
        filtered_items = []
        for item in menu_items:
            item_date = item.get('date', '').split('T')[0] 
            if item_date == date:
                food = {
                    'Name': item.get('name', 'N/A'),
                    'Description': item.get('description', 'N/A'),
                    'Station': item.get('stationName', 'N/A'),
                    'Category': item.get('categoryName', 'N/A'),
                    'Calories': item.get('nutritionals', {}).get('calories', 'N/A'),
                    'Allergens': ", ".join([a['name'] for a in item.get('allergens', [])]),
                    'Preferences': ", ".join([p['name'] for p in item.get('preferences', [])])
                }
                filtered_items.append(food)

        return filtered_items
    else:
        return {"error": "Failed to fetch menu"}


#----
def render_sidebar():
    """A function to handle the login in the sidebar."""
    st.sidebar.header("Login")

# Google OAuth login
if "access_token" not in st.session_state:
    st.sidebar.write("Please log in with your Google account:")
    if google_login():
        st.rerun()
    st.stop()

render_user_profile()

st.markdown(
    """
    <div style='text-align: center; padding-top: 1rem;'>
        <h1 style='font-size: 3rem;'>🫧 Welcome to Bubble! 🫧</h1>
        <p style='font-size: 1.2rem; color: #ffb6c1;'>
            Your cozy space to journal your meals, reflect your mood, and share food love 💌
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# role selection
user_email = st.session_state["user_email"]
user_name = st.session_state["user_name"]
existing_user = get_user(user_email)

if not existing_user:
    st.markdown("### Welcome!")
    st.info("Please select your role to continue.")
    role_selection = st.radio("Are you a student or staff?", ["Student", "Staff"])
    if st.button("Save Role"):
        add_user(user_email, user_name, role_selection)
        st.rerun()  #reruns page after role selection
else:
    role = existing_user[2] 

     
    if role == "Student":

        #Journal
        tabs = st.tabs(["Food Journal", "Community", "Resources", "Feedback form", "Profile"])

        with tabs[0]:
            st.title("🫧 Bubble: Food Journal")

            user_email = st.session_state.get("user_email")

            # Select date, dining location, and meal
            selected_date = st.date_input("Select date", value=datetime.today())
            formatted_date = selected_date.strftime('%Y-%m-%d')

            selected_location = st.radio("Choose dining location", df['location'].unique(), horizontal=True)
            meals = df[df['location'] == selected_location]['meal'].unique()
            selected_meal = st.radio("Choose meal", meals, horizontal=True)

            selected_row = df[(df['location'] == selected_location) & (df['meal'] == selected_meal)].iloc[0]
            locationID = selected_row['locationID']
            mealID = selected_row['mealID']
            menu_items = get_menu(formatted_date, locationID, mealID)

            food_names = sorted(set(item['Name'] for item in menu_items))

            # Reset state if switching meals or locations
            if "prev_location" not in st.session_state:
                st.session_state.prev_location = selected_location
            if "prev_meal" not in st.session_state:
                st.session_state.prev_meal = selected_meal

            if (
                selected_location != st.session_state.prev_location or
                selected_meal != st.session_state.prev_meal
            ):
                st.session_state.selected_foods = set()
                for food in food_names:
                    key = f"toggle_{food}"
                    if key in st.session_state:
                        del st.session_state[key]

            st.session_state.prev_location = selected_location
            st.session_state.prev_meal = selected_meal

            # Checkbox interface
            st.markdown("### What did you eat? (click to select, click again to unselect)")
            if "selected_foods" not in st.session_state:
                st.session_state.selected_foods = set()

            cols = st.columns(3)
            for i, food in enumerate(food_names):
                key = f"toggle_{food}"
                if key not in st.session_state:
                    st.session_state[key] = False

                with cols[i % 3]:
                    toggled = st.checkbox(food, key=key)
                    if toggled:
                        st.session_state.selected_foods.add(food)
                    else:
                        st.session_state.selected_foods.discard(food)

            st.markdown(f"**Selected foods:** {', '.join(st.session_state.selected_foods) or 'None'}")

            # Mood selection
            mood = st.selectbox("How did it make you feel?", ["😍 Loved it","😊 Happy", "😐 Neutral", "😕 Meh","😞 Unhappy"])

            # Star Rating
            st.markdown("### Rate the food (double click to rate)")
            if "star_rating" not in st.session_state:
                st.session_state.star_rating = 3
            cols = st.columns(5)
            for i in range(1, 6):
                star = "⭐" if i <= st.session_state.star_rating else "☆"
                if cols[i - 1].button(star, key=f"star_{i}"):
                    st.session_state.star_rating = i

            st.markdown(f"You rated this: **{st.session_state.star_rating} / 5**")

            comments = st.text_area("Any reviews? (optional)", placeholder="Thoughts, questions, opinions...?")

            if st.button("Save Entry"):
                selected_foods_str = ", ".join(st.session_state.selected_foods)
                add_journal_entry(
                    user_email,
                    formatted_date,
                    selected_location,
                    selected_meal,
                    selected_foods_str,
                    mood,
                    st.session_state.star_rating,
                    comments
                )
                st.success("Entry saved!")
                st.session_state.selected_foods = set()

            # Past entries and mood trend
            st.markdown("### Your past journal entries")
            past = get_journal_entries(user_email)
            if past:
                df_past = pd.DataFrame(past, columns=["Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"])
                st.dataframe(df_past)

                moods = {"😍 Loved it": 5,"😊 Happy": 4,"😐 Neutral": 3,"😕 Meh": 2,"😞 Unhappy": 1}
                st.markdown("### Mood Trend Over Time")
                df_past["Date"] = pd.to_datetime(df_past["Date"])
                df_past = df_past.sort_values("Date")
                df_past["Mood Score"] = df_past["Mood"].map(moods)

                fig = px.line(df_past, x="Date", y="Mood Score", markers=True,
                            title="Your mood trend based on food",
                            labels={"Mood score": "Mood Rating (1-5)"})
                fig.update_layout(
                    yaxis=dict(tickmode="array",tickvals=[1, 2, 3, 4, 5],
                        ticktext=["😞 Unhappy", "😕 Meh", "😐 Neutral", "😊 Happy", "😍 Loved it"])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No entries yet.")

    

        #Community
        with tabs[1]:
            st.title("Community Feed")
            user_email = st.session_state.get("user_email")

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
                        str(datetime.now())
                    )
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
                
        #Resources
        with tabs[2]:
            st.subheader("Resources & Links")
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


        
        #Feedback
        # to be added:
        # date, meal type, dining hall, specific meal eaten
        with tabs[3]:
            st.title("Anonymous feedback to dining hall staff")
            st.markdown("Your feedback will be anonymous.")

            # select date
            feedback_date = st.date_input("Select the date of your meal", value=datetime.today())
            formatted_feedback_date = feedback_date.strftime('%Y-%m-%d')

            # select dining hall and meal type
            # selected_location = st.selectbox("Choose dining location", df['location'].unique())
            # meals = df[df['location'] == selected_location]['meal'].unique()
            # selected_meal = st.selectbox("Choose meal", meals)

            feedback_location = st.selectbox("Dining Hall", df['location'].unique())
            feedback_meals = df[df['location'] == feedback_location]['meal'].unique()
            feedback_meal = st.selectbox("Meal type", feedback_meals)

            # get meal options
            selected_row = df[(df['location'] == selected_location) & (df['meal'] == selected_meal)].iloc[0]
            locationID = selected_row['locationID']
            mealID = selected_row['mealID']
            menu_items = get_menu(formatted_date, locationID, mealID)
            selected_feedback_food = st.selectbox("Specific meal you had", food_names)


            feedback_msg = st.text_area("Enter feedback", height=150)
            if st.button("Send Feedback"):
                if feedback_msg.strip():
                    # formatting feedback
                    full_feedback = (
                        f"Date: {formatted_feedback_date}\n"
                        f"Location: {feedback_location}\n"
                        f"Meal: {feedback_meal}\n"
                        f"Food: {selected_feedback_food}\n"
                        f"Feedback: {feedback_msg.strip()}"
                    )
                    submit_feedback(full_feedback, str(datetime.now()))
                    st.success("Your feedback was sent successfully (and anonymously)!")
                else:
                    st.warning("Please enter a message before submitting.")

        #profile
        # with tabs[4]:


    else:
        st.title("Dining hall staff access")
        st.markdown("### Anonymous feedback inbox from students")

        feedback_list = get_all_feedback()
        if not feedback_list:
            st.info("No feedback received yet.")
        else:
            for msg, submitted in feedback_list:
                st.markdown(" " + msg)
                st.caption(f"Submitted on {submitted[:16]}")
                st.markdown("---")
       
