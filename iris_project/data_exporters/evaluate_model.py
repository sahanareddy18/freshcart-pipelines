from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import confusion_matrix

try:
    from mage_ai.data_preparation.decorators import data_exporter, test
except ImportError:
    def data_exporter(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@data_exporter
def evaluate_model(training: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    labels = [0, 1, 2]
    matrix = confusion_matrix(training["y_true"], training["y_pred"], labels=labels)
    metrics = pd.DataFrame(
        [{"max_depth": training["max_depth"], "test_accuracy": training["accuracy"]}]
    )
    return {"confusion_matrix": matrix, "metrics": metrics}


@test
def test_evaluation_output(output: dict[str, Any]) -> None:
    assert output["confusion_matrix"].shape == (3, 3)
    assert float(output["metrics"].loc[0, "test_accuracy"]) >= 0.75