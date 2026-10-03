"""Pruebas de la demostración EDA con datos sintéticos y reproducibles."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd

from lumina_framework.data import DataProfiler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_synthetic_eda_demo.py"
EXPLORATION_DOC = PROJECT_ROOT / "docs" / "exploracion_sintetica.md"
README_PATH = PROJECT_ROOT / "README.md"


def _load_demo_module():
    """Carga el script real para probar su API sin duplicar su lógica."""
    assert SCRIPT_PATH.exists(), "Falta scripts/run_synthetic_eda_demo.py"
    spec = importlib.util.spec_from_file_location("synthetic_eda_demo", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_dataset_is_reproducible_and_profileable() -> None:
    """Detecta cambios de semilla, esquema o anomalías controladas."""
    demo = _load_demo_module()
    assert not hasattr(demo, "_add_synthetic_notice")

    first = demo.build_synthetic_dataset(seed=20260916)
    second = demo.build_synthetic_dataset(seed=20260916)

    pd.testing.assert_frame_equal(first, second)
    assert tuple(first.columns) == (
        "fecha_demo",
        "entidad_demo",
        "categoria_demo",
        "valor_demo",
        "promocion_demo",
    )
    assert first.shape == (74, 5)

    profile = DataProfiler().profile(first)
    assert profile.row_count == 74
    assert profile.column_count == 5
    assert profile.missing_counts == {
        "fecha_demo": 0,
        "entidad_demo": 0,
        "categoria_demo": 3,
        "valor_demo": 4,
        "promocion_demo": 0,
    }
    assert profile.exact_duplicates == 2
    assert set(profile.numeric_statistics) == {"valor_demo"}


def test_demo_cli_writes_profile_and_three_visualizations(tmp_path: Path) -> None:
    """Detecta una demostración incompleta o resultados que dejan de ser reproducibles."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--output-dir",
            str(tmp_path),
            "--seed",
            "20260916",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    summary_path = tmp_path / "resumen_demo.json"
    markdown_path = tmp_path / "resumen_demo.md"
    assert summary_path.exists()
    assert markdown_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["seed"] == 20260916
    assert summary["shape"] == {"rows": 74, "columns": 5}
    assert summary["exact_duplicates"] == 2
    assert summary["missing"]["categoria_demo"] == {
        "count": 3,
        "percentage": 4.05,
    }
    assert summary["missing"]["valor_demo"] == {
        "count": 4,
        "percentage": 5.41,
    }
    assert summary["categorical_cardinality"] == {
        "entidad_demo": 3,
        "categoria_demo": 3,
        "promocion_demo": 2,
    }
    assert summary["numeric_statistics"]["valor_demo"] == {
        "count": 70.0,
        "mean": 56.843857,
        "std": 5.462105,
        "min": 45.78,
        "25%": 52.3675,
        "50%": 57.51,
        "75%": 60.2775,
        "max": 68.18,
    }

    assert "warning" not in summary
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Advertencia" not in markdown
    assert "no representa" not in markdown.casefold()

    expected_images = {
        "serie_temporal_demo.png",
        "distribucion_demo.png",
        "mapa_calor_demo.png",
    }
    assert {path.name for path in tmp_path.glob("*.png")} == expected_images
    for image in tmp_path.glob("*.png"):
        assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert image.stat().st_size > 10_000


def test_github_exploration_exposes_code_libraries_and_outputs() -> None:
    """Mantiene visible en GitHub la trazabilidad entre datos, código y gráficas."""
    assert EXPLORATION_DOC.exists()
    content = EXPLORATION_DOC.read_text(encoding="utf-8")

    required_fragments = (
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "DataProfiler().profile(data)",
        "EDAVisualizer(output_dir)",
        "sns.lineplot",
        "sns.histplot",
        "sns.heatmap",
        "plt.savefig",
        "evidencia_sintetica/serie_temporal_demo.png",
        "evidencia_sintetica/distribucion_demo.png",
        "evidencia_sintetica/mapa_calor_demo.png",
        "Evolución temporal de la variable",
        "Distribución de la variable por categoría",
        "Promedio de la variable por entidad y categoría",
    )
    for fragment in required_fragments:
        assert fragment in content

    assert "Advertencia" not in content
    assert "no representa" not in content.casefold()

    readme = README_PATH.read_text(encoding="utf-8")
    assert readme.count("se simularon los datos") == 1
