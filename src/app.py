import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd

st.title("Life Tracking 2025")

# Connect to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# List of worksheet names (customize as needed)
worksheets = ["Tracking", "Workout A", "Workout B", "Workout C"]

# Create tabs in the UI
tabs = st.tabs(worksheets)

for i, worksheet_name in enumerate(worksheets):
    with tabs[i]:
        if worksheet_name == "Tracking":
            st.subheader("Daily Habit Tracking")

            # -------------------------------------------------------------
            # 1) Get the first row from the "Tracking" sheet to read headers
            # -------------------------------------------------------------
            df_raw = conn.read(worksheet="Tracking", header=None)

            # Make sure we have at least 1 row for headers
            if len(df_raw) < 1:
                st.error("Your 'Tracking' sheet must have at least one row for headers.")
                st.stop()

            # Row 1 (index=0) -> column names
            headers = df_raw.iloc[0].tolist()
            df_data = df_raw.iloc[1:].copy()  # Data below the header row

            if not df_data.empty:
                df_data.columns = headers

            # -------------------------------------------------------------
            # 2) Hardcoded questions for the tracking form
            # -------------------------------------------------------------
            hardcoded_questions = {
                "8hrs Sleep": "Did you sleep for at least 8 hours?",
                "Workout on Schedule": "Did you complete your workout as scheduled?",
                "Yoga": "Did you perform your yoga session?",
                "Meditate": "Did you meditate today?",
                "Journal": "Did you write in your journal?",
                "No Nic": "Did you avoid nicotine products?",
                "<30 min Social Media": "Did you limit social media use to under 30 minutes?",
                "Work Accomplished": "Did you accomplish your work goals for the day?",
                "M": "Did you drink?",
                "P": "Watch TikTok?"
            }

            # -------------------------------------------------------------
            # 3) Prepare today's date info
            # -------------------------------------------------------------
            today = datetime.date.today()
            today_str = today.strftime("%Y-%m-%d")
            day_str = today.strftime("%A")  # e.g., "Monday"

            # Display date and day at the top
            st.write(f"**Date:** {today_str}")
            st.write(f"**Day:** {day_str}")

            # -------------------------------------------------------------
            # 4) Build the form dynamically based on columns
            # -------------------------------------------------------------
            with st.form("tracking_form", clear_on_submit=True):
                st.write("Please answer Yes/No for the habits below:")

                # Collect user responses in a dictionary
                user_responses = {}

                for col_name in headers:
                    if col_name in ["Date", "Day"]:
                        continue  # Skip auto-filled columns
                    else:
                        # Use hardcoded question if available, else fallback to column name
                        prompt = hardcoded_questions.get(col_name, f"Please answer for {col_name}")
                        user_responses[col_name] = st.radio(prompt, ["Yes", "No"], horizontal=True, key=col_name)

                # Submit button inside the form block
                submitted = st.form_submit_button("Submit")

                if submitted:
                    row_dict = {}
                    for col_name in headers:
                        if col_name == "Date":
                            row_dict[col_name] = today_str
                        elif col_name == "Day":
                            row_dict[col_name] = day_str
                        else:
                            ans = user_responses.get(col_name, "No")
                            row_dict[col_name] = 1 if ans == "Yes" else 0

                    df_new_row = pd.DataFrame([row_dict])

                    # Append to the data and ensure structure consistency
                    df_final = pd.concat([df_data, df_new_row], ignore_index=True)

                    # Ensure columns match
                    df_final = df_final[headers]

                    # Update the data only below the header
                    conn.update(worksheet="Tracking", data=pd.concat([df_final], ignore_index=True))

                    st.success(f"Data for {today_str} submitted successfully!")
                    #st.rerun()
        elif worksheet_name in ["Push", "Pull", "Legs"]:
            st.subheader(f"Worksheet: {worksheet_name}")

            # Read data from the sheet
            df_raw = conn.read(worksheet=worksheet_name, header=None)

            if df_raw.empty or len(df_raw) < 2:
                st.warning(f"No sufficient data available in the '{worksheet_name}' worksheet.")
                st.write("Date of Last Workout: N/A")
            else:
                # Extract headers and data
                headers = df_raw.iloc[0].tolist()
                df_data = df_raw.iloc[1:].copy()
                df_data.columns = headers

                date_col = headers[0]
                exercise_cols = headers[1:]

                last_date = df_data[date_col].max() if not df_data[date_col].isna().all() else "N/A"
                st.write(f"**Date of Last Workout:** {last_date}")

                workout_data = {exercise: "N/A" for exercise in exercise_cols}

                st.write("### Enter your current workout details:")
                with st.form(f"workout_form_{worksheet_name}", clear_on_submit=True):
                    for exercise in exercise_cols:
                        st.write(f"### {exercise}")

                        # Last workout data for this exercise
                        exercise_data = df_data[[date_col, exercise]].dropna(subset=[exercise])
                        last_sets_reps = exercise_data[exercise].iloc[-1] if not exercise_data.empty else "N/A"
                        st.write(f"Last workout: {last_sets_reps}")

                        col1, col2, col3, col4, col5 = st.columns(5)
                        reps_input = [col.number_input(f"Set {i+1} Reps", 0, 50, key=f"{exercise}_reps_{i+1}") for i, col in enumerate([col1, col2, col3, col4, col5])]
                        weight_input = [col.number_input(f"Set {i+1} Weight (lbs)", 0, 1000, key=f"{exercise}_weight_{i+1}") for i, col in enumerate([col1, col2, col3, col4, col5])]

                        sets_reps_input = [f"{reps}@{weight}" for reps, weight in zip(reps_input, weight_input) if reps > 0]
                        workout_data[exercise] = ", ".join(sets_reps_input) if sets_reps_input else last_sets_reps

                    submitted = st.form_submit_button("Submit Workout")
                    if submitted:
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        new_row_dict = {date_col: today}

                        # Fill in the new row data
                        for exercise in exercise_cols:
                            new_row_dict[exercise] = workout_data[exercise]

                        # Convert new row to DataFrame and concatenate with existing data
                        df_new_row = pd.DataFrame([new_row_dict])
                        df_final = pd.concat([df_data, df_new_row], ignore_index=True)

                        # Ensure the final dataframe matches the original structure
                        df_final = df_final[headers]

                        # Update the sheet with the new dataframe
                        conn.update(worksheet=worksheet_name, data=pd.concat([df_final], ignore_index=True))

                        st.success(f"Workout data for '{worksheet_name}' submitted successfully!")
