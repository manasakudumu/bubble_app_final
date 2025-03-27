# Code refactored by ChatGPT
# Original code by Eni Mustafaraj & ChatGPT
# March 26, 2025

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Data loading and processing
# -------------------------------
@st.cache_data
def load_data():
    """
    Load and preprocess the availability data from CSV.
    Renames columns, extracts weekday names, and converts time availability
    into structured lists per student and day.

    Returns:
        pd.DataFrame: A structured DataFrame with student initials and availability per day as lists.
    """
    df = pd.read_csv("cs248-availability.csv")
    df.rename(columns={df.columns[0]: "Initials"}, inplace=True)

    days = [col.split("[")[1].replace("]", "") for col in df.columns[1:]]
    df.columns = ["Initials"] + days
    
    students = sorted(df['Initials'].unique())

    time_slots = ["Morning (9-12)", "Early afternoon (12-4)", "Afternoon (4-7)", "After 7pm"]
    structured_data = []
    for _, row in df.iterrows():
        student = students[_]
        availability = {"Initials": student}
        for day in days:
            times = str(row.get(day, ""))
            if times.lower() == "nan" or times.strip() == "":
                availability[day] = []
            else:
                availability[day] = [slot for slot in time_slots if slot.split(" (")[0] in times]
        structured_data.append(availability)
    
    return pd.DataFrame(structured_data)


def get_availability_matrix(df, selected_students, days, time_slots):
    """
    Create a matrix counting how many selected students are available in each time slot per day.

    Args:
        df (pd.DataFrame): The structured availability DataFrame.
        selected_students (list): List of selected student initials.
        days (list): List of weekday column names.
        time_slots (list): List of predefined time slots.

    Returns:
        pd.DataFrame: A matrix with days as rows, time slots as columns, and availability counts as values.
    """
    selected_df = df[df['Initials'].isin(selected_students)]
    matrix = pd.DataFrame(0, index=days, columns=time_slots)
    days = [day.capitalize() for day in days]

    for _, row in selected_df.iterrows():
        for day in days:
            times = row.get(day, [])
            if isinstance(times, list):
                for time in times:
                    if time in matrix.columns:
                        matrix.loc[day, time] += 1
    return matrix

def plot_heatmap(matrix, days):
    """
    Generate a heatmap plot of the availability matrix using Seaborn.

    Args:
        matrix (pd.DataFrame): The availability matrix to visualize.
        days (list): List of weekdays to label the x-axis.

    Returns:
        matplotlib.figure.Figure: The matplotlib figure object containing the heatmap.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        matrix.T.loc[::-1],
        cmap="coolwarm",
        annot=True,
        fmt="d",
        linewidths=0.5,
        ax=ax,
        xticklabels=days
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Time Slots")
    ax.set_xticklabels(days, rotation=45)
    return fig

def find_common_times(matrix, selected_count, days):
    """
    Identify time slots where all selected students are available.

    Args:
        matrix (pd.DataFrame): The availability matrix with counts.
        selected_count (int): Number of selected students.
        days (list): List of weekdays to preserve order.

    Returns:
        pd.DataFrame: A filtered matrix showing only the fully overlapping time slots,
                      or an empty DataFrame if none exist.
    """
    common = matrix[matrix == selected_count].dropna(how='all')
    return common.reindex(days) if not common.empty else pd.DataFrame()


# -------------------------------
# Streamlit UI
# -------------------------------
df = load_data()
days = list(df.columns[1:])
students = df['Initials'].unique()
time_slots = ["Morning (9-12)", "Early afternoon (12-4)", "Afternoon (4-7)", "After 7pm"]

st.title("Student Availability Overlap")
selected_students = st.multiselect("Select up to 3 students:", 
                                   students, 
                                   max_selections=3)

if selected_students:
    availability_matrix = get_availability_matrix(df, selected_students, days, time_slots)
    
    st.pyplot(plot_heatmap(availability_matrix, days))
    
    st.write("### Overlap Summary")
    common_times = find_common_times(availability_matrix, len(selected_students), days)
    if not common_times.empty:
        st.write(common_times)
        st.download_button(
            label = "Download Overlap as CSV",
            data=common_times.to_csv(index=True),
            file_name='overlap_summary.csv',
            mime='text/csv',
        )
    else:
        st.write("No common available times.")

