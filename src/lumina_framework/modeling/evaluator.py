"""Métricas comparables y regla explícita contra línea base."""

from math import sqrt
from typing import Iterable

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

from lumina_framework.core.contracts import EvaluationMetrics, EvaluationResult
from lumina_framework.core.exceptions import InsufficientDataError


def _as_finite_array(values: Iterable[float], name: str) -> np.ndarray:
    array = np.asarray(list(values), dtype=float).reshape(-1)
    if array.size == 0:
        raise InsufficientDataError(
            "Se requieren observaciones para calcular métricas."
        )
    if not np.isfinite(array).all():
        raise InsufficientDataError(f"{name} contiene valores no finitos.")
    return array


def _metrics(y_true: np.ndarray, predictions: np.ndarray) -> EvaluationMetrics:
    mae = float(mean_absolute_error(y_true, predictions))
    rmse = float(sqrt(mean_squared_error(y_true, predictions)))
    denominator = float(np.abs(y_true).sum())
    wape = None
    if denominator != 0:
        wape = float(np.abs(y_true - predictions).sum() / denominator)
    return EvaluationMetrics(mae=mae, rmse=rmse, wape=wape)


class ModelEvaluator:
    """Compara regresión con una referencia bajo las mismas observaciones."""

    def evaluate_regression(
        self,
        y_true: Iterable[float],
        predictions: Iterable[float],
        *,
        baseline_predictions: Iterable[float],
    ) -> EvaluationResult:
        """Calcula MAE, RMSE y WAPE y aplica la regla de línea base."""
        true_array = _as_finite_array(y_true, "y_true")
        prediction_array = _as_finite_array(predictions, "predictions")
        baseline_array = _as_finite_array(
            baseline_predictions,
            "baseline_predictions",
        )
        if not (
            len(true_array) == len(prediction_array) == len(baseline_array)
        ):
            raise InsufficientDataError(
                "Los valores reales y las predicciones deben tener la misma longitud."
            )

        model_metrics = _metrics(true_array, prediction_array)
        baseline_metrics = _metrics(true_array, baseline_array)
        recommended = model_metrics.mae < baseline_metrics.mae
        reason = (
            "El modelo supera la línea base en MAE."
            if recommended
            else "El modelo no supera la línea base en MAE."
        )
        return EvaluationResult(
            metrics=model_metrics,
            baseline_metrics=baseline_metrics,
            recommended=recommended,
            reason=reason,
        )
