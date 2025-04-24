import streamlit as st
import pandas as pd

import requests
import time
import csv
import json
import os
from datetime import datetime

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

# banner
st.image("images/banner.jpg", use_container_width=True)

# streamlit app
st.title("Wellesley Dining Menu Viewer")

#date input
selected_date = st.date_input("Select a date", value=datetime.today())
formatted_date = selected_date.strftime('%Y-%m-%d')

# location selection
locations = df['location'].unique()
selected_location = st.selectbox("Select a location", locations)

# meal selection
meals = df[df['location'] == selected_location]['meal'].unique()
selected_meal = st.selectbox("Select a meal", meals)

# get and display menu
if st.button("Get Menu"):
    # get locationID and mealID for the selected options
    selected_row = df[(df['location'] == selected_location) & (df['meal'] == selected_meal)].iloc[0]
    locationID = selected_row['locationID']
    mealID = selected_row['mealID']

    # fetch menu
    menu = get_menu(formatted_date, locationID, mealID)

    # displaying menu
    if "error" in menu:
        st.error(menu["error"])
    else:
        st.success(f"Menu for {selected_location} - {selected_meal} on {formatted_date}:")
        menu_df = pd.DataFrame(menu)
        st.dataframe(menu_df)