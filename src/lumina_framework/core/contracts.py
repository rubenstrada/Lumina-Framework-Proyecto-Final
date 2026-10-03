"""Clases de datos que hacen explícitos los contratos del framework."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DatasetContract:
    """Definiciones que Boreal deberá confirmar antes del análisis."""

    table_name: str | None = None
    columns: tuple[str, ...] = ()
    identifier_columns: tuple[str, ...] = ()
    date_column: str | None = None
    target_column: str | None = None
    prediction_horizon: str | None = None
    numeric_features: tuple[str, ...] = ()
    categorical_features: tuple[str, ...] = ()
    category_column: str | None = None
    price_column: str | None = None
    promotion_column: str | None = None
    inventory_column: str | None = None
    sales_column: str | None = None


@dataclass(frozen=True)
class ReadinessIssue:
    """Requisito ausente que bloquea una o más etapas."""

    code: str
    message: str


@dataclass(frozen=True)
class ReadinessResult:
    """Estado de preparación antes de acceder a una fuente."""

    blockers: tuple[ReadinessIssue, ...]

    @property
    def ready_for_profiling(self) -> bool:
        """Indica si ya existe fuente y diccionario de columnas."""
        profiling_codes = {"missing_source", "missing_columns"}
        return not any(issue.code in profiling_codes for issue in self.blockers)

    @property
    def ready_for_modeling(self) -> bool:
        """Indica si no queda ningún requisito esencial pendiente."""
        return not self.blockers


@dataclass(frozen=True)
class ValidationResult:
    """Hallazgos estructurales obtenidos sin modificar los datos."""

    valid: bool
    missing_columns: tuple[str, ...]
    exact_duplicates: int
    key_duplicates: int | None
    invalid_dates: int | None
    missing_by_column: dict[str, int] = field(default_factory=dict)
    negative_by_column: dict[str, int] = field(default_factory=dict)
    sales_above_inventory: int = 0
    inconsistent_categories: int = 0


@dataclass(frozen=True)
class CleaningChange:
    """Transformación autorizada y cantidad de registros afectados."""

    rule: str
    affected_rows: int
    details: str


@dataclass(frozen=True)
class CleaningResult:
    """Datos limpios y bitácora inseparable de los cambios."""

    data: pd.DataFrame
    changes: tuple[CleaningChange, ...]


@dataclass(frozen=True)
class ProfileResult:
    """Descripción serializable de la estructura disponible."""

    row_count: int
    column_count: int
    dtypes: dict[str, str]
    missing_counts: dict[str, int]
    exact_duplicates: int
    unique_counts: dict[str, int]
    numeric_statistics: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class PreprocessingResult:
    """Partición y transformador todavía no ajustado."""

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    transformer: Any
    train_dates: pd.Series | None
    test_dates: pd.Series | None


@dataclass(frozen=True)
class TrainingResult:
    """Pipeline ajustado y predicciones separadas por periodo."""

    pipeline: Any
    train_predictions: Any
    test_predictions: Any


@dataclass(frozen=True)
class EvaluationMetrics:
    """Métricas de regresión con WAPE opcional cuando el denominador es cero."""

    mae: float
    rmse: float
    wape: float | None
    r2: float = 0.0


@dataclass(frozen=True)
class EvaluationResult:
    """Comparación explícita del candidato contra una línea base."""

    metrics: EvaluationMetrics
    baseline_metrics: EvaluationMetrics
    recommended: bool
    reason: str


@dataclass(frozen=True)
class RunResult:
    """Estado observable de una evaluación o corrida del pipeline."""

    status: str
    blocker_codes: tuple[str, ...]
    loaded_rows: int | None = None
    artifact_paths: tuple[Path, ...] = ()

    def to_json(self) -> str:
        """Serializa el resultado para CLI o integraciones."""
        return json.dumps(
            {
                "status": self.status,
                "blocker_codes": list(self.blocker_codes),
                "loaded_rows": self.loaded_rows,
                "artifact_paths": [str(path) for path in self.artifact_paths],
            },
            ensure_ascii=False,
            indent=2,
        )
