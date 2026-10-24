
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from database import client

db = client["smart_student_hub"]
marks_collection = db["marks"]


def show_marks():
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in to view your marks.")
        return

    st.title("📊 My Marks Tracker")
    st.write("Record your subject marks and track your academic performance.")

    # Add marks
    with st.form("add_marks_form", clear_on_submit=True):
        subject = st.text_input("Subject Name")

        col1, col2 = st.columns(2)

        with col1:
            marks_obtained = st.number_input(
                "Marks Obtained",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0
            )

        with col2:
            total_marks = st.number_input(
                "Total Marks",
                min_value=1.0,
                max_value=1000.0,
                value=100.0,
                step=1.0
            )

        submitted = st.form_submit_button("Save Marks")

        if submitted:
            if not subject.strip():
                st.error("Please enter a subject name.")
            elif marks_obtained > total_marks:
                st.error("Marks obtained cannot exceed total marks.")
            else:
                marks_collection.insert_one({
                    "student_id": student_id,
                    "subject": subject.strip(),
                    "marks_obtained": marks_obtained,
                    "total_marks": total_marks,
                    "created_at": datetime.now(timezone.utc)
                })

                st.success("Marks saved successfully!")
                st.rerun()

    st.divider()
    st.subheader("📚 My Subject Marks")

    records = list(
        marks_collection.find(
            {"student_id": student_id}
        ).sort("created_at", 1)
    )

    if not records:
        st.info("No marks added yet. Enter your first subject above.")
        return

    # Prepare chart data
    data = []

    for record in records:
        percentage = (
            record["marks_obtained"] / record["total_marks"]
        ) * 100

        data.append({
            "Subject": record["subject"],
            "Marks Obtained": record["marks_obtained"],
            "Total Marks": record["total_marks"],
            "Percentage": round(percentage, 2)
        })

    df = pd.DataFrame(data)

    # Summary metrics
    total_obtained = sum(
        record["marks_obtained"] for record in records
    )
    total_possible = sum(
        record["total_marks"] for record in records
    )
    average_percentage = (
        total_obtained / total_possible
    ) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Subjects Recorded", len(records))
    col2.metric("Total Marks", f"{total_obtained:g} / {total_possible:g}")
    col3.metric("Overall Percentage", f"{average_percentage:.2f}%")

    # Marks table
    st.subheader("📋 Marks Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Performance chart
    st.subheader("📈 Subject-wise Performance")
    chart_data = df.set_index("Subject")[["Percentage"]]
    st.bar_chart(chart_data, y="Percentage")

    # Delete individual record
    st.subheader("🗑️ Manage Marks")

    record_options = {
        f"{r['subject']} — {r['marks_obtained']:g}/{r['total_marks']:g} (ID: {r['_id']})": r
        for r in records
    }

    selected_label = st.selectbox(
        "Choose a marks record to delete",
        list(record_options.keys())
    )

    if st.button("Delete Selected Record"):
        selected_record = record_options[selected_label]

        marks_collection.delete_one({
            "_id": selected_record["_id"],
            "student_id": student_id
        })

        st.success("Marks record deleted!")
        st.rerun()
