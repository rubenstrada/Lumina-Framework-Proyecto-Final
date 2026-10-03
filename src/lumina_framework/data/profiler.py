"""Perfilado descriptivo independiente de una etiqueta."""

from typing import Any

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

from lumina_framework.core.contracts import ProfileResult


def _normalized_dtype(series: pd.Series) -> str:
    """Reduce diferencias de versión de pandas a categorías legibles."""
    if is_string_dtype(series.dtype) and not is_numeric_dtype(series.dtype):
        return "string"
    return str(series.dtype)


class DataProfiler:
    """Describe lo observable sin limpiar ni interpretar por negocio."""

    def profile(self, data: pd.DataFrame) -> ProfileResult:
        """Calcula estructura, calidad básica y estadísticos disponibles."""
        dtypes = {str(column): _normalized_dtype(data[column]) for column in data.columns}
        missing = {
            str(column): int(data[column].isna().sum()) for column in data.columns
        }
        unique = {
            str(column): int(data[column].nunique(dropna=True))
            for column in data.columns
        }

        numeric_statistics: dict[str, dict[str, Any]] = {}
        numeric = data.select_dtypes(include="number")
        if not numeric.empty:
            described = numeric.describe().to_dict()
            numeric_statistics = {
                str(column): {
                    str(statistic): float(value)
                    for statistic, value in statistics.items()
                }
                for column, statistics in described.items()
            }

        return ProfileResult(
            row_count=int(data.shape[0]),
            column_count=int(data.shape[1]),
            dtypes=dtypes,
            missing_counts=missing,
            exact_duplicates=int(data.duplicated().sum()),
            unique_counts=unique,
            numeric_statistics=numeric_statistics,
        )
