
import streamlit as st

from auth import show_auth
from notes import show_notes
from projects import show_projects
from marks import show_marks
from ai_mentor import show_ai_mentor
from dashboard import show_dashboard

# Page configuration
st.set_page_config(
    page_title="Smart Student Hub",
    page_icon="🎓",
    layout="wide"
)


# Check whether a student is logged in
if "student_id" not in st.session_state:
    show_auth()
    st.stop()


# Main application
st.title("🎓 Smart Student Hub")

st.write(
    f"Welcome, {st.session_state.get('student_name', 'Student')}!"
)

st.caption("Your personal space for learning and project tracking.")


# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "My Notes",
        "My Projects",
        "My Marks",
        "Student Dashboard",
        "AI Mentor"
    ]
)


# Home page
if page == "Home":
    st.subheader("🏠 Your Learning Space")

    st.write(
        "Manage your personal notes, track your projects, "
        "and monitor your academic progress."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "**📝 My Notes**\n\n"
            "Create, view, edit, and delete your personal notes."
        )

    with col2:
        st.info(
            "**🚀 My Projects**\n\n"
            "Add projects and track their progress."
        )


# Notes page
elif page == "My Notes":
    show_notes()


# Projects page
elif page == "My Projects":
    show_projects()

elif page == "My Marks":
    show_marks()

elif page == "Student Dashboard":
    show_dashboard()

elif page == "AI Mentor":
    show_ai_mentor()



# Logout
st.sidebar.divider()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()
