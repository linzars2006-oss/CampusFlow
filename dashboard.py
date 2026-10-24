
import streamlit as st
import pandas as pd
from database import client

db = client["smart_student_hub"]
marks_collection = db["marks"]


def get_student_marks(student_id):
    records = list(
        marks_collection.find(
            {"student_id": student_id},
            {
                "_id": 0,
                "subject": 1,
                "marks_obtained": 1,
                "total_marks": 1,
                "created_at": 1,
            },
        ).sort("created_at", 1)
    )

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Ensure marks are numeric.
    df["marks_obtained"] = pd.to_numeric(
        df["marks_obtained"], errors="coerce"
    )
    df["total_marks"] = pd.to_numeric(
        df["total_marks"], errors="coerce"
    )

    # Remove invalid records.
    df = df.dropna(
        subset=["subject", "marks_obtained", "total_marks"]
    )

    # Avoid division by zero and invalid totals.
    df = df[df["total_marks"] > 0]

    if df.empty:
        return df

    df["percentage"] = (
        df["marks_obtained"] / df["total_marks"] * 100
    ).round(2)

    return df


def show_dashboard():
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in to view your dashboard.")
        return

    st.title("📊 Student Performance Dashboard")
    st.write(
        "Understand your academic performance and "
        "identify subjects that need more practice."
    )

    df = get_student_marks(student_id)

    if df.empty:
        st.info(
            "No valid marks found. Add your marks in "
            "My Marks to view your dashboard."
        )
        return

    # Calculate overall performance using total marks.
    total_obtained = df["marks_obtained"].sum()
    total_possible = df["total_marks"].sum()

    overall_percentage = (
        total_obtained / total_possible * 100
    )

    strongest = df.loc[df["percentage"].idxmax()]
    weakest = df.loc[df["percentage"].idxmin()]

    # Summary metrics.
    st.subheader("🎯 Overall Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Overall Percentage",
        f"{overall_percentage:.2f}%"
    )

    col2.metric(
        "Marks Obtained",
        f"{total_obtained:g} / {total_possible:g}"
    )

    col3.metric(
        "Subjects Recorded",
        df["subject"].nunique()
    )

    st.divider()

    # Subject-wise performance.
    st.subheader("📚 Subject-wise Performance")

    subject_summary = (
        df.groupby("subject", as_index=False)
        .agg(
            marks_obtained=("marks_obtained", "sum"),
            total_marks=("total_marks", "sum"),
        )
    )

    subject_summary["percentage"] = (
        subject_summary["marks_obtained"]
        / subject_summary["total_marks"]
        * 100
    ).round(2)

    st.bar_chart(
        subject_summary.set_index("subject")["percentage"],
        y_label="Percentage",
    )

    st.dataframe(
        subject_summary.rename(
            columns={
                "subject": "Subject",
                "marks_obtained": "Marks Obtained",
                "total_marks": "Total Marks",
                "percentage": "Percentage",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # Strengths and improvement areas.
    st.subheader("💡 Performance Insights")

    col1, col2 = st.columns(2)

    col1.success(
        f"**Strongest subject:** {strongest['subject']}\n\n"
        f"Score: {strongest['percentage']:.2f}%"
    )

    col2.warning(
        f"**Needs more practice:** {weakest['subject']}\n\n"
        f"Score: {weakest['percentage']:.2f}%"
    )

    # Show recorded marks.
    st.divider()
    st.subheader("📝 Recorded Marks")

    display_df = df.copy()

    if "created_at" in display_df.columns:
        display_df["created_at"] = pd.to_datetime(
            display_df["created_at"], errors="coerce", utc=True
        )

    display_df = display_df.rename(
        columns={
            "subject": "Subject",
            "marks_obtained": "Marks Obtained",
            "total_marks": "Total Marks",
            "percentage": "Percentage",
            "created_at": "Recorded At (UTC)",
        }
    )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "Overall percentage is calculated from total marks. "
        "Insights use the marks currently recorded in your account."
    )
