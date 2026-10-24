
from datetime import datetime, timezone

import streamlit as st
from database import client

db = client["smart_student_hub"]
notes_collection = db["notes"]


def show_notes():
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in to access your notes.")
        return

    st.title("📝 My Personal Notes")
    st.write("Create, view, edit, and delete your personal notes.")

    # Add a new note
    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Note Title")
        subject = st.text_input("Subject")
        content = st.text_area("Write your note here")

        submitted = st.form_submit_button("Save Note")

        if submitted:
            if not title.strip() or not content.strip():
                st.warning("Please enter a title and note content.")
            else:
                notes_collection.insert_one({
                    "student_id": student_id,
                    "title": title.strip(),
                    "subject": subject.strip() or "General",
                    "content": content.strip(),
                    "created_at": datetime.now(timezone.utc)
                })

                st.success("Note saved successfully!")
                st.rerun()

    st.divider()
    st.subheader("📚 Your Saved Notes")

    notes = list(
        notes_collection.find(
            {"student_id": student_id}
        ).sort("created_at", -1)
    )

    if not notes:
        st.info("You haven't added any notes yet.")
        return

    # View, edit, and delete notes
    for note in notes:
        with st.expander(
            f"{note['title']} — {note.get('subject', 'General')}"
        ):
            st.write("**Note content:**")
            st.write(note["content"])

            st.divider()
            st.write("**Edit this note**")

            with st.form(f"edit_form_{note['_id']}"):
                edited_title = st.text_input(
                    "Title",
                    value=note["title"],
                    key=f"title_{note['_id']}"
                )

                edited_subject = st.text_input(
                    "Subject",
                    value=note.get("subject", "General"),
                    key=f"subject_{note['_id']}"
                )

                edited_content = st.text_area(
                    "Content",
                    value=note["content"],
                    key=f"content_{note['_id']}"
                )

                save_changes = st.form_submit_button("Update Note")

                if save_changes:
                    if not edited_title.strip() or not edited_content.strip():
                        st.warning("Title and content cannot be empty.")
                    else:
                        notes_collection.update_one(
                            {
                                "_id": note["_id"],
                                "student_id": student_id
                            },
                            {
                                "$set": {
                                    "title": edited_title.strip(),
                                    "subject": edited_subject.strip() or "General",
                                    "content": edited_content.strip(),
                                    "updated_at": datetime.now(timezone.utc)
                                }
                            }
                        )

                        st.success("Note updated successfully!")
                        st.rerun()

            if st.button(
                "🗑️ Delete Note",
                key=f"delete_{note['_id']}"
            ):
                notes_collection.delete_one({
                    "_id": note["_id"],
                    "student_id": student_id
                })

                st.success("Note deleted successfully!")
                st.rerun()
