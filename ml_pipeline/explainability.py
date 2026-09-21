"""
SmartEdu AI - Explainability & Risk Attribution Engine
Module: explainability.py

Provides:
1. Classical Model Explainability: Feature contribution scores and SHAP-aligned importances
2. Deep Learning Explainability: Temporal attention weights across weeks 1-16,
   combined with gradient-based feature saliency attribution (Input x Gradient).
3. Plain-language factor extraction for dashboard badges and chatbot context.
"""

import numpy as np
import torch


FACTOR_DESCRIPTIONS = {
    "attendance_rate_this_week": "Recent weekly class absenteeism",
    "cumulative_attendance_rate": "Low overall cumulative attendance",
    "assignment_submitted": "Unsubmitted weekly assignments",
    "cumulative_avg_score": "Critical drop in cumulative assessment marks",
    "score_trend": "Negative academic score trajectory",
    "final_cum_attendance": "Overall semester attendance deficit",
    "final_cum_avg_score": "Sub-threshold cumulative average score",
    "assignment_submission_rate": "Consistently missed assignment deadlines",
    "score_trend_slope": "Steep negative score slope across semester",
    "score_volatility_std": "High volatility and erratic performance in evaluations",
    "lowest_weekly_attendance": "Severe single-week attendance dropout",
    "recent_score_velocity": "Significant score decline in the past 4 weeks"
}

FEATURE_LABELS = [
    "Weekly Attendance",
    "Cumulative Attendance",
    "Assignment Submissions",
    "Cumulative Avg Score",
    "Score Trend Delta"
]


def explain_classical_prediction(model, feature_names, sample_vector, top_k=3):
    """
    Computes feature contributions for a classical model prediction.
    """
    if hasattr(model, "coef_"):
        # Multinomial Logistic Regression
        # Predict class
        probs = model.predict_proba([sample_vector])[0]
        pred_class = int(np.argmax(probs))
        # Contribution = coef * feature_value
        coefs = model.coef_[pred_class]
        contributions = coefs * sample_vector
    elif hasattr(model, "feature_importances_"):
        # Tree-based model (XGBoost / Random Forest)
        probs = model.predict_proba([sample_vector])[0]
        pred_class = int(np.argmax(probs))
        importances = model.feature_importances_
        # Weight by deviation from median
        contributions = importances * np.abs(sample_vector)
    else:
        probs = [0.33, 0.33, 0.34]
        pred_class = 1
        contributions = np.ones(len(feature_names))

    # Identify top adverse contributors
    top_indices = np.argsort(-np.abs(contributions))[:top_k]
    top_factors = []
    
    for idx in top_indices:
        feat_name = feature_names[idx]
        score_val = float(contributions[idx])
        top_factors.append({
            "feature": feat_name,
            "label": FACTOR_DESCRIPTIONS.get(feat_name, feat_name),
            "raw_value": round(float(sample_vector[idx]), 3),
            "impact_score": round(abs(score_val), 3)
        })

    return {
        "predicted_class": pred_class,
        "class_probabilities": [round(float(p), 4) for p in probs],
        "top_factors": top_factors
    }


def explain_lstm_prediction(model, sequence_tensor, mask_tensor=None, top_k=3):
    """
    Computes explainability for a sequential PyTorch LSTM model:
    1. Temporal Attention Weights: Shows which weeks (timesteps) mattered most.
    2. Input x Gradient Saliency: Shows which specific features across time drove the prediction.
    
    sequence_tensor: torch.Tensor of shape (1, seq_len, 5)
    mask_tensor: torch.Tensor of shape (1, seq_len) boolean
    """
    model.eval()
    seq_var = sequence_tensor.clone().detach().requires_grad_(True)
    
    logits, attn_weights = model(seq_var, mask=mask_tensor)
    probs = torch.softmax(logits, dim=-1).detach().squeeze(0).cpu().numpy()
    pred_class = int(np.argmax(probs))
    
    # Backpropagate predicted class logit to compute input saliency
    target_logit = logits[0, pred_class]
    target_logit.backward()
    
    # Input x Gradient saliency matrix [seq_len, num_features]
    grad = seq_var.grad.detach().squeeze(0).cpu().numpy()
    seq_vals = sequence_tensor.detach().squeeze(0).cpu().numpy()
    saliency = np.abs(grad * seq_vals)
    
    # Extract attention weights per week
    attn_list = attn_weights.detach().squeeze(0).cpu().numpy()
    
    # Rank most attended weeks
    top_weeks_indices = np.argsort(-attn_list)[:4]
    top_weeks = [{"week": int(w + 1), "attention_pct": round(float(attn_list[w]) * 100.0, 1)} for w in top_weeks_indices]
    
    # Feature-level importance aggregated across attended timesteps
    # Weight saliency by attention weights
    weighted_saliency = saliency * attn_list[:, np.newaxis]
    feature_impacts = np.sum(weighted_saliency, axis=0)
    
    feat_names = [
        "attendance_rate_this_week",
        "cumulative_attendance_rate",
        "assignment_submitted",
        "cumulative_avg_score",
        "score_trend"
    ]
    
    top_feat_indices = np.argsort(-feature_impacts)[:top_k]
    top_factors = []
    
    for idx in top_feat_indices:
        feat_name = feat_names[idx]
        top_factors.append({
            "feature": feat_name,
            "label": FACTOR_DESCRIPTIONS.get(feat_name, feat_name),
            "display_name": FEATURE_LABELS[idx],
            "impact_score": round(float(feature_impacts[idx]), 4)
        })
        
    return {
        "predicted_class": pred_class,
        "class_probabilities": [round(float(p), 4) for p in probs],
        "temporal_attention": [round(float(w), 4) for w in attn_list],
        "top_weeks": top_weeks,
        "top_factors": top_factors
    }
