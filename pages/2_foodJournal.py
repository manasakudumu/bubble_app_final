import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
from db.bubbledb import get_journal_entries, add_journal_entry, get_user

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
    
st.title("🫧 Bubble: Food Journal")
if "access_token" not in st.session_state:
    st.warning("Please log in before accessing this page.")
    st.stop()

user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

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
comments = st.text_area("Any reviews? (optional)", placeholder="Thoughts, questions, opinions...?")
                
if st.button("Save Entry"):
                    add_journal_entry(user_email,formatted_date,selected_location,selected_meal,selected_food,mood,rating,comments)
                    st.success("Entry saved!")
                
                #journal history
st.markdown("### Your past journal entries")
past = get_journal_entries(user_email)
if past:
                    df_past = pd.DataFrame(past, columns=["Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"])
                    st.dataframe(df_past)
                    # journal mood viz
                    moods = {"😍 Loved it": 5,"😊 Happy": 4,"😐 Neutral": 3,"😕 Meh": 2,"😞 Unhappy": 1}
                    st.markdown("### Mood Trend Over Time")
                    df_past["Date"] = pd.to_datetime(df_past["Date"])
                    df_past = df_past.sort_values("Date")
                    df_past["Mood Score"] = df_past["Mood"].map(moods)

                    # plotly
                    fig = px.line(df_past, x="Date", y="Mood Score", markers=True,
                                title="Your mood trend based on food",
                                labels={"Mood score": "Mood Rating (1-5)"})
                    fig.update_layout(
                        yaxis=dict(tickmode="array",tickvals=[1, 2, 3, 4, 5],
                            ticktext=["😞 Unhappy", "😕 Meh", "😐 Neutral", "😊 Happy", "😍 Loved it"]
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No entries yet.")