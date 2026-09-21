"""
SmartEdu AI - Database Demo Data Seeder
Module: backend/api/seed_demo_data.py

Seeds initial demo accounts, academic records, 16-week longitudinal snapshots,
and risk predictions. Syncs all records to the MongoDB Atlas cluster.
"""

import os
import sys
import django
import random
import numpy as np

# Setup django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartedu.settings')
django.setup()

from api.models import (
    User, Student, Faculty, Subject,
    Attendance, Marks, Assignment,
    WeeklySnapshot, RiskPrediction, Recommendation,
    InterventionNote
)
from api.recommendation_engine import generate_recommendations_for_factors
from api.mongo_sync import (
    sync_student_record,
    sync_prediction_record,
    sync_snapshot_record
)


def seed_database():
    print("[*] Starting SmartEdu AI Demo Database Seeding...")

    # 1. Create Core Users
    admin_user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@smartedu.edu", "role": "admin", "first_name": "System", "last_name": "Administrator"}
    )
    admin_user.set_password("Admin@123")
    admin_user.role = "admin"
    admin_user.save()

    fac_user, _ = User.objects.get_or_create(
        username="faculty",
        defaults={"email": "faculty@smartedu.edu", "role": "faculty", "first_name": "Dr. Rajesh", "last_name": "Kumar"}
    )
    fac_user.set_password("Faculty@123")
    fac_user.role = "faculty"
    fac_user.save()

    faculty_prof, _ = Faculty.objects.get_or_create(
        user=fac_user,
        defaults={"name": "Dr. Rajesh Kumar", "department": "Computer Science & Engineering"}
    )

    stud_user, _ = User.objects.get_or_create(
        username="student",
        defaults={"email": "student@smartedu.edu", "role": "student", "first_name": "Arjun", "last_name": "Verma"}
    )
    stud_user.set_password("Student@123")
    stud_user.role = "student"
    stud_user.save()

    primary_student, _ = Student.objects.get_or_create(
        user=stud_user,
        defaults={
            "name": "Arjun Verma",
            "roll_no": "23CS001",
            "class_name": "CSE-A",
            "section": "1",
            "prev_gpa": 7.85
        }
    )
    sync_student_record(primary_student)

    # 2. Create Subjects
    subjects_data = [
        {"code": "CS101", "name": "Data Structures & Algorithms", "class": "CSE-A"},
        {"code": "CS102", "name": "Database Management Systems", "class": "CSE-A"},
        {"code": "CS103", "name": "Artificial Intelligence & ML", "class": "CSE-B"},
        {"code": "MA101", "name": "Applied Mathematics & Statistics", "class": "CSE-A"}
    ]
    created_subjects = []
    for s_info in subjects_data:
        subj, _ = Subject.objects.get_or_create(
            code=s_info["code"],
            defaults={
                "name": s_info["name"],
                "class_name": s_info["class"],
                "faculty": faculty_prof
            }
        )
        created_subjects.append(subj)

    # 3. Seed Cohort Students
    DEMO_STUDENTS = [
        ("Bhavna Patel", "23CS002", "CSE-A", 8.9, "low", "high_performer"),
        ("Chetan Reddy", "23CS003", "CSE-A", 6.2, "high", "early_disengager"),
        ("Divya Iyer", "23CS004", "CSE-A", 7.4, "medium", "mid_semester_slump"),
        ("Ishaan Gupta", "23CS005", "CSE-A", 9.4, "low", "high_performer"),
        ("Kavya Nair", "23CS006", "CSE-A", 5.8, "high", "erratic_struggler"),
        ("Manish Singh", "23CS007", "CSE-A", 7.1, "medium", "late_recovery"),
        ("Neha Joshi", "23CS008", "CSE-A", 8.5, "low", "average_steady"),
        ("Pranav Pillai", "23CS009", "CSE-A", 6.0, "high", "early_disengager"),
        ("Riya Das", "23CS010", "CSE-A", 7.6, "medium", "average_steady"),
        ("Tarun Bose", "23CS011", "CSE-B", 8.8, "low", "high_performer"),
        ("Sneha Choudhury", "23CS012", "CSE-B", 6.4, "high", "mid_semester_slump")
    ]

    all_students = [primary_student]
    for name, roll, cls, gpa, risk_tier, arch in DEMO_STUDENTS:
        u_name = roll.lower()
        u, _ = User.objects.get_or_create(
            username=u_name,
            defaults={"email": f"{u_name}@smartedu.edu", "role": "student", "first_name": name}
        )
        u.set_password("Student@123")
        u.save()

        s_obj, _ = Student.objects.get_or_create(
            roll_no=roll,
            defaults={
                "user": u,
                "name": name,
                "class_name": cls,
                "section": "1",
                "prev_gpa": gpa
            }
        )
        sync_student_record(s_obj)
        all_students.append(s_obj)

    # 4. Generate 16-Week Snapshots and Academic Records
    print("[*] Generating 16 weeks of attendance, marks, assignments, and snapshots...")
    for s_obj in all_students:
        # Determine archetype behavior
        if "003" in s_obj.roll_no or "006" in s_obj.roll_no or "009" in s_obj.roll_no:
            risk_cat = "high"
            base_att = 0.62
            base_score = 42.0
        elif "004" in s_obj.roll_no or "007" in s_obj.roll_no or "010" in s_obj.roll_no or s_obj.roll_no == "23CS001":
            risk_cat = "medium"
            base_att = 0.74
            base_score = 61.0
        else:
            risk_cat = "low"
            base_att = 0.94
            base_score = 86.0

        for subj in created_subjects[:2]:  # CS101, CS102
            cum_att = 0
            cum_score = 0
            cum_sub = 0
            prev_s = base_score

            for w in range(1, 17):
                att_flag = 1 if np.random.rand() < base_att else 0
                cum_att += att_flag
                att_rate = round(cum_att / w, 3)

                sub_flag = 1 if np.random.rand() < min(0.95, base_att + 0.05) else 0
                cum_sub += sub_flag
                sub_rate = round(cum_sub / w, 3)

                current_score = round(float(np.clip(np.random.normal(base_score, 5.0), 15.0, 100.0)), 1)
                cum_score += current_score
                avg_score = round(cum_score / w, 1)

                trend = round(current_score - prev_s, 1)
                prev_s = current_score

                # Attendance entry
                Attendance.objects.get_or_create(
                    student=s_obj,
                    subject=subj,
                    week_number=w,
                    defaults={"status": "present" if att_flag == 1 else "absent"}
                )

                # Assignment entry
                Assignment.objects.get_or_create(
                    student=s_obj,
                    subject=subj,
                    week_number=w,
                    defaults={
                        "submitted": bool(sub_flag == 1),
                        "score": current_score if sub_flag == 1 else 0.0,
                        "max_score": 100.0
                    }
                )

                # Marks entry for internal checkpoints
                if w in [4, 8, 12, 16]:
                    chk_name = f"Checkpoint W{w}"
                    Marks.objects.get_or_create(
                        student=s_obj,
                        subject=subj,
                        checkpoint=chk_name,
                        week_number=w,
                        defaults={"score": current_score, "max_score": 100.0}
                    )

                # WeeklySnapshot entry
                snap, _ = WeeklySnapshot.objects.update_or_create(
                    student=s_obj,
                    subject=subj,
                    week_number=w,
                    defaults={
                        "attendance_rate": att_rate,
                        "avg_score_so_far": avg_score,
                        "assignment_submission_rate": sub_rate,
                        "marks_trend": trend
                    }
                )
                sync_snapshot_record(snap)

            # Generate RiskPrediction for this student & subject
            # Rotate model_used for demo visibility
            models_cycle = ["dl", "ml", "rule"]
            chosen_model = models_cycle[s_obj.id % 3]

            if risk_cat == "high":
                conf = 0.94
                top_f = [
                    {"feature": "cumulative_attendance_rate", "label": "Severe attendance deficit (< 65%)", "impact_score": 0.52},
                    {"feature": "declining_score_trend", "label": "Steep score drop after midterm tests", "impact_score": 0.44},
                    {"feature": "low_submission_rate", "label": "Multiple missing weekly assignments", "impact_score": 0.38}
                ]
            elif risk_cat == "medium":
                conf = 0.86
                top_f = [
                    {"feature": "score_trend", "label": "Inconsistent performance across recent weeks", "impact_score": 0.38},
                    {"feature": "cumulative_attendance_rate", "label": "Attendance borderline near 75% threshold", "impact_score": 0.34}
                ]
            else:
                conf = 0.96
                top_f = [
                    {"feature": "cumulative_attendance_rate", "label": "Consistently high class attendance (94%)", "impact_score": 0.12},
                    {"feature": "cumulative_avg_score", "label": "Strong continuous evaluation average (86%)", "impact_score": 0.10}
                ]

            pred, _ = RiskPrediction.objects.update_or_create(
                student=s_obj,
                subject=subj,
                checkpoint="Week 16",
                defaults={
                    "model_used": chosen_model,
                    "risk_level": risk_cat,
                    "confidence_score": conf,
                    "top_factors": top_f
                }
            )
            sync_prediction_record(pred)

            # Generate and save matched recommendations
            recs = generate_recommendations_for_factors(top_f)
            Recommendation.objects.filter(risk_prediction=pred).delete()
            for r_item in recs:
                Recommendation.objects.create(
                    risk_prediction=pred,
                    factor_type=r_item["factor_type"],
                    recommendation_text=r_item["recommendation_text"]
                )

    # 5. Add Intervention Note for Demo
    InterventionNote.objects.get_or_create(
        student=primary_student,
        faculty=faculty_prof,
        defaults={
            "note": "Met with student Arjun Verma regarding DBMS score slump in Week 8. Advised to attend Friday doubt clinics."
        }
    )

    print("[+] Successfully seeded SmartEdu AI database and synced records to MongoDB Atlas!")


if __name__ == "__main__":
    seed_database()
