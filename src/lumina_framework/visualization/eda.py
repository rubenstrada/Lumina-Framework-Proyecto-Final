"""Gráficas exploratorias que no modifican la fuente."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from lumina_framework.core.exceptions import SchemaConfigurationError


class EDAVisualizer:
    """Genera figuras solo cuando se declaran columnas existentes."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    @staticmethod
    def _require_columns(data: pd.DataFrame, columns: tuple[str, ...]) -> None:
        missing = sorted(set(columns) - set(data.columns))
        if missing:
            raise SchemaConfigurationError(
                "Faltan columnas para la visualización: " + ", ".join(missing)
            )

    def _save(self, filename: str) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()
        return path

    def plot_time_series(
        self,
        data: pd.DataFrame,
        date_column: str,
        value_column: str,
    ) -> Path:
        """Crea una serie temporal de una medida configurada."""
        self._require_columns(data, (date_column, value_column))
        plot_data = data.loc[:, [date_column, value_column]].copy()
        plot_data[date_column] = pd.to_datetime(plot_data[date_column])
        plot_data = plot_data.sort_values(date_column)
        plt.figure(figsize=(8, 4.5))
        sns.lineplot(data=plot_data, x=date_column, y=value_column, marker="o")
        plt.title("Evolución temporal de la variable")
        plt.xlabel(date_column)
        plt.ylabel(value_column)
        return self._save("serie_temporal.png")

    def plot_distribution(
        self,
        data: pd.DataFrame,
        value_column: str,
        group_column: str | None = None,
    ) -> Path:
        """Crea una distribución global o segmentada."""
        columns = (value_column,) if group_column is None else (
            value_column,
            group_column,
        )
        self._require_columns(data, columns)
        plot_data = data.loc[:, list(columns)].copy()
        plt.figure(figsize=(8, 4.5))
        sns.histplot(
            data=plot_data,
            x=value_column,
            hue=group_column,
            kde=True,
            element="step",
        )
        plt.title("Distribución de la variable por categoría")
        plt.xlabel(value_column)
        plt.ylabel("Frecuencia")
        return self._save("distribucion.png")

    def plot_heatmap(
        self,
        data: pd.DataFrame,
        *,
        row_column: str,
        column_column: str,
        value_column: str,
    ) -> Path:
        """Crea un mapa de calor agregado por dos dimensiones."""
        columns = (row_column, column_column, value_column)
        self._require_columns(data, columns)
        plot_data = data.loc[:, list(columns)].copy()
        matrix = plot_data.pivot_table(
            index=row_column,
            columns=column_column,
            values=value_column,
            aggfunc="mean",
        )
        plt.figure(figsize=(8, 4.5))
        sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlGnBu")
        plt.title("Promedio de la variable por entidad y categoría")
        plt.xlabel(column_column)
        plt.ylabel(row_column)
        return self._save("mapa_calor.png")
