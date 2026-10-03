"""Pruebas de preparación configurable y separación temporal."""

import pandas as pd
import pytest

from lumina_framework.core.contracts import DatasetContract
from lumina_framework.core.exceptions import (
    SchemaConfigurationError,
    TargetNotConfiguredError,
)
from lumina_framework.preprocessing.preprocessor import DataPreprocessor


def test_preprocessor_requires_target() -> None:
    """Impide entrenar cuando Boreal no ha definido la etiqueta."""
    contract = DatasetContract(columns=("x",), target_column=None)

    with pytest.raises(TargetNotConfiguredError):
        DataPreprocessor().prepare(pd.DataFrame({"x": [1, 2]}), contract)


def test_preprocessor_requires_declared_features() -> None:
    """Impide usar automáticamente todas las columnas como predictores."""
    frame = pd.DataFrame({"objetivo": [1.0, 2.0]})
    contract = DatasetContract(columns=("objetivo",), target_column="objetivo")

    with pytest.raises(SchemaConfigurationError, match="predictoras"):
        DataPreprocessor().prepare(frame, contract)


def test_temporal_split_keeps_future_out_of_train() -> None:
    """Detecta una partición que mezclara observaciones futuras."""
    frame = pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                ["2026-01-03", "2026-01-01", "2026-01-04", "2026-01-02"]
            ),
            "x": [3.0, 1.0, 4.0, 2.0],
            "objetivo": [30.0, 10.0, 40.0, 20.0],
        }
    )
    contract = DatasetContract(
        columns=("fecha", "x", "objetivo"),
        date_column="fecha",
        target_column="objetivo",
        numeric_features=("x",),
    )

    result = DataPreprocessor(test_fraction=0.25).prepare(frame, contract)

    assert result.train_dates is not None
    assert result.test_dates is not None
    assert result.train_dates.max() < result.test_dates.min()
    assert result.X_train["x"].tolist() == [1.0, 2.0, 3.0]
    assert result.X_test["x"].tolist() == [4.0]

