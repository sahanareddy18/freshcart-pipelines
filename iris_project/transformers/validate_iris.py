from __future__ import annotations

from typing import Any

import pandas as pd

try:
    from mage_ai.data_preparation.decorators import test, transformer
except ImportError:
    def transformer(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@transformer
def transform(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    if df.isna().any().any():
        raise ValueError("Iris input contains missing values")
    if "target" not in df or df["target"].nunique() != 3:
        raise ValueError("Iris input must contain exactly three target classes")
    return df.copy()


@test
def test_iris_quality(output: pd.DataFrame) -> None:
    assert not output.isna().any().any()
    assert output["target"].nunique() == 3