
import json
import requests
import streamlit as st

from ai_chat_db import (
    save_chat_message,
    get_chat_history,
    clear_chat_history,
)
from marks_analysis import get_marks_summary

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


def ask_local_llm(question, chat_history):
    messages = [
        {
            "role": "system",
            "content": (
                "You are Smart Student Hub's AI Mentor. "
                "Explain concepts in simple English. "
                "Help with programming, academics, interviews, "
                "aptitude, and study plans. "
                "Give examples and simple code when useful. "
                "When analyzing marks, use only the supplied data. "
                "Do not invent marks or academic results."
            ),
        }
    ]

    messages.extend(chat_history)
    messages.append({
        "role": "user",
        "content": question,
    })

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()
    return response.json()["message"]["content"]


def show_ai_mentor():
    student_id = st.session_state.get("student_id")

    if not student_id:
        st.warning("Please log in to use your AI Mentor.")
        return

    st.title("🤖 AI Mentor")
    st.write(
        "Ask questions about programming, academics, "
        "interviews, aptitude, or study plans."
    )

    # Load this student's saved conversation.
    history_key = f"ai_chat_{student_id}"

    if history_key not in st.session_state:
        try:
            st.session_state[history_key] = (
                get_chat_history(student_id)
            )
        except Exception:
            st.error("Could not load your saved chat history.")
            return

    chat_history = st.session_state[history_key]

    # Clear saved conversation.
    if st.button("🧹 Clear Chat"):
        try:
            clear_chat_history(student_id)
            st.session_state[history_key] = []
            st.rerun()
        except Exception:
            st.error("Could not clear your saved chat history.")
            return

    # Analyze the student's actual marks.
    if st.button("📊 Analyse My Marks"):
        try:
            summary = get_marks_summary(student_id)

            if not summary:
                st.warning(
                    "You haven't added any marks yet. "
                    "Please add marks in My Marks first."
                )
            else:
                marks_prompt = f"""
Analyze this student's actual academic marks.

Marks data:
{json.dumps(summary, indent=2)}

Please:
1. Identify the strongest subject.
2. Identify the subject needing the most improvement.
3. Explain the results in simple English.
4. Give practical study tips for each subject.
5. Create a realistic 7-day study plan.
6. Be encouraging and constructive.

Use only the marks provided. Do not invent results.
"""

                with st.spinner("Analyzing your marks..."):
                    answer = ask_local_llm(
                        marks_prompt,
                        chat_history,
                    )

                # Display the AI's response.
                with st.chat_message("assistant"):
                    st.markdown(answer)

                # Save the analysis to MongoDB.
                save_chat_message(
                    student_id,
                    "user",
                    "Please analyze my marks and create a personalized study plan.",
                )
                save_chat_message(
                    student_id,
                    "assistant",
                    answer,
                )

                # Update session history.
                chat_history.append({
                    "role": "user",
                    "content": (
                        "Please analyze my marks and create "
                        "a personalized study plan."
                    ),
                })
                chat_history.append({
                    "role": "assistant",
                    "content": answer,
                })

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.Timeout:
            st.error(
                "The AI took too long to respond. "
                "Please try again."
            )
        except requests.exceptions.RequestException as error:
            st.error(f"AI request failed: {error}")
        except Exception as error:
            st.error(f"Could not analyze your marks: {error}")

    # Display saved conversation.
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Normal AI chat.
    question = st.chat_input("Ask your AI Mentor...")

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.spinner("Your AI Mentor is thinking..."):
                answer = ask_local_llm(
                    question,
                    chat_history,
                )

            with st.chat_message("assistant"):
                st.markdown(answer)

            # Save both messages to MongoDB.
            save_chat_message(student_id, "user", question)
            save_chat_message(student_id, "assistant", answer)

            chat_history.append({
                "role": "user",
                "content": question,
            })
            chat_history.append({
                "role": "assistant",
                "content": answer,
            })

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.Timeout:
            st.error(
                "The AI took too long to respond. "
                "Try a shorter question."
            )
        except requests.exceptions.RequestException as error:
            st.error(f"AI request failed: {error}")
        except Exception as error:
            st.error(f"Something went wrong: {error}")
