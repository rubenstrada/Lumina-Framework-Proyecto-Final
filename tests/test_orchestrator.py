"""Pruebas del flujo conceptual y del perfilado permitido."""

from pathlib import Path

from lumina_framework.core.config import FrameworkConfig
from lumina_framework.core.contracts import DatasetContract
from lumina_framework.pipeline.orchestrator import LuminaPipeline


def test_pipeline_reports_blockers_without_attempting_load() -> None:
    """Evita acceder a archivos cuando la preparación ya indica bloqueos."""
    pipeline = LuminaPipeline()

    result = pipeline.assess(FrameworkConfig(), DatasetContract())

    assert result.status == "blocked"
    assert result.loaded_rows is None
    assert set(result.blocker_codes) == {
        "missing_source",
        "missing_columns",
        "missing_target",
        "missing_prediction_horizon",
    }
    assert '"status": "blocked"' in result.to_json()


def test_pipeline_profiles_technical_source_without_enabling_modeling(
    tmp_path: Path,
) -> None:
    """Permite EDA estructural aun si la etiqueta continúa sin definirse."""
    source = tmp_path / "fixture_tecnico.csv"
    source.write_text("id,valor\n1,10\n2,20\n", encoding="utf-8")
    config = FrameworkConfig(source_path=source, output_dir=tmp_path / "artifacts")
    contract = DatasetContract(columns=("id", "valor"), target_column=None)

    result = LuminaPipeline().run_profile(config, contract)

    assert result.status == "profiled"
    assert result.loaded_rows == 2
    assert result.blocker_codes == (
        "missing_target",
        "missing_prediction_horizon",
    )
    assert len(result.artifact_paths) == 2
    assert all(path.exists() and path.stat().st_size > 0 for path in result.artifact_paths)
