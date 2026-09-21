"""
SmartEdu AI - Scoped Student Academic Advisor Chatbot
Module: backend/api/chatbot.py

Strictly scoped to explaining a student's own risk predictions, weekly sequence trajectory,
and personalized recommendations. Strictly rejects general tutoring or off-topic queries.
Logs conversations to MongoDB Atlas.
"""

import os
import re
import json
import logging
from api.mongo_sync import log_chat_to_atlas

logger = logging.getLogger(__name__)

OFF_TOPIC_PATTERNS = [
    r"\b(write a python code|solve this equation|who is|what is the capital|recipe|joke|poem|story|movie|weather|translate|essay)\b",
    r"\b(write a script|hack|debug this code|c\+\+|javascript tutorial|html code)\b"
]


def is_off_topic(query):
    query_lower = query.lower()
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    return False


def build_student_context_prompt(student, predictions, snapshots):
    """
    Constructs rich, factual academic context for the student.
    """
    lines = [
        f"STUDENT PROFILE:",
        f"- Name: {student.name}",
        f"- Roll No: {student.roll_no}",
        f"- Class: {student.class_name} Section {student.section}",
        f"- Prior GPA: {student.prev_gpa}/10.0\n",
        f"CURRENT ACADEMIC RISK STATUS:"
    ]
    
    if not predictions:
        lines.append("- No risk predictions recorded yet.")
    else:
        for p in predictions:
            factors_str = ", ".join([f.get("label", f.get("feature", "")) for f in p.top_factors[:3]]) if p.top_factors else "None"
            lines.append(
                f"- Subject: {p.subject.name} | Risk Level: {p.risk_level.upper()} "
                f"| Confidence: {p.confidence_score * 100:.1f}% | Model: {p.model_used.upper()} "
                f"| Top Factors: {factors_str}"
            )
            
    lines.append("\nRECENT WEEKLY TRAJECTORY SNAPSHOTS (LAST 4 WEEKS):")
    if not snapshots:
        lines.append("- No weekly snapshots recorded.")
    else:
        for s in snapshots[-6:]:
            lines.append(
                f"- Week {s.week_number} [{s.subject.code}]: Attendance={s.attendance_rate * 100:.0f}%, "
                f"Avg Score={s.avg_score_so_far:.1f}%, Submissions={s.assignment_submission_rate * 100:.0f}%, "
                f"Trend={s.marks_trend:+.1f}"
            )
            
    return "\n".join(lines)


