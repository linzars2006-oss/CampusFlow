"""
SmartEdu AI - Data Generation Pipeline
Module: generate_dataset.py

Generates realistic longitudinal weekly student engagement, attendance, and assessment
sequences across 16 weeks, modeling academic archetypes (consistent, slumping, disengaging,
recovering, and erratic).

NOTICE:
This script produces synthetic proxy data specifically engineered for sequence modeling
and educational early warning systems. Real institutional deployment requires streaming
or historical data logged by LMS/SMS systems over actual academic semesters.
"""

import os
import csv
import json
import random
import numpy as np

# Set deterministic seed for reproducibility
np.random.seed(42)
random.seed(42)

SUBJECTS = [
    {"id": "CS101", "name": "Data Structures & Algorithms", "class": "CSE-A"},
    {"id": "CS102", "name": "Database Management Systems", "class": "CSE-A"},
    {"id": "CS103", "name": "Artificial Intelligence & ML", "class": "CSE-B"},
    {"id": "MA101", "name": "Applied Mathematics & Statistics", "class": "CSE-A"},
    {"id": "EC101", "name": "Digital Logic & Microprocessors", "class": "CSE-B"}
]

ARCHETYPES = [
    {"type": "high_performer", "weight": 0.35, "base_att": 0.94, "base_score": 85, "decay": 0.0},
    {"type": "average_steady", "weight": 0.30, "base_att": 0.82, "base_score": 68, "decay": 0.0},
    {"type": "mid_semester_slump", "weight": 0.12, "base_att": 0.80, "base_score": 72, "slump_weeks": (6, 11)},
    {"type": "early_disengager", "weight": 0.10, "base_att": 0.70, "base_score": 55, "decay": -0.035},
    {"type": "late_recovery", "weight": 0.08, "base_att": 0.65, "base_score": 52, "recover_week": 9},
    {"type": "erratic_struggler", "weight": 0.05, "base_att": 0.60, "base_score": 45, "noise": 18}
]

FIRST_NAMES = ["Aarav", "Aditi", "Ananya", "Arjun", "Bhavna", "Chetan", "Deepak", "Divya",
               "Harish", "Ishaan", "Kavya", "Kiran", "Lakshmi", "Manish", "Meera", "Neha",
               "Nikhil", "Pooja", "Pranav", "Priya", "Rahul", "Riya", "Rohan", "Sanjay",
               "Sneha", "Tarun", "Varun", "Vikas", "Yash", "Zoya"]

LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Kulkarni", "Gupta",
              "Singh", "Mehta", "Bose", "Choudhury", "Pillai", "Deshmukh", "Joshi", "Das"]


