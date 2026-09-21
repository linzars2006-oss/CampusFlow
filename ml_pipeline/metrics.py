"""
SmartEdu AI - Native Metrics & Preprocessing Utilities
Module: ml_pipeline/metrics.py

Provides zero-dependency (pure NumPy & Python standard library) implementations of:
- Confusion Matrix
- Multi-Class Macro Precision, Recall, and F1-Score
- Standard Scaler
- Stratified Student-Level Group Splitter
"""

import numpy as np


class SimpleStandardScaler:
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        X = np.asarray(X, dtype=np.float32)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        # Avoid division by zero
        self.scale_[self.scale_ == 0.0] = 1.0
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=np.float32)
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def compute_confusion_matrix(y_true, y_pred, num_classes=3):
    """
    Computes confusion matrix where rows are True and columns are Predicted.
    """
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < num_classes and 0 <= p < num_classes:
            cm[int(t), int(p)] += 1
    return cm


def compute_classification_metrics(y_true, y_pred, num_classes=3):
    """
    Computes Accuracy, Macro-Precision, Macro-Recall, and Macro-F1.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    total_samples = len(y_true)
    
    if total_samples == 0:
        return {"Accuracy": 0.0, "Macro-Precision": 0.0, "Macro-Recall": 0.0, "Macro-F1": 0.0, "Confusion_Matrix": []}
        
    accuracy = float(np.mean(y_true == y_pred))
    cm = compute_confusion_matrix(y_true, y_pred, num_classes=num_classes)
    
    precisions = []
    recalls = []
    f1s = []
    
    for c in range(num_classes):
        tp = cm[c, c]
        fp = np.sum(cm[:, c]) - tp
        fn = np.sum(cm[c, :]) - tp
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        
    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))
    
    return {
        "Accuracy": round(accuracy, 4),
        "Macro-Precision": round(macro_prec, 4),
        "Macro-Recall": round(macro_rec, 4),
        "Macro-F1": round(macro_f1, 4),
        "Per-Class-F1": [round(f, 4) for f in f1s],
        "Confusion_Matrix": cm.tolist()
    }


def stratified_student_split(student_ids, y, test_ratio=0.20, random_seed=42):
    """
    Performs leak-free student-level stratified split using pure NumPy.
    """
    np.random.seed(random_seed)
    unique_students = np.unique(student_ids)
    
    # Identify predominant label per student
    student_labels = {}
    for sid in unique_students:
        s_y = y[student_ids == sid]
        counts = np.bincount(s_y, minlength=3)
        student_labels[sid] = int(np.argmax(counts))
        
    # Group students by predominant label
    class_to_students = {0: [], 1: [], 2: []}
    for sid, lbl in student_labels.items():
        class_to_students[lbl].append(sid)
        
    train_sids = set()
    test_sids = set()
    
    for lbl, s_list in class_to_students.items():
        s_arr = np.array(s_list)
        np.random.shuffle(s_arr)
        n_test = max(1, int(len(s_arr) * test_ratio))
        test_sids.update(s_arr[:n_test])
        train_sids.update(s_arr[n_test:])
        
    train_mask = np.isin(student_ids, list(train_sids))
    test_mask = np.isin(student_ids, list(test_sids))
    
    return train_mask, test_mask
