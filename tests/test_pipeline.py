"""
SmartEdu AI - Pipeline & Logic Unit Tests
Module: tests/test_pipeline.py

Verifies:
1. Attendance & marks longitudinal aggregation logic
2. Rule-based classifier deterministic heuristics
3. Sequence padding, masking, and feature normalization for LSTM
4. Recommendation engine factor mapping
5. Scoped chatbot guardrails
"""

import os
import sys
import unittest
import numpy as np

# Ensure root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

ML_PIPELINE_DIR = os.path.join(BASE_DIR, "ml_pipeline")
if ML_PIPELINE_DIR not in sys.path:
    sys.path.insert(0, ML_PIPELINE_DIR)

from ml_pipeline.models import RuleBasedClassifier
from ml_pipeline.feature_engineering import extract_student_subject_sequences, extract_aggregated_static_features
from ml_pipeline.metrics import compute_classification_metrics, SimpleStandardScaler
from backend.api.recommendation_engine import generate_recommendations_for_factors
from backend.api.chatbot import is_off_topic


class TestSmartEduPipeline(unittest.TestCase):

    def setUp(self):
        self.rule_classifier = RuleBasedClassifier()

    def test_rule_based_classifier_thresholds(self):
        """
        Verify Rule-Based baseline logic:
        - High risk: attendance < 75% AND score < 40%
        - Medium risk: attendance < 85% OR score < 50%
        - Low risk: otherwise
        """
        # Test Case 1: High Risk
        high_risk_record = [{"cumulative_attendance_rate": 0.65, "cumulative_avg_score": 35.0}]
        pred_high = self.rule_classifier.predict(high_risk_record)[0]
        self.assertEqual(pred_high, 2, "Expected class 2 (High Risk)")

        # Test Case 2: Medium Risk (low attendance only)
        med_risk_att = [{"cumulative_attendance_rate": 0.78, "cumulative_avg_score": 70.0}]
        pred_med1 = self.rule_classifier.predict(med_risk_att)[0]
        self.assertEqual(pred_med1, 1, "Expected class 1 (Medium Risk)")

        # Test Case 3: Medium Risk (low score only)
        med_risk_score = [{"cumulative_attendance_rate": 0.90, "cumulative_avg_score": 45.0}]
        pred_med2 = self.rule_classifier.predict(med_risk_score)[0]
        self.assertEqual(pred_med2, 1, "Expected class 1 (Medium Risk)")

        # Test Case 4: Low Risk
        low_risk_record = [{"cumulative_attendance_rate": 0.92, "cumulative_avg_score": 82.0}]
        pred_low = self.rule_classifier.predict(low_risk_record)[0]
        self.assertEqual(pred_low, 0, "Expected class 0 (Low Risk)")

    def test_sequence_padding_and_masking(self):
        """
        Verify sequence padding to 16 weeks, boolean masking, and feature normalization.
        """
        sample_records = [
            {
                "student_id": 99,
                "subject_id": "CS101",
                "week_number": w,
                "attendance_rate_this_week": 1.0,
                "cumulative_attendance_rate": 1.0,
                "assignment_submitted": 1.0,
                "cumulative_avg_score": 80.0,
                "score_trend": 2.0,
                "risk_label": 0,
                "risk_level": "Low"
            }
            for w in range(1, 9)  # Only 8 weeks (shorter than max 16)
        ]

        X_seq, masks, keys, y, s_ids = extract_student_subject_sequences(sample_records, max_timesteps=16)

        # Check shapes
        self.assertEqual(X_seq.shape, (1, 16, 5), "Should pad to [1, 16, 5]")
        self.assertEqual(masks.shape, (1, 16), "Mask shape should be [1, 16]")

        # Check mask values: first 8 True, remaining 8 False
        self.assertTrue(np.all(masks[0, :8] == True))
        self.assertTrue(np.all(masks[0, 8:] == False))

        # Check padding values: remaining 8 timesteps should be all zeros
        self.assertTrue(np.all(X_seq[0, 8:, :] == 0.0))

        # Check normalized cumulative_avg_score (index 3 in feature matrix): 80 / 100 = 0.8
        self.assertAlmostEqual(X_seq[0, 0, 3], 0.8, places=3)

    def test_attendance_and_marks_aggregation(self):
        """
        Verify static feature extraction aggregation across weeks.
        """
        records = [
            {
                "student_id": 101,
                "subject_id": "CS101",
                "week_number": 1,
                "attendance_rate_this_week": 1.0,
                "cumulative_attendance_rate": 1.0,
                "assignment_submitted": 1.0,
                "assignment_submission_rate": 1.0,
                "quiz_score": 70.0,
                "cumulative_avg_score": 70.0,
                "score_trend": 0.0,
                "risk_label": 0,
                "risk_level": "Low"
            },
            {
                "student_id": 101,
                "subject_id": "CS101",
                "week_number": 2,
                "attendance_rate_this_week": 0.0,
                "cumulative_attendance_rate": 0.5,
                "assignment_submitted": 1.0,
                "assignment_submission_rate": 1.0,
                "quiz_score": 80.0,
                "cumulative_avg_score": 75.0,
                "score_trend": 10.0,
                "risk_label": 0,
                "risk_level": "Low"
            }
        ]

        X_stat, feat_names, keys, y, s_ids = extract_aggregated_static_features(records)
        self.assertEqual(len(X_stat), 1)
        # Final attendance should be 0.5
        self.assertAlmostEqual(X_stat[0, 0], 0.5, places=2)
        # Final avg score should be 75.0
        self.assertAlmostEqual(X_stat[0, 1], 75.0, places=2)

    def test_recommendation_engine_mapping(self):
        """
        Verify deterministic recommendation engine maps factors to guidance.
        """
        factors = [
            {"feature": "low_attendance_trend", "label": "Declining Attendance"},
            {"feature": "declining_score_trend", "label": "Dropped Scores"}
        ]
        recs = generate_recommendations_for_factors(factors)
        self.assertEqual(len(recs), 2)
        self.assertIn("Attendance has been declining", recs[0]["recommendation_text"])
        self.assertIn("Scores have dropped", recs[1]["recommendation_text"])

    def test_scoped_chatbot_guardrail(self):
        """
        Verify off-topic queries are detected and blocked by guardrails.
        """
        off_topic_query = "Can you write a python code to scrape a website?"
        self.assertTrue(is_off_topic(off_topic_query))

        in_scope_query = "Why was I flagged as high risk in Data Structures?"
        self.assertFalse(is_off_topic(in_scope_query))

        trend_query = "How has my attendance changed since week 4?"
        self.assertFalse(is_off_topic(trend_query))


if __name__ == "__main__":
    unittest.main()
