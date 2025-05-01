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

# Optional styling
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Visualize your food Data!")

# auth check
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

# chart 1
st.markdown("### Dining Hall Frequency")

hall_counts = df["Location"].value_counts().reset_index()
hall_counts.columns = ["Dining Hall", "Entries"]

fig = px.bar(
    hall_counts,
    x="Dining Hall",
    y="Entries",
    color="Dining Hall",
    text="Entries",
    title="Which dining halls have you logged the most?",
)
fig.update_layout(xaxis_title="Dining Hall",yaxis_title="Number of Entries",title_x=0.2)
fig.update_traces(marker_line_color='black', marker_line_width=1.5)
st.plotly_chart(fig, use_container_width=True)


# chart 2
st.markdown("### Mood Trend Over Time")
mood_map = {"😞 Unhappy": 1,"😕 Meh": 2,"😐 Neutral": 3,"😊 Happy": 4,"😍 Loved it": 5}
emoji_labels = {1: "😞", 2: "😕", 3: "😐", 4: "😊", 5: "😍"}

df["Date"] = pd.to_datetime(df["Date"])
df["Mood Score"] = df["Mood"].map(mood_map)
df = df.sort_values("Date")

fig = px.line(
    df,
    x="Date",
    y="Mood Score",
    markers=True,
    title="How your meals made you feel",
)

fig.update_layout(
    yaxis=dict(tickmode="array",tickvals=list(emoji_labels.keys()),ticktext=list(emoji_labels.values()),title="Mood"),
    xaxis_title="Date",
    title_x=0.2
)
fig.update_traces(line=dict(color="#0080FF", width=3))
st.plotly_chart(fig, use_container_width=True)