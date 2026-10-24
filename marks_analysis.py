
import streamlit as st
from database import client

db = client["smart_student_hub"]
marks_collection = db["marks"]


def get_marks_summary(student_id):
    """Get marks belonging only to the logged-in student."""

    records = list(
        marks_collection.find(
            {"student_id": student_id},
            {
                "_id": 0,
                "subject": 1,
                "marks_obtained": 1,
                "total_marks": 1,
            },
        ).sort("created_at", 1)
    )

    if not records:
        return None

    total_obtained = sum(
        record["marks_obtained"] for record in records
    )

    total_possible = sum(
        record["total_marks"] for record in records
    )

    overall_percentage = (
        total_obtained / total_possible
    ) * 100 if total_possible else 0

    subject_results = []

    for record in records:
        obtained = record["marks_obtained"]
        total = record["total_marks"]

        percentage = (
            obtained / total
        ) * 100 if total else 0

        subject_results.append({
            "subject": record["subject"],
            "marks_obtained": obtained,
            "total_marks": total,
            "percentage": round(percentage, 2),
        })

    return {
        "subjects": subject_results,
        "total_obtained": total_obtained,
        "total_possible": total_possible,
        "overall_percentage": round(overall_percentage, 2),
    }


def show_marks_analysis():
    """Display an academic performance summary."""

    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in first.")
        return

    st.subheader("📊 AI-Powered Marks Analysis")

    summary = get_marks_summary(student_id)

    if not summary:
        st.info(
            "You haven't recorded any marks yet. "
            "Add marks in My Marks to get your analysis."
        )
        return

    st.metric(
        "Overall Percentage",
        f"{summary['overall_percentage']:.2f}%"
    )

    st.write("### 📚 Subject-wise Results")

    for subject in summary["subjects"]:
        st.write(
            f"**{subject['subject']}** — "
            f"{subject['marks_obtained']:g}/"
            f"{subject['total_marks']:g} "
            f"({subject['percentage']:.2f}%)"
        )

    st.write("### 💡 Get Personalized Advice")

    if st.button("🤖 Analyse My Marks with AI"):
        # Store the summary for the AI Mentor.
        st.session_state["marks_analysis_data"] = summary
        st.success(
            "Your marks summary is ready for the AI Mentor!"
        )
