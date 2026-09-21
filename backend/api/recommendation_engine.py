"""
SmartEdu AI - Deterministic Recommendation Engine
Module: backend/api/recommendation_engine.py

Maps identified top risk factors and trajectory patterns to prescriptive, actionable
academic interventions for students and advisors.
"""

# Deterministic factor mapping table
DEFAULT_RECOMMENDATION_MAPPINGS = {
    "low_attendance_trend": (
        "Attendance has been declining over recent weeks. Attend classes regularly and "
        "reach out to your academic advisor if there is a scheduling constraint or personal emergency."
    ),
    "attendance_rate_this_week": (
        "Recent class absenteeism detected. Review the lecture slides and peer notes for the missed sessions."
    ),
    "cumulative_attendance_rate": (
        "Overall semester attendance is below the 75% institutional requirement. Prioritize regular attendance "
        "to avoid debarment from final examinations."
    ),
    "declining_score_trend": (
        "Scores have dropped significantly over recent assessments. Schedule a one-on-one consultation "
        "with your course faculty before the upcoming internal exam."
    ),
    "score_trend": (
        "Downward score trajectory observed. Form a peer study circle and practice prior semester checkpoint tests."
    ),
    "low_submission_rate": (
        "Multiple weekly assignment deadlines were missed. Submitting assignments on time is essential "
        "to secure continuous assessment credits."
    ),
    "assignment_submitted": (
        "Recent assignment was unsubmitted. Complete and submit even partial homework to earn partial evaluation marks."
    ),
    "cumulative_avg_score": (
        "Cumulative test scores are currently in the critical zone. Enroll in department remedial coaching workshops."
    ),
    "final_cum_avg_score": (
        "Cumulative score is below threshold. Attend doubt-clearing clinics and make use of campus tutoring resources."
    ),
    "high_volatility": (
        "Performance fluctuations indicate inconsistent revision habits. Set up a structured daily 2-hour study schedule."
    ),
    "early_disengagement": (
        "Significant disengagement observed across attendance and coursework. Immediate academic mentor intervention advised."
    )
}


def generate_recommendations_for_factors(top_factors):
    """
    Given a list of top factors (from SHAP, Attention, or Rule baseline),
    returns matched prescriptive recommendation strings.
    """
    recommendations = []
    seen = set()
    
    for factor in top_factors:
        feat_name = factor.get("feature", "") if isinstance(factor, dict) else str(factor)
        
        # Match against mapping table
        matched_text = None
        for key, rec_text in DEFAULT_RECOMMENDATION_MAPPINGS.items():
            if key in feat_name or feat_name in key:
                matched_text = rec_text
                break
                
        if not matched_text:
            matched_text = (
                f"Attention needed on '{factor.get('label', feat_name)}'. "
                "Consult your course instructor during office hours for tailored guidance."
            )
            
        if matched_text not in seen:
            seen.add(matched_text)
            recommendations.append({
                "factor_type": feat_name,
                "recommendation_text": matched_text
            })
            
    # Default recommendation if no factors identified (e.g. low risk)
    if not recommendations:
        recommendations.append({
            "factor_type": "consistent_progress",
            "recommendation_text": (
                "Excellent consistency across attendance and assessments! Keep up the momentum "
                "and explore advanced problem sets to achieve academic honors."
            )
        })
        
    return recommendations
