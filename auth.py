
import streamlit as st
import bcrypt
from database import client

db = client["smart_student_hub"]
students_collection = db["students"]


def show_auth():
    st.title("🎓 Student Account")

    choice = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True
    )

    with st.form("auth_form"):
        email = st.text_input("Email").strip().lower()

        password = st.text_input(
            "Password",
            type="password"
        )

        name = ""

        if choice == "Register":
            name = st.text_input("Full Name")

        submitted = st.form_submit_button(choice)

        if submitted:
            if not email or not password:
                st.error("Enter your email and password.")
                return

            if choice == "Register":
                if not name.strip():
                    st.error("Enter your full name.")
                    return

                if len(password) < 8:
                    st.error(
                        "Password must have at least 8 characters."
                    )
                    return

                if students_collection.find_one({"email": email}):
                    st.error("This email is already registered.")
                    return

                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                )

                students_collection.insert_one({
                    "name": name.strip(),
                    "email": email,
                    "password_hash": password_hash
                })

                st.success(
                    "Registration successful! Please log in."
                )

            else:
                student = students_collection.find_one(
                    {"email": email}
                )

                if student and bcrypt.checkpw(
                    password.encode("utf-8"),
                    student["password_hash"]
                ):
                    st.session_state["student_id"] = str(
                        student["_id"]
                    )

                    st.session_state["student_name"] = (
                        student["name"]
                    )

                    st.rerun()

                else:
                    st.error("Invalid email or password.")
