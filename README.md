# CampusFlow — Smart Student Hub

> Manage notes, projects and marks in one place, see your performance at a glance, and get help from a locally running AI mentor.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)
![MongoDB](https://img.shields.io/badge/database-MongoDB%20Atlas-47A248)
![Status](https://img.shields.io/badge/status-prototype-orange)
<!-- TODO: Add a license badge once a LICENSE file is added, e.g. ![License](https://img.shields.io/badge/license-MIT-green) -->

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact and Acknowledgments](#contact-and-acknowledgments)

## Overview

CampusFlow is a Streamlit application that gives students one centralized place to organize study notes, manage projects, record subject marks and review their academic performance. An AI Mentor, powered by Ollama running the Qwen2.5 3B model on your own machine, answers academic questions without sending your data to a third-party AI service. Application data and chat history are stored in MongoDB Atlas.

An AI Study Planner and an AI Interview Guide are planned to support scheduling, progress tracking and placement preparation.

## Features

- **Student authentication:** Registration and login with bcrypt password hashing.
- **Notes management:** Create, organize and revisit study notes.
- **Project management:** Keep track of project details.
- **Marks management:** Record subject-wise marks and calculate percentages.
- **Performance dashboard:** Visualize results and spot stronger and weaker subjects.
- **AI Mentor:** Ask academic questions to a local language model, with chat history saved in MongoDB.
- **Study Planner (planned):** Generate study schedules and track tasks with checklists.
- **Interview Guide (planned):** Practise technical and HR questions with AI feedback.

> **Status:** Prototype. Some modules still need end-to-end testing, and the Study Planner and Interview Guide are not yet implemented.

## Screenshots

> Add your images to a `docs/screenshots/` folder using the file names below. The links will then render automatically.

### Login and registration

<img width="921" height="664" alt="image" src="https://github.com/user-attachments/assets/e3846c60-6d81-48db-95c5-209270bdff3b" />


### Performance dashboard

<img width="1920" height="2506" alt="Screenshot 2026-10-24 112803" src="https://github.com/user-attachments/assets/d49b07f0-e4c0-43e2-8c85-b633a6e6a0da" />


### Marks management

<img width="624" height="819" alt="image" src="https://github.com/user-attachments/assets/ca3ea07e-a3de-45a8-8654-c53f870346fa" />


### Notes and projects

<img width="663" height="794" alt="image" src="https://github.com/user-attachments/assets/073c89a9-cd45-4453-a6e3-56b15cba4219" />
<img width="610" height="768" alt="image" src="https://github.com/user-attachments/assets/9c1fb4e9-c314-4118-920b-9f9d49a087ab" />

### AI Mentor

<img width="968" height="2906" alt="image" src="https://github.com/user-attachments/assets/6acdbff4-47aa-427a-923f-d1ed4f256a97" />


<!-- TODO: Optionally add a short demo GIF at docs/screenshots/demo.gif and a link to a live demo if deployed. -->

## Tech Stack

| Layer | Technology |
|---|---|
| Interface | Streamlit |
| Database | MongoDB Atlas (PyMongo) |
| Authentication | bcrypt |
| Data handling | pandas |
| AI | Ollama + Qwen2.5 3B (local) |
| Configuration | python-dotenv |

## Getting Started

### Prerequisites

- Python 3.11 or later
- Git
- A [MongoDB Atlas](https://www.mongodb.com/atlas) account and connection string
- [Ollama](https://ollama.com/) installed and running locally

<!-- TODO: Confirm the exact minimum Python version after testing. -->

### 1. Clone the repository

```bash
git clone https://github.com/linzars2006-oss/CampusFlow.git
cd CampusFlow
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you have not created `requirements.txt` yet, add it with this content:

```text
streamlit
pymongo
python-dotenv
bcrypt
pandas
requests
```

<!-- TODO: Pin versions after verifying them, e.g. with `pip freeze`. -->

### 4. Configure the environment

Create a `.env` file in the project root:

```dotenv
MONGO_URI=your_mongodb_atlas_connection_string
```

| Variable | Required | Description |
|---|---|---|
| `MONGO_URI` | Yes | MongoDB Atlas connection string used by `database.py`. |

Never commit `.env` or any credentials to version control. Also make sure your current IP address is allowed in MongoDB Atlas under **Network Access**.

### 5. Set up the AI model

Install Ollama, then download the model:

```bash
ollama pull qwen2.5:3b
```

Keep Ollama running while you use the AI Mentor. The app calls the local endpoint:

```text
http://localhost:11434/api/chat
```

### 6. Run the application

```bash
streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in your browser.

## Usage

1. **Register or log in** to your student account.
2. **Add notes, projects or marks** from the relevant pages.
3. **Open the dashboard** to review your results and see which subjects need attention.
4. **Ask the AI Mentor** for help with a concept.

### How percentages are calculated

```text
Overall Percentage = (Total Marks Obtained / Total Maximum Marks) × 100
```

Example:

| Subject | Marks Obtained | Total Marks |
|---|---:|---:|
| Java | 56 | 100 |
| Data Structures | 79 | 100 |
| Machine Learning | 90 | 100 |

```text
(56 + 79 + 90) / (100 + 100 + 100) × 100 = 225 / 300 × 100 = 75%
```

### AI Mentor example

Prompt:

```text
Explain the difference between an array and an ArrayList in Java.
```

The model replies in plain language, typically covering that arrays have a fixed size while an `ArrayList` can grow and shrink dynamically. Exact answers vary because they are generated by the model.

## Project Structure

```text
CampusFlow/
├── app.py               # Main Streamlit entry point
├── auth.py              # Registration and login
├── database.py          # MongoDB connection and collections
├── notes.py             # Notes management
├── projects.py          # Project management
├── marks.py             # Marks management
├── marks_analysis.py    # Marks summary and analysis
├── dashboard.py         # Performance dashboard
├── ai_mentor.py         # AI Mentor chat (Ollama)       <!-- TODO: confirm file exists -->
├── ai_chat_db.py        # Chat history storage          <!-- TODO: confirm file exists -->
├── requirements.txt     # Python dependencies
├── docs/
│   └── screenshots/     # README images
├── .env                 # Local configuration (not committed)
└── .gitignore
```

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Connection refused on port 11434 | Ollama is not running | Start Ollama, then retry. |
| Model not found | Model not downloaded | Run `ollama pull qwen2.5:3b`. |
| MongoDB timeout or authentication error | IP not allowed or wrong URI | Add your IP in Atlas **Network Access** and re-check `MONGO_URI`. |
| `KeyError` or `None` for `MONGO_URI` | `.env` missing or in the wrong folder | Place `.env` in the project root and restart the app. |
| `ModuleNotFoundError` | Virtual environment not active | Activate `.venv` and run `pip install -r requirements.txt`. |
| Slow AI responses | Model running on CPU | Close other heavy apps or use a smaller model. |

## Testing

No automated tests exist yet. Until they are added, use this manual checklist:

- [ ] Register a new account and log in.
- [ ] Confirm a second account cannot see the first account's data.
- [ ] Add, edit and delete a note and a project.
- [ ] Add marks and check the percentage on the dashboard.
- [ ] Send a message to the AI Mentor and confirm it is saved in history.
- [ ] Log out and log back in to confirm data persists.

<!-- TODO: Add automated tests for authentication, marks calculations and database operations. -->

## Roadmap

- [x] Student registration and login
- [x] Notes and project modules
- [x] Marks recording and analysis
- [ ] Verify dashboard and AI Mentor end to end
- [ ] AI Study Planner with daily checklists
- [ ] AI Interview Guide with mock interviews and feedback
- [ ] Automated tests
- [ ] Deployment and production configuration guide

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes and test them locally.
4. Commit with a descriptive message.
5. Push the branch and open a pull request.

<!-- TODO: Add CONTRIBUTING.md with coding conventions and pull request guidelines. -->

## License

<!-- TODO: Add a LICENSE file (for example MIT) and update this section. -->

No license has been chosen yet. Until one is added, reuse, modification and distribution rights are not granted.

## Contact and Acknowledgments

**Developer:** Linza R. S.
**GitHub:** [linzars2006-oss](https://github.com/linzars2006-oss)
**Repository:** [CampusFlow](https://github.com/linzars2006-oss/CampusFlow)

Built with [Streamlit](https://streamlit.io/), [MongoDB Atlas](https://www.mongodb.com/atlas), [Ollama](https://ollama.com/) and [Qwen2.5](https://huggingface.co/Qwen).