def generate_student_cohort(num_students=400, num_weeks=16):
    """
    Generates student cohort longitudinal trajectory data over `num_weeks`.
    """
    students = []
    weekly_records = []
    labels_records = []
    
    archetype_names = [a["type"] for a in ARCHETYPES]
    archetype_weights = [a["weight"] for a in ARCHETYPES]
    archetype_map = {a["type"]: a for a in ARCHETYPES}
    
    for s_idx in range(1, num_students + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        roll_no = f"23CS{s_idx:03d}"
        assigned_class = "CSE-A" if s_idx % 2 == 1 else "CSE-B"
        section = "1" if s_idx % 4 in [1, 2] else "2"
        archetype_type = np.random.choice(archetype_names, p=archetype_weights)
        arch = archetype_map[archetype_type]
        
        base_score = arch.get("base_score", 70)
        prev_gpa = round(float(np.clip(np.random.normal(loc=base_score / 10.0, scale=0.5), 4.0, 9.8)), 2)
        
        student_info = {
            "student_id": s_idx,
            "roll_no": roll_no,
            "name": full_name,
            "class_name": assigned_class,
            "section": section,
            "prev_gpa": prev_gpa,
            "archetype": archetype_type,
            "email": f"{first.lower()}.{last.lower()}{s_idx}@smartedu.edu"
        }
        students.append(student_info)
        
        student_subjects = [s for s in SUBJECTS if s["class"] == assigned_class]
        
        for subj in student_subjects:
            subj_id = subj["id"]
            subj_name = subj["name"]
            
            cum_att_count = 0
            cum_score_sum = 0
            cum_score_count = 0
            cum_assignments_submitted = 0
            prev_week_score = None
            
            subj_weeks = []
            
            for week in range(1, num_weeks + 1):
                att_prob = arch.get("base_att", 0.85)
                score_center = arch.get("base_score", 70)
                
                if arch["type"] == "early_disengager":
                    att_prob = max(0.20, att_prob + arch["decay"] * week)
                    score_center = max(25, score_center + (arch["decay"] * 100 * week * 0.8))
                elif arch["type"] == "mid_semester_slump":
                    start_w, end_w = arch["slump_weeks"]
                    if start_w <= week <= end_w:
                        att_prob = max(0.35, att_prob - 0.35)
                        score_center = max(35, score_center - 28)
                elif arch["type"] == "late_recovery":
                    if week >= arch["recover_week"]:
                        att_prob = min(0.92, att_prob + 0.25)
                        score_center = min(82, score_center + 25)
                elif arch["type"] == "erratic_struggler":
                    noise_mag = arch.get("noise", 15)
                    att_prob = np.clip(att_prob + np.random.uniform(-0.3, 0.2), 0.2, 0.95)
                    score_center = np.clip(score_center + np.random.normal(0, noise_mag), 20, 85)
                
                week_att_flag = 1 if np.random.rand() < att_prob else 0
                cum_att_count += week_att_flag
                cum_att_rate = round(cum_att_count / week, 3)
                
                sub_prob = np.clip(att_prob + 0.05, 0.1, 0.98)
                is_submitted = bool(np.random.rand() < sub_prob)
                if is_submitted:
                    cum_assignments_submitted += 1
                    assgn_score = round(float(np.clip(np.random.normal(score_center, 6.0), 10.0, 100.0)), 1)
                else:
                    assgn_score = 0.0
                
                assignment_sub_rate = round(cum_assignments_submitted / week, 3)
                
                if week_att_flag == 1 or np.random.rand() < 0.4:
                    quiz_score = round(float(np.clip(np.random.normal(score_center, 7.5), 15.0, 100.0)), 1)
                    cum_score_sum += quiz_score
                    cum_score_count += 1
                else:
                    quiz_score = 0.0
                
                cum_avg_score = round(cum_score_sum / max(1, cum_score_count), 2)
                
                current_score = quiz_score if quiz_score > 0 else (assgn_score if is_submitted else cum_avg_score)
                if prev_week_score is not None:
                    score_trend = round(current_score - prev_week_score, 2)
                else:
                    score_trend = 0.0
                prev_week_score = current_score
                
                record = {
                    "student_id": s_idx,
                    "roll_no": roll_no,
                    "student_name": full_name,
                    "subject_id": subj_id,
                    "subject_name": subj_name,
                    "class_name": assigned_class,
                    "week_number": week,
                    "attendance_status": "present" if week_att_flag == 1 else "absent",
                    "attendance_rate_this_week": float(week_att_flag),
                    "cumulative_attendance_rate": cum_att_rate,
                    "assignment_submitted": 1 if is_submitted else 0,
                    "assignment_score": assgn_score,
                    "assignment_submission_rate": assignment_sub_rate,
                    "quiz_score": quiz_score,
                    "cumulative_avg_score": cum_avg_score,
                    "score_trend": score_trend
                }
                subj_weeks.append(record)
                
            # Final week outcome & risk label
            final_w = subj_weeks[-1]
            final_att = final_w["cumulative_attendance_rate"]
            final_score = final_w["cumulative_avg_score"]
            final_sub = final_w["assignment_submission_rate"]
            
            if final_score < 45.0 or (final_att < 0.70 and final_score < 55.0) or final_sub < 0.50:
                risk_label = 2  # High Risk
                risk_level = "High"
            elif final_score < 62.0 or final_att < 0.78 or final_sub < 0.72:
                risk_label = 1  # Medium Risk
                risk_level = "Medium"
            else:
                risk_label = 0  # Low Risk
                risk_level = "Low"
                
            for w_rec in subj_weeks:
                w_rec["risk_label"] = risk_label
                w_rec["risk_level"] = risk_level
                weekly_records.append(w_rec)
                
            labels_records.append({
                "student_id": s_idx,
                "subject_id": subj_id,
                "risk_label": risk_label,
                "risk_level": risk_level
            })
            
    return students, weekly_records, labels_records


def write_csv(filepath, dict_list):
    if not dict_list:
        return
    fieldnames = list(dict_list[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dict_list)


def save_dataset(output_dir="ml_pipeline/data"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating synthetic student longitudinal cohort dataset...")
    students, weekly_records, labels = generate_student_cohort(num_students=400, num_weeks=16)
    
    students_path = os.path.join(output_dir, "students_metadata.csv")
    weekly_path = os.path.join(output_dir, "weekly_student_records.csv")
    labels_path = os.path.join(output_dir, "student_subject_labels.csv")
    
    write_csv(students_path, students)
    write_csv(weekly_path, weekly_records)
    write_csv(labels_path, labels)
    
    print(f"[+] Successfully saved:")
    print(f"    - {students_path} ({len(students)} students)")
    print(f"    - {weekly_path} ({len(weekly_records)} weekly records)")
    print(f"    - {labels_path} ({len(labels)} student-subject outcomes)")
    
    counts = {}
    for item in labels:
        lvl = item["risk_level"]
        counts[lvl] = counts.get(lvl, 0) + 1
    print(f"[*] Label distribution across cohort: {counts}")
    return students_path, weekly_path, labels_path


if __name__ == "__main__":
    save_dataset()
