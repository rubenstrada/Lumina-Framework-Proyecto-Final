"""Pruebas de visualizaciones condicionadas por columnas existentes."""

from pathlib import Path

import pandas as pd
import pytest

from lumina_framework.core.exceptions import SchemaConfigurationError
from lumina_framework.visualization.eda import EDAVisualizer


def _technical_fixture() -> pd.DataFrame:
    """Tabla mínima de software; no representa observaciones de Lumina."""
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "grupo": ["a", "a", "b"],
            "segmento": ["norte", "sur", "norte"],
            "valor": [1.0, 2.0, 3.0],
        }
    )


def test_visualizer_requires_existing_roles(tmp_path: Path) -> None:
    """Evita inventar una columna de fecha para completar una gráfica."""
    frame = pd.DataFrame({"valor": [1, 2]})

    with pytest.raises(SchemaConfigurationError, match="fecha"):
        EDAVisualizer(tmp_path).plot_time_series(
            frame,
            date_column="fecha",
            value_column="valor",
        )


def test_visualizer_creates_three_figures_without_mutating_input(
    tmp_path: Path,
) -> None:
    """Protege los tres contratos gráficos y la inmutabilidad de entrada."""
    frame = _technical_fixture()
    original = frame.copy(deep=True)
    visualizer = EDAVisualizer(tmp_path)

    time_path = visualizer.plot_time_series(frame, "fecha", "valor")
    distribution_path = visualizer.plot_distribution(frame, "valor", "grupo")
    heatmap_path = visualizer.plot_heatmap(
        frame,
        row_column="grupo",
        column_column="segmento",
        value_column="valor",
    )

    assert time_path.name == "serie_temporal.png"
    assert distribution_path.name == "distribucion.png"
    assert heatmap_path.name == "mapa_calor.png"
    assert all(path.exists() and path.stat().st_size > 0 for path in (
        time_path,
        distribution_path,
        heatmap_path,
    ))
    pd.testing.assert_frame_equal(frame, original)


def test_visualizer_uses_titles_that_communicate_chart_purpose(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Evita que advertencias o etiquetas técnicas sustituyan el mensaje visual."""
    captured_titles: list[str] = []
    monkeypatch.setattr(
        "lumina_framework.visualization.eda.plt.title",
        captured_titles.append,
    )
    frame = _technical_fixture()
    visualizer = EDAVisualizer(tmp_path)

    visualizer.plot_time_series(frame, "fecha", "valor")
    visualizer.plot_distribution(frame, "valor", "grupo")
    visualizer.plot_heatmap(
        frame,
        row_column="grupo",
        column_column="segmento",
        value_column="valor",
    )

    assert captured_titles == [
        "Evolución temporal de la variable",
        "Distribución de la variable por categoría",
        "Promedio de la variable por entidad y categoría",
    ]
