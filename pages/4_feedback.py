import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
from datetime import datetime
import pytz
from db.bubbledb import get_journal_entries, add_journal_entry, get_user, submit_feedback

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
df = pd.DataFrame(data)
base_url = 'https://dish.avifoodsystems.com/api/menu-items/week'

def get_menu(date, locationId, mealId):
    params = {'date': date, 'locationId': locationId, 'mealId': mealId}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        items = response.json()
        filtered_items = []
        for item in items:
            if item.get('date', '').startswith(date):
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
    return []

st.title("Anonymous Feedback to Dining Hall Staff")
st.markdown("Your feedback will be anonymous and sent directly to staff.")

#auth check
if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
if user[2] != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

#inputs
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

if (selected_location != st.session_state.prev_location or selected_meal != st.session_state.prev_meal):
                st.session_state.selected_foods = set()
                for food in food_names:
                    key = f"toggle_{food}"
                    if key in st.session_state:
                        del st.session_state[key]

st.session_state.prev_location = selected_location
st.session_state.prev_meal = selected_meal

# Checkbox interface
st.markdown("###  What food would you like to leave feedback on?")
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

feedback_msg = st.text_area("What would you like to tell Dining hall workers?", placeholder="Share your thoughts...")
if st.button("Send Feedback"):
    if feedback_msg.strip():
        full_feedback = (
            f"Date: {formatted_date}\n"
            f"Location: {selected_location}\n"
            f"Meal: {selected_meal}\n"
            f"Food: {', '.join(st.session_state.selected_foods) or 'None'}\n"
            f"Feedback: {feedback_msg.strip()}"
        )
        submit_feedback(full_feedback, str(datetime.now()))
        st.success(" Your feedback was sent successfully and anonymously!")
    else:
        st.warning(" Please enter a message before submitting.")
