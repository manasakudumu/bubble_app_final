import streamlit as st
import pandas as pd
from auth import google_login
from user_profile import render_user_profile
import requests
from datetime import datetime
from db.bubbledb import (
    create_tables, create_journal_table,
    add_user, get_user,
    add_journal_entry, get_journal_entries, delete_user
)

create_tables()
create_journal_table()
# delete_user("mk122@wellesley.edu")


DEBUG = False # keep False when testing Google Login
# DEBUG = True # set to True, when you don't want to go through authentication
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

    if DEBUG and "access_token" not in st.session_state:
        fake_login()

    # If already logged in
    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.write("Please log in with your Google account:")
        logged_in = google_login()
        if logged_in:
            st.rerun()

render_sidebar()
if "access_token" not in st.session_state:
    st.stop()
user_email = st.session_state["user_email"]
user_name = st.session_state["user_name"]
existing_user = get_user(user_email)

if not existing_user:
    st.markdown("###Welcome!")
    st.info("Please select your role to continue.")
    role_selection = st.radio("Are you a student or staff?", ["Student", "Staff"])
    
    if st.button("Save Role"):
        add_user(user_email, user_name, role_selection)
        st.rerun()  #reruns page after role selection
else:
    role = existing_user[2]  
    if role == "Student":
        #Journal view
        st.title("🍽️ Bubble: Food Journal")
        st.write("Session:", st.session_state)
        if "user_email" in st.session_state:
            user_email = st.session_state["user_email"]

            # select date location meal
            selected_date = st.date_input("Select date", value=datetime.today())
            formatted_date = selected_date.strftime('%Y-%m-%d')

            selected_location = st.selectbox("Choose dining location", df['location'].unique())
            meals = df[df['location'] == selected_location]['meal'].unique()
            selected_meal = st.selectbox("Choose meal", meals)

            # get meal options
            selected_row = df[(df['location'] == selected_location) & (df['meal'] == selected_meal)].iloc[0]
            locationID = selected_row['locationID']
            mealID = selected_row['mealID']
            menu_items = get_menu(formatted_date, locationID, mealID)

            food_names = [item['Name'] for item in menu_items]
            selected_food = st.selectbox("What did you eat?", food_names)
            mood = st.selectbox("How did it make you feel?", ["😍 Loved it","😊 Happy", "😐 Neutral", "😕 Meh","😞 Unhappy"])
            rating = st.slider("Rate the food (1 = worst, 5 = best)", 1, 5, 3)
            comments = st.text_area("Any reviews? (optional)", placeholder="Taste, digestion, allergies...")
            
            if st.button("Save Entry"):
                add_journal_entry(user_email,formatted_date,selected_location,selected_meal,selected_food,mood,rating,comments)
                st.success("Entry saved!")
            
            #journal history
            st.markdown("###Your past journal entries")
            past = get_journal_entries(user_email)
            if past:
                df_past = pd.DataFrame(past, columns=["Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"])
                st.dataframe(df_past)
            else:
                st.info("No entries yet.")

    else:
        st.title("Staff Access")
        st.markdown("Staff dashboard is coming soon!")