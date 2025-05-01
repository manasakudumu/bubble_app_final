import streamlit as st
import pandas as pd
import plotly.express as px
from db.bubbledb import get_journal_entries, get_user
from nav import render_sidebar

st.set_page_config(page_title="Insights", layout="wide")

st.markdown("""
    <style>
        ul[data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Visualize your food data")

if "access_token" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_email = st.session_state.get("user_email")
user = get_user(user_email)
role = user[2]

if "role" in st.session_state:
    render_sidebar(st.session_state["role"])

if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()

past = get_journal_entries(user_email)
if not past:
    st.info("No journal entries to visualize yet.")
    st.stop()

df = pd.DataFrame(past, columns=["Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"])
df["Date"] = pd.to_datetime(df["Date"])

# Normalize moods for analysis
df["Mood"] = df["Mood"].str.strip().str.title()
mood_map = {"Unhappy": 1, "Meh": 2, "Neutral": 3, "Happy": 4, "Loved It": 5}
df["Mood Score"] = df["Mood"].map(mood_map)

# Tabs for visualizations (Mood Over Time and Heatmap removed)
tab1, tab2, tab3, tab4 = st.tabs([
    "Dining Hall Frequency",
    "Mood Stacked Bar",
    "Average Ratings",
    "Most Logged Foods"
])

with tab1:
    st.subheader("Dining Hall Frequency")
    hall_counts = df["Location"].value_counts().reset_index()
    hall_counts.columns = ["Dining Hall", "Entries"]
    fig = px.bar(hall_counts, x="Dining Hall", y="Entries", color="Dining Hall", text="Entries")
    fig.update_layout(title="Entries per Dining Hall", xaxis_title="Dining Hall", yaxis_title="Entries")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Mood Distribution by Location")
    mood_counts = df.groupby(["Location", "Mood"]).size().reset_index(name="Count")
    fig = px.bar(mood_counts, x="Location", y="Count", color="Mood", barmode="stack")
    fig.update_layout(title="Stacked Mood Distribution", xaxis_title="Location", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Average Food Ratings by Meal")
    rating_data = df.groupby(["Meal"])["Rating"].mean().reset_index()
    fig = px.bar(rating_data, x="Meal", y="Rating", color="Meal", text="Rating")
    fig.update_layout(title="Average Rating per Meal", yaxis=dict(range=[0, 5]))
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Most Frequently Logged Foods")
    from collections import Counter
    all_foods = ", ".join(df["Food"].dropna()).split(", ")
    food_counts = Counter([food.strip() for food in all_foods if food.strip()])
    food_df = pd.DataFrame(food_counts.items(), columns=["Food", "Count"]).sort_values(by="Count", ascending=False).head(20)
    fig = px.bar(food_df, x="Food", y="Count", color="Food", text="Count")
    fig.update_layout(title="Top 20 Most Logged Foods", xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
