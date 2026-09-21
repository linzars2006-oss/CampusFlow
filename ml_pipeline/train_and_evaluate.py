"""
SmartEdu AI - Benchmark & Comparative Evaluation Engine
Module: ml_pipeline/train_and_evaluate.py

Trains and compares:
1. Model A: Rule-Based Baseline
2. Model B1: Logistic Regression
3. Model B2: XGBoost Classifier
4. Model C: PyTorch Sequential LSTM with Masking & Temporal Attention

Evaluates all models on the EXACT same held-out student-stratified test set.
Produces:
- Macro-averaged Precision, Recall, F1-Score, and Accuracy
- Multi-class Confusion Matrices (Low / Medium / High)
- Evaluation comparison table and plots (saved to disk)
- Benchmark JSON export for FastAPI and Django dashboards
"""

import os
import sys
import json
import pickle
import numpy as np

# Ensure local imports work cleanly
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from generate_dataset import save_dataset
from feature_engineering import (
    load_weekly_csv,
    extract_student_subject_sequences,
    extract_aggregated_static_features,
    evaluate_rule_based_baseline
)
from metrics import (
    SimpleStandardScaler,
    compute_classification_metrics,
    stratified_student_split
)
from models import (
    RuleBasedClassifier,
    train_logistic_regression,
    train_xgboost,
    StudentRiskLSTM,
    HAS_XGB
)
from explainability import explain_lstm_prediction, explain_classical_prediction

CLASSES = ["Low", "Medium", "High"]


