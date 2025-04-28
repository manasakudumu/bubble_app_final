import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
from datetime import datetime
from db.bubbledb import get_journal_entries, add_journal_entry, get_user

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

st.title("Bubble: Food Journal")

if "access_token" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
if user[2] != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

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
        comments)
    st.success("Entry saved!")
    st.session_state.selected_foods = set()

# Past entries and mood trend
st.markdown("### Your past journal entries")
past = get_journal_entries(user_email)
if past:
    df_past = pd.DataFrame(past, columns=["Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"])
    df_past["Date"] = pd.to_datetime(df_past["Date"])

    # filters
    st.markdown("### Filter your journal history")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_filter_location = st.selectbox("Dining Hall", ["All"] + sorted(df_past["Location"].unique()))
    with col2:
        selected_filter_meal = st.selectbox("Meal", ["All"] + sorted(df_past["Meal"].unique()))
    with col3:
        date_range = st.date_input("Date Range", [df_past["Date"].min(), df_past["Date"].max()])
    with col4:
        selected_filter_mood = st.selectbox("Mood", ["All"] + sorted(df_past["Mood"].unique()))

    filtered_df = df_past.copy()

    if selected_filter_location != "All":
        filtered_df = filtered_df[filtered_df["Location"] == selected_filter_location]
    if selected_filter_meal != "All":
        filtered_df = filtered_df[filtered_df["Meal"] == selected_filter_meal]
    if selected_filter_mood != "All":
        filtered_df = filtered_df[filtered_df["Mood"] == selected_filter_mood]
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Date"] <= pd.to_datetime(end_date))
        ]

    # show filtered results
    if filtered_df.empty:
        st.info("No journal entries match your filters.")
    else:
        for _, row in filtered_df.iterrows():
            st.markdown(
                f"""
                <div class="journal-card">
                    <h3>{row['Date'].strftime('%Y-%m-%d')} — {row['Meal']} @ {row['Location']}</h3>
                    <p><strong>What you ate:</strong> {row['Food']}</p>
                    <p><strong>Mood:</strong> {row['Mood']}</p>
                    <p><strong>Rating:</strong> {row['Rating']}</p>
                    <p><strong>Notes:</strong> {row['Comments'] if row['Comments'] else '_No notes..._'}</p>
                    <small>⏱️ Logged at: {row['Created At']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

else:
    st.info("No entries yet.")