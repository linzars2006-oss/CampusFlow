<div align="center">

# 🎓 CampusFlow · SmartEdu AI

**Early-warning academic risk intelligence for universities.**

Spot the students who are slipping — in **Week 4**, not at the end of the semester.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django REST](https://img.shields.io/badge/Django-REST%20Framework-092E20?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Inference%20Service-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-LSTM%20%2B%20Attention-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-18%20%2B%20Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)

</div>

---

## ✨ What it does

Most academic dashboards tell you a student failed. CampusFlow tells you **who is about to**, and **why**, while there's still time to intervene.

It ingests weekly attendance, assignment submissions and continuous assessment scores, feeds the resulting 16-week sequence into a **temporal-attention LSTM**, and returns a **Low / Medium / High** risk level with the specific factors that drove it — *"declining score trend after Week 8"*, not an opaque probability.

| | |
|---|---|
| 📈 **Sequential risk modelling** | LSTM with temporal attention over per-week student trajectories — reads trend *shape*, not just end-of-term averages |
| ⏱️ **Mid-semester detection** | Scores risk from Week 4 onward, without waiting for final aggregates |
| 🔍 **Explainability built in** | Attention weights + SHAP surface the top contributing factors on every prediction |
| 🧑‍🏫 **Three role-based dashboards** | Admin (institution analytics), Faculty (risk triage, intervention notes), Student (own trends, scoped advisor chat) |
| 🧪 **Honest benchmarking** | Ships with XGBoost, logistic regression and a rule-based baseline, evaluated on identical held-out splits |
| 🛡️ **Decision support, never punishment** | No automated sanctions. Every flag routes to a human advisor. See [LIMITATIONS.md](LIMITATIONS.md) |

---

## 🏗️ Architecture

```
            ┌──────────────────────────────┐
            │   React 18 + Vite + Tailwind │   :5173
            │  Admin · Faculty · Student   │
            └──────────────┬───────────────┘
                           │ REST + JWT
            ┌──────────────▼───────────────┐
            │  Django REST Framework API   │   :8000
            │  auth · academics · risk     │
            │  recommendations · chatbot   │
            └───────┬──────────────┬───────┘
                    │              │
      ┌─────────────▼───┐   ┌──────▼─────────────────┐
      │ SQLite / Postgres│   │ MongoDB Atlas          │
      │ relational core  │   │ chat + event logs      │
      └──────────────────┘   └────────────────────────┘
                    │
            ┌───────▼──────────────────────┐
            │  FastAPI inference service   │   :8001
            │  LSTM + Attention (PyTorch)  │
            │  XGBoost · LogReg · Rules    │
            └──────────────────────────────┘
```

```
CampusFlow/
├── backend/            # Django REST API — models, views, chatbot, recommendation engine
│   ├── api/            # auth, students, faculty, subjects, attendance, marks, risk, interventions
│   └── smartedu/       # settings, URLs, WSGI
├── ml_service/         # FastAPI inference microservice (app.py)
├── ml_pipeline/        # dataset generation, feature engineering, models, training, explainability
│   ├── models.py                 # StudentRiskLSTM, TemporalAttention, baselines
│   ├── train_and_evaluate.py     # full benchmark run
│   └── academic_risk_prediction_benchmark.ipynb
├── react/              # Vite + Tailwind frontend
├── tests/              # pipeline tests
└── LIMITATIONS.md      # ethics, bias, and deployment guidance — read this
```

---

## 🚀 Quick start

> Requires Python 3.10+, Node 18+, and (optionally) a MongoDB instance.

**1 · Backend API**

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

**2 · ML inference service**

```bash
uvicorn ml_service.app:app --reload --port 8001
```

**3 · Frontend**

```bash
cd react
npm install
npm run dev          # http://localhost:5173
```

**4 · Train the models (optional — generates the synthetic cohort and benchmarks everything)**

```bash
python ml_pipeline/generate_dataset.py      # 400 students × 16 weeks
python ml_pipeline/train_and_evaluate.py    # writes best_lstm_model.pt to ml_pipeline/data/
```

**Environment variables**

| Variable | Default | Purpose |
|---|---|---|
| `ML_SERVICE_URL` | `http://127.0.0.1:8001` | Where Django reaches the inference service |
| `MONGO_URI` | local instance | Chat and event logging |

---

## 🔌 API at a glance

**Django REST API** — base `http://127.0.0.1:8000/api`

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register/` · `/auth/login/` | JWT authentication |
| `GET` | `/auth/me/` | Current user + role |
| `GET/POST` | `/students/` · `/faculty/` · `/subjects/` | Core CRUD |
| `POST` | `/admin/bulk-import/` | Bulk student import |
| `GET` | `/admin/analytics/` | Institution-wide analytics |
| `POST` | `/attendance/bulk/` · `/marks/` · `/assignments/` | Weekly academic capture |
| `GET` | `/faculty/risk-dashboard/` | Ranked at-risk cohort for a faculty member |
| `GET/POST` | `/interventions/` | Advisor intervention notes |
| `GET` | `/student/weekly-trends/` · `/student/my-risk/` | Student self-service |
| `POST` | `/student/chat/` | Scoped academic advisor chatbot |
| `GET` | `/system/status/` | Service + database health |

**Inference service** — `http://127.0.0.1:8001`

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/predict` | Weekly sequence → risk level, confidence, top factors |
| `GET` | `/models/benchmark` | Stored benchmark results |
| `GET` | `/health` | Model load status |

<details>
<summary><b>Example prediction request</b></summary>

```json
POST /predict
{
  "weekly_data": [
    {
      "week_number": 1,
      "attendance_rate_this_week": 0.95,
      "cumulative_attendance_rate": 0.95,
      "assignment_submitted": 1,
      "cumulative_avg_score": 78.0
    }
  ]
}
```

</details>

---

## 📊 Benchmark results

Evaluated on identical held-out test splits from the synthetic 16-week cohort:

| Model | Accuracy | Strength |
|---|---|---|
| **XGBoost** (static aggregates) | ~99–100% | Ceiling performance — but only with full end-of-semester features |
| **Sequential Attention-LSTM** ⭐ | ~97–98% | **Early detection from Week 4–8**, plus per-factor explanations |
| Logistic regression | — | Fast, interpretable linear baseline |
| Rule-based thresholds | ~85–88% | Zero-training heuristic; misses gradual and sudden trends alike |

The LSTM trades a sliver of end-of-term accuracy for the thing that actually matters: knowing early enough to do something about it.

---

## ⚖️ Responsible use

CampusFlow is an **early-intervention decision-support system**, not an automated grader.

- **No punitive automation.** Predictions must never drive failing, debarring, or withholding aid.
- **Right to human review.** Every flagged student gets a real conversation with a mentor first.
- **Context over correlation.** Attendance drops often mean illness, caregiving, transport or connectivity — not capability. Faculty can log that context directly against a prediction.
- **Synthetic demo data.** The prototype trains on archetype-based sequences inspired by OULAD; real deployment needs genuine longitudinal institutional data.

Full discussion in **[LIMITATIONS.md](LIMITATIONS.md)**.

---

## 🛠️ Tech stack

`Django` · `Django REST Framework` · `SimpleJWT` · `FastAPI` · `Uvicorn` · `PyTorch` · `XGBoost` · `scikit-learn` · `SHAP` · `pandas` · `NumPy` · `MongoDB` · `React 18` · `Vite` · `Tailwind CSS` · `Recharts` · `React Router` · `Lucide`

---

<div align="center">

Built to reach students **before** the transcript does.

</div>
