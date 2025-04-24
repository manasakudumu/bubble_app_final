import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from datetime import datetime
import pytz
from db.bubbledb import get_journal_entries, add_journal_entry, get_user

# 1. Dining hall & meal mapping
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
        return [item.get('name', 'N/A') for item in items if item.get('date', '').startswith(date)]
    return ["Menu unavailable"]

# 2. Access control
st.set_page_config(page_title="🫧 Food Journal", page_icon="🫧", layout="wide")
if "access_token" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
if user[2] != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

#time zone
eastern = pytz.timezone('US/Eastern')
today = datetime.now(eastern)

# Format nicely for display and API
today_display = today.strftime("%A, %B %d, %Y")  # e.g. "Wednesday, April 23, 2025"
today_api = today.strftime("%Y-%m-%d")  # e.g. "2025-04-23"

st.markdown(f"## 📝 Daily Food Planner — *{today_display}*")
st.markdown("Your cozy, colorful space to log everything from meals to mood 💗")
st.divider()

# Dining hall selection
with st.sidebar:
    st.markdown("🍽️ **Dining Hall**")
    selected_location = st.radio("Choose location:", df['location'].unique())
    formatted_date = datetime.today().strftime('%Y-%m-%d')

# Filter by selected location
location_data = df[df['location'] == selected_location]

# Layout: 3 columns = breakfast | lunch | dinner
col_b, col_l, col_d = st.columns(3)



# Helper to get menu for each meal
def meal_options(meal_name):
    meal_row = location_data[location_data['meal'] == meal_name].iloc[0]
    items = get_menu(today_api, meal_row['locationID'], meal_row['mealID'])
    return items
# Breakfast
with col_b:
    st.markdown("### Breakfast", unsafe_allow_html=True)
    breakfast_items = meal_options("Breakfast")
    breakfast_selection = []
    for i, item in enumerate(breakfast_items):
        if st.checkbox(f" {item}", key=f"bf_{i}_{item}"):
            breakfast_selection.append(item)


# Lunch
with col_l:
    st.markdown("### Lunch", unsafe_allow_html=True)
    lunch_items = meal_options("Lunch")
    lunch_selection = []
    for i, item in enumerate(lunch_items):
        if st.checkbox(f" {item}", key=f"l_{i}_{item}"):
            lunch_selection.append(item)


# Dinner
with col_d:
    st.markdown("### Dinner", unsafe_allow_html=True)
    dinner_items = meal_options("Dinner")
    dinner_selection = []
    for i, item in enumerate(dinner_items):
        if st.checkbox(f" {item}", key=f"d_{i}_{item}"):
            dinner_selection.append(item)



# ========== OTHER SECTIONS ========== #
st.markdown("### 🥤 Water Intake")
water = st.slider("💧 Glasses of water today", 0, 8, 4)

st.markdown("### 😴 Sleep Hours")
sleep = st.slider("How many hours of sleep?", 0, 12, 7)

st.markdown("### 🎭 Mood Today")
mood = st.multiselect("Check all that apply", ["Happiness", "Sadness", "Anger", "Fear", "Disgust", "Surprise"])

st.markdown("### 🧘 Exercise")
exercise = st.text_input("What physical activity did you do today?")

st.markdown("### 📝 Notes")
notes = st.text_area("Add thoughts, cravings, or anything else...")

# ========== SAVE ENTRIES ========== #
if st.button("💾 Save My Day"):
    for meal, food in zip(["Breakfast", "Lunch", "Dinner"], [breakfast, lunch, dinner]):
        add_journal_entry(user_email, formatted_date, location, meal, food,
                          ", ".join(mood), 0,
                          f"Water: {water} glasses | Sleep: {sleep}h | Exercise: {exercise} | Notes: {notes}")
    st.success("Your daily planner entry has been saved! 🌈")

# ========== JOURNAL HISTORY ========== #
st.markdown("## 📖 Your Food Mood Feed")
st.markdown("_A cozy log of your eats, feelings, and thoughts..._")
st.markdown("---")

for _, row in df_past.iterrows():
    with st.container():
        st.markdown(
            f"""
            <div style='
                background-color: #2a2b38;
                border-radius: 12px;
                padding: 1.2rem;
                margin-bottom: 1.2rem;
                border: 1px solid #444;
            '>
                <h3 style='color: #ffb6c1;'>📅 {row['Date']} — {row['Meal']} @ {row['Location']}</h3>
                <p style='font-size: 1rem;'>
                    <strong>🍽️ What you ate:</strong> {row['Food']}<br>
                    <strong>🎭 Mood:</strong> {row['Mood']}<br>
                    <strong>📝 Notes:</strong> {row['Comments'] if row['Comments'] else '_No notes..._' }<br>
                    <small>⏱️ Logged at: {row['Created At'][:16]}</small>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