def generate_scoped_response(student, query, predictions, snapshots):
    """
    Generates response strictly grounded in student's academic records.
    """
    # Guardrail check
    if is_off_topic(query):
        reply = (
            "I am the SmartEdu AI Academic Performance Advisor. My role is strictly scoped to helping "
            "you understand your personal academic performance, risk factors, attendance records, and course "
            "recommendations. I cannot assist with general programming, tutoring, or off-topic questions. "
            "Feel free to ask questions such as:\n"
            "• 'Why was I flagged as High/Medium risk?'\n"
            "• 'What changed in my performance over the last month?'\n"
            "• 'How is my attendance in Data Structures?'\n"
            "• 'What steps should I take to improve my standing?'"
        )
        log_chat_to_atlas(student.id, query, reply, "Blocked: Off-Topic Guardrail")
        return reply

    query_lower = query.lower()
    
    # 1. Inquiries about why flagged / risk factors
    if any(w in query_lower for w in ["why", "flagged", "risk", "high", "medium", "level", "factor"]):
        if not predictions:
            reply = "You currently have no active risk flags. Your records indicate normal academic progression."
        else:
            primary_p = predictions[0]
            factors = primary_p.top_factors
            factor_descriptions = []
            if factors:
                for f in factors:
                    label = f.get("label", f.get("feature", "Academic metric"))
                    factor_descriptions.append(f"• {label}")
                factors_joined = "\n".join(factor_descriptions)
            else:
                factors_joined = "• Maintained acceptable attendance and score thresholds."
                
            reply = (
                f"Based on your performance data, you have been categorized as **{primary_p.risk_level.upper()} RISK** "
                f"in **{primary_p.subject.name}** with **{primary_p.confidence_score * 100:.1f}% confidence** "
                f"evaluated using the **{primary_p.model_used.upper()}** sequence model.\n\n"
                f"The key contributing factors identified from your weekly trajectory are:\n{factors_joined}\n\n"
                f"**Recommended Action:** Consult the recommendations tab on your dashboard or schedule time with your faculty mentor."
            )
        log_chat_to_atlas(student.id, query, reply, "Answered: Risk Explanation")
        return reply

    # 2. Inquiries about trends / changes / past weeks
    if any(w in query_lower for w in ["change", "trend", "month", "last week", "weeks", "dropped", "improved"]):
        if len(snapshots) < 2:
            reply = "There are not enough weekly snapshots recorded yet to compute a multi-week trajectory."
        else:
            recent = snapshots[-1]
            prior = snapshots[0]
            att_delta = (recent.attendance_rate - prior.attendance_rate) * 100
            score_delta = recent.avg_score_so_far - prior.avg_score_so_far
            
            direction_att = "improved" if att_delta >= 0 else "declined"
            direction_score = "increased" if score_delta >= 0 else "dropped"
            
            reply = (
                f"Comparing Week {prior.week_number} to Week {recent.week_number} in your courses:\n"
                f"• Attendance: {direction_att} by {abs(att_delta):.1f}% (current: {recent.attendance_rate * 100:.0f}%)\n"
                f"• Cumulative Average Score: {direction_score} by {abs(score_delta):.1f} points (current: {recent.avg_score_so_far:.1f}%)\n"
                f"• Assignment Submission Rate: {recent.assignment_submission_rate * 100:.0f}%\n\n"
                f"{'Your weekly trajectory shows positive recovery!' if score_delta >= 0 and att_delta >= 0 else 'Your metrics indicate recent downward pressure on your grades. Focus on upcoming assignment deadlines!'}"
            )
        log_chat_to_atlas(student.id, query, reply, "Answered: Trend Trajectory")
        return reply

    # 3. Attendance specific inquiries
    if any(w in query_lower for w in ["attendance", "present", "absent", "classes"]):
        if not snapshots:
            reply = "No attendance snapshots found for your profile."
        else:
            latest = snapshots[-1]
            pct = latest.attendance_rate * 100
            status_text = "Safe (Above 75%)" if pct >= 75 else "⚠️ Critical (Below 75% Requirement)"
            reply = (
                f"Your current cumulative attendance is **{pct:.1f}%** ({status_text}).\n"
                f"Institutional guidelines require at least 75% attendance to qualify for semester examinations. "
                f"{'Keep attending all lectures!' if pct >= 75 else 'You should attend all upcoming classes to restore your percentage above 75%.'}"
            )
        log_chat_to_atlas(student.id, query, reply, "Answered: Attendance Inquiries")
        return reply

    # 4. Improvement / advice inquiries
    if any(w in query_lower for w in ["improve", "help", "better", "pass", "advice", "guidance", "recommendation"]):
        reply = (
            f"Here is your personalized SmartEdu action plan for {student.name}:\n"
            f"1. **Attendance Recovery**: Target 100% attendance over the next 3 weeks to raise your cumulative rate.\n"
            f"2. **Assignment Submissions**: Submit all pending weekly assignments to guarantee continuous assessment points.\n"
            f"3. **Faculty Consultation**: Attend office hours with your subject instructor to review weak exam concepts.\n"
            f"4. **Remedial Practice**: Work through the practice problem sets available in your LMS portal."
        )
        log_chat_to_atlas(student.id, query, reply, "Answered: Improvement Plan")
        return reply

    # General fallback for student academic questions
    context = build_student_context_prompt(student, predictions, snapshots)
    reply = (
        f"Here is a summary of your academic status for **{student.name}** ({student.roll_no}):\n"
        f"• Class: {student.class_name} | Prior GPA: {student.prev_gpa}/10.0\n"
        f"• Active Subjects Monitored: {len(predictions)}\n"
        f"You can ask me specific questions like 'Why am I at risk?', 'How did my attendance change?', or 'What should I do to improve?'"
    )
    log_chat_to_atlas(student.id, query, reply, "Answered: General Profile Status")
    return reply
