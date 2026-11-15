from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

try:
    from mage_ai.data_preparation.decorators import test, transformer
except ImportError:
    def transformer(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@transformer
def train_model(df: pd.DataFrame, **kwargs: Any) -> dict[str, Any]:
    runtime_vars = kwargs.get("runtime_vars", {})
    max_depth = int(kwargs.get("max_depth", runtime_vars.get("max_depth", 3)))
    feature_columns = [column for column in df.columns if column not in {"target", "split"}]
    train_rows = df[df["split"] == "train"]
    test_rows = df[df["split"] == "test"]
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(train_rows[feature_columns], train_rows["target"])
    predictions = model.predict(test_rows[feature_columns])
    return {
        "model": model,
        "feature_columns": feature_columns,
        "y_true": test_rows["target"].to_numpy(),
        "y_pred": predictions,
        "accuracy": float(accuracy_score(test_rows["target"], predictions)),
        "max_depth": max_depth,
    }


@test
def test_model_accuracy(output: dict[str, Any]) -> None:
    assert output["accuracy"] >= 0.75, (
        f"Accuracy {output['accuracy']:.3f} is below the 0.75 quality gate"
    )