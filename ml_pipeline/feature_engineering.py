"""
SmartEdu AI - Feature Engineering & Sequence Preprocessing
Module: ml_pipeline/feature_engineering.py

Prepares both:
1. Sequential feature matrices (timesteps x features) for Deep Learning (LSTM / GRU) with sequence padding.
2. Aggregated static feature vectors for Classical ML (Logistic Regression, XGBoost).
3. Rule-based evaluation snapshot extraction.
"""

import csv
import numpy as np

SEQUENCE_FEATURE_COLS = [
    "attendance_rate_this_week",
    "cumulative_attendance_rate",
    "assignment_submitted",
    "cumulative_avg_score",
    "score_trend"
]

AGGREGATED_FEATURE_NAMES = [
    "final_cum_attendance",
    "final_cum_avg_score",
    "assignment_submission_rate",
    "score_trend_slope",
    "score_volatility_std",
    "lowest_weekly_attendance",
    "recent_score_velocity"
]


def load_weekly_csv(filepath):
    """
    Loads weekly student records using Python's standard csv module.
    """
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "student_id": int(row["student_id"]),
                "subject_id": row["subject_id"],
                "week_number": int(row["week_number"]),
                "attendance_rate_this_week": float(row["attendance_rate_this_week"]),
                "cumulative_attendance_rate": float(row["cumulative_attendance_rate"]),
                "assignment_submitted": float(row["assignment_submitted"]),
                "assignment_score": float(row.get("assignment_score", 0.0)),
                "assignment_submission_rate": float(row.get("assignment_submission_rate", 1.0)),
                "quiz_score": float(row.get("quiz_score", 0.0)),
                "cumulative_avg_score": float(row["cumulative_avg_score"]),
                "score_trend": float(row["score_trend"]),
                "risk_label": int(row["risk_label"]),
                "risk_level": row["risk_level"]
            })
    return records


def extract_student_subject_sequences(records, max_timesteps=16):
    """
    Groups weekly records by (student_id, subject_id), sorts by week_number,
    and returns:
      X_seq: [N, max_timesteps, 5]
      masks: [N, max_timesteps] boolean
      keys: list of (student_id, subject_id)
      y: np.ndarray of shape (N,) integer class labels (0, 1, 2)
      student_ids: np.ndarray of student ids
    """
    # Group by (student_id, subject_id)
    grouped = {}
    for r in records:
        key = (r["student_id"], r["subject_id"])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(r)
        
    X_list = []
    masks_list = []
    keys_list = []
    y_list = []
    student_id_list = []
    
    for (s_id, subj_id), rows in grouped.items():
        rows.sort(key=lambda x: x["week_number"])
        
        seq_values = []
        for r in rows:
            # Features:
            # 0: attendance_rate_this_week
            # 1: cumulative_attendance_rate
            # 2: assignment_submitted
            # 3: cumulative_avg_score (scaled 0-1)
            # 4: score_trend (scaled)
            seq_values.append([
                r["attendance_rate_this_week"],
                r["cumulative_attendance_rate"],
                r["assignment_submitted"],
                r["cumulative_avg_score"] / 100.0,
                r["score_trend"] / 50.0
            ])
            
        seq_arr = np.array(seq_values, dtype=np.float32)
        seq_len = len(seq_arr)
        
        padded = np.zeros((max_timesteps, 5), dtype=np.float32)
        mask = np.zeros(max_timesteps, dtype=bool)
        
        if seq_len >= max_timesteps:
            padded[:] = seq_arr[:max_timesteps]
            mask[:] = True
        else:
            padded[:seq_len] = seq_arr
            mask[:seq_len] = True
            
        X_list.append(padded)
        masks_list.append(mask)
        keys_list.append((s_id, subj_id))
        y_list.append(rows[-1]["risk_label"])
        student_id_list.append(s_id)
        
    return (
        np.array(X_list, dtype=np.float32),
        np.array(masks_list, dtype=bool),
        keys_list,
        np.array(y_list, dtype=np.int64),
        np.array(student_id_list, dtype=np.int64)
    )


def extract_aggregated_static_features(records):
    """
    Aggregates sequential weeks into a single static feature vector per (student_id, subject_id)
    used for classical ML (Logistic Regression, XGBoost).
    """
    grouped = {}
    for r in records:
        key = (r["student_id"], r["subject_id"])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(r)
        
    records_list = []
    keys_list = []
    y_list = []
    student_id_list = []
    
    for (s_id, subj_id), rows in grouped.items():
        rows.sort(key=lambda x: x["week_number"])
        final_row = rows[-1]
        
        cum_att = final_row["cumulative_attendance_rate"]
        cum_score = final_row["cumulative_avg_score"]
        sub_rate = final_row["assignment_submission_rate"]
        
        scores = [r["quiz_score"] for r in rows if r["quiz_score"] > 0]
        if len(scores) > 1:
            volatility = float(np.std(scores))
            slope = float((scores[-1] - scores[0]) / max(1, len(scores)))
        else:
            volatility = 0.0
            slope = 0.0
            
        min_att = float(min(r["attendance_rate_this_week"] for r in rows))
        
        if len(rows) >= 4:
            recent_vel = float(rows[-1]["cumulative_avg_score"] - rows[-4]["cumulative_avg_score"])
        else:
            recent_vel = float(rows[-1]["score_trend"])
            
        records_list.append([
            cum_att,
            cum_score,
            sub_rate,
            slope,
            volatility,
            min_att,
            recent_vel
        ])
        keys_list.append((s_id, subj_id))
        y_list.append(final_row["risk_label"])
        student_id_list.append(s_id)
        
    return (
        np.array(records_list, dtype=np.float32),
        AGGREGATED_FEATURE_NAMES,
        keys_list,
        np.array(y_list, dtype=np.int64),
        np.array(student_id_list, dtype=np.int64)
    )


def evaluate_rule_based_baseline(records, test_keys):
    """
    Model A: Rule-based baseline (no training required).
    Applied strictly using the LAST week's snapshot values for test instances.
    """
    lookup = {}
    for r in records:
        key = (r["student_id"], r["subject_id"])
        if key not in lookup or r["week_number"] > lookup[key]["week_number"]:
            lookup[key] = r
            
    predictions = []
    for key in test_keys:
        final_row = lookup.get(key)
        if final_row is None:
            predictions.append(1)
            continue
            
        cum_att_pct = final_row["cumulative_attendance_rate"] * 100.0
        cum_score = final_row["cumulative_avg_score"]
        
        if cum_att_pct < 75.0 and cum_score < 40.0:
            pred = 2  # High Risk
        elif cum_att_pct < 85.0 or cum_score < 50.0:
            pred = 1  # Medium Risk
        else:
            pred = 0  # Low Risk
            
        predictions.append(pred)
        
    return np.array(predictions, dtype=np.int64)
