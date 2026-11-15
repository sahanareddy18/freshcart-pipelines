from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split

try:
    from mage_ai.data_preparation.decorators import test, transformer
except ImportError:
    def transformer(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@transformer
def transform(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """Return the Iris frame tagged with a reproducible stratified split."""
    if "target" not in df.columns:
        raise ValueError("Expected the Iris dataframe to contain a 'target' column")

    train_indices, test_indices = train_test_split(
        df.index,
        test_size=float(kwargs.get("test_size", 0.2)),
        random_state=int(kwargs.get("random_state", 42)),
        stratify=df["target"],
    )
    result = df.copy()
    result["split"] = "train"
    result.loc[test_indices, "split"] = "test"
    result.loc[train_indices, "split"] = "train"
    return result


@test
def test_split_is_disjoint_and_complete(output: pd.DataFrame) -> None:
    assert len(output) == 150
    assert output["split"].isin(["train", "test"]).all()
    assert output.loc[output["split"] == "train", "target"].nunique() == 3
    assert output.loc[output["split"] == "test", "target"].nunique() == 3