"""Configuración general y comprobación de preparación."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
import pandas as pd
from lumina_framework.core.exceptions import SchemaConfigurationError

from lumina_framework.core.contracts import (
    DatasetContract,
    ReadinessIssue,
    ReadinessResult,
)


@dataclass(frozen=True)
class FrameworkConfig:
    """Opciones independientes del esquema de un cliente."""

    source_path: Path | None = None
    output_dir: Path = Path("artifacts")


class ReadinessChecker:
    """Detecta información faltante sin inventar supuestos."""

    def check(
        self,
        config: FrameworkConfig,
        contract: DatasetContract,
    ) -> ReadinessResult:
        """Devuelve todos los bloqueos observables antes de ejecutar."""
        issues: list[ReadinessIssue] = []
        if config.source_path is None:
            issues.append(
                ReadinessIssue("missing_source", "Falta la fuente de datos.")
            )
        if not contract.columns:
            issues.append(
                ReadinessIssue(
                    "missing_columns",
                    "Falta el diccionario de columnas validado por el cliente.",
                )
            )
        if contract.target_column is None:
            issues.append(
                ReadinessIssue(
                    "missing_target",
                    "Falta definir la variable objetivo y su uso de negocio.",
                )
            )
        if contract.prediction_horizon is None:
            issues.append(
                ReadinessIssue(
                    "missing_prediction_horizon",
                    "Falta confirmar el horizonte de predicción.",
                )
            )
        return ReadinessResult(blockers=tuple(issues))


def load_yaml_configuration(
    path: Path,
) -> tuple[FrameworkConfig, DatasetContract]:
    """Carga configuración y contrato sin completar definiciones ausentes."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    dataset = raw.get("dataset") or {}
    source_value = raw.get("source_path")
    config = FrameworkConfig(
        source_path=None if source_value is None else Path(source_value),
        output_dir=Path(raw.get("output_dir", "artifacts")),
    )
    contract = DatasetContract(
        table_name=dataset.get("table_name"),
        columns=tuple(dataset.get("columns") or ()),
        identifier_columns=tuple(dataset.get("identifier_columns") or ()),
        date_column=dataset.get("date_column"),
        target_column=dataset.get("target_column"),
        prediction_horizon=dataset.get("prediction_horizon"),
        numeric_features=tuple(dataset.get("numeric_features") or ()),
        categorical_features=tuple(dataset.get("categorical_features") or ()),
    )
    return config, contract


@dataclass(frozen=True)
class SyntheticScenarioConfig:
    """Tamaño y semilla del escenario, independientes del experimento."""

    seed: int = 42
    product_count: int = 20
    branch_count: int = 5
    week_count: int = 104
    start_date: str = '2024-01-01'

    def __post_init__(self):
        if min(self.product_count, self.branch_count, self.week_count) <= 0:
            raise SchemaConfigurationError('Las cantidades deben ser positivas.')
        try:
            pd.Timestamp(self.start_date)
        except (ValueError, TypeError) as exc:
            raise SchemaConfigurationError('Fecha inicial inválida.') from exc


@dataclass(frozen=True)
class ExperimentConfig:
    """Orígenes semanales y espacios que impiden compartir etiquetas futuras."""

    train_start_week: int = 5
    train_end_week: int = 68
    validation_start_week: int = 73
    validation_end_week: int = 84
    test_start_week: int = 89
    test_end_week: int = 100
    horizon_weeks: int = 4
    seed: int = 42
    forest_trees: int = 300
    bootstrap_iterations: int = 1000
    start_date: str = '2024-01-01'

    def __post_init__(self):
        if self.horizon_weeks != 4:
            raise SchemaConfigurationError('Este experimento requiere cuatro semanas.')
        ranges = [(self.train_start_week, self.train_end_week),
                  (self.validation_start_week, self.validation_end_week),
                  (self.test_start_week, self.test_end_week)]
        if any(a < 5 or a > b for a, b in ranges):
            raise SchemaConfigurationError('Periodos insuficientes o invertidos.')
        if (self.train_end_week + 4 >= self.validation_start_week or
                self.validation_end_week + 4 >= self.test_start_week):
            raise SchemaConfigurationError('Los periodos comparten horizontes futuros.')


def load_project_configuration(path: Path):
    """Lee el contrato académico explícito y resuelve rutas desde el repositorio."""
    from dataclasses import replace
    raw = yaml.safe_load(path.read_text(encoding='utf-8'))
    config, contract = load_yaml_configuration(path)
    root = path.resolve().parent.parent
    config = replace(config,
                     source_path=root / config.source_path,
                     output_dir=root / config.output_dir)
    roles = raw['dataset']
    contract = replace(contract, **{k: roles.get(k) for k in (
        'category_column', 'price_column', 'promotion_column',
        'inventory_column', 'sales_column')})
    return (config, contract, SyntheticScenarioConfig(**raw.get('scenario', {})),
            ExperimentConfig(**raw.get('experiment', {})))
