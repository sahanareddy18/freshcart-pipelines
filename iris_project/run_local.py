from __future__ import annotations

import argparse
from pathlib import Path

from iris_project.data_exporters.evaluate_model import evaluate_model
from iris_project.data_exporters.save_results import save_results
from iris_project.data_loaders.load_iris import load_data
from iris_project.transformers.prepare_data import transform as prepare_data
from iris_project.transformers.train_model import train_model
from iris_project.transformers.validate_iris import transform as validate_iris


def run(max_depth: int = 3, output_path: str = "iris_predictions.csv") -> dict:
    loaded = load_data()
    checked = validate_iris(loaded)
    prepared = prepare_data(checked)
    training = train_model(prepared, max_depth=max_depth)
    from iris_project.transformers.train_model import test_model_accuracy

    test_model_accuracy(training)
    saved_path = save_results(training, output_path=output_path)
    evaluation = evaluate_model(training)
    print(f"max_depth={max_depth}; test_accuracy={training['accuracy']:.3f}")
    print("confusion_matrix:")
    print(evaluation["confusion_matrix"])
    print("metrics:")
    print(evaluation["metrics"].to_string(index=False))
    print(f"saved={saved_path}")
    return {"training": training, "evaluation": evaluation, "saved_path": saved_path}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--output", default="iris_predictions.csv")
    args = parser.parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    run(max_depth=args.max_depth, output_path=args.output)