
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# File to store data
DATA_FILE = "habit_data.csv"

# Load or create data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date"])

# Habits list (dynamic)
habits = [col for col in df.columns if col != "Date"]

st.title("📊 Habit Tracker Dashboard")

# Add new habit
st.subheader("Add a New Habit")
new_habit = st.text_input("Enter habit name:")
if st.button("Add Habit"):
    if new_habit and new_habit not in habits:
        habits.append(new_habit)
        if new_habit not in df.columns:
            df[new_habit] = 0
        st.success(f"Habit '{new_habit}' added!")
        df.to_csv(DATA_FILE, index=False)

# Today's date
today = datetime.date.today().strftime("%Y-%m-%d")

# Form to update today's habits
st.subheader("Mark Today's Habits")
completed = {}
with st.form("habit_form"):
    for habit in habits:
        completed[habit] = st.checkbox(habit)
    submitted = st.form_submit_button("Update")

if submitted:
    new_row = {"Date": today}
    for habit in habits:
        new_row[habit] = 1 if completed[habit] else 0
    df = df[df["Date"] != today]  # Remove old entry for today if exists
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Habits updated!")

# Show progress graph
st.subheader("Progress Over Time")
if not df.empty:
    fig, ax = plt.subplots()
    for habit in habits:
        ax.plot(df["Date"], df[habit], marker='o', label=habit)
    ax.set_title("Habit Completion")
    ax.set_xlabel("Date")
    ax.set_ylabel("Completed (1=Yes, 0=No)")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Streak Counter
    st.subheader("🔥 Current Streaks")
    streaks = {}
    for habit in habits:
        streak = 0
        for val in reversed(df[habit].tolist()):
            if val == 1:
                streak += 1
            else:
                break
        streaks[habit] = streak
    st.write(streaks)

    # Percentage Completion
    st.subheader("📈 Completion Percentage")
    percentages = {habit: round(df[habit].mean() * 100, 2) for habit in habits}
    st.write(percentages)
else:
    st.info("No data yet. Start tracking your habits!")
