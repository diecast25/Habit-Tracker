
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# File to store data
DATA_FILE = "habit_data.csv"

# Load or create data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "User"])

# Get list of users from data
users = df["User"].unique().tolist()

# Page styling
st.set_page_config(page_title="Habit Tracker", page_icon="✅", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🌟 Multi-User Habit Tracker 🌟</h1>", unsafe_allow_html=True)

# Add new user
st.sidebar.header("👤 User Management")
new_user = st.sidebar.text_input("Add a new user:")
if st.sidebar.button("➕ Add User"):
    if new_user and new_user not in users:
        users.append(new_user)
        st.sidebar.success(f"User '{new_user}' added!")

# Select user
selected_user = st.sidebar.selectbox("Select your dashboard:", users)

if selected_user:
    # Filter data for selected user
    user_df = df[df["User"] == selected_user]

    # Get habits for this user
    habits = [col for col in user_df.columns if col not in ["Date", "User"]]

    # Add new habit
    st.sidebar.header("📝 Add Habit")
    new_habit = st.sidebar.text_input("Enter habit name:")
    if st.sidebar.button("➕ Add Habit"):
        if new_habit and new_habit not in habits:
            habits.append(new_habit)
            if new_habit not in df.columns:
                df[new_habit] = 0
            st.sidebar.success(f"Habit '{new_habit}' added for {selected_user}!")
            df.to_csv(DATA_FILE, index=False)

    # Today's date
    today = datetime.date.today().strftime("%Y-%m-%d")

    # Form to update today's habits
    st.subheader(f"✅ Mark Today's Habits for {selected_user}")
    completed = {}
    with st.form("habit_form"):
        for habit in habits:
            completed[habit] = st.checkbox(f"✔ {habit}")
        submitted = st.form_submit_button("Update Habits")

    if submitted:
        new_row = {"Date": today, "User": selected_user}
        for habit in habits:
            new_row[habit] = 1 if completed[habit] else 0
        df = df[(df["Date"] != today) | (df["User"] != selected_user)]
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("🎉 Habits updated successfully!")

    # Show progress graph
    st.markdown("---")
    st.subheader(f"📊 Progress Over Time for {selected_user}")
    if not user_df.empty:
        # Line chart for habits
        fig = px.line(user_df, x="Date", y=habits, markers=True,
                      title=f"Habit Completion Trend - {selected_user}")
        fig.update_layout(legend_title_text="Habits", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Streak Counter
        st.subheader("🔥 Current Streaks")
        streaks = {}
        for habit in habits:
            streak = 0
            for val in reversed(user_df[habit].tolist()):
                if val == 1:
                    streak += 1
                else:
                    break
            streaks[habit] = streak
        st.write(streaks)

        # Percentage Completion Bar Chart
        st.subheader("📈 Completion Percentage")
        percentages = {habit: round(user_df[habit].mean() * 100, 2) for habit in habits}
        percent_df = pd.DataFrame(list(percentages.items()), columns=["Habit", "Completion %"])
        bar_fig = px.bar(percent_df, x="Habit", y="Completion %",
                         color="Completion %", text="Completion %",
                         title="Habit Completion Percentage",
                         color_continuous_scale="greens")
        bar_fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.info("No data yet. Start tracking your habits!")
