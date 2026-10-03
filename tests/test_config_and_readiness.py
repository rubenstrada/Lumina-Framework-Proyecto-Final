"""Pruebas del contrato y del diagnóstico previo a cualquier análisis."""

from pathlib import Path

from lumina_framework.core.config import (
    FrameworkConfig,
    ReadinessChecker,
    load_yaml_configuration,
)
from lumina_framework.core.contracts import DatasetContract
from lumina_framework.core.context import RunContext


def test_readiness_reports_all_missing_business_definitions() -> None:
    """Evita que el framework avance con requisitos esenciales ausentes."""
    config = FrameworkConfig()
    contract = DatasetContract()

    result = ReadinessChecker().check(config, contract)

    assert result.ready_for_profiling is False
    assert result.ready_for_modeling is False
    assert {issue.code for issue in result.blockers} == {
        "missing_source",
        "missing_columns",
        "missing_target",
        "missing_prediction_horizon",
    }


def test_readiness_requires_prediction_horizon_for_modeling() -> None:
    """Evita declarar listo un problema temporal sin horizonte confirmado."""
    config = FrameworkConfig(source_path=Path("fuente_confirmada.csv"))
    contract = DatasetContract(columns=("campo",), target_column="campo")

    result = ReadinessChecker().check(config, contract)

    assert result.ready_for_profiling is True
    assert result.ready_for_modeling is False
    assert [issue.code for issue in result.blockers] == [
        "missing_prediction_horizon"
    ]


def test_run_context_records_events_and_artifacts() -> None:
    """Impide perder la trazabilidad mínima de una corrida."""
    context = RunContext.start()

    context.record_event("readiness_checked")
    context.record_artifact("profile", "artifacts/profile.json")

    manifest = context.to_manifest()
    assert manifest["status"] == "created"
    assert manifest["events"] == ["readiness_checked"]
    assert manifest["artifacts"] == {
        "profile": "artifacts/profile.json",
    }
    assert len(manifest["run_id"]) == 36


def test_yaml_configuration_preserves_intentional_missing_definitions(
    tmp_path: Path,
) -> None:
    """Distingue valores aún no confirmados de nombres inventados."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
source_path: null
output_dir: artifacts
dataset:
  table_name: null
  columns: []
  identifier_columns: []
  date_column: null
  target_column: null
  prediction_horizon: null
  numeric_features: []
  categorical_features: []
""".strip(),
        encoding="utf-8",
    )

    config, contract = load_yaml_configuration(config_path)

    assert config == FrameworkConfig(source_path=None, output_dir=Path("artifacts"))
    assert contract == DatasetContract()
