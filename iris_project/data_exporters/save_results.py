from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

try:
    from mage_ai.data_preparation.decorators import data_exporter, test
except ImportError:
    def data_exporter(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@data_exporter
def save_results(training: dict[str, Any], **kwargs: Any) -> str:
    output_path = Path(kwargs.get("output_path", "iris_predictions.csv"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"y_true": training["y_true"], "y_pred": training["y_pred"]}).to_csv(
        output_path, index=False
    )
    return str(output_path)


@test
def test_saved_predictions(output: str) -> None:
    assert Path(output).is_file()