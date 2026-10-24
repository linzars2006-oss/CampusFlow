
import streamlit as st
from datetime import datetime, timezone
from database import client

db = client["smart_student_hub"]
projects_collection = db["projects"]


def show_projects():
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in to access your projects.")
        return

    st.title("🚀 My Projects")
    st.write("Track your projects and monitor their progress.")

    # Add a new project
    with st.form("add_project_form", clear_on_submit=True):
        project_name = st.text_input("Project Name")
        description = st.text_area("Project Description")

        technology = st.text_input(
            "Technologies Used",
            placeholder="Python, Streamlit, MongoDB"
        )

        status = st.selectbox(
            "Project Status",
            ["Not Started", "In Progress", "Completed"]
        )

        submitted = st.form_submit_button("Add Project")

        if submitted:
            if not project_name.strip():
                st.warning("Please enter a project name.")
            else:
                projects_collection.insert_one({
                    "student_id": student_id,
                    "project_name": project_name.strip(),
                    "description": description.strip(),
                    "technology": technology.strip(),
                    "status": status,
                    "created_at": datetime.now(timezone.utc)
                })

                st.success("Project added successfully!")
                st.rerun()

    st.divider()
    st.subheader("📂 Your Projects")

    projects = list(
        projects_collection.find(
            {"student_id": student_id}
        ).sort("created_at", -1)
    )

    if not projects:
        st.info("You haven't added any projects yet.")
        return

    for project in projects:
        with st.expander(
            f"📌 {project['project_name']} — {project['status']}"
        ):
            st.write("**Description:**")
            st.write(project.get("description") or "No description")

            st.write("**Technologies:**")
            st.write(project.get("technology") or "Not specified")

            new_status = st.selectbox(
                "Update Status",
                ["Not Started", "In Progress", "Completed"],
                index=[
                    "Not Started",
                    "In Progress",
                    "Completed"
                ].index(project["status"]),
                key=f"status_{project['_id']}"
            )

            if st.button(
                "Save Status",
                key=f"save_status_{project['_id']}"
            ):
                projects_collection.update_one(
                    {
                        "_id": project["_id"],
                        "student_id": student_id
                    },
                    {"$set": {"status": new_status}}
                )

                st.success("Project status updated!")
                st.rerun()

            if st.button(
                "🗑️ Delete Project",
                key=f"delete_project_{project['_id']}"
            ):
                projects_collection.delete_one({
                    "_id": project["_id"],
                    "student_id": student_id
                })

                st.success("Project deleted!")
                st.rerun()
