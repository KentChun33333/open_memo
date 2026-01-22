# scripts/train_iris.py
"""
train_iris.py
~~~~~~~~~~~
A minimal script that demonstrates training a simple ML model with scikit‑learn.

Features:
- Loads the bundled Iris CSV (`assets/iris_example.csv`) or any CSV supplied via CLI.
- Splits data (80 % train / 20 % test) using scikit‑learn's train_test_split.
- Trains a Logistic Regression classifier.
- Saves the model to `model.pkl` and prints accuracy, precision, recall.

Usage:
    python train_iris.py [options]

Options:
    -d <path>   Path to a custom CSV file (must follow schema in references/data_schema.json)
    -n <int>    Number of training epochs (default: 100)
"""

import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import sys
from pathlib import Path

def load_data(csv_path: Path) -> pd.DataFrame:
    """Read CSV and verify basic schema."""
    df = pd.read_csv(csv_path)
    # Expect at least one label column named 'target' or the last column if unnamed.
    if "target" not in df.columns:
        target_col = df.columns[-1]
    else:
        target_col = "target"
    return df

def main() -> None:
    parser = argparse.ArgumentParser(description="Train a simple model on Iris data")
    parser.add_argument("-d", "--data", type=str, default="assets/iris_example.csv",
                        help="Path to CSV dataset (default: assets/iris_example.csv)")
    parser.add_argument("-n", "--epochs", type=int, default=100,
                        help="Number of training epochs (default: 100)")
    args = parser.parse_args()

    csv_path = Path(args.data)
    if not csv_path.is_file():
        print(f"❌ File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    df = load_data(csv_path)

    # Basic validation – ensure we have features and a target
    X = df.drop(columns=[col for col in df.columns if "target" in str(col).lower()], errors="ignore")
    y = df.iloc[:, -1]  # assume last column is the label

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=args.epochs, stratify=y
    )

    model = LogisticRegression(max_iter=args.epochs)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, average="macro")
    rec = recall_score(y_test, preds, average="macro")

    print(f"✅ Model training complete!")
    print(f"   Accuracy : {acc:.3f}")
    print(f"   Precision: {prec:.3f}")
    print(f"   Recall   : {rec:.3f}")

    # Save model for later reuse
    joblib.dump(model, "model.pkl")
    print("🗂️ Model saved to `model.pkl`")

if __name__ == "__main__":
    main()