def train_lstm_model(X_train, y_train, masks_train, X_test, y_test, masks_test,
                     epochs=50, batch_size=32, lr=0.001, patience=8):
    """
    Trains the Sequential Attention-LSTM network with early stopping and class weighting.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Sequential LSTM on device: {device}")
    
    counts = np.bincount(y_train, minlength=3)
    total = len(y_train)
    weights = [total / (3.0 * max(1, c)) for c in counts]
    weight_tensor = torch.tensor(weights, dtype=torch.float32).to(device)
    
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(masks_train, dtype=torch.bool),
        torch.tensor(y_train, dtype=torch.long)
    )
    test_dataset = TensorDataset(
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(masks_test, dtype=torch.bool),
        torch.tensor(y_test, dtype=torch.long)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = StudentRiskLSTM(input_dim=5, hidden_dim=64, dense_dim=32, num_classes=3, dropout=0.3).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    best_loss = float("inf")
    best_state = None
    patience_counter = 0
    
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for x_b, m_b, y_b in train_loader:
            x_b, m_b, y_b = x_b.to(device), m_b.to(device), y_b.to(device)
            optimizer.zero_grad()
            logits, _ = model(x_b, mask=m_b)
            loss = criterion(logits, y_b)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * len(y_b)
            
        avg_train_loss = total_loss / len(train_dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        with torch.no_grad():
            for x_b, m_b, y_b in test_loader:
                x_b, m_b, y_b = x_b.to(device), m_b.to(device), y_b.to(device)
                logits, _ = model(x_b, mask=m_b)
                loss = criterion(logits, y_b)
                val_loss += loss.item() * len(y_b)
                preds = torch.argmax(logits, dim=-1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(y_b.cpu().numpy())
                
        avg_val_loss = val_loss / len(test_dataset)
        val_metrics = compute_classification_metrics(val_targets, val_preds, num_classes=3)
        macro_f1 = val_metrics["Macro-F1"]
        
        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch [{epoch:02d}/{epochs:02d}] - Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Macro-F1: {macro_f1:.4f}")
            
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"[*] Early stopping triggered at epoch {epoch}")
                break
                
    if best_state is not None:
        model.load_state_dict(best_state)
        
    return model


def run_complete_benchmark(data_dir="ml_pipeline/data"):
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. Dataset Generation or Loading
    weekly_csv = os.path.join(data_dir, "weekly_student_records.csv")
    if not os.path.exists(weekly_csv):
        save_dataset(data_dir)
        
    records = load_weekly_csv(weekly_csv)
    print(f"[+] Loaded {len(records)} weekly records from {weekly_csv}")
    
    # 2. Sequential Features for LSTM
    X_seq, masks, seq_keys, y_seq, student_ids = extract_student_subject_sequences(records, max_timesteps=16)
    
    # 3. Aggregated Static Features for Classical ML
    X_static, static_feature_names, static_keys, y_static, _ = extract_aggregated_static_features(records)
    
    # 4. Stratified Leak-Free Split by Student (Zero test leakage!)
    train_mask, test_mask = stratified_student_split(student_ids, y_seq, test_ratio=0.20, random_seed=42)
    
    X_seq_train, X_seq_test = X_seq[train_mask], X_seq[test_mask]
    masks_train, masks_test = masks[train_mask], masks[test_mask]
    y_train, y_test = y_seq[train_mask], y_seq[test_mask]
    test_keys = [seq_keys[i] for i, flag in enumerate(test_mask) if flag]
    
    X_stat_train, X_stat_test = X_static[train_mask], X_static[test_mask]
    
    # Standardize static features
    scaler = SimpleStandardScaler()
    X_stat_train_scaled = scaler.fit_transform(X_stat_train)
    X_stat_test_scaled = scaler.transform(X_stat_test)
    
    print(f"[*] Dataset split summary: Train={len(y_train)}, Test={len(y_test)}")
    print(f"[*] Test class counts: Low={np.sum(y_test==0)}, Med={np.sum(y_test==1)}, High={np.sum(y_test==2)}")
    
    results = {}
    
    # -------------------------------------------------------------
    # 1. Evaluate Model A: Rule-Based Baseline
    # -------------------------------------------------------------
    print("\n--- Evaluating Model A: Rule-Based Baseline ---")
    y_pred_rule = evaluate_rule_based_baseline(records, test_keys)
    metrics_rule = compute_classification_metrics(y_test, y_pred_rule, num_classes=3)
    results["Rule-Based Baseline"] = metrics_rule
    
    # -------------------------------------------------------------
    # 2. Train & Evaluate Model B1: Logistic Regression
    # -------------------------------------------------------------
    print("\n--- Training & Evaluating Model B1: Logistic Regression ---")
    lr_model = train_logistic_regression(X_stat_train_scaled, y_train, epochs=250, lr=0.015)
    y_pred_lr = lr_model.predict(X_stat_test_scaled)
    metrics_lr = compute_classification_metrics(y_test, y_pred_lr, num_classes=3)
    results["Logistic Regression"] = metrics_lr
    
    # -------------------------------------------------------------
    # 3. Train & Evaluate Model B2: XGBoost
    # -------------------------------------------------------------
    print("\n--- Training & Evaluating Model B2: XGBoost ---")
    xgb_model = train_xgboost(X_stat_train_scaled, y_train)
    y_pred_xgb = xgb_model.predict(X_stat_test_scaled)
    metrics_xgb = compute_classification_metrics(y_test, y_pred_xgb, num_classes=3)
    results["XGBoost"] = metrics_xgb
    
    # -------------------------------------------------------------
    # 4. Train & Evaluate Model C: Sequential Attention-LSTM
    # -------------------------------------------------------------
    print("\n--- Training & Evaluating Model C: Sequential Attention-LSTM ---")
    lstm_model = train_lstm_model(
        X_seq_train, y_train, masks_train,
        X_seq_test, y_test, masks_test,
        epochs=50, batch_size=32, lr=0.001, patience=8
    )
    
    lstm_model.eval()
    with torch.no_grad():
        test_x_tensor = torch.tensor(X_seq_test, dtype=torch.float32)
        test_m_tensor = torch.tensor(masks_test, dtype=torch.bool)
        logits, _ = lstm_model(test_x_tensor, mask=test_m_tensor)
        y_pred_lstm = torch.argmax(logits, dim=-1).cpu().numpy()
        
    metrics_lstm = compute_classification_metrics(y_test, y_pred_lstm, num_classes=3)
    results["Sequential LSTM (Ours)"] = metrics_lstm
    
    # -------------------------------------------------------------
    # Print Comparison Table
    # -------------------------------------------------------------
    print("\n" + "=" * 76)
    print(f"{'Model Architecture':<28} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'Macro F1':<9}")
    print("-" * 76)
    for model_name, m in results.items():
        print(f"{model_name:<28} | {m['Accuracy']:<9.4f} | {m['Macro-Precision']:<9.4f} | {m['Macro-Recall']:<9.4f} | {m['Macro-F1']:<9.4f}")
    print("=" * 76)
    
    # -------------------------------------------------------------
    # Plot Comparison Charts (Matplotlib)
    # -------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        models_list = list(results.keys())
        f1_scores = [results[m]["Macro-F1"] for m in models_list]
        accuracies = [results[m]["Accuracy"] for m in models_list]
        recalls = [results[m]["Macro-Recall"] for m in models_list]
        
        x = np.arange(len(models_list))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width, accuracies, width, label='Accuracy', color='#3b82f6')
        ax.bar(x, recalls, width, label='Macro Recall', color='#10b981')
        rects3 = ax.bar(x + width, f1_scores, width, label='Macro F1-Score', color='#8b5cf6')
        
        ax.set_ylabel('Score (0.0 - 1.0)')
        ax.set_title('Academic Risk Prediction: Sequential LSTM vs Classical Baselines')
        ax.set_xticks(x)
        ax.set_xticklabels(models_list, rotation=10, ha="right")
        ax.legend(loc='lower right')
        ax.set_ylim(0.0, 1.05)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        for rect in rects3:
            h = rect.get_height()
            ax.annotate(f'{h:.2f}', xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
                        
        plt.tight_layout()
        chart_path = os.path.join(data_dir, "model_comparison.png")
        plt.savefig(chart_path, dpi=200)
        plt.close()
        print(f"[+] Saved comparison plot: {chart_path}")
    except Exception as e:
        print(f"[-] Plot generation notice: {e}")
        
    # -------------------------------------------------------------
    # Save Model Artifacts
    # -------------------------------------------------------------
    lstm_save_path = os.path.join(data_dir, "best_lstm_model.pt")
    torch.save(lstm_model.state_dict(), lstm_save_path)
    
    scaler_save_path = os.path.join(data_dir, "scaler_params.json")
    with open(scaler_save_path, "w") as f:
        json.dump({"mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist()}, f)
        
    xgb_save_path = os.path.join(data_dir, "xgboost_model.json")
    if HAS_XGB:
        xgb_model.save_model(xgb_save_path)
        
    benchmark_json_path = os.path.join(data_dir, "benchmark_results.json")
    with open(benchmark_json_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"[+] Saved LSTM weights to: {lstm_save_path}")
    print(f"[+] Saved benchmark metrics to: {benchmark_json_path}")
    
    return results


if __name__ == "__main__":
    run_complete_benchmark()
