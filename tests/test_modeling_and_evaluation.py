"""Pruebas de entrenamiento genérico y evaluación contra línea base."""

import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from lumina_framework.core.contracts import DatasetContract
from lumina_framework.core.exceptions import InsufficientDataError
from lumina_framework.modeling.evaluator import ModelEvaluator
from lumina_framework.modeling.trainer import ModelTrainer
from lumina_framework.preprocessing.preprocessor import DataPreprocessor


def test_evaluator_rejects_empty_values() -> None:
    """Evita producir métricas aparentemente válidas sin observaciones."""
    with pytest.raises(InsufficientDataError, match="observaciones"):
        ModelEvaluator().evaluate_regression(
            [],
            [],
            baseline_predictions=[],
        )


def test_evaluator_rejects_different_lengths() -> None:
    """Impide comparar arreglos que no representan las mismas filas."""
    with pytest.raises(InsufficientDataError, match="misma longitud"):
        ModelEvaluator().evaluate_regression(
            [1.0, 2.0],
            [1.0],
            baseline_predictions=[1.0, 2.0],
        )


def test_evaluator_does_not_recommend_worse_model() -> None:
    """Protege la regla de no entregar complejidad que pierde al baseline."""
    result = ModelEvaluator().evaluate_regression(
        y_true=[1.0, 2.0, 3.0],
        predictions=[9.0, 9.0, 9.0],
        baseline_predictions=[1.0, 2.0, 2.5],
    )

    assert result.recommended is False
    assert result.reason == "El modelo no supera la línea base en MAE."
    assert result.metrics.mae == pytest.approx(7.0)
    assert result.baseline_metrics.mae == pytest.approx(1 / 6)


def test_trainer_fits_preprocessing_only_on_training_period() -> None:
    """Detecta fuga si la imputación aprende del periodo reservado."""
    frame = pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]
            ),
            "x": [1.0, 2.0, None, 1000.0],
            "objetivo": [1.0, 2.0, 3.0, 4.0],
        }
    )
    contract = DatasetContract(
        columns=("fecha", "x", "objetivo"),
        date_column="fecha",
        target_column="objetivo",
        numeric_features=("x",),
    )
    split = DataPreprocessor(test_fraction=0.25).prepare(frame, contract)

    result = ModelTrainer().train(split, LinearRegression())

    imputer = result.pipeline.named_steps["preprocessor"].named_transformers_[
        "numeric"
    ].named_steps["imputer"]
    assert imputer.statistics_[0] == pytest.approx(1.5)
    assert len(result.train_predictions) == 3
    assert len(result.test_predictions) == 1
