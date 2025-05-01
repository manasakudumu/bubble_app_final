import streamlit as st
import pandas as pd
import plotly.express as px
from db.bubbledb import get_journal_entries, get_user
from nav import render_sidebar

from auth_guard import require_login
require_login()


st.set_page_config(page_title="Food Journal Insights", layout="wide")

# Hide default Streamlit sidebar navigation
st.markdown("""
    <style>
        ul[data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)


with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if "access_token" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_email = st.session_state["user_email"]
user = get_user(user_email)
role = user[2]
if role != "Student":
    st.error("Access denied: This page is only for students.")
    st.stop()


render_sidebar(role)


past = get_journal_entries(user_email)
if not past:
    st.info("No journal entries to visualize yet.")
    st.stop()

df = pd.DataFrame(past, columns=[
    "Date", "Location", "Meal", "Food", "Mood", "Rating", "Comments", "Created At"
])
df["Date"] = pd.to_datetime(df["Date"])


df["Mood Category"] = df["Mood"].apply(lambda x: x.split(" ", 1)[1] if isinstance(x, str) and " " in x else x)

mood_map = {
    "Unhappy": 1,
    "Meh": 2,
    "Neutral": 3,
    "Happy": 4,
    "Loved it": 5
}
df["Mood Score"] = df["Mood Category"].map(mood_map)


tab1, tab2, tab3 = st.tabs([
    "Dining Hall Frequency",
    "Mood Trend Over Time",
    "Heatmap of Mood Scores"
])

# Tab 1: Dining Hall Frequency
with tab1:
    st.header("Dining Hall Frequency")
    hall_counts = df["Location"].value_counts().reset_index()
    hall_counts.columns = ["Dining Hall", "Entries"]

    fig1 = px.bar(
        hall_counts,
        x="Dining Hall",
        y="Entries",
        color="Dining Hall",
        text="Entries",
        title="Which dining halls have the most logged entries?"
    )
    fig1.update_layout(
        xaxis_title="Dining Hall",
        yaxis_title="Number of Entries",
        title_x=0.2
    )
    fig1.update_traces(marker_line_color="black", marker_line_width=1.5)
    st.plotly_chart(fig1, use_container_width=True)

# Tab 2: Mood Trend Over Time
with tab2:
    st.header("Mood Trend Over Time")
    df_sorted = df.sort_values("Date")

    fig2 = px.line(
        df_sorted,
        x="Date",
        y="Mood Score",
        markers=True,
        title="Mood scores over time"
    )
    fig2.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=list(mood_map.values()),
            ticktext=list(mood_map.keys()),
            title="Mood"
        ),
        xaxis_title="Date",
        title_x=0.2
    )
    fig2.update_traces(line=dict(color="#0066CC", width=3))
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3: Heatmap of Mood Scores
with tab3:
    st.header("Average Mood by Dining Hall and Meal")

    pivot = (
        df
        .groupby(["Location", "Meal"])["Mood Score"]
        .mean()
        .reset_index()
        .pivot(index="Location", columns="Meal", values="Mood Score")
    )

    fig3 = px.imshow(
        pivot,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        labels={"x": "Meal", "y": "Dining Hall", "color": "Avg Mood Score"},
        title="Average Mood Score by Dining Hall and Meal"
    )
    fig3.update_layout(title_x=0.2)
    st.plotly_chart(fig3, use_container_width=True)
