from __future__ import annotations

from typing import Any

from sklearn.datasets import load_iris as sklearn_load_iris

try:
    from mage_ai.data_preparation.decorators import data_loader, test
except ImportError:
    def data_loader(function: Any) -> Any:
        return function

    def test(function: Any) -> Any:
        return function


@data_loader
def load_data(**kwargs: Any):
    return sklearn_load_iris(as_frame=True).frame


@test
def test_iris_load(output) -> None:
    assert len(output) == 150
    assert output["target"].nunique() == 3