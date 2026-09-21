"""
SmartEdu AI - Model Architectures & Implementations
Module: ml_pipeline/models.py

Contains:
1. Model A: Rule-Based Classifier
2. Model B1: Multinomial Logistic Regression (PyTorch Linear Classifier with Balanced Cross-Entropy)
3. Model B2: XGBoost Gradient Boosted Trees Classifier
4. Model C: PyTorch Sequential LSTM with Masking, Temporal Attention, and Saliency Attribution
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


# -------------------------------------------------------------------------
# Model A: Rule-Based Classifier
# -------------------------------------------------------------------------
class RuleBasedClassifier:
    """
    Deterministic rule-based baseline using snapshot thresholds:
      IF cumulative_attendance < 75% AND cumulative_avg_score < 40% -> High Risk (2)
      ELIF cumulative_attendance < 85% OR cumulative_avg_score < 50% -> Medium Risk (1)
      ELSE -> Low Risk (0)
    """
    def predict(self, snapshot_records):
        preds = []
        for rec in snapshot_records:
            att = rec.get("cumulative_attendance_rate", 1.0) * 100.0
            score = rec.get("cumulative_avg_score", 100.0)
            
            if att < 75.0 and score < 40.0:
                preds.append(2)  # High Risk
            elif att < 85.0 or score < 50.0:
                preds.append(1)  # Medium Risk
            else:
                preds.append(0)  # Low Risk
        return np.array(preds, dtype=np.int64)


# -------------------------------------------------------------------------
# Model B1: Multinomial Logistic Regression (PyTorch LBFGS/Adam)
# -------------------------------------------------------------------------
class PyTorchLogisticRegression(nn.Module):
    def __init__(self, input_dim=7, num_classes=3):
        super().__init__()
        self.linear = nn.Linear(input_dim, num_classes)

    def forward(self, x):
        return self.linear(x)

    def predict(self, x_np):
        self.eval()
        with torch.no_grad():
            x_t = torch.tensor(x_np, dtype=torch.float32)
            logits = self(x_t)
            return torch.argmax(logits, dim=-1).cpu().numpy()

    def predict_proba(self, x_np):
        self.eval()
        with torch.no_grad():
            x_t = torch.tensor(x_np, dtype=torch.float32)
            logits = self(x_t)
            return torch.softmax(logits, dim=-1).cpu().numpy()


def train_logistic_regression(X_train, y_train, epochs=200, lr=0.01):
    """
    Trains multinomial Logistic Regression with balanced class weights.
    """
    input_dim = X_train.shape[1]
    model = PyTorchLogisticRegression(input_dim=input_dim, num_classes=3)
    
    # Class weights for imbalance
    counts = np.bincount(y_train, minlength=3)
    total = len(y_train)
    weights = [total / (3.0 * max(1, c)) for c in counts]
    weight_tensor = torch.tensor(weights, dtype=torch.float32)
    
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    x_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.long)
    
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits = model(x_train_t)
        loss = criterion(logits, y_train_t)
        loss.backward()
        optimizer.step()
        
    return model


# -------------------------------------------------------------------------
# Model B2: XGBoost Classifier
# -------------------------------------------------------------------------
def train_xgboost(X_train, y_train, random_state=42):
    """
    Trains XGBoost gradient boosted decision trees for multi-class risk classification.
    """
    if not HAS_XGB:
        return train_logistic_regression(X_train, y_train)
        
    clf = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        random_state=random_state,
        eval_metric="mlogloss"
    )
    clf.fit(X_train, y_train)
    return clf


# -------------------------------------------------------------------------
# Model C: Sequential Deep Learning LSTM with Masking & Temporal Attention
# -------------------------------------------------------------------------
class TemporalAttention(nn.Module):
    """
    Computes learnable temporal attention weights across sequence timesteps (weeks 1-16).
    """
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1, bias=False)

    def forward(self, lstm_outputs, mask=None):
        scores = self.attn(torch.tanh(lstm_outputs))  # [batch, seq_len, 1]
        
        if mask is not None:
            mask_expanded = mask.unsqueeze(-1)
            scores = scores.masked_fill(~mask_expanded, -1e9)
            
        weights = F.softmax(scores, dim=1)  # [batch, seq_len, 1]
        context = torch.sum(weights * lstm_outputs, dim=1)  # [batch, hidden_dim]
        return context, weights.squeeze(-1)


class StudentRiskLSTM(nn.Module):
    """
    Sequential LSTM network with Masking and Temporal Attention.
    Architecture:
      Input (Batch, 16, 5) -> LSTM(64) -> Temporal Attention -> Dropout(0.3) -> Dense(32, ReLU) -> Dense(3, Softmax)
    """
    def __init__(self, input_dim=5, hidden_dim=64, dense_dim=32, num_classes=3, dropout=0.3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=False
        )
        self.attention = TemporalAttention(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.dense = nn.Linear(hidden_dim, dense_dim)
        self.relu = nn.ReLU()
        self.classifier = nn.Linear(dense_dim, num_classes)

    def forward(self, x, mask=None):
        lstm_out, _ = self.lstm(x)  # [batch, seq_len, hidden_dim]
        context, attn_weights = self.attention(lstm_out, mask=mask)
        out = self.dropout(context)
        out = self.relu(self.dense(out))
        out = self.dropout(out)
        logits = self.classifier(out)
        return logits, attn_weights
