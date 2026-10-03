"""Métricas comparables y regla explícita contra línea base."""

from math import sqrt
from typing import Iterable

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from dataclasses import dataclass, asdict
import pandas as pd

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
    r2 = float(r2_score(y_true,predictions)) if len(y_true)>1 else float('nan')
    return EvaluationMetrics(mae=mae, rmse=rmse, wape=wape, r2=r2)


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float
    iterations: int
    block_weeks: int


class ModelEvaluator:
    """Compara regresión con una referencia bajo las mismas observaciones."""

    def calculate_regression_metrics(self, y_true, predictions):
        true = _as_finite_array(y_true,'y_true')
        pred = _as_finite_array(predictions,'predictions')
        if len(true) != len(pred):
            raise InsufficientDataError('Los arreglos requieren la misma longitud.')
        return _metrics(true,pred)

    def segmented_metrics(self, frame, y_column, prediction_column, segments):
        rows = [dict(segmento='global', valor='todos', n=len(frame),
                     **asdict(self.calculate_regression_metrics(frame[y_column],frame[prediction_column])))]
        for segment in segments:
            for value, group in frame.groupby(segment):
                rows.append(dict(segmento=segment,valor=str(value),n=len(group),
                    **asdict(self.calculate_regression_metrics(group[y_column],group[prediction_column]))))
        return pd.DataFrame(rows)

    def bootstrap_mae_difference(self, frame, y_column, candidate_column,
                                 baseline_column, week_column, iterations=1000, seed=42):
        """Bootstrap móvil de cuatro semanas: conserva autocorrelación del horizonte.

        Con solo doce semanas reservadas el intervalo es orientativo, no prueba
        de rentabilidad ni de generalización a otras organizaciones.
        """
        f = frame.copy()
        f['_difference'] = abs(f[y_column]-f[candidate_column])-abs(f[y_column]-f[baseline_column])
        weekly = f.groupby(week_column).agg(total=('_difference','sum'),n=('_difference','size')).sort_index()
        n = len(weekly)
        if not n:
            raise InsufficientDataError('No hay semanas para remuestreo.')
        block = min(4,n)
        rng = np.random.default_rng(seed)
        statistics = []
        for _ in range(iterations):
            starts = rng.integers(0,n-block+1,size=int(np.ceil(n/block)))
            idx = np.concatenate([np.arange(s,s+block) for s in starts])[:n]
            sample = weekly.iloc[idx]
            statistics.append(float(sample.total.sum()/sample.n.sum()))
        low,high = np.quantile(statistics,[.025,.975])
        return ConfidenceInterval(float(low),float(high),iterations,block)

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
